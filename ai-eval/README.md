[![ai-eval CI](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/ai-eval.yml/badge.svg)](https://github.com/SDETBMan/qa-automation-portfolio/actions/workflows/ai-eval.yml)

# ai-eval

A production-grade **LLM evaluation framework** built with **DeepEval + Pytest**, testing a RAG (Retrieval-Augmented Generation) pipeline grounded in the Swag Labs / SauceDemo knowledge base. Demonstrates how to apply automated quality gates to AI-generated answers. Covering: relevancy, faithfulness, hallucination, safety, and JSON schema correctness.

## Key Features

* **Ten DeepEval metrics:** `AnswerRelevancyMetric`, `FaithfulnessMetric`, `HallucinationMetric`, `HallucinationMetric` (aggregate benchmark), `ToxicityMetric` (safety), `BiasMetric` (bias), `JsonCorrectnessMetric`, `ContextualPrecisionMetric`, `ContextualRecallMetric`, `ContextualRelevancyMetric`: each with a configurable threshold and GPT-4o-mini as the LLM judge.
* **Full RAG pipeline under test:** ChromaDB (in-memory, ephemeral) + OpenAI `text-embedding-3-small` for semantic retrieval; GPT-4o-mini for answer generation. The entire pipeline is exercised end-to-end on every eval run.
* **Golden dataset:** `datasets/golden_dataset.json` contains ground-truth Q&A pairs covering the SauceDemo FAQ (products, checkout, shipping, returns, accounts). Each case carries `smoke` or `regression` tags consumed directly by pytest markers.
* **Pytest markers:** `smoke` (fast, push-safe), `regression` (full suite, nightly), `safety` (toxicity and bias), `retrieval` (contextual metrics). Filter with `-m smoke`, `-m regression`, or `-m retrieval`.
* **DataDog observability:** Suite-level pass/fail/skip/duration metrics plus per-call `llm.eval.*` scores and `llm.api.latency_ms` / token usage metrics sent on every assertion. Skips gracefully without `DD_API_KEY`.
* **Transient-failure resilience:** `pytest-rerunfailures` retries up to 5× with 60 s delay (`--reruns 5 --reruns-delay 60`) to tolerate transient OpenAI API timeouts in CI.

## Tech Stack

| Layer | Technology |
|---|---|
| LLM evaluation | DeepEval 1.0+ |
| LLM / judge | OpenAI GPT-4o-mini |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector store | ChromaDB (ephemeral, in-memory) |
| Test runner | Pytest 8+ |
| Observability | DataDog CI Visibility + custom GAUGE metrics |
| CI/CD | GitHub Actions |

## Test Coverage

| File | Metric | Threshold | What is evaluated |
|---|---|---|---|
| `test_answer_relevancy.py` | `AnswerRelevancyMetric` | 0.7 | Generated answer directly addresses the question, regardless of source |
| `test_faithfulness.py` | `FaithfulnessMetric` | 0.7 | Answer is grounded in retrieved context. No hallucinated claims |
| `test_hallucination.py` | `HallucinationMetric` | 0.3 | Answer does not contradict context (lower = more faithful) |
| `test_safety.py` | `ToxicityMetric` | 0.5 | Answer does not contain harmful, toxic, or inappropriate content |
| `test_bias.py` | `BiasMetric` | 0.5 | Answer does not contain gender, age, racial, or socioeconomic bias |
| `test_json_correctness.py` | `JsonCorrectnessMetric` | 0.9 | Answer matches expected Pydantic schema when structured output is requested |
| `test_hallucination_benchmark.py` | `HallucinationMetric` (aggregate) | 80% pass rate | Aggregate benchmark — all 10 cases run, sentinel test asserts >= 80% pass rate |
| `test_retrieval_quality.py` | `ContextualPrecisionMetric`, `ContextualRecallMetric`, `ContextualRelevancyMetric` | 0.7 | Retriever chunk relevance, coverage, and alignment — isolates retrieval quality from generator quality |

All eight test files are parametrized over the golden dataset or inline safety cases. The seven per-case files fail individually; the hallucination benchmark only fails at the aggregate level.

## How to Run

**Prerequisite:** [Python 3.11+](https://python.org) · `OPENAI_API_KEY` in `ai-eval/.env`

```bash
# Install dependencies
pip install -r requirements.txt

# Smoke tests (fast — subset of golden dataset)
pytest -m smoke -v

# Safety tests only
pytest -m safety -v

# Retrieval quality tests only
pytest -m retrieval -v

# Full regression suite
pytest -m regression -v

# All tests
pytest -v
```

> Copy `.env.example` to `.env` and add your `OPENAI_API_KEY` before running locally.

## CI/CD Pipeline

The `ai-eval.yml` workflow triggers on every push/PR to `main` that touches `ai-eval/**`, on a nightly schedule (`05:00 UTC`), and via `workflow_dispatch`.

**Manual dispatch input:**

| Input | Description |
|---|---|
| `marker` | pytest marker filter: `smoke`, `regression`, `safety`. Leave blank to run `smoke` (CI default). |

**Pipeline steps:**

1. Checkout code
2. Set up Python 3.11 with pip cache
3. `pip install -r requirements.txt`
4. Run pytest (`--reruns 5 --reruns-delay 60`, `DEEPEVAL_DISABLE_TIMEOUTS=true`)
5. Upload JUnit XML to DataDog CI Visibility (`if: always()`, `continue-on-error: true`)
6. Upload `.deepeval/` artifact (retained 30 days)

> **Secret required:** `OPENAI_API_KEY` must be set in repository secrets. `DD_API_KEY` (optional) enables DataDog CI Visibility and custom metrics.

## Project Structure

```
ai-eval/
├── datasets/
│   └── golden_dataset.json         # Ground-truth Q&A pairs with smoke/regression tags
├── evals/
│   ├── test_answer_relevancy.py    # AnswerRelevancyMetric (threshold 0.7)
│   ├── test_faithfulness.py        # FaithfulnessMetric (threshold 0.7)
│   ├── test_hallucination.py       # HallucinationMetric (threshold 0.3)
│   ├── test_safety.py              # ToxicityMetric (threshold 0.5)
│   ├── test_bias.py                # BiasMetric (threshold 0.5)
│   ├── test_json_correctness.py    # JsonCorrectnessMetric (threshold 0.9)
│   ├── test_hallucination_benchmark.py  # HallucinationMetric aggregate benchmark (80% pass rate)
│   └── test_retrieval_quality.py    # ContextualPrecision/Recall/Relevancy (threshold 0.7)
├── rag/
│   └── document.py                 # SauceDemo FAQ chunks (knowledge base)
├── utils/
│   └── datadog_reporter.py         # GAUGE metrics: test suite + per-eval scores
├── conftest.py                     # Session fixtures: OpenAI client · ChromaDB · retriever · answer_generator
├── pytest.ini                      # markers: smoke · regression · safety
└── requirements.txt
```

## DataDog Metrics

| Metric | Description |
|---|---|
| `test.suite.passed/failed/skipped` | Suite-level counts tagged `framework:ai-eval` |
| `test.suite.duration_ms` | Total session wall-clock duration |
| `llm.eval.answer_relevancy` | Per-case AnswerRelevancyMetric score (0–1) |
| `llm.eval.faithfulness` | Per-case FaithfulnessMetric score (0–1) |
| `llm.eval.hallucination` | Per-case HallucinationMetric score (0–1) |
| `llm.eval.safety` | Per-case ToxicityMetric safety score (0–1) |
| `llm.eval.bias` | Per-case BiasMetric bias score (0–1) |
| `llm.eval.json_correctness` | Per-case JsonCorrectnessMetric score (0–1) |
| `llm.eval.hallucination_benchmark.pass_rate` | Aggregate hallucination benchmark pass rate (0–100) |
| `llm.eval.hallucination_benchmark.mean_score` | Aggregate hallucination benchmark mean score (0–1) |
| `llm.eval.hallucination_benchmark.sample_count` | Number of cases in the hallucination benchmark run |
| `llm.eval.contextual_precision` | Per-case ContextualPrecisionMetric score (0–1) |
| `llm.eval.contextual_recall` | Per-case ContextualRecallMetric score (0–1) |
| `llm.eval.contextual_relevancy` | Per-case ContextualRelevancyMetric score (0–1) |
| `llm.api.latency_ms` | Per-call answer generation latency |
| `llm.api.prompt_tokens` | Per-call prompt token count |
| `llm.api.completion_tokens` | Per-call completion token count |
| `llm.api.total_tokens` | Per-call total token count |
