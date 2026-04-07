"""DSPy module wrapping the bug severity classifier."""

from __future__ import annotations

import dspy

from .signatures import BugSeveritySignature


class BugClassifier(dspy.Module):
    """Chain-of-thought bug severity classifier.

    Uses dspy.ChainOfThought to prompt the LLM to reason step-by-step before
    committing to a severity label — improves accuracy on borderline cases.
    """

    def __init__(self) -> None:
        super().__init__()
        self.classify = dspy.ChainOfThought(BugSeveritySignature)

    def forward(self, report: str) -> dspy.Prediction:
        return self.classify(report=report)
