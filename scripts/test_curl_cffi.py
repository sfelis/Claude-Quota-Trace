#!/usr/bin/env python3
"""Test curl_cffi with Chrome TLS impersonation."""
import json
from pathlib import Path
from curl_cffi import requests

DATA_DIR = Path.home() / ".floating-ball"
COOKIES_FILE = DATA_DIR / "cookies.json"
BASE_URL = "https://claude.ai"


def load_cookies():
    """Load cookies from file."""
    if not COOKIES_FILE.exists():
        print(f"No cookies file at {COOKIES_FILE}")
        return None

    with open(COOKIES_FILE) as f:
        cookies_list = json.load(f)

    # Convert to dict
    return {c["name"]: c["value"] for c in cookies_list}


def test_api():
    print("Testing with curl_cffi (Chrome impersonation)...")

    cookies = load_cookies()
    if not cookies:
        return

    print(f"Loaded {len(cookies)} cookies")

    # Create session with Chrome impersonation
    session = requests.Session(impersonate="chrome")

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    print("\nTesting /api/organizations...")
    try:
        resp = session.get(
            f"{BASE_URL}/api/organizations",
            headers=headers,
            cookies=cookies,
            timeout=10
        )

        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            data = resp.json()
            print(f"SUCCESS! Response:\n{json.dumps(data, indent=2)[:1000]}")

            # Get org ID and test usage
            if isinstance(data, list) and len(data) > 0:
                org_id = data[0].get("uuid") or data[0].get("id")
                print(f"\n\nTesting /api/organizations/{org_id}/usage...")

                usage_resp = session.get(
                    f"{BASE_URL}/api/organizations/{org_id}/usage",
                    headers=headers,
                    cookies=cookies,
                    timeout=10
                )

                print(f"Status: {usage_resp.status_code}")
                if usage_resp.status_code == 200:
                    print(f"Response:\n{json.dumps(usage_resp.json(), indent=2)}")
                else:
                    print(f"Response: {usage_resp.text[:500]}")
        else:
            print(f"Response: {resp.text[:500]}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_api()
