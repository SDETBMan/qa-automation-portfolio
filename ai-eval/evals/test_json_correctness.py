"""
test_json_correctness.py

Evaluates whether the RAG pipeline can produce structured, schema-conformant
JSON output — a critical capability when AI responses feed downstream services,
APIs, or UI components rather than being displayed directly to a user.

Metric: JsonCorrectnessMetric
  - Validates that actual_output deserializes cleanly into the expected Pydantic
    schema: correct field names, correct types, no missing required fields.
  - Binary pass/fail (score 1.0 or 0.0) — the JSON either conforms or it doesn't.
  - strict_mode=True enforces threshold=1.0: any schema violation fails the test.
  - When the output is invalid, DeepEval uses GPT-4o-mini to explain why it
    failed (missing field, wrong type, unexpected structure, etc.).

Design:
  A dedicated JSON generator is used here instead of the session-scoped
  answer_generator fixture. It passes response_format="json_object" to
  OpenAI, ensuring the model outputs raw JSON rather than prose with embedded
  JSON, and instructs it explicitly to match the requested field names.
  This isolates the evaluation to schema conformance, not natural language quality.

Each test case represents a realistic downstream use — the kind of structured
output a UI component, webhook, or data pipeline would consume.
"""

import time as _time
from typing import Optional

import pytest
from pydantic import BaseModel
from deepeval import assert_test
from deepeval.metrics import JsonCorrectnessMetric
from deepeval.test_case import LLMTestCase

from rag.document import FAQ_CHUNKS
from utils.datadog_reporter import send_eval_score

_CONTEXT = "\n\n".join(FAQ_CHUNKS)


# ── Expected output schemas ───────────────────────────────────────────────────

class ReturnEligibilitySchema(BaseModel):
    """Structured return eligibility check — consumed by a returns portal UI."""
    product_name: str
    eligible_for_return: bool
    policy_window_days: int
    receipt_required: bool
    next_steps: str


class ProductSummarySchema(BaseModel):
    """Structured product detail — consumed by a product card API endpoint."""
    product_name: str
    price_usd: float
    sku: str
    description: str


class ShippingOptionsSchema(BaseModel):
    """Structured shipping options — consumed by a checkout cost estimator."""
    standard_days: str
    standard_cost: str
    expedited_days: str
    expedited_cost: str
    overnight_cost: str


# ── Test cases ────────────────────────────────────────────────────────────────

JSON_CASES = [
    {
        "id": "json_return_eligibility",
        "prompt": (
            "Is the Sauce Labs Backpack eligible for return? "
            "Respond in JSON with exactly these fields: product_name, "
            "eligible_for_return, policy_window_days, receipt_required, next_steps."
        ),
        "schema": ReturnEligibilitySchema,
        "tags": ["smoke"],
    },
    {
        "id": "json_product_summary",
        "prompt": (
            "Give me details on the Sauce Labs Fleece Jacket. "
            "Respond in JSON with exactly these fields: product_name, "
            "price_usd, sku, description."
        ),
        "schema": ProductSummarySchema,
        "tags": ["smoke"],
    },
    {
        "id": "json_shipping_options",
        "prompt": (
            "What are the shipping options at Swag Labs? "
            "Respond in JSON with exactly these fields: standard_days, "
            "standard_cost, expedited_days, expedited_cost, overnight_cost."
        ),
        "schema": ShippingOptionsSchema,
        "tags": ["regression"],
    },
]

DATASET = [
    pytest.param(c, id=c["id"], marks=[getattr(pytest.mark, t) for t in c.get("tags", [])])
    for c in JSON_CASES
]


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("case", DATASET)
def test_json_correctness(case, openai_client):
    """
    Asks the RAG pipeline to produce a structured JSON response and asserts
    it conforms to the expected Pydantic schema.

    Uses OpenAI's response_format="json_object" to guarantee raw JSON output,
    then validates field names and types with JsonCorrectnessMetric.
    strict_mode=True means a single missing or mistyped field fails the test.
    """
    t0 = _time.time()
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Swag Labs customer support assistant. "
                    "Answer questions using ONLY the information below. "
                    "Always respond with valid JSON only — no prose, no markdown.\n\n"
                    f"{_CONTEXT}"
                ),
            },
            {"role": "user", "content": case["prompt"]},
        ],
    )
    latency_ms = (_time.time() - t0) * 1000
    actual_output = response.choices[0].message.content

    tags = ["model:gpt-4o-mini", "framework:ai-eval"]
    send_eval_score("llm.api.latency_ms", latency_ms, tags)
    if response.usage:
        send_eval_score("llm.api.prompt_tokens",     response.usage.prompt_tokens,     tags)
        send_eval_score("llm.api.completion_tokens", response.usage.completion_tokens, tags)
        send_eval_score("llm.api.total_tokens",      response.usage.total_tokens,      tags)

    test_case = LLMTestCase(
        input=case["prompt"],
        actual_output=actual_output,
    )

    metric = JsonCorrectnessMetric(
        expected_schema=case["schema"],
        model="gpt-4o-mini",
        strict_mode=True,
    )

    try:
        assert_test(test_case, [metric])
    finally:
        if metric.score is not None:
            send_eval_score(
                "llm.eval.json_correctness",
                metric.score,
                ["model:gpt-4o-mini", f"schema:{case['schema'].__name__}"],
            )
