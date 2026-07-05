"""Publish to LinkedIn — your personal profile OR a Company Page you administer
— with text and/or media (images, a video, or a PDF/document), using a token
vended by the BRAXIL Auth Broker. Run `python scripts/connect.py --platform
linkedin` once first.

  python scripts/linkedin_poster.py --list-orgs
  python scripts/linkedin_poster.py --text "hi" --org "BRAXIL"        # post as the page
  python scripts/linkedin_poster.py --text "hi"                       # post as yourself
  python scripts/linkedin_poster.py --text "look" --image a.png --image b.png
  python scripts/linkedin_poster.py --text "demo" --video clip.mp4
  python scripts/linkedin_poster.py --text "deck" --document slides.pdf

Media rules (LinkedIn allows ONE category per post):
  - up to 9 images, OR
  - exactly 1 video, OR
  - exactly 1 document (PDF/DOC/PPT...) rendered as a swipeable carousel.

Images/video use LinkedIn's Vector Asset flow on the legacy UGC Posts API
(registerUpload -> PUT the bytes -> reference the asset in the ugcPost).
Documents use the versioned Documents + Posts API (/rest/documents +
/rest/posts), which is a different surface. Stdlib only (urllib)."""

import argparse
import mimetypes
import os
import sys

try:
    from broker_client import get_token, http_json, http_bytes, normalize_text, BrokerError
except ImportError:
    from .broker_client import get_token, http_json, http_bytes, normalize_text, BrokerError

API = "https://api.linkedin.com"
# Versioned APIs (Documents/Posts) require a LinkedIn-Version header (YYYYMM).
# LinkedIn keeps a ROLLING ~12-month window and retires the OLDEST months first,
# so this must track a RECENT month — never an older one (202405/202404 are
# retired). When LinkedIn rejects a call with an "unsupported version" error,
# bump this to a current month (or set the LINKEDIN_API_VERSION env var, which
# overrides it without a code change).
LINKEDIN_VERSION = os.environ.get("LINKEDIN_API_VERSION", "202506")

# registerUpload recipe + ugcPost shareMediaCategory per media kind.
_RECIPES = {
    "image": ("urn:li:digitalmediaRecipe:feedshare-image", "IMAGE"),
    "video": ("urn:li:digitalmediaRecipe:feedshare-video", "VIDEO"),
}


def _li_headers(tok, version=None):
    h = {"Authorization": f"Bearer {tok['accessToken']}", "X-Restli-Protocol-Version": "2.0.0"}
    if version:
        h["LinkedIn-Version"] = version
    return h


def _resolve_author(tok, org):
    """Return the URN to post AS: the member (personal) or an organization the
    user administers. `org` may be the Page name or its numeric id."""
    ids = tok.get("ids") or {}
    if not org:
        urn = ids.get("memberUrn")
        if not urn:
            raise BrokerError("LinkedIn member URN missing — reconnect with connect.py --platform linkedin")
        return urn
    orgs = ids.get("organizations") or []
    needle = str(org).strip().lstrip("@").lower()
    for o in orgs:
        if str(o.get("id")).lower() == needle or str(o.get("name") or "").lower() == needle:
            return f"urn:li:organization:{o.get('id')}"
    if needle.isdigit():
        return f"urn:li:organization:{needle}"
    available = ", ".join(f"{o.get('name')} ({o.get('id')})" for o in orgs) or "(none discovered — pass the numeric org id)"
    raise BrokerError(f"organization '{org}' not found. Pages you administer: {available}")


