#!/usr/bin/env python3
"""Test Case Generator Pipeline — LangGraph demo.

Usage:
    python run.py --feature "User can add products to cart"
    python run.py --demo          # runs a built-in example
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

if not os.getenv("ANTHROPIC_API_KEY"):
    sys.exit(
        "ERROR: ANTHROPIC_API_KEY not set.\n"
        "  Copy .env.example → .env and add your key, or export ANTHROPIC_API_KEY=..."
    )

from graph.pipeline import build_graph

DEMO_FEATURE = "User can add products to cart and proceed to checkout"

DIVIDER = "─" * 60


def run_pipeline(feature_desc: str) -> dict:
    """Execute the full graph and return the final state."""
    graph = build_graph()

    initial_state = {
        "feature_desc": feature_desc,
        "requirements": "",
        "test_cases": "",
        "review_verdict": "",
        "review_feedback": "",
        "revision_count": 0,
    }

    print(f"\n{DIVIDER}")
    print(f"Feature: {feature_desc}")
    print(DIVIDER)

    # Stream node events so the user sees progress in real time
    final_state = None
    for event in graph.stream(initial_state):
        for node_name, node_output in event.items():
            print(f"\n[node: {node_name}]")
            if node_name == "parse_requirements":
                print(node_output.get("requirements", ""))
            elif node_name == "generate_tests":
                print(node_output.get("test_cases", ""))
            elif node_name == "review_quality":
                verdict = node_output.get("review_verdict", "")
                feedback = node_output.get("review_feedback", "")
                rev = node_output.get("revision_count", 0)
                print(f"Verdict: {verdict}  (revisions so far: {rev})")
                if feedback:
                    print(f"Feedback: {feedback}")
            elif node_name == "revise_tests":
                print(node_output.get("test_cases", ""))
            final_state = node_output

    return final_state or {}


def save_output(state: dict) -> Path:
    """Write final test cases to output/."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"test_cases_{ts}.md"

    content = f"""# Generated Test Cases

**Feature:** {state.get('feature_desc', '')}

**Revisions:** {state.get('revision_count', 0)}
**Final verdict:** {state.get('review_verdict', '')}

---

## Acceptance Criteria

{state.get('requirements', '')}

---

## Gherkin Scenarios

```gherkin
{state.get('test_cases', '')}
```
"""
    out_path.write_text(content, encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="LangGraph Test Case Generator")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--feature", "-f", help="Plain-English feature description")
    group.add_argument("--demo", action="store_true", help="Run built-in demo feature")
    args = parser.parse_args()

    if args.demo:
        feature = DEMO_FEATURE
    elif args.feature:
        feature = args.feature
    else:
        parser.print_help()
        sys.exit(1)

    final_state = run_pipeline(feature)

    out_path = save_output(final_state)
    print(f"\n{DIVIDER}")
    print(f"Done. Output saved to: {out_path}")
    print(DIVIDER)


if __name__ == "__main__":
    main()
