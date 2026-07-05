"""Thin client for the BRAXIL social "Auth Broker" (backend).

The backend custodies every social-network OAuth token (encrypted) and the
Client Secrets. This module lets the plugin:
  1. start a one-click connect flow (start_connect + poll_status), and
  2. fetch a SHORT-LIVED access token to publish with (get_token).

Identity: the engine exposes the logged-in user's BRAXIL bearer as the
KOI_AUTH_TOKEN environment variable (inherited by this subprocess) and the API
base as KOI_API_URL. We never see Client Secrets nor the durable refresh token.

Stdlib only (urllib) — no third-party deps required.
"""

import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE = "https://api.braxil.ai"

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass


class BrokerError(Exception):
    pass


def _base() -> str:
    return (os.environ.get("KOI_API_URL") or DEFAULT_BASE).rstrip("/")


def _bearer() -> str:
    tok = os.environ.get("KOI_AUTH_TOKEN")
    if not tok:
        raise BrokerError(
            "KOI_AUTH_TOKEN is not set — BRAXIL must be logged in. The engine "
            "provides it automatically; run this from inside BRAXIL."
        )
    return tok


def normalize_text(s):
    """Convert LITERAL escape sequences into real characters.

    The agent often emits captions with a literal backslash-n ("line1\\nline2")
    instead of a real newline. Passed through the CLI/JSON verbatim, those two
    characters reach the social network and show up as "\\n" in the post. This
    turns the common ones back into the real control characters."""
    if not s:
        return s
    return (s.replace("\\r\\n", "\n")
             .replace("\\r", "\n")
             .replace("\\n", "\n")
             .replace("\\t", "\t"))


def http_json(method, url, headers=None, json_body=None, form_body=None, timeout=60):
    """Generic JSON/form HTTP call (used for both the broker and the social
    network APIs). Raises BrokerError with the response body on failure."""
    headers = dict(headers or {})
    headers.setdefault("Accept", "application/json")
    data = None
    if json_body is not None:
        data = json.dumps(json_body).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    elif form_body is not None:
        data = urllib.parse.urlencode(form_body).encode("utf-8")
        headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        raise BrokerError(f"{method} {url} -> {e.code}: {body[:400]}")
    except urllib.error.URLError as e:
        raise BrokerError(f"{method} {url} failed: {e}")


def http_bytes(method, url, headers=None, data=b"", timeout=180):
    """Raw-binary HTTP call (e.g. LinkedIn asset upload). Returns parsed JSON
    when the response is JSON, else {}. Raises BrokerError on failure."""
    headers = dict(headers or {})
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "ignore")
            try:
                return json.loads(raw) if raw.strip() else {}
            except ValueError:
                return {}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        raise BrokerError(f"{method} {url} -> {e.code}: {body[:400]}")
    except urllib.error.URLError as e:
        raise BrokerError(f"{method} {url} failed: {e}")


def host_media(path, filename=None, timeout=180):
    """Upload a LOCAL file to the BRAXIL backend, which stores it on the media
    CDN and returns a PUBLIC URL. Needed for platforms (Instagram) whose API
    only accepts a public image/video URL, never a local file. Returns the URL."""
    import mimetypes
    if not os.path.isfile(path):
        raise BrokerError(f"file not found: {path}")
    with open(path, "rb") as f:
        data = f.read()
    name = filename or os.path.basename(path)
    ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
    boundary = "----braxilHost" + os.urandom(8).hex()
    crlf = b"\r\n"
    parts = [
        b"--" + boundary.encode(),
        ('Content-Disposition: form-data; name="file"; filename="%s"' % name).encode(),
        ("Content-Type: %s" % ctype).encode(),
        b"",
        data,
        b"--" + boundary.encode() + b"--",
        b"",
    ]
    res = http_bytes(
        "POST", _base() + "/social/media/host",
        headers={
            "Authorization": f"Bearer {_bearer()}",
            "Content-Type": "multipart/form-data; boundary=" + boundary,
            "Accept": "application/json",
        },
        data=crlf.join(parts), timeout=timeout,
    )
    url = res.get("publicUrl")
    if not url:
        raise BrokerError(f"media host returned no publicUrl: {res}")
    return url


def _broker(method, path, query=None):
    url = _base() + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    return http_json(method, url, headers={"Authorization": f"Bearer {_bearer()}"}, timeout=30)


def start_connect(platform):
    """POST /auth/social/{platform}/start -> { authUrl, state }"""
    return _broker("POST", f"/auth/social/{platform}/start")


def poll_status(platform, state, timeout=300, interval=2):
    """Poll GET /auth/social/{platform}/status until a terminal status.
    Returns the last status dict, or {'status': 'timeout'}."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        res = _broker("GET", f"/auth/social/{platform}/status", query={"state": state})
        if res.get("status") in ("connected", "error", "not_found"):
            return res
        time.sleep(interval)
    return {"status": "timeout"}


def get_token(platform, **params):
    """GET /social/{platform}/token -> { accessToken, expiresAt, providerAccountId, ids }.
    Pass page=<id> for Meta to select which Facebook page to publish to.
    The backend refreshes the token automatically when it is near expiry."""
    query = {k: v for k, v in params.items() if v is not None}
    return _broker("GET", f"/social/{platform}/token", query=query or None)


def list_connections():
    """GET /social/connections -> list of connected platforms (no secrets)."""
    return _broker("GET", "/social/connections")


def disconnect(platform, account=None):
    """DELETE /social/{platform}?account=… -> { disconnected: true }.
    Removes the stored connection (revokes the saved tokens server-side).
    Pass account=<handle|id> to disconnect ONE account; omit it to disconnect
    ALL accounts of that platform."""
    query = {"account": account} if account else None
    return _broker("DELETE", f"/social/{platform}", query=query)
