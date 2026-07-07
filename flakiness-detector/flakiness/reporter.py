"""
reporter.py — Generate markdown flakiness report.

Produces a severity-ranked report with quarantine recommendations
for tests above the configurable threshold.
"""

from __future__ import annotations

from .analyzer import FlakinessSummary


def generate_report(summary: FlakinessSummary, threshold: float = 0.15) -> str:
    """Generate a markdown flakiness report."""
    lines: list[str] = []

    lines.append("# Flakiness Report")
    lines.append("")
    lines.append(f"**Runs analyzed:** {summary.total_runs}")
    lines.append(f"**Total tests:** {summary.total_tests}")
    lines.append(f"**Flaky tests:** {summary.total_flaky}")
    lines.append(f"**Quarantine threshold:** {threshold:.0%}")
    lines.append("")

    # Quarantine candidates
    quarantine = [t for t in summary.tests if t.flakiness_score >= threshold]
    stable_flaky = [t for t in summary.tests if 0 < t.flakiness_score < threshold]

    if quarantine:
        lines.append("## Quarantine Recommended")
        lines.append("")
        lines.append("| Test | Suite | Score | Passed | Failed | Action |")
        lines.append("|---|---|---|---|---|---|")
        for t in quarantine:
            lines.append(
                f"| `{t.test_key}` | {t.suite} | **{t.flakiness_score:.0%}** "
                f"| {t.passed} | {t.failed + t.error} | QUARANTINE |"
            )
        lines.append("")

    if stable_flaky:
        lines.append("## Monitor (Below Threshold)")
        lines.append("")
        lines.append("| Test | Suite | Score | Passed | Failed |")
        lines.append("|---|---|---|---|---|")
        for t in stable_flaky:
            lines.append(
                f"| `{t.test_key}` | {t.suite} | {t.flakiness_score:.0%} "
                f"| {t.passed} | {t.failed + t.error} |"
            )
        lines.append("")

    stable = [t for t in summary.tests if t.flakiness_score == 0]
    if stable:
        lines.append(f"## Stable Tests: {len(stable)}")
        lines.append("")
        lines.append("All other tests showed consistent pass/fail behavior across all runs.")
        lines.append("")

    return "\n".join(lines)
