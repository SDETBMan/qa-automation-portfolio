"""Demo 1 — Codebase Reader & Rewriter

CAPABILITY DEMONSTRATED:
  An agent that reads a real legacy codebase, identifies a code smell,
  proposes a modernisation, writes the rewrite, validates it with a syntax
  check, and iterates until the validation passes.

WHAT IT DOES (concrete steps):
  1. Explores cucumber_python/steps/ to understand the step structure
  2. Reads auth_steps.py — identifies any places where inline Selenium
     calls bypass the Page Object / Screenplay abstraction
  3. Rewrites the file so every browser interaction goes through LoginPage
     or LoginTask (the Screenplay task already defined in utils/tasks.py)
  4. Saves the rewrite to coding-agent/output/auth_steps_rewritten.py
  5. Runs `python -m py_compile` to validate syntax
  6. Iterates if the compile step fails

WHY THIS MATTERS FOR ECI:
  Production test suites decay.  Steps accumulate inline Selenium, magic
  strings, and copy-pasted waits.  An agent that can read the current state,
  reason about the intended abstraction layer, and produce a compliant rewrite
  — and then VERIFY it — is the difference between AI-assisted and
  AI-assured modernisation.

ADAPTIVE THINKING:
  Uses `thinking: {type: "adaptive"}` so Claude decides how much reasoning
  to invest.  For a file with subtle violations the thinking budget rises
  automatically; for trivially clean code it stays low.
"""

from pathlib import Path

from shared.client import MODEL, get_client, get_repo_root
from shared.printer import divider, print_message, print_section
from tools.bash_tools import run_bash
from tools.file_tools import list_files, read_file, write_file

_SYSTEM = """\
You are a senior QA engineer specialising in Python test automation.
Your task is to modernise step definitions in a Behave (BDD) framework.

ARCHITECTURE RULES you must enforce:
  1. Steps MUST NOT contain inline Selenium / WebDriver calls.
     All browser interactions go through a Page Object in pages/.
  2. Steps MAY call Screenplay tasks from utils/tasks.py for multi-action flows.
  3. No bare time.sleep() — use explicit waits already in BasePage.
  4. No magic strings — use the string from the page object selector maps.

WORKFLOW:
  a. Call list_files to understand the step and page structure.
  b. Call read_file on auth_steps.py and the relevant page objects.
  c. Identify every violation of the architecture rules above.
  d. Write the corrected file to the output path supplied in the task.
  e. Run `python -m py_compile <output_path>` to confirm syntax is valid.
  f. If the compile fails, fix the error and re-run.  Do not stop until
     the compile exits 0.

Be explicit in your reasoning: list each violation found, then show the fix.
"""


def run(verbose: bool = True) -> None:
    repo = get_repo_root()
    steps_dir     = repo / "cucumber_python" / "steps"
    pages_dir     = repo / "cucumber_python" / "pages"
    utils_dir     = repo / "cucumber_python" / "utils"
    output_dir    = repo / "coding-agent" / "output"
    output_path   = output_dir / "auth_steps_rewritten.py"

    output_dir.mkdir(parents=True, exist_ok=True)

    task_message = (
        f"Modernise the Behave auth step definitions to comply with the "
        f"Page Object / Screenplay architecture.\n\n"
        f"DIRECTORIES TO EXPLORE:\n"
        f"  Steps : {steps_dir}\n"
        f"  Pages : {pages_dir}\n"
        f"  Utils : {utils_dir}\n\n"
        f"TARGET FILE : {steps_dir / 'auth_steps.py'}\n"
        f"OUTPUT FILE : {output_path}\n\n"
        f"After writing the output file, validate it with:\n"
        f"  python -m py_compile {output_path}\n\n"
        f"Iterate until the compile exits 0."
    )

    divider("DEMO 1 — Codebase Reader & Rewriter")
    print(f"  Target  : {steps_dir / 'auth_steps.py'}")
    print(f"  Output  : {output_path}")
    divider()

    client  = get_client()
    tools   = [list_files, read_file, write_file, run_bash]

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
        # Capture final text for the summary
        for block in message.content:
            if block.type == "text":
                final_text = block.text

    print_section("DEMO 1 RESULT", final_text)
    if output_path.exists():
        print(f"\n  Rewritten file saved → {output_path}")
