"""
datadog.py — Send flakiness metrics to DataDog.

Reuses the _gauge()/_post() pattern from fastapi-service/utils/datadog_reporter.py.
"""

from __future__ import annotations

import os
import time

import requests

_COMMON_TAGS = ["service:qa-automation-portfolio", "env:ci"]


def _api_key() -> str | None:
    key = os.getenv("DD_API_KEY", "")
    return key if key else None


def _gauge(metric: str, value: float, tags: list[str]) -> dict:
    return {
        "metric": metric,
        "type":   3,
        "points": [{"timestamp": int(time.time()), "value": value}],
        "tags":   tags,
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
            print("[INFO] DataDog flakiness metrics sent successfully.")
        else:
            print(f"[WARN] DataDog metrics returned HTTP {resp.status_code}.")
    except Exception as exc:
        print(f"[ERROR] DataDog metrics failed: {exc}")


def send_flakiness_metrics(
    total_flaky: int,
    quarantined_count: int,
    scores: dict[str, float],
) -> None:
    """Send flakiness metrics to DataDog."""
    tags = ["framework:flakiness-detector"] + _COMMON_TAGS
    series = [
        _gauge("flakiness.total_flaky", total_flaky, tags),
        _gauge("flakiness.quarantined_count", quarantined_count, tags),
    ]

    # Send individual test scores (top 20 to avoid metric explosion)
    for test_key, score in list(scores.items())[:20]:
        test_tags = tags + [f"test:{test_key}"]
        series.append(_gauge("flakiness.score", score, test_tags))

    _post(series)
