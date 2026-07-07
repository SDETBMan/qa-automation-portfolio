"""Tests for flakiness analyzer."""

from flakiness.parser import RunResults, TestResult
from flakiness.analyzer import analyze


def _make_runs() -> list[RunResults]:
    """Create test runs simulating flaky behavior."""
    return [
        RunResults(run_id="run-1", results=[
            TestResult(suite="s", name="stable_pass", classname="c", time_s=1, status="passed"),
            TestResult(suite="s", name="stable_fail", classname="c", time_s=1, status="failed"),
            TestResult(suite="s", name="flaky_test", classname="c", time_s=1, status="passed"),
        ]),
        RunResults(run_id="run-2", results=[
            TestResult(suite="s", name="stable_pass", classname="c", time_s=1, status="passed"),
            TestResult(suite="s", name="stable_fail", classname="c", time_s=1, status="failed"),
            TestResult(suite="s", name="flaky_test", classname="c", time_s=1, status="failed"),
        ]),
    ]


def test_stable_pass_has_zero_score():
    summary = analyze(_make_runs())
    stable = next(t for t in summary.tests if "stable_pass" in t.test_key)
    assert stable.flakiness_score == 0.0


def test_stable_fail_has_zero_score():
    summary = analyze(_make_runs())
    stable = next(t for t in summary.tests if "stable_fail" in t.test_key)
    assert stable.flakiness_score == 0.0


def test_flaky_test_has_nonzero_score():
    summary = analyze(_make_runs())
    flaky = next(t for t in summary.tests if "flaky_test" in t.test_key)
    assert flaky.flakiness_score > 0


def test_flaky_test_score_is_half():
    summary = analyze(_make_runs())
    flaky = next(t for t in summary.tests if "flaky_test" in t.test_key)
    # 1 pass, 1 fail → min(1,1)/2 = 0.5
    assert flaky.flakiness_score == 0.5


def test_total_flaky_count():
    summary = analyze(_make_runs())
    assert summary.total_flaky == 1


def test_sorted_by_score_descending():
    summary = analyze(_make_runs())
    scores = [t.flakiness_score for t in summary.tests]
    assert scores == sorted(scores, reverse=True)
