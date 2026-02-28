"""
conftest.py — session and function-scoped fixtures for the agent-eval suite.

Setup order:
  1. Load .env → OPENAI_API_KEY
  2. Build OpenAI client (session-scoped)
  3. agent fixture (function-scoped, yield) — fresh SwagAgent per test so each
     scenario gets an isolated tool-call trace; teardown emits per-call latency
     and token usage to DataDog regardless of test outcome
  4. agent_scenarios (session-scoped) — loads the scenario dataset once

What makes agent-eval different from ai-eval and conv-eval:
  - The system under test uses OpenAI function calling to orchestrate tools
  - Each agent.run() call may make multiple API round-trips (one per tool-use
    iteration plus a final synthesis call)
  - call_stats accumulates one entry per API call, not per test, so a multi-tool
    scenario produces 3+ DataDog latency/token data points
"""

import json
import os
import time as _time
from pathlib import Path

import pytest
from dotenv import load_dotenv
from openai import OpenAI

from agent.swag_agent import SwagAgent
from utils import datadog_reporter

load_dotenv()

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
        datadog_reporter.send_test_metrics(passed, failed, skipped, duration_ms, "agent-eval")
    except Exception as exc:
        print(f"[WARN] DataDog session finish hook failed: {exc}")


@pytest.fixture(scope="session")
def openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.exit("OPENAI_API_KEY not set. Add it to agent-eval/.env and retry.", returncode=1)
    return OpenAI(api_key=api_key)


@pytest.fixture
def agent(openai_client: OpenAI):
    """
    Yields a fresh SwagAgent for each test, then emits per-call latency and
    token usage to DataDog after the test completes.

    Function-scoped so each scenario gets a clean tool-call trace. The teardown
    loops over call_stats (one entry per API round-trip in the agent loop) so
    multi-tool scenarios produce multiple data points per test.
    """
    instance = SwagAgent(openai_client)
    yield instance

    tags = ["model:gpt-4o-mini", "framework:agent-eval"]
    for stat in instance.call_stats:
        datadog_reporter.send_eval_score("llm.api.latency_ms", stat["latency_ms"], tags)
        if "total_tokens" in stat:
            datadog_reporter.send_eval_score("llm.api.prompt_tokens",     stat["prompt_tokens"],     tags)
            datadog_reporter.send_eval_score("llm.api.completion_tokens", stat["completion_tokens"], tags)
            datadog_reporter.send_eval_score("llm.api.total_tokens",      stat["total_tokens"],      tags)


@pytest.fixture(scope="session")
def agent_scenarios() -> list[dict]:
    path = Path(__file__).parent / "datasets" / "agent_scenarios.json"
    with open(path) as f:
        return json.load(f)
