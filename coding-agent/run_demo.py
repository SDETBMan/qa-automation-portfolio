#!/usr/bin/env python3
"""Entry point for the coding-agent demo suite.

USAGE:
    python run_demo.py --demo 1   # Codebase Reader & Rewriter
    python run_demo.py --demo 2   # Code Execution Feedback Loop
    python run_demo.py --demo 3   # Git & PR Automation
    python run_demo.py --demo 4   # Multi-Agent: Planner → Executor → Validator
    python run_demo.py --all      # Run all four demos sequentially

PREREQUISITES:
    1. Copy .env.example → .env and set ANTHROPIC_API_KEY
    2. pip install -r requirements.txt
    3. (Demo 3 only) gh auth login   — GitHub CLI authenticated

ENVIRONMENT VARIABLES:
    ANTHROPIC_API_KEY  — required; Anthropic API key
    REPO_ROOT          — optional; path to monorepo root (default: ../)
"""

import argparse
import sys
from pathlib import Path

# Make the coding-agent/ package importable regardless of cwd
sys.path.insert(0, str(Path(__file__).parent))


DEMOS = {
    1: ("Codebase Reader & Rewriter",           "agents.demo1_codebase_rewriter"),
    2: ("Code Execution Feedback Loop",          "agents.demo2_code_execution"),
    3: ("Git & PR Automation",                   "agents.demo3_git_pr"),
    4: ("Multi-Agent: Planner → Executor → Validator", "agents.demo4_multi_agent"),
}


def run_demo(demo_number: int, verbose: bool = True) -> None:
    import importlib
    _, module_path = DEMOS[demo_number]
    module = importlib.import_module(module_path)
    module.run(verbose=verbose)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run coding-agent demos against the SauceDemo test suite.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(
            f"  --demo {n}  {label}" for n, (label, _) in DEMOS.items()
        ),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--demo",
        type=int,
        choices=DEMOS.keys(),
        metavar="{1-4}",
        help="Demo number to run (1-4)",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Run all four demos sequentially",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-message streaming output (print summaries only)",
    )

    args = parser.parse_args()
    verbose = not args.quiet

    if args.all:
        for n in DEMOS:
            run_demo(n, verbose=verbose)
    else:
        run_demo(args.demo, verbose=verbose)


if __name__ == "__main__":
    main()
