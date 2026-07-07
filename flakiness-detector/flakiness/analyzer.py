"""
analyzer.py — Aggregate test outcomes and compute flakiness scores.

Flakiness score = number of runs where the test's outcome differs
from its majority outcome, divided by total runs.

A test is "flaky" if it has both passes and failures across runs.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .parser import RunResults


@dataclass
class TestFlakiness:
    """Flakiness analysis for a single test."""
    test_key: str  # classname::name
    suite: str
    total_runs: int
    passed: int
    failed: int
    skipped: int
    error: int
    flakiness_score: float  # 0.0 = stable, 1.0 = always different


@dataclass
class FlakinessSummary:
    """Aggregated flakiness analysis across all runs."""
    tests: list[TestFlakiness] = field(default_factory=list)
    total_tests: int = 0
    total_flaky: int = 0
    total_runs: int = 0


def analyze(runs: list[RunResults], threshold: float = 0.15) -> FlakinessSummary:
    """
    Analyze test results across runs to compute flakiness scores.

    A test is flaky if it has both passed and failed/errored outcomes
    across different runs. The flakiness score is:
        min(pass_count, fail_count) / total_runs

    This means a test that always passes or always fails scores 0.0.
    """
    # Aggregate outcomes per test key
    outcomes: dict[str, dict[str, int]] = {}
    suites: dict[str, str] = {}

    for run in runs:
        for result in run.results:
            key = f"{result.classname}::{result.name}"
            if key not in outcomes:
                outcomes[key] = {"passed": 0, "failed": 0, "skipped": 0, "error": 0}
                suites[key] = result.suite

            outcomes[key][result.status] = outcomes[key].get(result.status, 0) + 1

    total_runs = len(runs)
    tests: list[TestFlakiness] = []

    for key, counts in outcomes.items():
        passed = counts.get("passed", 0)
        failed = counts.get("failed", 0) + counts.get("error", 0)
        skipped = counts.get("skipped", 0)
        total = passed + failed + skipped

        # Flakiness = min(pass_count, fail_count) / total non-skipped runs
        non_skipped = passed + failed
        if non_skipped > 0:
            score = min(passed, failed) / non_skipped
        else:
            score = 0.0

        tests.append(TestFlakiness(
            test_key=key,
            suite=suites[key],
            total_runs=total,
            passed=passed,
            failed=failed - counts.get("error", 0),
            skipped=skipped,
            error=counts.get("error", 0),
            flakiness_score=round(score, 4),
        ))

    # Sort by flakiness score descending
    tests.sort(key=lambda t: t.flakiness_score, reverse=True)

    total_flaky = sum(1 for t in tests if t.flakiness_score > 0)

    return FlakinessSummary(
        tests=tests,
        total_tests=len(tests),
        total_flaky=total_flaky,
        total_runs=total_runs,
    )