def _register_upload(tok, owner, recipe):
    body = {
        "registerUploadRequest": {
            "recipes": [recipe],
            "owner": owner,  # person OR organization URN — must match the post author
            "serviceRelationships": [
                {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
            ],
        }
    }
    res = http_json("POST", f"{API}/v2/assets?action=registerUpload", headers=_li_headers(tok), json_body=body)
    value = res.get("value") or {}
    asset = value.get("asset")
    mech = (value.get("uploadMechanism") or {}).get(
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ) or {}
    upload_url = mech.get("uploadUrl")
    if not asset or not upload_url:
        raise BrokerError(f"LinkedIn registerUpload failed: {res}")
    return asset, upload_url


def _upload_bytes(tok, upload_url, path, default_ctype):
    """PUT the raw file bytes to a LinkedIn upload URL (images, video, docs all
    use the same documented single-PUT mechanism)."""
    if not os.path.isfile(path):
        raise BrokerError(f"file not found: {path}")
    with open(path, "rb") as f:
        data = f.read()
    ctype = mimetypes.guess_type(path)[0] or default_ctype
    http_bytes("PUT", upload_url,
               headers={"Authorization": f"Bearer {tok['accessToken']}", "Content-Type": ctype},
               data=data)


def _upload_asset(tok, owner, path, kind):
    """registerUpload + PUT bytes for an image/video. Returns the asset URN."""
    recipe, _ = _RECIPES[kind]
    asset, upload_url = _register_upload(tok, owner, recipe)
    _upload_bytes(tok, upload_url, path, "image/png" if kind == "image" else "video/mp4")
    return asset


def list_orgs(account: str = None):
    tok = get_token("linkedin", account=account)
    orgs = (tok.get("ids") or {}).get("organizations") or []
    if not orgs:
        print("No admin Company Pages found (grant 'Community Management API' / r_organization_admin, "
              "or pass the numeric org id to --org).")
        return
    print("Company Pages you administer (use --org <id|name>):")
    for o in orgs:
        print(f"  - {o.get('name')}  (id={o.get('id')})")


def _post_ugc(tok, author, text, media, category):
    """Create a post on the legacy UGC Posts API (images / video / text-only)."""
    share = {
        "shareCommentary": {"text": text or ""},
        "shareMediaCategory": category,
    }
    if media:
        share["media"] = media
    body = {
        "author": author,
        "lifecycleState": "PUBLISHED",
        "specificContent": {"com.linkedin.ugc.ShareContent": share},
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    return http_json("POST", f"{API}/v2/ugcPosts", headers=_li_headers(tok), json_body=body)


def _post_document(tok, author, text, path):
    """Publish a PDF/document carousel via the versioned Documents + Posts API.
    The legacy ugcPosts/registerUpload flow does NOT handle documents."""
    if not os.path.isfile(path):
        raise BrokerError(f"document not found: {path}")
    # 1. initializeUpload -> { value: { document, uploadUrl } }
    init = http_json(
        "POST", f"{API}/rest/documents?action=initializeUpload",
        headers=_li_headers(tok, version=LINKEDIN_VERSION),
        json_body={"initializeUploadRequest": {"owner": author}},
    )
    value = init.get("value") or {}
    doc_urn = value.get("document")
    upload_url = value.get("uploadUrl")
    if not doc_urn or not upload_url:
        raise BrokerError(f"LinkedIn document initializeUpload failed: {init}")
    # 2. PUT the bytes
    _upload_bytes(tok, upload_url, path, "application/pdf")
    # 3. create the post referencing the document URN
    title = os.path.splitext(os.path.basename(path))[0]
    body = {
        "author": author,
        "commentary": text or "",
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "content": {"media": {"id": doc_urn, "title": title}},
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    return http_json("POST", f"{API}/rest/posts",
                     headers=_li_headers(tok, version=LINKEDIN_VERSION), json_body=body)


def post_to_linkedin(text: str = None, images=None, video: str = None,
                     document: str = None, account: str = None, org: str = None):
    images = images or []
    text = normalize_text(text)

    # LinkedIn permits ONE media category per post.
    categories = [bool(images), bool(video), bool(document)]
    if sum(categories) > 1:
        raise BrokerError("LinkedIn allows EITHER images OR one video OR one document per post — not a mix.")
    if len(images) > 9:
        raise BrokerError("LinkedIn allows at most 9 images per post.")
    if not text and not images and not video and not document:
        raise BrokerError("Nothing to post: provide --text and/or --image/--video/--document.")

    tok = get_token("linkedin", account=account)
    author = _resolve_author(tok, org)  # person URN or organization URN
    where = f"page '{org}'" if org else "personal profile"

    # Documents take the separate versioned Posts API path.
    if document:
        _post_document(tok, author, text, document)
        print(f"✅ Posted to LinkedIn {where} with document '{os.path.basename(document)}'.")
        return

    media = []
    category = "NONE"
    if video:
        media.append({"status": "READY", "media": _upload_asset(tok, author, video, "video")})
        category = "VIDEO"
    elif images:
        for p in images:
            media.append({"status": "READY", "media": _upload_asset(tok, author, p, "image")})
        category = "IMAGE"

    res = _post_ugc(tok, author, text, media, category)
    if video:
        extra = " with 1 video"
    elif media:
        extra = f" with {len(media)} image(s)"
    else:
        extra = ""
    print(f"✅ Posted to LinkedIn {where} (id={res.get('id')}){extra}.")
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post text and/or media (images, video, or a document) to LinkedIn (profile or Company Page) via the BRAXIL broker.")
    parser.add_argument("--text", help="Text to post (optional when media is provided)")
    parser.add_argument("--image", action="append", default=[], metavar="PATH", help="Local image to attach (repeatable, up to 9). Cannot combine with --video/--document.")
    parser.add_argument("--video", metavar="PATH", help="Local video to attach (1 max). Cannot combine with --image/--document.")
    parser.add_argument("--document", metavar="PATH", help="Local document (PDF/DOC/PPT…) shown as a swipeable carousel (1 max). Cannot combine with --image/--video.")
    parser.add_argument("--org", help="Post AS a Company Page you administer (id or name). Omit to post as your personal profile.")
    parser.add_argument("--account", help="Which connected LinkedIn account — needed when you manage several")
    parser.add_argument("--list-orgs", action="store_true", help="List the Company Pages you can post to and exit")
    args = parser.parse_args()
    try:
        if args.list_orgs:
            list_orgs(account=args.account)
            sys.exit(0)
        if not args.text and not args.image and not args.video and not args.document:
            parser.error("provide --text and/or --image/--video/--document")
        post_to_linkedin(args.text, images=args.image, video=args.video,
                         document=args.document, account=args.account, org=args.org)
    except BrokerError as e:
        print(f"❌ {e}")
        sys.exit(1)
