#!/usr/bin/env python3
"""Claims Adjudication Data Diff Engine.

Compares two sets of healthcare claim records and reports differences.
Demonstrates BigQuery/SQL data validation patterns for claims adjudication QA.

Usage:
    python run.py                                          # diff default datasets
    python run.py --baseline path/to/base.csv --current path/to/curr.csv
    python run.py --output output/diff_report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from differ.diff_engine import diff_claims
from differ.loader import load_claims_csv

_HERE = Path(__file__).resolve().parent
_DATASETS = _HERE / "datasets"
_OUTPUT = _HERE / "output"


def _print_diff_table(report) -> None:
    """Print a formatted diff summary table."""
    print()
    print("=" * 80)
    print("  CLAIMS ADJUDICATION DIFF REPORT")
    print("=" * 80)
    print(f"  Baseline claims: {report.total_baseline}")
    print(f"  Current claims:  {report.total_current}")
    print(f"  Unchanged:       {report.unchanged}")
    print(f"  Modified:        {report.modified}")
    print(f"  Added:           {report.added}")
    print(f"  Removed:         {report.removed}")
    print("=" * 80)

    if not report.diffs:
        print("  No differences found.")
        return

    print()
    for diff in report.diffs:
        if diff.change_type == "added":
            print(f"  + {diff.claim_id} (added)")
        elif diff.change_type == "removed":
            print(f"  - {diff.claim_id} (removed)")
        elif diff.change_type == "modified":
            print(f"  ~ {diff.claim_id} (modified)")
            for fd in diff.field_diffs:
                print(f"      {fd.field}: {fd.baseline_value!r} -> {fd.current_value!r}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python run.py",
        description="Claims Adjudication Data Diff Engine",
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default=str(_DATASETS / "baseline_claims.csv"),
        help="Path to baseline claims CSV (default: datasets/baseline_claims.csv)",
    )
    parser.add_argument(
        "--current",
        type=str,
        default=str(_DATASETS / "current_claims.csv"),
        help="Path to current claims CSV (default: datasets/current_claims.csv)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to write JSON diff report (default: output/diff_report.json)",
    )
    args = parser.parse_args()

    baseline_path = Path(args.baseline)
    current_path = Path(args.current)

    if not baseline_path.exists():
        print(f"error: baseline file not found: {baseline_path}", file=sys.stderr)
        raise SystemExit(1)
    if not current_path.exists():
        print(f"error: current file not found: {current_path}", file=sys.stderr)
        raise SystemExit(1)

    baseline = load_claims_csv(baseline_path)
    current = load_claims_csv(current_path)

    report = diff_claims(baseline, current)
    _print_diff_table(report)

    # Write JSON report
    output_path = Path(args.output) if args.output else _OUTPUT / "diff_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"  Report written: {output_path}")

    # Exit non-zero if unexpected diffs found
    total_diffs = report.added + report.removed + report.modified
    if total_diffs > 0:
        print(f"\n  {total_diffs} difference(s) detected.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
