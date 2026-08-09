"""QMS Evidence Collector — map CI artifacts to compliance clauses."""

from __future__ import annotations

from pathlib import Path

import click

from collector.scanner import scan_repo, load_registry
from collector.mapper import map_to_clauses
from collector.reporter import generate_markdown, generate_json, write_report
from collector.datadog import send_evidence_metrics


@click.command()
@click.option(
    "--repo-dir",
    default=str(Path(__file__).parent.parent),
    help="Root of the monorepo to scan (default: parent of this framework)",
)
@click.option(
    "--output",
    default=None,
    help="Write report to file (auto-detects .json or .md)",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["markdown", "json"]),
    default="markdown",
    help="Output format (default: markdown)",
)
@click.option(
    "--standard",
    type=click.Choice(["all", "iso9001", "soc2", "iso17025"]),
    default="all",
    help="Filter to a specific standard (default: all)",
)
def main(repo_dir: str, output: str | None, fmt: str, standard: str) -> None:
    """Scan the monorepo for CI artifacts and map them to compliance clauses.

    Maps test results, security scans, coverage reports, and other CI artifacts
    to ISO 9001:2015, SOC 2 CC-series, and ISO/IEC 17025:2017 clause references
    for audit evidence collection.
    """
    root = Path(repo_dir).resolve()
    print(f"[INFO] Scanning {root}...")

    # Load registry and scan
    registry = load_registry()
    scan_result = scan_repo(root, registry)

    print(
        f"[INFO] Scanned {len(scan_result.frameworks_scanned)} frameworks, "
        f"found {len(scan_result.hits)} artifact files across "
        f"{len(scan_result.artifact_types_found)} artifact types"
    )

    # Map to clauses
    compliance_map = map_to_clauses(scan_result, registry)

    # Filter by standard if requested
    if standard != "all":
        filter_map = {
            "iso9001": "ISO 9001:2015",
            "soc2": "SOC 2",
            "iso17025": "ISO/IEC 17025:2017",
        }
        target = filter_map[standard]
        compliance_map.evidence = [
            e for e in compliance_map.evidence if e.standard == target
        ]

    print(
        f"[INFO] Mapped to {compliance_map.unique_clause_count} unique clauses, "
        f"{compliance_map.total_evidence_files} evidence files"
    )

    # Auto-detect format from output extension
    if output and output.endswith(".json"):
        fmt = "json"

    # Output
    if output:
        write_report(compliance_map, output, fmt)
        print(f"[INFO] Report written to {output}")
    else:
        if fmt == "json":
            import json
            print(json.dumps(generate_json(compliance_map), indent=2))
        else:
            print("\n" + generate_markdown(compliance_map))

    # Send DataDog metrics
    send_evidence_metrics(compliance_map)


if __name__ == "__main__":
    main()
