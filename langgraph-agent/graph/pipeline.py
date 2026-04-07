"""Build and compile the Test Case Generator StateGraph."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from .edges import review_router
from .nodes import generate_tests, parse_requirements, review_quality, revise_tests
from .state import AgentState


def build_graph():
    """Construct and compile the LangGraph pipeline.

    Graph topology
    --------------
    parse_requirements
        → generate_tests
            → review_quality
                → (conditional) revise_tests → review_quality  (loop, max 2x)
                → END
    """
    builder = StateGraph(AgentState)

    # ── Register nodes ───────────────────────────────────────────────────────
    builder.add_node("parse_requirements", parse_requirements)
    builder.add_node("generate_tests", generate_tests)
    builder.add_node("review_quality", review_quality)
    builder.add_node("revise_tests", revise_tests)

    # ── Linear edges ─────────────────────────────────────────────────────────
    builder.set_entry_point("parse_requirements")
    builder.add_edge("parse_requirements", "generate_tests")
    builder.add_edge("generate_tests", "review_quality")

    # ── Conditional edge with cycle ───────────────────────────────────────────
    builder.add_conditional_edges(
        "review_quality",
        review_router,
        {
            "revise_tests": "revise_tests",
            "__end__": END,
        },
    )
    builder.add_edge("revise_tests", "review_quality")  # close the loop

    return builder.compile()
