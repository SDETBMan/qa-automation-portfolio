"""
metrics.py — Data structures for scenario results and comparison reports.

ScenarioResult captures a single scenario run (either traditional or AI-driven).
ComparisonReport aggregates results from both approaches for side-by-side analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ScenarioResult:
    """Result of running a single scenario with one approach."""

    scenario: str       # "login", "inventory", "cart", "checkout"
    approach: str       # "traditional" or "ai-driven"
    passed: bool
    duration_ms: float
    tokens_used: int = 0
    error: str | None = None


@dataclass
class ComparisonReport:
    """Aggregated comparison of traditional vs AI-driven test runs."""

    scenarios: list[ScenarioResult] = field(default_factory=list)
    traditional_total_ms: float = 0.0
    ai_driven_total_ms: float = 0.0
    ai_total_tokens: int = 0
    speed_ratio: float = 0.0
    all_passed: bool = True
    generated_at: str = ""


def build_comparison_report(results: list[ScenarioResult]) -> ComparisonReport:
    """Build a ComparisonReport from a list of ScenarioResult entries."""
    traditional_ms = sum(
        r.duration_ms for r in results if r.approach == "traditional"
    )
    ai_ms = sum(
        r.duration_ms for r in results if r.approach == "ai-driven"
    )
    ai_tokens = sum(
        r.tokens_used for r in results if r.approach == "ai-driven"
    )
    all_passed = all(r.passed for r in results)

    speed_ratio = (ai_ms / traditional_ms) if traditional_ms > 0 else 0.0

    return ComparisonReport(
        scenarios=results,
        traditional_total_ms=traditional_ms,
        ai_driven_total_ms=ai_ms,
        ai_total_tokens=ai_tokens,
        speed_ratio=round(speed_ratio, 2),
        all_passed=all_passed,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
