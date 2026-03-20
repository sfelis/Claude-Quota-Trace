"""Authentication service using Playwright for Claude OAuth login."""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from playwright.sync_api import sync_playwright, Browser, BrowserContext


class AuthService:
    """Handle Claude OAuth login via Playwright browser."""

    CLAUDE_URL = "https://claude.ai"
    LOGIN_URL = "https://claude.ai/login"

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize auth service.

        Args:
            data_dir: Directory to store cookies. Defaults to ~/.floating-ball/
        """
        if data_dir is None:
            data_dir = Path.home() / ".floating-ball"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.cookies_file = self.data_dir / "cookies.json"
        self.config_file = self.data_dir / "config.json"

    def get_cookies(self) -> Optional[List[Dict]]:
        """Load cookies from file."""
        if not self.cookies_file.exists():
            return None

        try:
            with open(self.cookies_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading cookies: {e}")
            return None

    def save_cookies(self, cookies: List[Dict]) -> None:
        """Save cookies to file."""
        with open(self.cookies_file, "w") as f:
            json.dump(cookies, f, indent=2)

    def clear_cookies(self) -> None:
        """Delete stored cookies (logout)."""
        if self.cookies_file.exists():
            self.cookies_file.unlink()

    def get_config(self) -> Dict:
        """Load config from file."""
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def save_config(self, config: Dict) -> None:
        """Save config to file."""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def get_selected_org_id(self) -> Optional[str]:
        """Get the currently selected organization ID."""
        config = self.get_config()
        return config.get("selected_org_id")

    def set_selected_org_id(self, org_id: str) -> None:
        """Set the selected organization ID."""
        config = self.get_config()
        config["selected_org_id"] = org_id
        self.save_config(config)

    def has_cookies(self) -> bool:
        """Check if cookies exist."""
        return self.cookies_file.exists()

    def get_cookies_as_dict(self) -> Dict[str, str]:
        """Get cookies in simple dict format for requests."""
        cookies = self.get_cookies()
        if not cookies:
            return {}

        return {cookie["name"]: cookie["value"] for cookie in cookies}

    def login(self, timeout_ms: int = 300000) -> bool:
        """
        Open browser for user to login to Claude.

        Args:
            timeout_ms: Timeout in milliseconds (default 5 minutes)

        Returns:
            True if login successful, False otherwise
        """
        print("Opening browser for Claude login...")

        # Use persistent browser profile to look more human
        browser_data_dir = self.data_dir / "browser_profile"

        try:
            with sync_playwright() as p:
                # Launch with persistent context (keeps cookies, history, fingerprint)
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(browser_data_dir),
                    headless=False,
                    # Make it look more like a real browser
                    args=[
                        "--disable-blink-features=AutomationControlled",
                    ],
                    ignore_default_args=["--enable-automation"],
                )
                page = context.pages[0] if context.pages else context.new_page()

                # Navigate to Claude
                page.goto(self.CLAUDE_URL)

                # Wait for user to complete login
                # Detect successful login by URL change
                try:
                    page.wait_for_url(
                        lambda url: any(x in url for x in ["/new", "/chat", "/recents"]) or url == "https://claude.ai/",
                        timeout=timeout_ms
                    )

                    # Extra wait for cookies to settle
                    page.wait_for_timeout(2000)

                    # Capture cookies
                    cookies = context.cookies()
                    self.save_cookies(cookies)

                    context.close()
                    return True

                except Exception as e:
                    print(f"Login failed or timed out: {e}")
                    context.close()
                    return False

        except Exception as e:
            print(f"Browser error: {e}")
            return False

    def logout(self) -> None:
        """Clear all stored authentication data."""
        self.clear_cookies()
        # Optionally clear selected org
        config = self.get_config()
        config.pop("selected_org_id", None)
        self.save_config(config)
