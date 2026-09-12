"""
runner.py — Orchestrator that runs traditional, AI-driven, or both approaches.

Based on mode, instantiates PlaywrightRunner, StagehandRunner, or both,
collects ScenarioResult entries, and builds a ComparisonReport.
"""

from __future__ import annotations

import asyncio
import os

from playwright.sync_api import sync_playwright
from stagehand import Stagehand

from comparison.metrics import ComparisonReport, ScenarioResult, build_comparison_report
from traditional.playwright_runner import PlaywrightRunner
from agent.stagehand_runner import StagehandRunner


SCENARIO_MAP = {
    "login": "run_login",
    "inventory": "run_inventory",
    "cart": "run_cart",
    "checkout": "run_checkout",
}


def _run_traditional(
    scenarios: list[str],
    base_url: str,
) -> list[ScenarioResult]:
    """Run traditional Playwright scenarios."""
    results: list[ScenarioResult] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for scenario in scenarios:
            page = browser.new_page()
            runner = PlaywrightRunner(page, base_url=base_url)
            method_name = SCENARIO_MAP[scenario]
            try:
                result = getattr(runner, method_name)()
                results.append(result)
            except Exception as exc:
                results.append(ScenarioResult(
                    scenario=scenario,
                    approach="traditional",
                    passed=False,
                    duration_ms=0.0,
                    error=str(exc),
                ))
            finally:
                page.close()
        browser.close()
    return results


async def _run_ai_driven(
    scenarios: list[str],
    base_url: str,
) -> list[ScenarioResult]:
    """Run AI-driven Stagehand scenarios."""
    results: list[ScenarioResult] = []
    client = Stagehand(
        api_key=os.getenv("BROWSERBASE_API_KEY", ""),
        project_id=os.getenv("BROWSERBASE_PROJECT_ID", ""),
    )
    runner = StagehandRunner(client, base_url=base_url)

    for scenario in scenarios:
        method_name = SCENARIO_MAP[scenario]
        try:
            result = await getattr(runner, method_name)()
            results.append(result)
        except Exception as exc:
            results.append(ScenarioResult(
                scenario=scenario,
                approach="ai-driven",
                passed=False,
                duration_ms=0.0,
                error=str(exc),
            ))

    return results


def run_comparison(
    mode: str = "compare",
    scenarios: list[str] | None = None,
    base_url: str = "https://www.saucedemo.com",
) -> ComparisonReport:
    """Run the comparison based on mode and return a ComparisonReport.

    Args:
        mode: "traditional", "ai", or "compare" (both).
        scenarios: List of scenario names to run. Defaults to all.
        base_url: Target application URL.

    Returns:
        ComparisonReport with aggregated results.
    """
    if scenarios is None:
        scenarios = list(SCENARIO_MAP.keys())

    # Validate scenario names
    for s in scenarios:
        if s not in SCENARIO_MAP:
            raise ValueError(f"Unknown scenario: {s}. Must be one of {list(SCENARIO_MAP.keys())}")

    all_results: list[ScenarioResult] = []

    if mode in ("traditional", "compare"):
        print(f"[INFO] Running traditional Playwright scenarios: {scenarios}")
        traditional_results = _run_traditional(scenarios, base_url)
        all_results.extend(traditional_results)
        for r in traditional_results:
            status = "PASS" if r.passed else "FAIL"
            print(f"  [{status}] {r.scenario} — {r.duration_ms:.1f}ms")

    if mode in ("ai", "compare"):
        print(f"[INFO] Running AI-driven Stagehand scenarios: {scenarios}")
        ai_results = asyncio.run(_run_ai_driven(scenarios, base_url))
        all_results.extend(ai_results)
        for r in ai_results:
            status = "PASS" if r.passed else "FAIL"
            print(f"  [{status}] {r.scenario} — {r.duration_ms:.1f}ms ({r.tokens_used} tokens)")

    return build_comparison_report(all_results)
