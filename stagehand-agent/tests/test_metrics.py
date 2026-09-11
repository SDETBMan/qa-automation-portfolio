"""Tests for comparison/metrics.py — ScenarioResult and build_comparison_report()."""

import pytest

from comparison.metrics import ScenarioResult, build_comparison_report


@pytest.fixture
def sample_results():
    """A set of mixed scenario results for testing aggregation."""
    return [
        ScenarioResult(
            scenario="login", approach="traditional",
            passed=True, duration_ms=1200.0,
        ),
        ScenarioResult(
            scenario="login", approach="ai-driven",
            passed=True, duration_ms=3500.0, tokens_used=150,
        ),
        ScenarioResult(
            scenario="inventory", approach="traditional",
            passed=True, duration_ms=800.0,
        ),
        ScenarioResult(
            scenario="inventory", approach="ai-driven",
            passed=True, duration_ms=4200.0, tokens_used=220,
        ),
    ]


class TestScenarioResult:
    def test_default_tokens_zero(self):
        result = ScenarioResult(
            scenario="login", approach="traditional",
            passed=True, duration_ms=100.0,
        )
        assert result.tokens_used == 0
        assert result.error is None

    def test_failed_result(self):
        result = ScenarioResult(
            scenario="checkout", approach="ai-driven",
            passed=False, duration_ms=5000.0,
            tokens_used=300, error="Timeout waiting for confirmation",
        )
        assert result.passed is False
        assert result.error is not None


class TestBuildComparisonReport:
    @pytest.mark.smoke
    def test_aggregation(self, sample_results):
        report = build_comparison_report(sample_results)
        assert report.traditional_total_ms == 2000.0
        assert report.ai_driven_total_ms == 7700.0
        assert report.ai_total_tokens == 370
        assert report.all_passed is True
        assert len(report.scenarios) == 4

    def test_speed_ratio(self, sample_results):
        report = build_comparison_report(sample_results)
        # AI took 7700ms, traditional took 2000ms → ratio = 3.85
        assert report.speed_ratio == 3.85

    def test_all_passed_false_on_failure(self, sample_results):
        sample_results.append(
            ScenarioResult(
                scenario="checkout", approach="ai-driven",
                passed=False, duration_ms=5000.0, error="Timed out",
            )
        )
        report = build_comparison_report(sample_results)
        assert report.all_passed is False

    def test_empty_results(self):
        report = build_comparison_report([])
        assert report.traditional_total_ms == 0.0
        assert report.ai_driven_total_ms == 0.0
        assert report.speed_ratio == 0.0
        assert report.all_passed is True

    def test_generated_at_is_iso_format(self, sample_results):
        report = build_comparison_report(sample_results)
        assert "T" in report.generated_at
        assert report.generated_at.endswith("+00:00")

    def test_traditional_only(self):
        results = [
            ScenarioResult(
                scenario="login", approach="traditional",
                passed=True, duration_ms=500.0,
            ),
        ]
        report = build_comparison_report(results)
        assert report.traditional_total_ms == 500.0
        assert report.ai_driven_total_ms == 0.0
        assert report.speed_ratio == 0.0

    def test_ai_only(self):
        results = [
            ScenarioResult(
                scenario="login", approach="ai-driven",
                passed=True, duration_ms=3000.0, tokens_used=100,
            ),
        ]
        report = build_comparison_report(results)
        assert report.ai_driven_total_ms == 3000.0
        assert report.traditional_total_ms == 0.0
        assert report.speed_ratio == 0.0
