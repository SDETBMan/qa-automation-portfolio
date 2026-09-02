"""MCP tool wrapper for claims CSV diffing.

Wraps claims-diff/differ/loader.py and claims-diff/differ/diff_engine.py
to compare two claims CSV files and return field-level diffs.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from differ.diff_engine import diff_claims as _diff_claims
from differ.loader import load_claims_csv as _load_csv

from utils.datadog_reporter import report_tool_call


def _serialize_diff_report(report) -> dict:
    """Convert a DiffReport to a JSON-serializable dict."""
    diffs = []
    for d in report.diffs:
        entry = {
            "claim_id": d.claim_id,
            "change_type": d.change_type,
        }
        if d.field_diffs:
            entry["field_diffs"] = [
                {
                    "field": fd.field,
                    "baseline_value": str(fd.baseline_value),
                    "current_value": str(fd.current_value),
                }
                for fd in d.field_diffs
            ]
        diffs.append(entry)

    return {
        "total_baseline": report.total_baseline,
        "total_current": report.total_current,
        "added": report.added,
        "removed": report.removed,
        "modified": report.modified,
        "unchanged": report.unchanged,
        "diffs": diffs,
    }


async def diff_claims(baseline_csv: str, current_csv: str) -> str:
    """Compare two claims CSV files and return field-level diffs.

    Args:
        baseline_csv: Absolute path to the baseline claims CSV file.
        current_csv: Absolute path to the current claims CSV file.

    Returns:
        JSON with total_baseline, total_current, added/removed/modified/
        unchanged counts, and per-claim field-level diffs.
    """
    start = time.time()
    error = None
    try:
        bp = Path(baseline_csv)
        cp = Path(current_csv)
        if not bp.exists():
            raise FileNotFoundError(f"Baseline CSV not found: {baseline_csv}")
        if not cp.exists():
            raise FileNotFoundError(f"Current CSV not found: {current_csv}")

        baseline = _load_csv(bp)
        current = _load_csv(cp)
        report = _diff_claims(baseline, current)

        return json.dumps(_serialize_diff_report(report), indent=2)
    except Exception as exc:
        error = str(exc)
        raise
    finally:
        duration_ms = (time.time() - start) * 1000
        report_tool_call("diff_claims", duration_ms, error)
