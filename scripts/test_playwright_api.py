#!/usr/bin/env python3
"""Test API calls using Playwright."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

DATA_DIR = Path.home() / ".floating-ball"
BROWSER_PROFILE = DATA_DIR / "browser_profile"
BASE_URL = "https://claude.ai"


def test_api():
    print("Testing API with Playwright...")
    print(f"Using browser profile: {BROWSER_PROFILE}")

    with sync_playwright() as p:
        # Try non-headless first to debug
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE),
            headless=False,  # Visible for debugging
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )

        page = context.pages[0] if context.pages else context.new_page()

        # First, go to main page to establish session
        print("\nLoading main page first...")
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)  # Wait for any JS to execute

        print(f"Current URL: {page.url}")

        # Now try the API using fetch() from within the page context
        print("\n" + "="*60)
        print("Fetching /api/organizations via page.evaluate()")
        print("="*60)

        try:
            result = page.evaluate("""
                async () => {
                    const response = await fetch('/api/organizations');
                    const data = await response.json();
                    return { status: response.status, data: data };
                }
            """)

            print(f"Status: {result['status']}")
            print(f"Response:\n{json.dumps(result['data'], indent=2)[:2000]}")

            if isinstance(result['data'], list) and len(result['data']) > 0:
                org = result['data'][0]
                org_id = org.get("uuid") or org.get("id")
                org_name = org.get("name", "Unknown")
                print(f"\n\nFound org: {org_name} (ID: {org_id})")

                # Try usage endpoint
                print(f"\n{'='*60}")
                print(f"Fetching /api/organizations/{org_id}/usage")
                print("="*60)

                usage_result = page.evaluate(f"""
                    async () => {{
                        const response = await fetch('/api/organizations/{org_id}/usage');
                        if (!response.ok) {{
                            return {{ status: response.status, error: await response.text() }};
                        }}
                        const data = await response.json();
                        return {{ status: response.status, data: data }};
                    }}
                """)

                print(f"Status: {usage_result['status']}")
                if 'data' in usage_result:
                    print(f"Response:\n{json.dumps(usage_result['data'], indent=2)[:2000]}")
                else:
                    print(f"Error: {usage_result.get('error', 'Unknown')[:500]}")

        except Exception as e:
            print(f"Error: {e}")

        input("\nPress Enter to close browser...")
        context.close()


if __name__ == "__main__":
    test_api()
