"""GitHub CLI tools — create PRs, read and respond to review comments.

Requires `gh` (GitHub CLI) to be installed and authenticated.
https://cli.github.com/
"""

import subprocess

from anthropic import beta_tool


def _gh(args: list[str], cwd: str) -> str:
    """Run a gh command and return stdout + stderr."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    output = (result.stdout + result.stderr).strip()
    return output or "(no output)"


@beta_tool
def gh_create_pr(
    repo_path: str,
    title: str,
    body: str,
    base: str = "main",
    draft: bool = True,
) -> str:
    """Create a GitHub Pull Request using the gh CLI.

    Args:
        repo_path: Absolute path to the git repository root.
        title: PR title (keep under 72 characters).
        body: PR description in markdown.  Include Summary and Test Plan sections.
        base: Target branch to merge into (default: main).
        draft: If true (default), open as a draft PR — safe for automation.
    """
    args = ["pr", "create", "--title", title, "--body", body, "--base", base]
    if draft:
        args.append("--draft")
    return _gh(args, repo_path)


@beta_tool
def gh_list_pr_comments(repo_path: str, pr_number: str) -> str:
    """Fetch all review comments on a Pull Request.

    Args:
        repo_path: Absolute path to the git repository root.
        pr_number: The PR number as a string (e.g. '42').
    """
    return _gh(["pr", "view", pr_number, "--comments"], repo_path)


@beta_tool
def gh_reply_to_pr(repo_path: str, pr_number: str, body: str) -> str:
    """Post a top-level comment on a Pull Request (e.g. to address review feedback).

    Args:
        repo_path: Absolute path to the git repository root.
        pr_number: The PR number as a string.
        body: The comment text in markdown.
    """
    return _gh(["pr", "comment", pr_number, "--body", body], repo_path)


@beta_tool
def gh_pr_status(repo_path: str) -> str:
    """Show the status of the current branch's open PR (checks, reviews, etc.).

    Args:
        repo_path: Absolute path to the git repository root.
    """
    return _gh(["pr", "status"], repo_path)
