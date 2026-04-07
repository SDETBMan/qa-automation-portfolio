"""Conditional edge routing for the Test Case Generator graph."""

from __future__ import annotations

from typing import Literal

from .state import AgentState

MAX_REVISIONS = 2


def review_router(state: AgentState) -> Literal["revise_tests", "__end__"]:
    """Route after review_quality: end on PASS or max revisions, else revise.

    This function is the single conditional edge in the graph, demonstrating
    LangGraph's cycle-with-termination pattern:

        review_quality → review_router → revise_tests → review_quality  (loop)
                                       → END                             (exit)
    """
    if state["review_verdict"] == "PASS" or state["revision_count"] >= MAX_REVISIONS:
        return "__end__"
    return "revise_tests"
