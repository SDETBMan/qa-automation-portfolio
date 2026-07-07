# Coding Agent — AI-Assisted QA Automation

A Python framework demonstrating four core coding-agent capabilities using the
Anthropic Claude API (`claude-opus-4-6`) against the real SauceDemo test suite
in this monorepo.

Each demo is independently runnable and designed to show a distinct AI
engineering pattern — from simple tool use to multi-agent orchestration.

---

## Capabilities Demonstrated

| Demo | Pattern | One-Line Description |
|------|---------|----------------------|
| 1 | Codebase Reader & Rewriter | Reads live test code, identifies violations of the Page Object architecture, rewrites + validates |
| 2 | Code Execution Feedback Loop | Writes a Python script, runs it, reads stdout/stderr, and iterates until all assertions pass |
| 3 | Git & PR Automation | Creates a branch, makes a purposeful commit, dry-runs push, and drafts a full PR description |
| 4 | Multi-Agent: Planner → Executor → Validator | Three specialised agents with role-scoped tools collaborate through clean context handoff |
| 5 | AI Test Generator (Manual QA → pytest) | Translates a plain-English test description into a runnable pytest test using existing project patterns |

---

## Architecture

```
coding-agent/
├── run_demo.py              # CLI entry point  (python run_demo.py --demo N)
├── requirements.txt
│
├── shared/
│   ├── client.py            # Anthropic client + MODEL constant + repo root helper
│   └── printer.py           # Colour-coded streaming output for BetaMessage stream
│
├── tools/                   # @beta_tool decorated functions — auto-schema generation
│   ├── file_tools.py        # read_file · write_file · list_files
│   ├── bash_tools.py        # run_bash (stdout + stderr + exit code)
│   ├── git_tools.py         # git_status · git_diff · git_create_branch · git_add_and_commit · git_push
│   └── github_tools.py      # gh_create_pr · gh_list_pr_comments · gh_reply_to_pr · gh_pr_status
│
├── agents/
│   ├── demo1_codebase_rewriter.py
│   ├── demo2_code_execution.py
│   ├── demo3_git_pr.py
│   ├── demo4_multi_agent.py
│   └── demo5_test_generator.py
│
└── output/                  # Agent-generated files written here (git-ignored)
```

### Key Design Decisions

**`@beta_tool` decorator** — tool schemas are generated automatically from
function signatures and Google-style docstrings.  Adding a new tool is one
function; no JSON schemas to maintain by hand.

**`client.beta.messages.tool_runner()`** — the SDK's agentic loop handles the
`tool_use → tool_result → next_call` cycle automatically.  Each iteration yields
a `BetaMessage`; the loop exits when `stop_reason == "end_turn"`.

**`thinking: {"type": "adaptive"}`** — Opus 4.6 decides dynamically how much
chain-of-thought to invest.  Simple tasks (read a file) stay fast; complex
reasoning (multi-file architecture analysis) gets a larger budget automatically.

**Role-scoped tools in Demo 4** — each agent receives only the tools appropriate
to its role:
- Planner: `read_file`, `list_files` (analysis only, no writes)
- Executor: `read_file`, `write_file`, `run_bash` (implementation)
- Validator: `run_bash` (verification only, no file access)

This mirrors real-world access control: a CI validator shouldn't be able to
modify the files it's verifying.

---

## Quick Start

```bash
# 1. Install dependencies
cd coding-agent
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env

# 3. Run a demo
python run_demo.py --demo 2          # Recommended first run — no side effects
python run_demo.py --demo 1          # Requires cucumber_python/ to be present
python run_demo.py --demo 3          # Reads + modifies feature files (git tracked)
python run_demo.py --demo 4          # Runs all three agents sequentially
python run_demo.py --demo 5          # AI Test Generator — manual QA → pytest
python run_demo.py --all             # All five demos

# Quiet mode (summaries only, no streaming)
python run_demo.py --demo 4 --quiet
```

### Prerequisites by Demo

| Demo | Requires |
|------|----------|
| 1    | `cucumber_python/` in the monorepo |
| 2    | Nothing beyond `ANTHROPIC_API_KEY` |
| 3    | `cucumber_python/` + git configured; `gh` CLI optional |
| 4    | `cucumber_python/` + `behave` installed (`pip install behave`) |
| 5    | `claims-diff/` in the monorepo (reads tests + source for pattern learning) |

