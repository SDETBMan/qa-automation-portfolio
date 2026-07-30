"""datadog.py — Send site drift metrics to DataDog.

Reuses the _gauge()/_post() pattern from flakiness-detector/flakiness/datadog.py.
"""

from __future__ import annotations

import os
import time

import requests

_COMMON_TAGS = ["service:qa-automation-portfolio", "env:ci", "target:saucedemo"]


def _api_key() -> str | None:
    key = os.getenv("DD_API_KEY", "")
    return key if key else None


def _gauge(metric: str, value: float, tags: list[str]) -> dict:
    return {
        "metric": metric,
        "type": 3,
        "points": [{"timestamp": int(time.time()), "value": value}],
        "tags": tags,
    }


def _post(series: list[dict]) -> None:
    api_key = _api_key()
    if not api_key:
        print("[WARN] DD_API_KEY not set. Skipping DataDog metrics.")
        return

    site = os.getenv("DD_SITE", "datadoghq.com")
    url = f"https://api.{site}/api/v2/series"

    try:
        resp = requests.post(
            url,
            headers={"DD-API-KEY": api_key, "Content-Type": "application/json"},
            json={"series": series},
            timeout=10,
        )
        if resp.status_code in (200, 202):
            print("[INFO] DataDog site-monitor metrics sent successfully.")
        else:
            print(f"[WARN] DataDog metrics returned HTTP {resp.status_code}.")
    except Exception as exc:
        print(f"[ERROR] DataDog metrics failed: {exc}")


def send_drift_metrics(
    drift_detected: bool,
    selectors_removed: int,
    selectors_added: int,
) -> None:
    """Send site drift metrics to DataDog."""
    tags = ["framework:site-monitor"] + _COMMON_TAGS
    series = [
        _gauge("site_monitor.drift_detected", 1 if drift_detected else 0, tags),
        _gauge("site_monitor.selectors_removed", selectors_removed, tags),
        _gauge("site_monitor.selectors_added", selectors_added, tags),
    ]
    _post(series)
