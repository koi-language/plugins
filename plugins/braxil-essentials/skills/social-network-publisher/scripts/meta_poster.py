"""Publish to Facebook Pages and Instagram (Business) via the Graph API, using
tokens vended by the BRAXIL Auth Broker. The broker returns the correct PAGE
access token + the IG business id for the selected page.

Run `python scripts/connect.py --platform meta` once first. Pass `page=<id>` to
target a specific Facebook page when you manage several.

Media: Facebook supports text, image and video; Instagram supports image and
video (Reels). Local files are hosted on the BRAXIL media CDN first, because the
Graph API only accepts a PUBLIC url for photos/videos."""

import argparse
import sys
import time

try:
    from broker_client import get_token, http_json, host_media, normalize_text, BrokerError
except ImportError:
    from .broker_client import get_token, http_json, host_media, normalize_text, BrokerError

GRAPH = "https://graph.facebook.com/v19.0"


def _public_url(url: str = None, local: str = None):
    """Return a public URL for a media asset: pass a url through, or host a
    local file on the BRAXIL CDN to obtain one."""
    if url:
        return url
    if local:
        return host_media(local)  # local → public URL (backend must have media hosting configured)
    return None


def post_to_facebook(text: str = "", page: str = None, account: str = None,
                     image: str = None, image_url: str = None,
                     video: str = None, video_url: str = None):
    text = normalize_text(text)
    tok = get_token("meta", page=page, account=account)
    ids = tok.get("ids") or {}
    page_id = ids.get("pageId")
    if not page_id:
        raise BrokerError("No Facebook page connected — reconnect with connect.py --platform meta")
    access_token = tok["accessToken"]

    # Validate exclusivity BEFORE hosting any local file (host_media uploads).
    if (image or image_url) and (video or video_url):
        raise BrokerError("Facebook: post EITHER a photo OR a video, not both.")
    img = _public_url(image_url, image)
    vid = _public_url(video_url, video)

    if vid:
        # Video → /{page}/videos. `file_url` must be a public URL.
        res = http_json(
            "POST", f"{GRAPH}/{page_id}/videos",
            form_body={"file_url": vid, "description": text, "access_token": access_token},
        )
        print(f"✅ Posted video to Facebook page {page_id} (id={res.get('id')}).")
        return res
    if img:
        # Photo → /{page}/photos. `url` must be a public URL; `caption` is the text.
        res = http_json(
            "POST", f"{GRAPH}/{page_id}/photos",
            form_body={"url": img, "caption": text, "access_token": access_token},
        )
        print(f"✅ Posted photo to Facebook page {page_id} (id={res.get('id') or res.get('post_id')}).")
        return res

    # Text-only feed post.
    res = http_json(
        "POST", f"{GRAPH}/{page_id}/feed",
        form_body={"message": text, "access_token": access_token},
    )
    print(f"✅ Posted to Facebook page {page_id} (id={res.get('id')}).")
    return res


def _wait_ig_container(ig_id, container_id, access_token, tries=30, interval=4):
    """IG video/Reels containers must finish processing before publish. Poll
    the container's status_code until FINISHED (or surface an error)."""
    for _ in range(tries):
        st = http_json(
            "GET", f"{GRAPH}/{container_id}?fields=status_code&access_token={access_token}",
        )
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise BrokerError(f"Instagram media processing {code} (container={container_id}).")
        time.sleep(interval)
    raise BrokerError(f"Instagram media still processing after timeout (container={container_id}).")


def post_to_instagram(image_url: str = None, caption: str = "", page: str = None,
                      account: str = None, image: str = None,
                      video: str = None, video_url: str = None):
    # The IG Graph API only accepts a PUBLIC media URL. Local files are hosted
    # on the BRAXIL media CDN first to obtain one. Validate exclusivity/presence
    # BEFORE hosting any local file (host_media uploads).
    if (image or image_url) and (video or video_url):
        raise BrokerError("Instagram: post EITHER an image OR a video (Reel), not both.")
    if not image and not image_url and not video and not video_url:
        raise BrokerError("Instagram needs media: pass --image/--video (local file) or --image-url/--video-url.")
    img = _public_url(image_url, image)
    vid = _public_url(video_url, video)
    caption = normalize_text(caption)

    tok = get_token("meta", page=page, account=account)
    ids = tok.get("ids") or {}
    ig_id = ids.get("igBusinessId")
    if not ig_id:
        raise BrokerError("No Instagram Business account is linked to the selected Facebook page.")
    access_token = tok["accessToken"]

    # Step 1: create the media container.
    if vid:
        # Video is published as a Reel (the only supported IG video container).
        form = {"media_type": "REELS", "video_url": vid, "caption": caption, "access_token": access_token}
    else:
        form = {"image_url": img, "caption": caption, "access_token": access_token}
    container = http_json("POST", f"{GRAPH}/{ig_id}/media", form_body=form)
    creation_id = container.get("id")
    if not creation_id:
        raise BrokerError(f"Instagram media container failed: {container}")

    # Step 2 (video only): wait for the container to finish processing.
    if vid:
        _wait_ig_container(ig_id, creation_id, access_token)

    # Step 3: publish it.
    res = http_json(
        "POST", f"{GRAPH}/{ig_id}/media_publish",
        form_body={"creation_id": creation_id, "access_token": access_token},
    )
    kind = "Reel" if vid else "image"
    print(f"✅ Posted {kind} to Instagram {ig_id} (id={res.get('id')}).")
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post to Facebook/Instagram via the BRAXIL broker.")
    parser.add_argument("--target", choices=["facebook", "instagram"], default="facebook")
    parser.add_argument("--text", help="Text (Facebook) / caption (Instagram)")
    parser.add_argument("--image", help="Local image file — hosted automatically to a public URL")
    parser.add_argument("--image-url", help="Public image URL — alternative to --image")
    parser.add_argument("--video", help="Local video file — hosted automatically to a public URL (IG → Reel)")
    parser.add_argument("--video-url", help="Public video URL — alternative to --video")
    parser.add_argument("--page", help="Facebook page id (optional)")
    parser.add_argument("--account", help="Which connected Meta login — needed when you connect several")
    args = parser.parse_args()
    try:
        if args.target == "facebook":
            post_to_facebook(args.text or "", page=args.page, account=args.account,
                             image=args.image, image_url=args.image_url,
                             video=args.video, video_url=args.video_url)
        else:
            post_to_instagram(image_url=args.image_url, image=args.image, caption=args.text or "",
                              page=args.page, account=args.account,
                              video=args.video, video_url=args.video_url)
    except BrokerError as e:
        print(f"❌ {e}")
        sys.exit(1)
