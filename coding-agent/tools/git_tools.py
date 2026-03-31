"""Git operation tools — status, diff, branch, commit, push.

Each tool wraps a git subprocess call and returns structured output so Claude
can reason about the repository state before acting.
"""

import subprocess
from pathlib import Path

from anthropic import beta_tool


def _git(args: list[str], cwd: str) -> str:
    """Run a git command and return stdout + stderr."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    output = (result.stdout + result.stderr).strip()
    return output or "(no output)"


@beta_tool
def git_status(repo_path: str) -> str:
    """Show the working tree status of a git repository.

    Args:
        repo_path: Absolute path to the git repository root.
    """
    return _git(["status", "--short"], repo_path)


@beta_tool
def git_diff(repo_path: str, staged: bool = False) -> str:
    """Show changes in the working tree or staging area.

    Args:
        repo_path: Absolute path to the git repository root.
        staged: If true, show staged (--cached) changes; otherwise unstaged.
    """
    args = ["diff", "--stat"]
    if staged:
        args.append("--cached")
    return _git(args, repo_path)


@beta_tool
def git_create_branch(repo_path: str, branch_name: str) -> str:
    """Create and check out a new git branch.

    Args:
        repo_path: Absolute path to the git repository root.
        branch_name: Name for the new branch (e.g. feature/add-smoke-tags).
    """
    return _git(["checkout", "-b", branch_name], repo_path)


@beta_tool
def git_add_and_commit(repo_path: str, message: str, paths: str = ".") -> str:
    """Stage files and create a commit.

    Args:
        repo_path: Absolute path to the git repository root.
        message: Commit message (should follow conventional commits style).
        paths: Space-separated file paths to stage.  Defaults to '.' (all changes).
    """
    # Stage
    stage_result = _git(["add"] + paths.split(), repo_path)
    # Commit
    commit_result = _git(["commit", "-m", message], repo_path)
    return f"[STAGE]\n{stage_result}\n\n[COMMIT]\n{commit_result}"


@beta_tool
def git_push(repo_path: str, branch: str, dry_run: bool = True) -> str:
    """Push a branch to the origin remote.

    Args:
        repo_path: Absolute path to the git repository root.
        branch: Branch name to push.
        dry_run: If true (default), simulate the push without sending data.
                 Set to false only when you intend to publish the branch.
    """
    args = ["push", "-u", "origin", branch]
    if dry_run:
        args.append("--dry-run")
    result = _git(args, repo_path)
    prefix = "[DRY RUN] " if dry_run else ""
    return f"{prefix}{result}"


@beta_tool
def git_log(repo_path: str, count: int = 5) -> str:
    """Show recent commit history.

    Args:
        repo_path: Absolute path to the git repository root.
        count: Number of recent commits to show (default 5).
    """
    return _git(["log", f"-{count}", "--oneline", "--decorate"], repo_path)
