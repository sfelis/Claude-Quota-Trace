#!/usr/bin/env python3
"""
Test script to explore Claude web API using captured cookies.

Usage:
    1. First run: python scripts/test_login.py (to capture cookies)
    2. Then run: python scripts/test_api.py

This script will:
    - Load cookies from cookies.json
    - Test various API endpoints
    - Print response data for analysis
"""
import json
import requests
from pathlib import Path


COOKIES_FILE = Path(__file__).parent / "cookies.json"
BASE_URL = "https://claude.ai"


def load_cookies() -> dict:
    """Load cookies from file and convert to requests format."""
    if not COOKIES_FILE.exists():
        print(f"Error: {COOKIES_FILE} not found.")
        print("Run 'python scripts/test_login.py' first to capture cookies.")
        return None

    with open(COOKIES_FILE) as f:
        cookies_list = json.load(f)

    # Convert to simple dict for requests
    cookies = {}
    for cookie in cookies_list:
        cookies[cookie["name"]] = cookie["value"]

    return cookies


def test_api(session: requests.Session):
    """Test various Claude API endpoints."""

    print("\n" + "="*60)
    print("Testing Claude Web API")
    print("="*60)

    # Common headers that mimic browser
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/",
    }

    # Test 1: Get organizations
    print("\n[1] Testing: GET /api/organizations")
    print("-" * 40)
    try:
        resp = session.get(
            f"{BASE_URL}/api/organizations",
            headers=headers,
            timeout=10
        )
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Response: {json.dumps(data, indent=2)[:2000]}")

            # Extract org IDs for further testing
            if isinstance(data, list) and len(data) > 0:
                org_id = data[0].get("uuid") or data[0].get("id")
                print(f"\nFound organization ID: {org_id}")
                return data, org_id
            elif isinstance(data, dict):
                print(f"Response is dict with keys: {list(data.keys())}")
                return data, None
        else:
            print(f"Response: {resp.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

    return None, None


def test_usage_endpoints(session: requests.Session, org_id: str):
    """Test usage-related endpoints."""

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/",
    }

    # List of potential usage endpoints to try
    endpoints = [
        f"/api/organizations/{org_id}/usage",
        f"/api/organizations/{org_id}/stats",
        f"/api/organizations/{org_id}/billing",
        f"/api/organizations/{org_id}/subscription",
        f"/api/organizations/{org_id}/settings",
        f"/api/organizations/{org_id}",
        "/api/account",
        "/api/settings",
        "/api/billing",
    ]

    for endpoint in endpoints:
        print(f"\n[Testing] GET {endpoint}")
        print("-" * 40)
        try:
            resp = session.get(
                f"{BASE_URL}{endpoint}",
                headers=headers,
                timeout=10
            )
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    # Pretty print, but limit length
                    output = json.dumps(data, indent=2)
                    if len(output) > 2000:
                        print(f"Response (truncated): {output[:2000]}...")
                    else:
                        print(f"Response: {output}")
                except:
                    print(f"Response (text): {resp.text[:500]}")
            elif resp.status_code == 404:
                print("Not found (404)")
            elif resp.status_code == 403:
                print("Forbidden (403) - may need different permissions")
            else:
                print(f"Response: {resp.text[:300]}")
        except Exception as e:
            print(f"Error: {e}")


def test_bootstrap_endpoint(session: requests.Session):
    """Test the bootstrap endpoint which often contains user/org info."""

    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }

    print("\n[Testing] GET /api/bootstrap")
    print("-" * 40)
    try:
        resp = session.get(
            f"{BASE_URL}/api/bootstrap",
            headers=headers,
            timeout=10
        )
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            output = json.dumps(data, indent=2)
            if len(output) > 3000:
                print(f"Response (truncated): {output[:3000]}...")
            else:
                print(f"Response: {output}")
            return data
    except Exception as e:
        print(f"Error: {e}")

    return None


def main():
    print("Loading cookies...")
    cookies = load_cookies()
    if not cookies:
        return

    print(f"Loaded {len(cookies)} cookies")

    # Create session with cookies
    session = requests.Session()
    session.cookies.update(cookies)

    # Test bootstrap first (often has org info)
    bootstrap = test_bootstrap_endpoint(session)

    # Test organizations endpoint
    orgs_data, org_id = test_api(session)

    # If we found an org ID, test usage endpoints
    if org_id:
        test_usage_endpoints(session, org_id)
    elif bootstrap and "account" in bootstrap:
        # Try to get org from bootstrap
        account = bootstrap.get("account", {})
        memberships = account.get("memberships", [])
        if memberships:
            org = memberships[0].get("organization", {})
            org_id = org.get("uuid")
            if org_id:
                print(f"\nFound org ID from bootstrap: {org_id}")
                test_usage_endpoints(session, org_id)

    print("\n" + "="*60)
    print("API exploration complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the responses above to identify the correct endpoint")
    print("2. Note the response format for usage data")
    print("3. Update the main app to use the discovered endpoint")


if __name__ == "__main__":
    main()
