"""
test_conversation_relevancy.py

Evaluates whether every bot response across a conversation was relevant to
the user's message in that turn — regardless of memory or persona.

Metric: ConversationRelevancyMetric
  - Scores each turn's response against the corresponding user input.
  - A response that is factually correct but fails to address what the user
    actually asked in that turn will score low.
  - Threshold: 0.7 (70% relevancy required to pass).
  - Runs against all scenarios (smoke + regression) as a broad sanity check.

DeepEval uses GPT-4o-mini as the LLM judge for scoring.
"""

import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import ConversationRelevancyMetric
from deepeval.test_case import ConversationalTestCase, LLMTestCase

from utils.datadog_reporter import send_eval_score

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "conversations.json"
with open(DATASET_PATH) as f:
    _raw = json.load(f)

# All scenarios — relevancy is a baseline quality check for every conversation.
DATASET = [
    pytest.param(c, id=c["id"], marks=[getattr(pytest.mark, t) for t in c.get("tags", [])])
    for c in _raw
]


@pytest.mark.parametrize("case", DATASET)
def test_conversation_relevancy(case, bot):
    """
    Drives the bot through all turns in the scenario, then asserts that every
    response was relevant to the user message that prompted it.

    Pipeline:
      1. Run each user turn through the stateful bot, collecting (input, output) pairs.
      2. Build a ConversationalTestCase from those pairs.
      3. Assert with ConversationRelevancyMetric.
    """
    turns = []
    for turn in case["turns"]:
        response = bot.chat(turn["content"])
        turns.append(LLMTestCase(input=turn["content"], actual_output=response))

    test_case = ConversationalTestCase(turns=turns)
    metric = ConversationRelevancyMetric(threshold=0.7, model="gpt-4o-mini")

    try:
        assert_test(test_case, [metric])
    finally:
        if metric.score is not None:
            send_eval_score(
                "llm.conv.conversation_relevancy",
                metric.score,
                ["model:gpt-4o-mini", f"scenario:{case['id']}"],
            )
