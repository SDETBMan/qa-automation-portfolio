"""
datadog_reporter.py — Send quality KPI metrics to DataDog.

Emits portfolio-wide and per-framework quality KPIs as GAUGE metrics
to the DataDog v2 HTTP API.  Follows the same graceful-skip pattern
used by every other framework in the monorepo: DD_API_KEY absent →
log warning → return without raising → CI stays green.

Metrics emitted:
  kpi.pass_rate           Overall pass rate (0–1)
  kpi.failure_density     Failures / total tests
  kpi.avg_duration_s      Mean test execution time
  kpi.p95_duration_s      95th percentile duration
  kpi.total_tests         Total test count
  kpi.suite_stability     Pass rate over last N runs
  kpi.flakiness_rate      Flaky test percentage
  kpi.mttd_seconds        Mean time to detect (commit → failure)

Each metric tagged with framework:<name> for per-framework breakdown
plus framework:aggregate for the roll-up.
"""

from __future__ import annotations

import os
import time

import requests

from kpi_calculator import AggregateKPI, FrameworkKPI

_COMMON_TAGS = ["service:qa-automation-portfolio", "env:ci"]


# ── Internal helpers ──────────────────────────────────────────────────────────

def _api_key() -> str | None:
    """Return DD_API_KEY from the environment, or None if not set."""
    key = os.getenv("DD_API_KEY", "")
    return key if key else None


def _gauge(metric: str, value: float, tags: list[str]) -> dict:
    """Build one DataDog v2 series entry for a GAUGE metric."""
    return {
        "metric": metric,
        "type":   3,          # 3 = GAUGE in DataDog's metric type enum
        "points": [{"timestamp": int(time.time()), "value": value}],
        "tags":   tags,
    }


def _post(series: list[dict]) -> None:
    """POST a list of series dicts to the DataDog v2 metrics endpoint.

    Silently skips if DD_API_KEY is absent.  Catches all exceptions so a
    DataDog outage or misconfiguration never fails the pipeline.
    """
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


# ── Public API ────────────────────────────────────────────────────────────────

def send_framework_kpis(kpi: FrameworkKPI) -> None:
    """Send per-framework KPI metrics to DataDog.

    Args:
        kpi: A FrameworkKPI object for a single framework.
    """
    tags = [f"framework:{kpi.framework}"] + _COMMON_TAGS
    _post([
        _gauge("kpi.pass_rate",       kpi.pass_rate,       tags),
        _gauge("kpi.failure_density", kpi.failure_density,  tags),
        _gauge("kpi.avg_duration_s",  kpi.avg_duration_s,   tags),
        _gauge("kpi.p95_duration_s",  kpi.p95_duration_s,   tags),
        _gauge("kpi.total_tests",     kpi.total_tests,      tags),
    ])


def send_aggregate_kpis(agg: AggregateKPI) -> None:
    """Send aggregate (portfolio-wide) KPI metrics to DataDog.

    Args:
        agg: An AggregateKPI object rolled up across all frameworks.
    """
    tags = ["framework:aggregate"] + _COMMON_TAGS
    series = [
        _gauge("kpi.pass_rate",         agg.overall_pass_rate,       tags),
        _gauge("kpi.failure_density",   agg.overall_failure_density, tags),
        _gauge("kpi.total_tests",       agg.total_tests,             tags),
        _gauge("kpi.suite_stability",   agg.suite_stability,         tags),
        _gauge("kpi.flakiness_rate",    agg.flakiness_rate,          tags),
    ]
    if agg.mttd_seconds is not None:
        series.append(_gauge("kpi.mttd_seconds", agg.mttd_seconds, tags))
    _post(series)
