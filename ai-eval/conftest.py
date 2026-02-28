"""
conftest.py — session-scoped fixtures for the AI evaluation suite.

Setup order (once per pytest session):
  1. Load .env → OPENAI_API_KEY
  2. Build OpenAI client
  3. Embed FAQ chunks into an in-memory ChromaDB collection
  4. Expose retriever and answer_generator fixtures to all test files

DataDog integration:
  - pytest_sessionstart records the session start time.
  - pytest_sessionfinish reads pass/fail/skip counts from TerminalReporter and
    posts suite-level metrics to DataDog via datadog_reporter.send_test_metrics().
    Skips silently if DD_API_KEY is not set — CI stays green without it.
"""

import os
import json
import time as _time
from pathlib import Path

import pytest
import chromadb
from dotenv import load_dotenv
from openai import OpenAI

from rag.document import FAQ_CHUNKS
from utils import datadog_reporter

load_dotenv()

# ── DataDog session timing ─────────────────────────────────────────────────────

_session_start: float = 0.0


def pytest_sessionstart(session: pytest.Session) -> None:
    """Record session start time so pytest_sessionfinish can compute duration."""
    global _session_start
    _session_start = _time.time()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Send suite-level metrics to DataDog after all tests complete.

    Uses pytest's TerminalReporter plugin to read aggregate pass/fail/skip counts.
    No-op if DD_API_KEY is absent — CI stays green without the secret set.
    """
    try:
        reporter = session.config.pluginmanager.get_plugin("terminalreporter")
        passed  = len(reporter.stats.get("passed",  []))
        failed  = len(reporter.stats.get("failed",  []))
        skipped = len(reporter.stats.get("skipped", []))
        duration_ms = (_time.time() - _session_start) * 1000
        datadog_reporter.send_test_metrics(passed, failed, skipped, duration_ms, "ai-eval")
    except Exception as exc:
        print(f"[WARN] DataDog session finish hook failed: {exc}")


# ── OpenAI client ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.exit("OPENAI_API_KEY not set. Add it to ai-eval/.env and retry.", returncode=1)
    return OpenAI(api_key=api_key)


# ── ChromaDB — embed FAQ once per session ─────────────────────────────────────

@pytest.fixture(scope="session")
def chroma_collection(openai_client: OpenAI):
    """
    Embeds the SauceDemo FAQ document into an ephemeral (in-memory) ChromaDB
    collection using OpenAI's text-embedding-3-small model.
    This runs once per session — subsequent tests reuse the same collection.
    """
    client = chromadb.EphemeralClient()
    collection = client.create_collection("saucedemo_faq")

    for i, chunk in enumerate(FAQ_CHUNKS):
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=chunk,
        )
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[response.data[0].embedding],
            documents=[chunk],
        )

    return collection


# ── Retriever — semantic search over FAQ ──────────────────────────────────────

@pytest.fixture(scope="session")
def retriever(openai_client: OpenAI, chroma_collection):
    """
    Returns a callable that takes a query string and returns the top-k
    most relevant FAQ chunks as a list of strings.
    """
    def _retrieve(query: str, n_results: int = 3) -> list[str]:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query,
        )
        results = chroma_collection.query(
            query_embeddings=[response.data[0].embedding],
            n_results=n_results,
        )
        return results["documents"][0]

    return _retrieve


# ── Answer generator — RAG pipeline ──────────────────────────────────────────

@pytest.fixture(scope="session")
def answer_generator(openai_client: OpenAI):
    """
    Returns a callable that generates a GPT-4o-mini answer grounded in the
    provided context chunks — the core of the RAG pipeline under test.
    """
    def _generate(question: str, context: list[str]) -> str:
        context_text = "\n\n".join(context)
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful customer support assistant for Swag Labs. "
                        "Answer questions using ONLY the information provided below. "
                        "If the answer is not in the provided information, say so.\n\n"
                        f"{context_text}"
                    ),
                },
                {"role": "user", "content": question},
            ],
        )
        return response.choices[0].message.content

    return _generate


# ── Golden dataset ────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def golden_dataset() -> list[dict]:
    path = Path(__file__).parent / "datasets" / "golden_dataset.json"
    with open(path) as f:
        return json.load(f)
