"""
kpi_calculator.py — Core KPI computation engine.

Aggregates test results across all frameworks from JUnit XML files,
computes derived quality KPIs (pass rate, failure density, MTTD,
suite stability), and produces per-framework and aggregate roll-ups.

Data source: JUnit XML files (same format every framework produces).
Reuses flakiness-detector's parser for JUnit XML parsing.
"""

from __future__ import annotations

import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Add flakiness-detector to path so we can reuse its parser
_REPO_ROOT = Path(__file__).parent.parent
_FLAKINESS_DIR = _REPO_ROOT / "flakiness-detector"
if str(_FLAKINESS_DIR) not in sys.path:
    sys.path.insert(0, str(_FLAKINESS_DIR))

from flakiness.parser import RunResults, TestResult, parse_directory, parse_junit_xml  # noqa: E402


@dataclass
class FrameworkKPI:
    """Per-framework quality KPIs computed from JUnit XML results."""

    framework: str
    pass_rate: float          # passed / total
    failure_density: float    # failed / total
    avg_duration_s: float     # mean test execution time
    p95_duration_s: float     # 95th percentile duration
    total_tests: int
    passed: int
    failed: int
    skipped: int
    error: int


@dataclass
class AggregateKPI:
    """Portfolio-wide quality KPIs aggregated across all frameworks."""

    frameworks: list[FrameworkKPI]
    overall_pass_rate: float
    overall_failure_density: float
    total_tests: int
    total_passed: int
    total_failed: int
    flakiness_rate: float          # from flakiness-detector data if available
    mttd_seconds: float | None     # mean time to detect (commit → CI failure)
    suite_stability: float         # pass rate over last N runs
    timestamp: str


def compute_framework_kpi(runs: list[RunResults], framework: str = "") -> FrameworkKPI:
    """Compute per-framework KPIs from JUnit XML run results.

    Args:
        runs: List of RunResults from parsing JUnit XML files.
        framework: Framework name label. If empty, derived from first run_id.
    """
    all_results: list[TestResult] = []
    for run in runs:
        all_results.extend(run.results)

    total = len(all_results)
    if total == 0:
        return FrameworkKPI(
            framework=framework or "unknown",
            pass_rate=0.0,
            failure_density=0.0,
            avg_duration_s=0.0,
            p95_duration_s=0.0,
            total_tests=0,
            passed=0,
            failed=0,
            skipped=0,
            error=0,
        )

    passed = sum(1 for r in all_results if r.status == "passed")
    failed = sum(1 for r in all_results if r.status == "failed")
    skipped = sum(1 for r in all_results if r.status == "skipped")
    error = sum(1 for r in all_results if r.status == "error")

    durations = [r.time_s for r in all_results if r.time_s > 0]
    avg_duration = statistics.mean(durations) if durations else 0.0
    p95_duration = _percentile(durations, 95) if durations else 0.0

    fw_name = framework or (runs[0].run_id if runs else "unknown")

    return FrameworkKPI(
        framework=fw_name,
        pass_rate=passed / total if total > 0 else 0.0,
        failure_density=failed / total if total > 0 else 0.0,
        avg_duration_s=round(avg_duration, 3),
        p95_duration_s=round(p95_duration, 3),
        total_tests=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        error=error,
    )


def compute_aggregate_kpi(
    framework_kpis: list[FrameworkKPI],
    flakiness_rate: float = 0.0,
    mttd_seconds: float | None = None,
    suite_stability: float = 0.0,
    timestamp: str = "",
) -> AggregateKPI:
    """Roll up per-framework KPIs into portfolio-wide aggregate KPIs.

    Args:
        framework_kpis: List of FrameworkKPI objects.
        flakiness_rate: Portfolio-wide flakiness rate (0–1).
        mttd_seconds: Mean time to detect (commit → CI failure), in seconds.
        suite_stability: Pass rate trend over last N runs (0–1).
        timestamp: ISO 8601 timestamp for the report.
    """
    total_tests = sum(f.total_tests for f in framework_kpis)
    total_passed = sum(f.passed for f in framework_kpis)
    total_failed = sum(f.failed for f in framework_kpis)

    if not timestamp:
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).isoformat()

    return AggregateKPI(
        frameworks=framework_kpis,
        overall_pass_rate=total_passed / total_tests if total_tests > 0 else 0.0,
        overall_failure_density=total_failed / total_tests if total_tests > 0 else 0.0,
        total_tests=total_tests,
        total_passed=total_passed,
        total_failed=total_failed,
        flakiness_rate=flakiness_rate,
        mttd_seconds=mttd_seconds,
        suite_stability=suite_stability,
        timestamp=timestamp,
    )


def compute_mttd(workflow_runs: list[dict]) -> float | None:
    """Compute mean time to detect from workflow run data.

    Each dict should have:
      - 'created_at': ISO timestamp when the workflow started (≈ push time)
      - 'updated_at': ISO timestamp when the workflow concluded
      - 'conclusion': 'failure' | 'success' | etc.

    Returns average seconds from push to failure detection, or None if
    no failed runs are available.
    """
    from datetime import datetime

    failure_times: list[float] = []
    for run in workflow_runs:
        if run.get("conclusion") != "failure":
            continue
        created = run.get("created_at")
        updated = run.get("updated_at")
        if not created or not updated:
            continue
        try:
            start = datetime.fromisoformat(created.replace("Z", "+00:00"))
            end = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            delta = (end - start).total_seconds()
            if delta > 0:
                failure_times.append(delta)
        except (ValueError, TypeError):
            continue

    if not failure_times:
        return None
    return round(statistics.mean(failure_times), 1)


def compute_suite_stability(historical_pass_rates: list[float]) -> float:
    """Compute suite stability as the average pass rate over last N runs.

    Args:
        historical_pass_rates: List of pass rates (0–1) from recent runs,
                               ordered from oldest to newest.

    Returns:
        Average pass rate as a float (0–1). Returns 0.0 if no data.
    """
    if not historical_pass_rates:
        return 0.0
    return round(statistics.mean(historical_pass_rates), 4)


def _percentile(data: list[float], pct: int) -> float:
    """Compute the pct-th percentile of a list of floats."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (pct / 100)
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[-1]
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])
