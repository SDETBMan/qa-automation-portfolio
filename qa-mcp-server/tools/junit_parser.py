"""MCP tool wrapper for JUnit XML parsing.

Wraps flakiness-detector/flakiness/parser.py — parse_junit_xml() and
parse_directory() — to produce structured JSON from JUnit XML files.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import asdict
from pathlib import Path

from flakiness.parser import parse_directory as _parse_directory
from flakiness.parser import parse_junit_xml as _parse_junit_xml

from utils.datadog_reporter import report_tool_call


async def parse_junit_xml(xml_path: str) -> str:
    """Parse JUnit XML file(s) and return structured test results.

    Args:
        xml_path: Absolute path to a JUnit XML file or directory of XML files.

    Returns:
        JSON with summary counts and per-test results.
    """
    start = time.time()
    error = None
    try:
        p = Path(xml_path)
        if not p.exists():
            raise FileNotFoundError(f"Path not found: {xml_path}")

        if p.is_dir():
            runs = _parse_directory(p)
        else:
            runs = [_parse_junit_xml(p)]

        all_results = []
        for run in runs:
            for r in run.results:
                all_results.append(asdict(r))

        passed = sum(1 for r in all_results if r["status"] == "passed")
        failed = sum(1 for r in all_results if r["status"] == "failed")
        skipped = sum(1 for r in all_results if r["status"] == "skipped")
        errored = sum(1 for r in all_results if r["status"] == "error")

        output = {
            "summary": {
                "total": len(all_results),
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "error": errored,
            },
            "results": all_results,
        }
        return json.dumps(output, indent=2)
    except Exception as exc:
        error = str(exc)
        raise
    finally:
        duration_ms = (time.time() - start) * 1000
        report_tool_call("parse_junit_xml", duration_ms, error)
