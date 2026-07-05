"""Publish to X (Twitter) — text and/or media (images, video) — using a token
vended by the BRAXIL Auth Broker. Run `python scripts/connect.py --platform x`
once first.

Media uses X's v2 media-upload endpoint (POST /2/media/upload) with the user's
OAuth 2.0 token, which requires the `media.write` scope. That scope was added to
the broker's X scopes — if the account was connected BEFORE it existed, run
`connect.py --platform x` again to reconnect and mint a token that carries it.

Stdlib only (urllib) — no third-party deps, matching the rest of the plugin.
"""

import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
import ssl

try:
    from broker_client import get_token, http_json, normalize_text, BrokerError
except ImportError:
    from .broker_client import get_token, http_json, normalize_text, BrokerError

TWEETS_URL = "https://api.twitter.com/2/tweets"
# v2 media upload. If a future API change 404s this, the canonical host is
# `https://api.x.com/2/media/upload` — swap the base below.
MEDIA_UPLOAD_URL = "https://api.twitter.com/2/media/upload"

CHUNK = 4 * 1024 * 1024  # 4 MB per APPEND segment (X caps each APPEND at 5 MB)

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass


def _auth(tok):
    return {"Authorization": f"Bearer {tok['accessToken']}", "Accept": "application/json"}


def _multipart(fields, file_field=None, file_name=None, file_bytes=None):
    """Build a multipart/form-data body (X media commands expect multipart).
    `fields` → str parts; optionally one binary part."""
    boundary = "----braxilX" + os.urandom(8).hex()
    crlf = b"\r\n"
    parts = []
    for k, v in fields.items():
        parts.append(b"--" + boundary.encode())
        parts.append(('Content-Disposition: form-data; name="%s"' % k).encode())
        parts.append(b"")
        parts.append(str(v).encode())
    if file_field is not None:
        parts.append(b"--" + boundary.encode())
        parts.append(
            ('Content-Disposition: form-data; name="%s"; filename="%s"'
             % (file_field, file_name)).encode())
        parts.append(b"Content-Type: application/octet-stream")
        parts.append(b"")
        parts.append(file_bytes)
    parts.append(b"--" + boundary.encode() + b"--")
    parts.append(b"")
    return crlf.join(parts), "multipart/form-data; boundary=" + boundary


def _request(method, url, tok, body=None, content_type=None, timeout=180):
    headers = _auth(tok)
    if content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "ignore")
            return json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "ignore")
        raise BrokerError(f"{method} {url} -> {e.code}: {msg[:400]}")
    except urllib.error.URLError as e:
        raise BrokerError(f"{method} {url} failed: {e}")


def _media_id(res):
    # v2 returns data.id; legacy/v1.1 returns media_id_string. Be defensive.
    return (res.get("data") or {}).get("id") or res.get("media_id_string") or res.get("id")


def _processing(res):
    return (res.get("data") or {}).get("processing_info") or res.get("processing_info")


def upload_image(tok, path):
    if not os.path.isfile(path):
        raise BrokerError(f"image not found: {path}")
    with open(path, "rb") as f:
        data = f.read()
    body, ct = _multipart(
        {"media_category": "tweet_image"},
        file_field="media", file_name=os.path.basename(path), file_bytes=data,
    )
    res = _request("POST", MEDIA_UPLOAD_URL, tok, body=body, content_type=ct)
    mid = _media_id(res)
    if not mid:
        raise BrokerError(f"image upload returned no media id: {res}")
    return mid


