"""
run.py — Quality KPI dashboard CLI entry point.

Usage:
    python run.py --xml-dir ./results/
    python run.py --xml-dir ./results/ --output report.json
    python run.py --from-github --repo SDETBMan/qa-automation-portfolio

Flow:
    1. Parse JUnit XML files from local directory or GitHub Actions artifacts
    2. Compute per-framework KPIs
    3. Compute aggregate (portfolio-wide) KPIs
    4. Optionally fetch MTTD and suite stability from GitHub Actions API
    5. Send all metrics to DataDog
    6. Write JSON report to stdout or file
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from kpi_calculator import (
    AggregateKPI,
    FrameworkKPI,
    compute_aggregate_kpi,
    compute_framework_kpi,
    compute_mttd,
    compute_suite_stability,
)

# Reuse flakiness-detector's parser via kpi_calculator (avoids sys.path manipulation)
from kpi_calculator import RunResults, parse_directory


def _group_runs_by_suite(runs: list[RunResults]) -> dict[str, list[RunResults]]:
    """Group run results by suite name for per-framework KPI computation.

    If results span multiple suites, each suite becomes a separate
    'framework'.  If all results share one suite, the run_id is used.
    """
    suite_map: dict[str, list[RunResults]] = defaultdict(list)

    for run in runs:
        # Collect unique suite names in this run
        suites_in_run: set[str] = set()
        for result in run.results:
            suites_in_run.add(result.suite)

        if len(suites_in_run) <= 1:
            # Single suite or empty — group by run
            suite_name = next(iter(suites_in_run), run.run_id)
            suite_map[suite_name].append(run)
        else:
            # Multiple suites — split into per-suite RunResults
            for suite_name in suites_in_run:
                filtered_results = [r for r in run.results if r.suite == suite_name]
                filtered_run = RunResults(
                    run_id=run.run_id,
                    results=filtered_results,
                )
                suite_map[suite_name].append(filtered_run)

    return dict(suite_map)


def _build_report(aggregate: AggregateKPI) -> dict:
    """Convert AggregateKPI to a JSON-serializable report dict."""
    report = {
        "report": "Quality KPI Dashboard",
        "timestamp": aggregate.timestamp,
        "aggregate": {
            "overall_pass_rate": round(aggregate.overall_pass_rate, 4),
            "overall_failure_density": round(aggregate.overall_failure_density, 4),
            "total_tests": aggregate.total_tests,
            "total_passed": aggregate.total_passed,
            "total_failed": aggregate.total_failed,
            "flakiness_rate": aggregate.flakiness_rate,
            "mttd_seconds": aggregate.mttd_seconds,
            "mttr_seconds": aggregate.mttr_seconds,
            "suite_stability": aggregate.suite_stability,
        },
        "frameworks": [],
    }

    for fw in aggregate.frameworks:
        report["frameworks"].append({
            "framework": fw.framework,
            "pass_rate": round(fw.pass_rate, 4),
            "failure_density": round(fw.failure_density, 4),
            "avg_duration_s": fw.avg_duration_s,
            "p95_duration_s": fw.p95_duration_s,
            "total_tests": fw.total_tests,
            "passed": fw.passed,
            "failed": fw.failed,
            "skipped": fw.skipped,
            "error": fw.error,
        })

    return report


def run_from_xml_dir(xml_dir: Path, output: Path | None = None) -> dict:
    """Parse JUnit XML from a directory and compute KPIs.

    Args:
        xml_dir: Directory containing JUnit XML files.
        output: Optional path to write JSON report.

    Returns:
        Report dict.
    """
    print(f"Parsing JUnit XML from {xml_dir}...")
    runs = parse_directory(xml_dir)

    if not runs:
        print("[WARN] No JUnit XML files found.")
        return {}

    total_results = sum(len(r.results) for r in runs)
    print(f"  Found {len(runs)} XML file(s) with {total_results} test results.")

    # Group by suite for per-framework breakdown
    suite_groups = _group_runs_by_suite(runs)
    print(f"  Detected {len(suite_groups)} framework(s): {', '.join(suite_groups.keys())}")

    # Compute per-framework KPIs
    framework_kpis: list[FrameworkKPI] = []
    for suite_name, suite_runs in suite_groups.items():
        kpi = compute_framework_kpi(suite_runs, framework=suite_name)
        framework_kpis.append(kpi)
        print(f"  [{suite_name}] pass_rate={kpi.pass_rate:.2%}  "
              f"failure_density={kpi.failure_density:.2%}  "
              f"tests={kpi.total_tests}")

    # Compute historical pass rates for suite stability
    pass_rates = [kpi.pass_rate for kpi in framework_kpis]
    stability = compute_suite_stability(pass_rates)

    # Compute aggregate KPIs
    timestamp = datetime.now(timezone.utc).isoformat()
    aggregate = compute_aggregate_kpi(
        framework_kpis=framework_kpis,
        suite_stability=stability,
        timestamp=timestamp,
    )

    print(f"\n  Aggregate: pass_rate={aggregate.overall_pass_rate:.2%}  "
          f"failure_density={aggregate.overall_failure_density:.2%}  "
          f"total_tests={aggregate.total_tests}  "
          f"suite_stability={aggregate.suite_stability:.2%}")

    # Send to DataDog
    try:
        from datadog_reporter import send_aggregate_kpis, send_framework_kpis
        for kpi in framework_kpis:
            send_framework_kpis(kpi)
        send_aggregate_kpis(aggregate)
    except Exception as exc:  # noqa: BLE001
        print(f"[WARN] DataDog reporting skipped: {exc}")

    # Build and output report
    report = _build_report(aggregate)
    report_json = json.dumps(report, indent=2)

    if output:
        output.write_text(report_json, encoding="utf-8")
        print(f"\nReport written to {output}")
    else:
        print(f"\n{report_json}")

    return report


def run_from_github(repo: str, output: Path | None = None) -> dict:
    """Fetch workflow data from GitHub Actions and compute KPIs.

    Args:
        repo: GitHub repository in owner/repo format.
        output: Optional path to write JSON report.

    Returns:
        Report dict.
    """
    from github_actions import (
        compute_mttd_from_runs,
        compute_mttr_from_runs,
        fetch_historical_pass_rates,
        fetch_workflow_runs,
    )

    workflows = [
        "playwright.yml",
        "selenium-java.yml",
        "cucumber.yml",
        "cypress.yml",
        "ai-eval.yml",
        "conv-eval.yml",
        "agent-eval.yml",
        "flakiness-detector.yml",
    ]

    print(f"Fetching workflow data from {repo}...")
    all_runs: list[dict] = []
    pass_rates: list[float] = []
    per_workflow_mttrs: list[float] = []

    for wf in workflows:
        runs = fetch_workflow_runs(repo, wf, limit=10)
        all_runs.extend(runs)
        rates = fetch_historical_pass_rates(repo, wf, limit=10)
        pass_rates.extend(rates)

        # Compute per-workflow MTTR (avoid cross-workflow false recoveries)
        wf_mttr = compute_mttr_from_runs(runs)
        if wf_mttr is not None:
            per_workflow_mttrs.append(wf_mttr)

        success = sum(1 for r in runs if r.get("conclusion") == "success")
        failure = sum(1 for r in runs if r.get("conclusion") == "failure")
        print(f"  [{wf}] {len(runs)} runs, {success} success, {failure} failure")

    # Compute MTTD from all failed runs
    mttd = compute_mttd_from_runs(all_runs)
    stability = compute_suite_stability(pass_rates) if pass_rates else 0.0

    # Average per-workflow MTTR values (excluding workflows with no recovery pairs)
    import statistics
    mttr: float | None = None
    if per_workflow_mttrs:
        mttr = round(statistics.mean(per_workflow_mttrs), 1)

    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"\n  MTTD: {mttd}s  MTTR: {mttr}s  Suite Stability: {stability:.2%}")

    report = {
        "report": "Quality KPI Dashboard (GitHub Actions)",
        "timestamp": timestamp,
        "aggregate": {
            "mttd_seconds": mttd,
            "mttr_seconds": mttr,
            "suite_stability": stability,
            "total_workflow_runs": len(all_runs),
        },
        "workflows_checked": workflows,
    }

    report_json = json.dumps(report, indent=2)

    if output:
        output.write_text(report_json, encoding="utf-8")
        print(f"\nReport written to {output}")
    else:
        print(f"\n{report_json}")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quality KPI Dashboard — aggregate test KPIs across all frameworks"
    )
    parser.add_argument(
        "--xml-dir",
        type=Path,
        default=None,
        help="Directory containing JUnit XML result files",
    )
    parser.add_argument(
        "--from-github",
        action="store_true",
        help="Fetch workflow data from GitHub Actions API",
    )
    parser.add_argument(
        "--repo",
        type=str,
        default="SDETBMan/qa-automation-portfolio",
        help="GitHub repository (owner/repo) for --from-github mode",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON report to file (default: stdout)",
    )
    args = parser.parse_args()

    if not args.xml_dir and not args.from_github:
        parser.error("Provide --xml-dir or --from-github")

    if args.xml_dir:
        run_from_xml_dir(args.xml_dir, args.output)

    if args.from_github:
        run_from_github(args.repo, args.output)


if __name__ == "__main__":
    main()
