#!/usr/bin/env python3
"""
run.py — CLI entry point for the dependency audit tool.

Usage:
  python run.py --repo-dir ..              # audit all frameworks
  python run.py --repo-dir .. --update     # audit + auto-update
  python run.py --repo-dir .. --ecosystem npm   # npm only
  python run.py --repo-dir .. --output report.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import click

from auditor.scanner import scan_repo
from auditor.checkers import check_manifest
from auditor.updater import update_manifest
from auditor.reporter import generate_report


@click.command()
@click.option(
    "--repo-dir",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    required=True,
    help="Path to the monorepo root.",
)
@click.option(
    "--ecosystem",
    type=click.Choice(["npm", "pip", "nuget", "maven", "go"], case_sensitive=False),
    default=None,
    help="Filter to a single ecosystem (default: all).",
)
@click.option(
    "--update",
    is_flag=True,
    default=False,
    help="Auto-update outdated dependencies in manifests.",
)
@click.option(
    "--output",
    type=click.Path(dir_okay=False),
    default=None,
    help="Write report to a file (default: stdout).",
)
def main(
    repo_dir: str,
    ecosystem: str | None,
    update: bool,
    output: str | None,
) -> None:
    """Scan the monorepo for outdated dependencies."""
    repo_path = Path(repo_dir)
    click.echo(f"Scanning {repo_path} ...")

    # 1. Discover manifests
    manifests = scan_repo(repo_path)
    if ecosystem:
        manifests = [m for m in manifests if m.ecosystem == ecosystem.lower()]

    click.echo(f"Found {len(manifests)} manifest(s).")

    # 2. Check each manifest
    results: list[tuple] = []
    for manifest in manifests:
        click.echo(f"  Checking {manifest.framework}/{manifest.path.name} ({manifest.ecosystem}) ...")
        deps = check_manifest(manifest.ecosystem, manifest.path)
        results.append((manifest, deps))

        outdated_count = sum(1 for d in deps if d.status == "outdated")
        if outdated_count:
            click.echo(f"    → {outdated_count} outdated")

    # 3. Optionally update
    if update:
        total_updates = 0
        for manifest, deps in results:
            count = update_manifest(manifest.ecosystem, manifest.path, deps)
            if count:
                click.echo(f"  Updated {count} package(s) in {manifest.path.name}")
                total_updates += count
        click.echo(f"\nTotal updates: {total_updates}")

    # 4. Generate report
    report = generate_report(results, repo_path)

    if output:
        out_path = Path(output)
        out_path.write_text(report)
        click.echo(f"\nReport written to {out_path}")
    else:
        click.echo("\n" + report)


if __name__ == "__main__":
    main()
