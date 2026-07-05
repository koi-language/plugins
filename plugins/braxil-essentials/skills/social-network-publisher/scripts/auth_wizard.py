"""DEPRECATED. The local Flask OAuth proof-of-concept is superseded by the
official "Auth Broker" hosted in the BRAXIL backend. Client Secrets are never
stored on this machine. Connect accounts with:

    python scripts/connect.py --platform x   # x | linkedin | meta | tiktok"""

import sys

if __name__ == "__main__":
    print(__doc__)
    sys.exit(1)
