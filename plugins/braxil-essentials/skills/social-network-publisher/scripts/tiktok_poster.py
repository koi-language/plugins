"""Publish a video to TikTok via the Content Posting API, using a token vended
by the BRAXIL Auth Broker. Run `python scripts/connect.py --platform tiktok` once.

This uploads the video FILE directly to TikTok (push_by_file / FILE_UPLOAD), so
NO domain verification is needed (that's only required for pull_by_url). Pass a
local file with --video, or a URL with --video-url (it gets downloaded first).

TikTok gotcha: until your app passes TikTok's audit it can only post to YOUR own
account and the post is forced private, so --privacy defaults to SELF_ONLY; use
--privacy PUBLIC_TO_EVERYONE only once the app is audited."""

import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request

try:
    from broker_client import get_token, http_json, http_bytes, normalize_text, BrokerError
except ImportError:
    from .broker_client import get_token, http_json, http_bytes, normalize_text, BrokerError

INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
CREATOR_INFO_URL = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"

PRIVACY_LEVELS = ["SELF_ONLY", "PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "FOLLOWER_OF_CREATOR"]


def query_creator_info(account=None):
    """Fetch the creator's current posting state from TikTok. REQUIRED by
    TikTok's UX rules before rendering the post form: it tells you the
    creator nickname, which privacy levels are allowed, which interactions
    (comment/duet/stitch) are disabled in their app settings, the max video
    duration, and whether the creator can post right now. Returns the raw
    `data` object from TikTok (see the fields used in SKILL.md)."""
    tok = get_token("tiktok", account=account)
    res = http_json(
        "POST", CREATOR_INFO_URL,
        headers={"Authorization": f"Bearer {tok['accessToken']}",
                 "Content-Type": "application/json; charset=UTF-8"},
        json_body={},
    )
    err = (res or {}).get("error") or {}
    code = err.get("code")
    if code and code != "ok":
        raise BrokerError(f"TikTok creator_info failed ({code}): {err.get('message')}")
    return res.get("data") or {}

MAX_CHUNK = 64 * 1024 * 1024  # 64 MB — TikTok's max chunk size.


def _read_video_bytes(video_path=None, video_url=None):
    """Return (bytes, content_type). Reads a local file or downloads a URL."""
    if video_path:
        if not os.path.isfile(video_path):
            raise BrokerError(f"video not found: {video_path}")
        with open(video_path, "rb") as f:
            data = f.read()
        ctype = mimetypes.guess_type(video_path)[0] or "video/mp4"
        return data, ctype
    if video_url:
        try:
            with urllib.request.urlopen(video_url, timeout=300) as resp:
                data = resp.read()
                ctype = resp.headers.get("Content-Type") or mimetypes.guess_type(video_url)[0] or "video/mp4"
                return data, ctype
        except urllib.error.URLError as e:
            raise BrokerError(f"could not download --video-url ({video_url}): {e}")
    raise BrokerError("provide --video <local file> or --video-url <url>")


def _chunk_plan(video_size):
    """TikTok chunking: a single chunk for <=64MB, else 64MB chunks with the
    final chunk absorbing the remainder."""
    if video_size <= MAX_CHUNK:
        return video_size, 1
    chunk_size = MAX_CHUNK
    total = video_size // chunk_size  # last chunk absorbs the remainder
    return chunk_size, total


def _upload_chunks(upload_url, data, ctype):
    video_size = len(data)
    chunk_size, total = _chunk_plan(video_size)
    for i in range(total):
        start = i * chunk_size
        end = video_size - 1 if i == total - 1 else start + chunk_size - 1
        chunk = data[start:end + 1]
        http_bytes(
            "PUT", upload_url,
            headers={
                "Content-Type": ctype,
                "Content-Range": f"bytes {start}-{end}/{video_size}",
            },
            data=chunk,
        )


def _wait_for_status(tok, publish_id, tries=12, interval=3):
    """Poll publish status a few times to surface processing errors early."""
    for _ in range(tries):
        res = http_json(
            "POST", STATUS_URL,
            headers={"Authorization": f"Bearer {tok['accessToken']}",
                     "Content-Type": "application/json; charset=UTF-8"},
            json_body={"publish_id": publish_id},
        )
        status = (res.get("data") or {}).get("status")
        if status in ("PUBLISH_COMPLETE", "FAILED"):
            return status, res
        time.sleep(interval)
    return "PROCESSING", {}


def post_to_tiktok(title, video_path=None, video_url=None, account=None, privacy="SELF_ONLY",
                   allow_comment=False, allow_duet=False, allow_stitch=False,
                   your_brand=False, branded_content=False):
    title = normalize_text(title)

    # Commercial-content / privacy compliance (TikTok UX rules):
    # branded content (paid partnership) can NOT be posted as private.
    if branded_content and privacy == "SELF_ONLY":
        raise BrokerError(
            "Branded content cannot be private. TikTok forbids 'SELF_ONLY' visibility "
            "for branded content — pick PUBLIC_TO_EVERYONE or MUTUAL_FOLLOW_FRIENDS, "
            "or drop the branded-content disclosure."
        )

    tok = get_token("tiktok", account=account)
    data, ctype = _read_video_bytes(video_path, video_url)
    video_size = len(data)
    chunk_size, total = _chunk_plan(video_size)

    init = http_json(
        "POST", INIT_URL,
        headers={"Authorization": f"Bearer {tok['accessToken']}",
                 "Content-Type": "application/json; charset=UTF-8"},
        json_body={
            "post_info": {
                "title": title,
                "privacy_level": privacy,
                # Interactions are OFF unless the user explicitly enabled them
                # in the form (TikTok rule: none checked by default).
                "disable_comment": not allow_comment,
                "disable_duet": not allow_duet,
                "disable_stitch": not allow_stitch,
                # Commercial-content disclosure. brand_organic = "Your brand"
                # (Promotional content); brand_content = "Branded content"
                # (Paid partnership). Both default off.
                "brand_organic_toggle": bool(your_brand),
                "brand_content_toggle": bool(branded_content),
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": video_size,
                "chunk_size": chunk_size,
                "total_chunk_count": total,
            },
        },
    )

    err = (init or {}).get("error") or {}
    code = err.get("code")
    if code and code != "ok":
        if code in ("unaudited_client_can_only_post_to_private_accounts", "scope_not_authorized"):
            raise BrokerError(
                "TikTok rejected the post: an unaudited app can only post privately "
                "(SELF_ONLY) to its own account. Use --privacy SELF_ONLY until the app "
                f"passes TikTok's audit. TikTok message: {err.get('message')}"
            )
        raise BrokerError(f"TikTok init failed ({code}): {err.get('message')}")

    info = init.get("data") or {}
    upload_url = info.get("upload_url")
    publish_id = info.get("publish_id")
    if not upload_url or not publish_id:
        raise BrokerError(f"TikTok init returned no upload_url/publish_id: {init}")

    _upload_chunks(upload_url, data, ctype)

    status, _ = _wait_for_status(tok, publish_id)
    note = " (private — visible only to you until the app is audited)" if privacy == "SELF_ONLY" else ""
    if status == "FAILED":
        raise BrokerError(f"TikTok reported the publish FAILED (publish_id={publish_id}).")
    state = "published" if status == "PUBLISH_COMPLETE" else "uploaded, still processing"
    print(f"✅ TikTok video {state} (publish_id={publish_id}){note}.")
    return {"publish_id": publish_id, "status": status}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post a video to TikTok (direct file upload) via the BRAXIL broker.")
    parser.add_argument("--creator-info", action="store_true",
                        help="Query and print (JSON) the creator's posting state — nickname, "
                             "allowed privacy levels, disabled interactions, max video duration. "
                             "MUST be fetched before building the post form (see SKILL.md).")
    parser.add_argument("--video", help="Local video file (.mp4/.mov)")
    parser.add_argument("--video-url", help="Video URL to download then upload (.mp4/.mov)")
    parser.add_argument("--title", help="Video title/caption (ask the user — never invent it)")
    parser.add_argument("--privacy", choices=PRIVACY_LEVELS, default="SELF_ONLY",
                        help="Visibility. The user MUST pick this from the privacy_level_options "
                             "returned by --creator-info (no default in the UX). Falls back to "
                             "SELF_ONLY for safety, but always pass the user's explicit choice.")
    parser.add_argument("--account", help="Which connected TikTok account — needed when you manage several")
    # Interactions — OFF unless the user turns them on (TikTok: none checked by default).
    parser.add_argument("--allow-comment", action="store_true", help="User enabled comments")
    parser.add_argument("--allow-duet", action="store_true", help="User enabled Duet (video only)")
    parser.add_argument("--allow-stitch", action="store_true", help="User enabled Stitch (video only)")
    # Commercial-content disclosure — OFF unless the user discloses it.
    parser.add_argument("--your-brand", action="store_true",
                        help="'Your brand' — promoting yourself/your business (Promotional content)")
    parser.add_argument("--branded-content", action="store_true",
                        help="'Branded content' — promoting a third party (Paid partnership). "
                             "Cannot be private.")
    args = parser.parse_args()

    if args.creator_info:
        try:
            print(json.dumps(query_creator_info(account=args.account), indent=2))
        except BrokerError as e:
            print(f"❌ {e}")
            sys.exit(1)
        sys.exit(0)

    if not args.title:
        parser.error("--title is required to post (ask the user for the Reel title first)")
    if not args.video and not args.video_url:
        parser.error("provide --video <local file> or --video-url <url>")
    try:
        post_to_tiktok(args.title, video_path=args.video, video_url=args.video_url,
                       account=args.account, privacy=args.privacy,
                       allow_comment=args.allow_comment, allow_duet=args.allow_duet,
                       allow_stitch=args.allow_stitch, your_brand=args.your_brand,
                       branded_content=args.branded_content)
    except BrokerError as e:
        print(f"❌ {e}")
        sys.exit(1)
