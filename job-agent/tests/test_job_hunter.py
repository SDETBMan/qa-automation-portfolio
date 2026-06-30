"""
test_job_hunter.py — Unit tests for the JobHunter orchestrator.

Tests query filtering, system prompt construction, tool dispatch routing,
and the agentic loop with a fully mocked Anthropic client. No real API
calls are made.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from agent.job_hunter import SEARCH_QUERIES, JobHunter


# ── Helpers ──────────────────────────────────────────────────────────────────


def _make_hunter(profile_path: Path, role_filter: str | None = None) -> JobHunter:
    """Create a JobHunter with a patched profile path and mocked Anthropic client."""
    with patch("agent.job_hunter.anthropic.Anthropic"):
        hunter = JobHunter(role_filter=role_filter)
    # Patch _load_profile to read from the test fixture
    hunter._load_profile = lambda: profile_path.read_text(encoding="utf-8")
    return hunter


def _mock_end_turn_response(text: str = "Done. Found 2 jobs.") -> MagicMock:
    """Create a mock Anthropic response with stop_reason='end_turn'."""
    text_block = SimpleNamespace(type="text", text=text)
    resp = MagicMock()
    resp.stop_reason = "end_turn"
    resp.content = [text_block]
    return resp


def _mock_tool_use_response(tool_name: str, tool_input: dict, tool_id: str = "toolu_test") -> MagicMock:
    """Create a mock Anthropic response with stop_reason='tool_use'."""
    tool_block = SimpleNamespace(type="tool_use", name=tool_name, input=tool_input, id=tool_id)
    resp = MagicMock()
    resp.stop_reason = "tool_use"
    resp.content = [tool_block]
    return resp


# ── role_filter_queries ──────────────────────────────────────────────────────


@pytest.mark.smoke
def test_role_filter_narrows_queries(sample_profile):
    hunter = _make_hunter(sample_profile, role_filter="SDET")
    queries = hunter.role_filter_queries()
    assert len(queries) < len(SEARCH_QUERIES)
    assert all("sdet" in q.lower() for q in queries)


@pytest.mark.smoke
def test_role_filter_none_returns_all(sample_profile):
    hunter = _make_hunter(sample_profile, role_filter=None)
    queries = hunter.role_filter_queries()
    assert queries == SEARCH_QUERIES


@pytest.mark.smoke
def test_role_filter_no_match_falls_back(sample_profile):
    hunter = _make_hunter(sample_profile, role_filter="NonexistentRole")
    queries = hunter.role_filter_queries()
    assert queries == SEARCH_QUERIES


# ── _build_system ────────────────────────────────────────────────────────────


@pytest.mark.smoke
def test_build_system_includes_profile(sample_profile):
    hunter = _make_hunter(sample_profile)
    system = hunter._build_system(sample_profile.read_text())
    assert "Senior QA / SDET" in system
    assert "Selenium" in system


@pytest.mark.smoke
def test_build_system_includes_search_queries(sample_profile):
    hunter = _make_hunter(sample_profile)
    system = hunter._build_system(sample_profile.read_text())
    for query in SEARCH_QUERIES:
        assert query in system


# ── _dispatch routing ────────────────────────────────────────────────────────


@pytest.mark.smoke
def test_dispatch_routes_search_jobs(sample_profile):
    hunter = _make_hunter(sample_profile)
    with patch("agent.job_hunter.search_jobs", return_value=[{"title": "SDET"}]) as mock_search:
        result = hunter._dispatch("search_jobs", {"query": "test query"})
    mock_search.assert_called_once_with("test query")
    assert "SDET" in result


@pytest.mark.smoke
def test_dispatch_routes_fetch_job_posting(sample_profile):
    hunter = _make_hunter(sample_profile)
    with patch("agent.job_hunter.fetch_job_posting", return_value="Job description text") as mock_fetch:
        result = hunter._dispatch("fetch_job_posting", {"url": "https://example.com"})
    mock_fetch.assert_called_once_with("https://example.com")
    assert result == "Job description text"


@pytest.mark.smoke
def test_dispatch_routes_save_results(sample_profile):
    hunter = _make_hunter(sample_profile)
    with patch("agent.job_hunter.save_results", return_value=["/tmp/jobs.md"]) as mock_save:
        result = hunter._dispatch("save_results", {"jobs_json": "[]", "cover_letters_json": "[]"})
    mock_save.assert_called_once_with("[]", "[]")
    parsed = json.loads(result)
    assert "saved" in parsed


@pytest.mark.smoke
def test_dispatch_routes_claude_tools(sample_profile):
    """score_job_fit and draft_cover_letter are resolved by Claude, not local code."""
    hunter = _make_hunter(sample_profile)
    hunter._claude_tool_response = MagicMock(return_value='{"score": 8}')

    result = hunter._dispatch("score_job_fit", {
        "job_title": "SDET",
        "company": "Acme",
        "job_description": "Build test frameworks",
    })
    hunter._claude_tool_response.assert_called_once()
    assert "score" in result


@pytest.mark.smoke
def test_dispatch_unknown_tool(sample_profile):
    hunter = _make_hunter(sample_profile)
    result = hunter._dispatch("nonexistent_tool", {})
    parsed = json.loads(result)
    assert "error" in parsed
    assert "Unknown tool" in parsed["error"]


# ── Agentic loop ─────────────────────────────────────────────────────────────


@pytest.mark.smoke
def test_run_end_turn_returns_summary(sample_profile):
    """When Claude immediately returns end_turn, run() returns the text."""
    hunter = _make_hunter(sample_profile)
    mock_resp = _mock_end_turn_response("Found 3 jobs, saved results.")
    hunter._create_with_retry = MagicMock(return_value=mock_resp)

    summary = hunter.run()
    assert "Found 3 jobs" in summary


@pytest.mark.smoke
def test_run_processes_tool_calls(sample_profile):
    """The loop dispatches tool calls and feeds results back."""
    hunter = _make_hunter(sample_profile)

    # First response: Claude calls search_jobs
    tool_resp = _mock_tool_use_response("search_jobs", {"query": "SDET remote"})
    # Second response: Claude says end_turn with summary
    end_resp = _mock_end_turn_response("Search complete. 2 jobs found.")

    hunter._create_with_retry = MagicMock(side_effect=[tool_resp, end_resp])

    with patch("agent.job_hunter.search_jobs", return_value=[{"title": "SDET", "url": "https://example.com"}]):
        summary = hunter.run()

    assert hunter._create_with_retry.call_count == 2
    assert "Search complete" in summary


@pytest.mark.smoke
def test_run_handles_max_iterations(sample_profile):
    """If Claude never stops calling tools, run() exits after max iterations."""
    hunter = _make_hunter(sample_profile)

    # Always return a tool_use response (infinite loop scenario)
    tool_resp = _mock_tool_use_response("search_jobs", {"query": "test"})
    hunter._create_with_retry = MagicMock(return_value=tool_resp)

    with patch("agent.job_hunter.search_jobs", return_value=[]):
        # Patch _MAX_ITER to a small number for fast test
        with patch("agent.job_hunter._MAX_ITER", 3):
            summary = hunter.run()

    assert hunter._create_with_retry.call_count == 3
    assert "max iterations" in summary.lower()
