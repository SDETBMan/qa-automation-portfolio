"""BootstrapFewShot optimizer for the bug severity classifier."""

from __future__ import annotations

from pathlib import Path

import dspy
from dspy.teleprompt import BootstrapFewShot

from .modules import BugClassifier


def _severity_metric(example: dspy.Example, prediction: dspy.Prediction, trace=None) -> bool:
    """Return True if the predicted severity matches the gold label (case-insensitive)."""
    return example.severity.strip().lower() == prediction.severity.strip().lower()


def compile_with_bootstrap(
    trainset: list[dspy.Example],
    max_bootstrapped_demos: int = 3,
) -> BugClassifier:
    """Compile BugClassifier using BootstrapFewShot.

    BootstrapFewShot runs the unoptimized module on *trainset*, collects
    successful (input, output) demonstrations, and injects them as few-shot
    examples into the optimized module's prompt.

    Args:
        trainset: Training examples with .report and .severity fields.
        max_bootstrapped_demos: Maximum few-shot examples to inject (keeps
            token count and cost low; default 3 is sufficient for this task).

    Returns:
        A compiled BugClassifier with optimized prompts.
    """
    optimizer = BootstrapFewShot(
        metric=_severity_metric,
        max_bootstrapped_demos=max_bootstrapped_demos,
        max_labeled_demos=max_bootstrapped_demos,
    )
    student = BugClassifier()
    compiled = optimizer.compile(student, trainset=trainset)
    return compiled


def evaluate(classifier: BugClassifier, devset: list[dspy.Example]) -> float:
    """Return accuracy (fraction correct) on *devset*."""
    correct = 0
    for ex in devset:
        pred = classifier(report=ex.report)
        if _severity_metric(ex, pred):
            correct += 1
    return correct / len(devset) if devset else 0.0


def save_compiled(classifier: BugClassifier, path: Path) -> None:
    """Save the compiled program state to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    classifier.save(str(path))


def load_compiled(path: Path) -> BugClassifier:
    """Load a previously compiled program from a JSON file."""
    classifier = BugClassifier()
    classifier.load(str(path))
    return classifier
