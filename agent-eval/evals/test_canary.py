"""
test_canary.py — Canary (negative-control) tests for agent-eval metrics.

These tests feed known-bad tool calls and outputs to each metric and assert the
metric fires (i.e. the score is bad). They validate the metrics themselves, not
the agent. If a DeepEval upgrade, model deprecation, or prompt tweak silently
degrades a metric, the canary will fail before any real eval test is affected.

Design principles:
  - All inputs/outputs are hardcoded. No agent runs. Only the LLM judge
    (gpt-4o-mini) is called.
  - Inverted assertions: metric.measure() then assert the score lands in the
    "clearly bad" range. Wide margins absorb LLM judge non-determinism.
  - Dual markers: @canary + @smoke so canaries run on every push.

DataDog metrics:
  llm.agent.canary.tool_correctness
  llm.agent.canary.task_completion
"""

import pytest
from deepeval.metrics import TaskCompletionMetric, ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall

from agent.tools import AVAILABLE_TOOLS_DEEPEVAL
from utils.datadog_reporter import send_eval_score


# ── Canary: Tool Correctness ────────────────────────────────────────────────

@pytest.mark.canary
@pytest.mark.smoke
def test_canary_tool_correctness():
    """
    User asks for a product price (expected: lookup_product). Agent calls
    calculate_shipping_cost instead. A functioning tool correctness metric
    must score low.
    """
    metric = ToolCorrectnessMetric(
        available_tools=AVAILABLE_TOOLS_DEEPEVAL,
        threshold=0.7,
        should_exact_match=False,
        should_consider_ordering=False,
        model="gpt-4o-mini",
    )

    test_case = LLMTestCase(
        input="How much does the Sauce Labs Backpack cost?",
        actual_output=(
            "The standard shipping cost is free with a 5-7 business day "
            "delivery window."
        ),
        tools_called=[ToolCall(name="calculate_shipping_cost")],
        expected_tools=[ToolCall(name="lookup_product")],
    )

    try:
        metric.measure(test_case)
    finally:
        if metric.score is not None:
            send_eval_score(
                "llm.agent.canary.tool_correctness",
                metric.score,
                ["model:gpt-4o-mini"],
            )

    assert metric.score is not None, "Tool correctness metric returned no score"
    assert metric.score < 0.3, (
        f"Canary tool correctness: expected score < 0.3 for wrong tool called, "
        f"got {metric.score:.2f}"
    )


# ── Canary: Task Completion ─────────────────────────────────────────────────

@pytest.mark.canary
@pytest.mark.smoke
def test_canary_task_completion():
    """
    Task: look up the price of the Sauce Labs Backpack and tell the user.
    Agent output is a generic greeting with no price information.
    A functioning task completion metric must score low.
    """
    metric = TaskCompletionMetric(
        task=(
            "Look up the price of the Sauce Labs Backpack and provide it to "
            "the customer."
        ),
        threshold=0.7,
        model="gpt-4o-mini",
    )

    test_case = LLMTestCase(
        input="How much does the Sauce Labs Backpack cost?",
        actual_output=(
            "Hello! Welcome to Swag Labs. We're happy to help you today. "
            "Please let us know if you have any questions about our store. "
            "Have a great day!"
        ),
        tools_called=[],
    )

    try:
        metric.measure(test_case)
    finally:
        if metric.score is not None:
            send_eval_score(
                "llm.agent.canary.task_completion",
                metric.score,
                ["model:gpt-4o-mini"],
            )

    assert metric.score is not None, "Task completion metric returned no score"
    assert metric.score < 0.3, (
        f"Canary task completion: expected score < 0.3 for generic greeting "
        f"with no price, got {metric.score:.2f}"
    )
