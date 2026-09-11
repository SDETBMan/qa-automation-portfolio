"""
conftest.py — Shared fixtures for stagehand-agent tests.

All tests run with mocked API calls — no Browserbase, no Anthropic,
no real browser needed.
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock

import pytest

from comparison.metrics import ScenarioResult


@pytest.fixture(autouse=True)
def _fake_env(monkeypatch):
    """Set fake environment variables for all tests."""
    monkeypatch.setenv("BROWSERBASE_API_KEY", "bb-test-key")
    monkeypatch.setenv("BROWSERBASE_PROJECT_ID", "proj_test")
    monkeypatch.setenv("MODEL_API_KEY", "sk-test-key")
    monkeypatch.setenv("BASE_URL", "https://www.saucedemo.com")
    # Ensure DataDog metrics are skipped
    monkeypatch.delenv("DD_API_KEY", raising=False)


@pytest.fixture
def mock_playwright_page():
    """A MagicMock that simulates a Playwright Page object."""
    page = MagicMock()
    page.url = "https://www.saucedemo.com/inventory.html"
    page.goto = MagicMock()

    # Default locator behavior
    locator = MagicMock()
    locator.click = MagicMock()
    locator.fill = MagicMock()
    locator.inner_text = MagicMock(return_value="")
    locator.all_inner_texts = MagicMock(return_value=[])
    locator.count = MagicMock(return_value=6)
    locator.is_visible = MagicMock(return_value=True)
    locator.wait_for = MagicMock()
    page.locator = MagicMock(return_value=locator)

    return page


@pytest.fixture
def mock_stagehand_client():
    """An AsyncMock that simulates a Stagehand client."""
    client = AsyncMock()

    # Session creation
    session = MagicMock()
    session.id = "test-session-123"
    client.sessions.create = AsyncMock(return_value=session)
    client.sessions.navigate = AsyncMock()

    # act() returns a result with no usage by default
    act_result = MagicMock()
    act_result.usage = None
    client.sessions.act = AsyncMock(return_value=act_result)

    # extract() returns a dict by default
    client.sessions.extract = AsyncMock(return_value={
        "logged_in": True,
        "current_url": "https://www.saucedemo.com/inventory.html",
        "error_message": None,
    })

    return client


@pytest.fixture
def sample_scenario_results():
    """A realistic set of scenario results for testing reporters."""
    return [
        ScenarioResult(
            scenario="login", approach="traditional",
            passed=True, duration_ms=1200.0,
        ),
        ScenarioResult(
            scenario="login", approach="ai-driven",
            passed=True, duration_ms=3500.0, tokens_used=150,
        ),
        ScenarioResult(
            scenario="inventory", approach="traditional",
            passed=True, duration_ms=800.0,
        ),
        ScenarioResult(
            scenario="inventory", approach="ai-driven",
            passed=True, duration_ms=4200.0, tokens_used=220,
        ),
        ScenarioResult(
            scenario="cart", approach="traditional",
            passed=True, duration_ms=950.0,
        ),
        ScenarioResult(
            scenario="cart", approach="ai-driven",
            passed=True, duration_ms=3800.0, tokens_used=180,
        ),
        ScenarioResult(
            scenario="checkout", approach="traditional",
            passed=True, duration_ms=2100.0,
        ),
        ScenarioResult(
            scenario="checkout", approach="ai-driven",
            passed=True, duration_ms=8500.0, tokens_used=450,
        ),
    ]
