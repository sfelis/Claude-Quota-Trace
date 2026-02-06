#!/usr/bin/env python3
"""Test if headless mode works for API calls."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

DATA_DIR = Path.home() / ".floating-ball"
BROWSER_PROFILE = DATA_DIR / "browser_profile"
BASE_URL = "https://claude.ai"


def test_headless():
    print("Testing HEADLESS mode...")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE),
            headless=True,  # HEADLESS
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("Loading main page...")
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        print(f"Current URL: {page.url}")

        # Check if we hit Cloudflare
        content = page.content()
        if "Just a moment" in content or "challenge" in content.lower():
            print("ERROR: Cloudflare challenge detected in headless mode!")
            context.close()
            return False

        print("Fetching /api/organizations...")
        try:
            result = page.evaluate("""
                async () => {
                    const response = await fetch('/api/organizations');
                    return { status: response.status, ok: response.ok };
                }
            """)
            print(f"Result: {result}")

            if result.get("ok"):
                print("SUCCESS: Headless mode works!")
                context.close()
                return True
            else:
                print(f"FAILED: Status {result.get('status')}")

        except Exception as e:
            print(f"Error: {e}")

        context.close()
        return False


def test_visible():
    print("\nTesting VISIBLE mode...")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE),
            headless=False,  # VISIBLE
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )

        page = context.pages[0] if context.pages else context.new_page()

        print("Loading main page...")
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        print(f"Current URL: {page.url}")

        print("Fetching /api/organizations...")
        try:
            result = page.evaluate("""
                async () => {
                    const response = await fetch('/api/organizations');
                    return { status: response.status, ok: response.ok };
                }
            """)
            print(f"Result: {result}")

        except Exception as e:
            print(f"Error: {e}")

        input("Press Enter to close...")
        context.close()


if __name__ == "__main__":
    success = test_headless()
    if not success:
        print("\nHeadless failed. Trying visible mode...")
        test_visible()
