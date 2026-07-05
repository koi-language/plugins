"""Upload a video to YouTube using a token vended by the BRAXIL Auth Broker.
Run `python scripts/connect.py --platform youtube` once first.

  python scripts/youtube_poster.py --video clip.mp4 --title "My video" --description "..." --privacy public
  python scripts/youtube_poster.py --video short.mp4 --title "My Short #Shorts" --tags shorts,demo

YouTube only publishes VIDEO (there is no "text post"). A vertical clip ≤60s
with #Shorts in the title/description is surfaced as a Short. Uses the YouTube
Data API v3 resumable-upload protocol (init → PUT bytes). Stdlib only (urllib)
— we talk to Google directly here because the resumable-init reply carries the
upload URL in the `Location` HEADER, which the broker's JSON helper can't expose.

NOTE: while your Google Cloud project is unverified (OAuth consent screen in
"testing", or pending audit), YouTube forces every uploaded video to PRIVATE
regardless of --privacy. Once Google verifies the app, public/unlisted work."""

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

try:
    from broker_client import get_token, normalize_text, BrokerError
except ImportError:
    from .broker_client import get_token, normalize_text, BrokerError

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

INIT_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"


def post_to_youtube(video, title="", description="", tags=None, privacy="public",
                    category_id="22", account=None):
    if not video or not os.path.isfile(video):
        raise BrokerError(f"video file not found: {video}")
    if privacy not in ("public", "unlisted", "private"):
        raise BrokerError("privacy must be public | unlisted | private")
    title = (normalize_text(title) or os.path.basename(video))[:100]
    description = normalize_text(description) or ""
    tags = [t.strip() for t in (tags or []) if t.strip()]

    tok = get_token("youtube", account=account)
    access_token = tok["accessToken"]

    metadata = {
        "snippet": {"title": title, "description": description, "categoryId": category_id},
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }
    if tags:
        metadata["snippet"]["tags"] = tags
    body = json.dumps(metadata).encode("utf-8")
    size = os.path.getsize(video)

    # Step 1: open a resumable session — the upload URL returns in `Location`.
    init = urllib.request.Request(INIT_URL, data=body, method="POST", headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": "video/*",
        "X-Upload-Content-Length": str(size),
    })
    try:
        with urllib.request.urlopen(init, timeout=60) as resp:
            upload_url = resp.headers.get("Location")
    except urllib.error.HTTPError as e:
        raise BrokerError(f"YouTube init failed -> {e.code}: {e.read().decode('utf-8', 'ignore')[:400]}")
    except urllib.error.URLError as e:
        raise BrokerError(f"YouTube init failed: {e}")
    if not upload_url:
        raise BrokerError("YouTube did not return a resumable upload URL")

    # Step 2: PUT the bytes in one request (fine for typical short videos).
    with open(video, "rb") as f:
        data = f.read()
    put = urllib.request.Request(upload_url, data=data, method="PUT", headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "video/*",
        "Content-Length": str(size),
    })
    try:
        with urllib.request.urlopen(put, timeout=900) as resp:
            res = json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        raise BrokerError(f"YouTube upload failed -> {e.code}: {e.read().decode('utf-8', 'ignore')[:400]}")
    except urllib.error.URLError as e:
        raise BrokerError(f"YouTube upload failed: {e}")
    vid_id = res.get("id")
    if not vid_id:
        raise BrokerError(f"YouTube upload returned no video id: {res}")
    final_privacy = (res.get("status") or {}).get("privacyStatus", privacy)
    print(f"✅ Uploaded to YouTube: https://youtu.be/{vid_id}  (privacy={final_privacy})")
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a video to YouTube via the BRAXIL broker.")
    parser.add_argument("--video", required=True, help="Local video file to upload")
    parser.add_argument("--title", default="", help="Video title (defaults to the file name)")
    parser.add_argument("--description", default="", help="Video description")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--privacy", default="public", choices=["public", "unlisted", "private"])
    parser.add_argument("--category-id", default="22", help="YouTube category id (default 22 = People & Blogs)")
    parser.add_argument("--account", help="Which connected YouTube channel (optional)")
    args = parser.parse_args()
    try:
        post_to_youtube(video=args.video, title=args.title, description=args.description,
                        tags=args.tags.split(",") if args.tags else None,
                        privacy=args.privacy, category_id=args.category_id, account=args.account)
    except BrokerError as e:
        print(f"❌ {e}")
        sys.exit(1)
