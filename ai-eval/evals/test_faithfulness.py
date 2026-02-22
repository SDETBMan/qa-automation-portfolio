"""
test_faithfulness.py

Evaluates whether the RAG pipeline's answers are grounded in the retrieved
context — i.e., the model isn't inventing facts beyond what was provided.

Metric: GEval (custom faithfulness rubric)
  - GEval is DeepEval's flexible LLM-as-judge metric — it evaluates against
    a natural-language criteria string and returns a 0–10 score.
  - Used here instead of the built-in FaithfulnessMetric because the latter
    generates claim-by-claim structured JSON verdicts that exceed gpt-4o-mini's
    output token cap on longer FAQ chunks.
  - GEval produces a single concise score + reason, making it robust across
    all context sizes while measuring the same faithfulness contract.
  - Threshold: 0.7 (score ≥ 7/10 required to pass).
"""

import json
from pathlib import Path

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

DATASET_PATH = Path(__file__).parent.parent / "datasets" / "golden_dataset.json"
with open(DATASET_PATH) as f:
    _raw = json.load(f)

DATASET = [
    pytest.param(c, id=c["id"], marks=[getattr(pytest.mark, t) for t in c.get("tags", [])])
    for c in _raw
]

@pytest.mark.parametrize("case", DATASET)
def test_faithfulness(case, retriever, answer_generator):
    """
    Asserts the generated answer does not introduce facts beyond what the
    top-3 retrieved FAQ chunks contain. GEval scores 0–1 against the
    faithfulness rubric above; threshold 0.7 must be met to pass.

    GEval is instantiated here (not at module level) to avoid a collection-time
    DeepEvalError when the OpenAI API key is resolved from env at test runtime.
    """
    metric = GEval(
        name="Faithfulness",
        criteria=(
            "Evaluate whether the actual output is faithful to the retrieval context. "
            "The actual output should only contain information that is supported by the "
            "retrieval context. Penalize any claims that contradict or cannot be found "
            "in the retrieval context. Reward concise, accurate answers."
        ),
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT,
        ],
        threshold=0.7,
        model="gpt-4o-mini",
    )

    context = retriever(case["question"])
    actual_output = answer_generator(case["question"], context)

    test_case = LLMTestCase(
        input=case["question"],
        actual_output=actual_output,
        retrieval_context=context,
    )

    assert_test(test_case, [metric])
