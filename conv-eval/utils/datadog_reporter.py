"""
datadog_reporter.py — Sends test metrics and LLM evaluation scores to DataDog.

Two public functions:
  send_test_metrics(passed, failed, skipped, duration_ms, framework)
      Called once per pytest session from conftest.pytest_sessionfinish.
      Posts suite-level pass/fail/skip/duration counts as GAUGE metrics.

  send_eval_score(metric_name, score, extra_tags)
      Called after each assert_test() in the eval test files.
      Posts one LLM evaluation score (e.g. conversation relevancy, role
      adherence) as a GAUGE metric so DataDog dashboards can chart AI
      conversational quality over time.

Graceful-skip pattern (mirrors SlackUtils in the Java/C# frameworks):
  DD_API_KEY absent → log warning → return without raising → CI stays green.

DataDog v2 metrics API:
  POST https://api.datadoghq.com/api/v2/series
  Header: DD-API-KEY: <key>
  Body:   { "series": [ { "metric": "...", "type": 3, "points": [...], "tags": [...] } ] }
  Success: HTTP 202 Accepted

Metric type 3 = GAUGE (point-in-time snapshot — suitable for scores and counts
that do not need to accumulate across requests).
"""

from __future__ import annotations

import os
import time

import requests

_DD_API_URL  = "https://api.datadoghq.com/api/v2/series"
_COMMON_TAGS = ["service:qa-automation-portfolio", "env:ci"]


# ── Internal helpers ──────────────────────────────────────────────────────────

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

    try:
        resp = requests.post(
            _DD_API_URL,
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

def send_test_metrics(
    passed:      int,
    failed:      int,
    skipped:     int,
    duration_ms: float,
    framework:   str = "conv-eval",
) -> None:
    """Send suite-level pass/fail/skip/duration metrics to DataDog.

    Args:
        passed:      Number of tests that passed.
        failed:      Number of tests that failed.
        skipped:     Number of tests that were skipped.
        duration_ms: Total session wall-clock duration in milliseconds.
        framework:   Short framework label for the tag, e.g. "conv-eval".
    """
    tags = [f"framework:{framework}"] + _COMMON_TAGS
    _post([
        _gauge("test.suite.passed",      passed,      tags),
        _gauge("test.suite.failed",      failed,      tags),
        _gauge("test.suite.skipped",     skipped,     tags),
        _gauge("test.suite.duration_ms", duration_ms, tags),
    ])


def send_eval_score(
    metric_name: str,
    score:       float,
    extra_tags:  list[str] | None = None,
) -> None:
    """Send a single LLM evaluation score metric to DataDog.

    Args:
        metric_name: DataDog metric name, e.g. "llm.conv.knowledge_retention".
        score:       The evaluation score (typically 0.0–1.0).
        extra_tags:  Optional additional tags, e.g. ["model:gpt-4o-mini"].

    Example:
        send_eval_score("llm.conv.role_adherence", 0.95, ["model:gpt-4o-mini"])
    """
    tags = (extra_tags or []) + _COMMON_TAGS
    _post([_gauge(metric_name, score, tags)])
