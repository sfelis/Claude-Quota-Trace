#!/usr/bin/env python3
"""
Test script for Claude OAuth login via Playwright.
This script opens a browser for login and captures cookies.

Usage:
    python scripts/test_login.py

After login, cookies will be saved to scripts/cookies.json
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


CLAUDE_URL = "https://claude.ai"
COOKIES_FILE = Path(__file__).parent / "cookies.json"


def login_and_capture_cookies():
    """Open browser for login and capture cookies after successful auth."""

    print("Opening browser for Claude login...")
    print("Please log in with your Claude account.")
    print("The browser will close automatically after successful login.\n")

    # Use persistent profile to avoid CAPTCHA
    browser_data_dir = Path(__file__).parent / "browser_profile"

    with sync_playwright() as p:
        # Launch with persistent context (looks more human)
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(browser_data_dir),
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        page = context.pages[0] if context.pages else context.new_page()

        # Navigate to Claude
        page.goto(CLAUDE_URL)

        # Wait for user to complete login
        # We detect successful login by checking for specific URL patterns or elements
        print("Waiting for login to complete...")
        print("(Looking for redirect to claude.ai/new or presence of chat interface)\n")

        try:
            # Wait for either:
            # 1. URL contains /new (new chat page)
            # 2. URL contains /chat (existing chat)
            # 3. Presence of the main app interface
            page.wait_for_url(
                lambda url: "/new" in url or "/chat" in url or url == "https://claude.ai/",
                timeout=300000  # 5 minutes timeout for login
            )
            print("Login detected!")

        except Exception as e:
            print(f"Login timeout or error: {e}")
            context.close()
            return None

        # Small delay to ensure all cookies are set
        page.wait_for_timeout(2000)

        # Capture cookies
        cookies = context.cookies()

        # Save cookies to file
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f, indent=2)

        print(f"\nCookies saved to: {COOKIES_FILE}")
        print(f"Total cookies captured: {len(cookies)}")

        # Print cookie names (not values, for security)
        print("\nCaptured cookies:")
        for cookie in cookies:
            print(f"  - {cookie['name']} (domain: {cookie['domain']})")

        context.close()
        return cookies


def main():
    cookies = login_and_capture_cookies()

    if cookies:
        print("\n" + "="*50)
        print("SUCCESS! Cookies captured.")
        print("="*50)
        print(f"\nYou can now run: python scripts/test_api.py")
        print("to test API access with these cookies.")
    else:
        print("\n" + "="*50)
        print("FAILED to capture cookies.")
        print("="*50)


if __name__ == "__main__":
    main()
