"""reporter.py — Generate markdown report + optional GitHub issue."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone

from .comparator import DriftReport


def generate_markdown(report: DriftReport, affected: list[dict]) -> str:
    """Render a markdown drift report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []

    lines.append("# Site Drift Report")
    lines.append(f"\n**Generated:** {now}")
    lines.append(f"**Target:** saucedemo.com")

    # Summary
    lines.append("\n## Summary\n")
    if not report.has_drift:
        lines.append("No drift detected. All monitored selectors are stable.")
        return "\n".join(lines)

    lines.append(f"- **Drift detected:** Yes")
    lines.append(f"- **Severity:** {report.severity}")
    lines.append(f"- **Selectors removed:** {report.total_removed}")
    lines.append(f"- **Selectors added:** {report.total_added}")

    # Removed selectors (critical)
    if report.total_removed > 0:
        lines.append("\n## Removed Selectors\n")
        lines.append("| Selector | Type | Affected Frameworks |")
        lines.append("|----------|------|---------------------|")

        affected_map = {item["selector"]: item for item in affected}

        for selector in report.removed_ids:
            item = affected_map.get(selector, {})
            frameworks = ", ".join(item.get("frameworks", ["unknown"]))
            lines.append(f"| `{selector}` | id | {frameworks} |")

        for selector in report.removed_classes:
            item = affected_map.get(selector, {})
            frameworks = ", ".join(item.get("frameworks", ["unknown"]))
            lines.append(f"| `{selector}` | class | {frameworks} |")

        for selector in report.removed_data_test:
            item = affected_map.get(selector, {})
            frameworks = ", ".join(item.get("frameworks", ["unknown"]))
            lines.append(f"| `{selector}` | data-test | {frameworks} |")

    # Added selectors (info)
    if report.total_added > 0:
        lines.append("\n## Added Selectors\n")
        all_added = (
            [(s, "id") for s in report.added_ids]
            + [(s, "class") for s in report.added_classes]
            + [(s, "data-test") for s in report.added_data_test]
        )
        for selector, sel_type in all_added:
            lines.append(f"- `{selector}` ({sel_type})")

    # Recommendation
    if affected:
        lines.append("\n## Recommendation\n")
        framework_set: set[str] = set()
        for item in affected:
            framework_set.update(item["frameworks"])
        frameworks_str = ", ".join(sorted(framework_set))
        lines.append(
            f"Investigate test suites for: **{frameworks_str}**. "
            "Removed selectors may cause test failures."
        )

    return "\n".join(lines)


def create_github_issue(title: str, body: str) -> None:
    """Create a GitHub issue via gh CLI."""
    try:
        subprocess.run(
            [
                "gh", "issue", "create",
                "--title", title,
                "--body", body,
                "--label", "site-drift",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        print("[INFO] GitHub issue created successfully.")
    except FileNotFoundError:
        print("[WARN] gh CLI not found. Skipping GitHub issue creation.")
    except subprocess.CalledProcessError as exc:
        print(f"[WARN] Failed to create GitHub issue: {exc.stderr}")
