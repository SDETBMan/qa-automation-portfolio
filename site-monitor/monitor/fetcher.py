"""fetcher.py — HTTP fetch of SauceDemo HTML + JS bundle."""

from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

_TIMEOUT = 30
_USER_AGENT = "SiteDriftDetector/1.0 (qa-automation-portfolio)"


def fetch_page(url: str) -> str:
    """GET the HTML page, return body text."""
    resp = requests.get(url, timeout=_TIMEOUT, headers={"User-Agent": _USER_AGENT})
    resp.raise_for_status()
    return resp.text


def fetch_js_bundle(html: str, base_url: str) -> tuple[str, str]:
    """Parse <script> tags from HTML, fetch the Vite JS bundle.

    Returns (js_content, bundle_path) tuple.
    """
    soup = BeautifulSoup(html, "html.parser")
    bundle_path = None

    for script in soup.find_all("script", src=True):
        src = script["src"]
        if re.match(r"/assets/index-.*\.js", src):
            bundle_path = src
            break

    if not bundle_path:
        return "", ""

    bundle_url = base_url.rstrip("/") + bundle_path
    resp = requests.get(
        bundle_url, timeout=_TIMEOUT, headers={"User-Agent": _USER_AGENT}
    )
    resp.raise_for_status()
    return resp.text, bundle_path
