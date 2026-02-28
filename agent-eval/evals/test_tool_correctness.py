"""
test_tool_correctness.py

Evaluates whether the agent selects and calls the right tools for each query —
the primary correctness signal for function-calling AI systems.

Metric: ToolCorrectnessMetric
  - Compares tools_called (what the agent actually invoked) against
    expected_tools (what it should have invoked for this query).
  - should_exact_match=False: argument values are judged semantically, not
    literally — "Fleece Jacket" and "Sauce Labs Fleece Jacket" are equivalent.
  - should_consider_ordering=False: for multi-tool scenarios, order is not
    enforced — lookup_product before or after calculate_shipping_cost both pass.
  - available_tools: the full tool inventory lets the metric judge whether the
    agent also avoided calling irrelevant tools.
  - Threshold: 0.7 (70% correctness required to pass).

This is the key eval for agent reliability: an agent that generates plausible
text but calls the wrong tool (or no tool) is silently wrong in production.

DeepEval uses GPT-4o-mini as the LLM judge for scoring.
"""

import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, ToolCall

from agent.tools import AVAILABLE_TOOLS_DEEPEVAL
from utils.datadog_reporter import send_eval_score

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "agent_scenarios.json"
with open(DATASET_PATH) as f:
    _raw = json.load(f)

DATASET = [
    pytest.param(c, id=c["id"], marks=[getattr(pytest.mark, t) for t in c.get("tags", [])])
    for c in _raw
]


@pytest.mark.parametrize("case", DATASET)
def test_tool_correctness(case, agent):
    """
    Runs the agent on the scenario query, then asserts it called the expected
    tool(s) — the right ones, for the right reason, with sensible arguments.

    Pipeline:
      1. Run agent.run(query) → collects (final_response, tools_called).
      2. Build expected_tools list from the scenario's expected_tools field.
      3. Assert with ToolCorrectnessMetric.

    Multi-tool scenarios (e.g. agent_multi_product_and_shipping) verify that
    the agent correctly orchestrated two sequential tool calls rather than
    hallucinating an answer from a single call.
    """
    final_response, tools_called = agent.run(case["input"])

    expected_tools = [ToolCall(name=t["name"]) for t in case["expected_tools"]]

    test_case = LLMTestCase(
        input=case["input"],
        actual_output=final_response,
        tools_called=tools_called,
        expected_tools=expected_tools,
    )

    metric = ToolCorrectnessMetric(
        available_tools=AVAILABLE_TOOLS_DEEPEVAL,
        threshold=0.7,
        should_exact_match=False,
        should_consider_ordering=False,
        model="gpt-4o-mini",
    )

    try:
        assert_test(test_case, [metric])
    finally:
        if metric.score is not None:
            send_eval_score(
                "llm.agent.tool_correctness",
                metric.score,
                ["model:gpt-4o-mini", f"scenario:{case['id']}"],
            )
