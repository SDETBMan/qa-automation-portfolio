"""
api_client.py — Thin HTTP client for API testing steps.

Wraps requests with a base URL, common headers, and a default timeout.
Step definitions can call this instead of raw requests, keeping API config
centralized and making base URL changes a one-line edit.

Replaces: ApiSteps.java's RestAssured configuration layer
"""

import requests
from requests import Response

from utils import config_reader


class ApiClient:
    """Reusable HTTP client pre-configured with the framework's API base URL."""

    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = base_url or config_reader.get(
            "api", "base_url", "https://jsonplaceholder.typicode.com"
        )
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def get(self, path: str, **kwargs) -> Response:
        """Send a GET request to base_url + path."""
        url = f"{self.base_url.rstrip('/')}{path}"
        return self.session.get(url, timeout=kwargs.pop("timeout", 10), **kwargs)

    def post(self, path: str, json: dict | None = None, **kwargs) -> Response:
        """Send a POST request to base_url + path."""
        url = f"{self.base_url.rstrip('/')}{path}"
        return self.session.post(url, json=json, timeout=kwargs.pop("timeout", 10), **kwargs)
