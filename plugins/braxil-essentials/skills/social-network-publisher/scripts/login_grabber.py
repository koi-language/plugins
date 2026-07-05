"""DEPRECATED. Browser-cookie grabbing has been replaced by the official OAuth
"Auth Broker" flow. Connect accounts with:

    python scripts/connect.py --platform x   # x | linkedin | meta | tiktok

Tokens are stored securely server-side by the BRAXIL backend — no local cookies."""

import sys

if __name__ == "__main__":
    print(__doc__)
    sys.exit(1)
