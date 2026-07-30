"""
conftest.py -- fixtures and DataDog hooks for the fastapi-service test suite.

Fixtures:
  reset_store (autouse, function-scoped) -- calls store.reset() before every test
      so each test starts with the seeded product/user data and a clean _next_id.
  _reset_cache (autouse, function-scoped) -- injects a fresh fakeredis instance
      before every test, flushes all keys, and resets hit/miss counters.
  client (function-scoped) -- httpx-backed TestClient for the FastAPI app.
      Zero external server or port needed; fully in-process.

DataDog hooks:
  pytest_sessionstart -- records wall-clock start time.
  pytest_sessionfinish -- posts pass/fail/skip/duration and cache hit/miss
      metrics tagged framework:fastapi-service. Skips silently if DD_API_KEY
      is absent.
"""

import time as _time

import fakeredis
import pytest
from fastapi.testclient import TestClient

from app.cache import cache
from app.main import app
from app.store import store
from utils import datadog_reporter

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
        datadog_reporter.send_test_metrics(passed, failed, skipped, duration_ms, "fastapi-service")
        datadog_reporter.send_cache_metrics(cache.hits, cache.misses, "fastapi-service")
    except Exception as exc:
        print(f"[WARN] DataDog session finish hook failed: {exc}")


@pytest.fixture(autouse=True)
def reset_store() -> None:
    """Reset in-memory store to seed data before every test."""
    store.reset()


@pytest.fixture(autouse=True)
def _reset_cache() -> None:
    """Inject a fresh fakeredis instance and reset counters before every test."""
    cache._client = fakeredis.FakeRedis(decode_responses=True)
    cache.flush()
    cache.reset_counters()


@pytest.fixture
def client() -> TestClient:
    """Return an httpx-backed TestClient for the FastAPI app."""
    with TestClient(app) as c:
        yield c
