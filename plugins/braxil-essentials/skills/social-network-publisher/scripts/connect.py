"""Connect a social account to BRAXIL (one-click OAuth via the Auth Broker).

    python scripts/connect.py --platform x        # x | linkedin | meta | tiktok | youtube | threads | pinterest

Opens the system browser to the official authorization page. After you grant
access, the BRAXIL backend exchanges the code, stores your tokens securely
(server-side, encrypted) and this script confirms the connection. Nothing
secret is stored on this machine.
"""

from __future__ import annotations  # keep type hints lazy so `str | None` works on Python 3.7+

import argparse
import sys
import webbrowser

try:
    from broker_client import start_connect, poll_status, list_connections, disconnect, BrokerError
except ImportError:  # when imported as a package module
    from .broker_client import start_connect, poll_status, list_connections, disconnect, BrokerError

PLATFORMS = ["x", "linkedin", "meta", "tiktok", "youtube", "threads", "pinterest"]


def show_connections() -> int:
    try:
        conns = list_connections()
    except BrokerError as e:
        print(f"❌ {e}")
        return 1
    if not conns:
        print("No social accounts connected yet.")
        return 0
    print("Connected accounts:")
    for c in conns:
        print(f"  - {c.get('platform')}: {c.get('account')}  (id={c.get('providerAccountId')})")
    return 0


def disconnect_account(platform: str, account: str | None) -> int:
    try:
        disconnect(platform, account=account)
    except BrokerError as e:
        print(f"❌ Could not disconnect: {e}")
        return 1
    who = f"{platform} account '{account}'" if account else f"ALL {platform} accounts"
    print(f"✅ Disconnected {who}.")
    return 0


def connect(platform: str) -> int:
    try:
        started = start_connect(platform)
    except BrokerError as e:
        print(f"❌ Could not start the connection: {e}")
        return 1

    auth_url = started.get("authUrl")
    state = started.get("state")
    if not auth_url or not state:
        print(f"❌ Unexpected response from the broker: {started}")
        return 1

    print(f"Opening your browser to authorize {platform}…")
    print(auth_url)
    try:
        webbrowser.open(auth_url)
    except Exception:
        print("(Could not open the browser automatically — copy the URL above.)")

    print("Waiting for you to finish signing in…")
    res = poll_status(platform, state)
    status = res.get("status")

    if status == "connected":
        print(f"✅ Connected to {platform}.")
        return 0
    if status == "timeout":
        print("⏱️  Timed out waiting for authorization. Run the command again to retry.")
        return 1
    print(f"❌ Connection {status}: {res.get('errorMessage', '')}".rstrip(": "))
    return 1


def main():
    parser = argparse.ArgumentParser(description="Connect a social account via BRAXIL.")
    parser.add_argument("--platform", choices=PLATFORMS, help="Platform to connect (or disconnect)")
    parser.add_argument("--list", action="store_true", help="List already-connected accounts and exit")
    parser.add_argument("--disconnect", action="store_true",
                        help="Disconnect a connected account instead of connecting. "
                             "Use with --platform; add --account to pick one, or omit it to remove ALL of that platform.")
    parser.add_argument("--account", help="Which account to act on (a @handle, display name, or id) — for --disconnect.")
    args = parser.parse_args()
    if args.list:
        sys.exit(show_connections())
    if args.disconnect:
        if not args.platform:
            parser.error("--disconnect requires --platform (and optionally --account)")
        sys.exit(disconnect_account(args.platform, args.account))
    if not args.platform:
        parser.error("--platform is required (or use --list / --disconnect)")
    # Connect another account of the same platform by running this again while
    # signed into that account in your browser (multiple accounts are supported).
    sys.exit(connect(args.platform))


if __name__ == "__main__":
    main()
