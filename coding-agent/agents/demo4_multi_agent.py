"""Demo 4 — Multi-Agent System: Planner → Executor → Validator

CAPABILITY DEMONSTRATED:
  Three specialised agents collaborating through clean context handoff.
  Each agent has a focused toolset appropriate to its role.  The Orchestrator
  passes the output of agent N as the structured input to agent N+1.

AGENT ROLES:

  ┌─────────────┐     plan JSON     ┌──────────────┐     result     ┌───────────────┐
  │   PLANNER   │ ────────────────► │   EXECUTOR   │ ─────────────► │   VALIDATOR   │
  │             │                   │              │                 │               │
  │ Tools:      │                   │ Tools:       │                 │ Tools:        │
  │  read_file  │                   │  read_file   │                 │  run_bash     │
  │  list_files │                   │  write_file  │                 │               │
  └─────────────┘                   │  run_bash    │                 └───────────────┘
                                    └──────────────┘

WHAT IT DOES (concrete task):
  "Add a new Behave scenario to cart.feature that verifies the cart item
   count badge updates correctly when an item is added."

  PLANNER  → reads cart.feature + cart_steps.py + cart_page.py
           → produces a structured JSON plan: which file to edit,
             the Gherkin scenario to add, and the step definitions needed

  EXECUTOR → receives the plan
           → writes the new scenario into cart.feature
           → writes any new step definitions into inventory_steps.py
           → runs `python -m py_compile` on modified files

  VALIDATOR → receives a summary of what changed
            → runs `behave --dry-run` against cart.feature
            → reports PASS / FAIL with evidence

WHY THIS MATTERS FOR ECI:
  Complex QA tasks benefit from specialisation.  A single monolithic agent
  trying to plan AND implement AND validate degrades in quality as context
  grows.  The multi-agent pattern:
    • Makes reasoning auditable (each agent's output is inspectable)
    • Limits blast radius (Executor can't exceed its tool grant)
    • Enables parallelism (Executor could spawn parallel sub-executors)
    • Mirrors how human teams work — Planner ↔ Architect, Executor ↔ Engineer

  This is the foundation pattern for AI-assisted CI pipelines where
  planning, implementation, and verification are separate guardrailed stages.
"""

from shared.client import MODEL, get_client, get_repo_root
from shared.printer import divider, print_message, print_section
from tools.bash_tools import run_bash
from tools.file_tools import list_files, read_file, write_file

# ─────────────────────────────────────────────────────────────────────────────
# System prompts — each agent gets a narrow, role-specific persona
# ─────────────────────────────────────────────────────────────────────────────

_PLANNER_SYSTEM = """\
You are a QA Planning Agent.  Your ONLY job is to analyse existing test code
and produce a precise, unambiguous implementation plan.

YOU DO NOT WRITE CODE.  You only plan.

OUTPUT FORMAT — your final message MUST contain a JSON block like this:

```plan
{
  "task_summary": "one-sentence description",
  "files_to_modify": [
    {
      "path": "<absolute path>",
      "action": "append_scenario | add_steps | create",
      "description": "what to add or change"
    }
  ],
  "gherkin_scenario": "the full Gherkin scenario text to add",
  "step_definitions": [
    {
      "decorator": "@when | @then | @given",
      "pattern": "the step pattern string",
      "implementation": "Python implementation code"
    }
  ],
  "validation_command": "shell command to verify the feature file parses"
}
```

Be explicit about file paths.  Do not leave anything ambiguous for the Executor.
"""

_EXECUTOR_SYSTEM = """\
You are a QA Execution Agent.  You receive an implementation plan and execute
it precisely.

RULES:
  1. Implement EXACTLY what the plan specifies — no additions, no deviations.
  2. After writing each file, run `python -m py_compile <path>` to check syntax.
  3. If a compile check fails, fix the error and re-run — do not stop until clean.
  4. After all files are written and syntax-checked, run the validation_command
     from the plan.
  5. Your final message must be a concise summary:
       - Files modified (paths)
       - Scenario added (Gherkin text)
       - Steps added (decorator + pattern)
       - Validation result (exit code + relevant output)
"""

_VALIDATOR_SYSTEM = """\
You are a QA Validation Agent.  You verify that an implementation is correct
and complete.

YOUR ONLY TOOL is run_bash.  You cannot read or modify files.

VALIDATION PROTOCOL:
  1. Run `behave --dry-run <feature_file>` and check for parse errors.
  2. Run `python -m py_compile <steps_file>` on each modified steps file.
  3. Run `grep -n "<scenario_title>" <feature_file>` to confirm the scenario exists.

FINAL REPORT must include:
  VERDICT: PASS | FAIL
  EVIDENCE: (exact command output for each check)
  NOTES: (any observations for the engineering team)
"""


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────────────────────

