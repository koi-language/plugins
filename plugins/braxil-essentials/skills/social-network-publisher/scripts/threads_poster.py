"""Publish to Threads (Meta) — text, an image, or a video — using a token
vended by the BRAXIL Auth Broker. Run `python scripts/connect.py --platform
threads` once first.

  python scripts/threads_poster.py --text "hello threads"
  python scripts/threads_poster.py --text "look" --image photo.png
  python scripts/threads_poster.py --text "clip" --video clip.mp4

Threads (like Instagram) only accepts a PUBLIC media URL, so local files are
hosted on the BRAXIL media CDN first. Publishing is two steps: create a media
container, then publish it. Text-only posts ARE allowed (unlike Instagram).
Stdlib only (urllib)."""

import argparse
import sys
import time

try:
    from broker_client import get_token, http_json, host_media, normalize_text, BrokerError
except ImportError:
    from .broker_client import get_token, http_json, host_media, normalize_text, BrokerError

GRAPH = "https://graph.threads.net/v1.0"


def _public_url(url, local):
    if url:
        return url
    if local:
        return host_media(local)
    return None


def _wait_container(creation_id, access_token, timeout=180, interval=3):
    """Poll a media container until it finishes processing (videos need this)."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        res = http_json("GET", f"{GRAPH}/{creation_id}?fields=status&access_token={access_token}")
        status = (res.get("status") or "").upper()
        if status in ("FINISHED", "PUBLISHED"):
            return
        if status in ("ERROR", "EXPIRED"):
            raise BrokerError(f"Threads container failed processing: {res}")
        time.sleep(interval)
    raise BrokerError("Threads container did not finish processing in time")


def post_to_threads(text="", image=None, image_url=None, video=None, video_url=None, account=None):
    if (image or image_url) and (video or video_url):
        raise BrokerError("Threads: post EITHER an image OR a video, not both.")
    text = normalize_text(text)
    img = _public_url(image_url, image)
    vid = _public_url(video_url, video)

    tok = get_token("threads", account=account)
    ids = tok.get("ids") or {}
    user_id = ids.get("threadsUserId") or tok.get("providerAccountId")
    if not user_id:
        raise BrokerError("Threads user id missing — reconnect with connect.py --platform threads")
    access_token = tok["accessToken"]

    # Step 1: create the media container.
    form = {"access_token": access_token}
    if vid:
        form.update({"media_type": "VIDEO", "video_url": vid, "text": text})
    elif img:
        form.update({"media_type": "IMAGE", "image_url": img, "text": text})
    else:
        if not text:
            raise BrokerError("Threads: provide --text and/or media.")
        form.update({"media_type": "TEXT", "text": text})
    container = http_json("POST", f"{GRAPH}/{user_id}/threads", form_body=form)
    creation_id = container.get("id")
    if not creation_id:
        raise BrokerError(f"Threads container failed: {container}")

    # Step 2 (media only): wait for the container to finish processing.
    if vid or img:
        _wait_container(creation_id, access_token)

    # Step 3: publish it.
    res = http_json(
        "POST", f"{GRAPH}/{user_id}/threads_publish",
        form_body={"creation_id": creation_id, "access_token": access_token},
    )
    kind = "video" if vid else ("image" if img else "text")
    print(f"✅ Posted {kind} to Threads (id={res.get('id')}).")
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post to Threads via the BRAXIL broker.")
    parser.add_argument("--text", default="", help="Post text")
    parser.add_argument("--image", help="Local image file (hosted automatically to a public URL)")
    parser.add_argument("--image-url", help="Public image URL — alternative to --image")
    parser.add_argument("--video", help="Local video file (hosted automatically to a public URL)")
    parser.add_argument("--video-url", help="Public video URL — alternative to --video")
    parser.add_argument("--account", help="Which connected Threads account (optional)")
    args = parser.parse_args()
    if not args.text and not args.image and not args.image_url and not args.video and not args.video_url:
        parser.error("provide --text and/or --image/--video")
    try:
        post_to_threads(text=args.text, image=args.image, image_url=args.image_url,
                        video=args.video, video_url=args.video_url, account=args.account)
    except BrokerError as e:
        print(f"❌ {e}")
        sys.exit(1)
