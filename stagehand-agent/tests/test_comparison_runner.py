"""Tests for comparison/runner.py — mode routing and orchestration."""

from unittest.mock import MagicMock, patch

import pytest

from comparison.metrics import ScenarioResult
from comparison.runner import SCENARIO_MAP, run_comparison


def _mock_traditional_results(scenarios, base_url):
    """Return fake traditional results."""
    return [
        ScenarioResult(
            scenario=s, approach="traditional",
            passed=True, duration_ms=1000.0,
        )
        for s in scenarios
    ]


async def _mock_ai_results(scenarios, base_url):
    """Return fake AI-driven results."""
    return [
        ScenarioResult(
            scenario=s, approach="ai-driven",
            passed=True, duration_ms=3000.0, tokens_used=200,
        )
        for s in scenarios
    ]


class TestRunComparison:
    @patch("comparison.runner._run_traditional", side_effect=_mock_traditional_results)
    @patch("comparison.runner._run_ai_driven", side_effect=_mock_ai_results)
    def test_compare_mode_calls_both(self, mock_ai, mock_trad):
        report = run_comparison(mode="compare")
        mock_trad.assert_called_once()
        mock_ai.assert_called_once()
        # 4 scenarios × 2 approaches = 8 results
        assert len(report.scenarios) == 8

    @patch("comparison.runner._run_traditional", side_effect=_mock_traditional_results)
    @patch("comparison.runner._run_ai_driven", side_effect=_mock_ai_results)
    def test_traditional_mode_only(self, mock_ai, mock_trad):
        report = run_comparison(mode="traditional")
        mock_trad.assert_called_once()
        mock_ai.assert_not_called()
        assert len(report.scenarios) == 4
        assert all(r.approach == "traditional" for r in report.scenarios)

    @patch("comparison.runner._run_traditional", side_effect=_mock_traditional_results)
    @patch("comparison.runner._run_ai_driven", side_effect=_mock_ai_results)
    def test_ai_mode_only(self, mock_ai, mock_trad):
        report = run_comparison(mode="ai")
        mock_ai.assert_called_once()
        mock_trad.assert_not_called()
        assert len(report.scenarios) == 4
        assert all(r.approach == "ai-driven" for r in report.scenarios)

    @patch("comparison.runner._run_traditional", side_effect=_mock_traditional_results)
    def test_specific_scenarios(self, mock_trad):
        report = run_comparison(mode="traditional", scenarios=["login", "cart"])
        args = mock_trad.call_args[0]
        assert "login" in args[0]
        assert "cart" in args[0]
        assert len(report.scenarios) == 2

    def test_invalid_scenario_raises(self):
        with pytest.raises(ValueError, match="Unknown scenario"):
            run_comparison(mode="traditional", scenarios=["nonexistent"])


class TestScenarioMap:
    @pytest.mark.smoke
    def test_all_scenarios_mapped(self):
        expected = {"login", "inventory", "cart", "checkout"}
        assert set(SCENARIO_MAP.keys()) == expected

    def test_all_methods_exist(self):
        for method_name in SCENARIO_MAP.values():
            assert method_name.startswith("run_")
