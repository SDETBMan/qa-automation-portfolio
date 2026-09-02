"""
datadog_reporter.py — Send MCP tool invocation metrics to DataDog.

Emits GAUGE metrics for tool invocations, errors, and duration
to the DataDog v2 HTTP API. Follows the same graceful-skip pattern
used by every other framework in the monorepo: DD_API_KEY absent ->
log warning -> return without raising -> server stays healthy.

Metrics emitted:
  mcp.tool_invocations    Count of tool calls (tagged tool:<name>)
  mcp.tool_errors         Count of tool errors (tagged tool:<name>)
  mcp.tool_duration_ms    Tool execution time in ms (tagged tool:<name>)
"""

from __future__ import annotations

import os
import sys
import time

import requests

_COMMON_TAGS = ["service:qa-automation-portfolio", "env:ci"]


def _api_key() -> str | None:
    """Return DD_API_KEY from the environment, or None if not set."""
    key = os.getenv("DD_API_KEY", "")
    return key if key else None


def _gauge(metric: str, value: float, tags: list[str]) -> dict:
    """Build one DataDog v2 series entry for a GAUGE metric."""
    return {
        "metric": metric,
        "type": 3,  # 3 = GAUGE in DataDog's metric type enum
        "points": [{"timestamp": int(time.time()), "value": value}],
        "tags": tags,
    }


def _post(series: list[dict]) -> None:
    """POST a list of series dicts to the DataDog v2 metrics endpoint.

    Silently skips if DD_API_KEY is absent. Catches all exceptions so a
    DataDog outage or misconfiguration never affects the MCP server.
    """
    api_key = _api_key()
    if not api_key:
        return  # Skip silently — no warning on every tool call

    site = os.getenv("DD_SITE", "datadoghq.com")
    url = f"https://api.{site}/api/v2/series"

    try:
        resp = requests.post(
            url,
            headers={"DD-API-KEY": api_key, "Content-Type": "application/json"},
            json={"series": series},
            timeout=10,
        )
        if resp.status_code not in (200, 202):
            print(
                f"[WARN] DataDog metrics returned HTTP {resp.status_code}.",
                file=sys.stderr,
            )
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] DataDog metrics failed: {exc}", file=sys.stderr)


def report_tool_call(
    tool_name: str,
    duration_ms: float,
    error: str | None = None,
) -> None:
    """Report a tool invocation to DataDog.

    Args:
        tool_name: Name of the MCP tool that was called.
        duration_ms: Wall-clock execution time in milliseconds.
        error: Error message if the tool failed, None on success.
    """
    tags = [f"tool:{tool_name}"] + _COMMON_TAGS
    series = [
        _gauge("mcp.tool_invocations", 1, tags),
        _gauge("mcp.tool_duration_ms", duration_ms, tags),
    ]
    if error is not None:
        series.append(_gauge("mcp.tool_errors", 1, tags))
    _post(series)
