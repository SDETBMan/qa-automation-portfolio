"""Demo 2 — Code Execution Feedback Loop

CAPABILITY DEMONSTRATED:
  An agent that writes a Python script, executes it in a bash sandbox,
  reads the output, and iterates — fixing errors on each cycle — until
  the script runs cleanly and produces the expected result.

WHAT IT DOES (concrete steps):
  1. Receives a spec: "Write a script that validates SauceDemo is reachable
     and that the page title is 'Swag Labs'."
  2. Writes validate_saucedemo.py to coding-agent/output/
  3. Runs it with `python validate_saucedemo.py`
  4. Reads stdout / stderr
  5. If the exit code is non-zero OR the assertion fails → fixes the script
  6. Repeats until: exit code 0 AND "PASS" appears in stdout
  7. Reports the final working script

WHY THIS MATTERS FOR ECI:
  Test code generation without a feedback loop produces brittle, unverified
  output.  A write → run → observe → fix cycle mirrors what a human engineer
  does at the REPL — it's the core of reliable AI-assisted test authoring.
  The agent must reason about Python exceptions, missing imports, network
  errors, and assertion failures — all different failure modes, all resolved
  without human intervention.

NOTE ON DEPENDENCIES:
  The generated script uses only the Python standard library (urllib) so it
  runs without installing Selenium or Playwright.  The agent discovers this
  constraint from the environment and adapts.
"""

from pathlib import Path

from shared.client import MODEL, get_client, get_repo_root
from shared.printer import divider, print_message, print_section
from tools.bash_tools import run_bash
from tools.file_tools import write_file

_SYSTEM = """\
You are a QA automation engineer working in a Python environment.
Your task is to write and verify a script using a write → run → fix loop.

RULES:
  1. Use only the Python standard library — no pip installs.
  2. The script must exit 0 on success and non-zero on failure.
  3. The script must print "PASS: <assertion>" for each passing check.
  4. Iterate until every check passes and exit code is 0.
  5. After success, print a brief summary of the final script and what it validates.

SCRIPT SPEC:
  Validate SauceDemo (https://www.saucedemo.com) by:
    a. Making an HTTP GET request to the homepage.
    b. Asserting the HTTP status code is 200.
    c. Asserting the page HTML contains the string "Swag Labs".
  Print PASS for each assertion, FAIL + reason if any assertion fails.
"""


def run(verbose: bool = True) -> None:
    repo       = get_repo_root()
    output_dir = repo / "coding-agent" / "output"
    script_path = output_dir / "validate_saucedemo.py"

    output_dir.mkdir(parents=True, exist_ok=True)

    task_message = (
        f"Write, run, and iterate on a SauceDemo validation script.\n\n"
        f"Save the script to: {script_path}\n\n"
        f"Run it with: python \"{script_path}\"\n\n"
        f"The loop is complete when:\n"
        f"  • exit code is 0\n"
        f"  • stdout contains 'PASS' for every assertion\n"
        f"  • stdout does NOT contain 'FAIL'\n\n"
        f"If the script fails for any reason, inspect the output, fix the "
        f"script, overwrite the file, and run again."
    )

    divider("DEMO 2 — Code Execution Feedback Loop")
    print(f"  Output : {script_path}")
    divider()

    client  = get_client()
    tools   = [write_file, run_bash]

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

    print_section("DEMO 2 RESULT", final_text)
    if script_path.exists():
        print(f"\n  Final script saved → {script_path}")
