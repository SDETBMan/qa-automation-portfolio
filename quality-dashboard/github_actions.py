"""
github_actions.py — Fetch workflow run history from GitHub Actions for MTTD.

Uses subprocess to call `gh api` (same pattern as vulnerability-aggregator).
Fetches recent workflow runs per framework, extracts commit and conclusion
timestamps, and computes Mean Time to Detect (MTTD).

Graceful skip if `gh` is not authenticated or not installed.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime


def _run_gh(args: list[str]) -> str:
    """Run a gh CLI command and return stdout."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            print(f"[WARN] gh command failed: {result.stderr.strip()}")
            return "[]"
        return result.stdout
    except FileNotFoundError:
        print("[WARN] gh CLI not found. Install from https://cli.github.com/")
        return "[]"
    except subprocess.TimeoutExpired:
        print("[WARN] gh command timed out")
        return "[]"


def fetch_workflow_runs(
    repo: str,
    workflow: str,
    limit: int = 20,
) -> list[dict]:
    """Fetch recent workflow runs for a specific workflow.

    Args:
        repo: GitHub repository in owner/repo format.
        workflow: Workflow filename (e.g. 'selenium-java.yml').
        limit: Maximum number of runs to fetch (default 20).

    Returns:
        List of workflow run dicts with keys: id, created_at, updated_at,
        conclusion, head_sha, status, name.
    """
    raw = _run_gh([
        "api",
        f"/repos/{repo}/actions/workflows/{workflow}/runs",
        "--jq", f".workflow_runs[:{ limit}] | [.[] | {{id, created_at, updated_at, conclusion, head_sha, status, name}}]",
        "-q",
    ])

    try:
        runs = json.loads(raw)
        if isinstance(runs, list):
            return runs
    except json.JSONDecodeError:
        print(f"[WARN] Failed to parse workflow runs for {workflow}")

    return []


def compute_mttd_from_runs(runs: list[dict]) -> float | None:
    """Compute Mean Time to Detect from workflow runs.

    MTTD = average seconds from workflow creation (≈ push time) to
    workflow conclusion for failed runs.

    Args:
        runs: List of workflow run dicts from fetch_workflow_runs().

    Returns:
        Average MTTD in seconds, or None if no failed runs.
    """
    failure_durations: list[float] = []

    for run in runs:
        if run.get("conclusion") != "failure":
            continue
        created = run.get("created_at")
        updated = run.get("updated_at")
        if not created or not updated:
            continue
        try:
            start = datetime.fromisoformat(created.replace("Z", "+00:00"))
            end = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            delta = (end - start).total_seconds()
            if delta > 0:
                failure_durations.append(delta)
        except (ValueError, TypeError):
            continue

    if not failure_durations:
        return None

    import statistics
    return round(statistics.mean(failure_durations), 1)


def compute_mttr_from_runs(runs: list[dict]) -> float | None:
    """Compute Mean Time to Recovery from workflow runs.

    MTTR = average seconds from a failed run's creation to the next
    successful run's completion.  For each failed run, the first
    chronologically subsequent run with conclusion=="success" is used.

    Args:
        runs: List of workflow run dicts from fetch_workflow_runs(),
              ordered newest-first (GitHub API default).

    Returns:
        Average MTTR in seconds, or None if no recovery pairs found.
    """
    # Sort oldest-first so we can scan forward for recovery
    sorted_runs = sorted(
        [r for r in runs if r.get("created_at")],
        key=lambda r: r["created_at"],
    )

    recovery_durations: list[float] = []

    for i, run in enumerate(sorted_runs):
        if run.get("conclusion") != "failure":
            continue
        failure_created = run.get("created_at")
        if not failure_created:
            continue

        # Find the next successful run after this failure
        for j in range(i + 1, len(sorted_runs)):
            if sorted_runs[j].get("conclusion") == "success":
                recovery_updated = sorted_runs[j].get("updated_at")
                if not recovery_updated:
                    break
                try:
                    start = datetime.fromisoformat(
                        failure_created.replace("Z", "+00:00")
                    )
                    end = datetime.fromisoformat(
                        recovery_updated.replace("Z", "+00:00")
                    )
                    delta = (end - start).total_seconds()
                    if delta > 0:
                        recovery_durations.append(delta)
                except (ValueError, TypeError):
                    pass
                break

    if not recovery_durations:
        return None

    import statistics
    return round(statistics.mean(recovery_durations), 1)


def fetch_historical_pass_rates(
    repo: str,
    workflow: str,
    limit: int = 20,
) -> list[float]:
    """Compute historical pass rates from recent workflow runs.

    Args:
        repo: GitHub repository in owner/repo format.
        workflow: Workflow filename.
        limit: Number of recent runs to consider.

    Returns:
        List of pass rates (1.0 for success, 0.0 for failure) ordered
        oldest to newest.
    """
    runs = fetch_workflow_runs(repo, workflow, limit)
    rates: list[float] = []
    for run in reversed(runs):  # oldest first
        conclusion = run.get("conclusion")
        if conclusion == "success":
            rates.append(1.0)
        elif conclusion == "failure":
            rates.append(0.0)
        # skip in_progress, cancelled, etc.
    return rates
