"""Publish a Pin to Pinterest — an image with a title/description, on one of
your boards — using a token vended by the BRAXIL Auth Broker. Run
`python scripts/connect.py --platform pinterest` once first.

  python scripts/pinterest_poster.py --list-boards
  python scripts/pinterest_poster.py --image pin.png --title "My pin" --description "..." --board "Inspiration"
  python scripts/pinterest_poster.py --image-url https://… --title "My pin" --board 123456 --link https://site.com

A Pin needs a BOARD and an IMAGE. Local images are hosted on the BRAXIL media
CDN first (Pinterest only accepts a public URL). Stdlib only (urllib)."""

import argparse
import sys

try:
    from broker_client import get_token, http_json, host_media, normalize_text, BrokerError
except ImportError:
    from .broker_client import get_token, http_json, host_media, normalize_text, BrokerError

API = "https://api.pinterest.com/v5"


def _auth(access_token):
    return {"Authorization": f"Bearer {access_token}"}


def _list_boards(access_token):
    res = http_json("GET", f"{API}/boards?page_size=100", headers=_auth(access_token))
    return res.get("items") or []


def _resolve_board(access_token, board):
    boards = _list_boards(access_token)
    if not boards:
        raise BrokerError("You have no Pinterest boards yet — create one in Pinterest first, then retry.")
    if not board:
        if len(boards) == 1:
            return boards[0]["id"]
        names = ", ".join(f'"{b.get("name")}"' for b in boards)
        raise BrokerError(f"You have several boards — pass --board <name|id>. Available: {names}")
    needle = str(board).strip().lstrip("@").lower()
    for b in boards:
        if str(b.get("id")).lower() == needle or str(b.get("name") or "").lower() == needle:
            return b["id"]
    raise BrokerError(f"Board '{board}' not found. Use --list-boards to see them.")


def post_to_pinterest(image=None, image_url=None, title="", description="", link=None, board=None, account=None):
    img = image_url or (host_media(image) if image else None)
    if not img:
        raise BrokerError("Pinterest needs an image: pass --image (local) or --image-url (public).")
    tok = get_token("pinterest", account=account)
    access_token = tok["accessToken"]
    board_id = _resolve_board(access_token, board)
    body = {
        "board_id": board_id,
        "title": normalize_text(title) or None,
        "description": normalize_text(description) or None,
        "media_source": {"source_type": "image_url", "url": img},
    }
    if link:
        body["link"] = link
    body = {k: v for k, v in body.items() if v is not None}
    res = http_json("POST", f"{API}/pins", headers=_auth(access_token), json_body=body)
    pin_id = res.get("id")
    if not pin_id:
        raise BrokerError(f"Pinterest pin failed: {res}")
    print(f"✅ Posted Pin to Pinterest (id={pin_id}, board={board_id}).")
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Post a Pin to Pinterest via the BRAXIL broker.")
    parser.add_argument("--list-boards", action="store_true", help="List your boards (id + name) and exit")
    parser.add_argument("--image", help="Local image file (hosted automatically to a public URL)")
    parser.add_argument("--image-url", help="Public image URL — alternative to --image")
    parser.add_argument("--title", default="", help="Pin title")
    parser.add_argument("--description", default="", help="Pin description")
    parser.add_argument("--link", help="Destination link for the pin (optional)")
    parser.add_argument("--board", help="Board name or id to pin to (required when you have several)")
    parser.add_argument("--account", help="Which connected Pinterest account (optional)")
    args = parser.parse_args()
    try:
        if args.list_boards:
            tok = get_token("pinterest", account=args.account)
            boards = _list_boards(tok["accessToken"])
            if not boards:
                print("(no boards yet — create one in Pinterest)")
            for b in boards:
                print(f"  - {b.get('name')}  (id={b.get('id')})")
            sys.exit(0)
        if not args.image and not args.image_url:
            parser.error("provide --image or --image-url (a Pin requires an image)")
        post_to_pinterest(image=args.image, image_url=args.image_url, title=args.title,
                          description=args.description, link=args.link, board=args.board, account=args.account)
    except BrokerError as e:
        print(f"❌ {e}")
        sys.exit(1)
