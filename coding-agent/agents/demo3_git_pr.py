"""Demo 3 — Git & PR Automation

CAPABILITY DEMONSTRATED:
  An agent that reads existing feature files, makes a purposeful code change,
  creates a feature branch, commits with a meaningful message, dry-runs a push,
  and drafts a Pull Request description — all autonomously.

WHAT IT DOES (concrete steps):
  1. Reads the cucumber_python feature files to understand what's already tagged
  2. Identifies the most complex / highest-value scenario in inventory.feature
  3. Adds the @performance tag to that scenario (a common QA practice for
     targeting scenarios in load / performance test runs)
  4. Creates a branch: agent/add-performance-tags
  5. Commits: "test(cucumber): tag high-value inventory scenarios @performance"
  6. Dry-runs `git push` (no remote write; safe for demo)
  7. Drafts the PR title, body, and labels — prints what `gh pr create` would send

WHY THIS MATTERS FOR ECI:
  Tagging and triage work is unglamorous but critical for test suite health.
  An agent that can reason about which scenarios are "high-value" (multi-step,
  critical path, data-intensive) and apply consistent metadata — then commit
  and PR without human involvement — is a force multiplier for any QA team
  building automated triage into their CI pipeline.

NOTE ON git push / gh pr create:
  Both are run in dry-run / draft mode by default.  No remote state is modified.
  The agent prints exactly what it would push and create so you can inspect
  the intent without side effects.
"""

from shared.client import MODEL, get_client, get_repo_root
from shared.printer import divider, print_message, print_section
from tools.file_tools import list_files, read_file, write_file
from tools.git_tools import (
    git_add_and_commit,
    git_create_branch,
    git_diff,
    git_log,
    git_push,
    git_status,
)

_SYSTEM = """\
You are a QA lead automating test suite maintenance with git.

YOUR TASK:
  Add @performance tags to the most complex scenarios in the Behave feature
  files, then commit and draft a Pull Request.

CRITERIA for "most complex / highest-value" scenario:
  • More than 3 steps OR involves a multi-step user flow
  • Covers a critical business path (checkout, cart, login)
  • Not already tagged @performance

GIT WORKFLOW:
  1. Inspect the current repository state (git_status, git_log).
  2. Read the relevant feature files.
  3. Identify and tag qualifying scenarios.
  4. Write the modified files back.
  5. Create branch: agent/add-performance-tags
  6. Commit with conventional commit message format:
       test(cucumber): tag high-value scenarios @performance
  7. Dry-run push to confirm what would be sent to origin.
  8. Print the FULL PR title and body you would submit — include:
       - Summary (bullet list of what changed)
       - Motivation (why @performance tagging matters)
       - Test plan (how to verify the tags are correct)

IMPORTANT: git_push has dry_run=True by default.  Do not set dry_run=False.
"""


def run(verbose: bool = True) -> None:
    repo = get_repo_root()
    features_dir = repo / "cucumber_python" / "features"

    divider("DEMO 3 — Git & PR Automation")
    print(f"  Repository : {repo}")
    print(f"  Target dir : {features_dir}")
    divider()

    task_message = (
        f"Repository root: {repo}\n\n"
        f"Feature files are in: {features_dir}\n\n"
        f"Follow the git workflow in your system prompt exactly.\n"
        f"After the dry-run push, print the complete PR title and body "
        f"you would submit to GitHub."
    )

    client = get_client()
    tools  = [
        list_files,
        read_file,
        write_file,
        git_status,
        git_log,
        git_diff,
        git_create_branch,
        git_add_and_commit,
        git_push,
    ]

    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=8192,
        thinking={"type": "adaptive"},
        system=_SYSTEM,
        tools=tools,
        messages=[{"role": "user", "content": task_message}],
    )

    final_text = ""
    for message in runner:
        if verbose:
            print_message(message)
        for block in message.content:
            if block.type == "text":
                final_text = block.text

    print_section("DEMO 3 RESULT  (PR draft)", final_text)
