"""MCP tool wrapper for quality KPI computation.

Wraps quality-dashboard/kpi_calculator.py — compute_framework_kpi() and
compute_aggregate_kpi() — to produce pass rate, failure density, and
duration KPIs from JUnit XML files.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path

from kpi_calculator import (
    compute_aggregate_kpi as _compute_aggregate,
    compute_framework_kpi as _compute_framework,
    parse_directory,
)

from utils.datadog_reporter import report_tool_call


async def compute_quality_kpis(xml_dir: str) -> str:
    """Compute quality KPIs from JUnit XML test results.

    Args:
        xml_dir: Directory containing JUnit XML files.

    Returns:
        JSON with aggregate KPIs (overall_pass_rate, failure_density,
        total_tests, suite_stability) and per-framework breakdown.
    """
    start = time.time()
    error = None
    try:
        p = Path(xml_dir)
        if not p.is_dir():
            raise NotADirectoryError(f"Not a directory: {xml_dir}")

        runs = parse_directory(p)
        if not runs:
            return json.dumps({
                "aggregate": {
                    "overall_pass_rate": 0.0,
                    "failure_density": 0.0,
                    "total_tests": 0,
                    "suite_stability": 0.0,
                },
                "frameworks": [],
            }, indent=2)

        fw_kpi = _compute_framework(runs, framework="suite")
        agg_kpi = _compute_aggregate([fw_kpi])

        fw_dict = asdict(fw_kpi)
        agg_dict = {
            "overall_pass_rate": round(agg_kpi.overall_pass_rate, 4),
            "failure_density": round(agg_kpi.overall_failure_density, 4),
            "total_tests": agg_kpi.total_tests,
            "total_passed": agg_kpi.total_passed,
            "total_failed": agg_kpi.total_failed,
            "suite_stability": agg_kpi.suite_stability,
            "timestamp": agg_kpi.timestamp,
        }

        output = {
            "aggregate": agg_dict,
            "frameworks": [fw_dict],
        }
        return json.dumps(output, indent=2)
    except Exception as exc:
        error = str(exc)
        raise
    finally:
        duration_ms = (time.time() - start) * 1000
        report_tool_call("compute_quality_kpis", duration_ms, error)
