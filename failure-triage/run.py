"""
run.py — Failure triage agent CLI entry point.

Usage:
    python run.py --xml-dir ../flakiness-detector/fixtures/
    python run.py --xml-dir ./results/ --output triage_report.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from triage_agent import run_triage


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Failure Triage Agent — AI-powered root cause clustering of test failures"
    )
    parser.add_argument(
        "--xml-dir",
        type=Path,
        required=True,
        help="Directory containing JUnit XML result files",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("triage_report.json"),
        help="Path to write the triage report JSON (default: triage_report.json)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress agent output (only write report file)",
    )
    args = parser.parse_args()

    if not args.xml_dir.exists():
        print(f"[ERROR] XML directory not found: {args.xml_dir}")
        return

    report = run_triage(
        xml_dir=str(args.xml_dir),
        output_path=str(args.output),
        verbose=not args.quiet,
    )

    if report:
        # Send metrics to DataDog
        try:
            from datadog_reporter import send_triage_metrics
            send_triage_metrics(report)
        except Exception as exc:  # noqa: BLE001
            print(f"[WARN] DataDog reporting skipped: {exc}")

        if args.quiet:
            print(json.dumps(report, indent=2))
    else:
        print("[WARN] No triage report produced.")


if __name__ == "__main__":
    main()
