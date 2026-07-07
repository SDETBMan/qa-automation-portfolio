"""
run.py — Flakiness detector CLI entry point.

Usage:
    python run.py --xml-dir ./fixtures/
    python run.py --xml-dir ./fixtures/ --threshold 0.20
    python run.py --xml-dir ./fixtures/ --output report.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from flakiness.parser import parse_directory
from flakiness.analyzer import analyze
from flakiness.reporter import generate_report
from flakiness.datadog import send_flakiness_metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect flaky tests from JUnit XML results")
    parser.add_argument(
        "--xml-dir",
        type=Path,
        required=True,
        help="Directory containing JUnit XML files",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.15,
        help="Flakiness score threshold for quarantine (default: 0.15)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write markdown report to file (default: stdout)",
    )
    args = parser.parse_args()

    if not args.xml_dir.exists():
        print(f"Error: directory {args.xml_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    # Parse → Analyze → Report
    runs = parse_directory(args.xml_dir)
    if not runs:
        print("No JUnit XML files found.", file=sys.stderr)
        sys.exit(1)

    summary = analyze(runs, threshold=args.threshold)
    report = generate_report(summary, threshold=args.threshold)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report)

    # Send to DataDog
    quarantined = sum(1 for t in summary.tests if t.flakiness_score >= args.threshold)
    scores = {t.test_key: t.flakiness_score for t in summary.tests if t.flakiness_score > 0}
    send_flakiness_metrics(
        total_flaky=summary.total_flaky,
        quarantined_count=quarantined,
        scores=scores,
    )


if __name__ == "__main__":
    main()
