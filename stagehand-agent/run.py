"""
run.py — Stagehand Agent CLI entry point.

Usage:
    python run.py --mode compare
    python run.py --mode traditional --scenarios login cart
    python run.py --mode ai --output output/report --format both
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from comparison.reporter import generate_json_report, generate_markdown_report
from comparison.runner import run_comparison
from utils.datadog_reporter import send_comparison_metrics


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Compare traditional Playwright automation vs AI-driven Stagehand on SauceDemo",
    )
    parser.add_argument(
        "--mode",
        choices=["traditional", "ai", "compare"],
        default="compare",
        help="Run mode: traditional (POM only), ai (Stagehand only), or compare (both) (default: compare)",
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        choices=["login", "inventory", "cart", "checkout", "all"],
        default=["all"],
        help="Scenarios to run (default: all)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/comparison"),
        help="Output file path without extension (default: output/comparison)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "both"],
        default="both",
        help="Output format (default: both)",
    )
    args = parser.parse_args()

    # Resolve "all" to the full scenario list
    scenarios = None  # None means all in run_comparison
    if "all" not in args.scenarios:
        scenarios = args.scenarios

    print(f"[INFO] Mode: {args.mode}")
    print(f"[INFO] Scenarios: {scenarios or 'all'}")

    # Run comparison
    report = run_comparison(
        mode=args.mode,
        scenarios=scenarios,
    )

    # Generate output
    if args.format in ("json", "both"):
        json_output = generate_json_report(report)
        json_path = args.output.with_suffix(".json")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json_output, encoding="utf-8")
        print(f"[INFO] JSON report written to {json_path}")

    if args.format in ("markdown", "both"):
        md_output = generate_markdown_report(report)
        md_path = args.output.with_suffix(".md")
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(md_output, encoding="utf-8")
        print(f"[INFO] Markdown report written to {md_path}")

    # Summary
    passed_count = sum(1 for s in report.scenarios if s.passed)
    total_count = len(report.scenarios)
    print(f"\n[RESULT] Passed: {passed_count}/{total_count}")
    print(f"[RESULT] Traditional: {report.traditional_total_ms:.1f}ms")
    print(f"[RESULT] AI-driven: {report.ai_driven_total_ms:.1f}ms")
    if report.speed_ratio > 0:
        print(f"[RESULT] Speed ratio (AI/Traditional): {report.speed_ratio}x")
    print(f"[RESULT] AI tokens used: {report.ai_total_tokens}")

    # Send DataDog metrics
    send_comparison_metrics(
        traditional_duration_ms=report.traditional_total_ms,
        ai_driven_duration_ms=report.ai_driven_total_ms,
        ai_tokens_used=report.ai_total_tokens,
        speed_ratio=report.speed_ratio,
        scenarios_passed=passed_count,
        scenarios_total=total_count,
    )

    if not report.all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
