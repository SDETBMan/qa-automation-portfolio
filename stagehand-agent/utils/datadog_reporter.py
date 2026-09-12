"""
datadog_reporter.py — Sends stagehand-agent comparison metrics to DataDog.

Follows the job-agent/utils/datadog_reporter.py pattern exactly.

Graceful-skip pattern:
  DD_API_KEY absent → log warning → return without raising → CI stays green.

DataDog v2 metrics API:
  POST https://api.datadoghq.com/api/v2/series
  Metric type 3 = GAUGE.
"""

from __future__ import annotations

import os
import time

import requests

_COMMON_TAGS = ["service:qa-automation-portfolio", "env:ci", "framework:stagehand-agent"]


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
    url  = f"https://api.{site}/api/v2/series"

    try:
        resp = requests.post(
            url,
            headers={"DD-API-KEY": api_key, "Content-Type": "application/json"},
            json={"series": series},
            timeout=10,
        )
        if resp.status_code in (200, 202):
            print("[INFO] DataDog metrics sent successfully.")
        else:
            print(f"[WARN] DataDog metrics returned HTTP {resp.status_code}.")
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] DataDog metrics failed: {exc}")


def send_comparison_metrics(
    traditional_duration_ms: float,
    ai_driven_duration_ms: float,
    ai_tokens_used: int,
    speed_ratio: float,
    scenarios_passed: int,
    scenarios_total: int,
) -> None:
    """Send per-run stagehand comparison metrics to DataDog."""
    _post([
        _gauge("stagehand.traditional.duration_ms", traditional_duration_ms, _COMMON_TAGS),
        _gauge("stagehand.ai_driven.duration_ms",   ai_driven_duration_ms,   _COMMON_TAGS),
        _gauge("stagehand.ai_driven.tokens_used",   ai_tokens_used,          _COMMON_TAGS),
        _gauge("stagehand.speed_ratio",             speed_ratio,             _COMMON_TAGS),
        _gauge("stagehand.scenarios_passed",        scenarios_passed,        _COMMON_TAGS),
        _gauge("stagehand.scenarios_total",         scenarios_total,         _COMMON_TAGS),
    ])