---

## Demo Deep-Dives

### Demo 1 — Codebase Reader & Rewriter

The agent explores `cucumber_python/steps/` and `pages/`, identifies any
violations of the Page Object architecture in `auth_steps.py` (inline Selenium
calls, magic strings, `time.sleep()` usage), and produces a compliant rewrite
at `output/auth_steps_rewritten.py`.  It then runs `python -m py_compile` to
validate syntax and iterates if it fails.

This demonstrates the core capability for **legacy migration tooling** — an
agent that understands a codebase's intended abstractions and enforces them.

### Demo 2 — Code Execution Feedback Loop

The agent writes `output/validate_saucedemo.py`, a pure-stdlib Python script
that validates SauceDemo is reachable and that the page title matches.  It runs
the script, reads stdout/stderr and exit code, and iterates until all assertions
pass.  The final script is left in `output/` as an artefact.

This demonstrates the **write → run → observe → fix** cycle that underpins
reliable AI-generated code.  The agent encounters real failure modes
(ImportError, connection error, assertion failure) and resolves them.

### Demo 3 — Git & PR Automation

The agent reads the Behave feature files, identifies the highest-value scenarios
(multi-step, critical path), adds `@performance` tags, creates a branch
`agent/add-performance-tags`, commits with a conventional commit message, and
dry-runs a push.  It then produces a full PR title, body (Summary + Motivation +
Test Plan), and label recommendations.

This demonstrates **automated test suite maintenance** — triage and metadata
work that is tedious for humans but straightforward for an agent that can reason
about test complexity.

### Demo 4 — Multi-Agent System

Three agents collaborate with role-scoped tools:

1. **Planner** explores the codebase and produces a structured JSON plan for
   adding a new cart badge scenario to `cart.feature`.
2. **Executor** receives the plan, writes the scenario + step definitions,
   runs `py_compile` on each modified file.
3. **Validator** runs `behave --dry-run` and `grep` to confirm the scenario
   exists and the feature file parses without errors.

The orchestrator (`demo4_multi_agent.py`) passes the Planner's full text output
as the Executor's task, and the Executor's summary as the Validator's input —
a clean, auditable context handoff chain.

### Demo 5 — AI Test Generator (Manual QA → pytest)

A manual QA engineer provides a plain-English test description, and the agent
generates a production-quality pytest test by learning from existing project
patterns.  The agent:

1. Reads `claims-diff/tests/` to learn class structure, fixture usage, and
   assertion style
2. Reads `claims-diff/differ/` to understand the code under test
3. Generates `output/generated_test.py` following all discovered conventions
4. Validates with `python -m py_compile` and runs `pytest -v`
5. Iterates on failures until the test is green

This demonstrates the core capability of **AI-assisted test authoring** —
enabling manual QA testers to produce automated tests by describing what they
want to verify, while the agent enforces project conventions and ensures the
output is indistinguishable from hand-written tests.

---

## CI / CD

The `coding-agent.yml` workflow runs on every push to `coding-agent/**`:

- **Lint job**: ruff + import smoke test (no API calls)
- **Demo 2 job**: runs the feedback loop demo (requires `ANTHROPIC_API_KEY` secret)
- **Manual dispatch**: run any demo or all four via `workflow_dispatch`

The `ANTHROPIC_API_KEY` is stored as a GitHub Actions secret.  Set
`vars.RUN_AGENT_DEMOS = 'true'` on the repository to enable Demo 2 on every PR.

---

## Adding New Tools

```python
# tools/my_tools.py
from anthropic import beta_tool

@beta_tool
def my_tool(arg1: str, arg2: int = 5) -> str:
    """One-line description of what this tool does.

    Args:
        arg1: Description of arg1.
        arg2: Description of arg2 (default 5).
    """
    return f"result: {arg1} * {arg2}"
```

Import and add to the `tools=[...]` list in any agent.  The `@beta_tool`
decorator handles JSON schema generation automatically.

---

## Model Configuration

All agents use `claude-opus-4-6` with adaptive thinking.  To switch models:

```python
# shared/client.py
MODEL = "claude-sonnet-4-6"   # Faster, lower cost — good for Demo 2
```

For cost-sensitive bulk runs, swap Demo 4's Validator (simple bash verification)
to `claude-haiku-4-5` by passing `model=` explicitly to that agent's
`tool_runner()` call.
