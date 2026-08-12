"""
reporter.py — Generate a markdown dependency audit report.

Output format:
  | Framework | File | Package | Current | Latest | Status |
  |-----------|------|---------|---------|--------|--------|
  | playwright | package.json | @playwright/test | 1.44.0 | 1.52.0 | outdated |
"""

from __future__ import annotations

from pathlib import Path

from auditor.checkers import DependencyInfo
from auditor.scanner import ManifestInfo


def generate_report(
    results: list[tuple[ManifestInfo, list[DependencyInfo]]],
    repo_dir: Path,
) -> str:
    """Generate a markdown table from audit results."""
    lines: list[str] = [
        "# Dependency Audit Report",
        "",
        f"Repository: `{repo_dir}`",
        "",
    ]

    # Summary
    total = sum(len(deps) for _, deps in results)
    outdated = sum(
        1 for _, deps in results for d in deps if d.status == "outdated"
    )
    up_to_date = sum(
        1 for _, deps in results for d in deps if d.status == "up-to-date"
    )
    unknown = sum(
        1 for _, deps in results for d in deps if d.status == "unknown"
    )

    lines.extend([
        f"**Total packages:** {total}  ",
        f"**Up-to-date:** {up_to_date}  ",
        f"**Outdated:** {outdated}  ",
        f"**Unknown:** {unknown}  ",
        "",
    ])

    # Outdated table
    if outdated:
        lines.extend([
            "## Outdated Dependencies",
            "",
            "| Framework | File | Package | Current | Latest | Status |",
            "|-----------|------|---------|---------|--------|--------|",
        ])
        for manifest, deps in results:
            for dep in deps:
                if dep.status != "outdated":
                    continue
                rel_path = manifest.path.relative_to(repo_dir)
                lines.append(
                    f"| {manifest.framework} | {rel_path.name} "
                    f"| {dep.package} | {dep.current} "
                    f"| {dep.latest} | {dep.status} |"
                )
        lines.append("")

    # Full table
    lines.extend([
        "## All Dependencies",
        "",
        "| Framework | File | Package | Current | Latest | Status |",
        "|-----------|------|---------|---------|--------|--------|",
    ])
    for manifest, deps in results:
        for dep in deps:
            rel_path = manifest.path.relative_to(repo_dir)
            lines.append(
                f"| {manifest.framework} | {rel_path.name} "
                f"| {dep.package} | {dep.current} "
                f"| {dep.latest or 'N/A'} | {dep.status} |"
            )
    lines.append("")

    return "\n".join(lines)
