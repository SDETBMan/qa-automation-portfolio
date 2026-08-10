#!/usr/bin/env python3
"""Bug Report Severity Classifier — DSPy on Vertex AI (Gemini).

Demonstrates the same BootstrapFewShot optimization pipeline as dspy-optimizer,
but using Google Vertex AI (Gemini) as the LLM backend instead of OpenAI.

Usage:
    python run.py                      # default: compare baseline vs optimized
    python run.py --mode baseline      # zero-shot only
    python run.py --mode optimized     # bootstrap + evaluate
    python run.py --mode compare       # side-by-side accuracy comparison
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import dspy
from dotenv import load_dotenv

from classifier.modules import BugClassifier
from classifier.optimizer import compile_with_bootstrap, evaluate, save_compiled
from datasets.bug_reports import DEVSET, TRAINSET

DIVIDER = "─" * 60
COMPILED_PATH = Path(__file__).parent / "output" / "compiled_classifier.json"


def _configure_lm() -> None:
    """Configure DSPy to use Vertex AI (Gemini) as the LLM backend."""
    project = os.environ.get("GCP_PROJECT", "")
    location = os.environ.get("GCP_LOCATION", "us-central1")

    if not project:
        print(
            "WARNING: GCP_PROJECT not set. Vertex AI requires a GCP project.\n"
            "  Copy .env.example -> .env and set GCP_PROJECT, or export GCP_PROJECT=...\n"
            "  Exiting gracefully (no GCP credentials)."
        )
        sys.exit(0)

    try:
        lm = dspy.LM(
            "vertex_ai/gemini-1.5-flash",
            temperature=0,
        )
        dspy.configure(lm=lm)
    except Exception as exc:
        print(
            f"WARNING: Failed to configure Vertex AI LM: {exc}\n"
            "  Ensure google-cloud-aiplatform is installed and GCP credentials are set.\n"
            "  Exiting gracefully."
        )
        sys.exit(0)


def run_baseline() -> tuple[BugClassifier, float]:
    """Evaluate the zero-shot (unoptimized) classifier on the dev set."""
    print(f"\n{DIVIDER}")
    print("MODE: Baseline (zero-shot, no few-shot examples)")
    print(f"  Backend: Vertex AI / Gemini 1.5 Flash")
    print(DIVIDER)

    classifier = BugClassifier()
    print(f"Evaluating on {len(DEVSET)} held-out examples...", flush=True)
    acc = evaluate(classifier, DEVSET)

    print(f"\nBaseline accuracy: {acc:.0%}  ({int(acc * len(DEVSET))}/{len(DEVSET)} correct)")
    _print_sample_predictions(classifier, DEVSET[:3], label="Baseline")
    return classifier, acc


def run_optimized() -> tuple[BugClassifier, float]:
    """Compile with BootstrapFewShot and evaluate on the dev set."""
    print(f"\n{DIVIDER}")
    print("MODE: Optimized (BootstrapFewShot, max_bootstrapped_demos=3)")
    print(f"  Backend: Vertex AI / Gemini 1.5 Flash")
    print(DIVIDER)

    print(f"Compiling on {len(TRAINSET)} training examples...", flush=True)
    compiled = compile_with_bootstrap(TRAINSET, max_bootstrapped_demos=3)

    print(f"Evaluating on {len(DEVSET)} held-out examples...", flush=True)
    acc = evaluate(compiled, DEVSET)

    save_compiled(compiled, COMPILED_PATH)
    print(f"\nOptimized accuracy: {acc:.0%}  ({int(acc * len(DEVSET))}/{len(DEVSET)} correct)")
    print(f"Compiled program saved to: {COMPILED_PATH}")
    _print_sample_predictions(compiled, DEVSET[:3], label="Optimized")
    return compiled, acc


def run_compare() -> None:
    """Run both modes and print a side-by-side accuracy comparison."""
    _, base_acc = run_baseline()
    _, opt_acc = run_optimized()

    delta = opt_acc - base_acc
    print(f"\n{DIVIDER}")
    print("RESULTS SUMMARY (Vertex AI / Gemini 1.5 Flash)")
    print(DIVIDER)
    print(f"{'Baseline accuracy':<30} {base_acc:.0%}")
    print(f"{'Optimized accuracy':<30} {opt_acc:.0%}")
    print(f"{'Delta':<30} {delta:+.0%}")
    print(DIVIDER)
    print("\nKey insight: BootstrapFewShot automatically selects high-quality")
    print("training demonstrations and injects them as few-shot examples,")
    print("improving accuracy without any manual prompt engineering.")
    print("\nThis variant demonstrates the same optimization pipeline on")
    print("Google Vertex AI (Gemini) instead of OpenAI, showing cloud-native")
    print("ML pipeline portability.")


def _print_sample_predictions(classifier: BugClassifier, examples: list, label: str) -> None:
    """Print a few sample predictions with gold labels."""
    print(f"\n  Sample predictions ({label}):")
    for ex in examples:
        pred = classifier(report=ex.report)
        match = "✓" if pred.severity.strip().lower() == ex.severity.lower() else "✗"
        short_report = ex.report[:70] + ("…" if len(ex.report) > 70 else "")
        print(f"  {match} Gold={ex.severity:<9} Pred={pred.severity.strip():<9} | {short_report}")


def main() -> None:
    load_dotenv(Path(__file__).parent / ".env")

    parser = argparse.ArgumentParser(description="DSPy Bug Severity Classifier (Vertex AI)")
    parser.add_argument(
        "--mode",
        choices=["baseline", "optimized", "compare"],
        default="compare",
        help="Which mode to run (default: compare)",
    )
    args = parser.parse_args()

    _configure_lm()

    if args.mode == "baseline":
        run_baseline()
    elif args.mode == "optimized":
        run_optimized()
    else:
        run_compare()


if __name__ == "__main__":
    main()
