"""
datadog_reporter.py — Sends job-agent run metrics to DataDog.

Three public functions:
  send_run_metrics(jobs_found, jobs_scored, cover_letters_drafted, duration_ms)
      Called once at the end of a job-agent run.
      Posts per-run counters as GAUGE metrics.

  send_api_latency(latency_ms)
      Posts LLM API latency tagged framework:job-agent.

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

_DD_API_URL  = "https://api.datadoghq.com/api/v2/series"
_COMMON_TAGS = ["service:qa-automation-portfolio", "env:ci", "framework:job-agent"]


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


def send_run_metrics(
    jobs_found:             int,
    jobs_scored:            int,
    cover_letters_drafted:  int,
    duration_ms:            float,
) -> None:
    """Send per-run job-agent metrics to DataDog."""
    _post([
        _gauge("llm.job_agent.jobs_found",            jobs_found,            _COMMON_TAGS),
        _gauge("llm.job_agent.jobs_scored",           jobs_scored,           _COMMON_TAGS),
        _gauge("llm.job_agent.cover_letters_drafted", cover_letters_drafted, _COMMON_TAGS),
        _gauge("llm.job_agent.duration_ms",           duration_ms,           _COMMON_TAGS),
    ])


def send_api_latency(latency_ms: float) -> None:
    """Send LLM API latency metric tagged framework:job-agent."""
    _post([_gauge("llm.api.latency_ms", latency_ms, _COMMON_TAGS)])
