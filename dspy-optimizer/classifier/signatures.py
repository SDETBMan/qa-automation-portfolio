"""DSPy Signatures for the Bug Report Severity Classifier."""

from __future__ import annotations

import dspy


class BugSeveritySignature(dspy.Signature):
    """Classify a software bug report into a severity level.

    Severity levels:
    - Critical: System down, data loss, security breach, complete feature failure
      affecting all users.
    - High: Major feature broken for a significant subset of users, no workaround.
    - Medium: Feature partially broken or degraded; workaround exists; affects
      a limited set of users.
    - Low: Cosmetic issue, minor UX annoyance, typo, or documentation error.
    """

    report: str = dspy.InputField(desc="Bug report text submitted by a QA engineer or user.")
    reasoning: str = dspy.OutputField(
        desc="Step-by-step reasoning explaining the severity classification."
    )
    severity: str = dspy.OutputField(
        desc="One of: Critical, High, Medium, or Low."
    )
