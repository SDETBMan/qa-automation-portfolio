"""
datadog_reporter.py — Send failure triage metrics to DataDog.

Emits triage summary metrics: total failures, cluster count, and
per-root-cause failure counts.  Follows the same graceful-skip
pattern as every other framework in the monorepo.

Metrics:
  triage.total_failures              Total test failures triaged
  triage.cluster_count               Number of root cause clusters identified
  triage.root_cause                  Failure count per root cause category
  triage.cross_framework_incidents   Number of clusters affecting 2+ frameworks
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


def send_triage_metrics(report: dict) -> None:
    """Send triage summary metrics to DataDog.

    Args:
        report: The triage report dict with 'summary' and 'clusters' keys.
    """
    summary = report.get("summary", {})
    clusters = report.get("clusters", [])

    tags = ["framework:failure-triage"] + _COMMON_TAGS

    series = [
        _gauge("triage.total_failures", summary.get("total_failures", 0), tags),
        _gauge("triage.cluster_count",  summary.get("clusters", 0),       tags),
    ]

    cross_fw = summary.get("cross_framework_incidents")
    if cross_fw is not None:
        series.append(_gauge("triage.cross_framework_incidents", cross_fw, tags))

    # Per-root-cause metrics
    for cluster in clusters:
        root_cause = cluster.get("root_cause", "unknown")
        count = cluster.get("count", 0)
        cause_tags = [f"root_cause:{root_cause}"] + tags
        series.append(_gauge("triage.root_cause", count, cause_tags))

    _post(series)
