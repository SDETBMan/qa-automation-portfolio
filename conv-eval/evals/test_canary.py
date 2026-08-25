"""
test_canary.py — Canary (negative-control) tests for conv-eval metrics.

These tests feed known-bad conversations to each metric and assert the metric
fires (i.e. the score is bad). They validate the metrics themselves, not the
chatbot. If a DeepEval upgrade, model deprecation, or prompt tweak silently
degrades a metric, the canary will fail before any real eval test is affected.

Design principles:
  - All turns are hardcoded. No chatbot calls. Only the LLM judge (gpt-4o-mini)
    is called.
  - Inverted assertions: metric.measure() then assert the score lands in the
    "clearly bad" range. Wide margins absorb LLM judge non-determinism.
  - Dual markers: @canary + @smoke so canaries run on every push.

DataDog metrics:
  llm.conv.canary.knowledge_retention
  llm.conv.canary.role_adherence
  llm.conv.canary.turn_relevancy
"""

import pytest
from deepeval.metrics import (
    KnowledgeRetentionMetric,
    RoleAdherenceMetric,
    TurnRelevancyMetric,
)
from deepeval.test_case import ConversationalTestCase, Turn

from chatbot.swag_support_bot import CHATBOT_ROLE
from utils.datadog_reporter import send_eval_score


# ── Canary: Knowledge Retention ──────────────────────────────────────────────

@pytest.mark.canary
@pytest.mark.smoke
def test_canary_knowledge_retention():
    """
    User says they ordered the Sauce Labs Backpack at $29.99 with overnight
    shipping. Bot later contradicts every fact: wrong product, wrong price,
    wrong shipping tier, wrong delivery window. A functioning retention metric
    must score below the 0.7 pass threshold.
    """
    metric = KnowledgeRetentionMetric(threshold=0.7, model="gpt-4o-mini")

    test_case = ConversationalTestCase(
        turns=[
            Turn(
                role="user",
                content=(
                    "I just ordered the Sauce Labs Backpack for $29.99 with "
                    "overnight shipping. My order number is #12345."
                ),
            ),
            Turn(
                role="assistant",
                content=(
                    "I can confirm your order #12345 for the Sauce Labs Backpack "
                    "at $29.99 with overnight shipping. It will arrive within "
                    "1 business day."
                ),
            ),
            Turn(
                role="user",
                content="Can you repeat my order details?",
            ),
            Turn(
                role="assistant",
                content=(
                    "Sure! You ordered the Sauce Labs Fleece Jacket for $49.99 "
                    "with standard shipping. Your order number is #99999 and it "
                    "will arrive in 5-7 business days."
                ),
            ),
        ],
    )

    try:
        metric.measure(test_case)
    finally:
        if metric.score is not None:
            send_eval_score(
                "llm.conv.canary.knowledge_retention",
                metric.score,
                ["model:gpt-4o-mini"],
            )

    assert metric.score is not None, "Knowledge retention metric returned no score"
    assert metric.score < 0.7, (
        f"Canary knowledge retention: expected score < 0.7 for contradicted "
        f"product, price, shipping, and order number, got {metric.score:.2f}"
    )


# ── Canary: Role Adherence ───────────────────────────────────────────────────

@pytest.mark.canary
@pytest.mark.smoke
def test_canary_role_adherence():
    """
    User asks about Swag Labs products. Bot ignores its role and gives
    unsolicited medical advice. A functioning role adherence metric must
    score low.
    """
    metric = RoleAdherenceMetric(threshold=0.7, model="gpt-4o-mini")

    test_case = ConversationalTestCase(
        chatbot_role=CHATBOT_ROLE,
        turns=[
            Turn(
                role="user",
                content="What products do you have in stock?",
            ),
            Turn(
                role="assistant",
                content=(
                    "Based on your question, I think you might be experiencing "
                    "some health issues. I recommend taking 500mg of ibuprofen "
                    "twice daily and scheduling an appointment with your doctor. "
                    "Also, make sure to drink at least 8 glasses of water per day "
                    "and get 7-9 hours of sleep for optimal health."
                ),
            ),
            Turn(
                role="user",
                content="I asked about your products, not medical advice.",
            ),
            Turn(
                role="assistant",
                content=(
                    "I understand your frustration. Let me also recommend some "
                    "vitamins: Vitamin D3 5000 IU daily, and a B-complex "
                    "supplement. These will help with your energy levels. For "
                    "mental clarity, try meditation apps like Headspace."
                ),
            ),
        ],
    )

    try:
        metric.measure(test_case)
    finally:
        if metric.score is not None:
            send_eval_score(
                "llm.conv.canary.role_adherence",
                metric.score,
                ["model:gpt-4o-mini"],
            )

    assert metric.score is not None, "Role adherence metric returned no score"
    assert metric.score < 0.3, (
        f"Canary role adherence: expected score < 0.3 for completely "
        f"off-role medical advice, got {metric.score:.2f}"
    )


# ── Canary: Turn Relevancy ──────────────────────────────────────────────────

@pytest.mark.canary
@pytest.mark.smoke
def test_canary_turn_relevancy():
    """
    User asks about Swag Labs products. Bot discusses the weather in Paris.
    A functioning turn relevancy metric must score low.
    """
    metric = TurnRelevancyMetric(threshold=0.7, model="gpt-4o-mini")

    test_case = ConversationalTestCase(
        turns=[
            Turn(
                role="user",
                content="What are your most popular products?",
            ),
            Turn(
                role="assistant",
                content=(
                    "The weather in Paris today is partly cloudy with a high of "
                    "22 degrees Celsius. There's a 30% chance of rain in the "
                    "afternoon, so I'd recommend bringing an umbrella if you're "
                    "planning to visit the Eiffel Tower."
                ),
            ),
            Turn(
                role="user",
                content="I'm asking about your products, not the weather.",
            ),
            Turn(
                role="assistant",
                content=(
                    "Speaking of travel, the best time to visit Tokyo is during "
                    "cherry blossom season in late March to early April. The "
                    "blooms typically last about two weeks and draw millions of "
                    "tourists from around the world."
                ),
            ),
        ],
    )

    try:
        metric.measure(test_case)
    finally:
        if metric.score is not None:
            send_eval_score(
                "llm.conv.canary.turn_relevancy",
                metric.score,
                ["model:gpt-4o-mini"],
            )

    assert metric.score is not None, "Turn relevancy metric returned no score"
    assert metric.score < 0.3, (
        f"Canary turn relevancy: expected score < 0.3 for completely "
        f"off-topic responses, got {metric.score:.2f}"
    )
