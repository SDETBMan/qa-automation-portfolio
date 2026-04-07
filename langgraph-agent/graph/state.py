"""AgentState TypedDict — shared state schema for the test-case generator graph."""

from __future__ import annotations

from typing import TypedDict


class AgentState(TypedDict):
    """State passed between every node in the LangGraph pipeline.

    Fields
    ------
    feature_desc : str
        Plain-English description of the feature under test (user input).
    requirements : str
        Structured acceptance criteria extracted by parse_requirements.
    test_cases : str
        BDD Gherkin scenarios produced (or revised) by generate/revise nodes.
    review_verdict : str
        "PASS" or "REVISE" — set by the review_quality node.
    review_feedback : str
        Actionable feedback from the reviewer (empty string on PASS).
    revision_count : int
        Number of revisions performed; capped at 2 to bound LLM cost.
    """

    feature_desc: str
    requirements: str
    test_cases: str
    review_verdict: str
    review_feedback: str
    revision_count: int
