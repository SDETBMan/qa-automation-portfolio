"""
test_knowledge_retention.py

Evaluates whether the bot retains information shared earlier in a conversation
when answering follow-up questions — the core quality signal for conversational AI.

Metric: KnowledgeRetentionMetric
  - Detects whether the bot "forgets" facts that the user stated or that the bot
    itself stated in prior turns.
  - Covers three sub-scenarios that stress-test memory:
      • Implicit reference  — "it" / "that" resolves to a product from turn 1.
      • Self-correction     — the user amends the topic mid-conversation.
      • Multi-topic session — the bot must track context across topic switches.
  - Threshold: 0.7 (70% retention required to pass).
  - Runs only on "retention"-tagged scenarios to keep the smoke suite fast.

Note on DeepEval 3.x API:
  ConversationalTestCase now takes Turn(role, content) objects that interleave
  user and assistant messages — not LLMTestCase objects as in earlier versions.

DeepEval uses GPT-4o-mini as the LLM judge for scoring.
"""

import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import KnowledgeRetentionMetric
from deepeval.test_case import ConversationalTestCase, Turn

from utils.datadog_reporter import send_eval_score

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "conversations.json"
with open(DATASET_PATH) as f:
    _raw = json.load(f)

# Only scenarios that specifically exercise context carryover across turns.
DATASET = [
    pytest.param(c, id=c["id"], marks=[getattr(pytest.mark, t) for t in c.get("tags", [])])
    for c in _raw
    if "retention" in c.get("tags", [])
]


@pytest.mark.parametrize("case", DATASET)
def test_knowledge_retention(case, bot):
    """
    Drives the bot through all turns in the scenario, then asserts it retained
    information from earlier turns when answering later ones.

    KnowledgeRetentionMetric is instantiated inside the test (not at module
    level) to avoid a DeepEvalError when the OpenAI key is resolved at runtime.
    """
    metric = KnowledgeRetentionMetric(threshold=0.7, model="gpt-4o-mini")

    turns = []
    for turn in case["turns"]:
        response = bot.chat(turn["content"])
        turns.append(Turn(role="user", content=turn["content"]))
        turns.append(Turn(role="assistant", content=response))

    test_case = ConversationalTestCase(turns=turns)

    try:
        assert_test(test_case, [metric])
    finally:
        if metric.score is not None:
            send_eval_score(
                "llm.conv.knowledge_retention",
                metric.score,
                ["model:gpt-4o-mini", f"scenario:{case['id']}"],
            )
