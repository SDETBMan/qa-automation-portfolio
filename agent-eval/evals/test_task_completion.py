"""
test_task_completion.py

Evaluates whether the agent's final response actually accomplishes the user's
goal — the end-to-end quality signal that complements tool correctness.

Metric: TaskCompletionMetric
  - Judges whether actual_output successfully completes the task described in
    the `task` parameter.
  - An agent can call the right tool but still fail this metric if its final
    response is incomplete, incorrect, or doesn't address the user's question.
  - Threshold: 0.7 (70% task completion required to pass).

Relationship to ToolCorrectnessMetric:
  - ToolCorrectnessMetric asks: "Did it use the right tools?"
  - TaskCompletionMetric asks:  "Did it actually help the user?"
  Together they catch two distinct failure modes:
    • Wrong tool, but coherent response (tool correctness fails, task may pass)
    • Right tool, but garbled or incomplete synthesis (tool correctness passes, task fails)

DeepEval uses GPT-4o-mini as the LLM judge for scoring.
"""

import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import TaskCompletionMetric
from deepeval.test_case import LLMTestCase

from utils.datadog_reporter import send_eval_score

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "agent_scenarios.json"
with open(DATASET_PATH) as f:
    _raw = json.load(f)

DATASET = [
    pytest.param(c, id=c["id"], marks=[getattr(pytest.mark, t) for t in c.get("tags", [])])
    for c in _raw
]


@pytest.mark.parametrize("case", DATASET)
def test_task_completion(case, agent):
    """
    Runs the agent on the scenario query, then asserts the final response
    successfully accomplishes the stated task.

    The `task` field from the dataset is passed to TaskCompletionMetric as the
    ground-truth description of what the agent was supposed to achieve. The
    metric judges actual_output against that goal rather than against a fixed
    expected string — appropriate for non-deterministic LLM output.
    """
    final_response, tools_called = agent.run(case["input"])

    test_case = LLMTestCase(
        input=case["input"],
        actual_output=final_response,
        tools_called=tools_called,
    )

    metric = TaskCompletionMetric(
        task=case["task"],
        threshold=0.7,
        model="gpt-4o-mini",
    )

    try:
        assert_test(test_case, [metric])
    finally:
        if metric.score is not None:
            send_eval_score(
                "llm.agent.task_completion",
                metric.score,
                ["model:gpt-4o-mini", f"scenario:{case['id']}"],
            )
