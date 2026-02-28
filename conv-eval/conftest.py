"""
conftest.py — session and function-scoped fixtures for the conv-eval suite.

Setup order:
  1. Load .env → OPENAI_API_KEY
  2. Build OpenAI client (session-scoped — one client for the whole run)
  3. bot fixture (function-scoped) — fresh SwagSupportBot per test so each
     test starts with a clean conversation history
  4. conversations fixture (session-scoped) — loads the scenario dataset once

Key difference from ai-eval's conftest:
  ai-eval builds a stateless RAG pipeline (retriever + answer_generator).
  conv-eval builds a stateful chatbot (SwagSupportBot) that maintains message
  history across turns. The bot fixture is function-scoped (not session-scoped)
  so each parametrized test case gets isolated conversation state.

DataDog integration:
  - pytest_sessionstart records the session start time.
  - pytest_sessionfinish reads pass/fail/skip counts and posts suite-level
    metrics to DataDog. Skips silently if DD_API_KEY is not set.
"""

import json
import os
import time as _time
from pathlib import Path

import pytest
from dotenv import load_dotenv
from openai import OpenAI

from chatbot.swag_support_bot import SwagSupportBot
from utils import datadog_reporter

load_dotenv()

# ── DataDog session timing ─────────────────────────────────────────────────────

_session_start: float = 0.0


def pytest_sessionstart(session: pytest.Session) -> None:
    global _session_start
    _session_start = _time.time()


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    try:
        reporter = session.config.pluginmanager.get_plugin("terminalreporter")
        passed   = len(reporter.stats.get("passed",  []))
        failed   = len(reporter.stats.get("failed",  []))
        skipped  = len(reporter.stats.get("skipped", []))
        duration_ms = (_time.time() - _session_start) * 1000
        datadog_reporter.send_test_metrics(passed, failed, skipped, duration_ms, "conv-eval")
    except Exception as exc:
        print(f"[WARN] DataDog session finish hook failed: {exc}")


# ── OpenAI client ──────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.exit("OPENAI_API_KEY not set. Add it to conv-eval/.env and retry.", returncode=1)
    return OpenAI(api_key=api_key)


# ── Stateful chatbot — fresh instance per test ────────────────────────────────

@pytest.fixture
def bot(openai_client: OpenAI) -> SwagSupportBot:
    """
    Returns a fresh SwagSupportBot for each test.

    Function-scoped (default) so each parametrized scenario gets its own
    clean conversation history — tests cannot bleed state into one another.
    """
    return SwagSupportBot(openai_client)


# ── Conversation dataset ───────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def conversations() -> list[dict]:
    path = Path(__file__).parent / "datasets" / "conversations.json"
    with open(path) as f:
        return json.load(f)
