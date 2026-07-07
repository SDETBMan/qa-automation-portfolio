"""Demo 5 — AI Test Generator (Manual QA → Automated pytest)

CAPABILITY DEMONSTRATED:
  A manual QA engineer describes a test in plain English, and the agent
  generates a runnable pytest test by learning patterns from the existing
  test suite and source code.

WHAT IT DOES (concrete steps):
  1. Receives a natural language test description from the QA engineer
  2. Reads existing tests (claims-diff/tests/) to learn patterns — fixtures,
     assertions, class structure, naming conventions
  3. Reads source code (claims-diff/differ/) to understand the code under test
  4. Generates a pytest test file in coding-agent/output/generated_test.py
  5. Validates syntax with `python -m py_compile`
  6. Runs `pytest output/generated_test.py -v` to verify it passes
  7. Iterates on failures until the test is green

WHY THIS MATTERS:
  This is the core value proposition of AI tooling for QA — enabling manual
  testers to generate automated tests by describing what they want to verify
  in plain English. The agent enforces project conventions, uses existing
  fixtures, and produces tests indistinguishable from hand-written ones.

DEFAULT DEMO INPUT (realistic manual QA description):
  "Write a pytest test that verifies the diff engine correctly detects when
   a claim's procedure code changes from one CPT code to another, and reports
   it as a modified field with the correct baseline and current values."
"""

from shared.client import MODEL, get_client, get_repo_root
from shared.printer import divider, print_message, print_section
from tools.bash_tools import run_bash
from tools.file_tools import list_files, read_file, write_file

_SYSTEM = """\
You are an expert QA automation engineer specialising in pytest.  Your job is
to translate a manual tester's plain-English test description into a production-
quality pytest test that follows the existing project conventions.

PROCESS (follow these steps in order):
  1. EXPLORE — Read existing tests in the project's tests/ directory to learn:
     • Class-based test organisation (TestClassName pattern)
     • Factory fixtures (sample_claim) and how they're invoked
     • Assertion style, docstrings, and naming conventions
  2. EXPLORE — Read the source code under test (differ/) to understand:
     • The function signatures and return types you'll be testing
     • The data models (ClaimRecord, DiffReport, FieldDiff, etc.)
     • What behaviour is already tested vs. what the new test adds
  3. GENERATE — Write a pytest test file that:
     • Uses pytest classes with descriptive names (TestProcedureCodeChange, etc.)
     • Uses the sample_claim factory fixture from conftest.py — do NOT redefine it
     • Uses descriptive test method names (test_<what>_<expected_outcome>)
     • Includes a class-level docstring and per-test docstrings
     • Has no magic strings — use the same CPT codes and patterns from the project
     • Imports only from the project's own modules (differ.diff_engine, differ.models)
     • Follows the exact same style as the existing tests
  4. VALIDATE — Run `python -m py_compile <file>` to check syntax
  5. RUN — Run `pytest <file> -v` to verify the test passes
  6. FIX — If either step fails, read the error, fix the test, and repeat from step 4

QUALITY RULES:
  - The generated test must pass on the FIRST pytest run (or iterate until it does)
  - Do NOT duplicate tests that already exist — the new test must add coverage
  - Use the sample_claim fixture from conftest.py — never create your own fixture
  - Keep assertions specific: assert exact field names, baseline values, current values
  - One test class per logical behaviour being tested
  - sys.path manipulation is acceptable to make imports work from the output/ location
"""

_DEFAULT_DESCRIPTION = (
    "Write a pytest test that verifies the diff engine correctly detects when "
    "a claim's procedure code changes from one CPT code to another, and reports "
    "it as a modified field with the correct baseline and current values."
)


def run(verbose: bool = True) -> None:
    repo = get_repo_root()
    output_dir = repo / "coding-agent" / "output"
    test_path = output_dir / "generated_test.py"
    claims_diff = repo / "claims-diff"

    output_dir.mkdir(parents=True, exist_ok=True)

    task_message = (
        f"A manual QA tester has asked you to create an automated test:\n\n"
        f'"{_DEFAULT_DESCRIPTION}"\n\n'
        f"Project layout:\n"
        f"  Source code:     {claims_diff / 'differ'}\n"
        f"  Existing tests:  {claims_diff / 'tests'}\n"
        f"  conftest.py:     {claims_diff / 'tests' / 'conftest.py'}\n\n"
        f"Write the generated test to: {test_path}\n\n"
        f"After writing, validate and run with:\n"
        f"  python -m py_compile \"{test_path}\"\n"
        f"  pytest \"{test_path}\" -v\n\n"
        f"The test must import from differ.diff_engine and differ.models.\n"
        f"Add the claims-diff directory to sys.path at the top of the generated\n"
        f"test file so imports resolve correctly:\n"
        f"  import sys; sys.path.insert(0, r\"{claims_diff}\")\n\n"
        f"Iterate until pytest shows all tests PASSED."
    )

    divider("DEMO 5 — AI Test Generator (Manual QA → Automated pytest)")
    print(f"  Input  : \"{_DEFAULT_DESCRIPTION}\"")
    print(f"  Output : {test_path}")
    divider()

    client = get_client()
    tools = [read_file, list_files, write_file, run_bash]

    runner = client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=16384,
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

    print_section("DEMO 5 RESULT", final_text)
    if test_path.exists():
        print(f"\n  Generated test saved -> {test_path}")
