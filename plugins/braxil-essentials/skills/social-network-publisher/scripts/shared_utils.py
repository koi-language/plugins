"""DEPRECATED helpers from the old Playwright/cookie flow.

Tokens are no longer read from a local .env or session files — the posters call
broker_client.get_token(<platform>) which fetches a fresh, short-lived token
from the BRAXIL backend. Kept only so any stray legacy import doesn't crash."""

import os


def get_session_path(platform: str) -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sessions_dir = os.path.abspath(os.path.join(script_dir, "..", "sessions"))
    return os.path.join(sessions_dir, f"{platform}.json")


def check_session_exists(platform: str) -> bool:
    return os.path.exists(get_session_path(platform))
