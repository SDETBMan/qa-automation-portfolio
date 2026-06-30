"""
conftest.py — Test fixtures for job-agent unit tests.

Provides mock Anthropic and Tavily responses so tests run without API keys.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure no real API calls happen during tests
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-fake-key")
os.environ.setdefault("TAVILY_API_KEY", "tvly-test-fake-key")


SAMPLE_PROFILE = """\
## Summary

Senior QA / SDET with 10 years of experience building test automation frameworks.

## Technical Skills

- **Languages**: Java, Python, TypeScript
- **Automation**: Selenium, Playwright, Cypress
- **AI / LLM**: DeepEval, Anthropic Claude, OpenAI

## Preferences

- **Job types**: SDET, QA Lead
- **Work style**: Remote preferred
- **Location**: Salt Lake City, UT
"""


SAMPLE_TAVILY_SEARCH_RESPONSE = {
    "results": [
        {
            "title": "Senior SDET — Acme Corp (Remote)",
            "url": "https://example.com/jobs/sdet-acme",
            "content": "Looking for an experienced SDET to build automation frameworks...",
            "score": 0.95,
        },
        {
            "title": "QA Lead — Widget Inc (Salt Lake City)",
            "url": "https://example.com/jobs/qa-lead-widget",
            "content": "Widget Inc seeks a QA Lead for their SLC office...",
            "score": 0.88,
        },
    ]
}


SAMPLE_TAVILY_EXTRACT_RESPONSE = {
    "results": [
        {
            "raw_content": (
                "Senior SDET — Acme Corp\n\n"
                "We are looking for a Senior SDET to join our engineering team. "
                "Requirements: 5+ years automation experience, Python, Selenium, CI/CD. "
                "Remote-friendly. Competitive salary and benefits."
            ),
        }
    ]
}


SAMPLE_JOBS_JSON = json.dumps([
    {
        "title": "Senior SDET",
        "company": "Acme Corp",
        "url": "https://example.com/jobs/sdet-acme",
        "score": 8,
        "strengths": ["Strong automation background", "Python expertise"],
        "gaps": ["No Go experience listed"],
        "recommendation": "apply",
    },
])


SAMPLE_COVER_LETTERS_JSON = json.dumps([
    {
        "company": "Acme Corp",
        "title": "Senior SDET",
        "letter": "# Cover Letter\n\nDear Hiring Manager,\n\n...",
    },
])


@pytest.fixture
def sample_profile(tmp_path: Path) -> Path:
    """Write a sample profile.md and return its path."""
    profile_dir = tmp_path / "profile"
    profile_dir.mkdir()
    profile_path = profile_dir / "profile.md"
    profile_path.write_text(SAMPLE_PROFILE, encoding="utf-8")
    return profile_path


@pytest.fixture
def mock_tavily_search():
    """Mock requests.post for Tavily search endpoint."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = SAMPLE_TAVILY_SEARCH_RESPONSE
    return mock_resp


@pytest.fixture
def mock_tavily_extract():
    """Mock requests.post for Tavily extract endpoint."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = SAMPLE_TAVILY_EXTRACT_RESPONSE
    return mock_resp
