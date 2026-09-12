"""
run.py — Branch Collision Monitor CLI entry point.

Usage:
    python run.py --repo SDETBMan/qa-automation-portfolio
    python run.py --repo SDETBMan/qa-automation-portfolio --format both --output report
    python run.py --repo SDETBMan/qa-automation-portfolio --semantic --max-semantic 5
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from monitor.github_api import (
    detect_base_branch,
    fetch_active_branches,
    fetch_branch_diff,
    fetch_branch_files,
)
from monitor.analyzer import BranchInfo, analyze
from monitor.reporter import generate_json_report, generate_markdown_report
from monitor.datadog import send_collision_metrics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect branch collisions — file-level and semantic overlaps between active branches",
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="GitHub repository (owner/repo)",
    )
    parser.add_argument(
        "--base",
        default=None,
        help="Base branch to compare against (default: auto-detect)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Maximum number of branches to analyze (default: 20)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown", "both"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write report to file (default: stdout). For 'both', writes .json and .md",
    )
    parser.add_argument(
        "--semantic",
        action="store_true",
        help="Enable Claude-powered semantic conflict analysis (requires ANTHROPIC_API_KEY)",
    )
    parser.add_argument(
        "--max-semantic",
        type=int,
        default=10,
        help="Maximum semantic analysis API calls (default: 10)",
    )
    args = parser.parse_args()

    # Detect base branch
    base = args.base or detect_base_branch(args.repo)
    print(f"[INFO] Repository: {args.repo}")
    print(f"[INFO] Base branch: {base}")
    print(f"[INFO] Fetching active branches (limit: {args.limit})...")

    # Fetch branches
    raw_branches = fetch_active_branches(args.repo, limit=args.limit)
    if not raw_branches:
        print("[WARN] No branches found.", file=sys.stderr)
        sys.exit(1)

    # Filter out base branch
    raw_branches = [b for b in raw_branches if b["name"] != base]
    print(f"[INFO] Found {len(raw_branches)} branches to analyze.")

    # Fetch file-level changes for each branch
    branches: list[BranchInfo] = []
    for i, b in enumerate(raw_branches):
        name = b["name"]
        print(f"[INFO] Fetching diff {i + 1}/{len(raw_branches)}: {name}")
        info = fetch_branch_files(args.repo, base, name)
        if info.files_changed:
            branches.append(info)

    if not branches:
        print("[INFO] No branches with file changes detected.")
        sys.exit(0)

    print(f"[INFO] {len(branches)} branches have file changes. Analyzing...")

    # Run structural analysis
    report = analyze(branches, repo=args.repo, base_branch=base)

    # Run semantic analysis if requested
    if args.semantic and report.overlapping_files:
        from monitor.semantic import run_semantic_analysis

        # Build pairs for semantic analysis
        # For each overlapping file, pair the first two branches
        pairs: list[dict] = []
        for overlap in report.overlapping_files:
            if len(overlap.branches) >= 2:
                # Fetch raw diffs for the pair
                diff_a = fetch_branch_diff(args.repo, base, overlap.branches[0])
                diff_b = fetch_branch_diff(args.repo, base, overlap.branches[1])
                pairs.append({
                    "file_path": overlap.path,
                    "branch_a": overlap.branches[0],
                    "diff_a": diff_a,
                    "branch_b": overlap.branches[1],
                    "diff_b": diff_b,
                })

        if pairs:
            semantic_results = run_semantic_analysis(pairs, max_calls=args.max_semantic)
            report.semantic_overlaps = semantic_results

    # Generate output
    if args.format in ("json", "both"):
        json_output = generate_json_report(report)
        if args.output:
            json_path = args.output.with_suffix(".json")
            json_path.write_text(json_output, encoding="utf-8")
            print(f"[INFO] JSON report written to {json_path}")
        elif args.format == "json":
            print(json_output)

    if args.format in ("markdown", "both"):
        md_output = generate_markdown_report(report)
        if args.output:
            md_path = args.output.with_suffix(".md")
            md_path.write_text(md_output, encoding="utf-8")
            print(f"[INFO] Markdown report written to {md_path}")
        elif args.format == "markdown":
            print(md_output)

    # Summary
    print(f"\n[RESULT] Risk: {report.overall_risk} (score: {report.overall_score:.4f})")
    print(f"[RESULT] Overlapping files: {len(report.overlapping_files)}")
    if report.semantic_overlaps:
        high_conflicts = sum(
            1 for s in report.semantic_overlaps
            if s.conflict_likelihood in ("high", "medium")
        )
        print(f"[RESULT] Semantic conflicts (high/medium): {high_conflicts}")

    # Send DataDog metrics
    semantic_conflicts = sum(
        1 for s in report.semantic_overlaps
        if s.conflict_likelihood in ("high", "medium")
    )
    send_collision_metrics(
        overall_risk=report.overall_risk,
        overall_score=report.overall_score,
        branches_analyzed=report.branches_analyzed,
        overlapping_file_count=len(report.overlapping_files),
        semantic_conflicts=semantic_conflicts,
    )


if __name__ == "__main__":
    main()
