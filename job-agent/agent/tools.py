"""
tools.py — Anthropic tool-use definitions and implementations for job-agent.

Five tools:
  search_jobs(query)                          → list of {title, url, snippet, score}
  fetch_job_posting(url)                      → full posting text
  score_job_fit(job_title, company, job_desc) → {score, strengths, gaps, recommendation}
  draft_cover_letter(job_title, company, job_desc) → markdown cover letter string
  save_results(jobs_json, cover_letters_json) → list of file paths written

score_job_fit and draft_cover_letter are fulfilled by Claude inside the agentic loop
(the profile is in the system prompt), so their implementations here are stubs that
return a sentinel — the orchestrator never actually invokes them directly; Claude uses
them as tool calls that the loop resolves by letting Claude fill the answer.

search_jobs and fetch_job_posting call the Tavily API.
save_results writes files to output/.
"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

import requests

# ── Tavily helpers ─────────────────────────────────────────────────────────────

_TAVILY_BASE = "https://api.tavily.com"


def _tavily_key() -> str:
    key = os.getenv("TAVILY_API_KEY", "")
    if not key:
        raise EnvironmentError("TAVILY_API_KEY is not set.")
    return key


def search_jobs(query: str) -> list[dict]:
    """
    Search for job postings via Tavily.
    Returns a list of {title, url, snippet, score} dicts.
    """
    payload = {
        "api_key": _tavily_key(),
        "query": query,
        "search_depth": "basic",
        "include_answer": False,
        "max_results": 5,
    }
    resp = requests.post(f"{_TAVILY_BASE}/search", json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for r in data.get("results", []):
        results.append({
            "title":   r.get("title", ""),
            "url":     r.get("url", ""),
            "snippet": r.get("content", "")[:500],
            "score":   r.get("score", 0.0),
        })
    return results


def fetch_job_posting(url: str) -> str:
    """
    Fetch the full text of a job posting via Tavily extract.
    Returns raw text content (truncated to 4 000 chars to stay within context).
    """
    payload = {
        "api_key": _tavily_key(),
        "urls": [url],
    }
    resp = requests.post(f"{_TAVILY_BASE}/extract", json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results", [])
    if results:
        return results[0].get("raw_content", "")[:2000]
    return ""


def score_job_fit(job_title: str, company: str, job_description: str) -> dict:
    """
    Placeholder — fulfilled by Claude inside the agentic loop.
    Claude receives the profile via system prompt and scores the role.
    Returns structure: {score, strengths, gaps, recommendation}
    """
    raise NotImplementedError("score_job_fit is resolved by Claude in the agentic loop.")


def draft_cover_letter(job_title: str, company: str, job_description: str) -> str:
    """
    Placeholder — fulfilled by Claude inside the agentic loop.
    Claude receives the profile via system prompt and drafts the letter.
    Returns a markdown-formatted cover letter string.
    """
    raise NotImplementedError("draft_cover_letter is resolved by Claude in the agentic loop.")


def save_results(jobs_json: str, cover_letters_json: str) -> list[str]:
    """
    Persist job results and cover letters to output/.

    jobs_json         — JSON array of scored job objects
    cover_letters_json — JSON array of {company, title, letter} objects

    Returns list of file paths written.
    """
    base = Path(__file__).parent.parent / "output"
    base.mkdir(parents=True, exist_ok=True)
    letters_dir = base / "cover_letters"
    letters_dir.mkdir(exist_ok=True)

    written: list[str] = []
    today = date.today().isoformat()

    # ── Jobs report ────────────────────────────────────────────────────────────
    jobs: list[dict] = json.loads(jobs_json) if isinstance(jobs_json, str) else jobs_json
    jobs_path = base / f"jobs_{today}.md"
    with jobs_path.open("w", encoding="utf-8") as fh:
        fh.write(f"# Job Search Results — {today}\n\n")
        for i, job in enumerate(jobs, 1):
            score = job.get("score", "N/A")
            fh.write(f"## {i}. {job.get('title', 'Untitled')} @ {job.get('company', 'Unknown')}\n\n")
            fh.write(f"- **Fit score**: {score}/10\n")
            fh.write(f"- **URL**: {job.get('url', '')}\n")
            fh.write(f"- **Strengths**: {job.get('strengths', '')}\n")
            fh.write(f"- **Gaps**: {job.get('gaps', '')}\n")
            fh.write(f"- **Recommendation**: {job.get('recommendation', '')}\n\n")
    written.append(str(jobs_path))

    # ── Cover letters ──────────────────────────────────────────────────────────
    letters: list[dict] = (
        json.loads(cover_letters_json) if isinstance(cover_letters_json, str) else cover_letters_json
    )
    for item in letters:
        company = item.get("company", "Company").replace(" ", "_")
        title   = item.get("title", "Role").replace(" ", "_")
        safe    = f"{company}_{title}.md"
        path    = letters_dir / safe
        with path.open("w", encoding="utf-8") as fh:
            fh.write(item.get("letter", ""))
        written.append(str(path))

    return written


# ── Anthropic tool schemas ────────────────────────────────────────────────────

TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "search_jobs",
        "description": (
            "Search the web for job postings matching the given query. "
            "Returns a list of results with title, url, snippet, and relevance score."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Job search query, e.g. 'SDET remote job opening 2026'",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "fetch_job_posting",
        "description": (
            "Fetch the full text of a specific job posting URL. "
            "Use this to get detailed requirements before scoring."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full URL of the job posting to fetch.",
                }
            },
            "required": ["url"],
        },
    },
    {
        "name": "score_job_fit",
        "description": (
            "Score how well the candidate's profile matches a job posting. "
            "Returns a JSON object with: score (0-10), strengths (list), gaps (list), "
            "and recommendation (apply / consider / skip)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "job_title": {"type": "string", "description": "Job title as posted."},
                "company":   {"type": "string", "description": "Hiring company name."},
                "job_description": {
                    "type": "string",
                    "description": "Full or summarised job description text.",
                },
            },
            "required": ["job_title", "company", "job_description"],
        },
    },
    {
        "name": "draft_cover_letter",
        "description": (
            "Draft a tailored cover letter for the specified role. "
            "Returns a polished, markdown-formatted cover letter string."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "job_title": {"type": "string", "description": "Job title as posted."},
                "company":   {"type": "string", "description": "Hiring company name."},
                "job_description": {
                    "type": "string",
                    "description": "Full or summarised job description text.",
                },
            },
            "required": ["job_title", "company", "job_description"],
        },
    },
    {
        "name": "save_results",
        "description": (
            "Persist all job results and cover letters to disk. "
            "Call this once at the end of the run after all scoring and drafting is done."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "jobs_json": {
                    "type": "string",
                    "description": (
                        "JSON array string of scored job objects. Each object: "
                        "{title, company, url, score, strengths, gaps, recommendation}."
                    ),
                },
                "cover_letters_json": {
                    "type": "string",
                    "description": (
                        "JSON array string of cover letter objects. Each object: "
                        "{company, title, letter}."
                    ),
                },
            },
            "required": ["jobs_json", "cover_letters_json"],
        },
    },
]
