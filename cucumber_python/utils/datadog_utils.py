"""
datadog_utils.py — Send suite-level metrics to DataDog via the v2 metrics API.

Four GAUGE metrics posted after each suite run:
  test.suite.passed, test.suite.failed, test.suite.skipped, test.suite.duration_ms

Fail-safe: if DD_API_KEY is absent (local dev), logs a warning and returns.
This mirrors DataDogUtils.java exactly.
"""

import os
import time
import requests


def _dd_api_url() -> str:
    site = os.getenv("DD_SITE", "datadoghq.com")
    return f"https://api.{site}/api/v2/series"


def send_test_metrics(
    passed: int,
    failed: int,
    skipped: int,
    duration_ms: int,
    framework: str,
) -> None:
    """Post suite-level GAUGE metrics to DataDog.

    Args:
        passed:      Number of passing scenarios.
        failed:      Number of failing scenarios.
        skipped:     Number of skipped scenarios.
        duration_ms: Total suite wall-clock duration in milliseconds.
        framework:   Short label for the 'framework' tag (e.g. 'cucumber-python').
    """
    api_key = os.getenv("DD_API_KEY", "")
    if not api_key:
        print("[WARN] DD_API_KEY not set. Skipping DataDog metrics.")
        return

    timestamp = int(time.time())
    tags = [
        f"framework:{framework}",
        "service:qa-automation-portfolio",
        "env:ci",
    ]

    def _series(metric: str, value: int | float) -> dict:
        return {
            "metric": metric,
            "type":   3,  # 3 = GAUGE
            "points": [{"timestamp": timestamp, "value": value}],
            "tags":   tags,
        }

    payload = {
        "series": [
            _series("test.suite.passed",      passed),
            _series("test.suite.failed",      failed),
            _series("test.suite.skipped",     skipped),
            _series("test.suite.duration_ms", duration_ms),
        ]
    }

    try:
        response = requests.post(
            _dd_api_url(),
            json=payload,
            headers={"DD-API-KEY": api_key, "Content-Type": "application/json"},
            timeout=10,
        )
        if response.status_code == 202:
            print("[INFO] DataDog metrics sent successfully.")
        else:
            print(f"[WARN] DataDog metrics returned unexpected status: {response.status_code}")
    except Exception as exc:
        # Never crash the test run over a metrics delivery failure
        print(f"[ERROR] DataDog metrics failed: {exc}")