def _extract_last_text(messages_seen: list) -> str:
    """Return the last text block from a list of BetaMessages."""
    for message in reversed(messages_seen):
        for block in reversed(message.content):
            if block.type == "text" and block.text.strip():
                return block.text
    return ""


def run(verbose: bool = True) -> None:
    repo = get_repo_root()
    features_dir = repo / "cucumber_python" / "features"
    steps_dir    = repo / "cucumber_python" / "steps"
    pages_dir    = repo / "cucumber_python" / "pages"

    divider("DEMO 4 — Multi-Agent: Planner → Executor → Validator")
    print("  Agents   : Planner · Executor · Validator")
    print(f"  Target   : {features_dir}/cart.feature")
    divider()

    client = get_client()

    # ── STAGE 1: PLANNER ────────────────────────────────────────────────────
    divider("STAGE 1 / PLANNER")
    print("  Tools: read_file, list_files (read-only exploration)")
    divider()

    planner_task = (
        f"Produce an implementation plan for adding a new Behave scenario.\n\n"
        f"TASK: Add a scenario to cart.feature that verifies the cart item "
        f"count badge updates when an item is added via the inventory page.\n\n"
        f"DIRECTORIES:\n"
        f"  Features : {features_dir}\n"
        f"  Steps    : {steps_dir}\n"
        f"  Pages    : {pages_dir}\n\n"
        f"Explore the existing cart.feature, inventory_steps.py, and "
        f"cart_page.py before writing your plan."
    )

    planner_messages_seen: list = []
    planner_runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=8192,
        thinking={"type": "adaptive"},
        system=_PLANNER_SYSTEM,
        tools=[read_file, list_files],
        messages=[{"role": "user", "content": planner_task}],
    )
    for msg in planner_runner:
        planner_messages_seen.append(msg)
        if verbose:
            print_message(msg)

    plan_text = _extract_last_text(planner_messages_seen)
    print_section("PLANNER OUTPUT", plan_text)

    # ── STAGE 2: EXECUTOR ───────────────────────────────────────────────────
    divider("STAGE 2 / EXECUTOR")
    print("  Tools: read_file, write_file, run_bash (read + write + run)")
    divider()

    executor_task = (
        f"Execute the following implementation plan precisely.\n\n"
        f"PLAN FROM PLANNER:\n{plan_text}\n\n"
        f"After all writes, run `python -m py_compile` on each modified file "
        f"and report the results."
    )

    executor_messages_seen: list = []
    executor_runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=8192,
        thinking={"type": "adaptive"},
        system=_EXECUTOR_SYSTEM,
        tools=[read_file, write_file, run_bash],
        messages=[{"role": "user", "content": executor_task}],
    )
    for msg in executor_runner:
        executor_messages_seen.append(msg)
        if verbose:
            print_message(msg)

    executor_result = _extract_last_text(executor_messages_seen)
    print_section("EXECUTOR OUTPUT", executor_result)

    # ── STAGE 3: VALIDATOR ──────────────────────────────────────────────────
    divider("STAGE 3 / VALIDATOR")
    print("  Tools: run_bash (verify only — no file access)")
    divider()

    validator_task = (
        f"Validate the following implementation.\n\n"
        f"EXECUTOR SUMMARY:\n{executor_result}\n\n"
        f"Feature file: {features_dir / 'cart.feature'}\n"
        f"Steps file  : {steps_dir / 'inventory_steps.py'}\n\n"
        f"Run all three validation checks from your protocol and issue a "
        f"final PASS or FAIL verdict with evidence."
    )

    validator_messages_seen: list = []
    validator_runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=_VALIDATOR_SYSTEM,
        tools=[run_bash],
        messages=[{"role": "user", "content": validator_task}],
    )
    for msg in validator_runner:
        validator_messages_seen.append(msg)
        if verbose:
            print_message(msg)

    validation_result = _extract_last_text(validator_messages_seen)
    print_section("VALIDATOR VERDICT", validation_result)

    # ── FINAL SUMMARY ────────────────────────────────────────────────────────
    divider("MULTI-AGENT RUN COMPLETE")
    verdict_line = next(
        (line for line in validation_result.splitlines() if "VERDICT" in line),
        "VERDICT: see output above",
    )
    print(f"\n  {verdict_line}")
    divider()
