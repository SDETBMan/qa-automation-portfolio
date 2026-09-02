"""MCP tool wrapper for flakiness analysis.

Wraps flakiness-detector/flakiness/analyzer.py — analyze() — to detect
flaky tests across multiple CI runs from JUnit XML files.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path

from flakiness.analyzer import analyze as _analyze
from flakiness.parser import parse_directory as _parse_directory

from utils.datadog_reporter import report_tool_call


async def analyze_flakiness(xml_dir: str, threshold: float = 0.15) -> str:
    """Detect flaky tests across multiple CI runs.

    Args:
        xml_dir: Directory containing JUnit XML files (one per CI run).
        threshold: Flakiness score threshold (0.0-1.0). Tests above this
                   are recommended for quarantine. Default 0.15.

    Returns:
        JSON with total_tests, total_flaky, total_runs, and lists of
        tests recommended for quarantine vs monitoring.
    """
    start = time.time()
    error = None
    try:
        p = Path(xml_dir)
        if not p.is_dir():
            raise NotADirectoryError(f"Not a directory: {xml_dir}")

        runs = _parse_directory(p)
        if not runs:
            return json.dumps({
                "total_tests": 0,
                "total_flaky": 0,
                "total_runs": 0,
                "quarantine_recommended": [],
                "monitor": [],
            }, indent=2)

        summary = _analyze(runs, threshold=threshold)

        quarantine = []
        monitor = []
        for t in summary.tests:
            entry = asdict(t)
            if t.flakiness_score >= threshold:
                quarantine.append(entry)
            elif t.flakiness_score > 0:
                monitor.append(entry)

        output = {
            "total_tests": summary.total_tests,
            "total_flaky": summary.total_flaky,
            "total_runs": summary.total_runs,
            "quarantine_recommended": quarantine,
            "monitor": monitor,
        }
        return json.dumps(output, indent=2)
    except Exception as exc:
        error = str(exc)
        raise
    finally:
        duration_ms = (time.time() - start) * 1000
        report_tool_call("analyze_flakiness", duration_ms, error)
