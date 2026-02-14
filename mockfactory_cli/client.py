"""API client for MockFactory."""

from typing import Any, Dict, Optional

import requests
from pydantic import BaseModel

from .config import Config


class ExecutionResult(BaseModel):
    """Result of code execution."""

    success: bool
    output: str
    error: Optional[str] = None
    execution_time: Optional[float] = None
    language: str


class UsageInfo(BaseModel):
    """User usage information."""

    runs_used: int
    runs_limit: int
    tier: str
    is_authenticated: bool


class MockFactoryClient:
    """Client for interacting with MockFactory API."""

    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()

        # Set up headers
        token = config.get_token()
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

        if config.session_id:
            self.session.headers["X-Session-Id"] = config.session_id

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an API request."""
        url = f"{self.config.api_url}/api/v1{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.config.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                try:
                    error_detail = e.response.json().get("detail", str(e))
                except Exception:
                    error_detail = str(e)
                raise Exception(f"API Error: {error_detail}")
            raise Exception(f"HTTP Error: {e}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def execute_code(
        self,
        code: str,
        language: str,
        timeout: Optional[int] = None,
    ) -> ExecutionResult:
        """Execute code in the sandbox."""
        data = {
            "code": code,
            "language": language,
        }
        if timeout is not None:
            data["timeout"] = timeout

        result = self._request("POST", "/code/execute", data=data)
        return ExecutionResult(**result)

    def get_usage(self) -> UsageInfo:
        """Get current usage information."""
        result = self._request("GET", "/code/usage")
        return UsageInfo(**result)

    def signin(self, email: str, password: str) -> str:
        """Sign in and return access token."""
        data = {"email": email, "password": password}
        result = self._request("POST", "/auth/signin", data=data)
        return result["access_token"]

    def signup(self, email: str, password: str) -> str:
        """Sign up and return access token."""
        data = {"email": email, "password": password}
        result = self._request("POST", "/auth/signup", data=data)
        return result["access_token"]

    def get_profile(self) -> Dict[str, Any]:
        """Get user profile information."""
        return self._request("GET", "/auth/me")