def upload_video(tok, path):
    if not os.path.isfile(path):
        raise BrokerError(f"video not found: {path}")
    size = os.path.getsize(path)
    media_type = mimetypes.guess_type(path)[0] or "video/mp4"

    # INIT
    init_body, ct = _multipart({
        "command": "INIT",
        "total_bytes": size,
        "media_type": media_type,
        "media_category": "tweet_video",
    })
    init = _request("POST", MEDIA_UPLOAD_URL, tok, body=init_body, content_type=ct)
    mid = _media_id(init)
    if not mid:
        raise BrokerError(f"video INIT returned no media id: {init}")

    # APPEND (chunked)
    with open(path, "rb") as f:
        seg = 0
        while True:
            chunk = f.read(CHUNK)
            if not chunk:
                break
            ab, act = _multipart(
                {"command": "APPEND", "media_id": mid, "segment_index": seg},
                file_field="media", file_name="chunk", file_bytes=chunk,
            )
            _request("POST", MEDIA_UPLOAD_URL, tok, body=ab, content_type=act)
            seg += 1

    # FINALIZE
    fb, fct = _multipart({"command": "FINALIZE", "media_id": mid})
    fin = _request("POST", MEDIA_UPLOAD_URL, tok, body=fb, content_type=fct)

    # Async transcode: poll STATUS until ready
    info = _processing(fin)
    while info and info.get("state") in ("pending", "in_progress"):
        time.sleep(int(info.get("check_after_secs", 3)))
        st = _request("GET", f"{MEDIA_UPLOAD_URL}?command=STATUS&media_id={mid}", tok)
        info = _processing(st)
    if info and info.get("state") == "failed":
        raise BrokerError(f"video processing failed: {info}")
    return mid


def post_to_x(text=None, images=None, video=None, account=None):
    images = images or []
    if video and images:
        raise BrokerError("X allows EITHER up to 4 images OR 1 video — not both.")
    if len(images) > 4:
        raise BrokerError("X allows at most 4 images per post.")
    if not text and not images and not video:
        raise BrokerError("Nothing to post: provide --text and/or --image/--video.")

    text = normalize_text(text)
    tok = get_token("x", account=account)

    media_ids = []
    for p in images:
        media_ids.append(upload_image(tok, p))
    if video:
        media_ids.append(upload_video(tok, video))

    body = {}
    if text:
        body["text"] = text
    if media_ids:
        body["media"] = {"media_ids": media_ids}

    res = http_json("POST", TWEETS_URL, headers=_auth(tok), json_body=body)
    tweet_id = (res.get("data") or {}).get("id")
    extra = f" with {len(media_ids)} media" if media_ids else ""
    print(f"✅ Posted to X (id={tweet_id}){extra}.")
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Post text and/or media (images, video) to X via the BRAXIL broker.")
    parser.add_argument("--text", help="Text to post (optional when media is provided)")
    parser.add_argument("--image", action="append", default=[], metavar="PATH",
                        help="Image to attach (repeatable, up to 4). Cannot combine with --video.")
    parser.add_argument("--video", metavar="PATH",
                        help="Video to attach (1 max). Cannot combine with --image.")
    parser.add_argument("--account",
                        help="Which connected X account (@handle or id) — needed when you manage several")
    parser.add_argument("--reply-to",
                        help="Tweet ID to reply to (to create a thread)")
    args = parser.parse_args()
    try:
        # Expose --reply-to in post_to_x
        images = args.image or []
        if args.video and images:
            print("❌ X allows EITHER up to 4 images OR 1 video — not both.")
            sys.exit(1)
        if len(images) > 4:
            print("❌ X allows at most 4 images per post.")
            sys.exit(1)
        if not args.text and not images and not args.video:
            print("❌ Nothing to post: provide --text and/or --image/--video.")
            sys.exit(1)
        
        # Call post_to_x or direct request
        tok = get_token("x", account=args.account)
        
        # Process media uploads
        media_ids = []
        for p in images:
            media_ids.append(upload_image(tok, p))
        if args.video:
            media_ids.append(upload_video(tok, args.video))
            
        body = {}
        if args.text:
            body["text"] = normalize_text(args.text)
        if media_ids:
            body["media"] = {"media_ids": media_ids}
        if args.reply_to:
            body["reply"] = {"in_reply_to_tweet_id": args.reply_to}
            
        res = http_json("POST", TWEETS_URL, headers=_auth(tok), json_body=body)
        tweet_id = (res.get("data") or {}).get("id")
        extra = f" with {len(media_ids)} media" if media_ids else ""
        print(f"✅ Posted to X (id={tweet_id}){extra}.")
    except BrokerError as e:
        print(f"❌ {e}")
        sys.exit(1)
