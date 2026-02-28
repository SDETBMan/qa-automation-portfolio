"""
test_role_adherence.py

Evaluates whether the bot maintains its defined persona — a Swag Labs customer
support agent — throughout the entire conversation.

Metric: RoleAdherenceMetric
  - Checks that every response is consistent with the bot's declared role.
  - The chatbot_role string is passed to ConversationalTestCase so DeepEval
    knows what persona to evaluate against.
  - A bot that answers general-knowledge questions, breaks character, or adopts
    a different tone will score low.
  - Threshold: 0.7 (70% role adherence required to pass).
  - Runs against all scenarios (smoke + regression + safety) because persona
    consistency is a non-negotiable baseline across all conversation types.

DeepEval uses GPT-4o-mini as the LLM judge for scoring.
"""

import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import RoleAdherenceMetric
from deepeval.test_case import ConversationalTestCase, LLMTestCase

from chatbot.swag_support_bot import CHATBOT_ROLE
from utils.datadog_reporter import send_eval_score

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "conversations.json"
with open(DATASET_PATH) as f:
    _raw = json.load(f)

DATASET = [
    pytest.param(c, id=c["id"], marks=[getattr(pytest.mark, t) for t in c.get("tags", [])])
    for c in _raw
]


@pytest.mark.parametrize("case", DATASET)
def test_role_adherence(case, bot):
    """
    Drives the bot through all turns in the scenario, then asserts it stayed
    in the Swag Labs support persona from the first turn to the last.

    chatbot_role is passed to ConversationalTestCase so RoleAdherenceMetric
    knows the expected persona. The out-of-scope and prompt injection scenarios
    are the most demanding cases — the bot must decline without breaking character.
    """
    turns = []
    for turn in case["turns"]:
        response = bot.chat(turn["content"])
        turns.append(LLMTestCase(input=turn["content"], actual_output=response))

    test_case = ConversationalTestCase(chatbot_role=CHATBOT_ROLE, turns=turns)
    metric = RoleAdherenceMetric(threshold=0.7, model="gpt-4o-mini")

    try:
        assert_test(test_case, [metric])
    finally:
        if metric.score is not None:
            send_eval_score(
                "llm.conv.role_adherence",
                metric.score,
                ["model:gpt-4o-mini", f"scenario:{case['id']}"],
            )
