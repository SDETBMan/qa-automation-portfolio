"""
github_api.py — Fetch branch and diff data from GitHub via gh CLI.

Uses subprocess to call `gh` commands, avoiding the need for
PyGithub dependency and leveraging existing `gh` authentication.
"""

from __future__ import annotations

import json
import re
import subprocess

from .analyzer import BranchInfo


def _run_gh(args: list[str], timeout: int = 30) -> str:
    """Run a gh CLI command and return stdout."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
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


def detect_base_branch(repo: str) -> str:
    """Detect the default branch of a repository."""
    raw = _run_gh([
        "api", f"/repos/{repo}",
        "--jq", ".default_branch",
        "-q",
    ])
    branch = raw.strip()
    return branch if branch and branch != "[]" else "main"


def fetch_active_branches(repo: str, limit: int = 30) -> list[dict]:
    """Fetch recently-pushed branches from a repository.

    Returns a list of dicts with keys: name, author, last_commit_date.
    """
    raw = _run_gh([
        "api", f"/repos/{repo}/branches",
        "--paginate",
        "--jq", ".[].name",
        "-q",
    ])

    if not raw.strip() or raw.strip() == "[]":
        return []

    branch_names = [b.strip() for b in raw.strip().splitlines() if b.strip()]

    # Limit to the requested count
    branch_names = branch_names[:limit]

    branches = []
    for name in branch_names:
        branches.append({
            "name": name,
            "author": "",
            "last_commit_date": "",
        })

    return branches


def fetch_branch_diff(repo: str, base: str, branch: str) -> str:
    """Fetch the unified diff between base and branch."""
    raw = _run_gh([
        "api", f"/repos/{repo}/compare/{base}...{branch}",
        "--jq", ".files",
        "-q",
    ], timeout=60)

    return raw


def fetch_branch_files(repo: str, base: str, branch: str) -> BranchInfo:
    """Fetch file-level change info for a branch compared to base.

    Returns a BranchInfo with files_changed, lines_added, lines_removed.
    """
    raw = fetch_branch_diff(repo, base, branch)

    files_changed: list[str] = []
    lines_added = 0
    lines_removed = 0

    try:
        files = json.loads(raw)
        if not isinstance(files, list):
            return BranchInfo(name=branch)

        for file_info in files:
            filename = file_info.get("filename", "")
            if filename:
                files_changed.append(filename)
            lines_added += file_info.get("additions", 0)
            lines_removed += file_info.get("deletions", 0)

    except json.JSONDecodeError:
        print(f"[WARN] Failed to parse diff for branch {branch}")

    return BranchInfo(
        name=branch,
        files_changed=files_changed,
        lines_added=lines_added,
        lines_removed=lines_removed,
    )


def parse_diff_stats(diff_text: str) -> tuple[list[str], int, int]:
    """Parse a unified diff to extract filenames and line counts.

    Useful for parsing pre-fetched diffs (e.g., from fixtures).

    Returns:
        (files, lines_added, lines_removed)
    """
    files: list[str] = []
    lines_added = 0
    lines_removed = 0

    for line in diff_text.splitlines():
        # Detect file headers: diff --git a/path b/path
        if line.startswith("diff --git"):
            match = re.search(r"b/(.+)$", line)
            if match:
                files.append(match.group(1))
        elif line.startswith("+") and not line.startswith("+++"):
            lines_added += 1
        elif line.startswith("-") and not line.startswith("---"):
            lines_removed += 1

    return files, lines_added, lines_removed
