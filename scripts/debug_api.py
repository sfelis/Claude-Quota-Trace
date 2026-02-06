#!/usr/bin/env python3
"""Debug script to check cookies and API responses."""
import json
import requests
from pathlib import Path

DATA_DIR = Path.home() / ".floating-ball"
COOKIES_FILE = DATA_DIR / "cookies.json"
BASE_URL = "https://claude.ai"


def main():
    print("="*60)
    print("DEBUG: Checking cookies and API")
    print("="*60)

    # Check if cookies exist
    if not COOKIES_FILE.exists():
        print(f"\nERROR: No cookies file at {COOKIES_FILE}")
        return

    # Load cookies
    with open(COOKIES_FILE) as f:
        cookies_list = json.load(f)

    print(f"\nLoaded {len(cookies_list)} cookies:")
    for c in cookies_list:
        # Show cookie names and domains (not values for security)
        print(f"  - {c['name']:30} domain: {c.get('domain', 'N/A')}")

    # Convert to dict for requests
    cookies = {c["name"]: c["value"] for c in cookies_list}

    # Create session
    session = requests.Session()

    # Test different header combinations
    print("\n" + "="*60)
    print("Testing API with different headers...")
    print("="*60)

    # Headers variation 1: Minimal
    headers_v1 = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }

    # Headers variation 2: With Origin/Referer
    headers_v2 = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Origin": "https://claude.ai",
        "Referer": "https://claude.ai/",
    }

    # Headers variation 3: Full browser-like
    headers_v3 = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://claude.ai",
        "Referer": "https://claude.ai/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    endpoints = [
        "/api/organizations",
        "/api/auth/session",
        "/api/account",
    ]

    for i, headers in enumerate([headers_v1, headers_v2, headers_v3], 1):
        print(f"\n--- Headers variation {i} ---")

        for endpoint in endpoints:
            try:
                resp = session.get(
                    f"{BASE_URL}{endpoint}",
                    cookies=cookies,
                    headers=headers,
                    timeout=10
                )
                print(f"\n{endpoint}")
                print(f"  Status: {resp.status_code}")

                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        preview = json.dumps(data, indent=2)[:500]
                        print(f"  Response: {preview}...")
                    except:
                        print(f"  Response: {resp.text[:200]}")
                else:
                    print(f"  Response: {resp.text[:200]}")

                # If we got a 200, we found working headers
                if resp.status_code == 200 and endpoint == "/api/organizations":
                    print("\n" + "="*60)
                    print("SUCCESS! Found working configuration")
                    print(f"Headers variation: {i}")
                    print("="*60)
                    return headers, data

            except Exception as e:
                print(f"\n{endpoint}")
                print(f"  Error: {e}")

    print("\n" + "="*60)
    print("Could not find working configuration")
    print("="*60)


if __name__ == "__main__":
    main()
