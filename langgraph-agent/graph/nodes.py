"""Four node functions for the Test Case Generator pipeline."""

from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from .state import AgentState

# Use claude-haiku — cheapest Anthropic model; shows LangGraph is provider-agnostic
_LLM = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0)


def _call(system: str, human: str) -> str:
    """Single LLM call returning stripped text content."""
    response = _LLM.invoke([SystemMessage(content=system), HumanMessage(content=human)])
    return response.content.strip()


# ── Node 1 ──────────────────────────────────────────────────────────────────

def parse_requirements(state: AgentState) -> AgentState:
    """Extract structured acceptance criteria from a feature description."""
    system = (
        "You are a senior QA engineer. Given a feature description, extract "
        "3-6 clear, testable acceptance criteria as a numbered list. "
        "Be concise and specific."
    )
    requirements = _call(system, f"Feature: {state['feature_desc']}")
    return {**state, "requirements": requirements}


# ── Node 2 ──────────────────────────────────────────────────────────────────

def generate_tests(state: AgentState) -> AgentState:
    """Write BDD Gherkin scenarios for the acceptance criteria."""
    system = (
        "You are a senior QA engineer writing BDD Gherkin test cases. "
        "Write a complete Feature block with 3-5 Scenarios (or Scenario Outlines). "
        "Follow Gherkin syntax: Feature, Background (if needed), Scenario, "
        "Given/When/Then/And. Include at least one positive path, one negative path, "
        "and one edge case."
    )
    human = (
        f"Feature: {state['feature_desc']}\n\n"
        f"Acceptance criteria:\n{state['requirements']}"
    )
    test_cases = _call(system, human)
    return {**state, "test_cases": test_cases, "review_verdict": "", "review_feedback": ""}


# ── Node 3 ──────────────────────────────────────────────────────────────────

def review_quality(state: AgentState) -> AgentState:
    """Review the Gherkin scenarios and return PASS or REVISE with feedback."""
    system = (
        "You are a QA lead reviewing Gherkin test cases. "
        "Evaluate whether the scenarios adequately cover the acceptance criteria. "
        "Reply with exactly one line: 'VERDICT: PASS' or 'VERDICT: REVISE'. "
        "If REVISE, add a second paragraph starting with 'FEEDBACK:' that lists "
        "specific improvements needed (missing edge cases, vague steps, etc.)."
    )
    human = (
        f"Acceptance criteria:\n{state['requirements']}\n\n"
        f"Test cases to review:\n{state['test_cases']}"
    )
    review_text = _call(system, human)

    verdict = "PASS" if "VERDICT: PASS" in review_text.upper() else "REVISE"
    feedback = ""
    if verdict == "REVISE" and "FEEDBACK:" in review_text.upper():
        idx = review_text.upper().index("FEEDBACK:")
        feedback = review_text[idx + len("FEEDBACK:"):].strip()

    return {**state, "review_verdict": verdict, "review_feedback": feedback}


# ── Node 4 ──────────────────────────────────────────────────────────────────

def revise_tests(state: AgentState) -> AgentState:
    """Improve the test cases based on reviewer feedback."""
    system = (
        "You are a senior QA engineer revising BDD Gherkin test cases based on "
        "reviewer feedback. Apply all requested changes and return the complete "
        "revised Feature block."
    )
    human = (
        f"Original test cases:\n{state['test_cases']}\n\n"
        f"Reviewer feedback:\n{state['review_feedback']}"
    )
    revised = _call(system, human)
    return {**state, "test_cases": revised, "revision_count": state["revision_count"] + 1}
