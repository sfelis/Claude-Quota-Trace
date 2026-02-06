"""Claude web API service using curl_cffi for Cloudflare bypass."""
import json
from datetime import datetime
from typing import Optional, Tuple, Dict, List
from curl_cffi import requests as curl_requests

from auth_service import AuthService


class APIError(Exception):
    """Custom exception for API errors."""

    def __init__(self, error_type: str, message: str):
        self.error_type = error_type
        self.message = message
        super().__init__(message)


class APIService:
    """Service for interacting with Claude web API."""

    BASE_URL = "https://claude.ai"

    def __init__(self, auth_service: AuthService):
        """Initialize API service."""
        self.auth_service = auth_service
        self._organizations_cache = None
        # Use curl_cffi with Chrome impersonation to bypass Cloudflare
        self._session = curl_requests.Session(impersonate="chrome")

    def _get_cookies(self) -> Dict[str, str]:
        """Get cookies as dict for requests."""
        return self.auth_service.get_cookies_as_dict()

    def _fetch(self, endpoint: str) -> dict:
        """Make an API request with Chrome TLS impersonation."""
        cookies = self._get_cookies()
        if not cookies:
            raise APIError("not_authenticated", "Not logged in. Please login first.")

        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        try:
            response = self._session.get(
                f"{self.BASE_URL}{endpoint}",
                headers=headers,
                cookies=cookies,
                timeout=15
            )

            if response.status_code == 401:
                raise APIError("session_expired", "Session expired. Please login again.")
            elif response.status_code == 403:
                # Check if it's Cloudflare or actual forbidden
                if "Just a moment" in response.text:
                    raise APIError("cloudflare_blocked", "Blocked by Cloudflare. Please re-login.")
                raise APIError("forbidden", "Access denied. Please login again.")
            elif response.status_code != 200:
                raise APIError("fetch_error", f"API error: {response.status_code}")

            return response.json()

        except APIError:
            raise
        except Exception as e:
            raise APIError("network_error", f"Network error: {str(e)}")

    def test_connection(self) -> Tuple[bool, str]:
        """Test if current session is valid."""
        if not self.auth_service.has_cookies():
            return False, "Not logged in"

        try:
            data = self._fetch("/api/organizations")
            if data:
                return True, "Connected successfully"
            return False, "No data returned"

        except APIError as e:
            return False, e.message
        except Exception as e:
            return False, f"Error: {str(e)}"

    def fetch_organizations(self) -> List[Dict]:
        """Fetch list of organizations the user belongs to."""
        data = self._fetch("/api/organizations")
        self._organizations_cache = data
        return data if isinstance(data, list) else []

    def get_organizations(self) -> List[Dict]:
        """Get organizations (from cache or fetch)."""
        if self._organizations_cache is not None:
            return self._organizations_cache
        return self.fetch_organizations()

    def fetch_usage(self, org_id: Optional[str] = None) -> Dict:
        """Fetch usage data for an organization."""
        if org_id is None:
            org_id = self.auth_service.get_selected_org_id()

        if org_id is None:
            orgs = self.get_organizations()
            if orgs and len(orgs) > 0:
                org_id = orgs[0].get("uuid") or orgs[0].get("id")
                if org_id:
                    self.auth_service.set_selected_org_id(org_id)

        if not org_id:
            raise APIError("no_org", "No organization found.")

        usage_data = self._fetch(f"/api/organizations/{org_id}/usage")
        return self._parse_usage_response(usage_data)

    def _parse_usage_response(self, data: Dict) -> Dict:
        """Parse the Claude usage API response."""
        result = {
            "last_updated": datetime.now(),
            "raw_data": data,
        }

        # Parse five_hour usage (primary)
        five_hour = data.get("five_hour") or {}
        result["usage_percentage"] = five_hour.get("utilization", 0) / 100.0
        result["resets_at"] = five_hour.get("resets_at", "")

        # Parse seven_day usage
        seven_day = data.get("seven_day") or {}
        result["usage_percentage_7day"] = seven_day.get("utilization", 0) / 100.0
        result["resets_at_7day"] = seven_day.get("resets_at", "")

        # For display
        result["utilization_5h"] = five_hour.get("utilization", 0)
        result["utilization_7d"] = seven_day.get("utilization", 0)

        # Human readable reset times
        result["resets_in"] = self._parse_reset_time(result["resets_at"])
        result["resets_in_7day"] = self._parse_reset_time(result["resets_at_7day"])

        # Calculate time percentage (how much of the period has elapsed)
        result["time_percentage_5h"] = self._calculate_time_percentage(result["resets_at"], 5)
        result["time_percentage_7day"] = self._calculate_time_percentage(result["resets_at_7day"], 168)  # 7 days = 168 hours

        return result

    def _parse_reset_time(self, iso_time: str) -> str:
        """Convert ISO time to 'H:MM' format."""
        if not iso_time:
            return ""

        try:
            from datetime import timezone
            reset_time = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            delta = reset_time - now

            total_minutes = int(delta.total_seconds() / 60)
            if total_minutes < 0:
                return "now"
            else:
                hours = total_minutes // 60
                mins = total_minutes % 60
                return f"{hours}:{mins:02d}"
        except:
            return ""

    def _calculate_time_percentage(self, iso_time: str, period_hours: int) -> float:
        """Calculate percentage of time elapsed in a reset period.

        Args:
            iso_time: ISO timestamp when reset occurs
            period_hours: Total period duration in hours (5 for 5h, 168 for 7d)

        Returns:
            Percentage of time elapsed (0.0 to 1.0)
        """
        if not iso_time:
            return 0.0

        try:
            from datetime import timezone
            reset_time = datetime.fromisoformat(iso_time.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            time_remaining = reset_time - now

            # Calculate elapsed time
            total_seconds = period_hours * 3600
            remaining_seconds = max(0, time_remaining.total_seconds())
            elapsed_seconds = total_seconds - remaining_seconds

            # Return as percentage (0.0 to 1.0)
            return max(0.0, min(1.0, elapsed_seconds / total_seconds))
        except:
            return 0.0
