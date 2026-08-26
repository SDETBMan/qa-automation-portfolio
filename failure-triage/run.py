"""
run.py — Failure triage agent CLI entry point.

Usage:
    python run.py --xml-dir ../flakiness-detector/fixtures/
    python run.py --xml-dir ./results/ --output triage_report.json

    # Multi-framework correlation
    python run.py --xml-dir ../cypress/results --xml-dir ../selenium-java/results
    python run.py --xml-dir ./cypress-results --framework cypress \
                  --xml-dir ./selenium-results --framework selenium
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
        action="append",
        dest="xml_dirs",
        required=True,
        help="Directory containing JUnit XML result files (repeatable for multi-framework)",
    )
    parser.add_argument(
        "--framework",
        type=str,
        action="append",
        dest="frameworks",
        default=None,
        help="Framework label for each --xml-dir (repeatable, must match --xml-dir count)",
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

    xml_dirs: list[Path] = args.xml_dirs
    frameworks: list[str] | None = args.frameworks

    # Validate framework labels match xml-dir count when provided
    if frameworks and len(frameworks) != len(xml_dirs):
        parser.error(
            f"--framework count ({len(frameworks)}) must match "
            f"--xml-dir count ({len(xml_dirs)})"
        )

    # Derive framework names from directory paths if not provided
    if not frameworks:
        frameworks = [d.resolve().parent.name if d.name == "results" else d.resolve().name for d in xml_dirs]

    # Validate all directories exist
    for d in xml_dirs:
        if not d.exists():
            print(f"[ERROR] XML directory not found: {d}")
            return

    # Build (path, framework_name) tuples
    xml_sources = list(zip(xml_dirs, frameworks))

    report = run_triage(
        xml_sources=xml_sources,
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
