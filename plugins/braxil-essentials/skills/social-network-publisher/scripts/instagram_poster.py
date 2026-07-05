"""Instagram publishing lives under Meta's Graph API — see meta_poster.py.
This thin shim forwards to it so existing callers keep working."""

import argparse
import sys

try:
    from meta_poster import post_to_instagram
    from broker_client import BrokerError
except ImportError:
    from .meta_poster import post_to_instagram
    from .broker_client import BrokerError

__all__ = ["post_to_instagram"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post an image or video (Reel) to Instagram via the BRAXIL broker.")
    parser.add_argument("--image", help="Local image file (hosted automatically to a public URL)")
    parser.add_argument("--image-url", help="Public image URL — alternative to --image")
    parser.add_argument("--video", help="Local video file → posted as a Reel (hosted automatically)")
    parser.add_argument("--video-url", help="Public video URL — alternative to --video")
    parser.add_argument("--caption", default="", help="Caption")
    parser.add_argument("--page", help="Facebook page id linked to the IG account (optional)")
    parser.add_argument("--account", help="Which connected Meta login (optional)")
    args = parser.parse_args()
    if not args.image and not args.image_url and not args.video and not args.video_url:
        parser.error("provide --image/--video (local file) or --image-url/--video-url (public url)")
    try:
        post_to_instagram(image_url=args.image_url, image=args.image, caption=args.caption,
                          page=args.page, account=args.account,
                          video=args.video, video_url=args.video_url)
    except BrokerError as e:
        print(f"❌ {e}")
        sys.exit(1)
