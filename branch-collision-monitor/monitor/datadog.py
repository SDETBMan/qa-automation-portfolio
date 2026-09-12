"""
datadog.py — Send collision metrics to DataDog.

Reuses the _gauge()/_post() pattern from flakiness-detector/flakiness/datadog.py.
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
            print("[INFO] DataDog collision metrics sent successfully.")
        else:
            print(f"[WARN] DataDog metrics returned HTTP {resp.status_code}.")
    except Exception as exc:
        print(f"[ERROR] DataDog metrics failed: {exc}")


def send_collision_metrics(
    overall_risk: str,
    overall_score: float,
    branches_analyzed: int,
    overlapping_file_count: int,
    semantic_conflicts: int = 0,
) -> None:
    """Send branch collision metrics to DataDog."""
    tags = ["framework:branch-collision-monitor"] + _COMMON_TAGS

    risk_numeric = {"LOW": 0, "MODERATE": 1, "HIGH": 2, "CRITICAL": 3}.get(overall_risk, 0)

    series = [
        _gauge("branch_collision.risk_level", risk_numeric, tags),
        _gauge("branch_collision.overall_score", overall_score, tags),
        _gauge("branch_collision.branches_analyzed", branches_analyzed, tags),
        _gauge("branch_collision.overlapping_files", overlapping_file_count, tags),
        _gauge("branch_collision.semantic_conflicts", semantic_conflicts, tags),
    ]

    _post(series)
