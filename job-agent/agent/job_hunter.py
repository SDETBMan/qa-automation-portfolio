"""
job_hunter.py — Claude-powered agentic job search orchestrator.

JobHunter.run():
  1. Loads profile.md and injects it into the system prompt.
  2. Sends an initial user message to Claude with all 5 tool definitions.
  3. Drives an agentic tool-use loop (max 30 iterations):
       • Claude calls search_jobs() for each of 5 role types
       • Claude calls fetch_job_posting() on promising URLs
       • Claude calls score_job_fit() for each unique job
       • Claude filters to score >= 6, sorts by score
       • Claude calls draft_cover_letter() for top 5 matches
       • Claude calls save_results() with all findings
  4. Returns a final summary string when the loop ends.

score_job_fit and draft_cover_letter are handled *by Claude* (not by Python
implementations), so when the loop sees those tool names it asks Claude for the
answer rather than running local code.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import anthropic

from .tools import (
    TOOL_DEFINITIONS,
    fetch_job_posting,
    save_results,
    search_jobs,
)

_MODEL      = "claude-sonnet-4-6"
_MAX_ITER   = 30
_TEMP       = 0

# Roles to search — 5 queries, one per role type.
SEARCH_QUERIES = [
    "SDET remote job opening 2026",
    "Lead QA Engineer remote job opening 2026",
    "Quality Engineering Manager remote job 2026",
    "AI QA Engineer LLM testing remote 2026",
    "QA Automation Lead Selenium Playwright remote 2026",
]

_SYSTEM_TEMPLATE = """\
You are a job-search agent helping a senior QA engineer find their next role.
Your task is to search for relevant job postings, score each against the
candidate's profile, and draft tailored cover letters for the best matches.

## Candidate Profile
{profile}

## Instructions
1. Call search_jobs() for each of these queries (one call per query):
{queries}

2. For each unique job URL found, call fetch_job_posting() to get the full description.
   Deduplicate by URL — don't fetch the same URL twice.

3. Call score_job_fit() for every unique job. Provide the full job_description text.
   score_job_fit returns {{score, strengths, gaps, recommendation}}.
   Score 0-10 based on alignment with the candidate profile above.

4. Filter to jobs with score >= 6. Sort descending by score.

5. Call draft_cover_letter() for the top 5 scoring jobs (or fewer if < 5 found).
   Each letter should be personalised, reference specific experience from the profile,
   and be formatted as markdown.

6. Call save_results() ONCE with:
   - jobs_json: JSON array of ALL scored jobs (score >= 6), sorted by score descending.
     Each element: {{title, company, url, score, strengths, gaps, recommendation}}
   - cover_letters_json: JSON array of cover letters.
     Each element: {{company, title, letter}}

7. After save_results() returns, respond with a short plain-text summary of what was
   found and saved. This is the final output — do NOT call any more tools after this.
"""


class JobHunter:
    def __init__(self, role_filter: str | None = None) -> None:
        self.client      = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.role_filter = role_filter

    def _load_profile(self) -> str:
        profile_path = Path(__file__).parent.parent / "profile" / "profile.md"
        if not profile_path.exists():
            raise FileNotFoundError(
                f"profile.md not found at {profile_path}. "
                "Copy profile/profile.example.md → profile/profile.md and fill in your details."
            )
        return profile_path.read_text(encoding="utf-8")

    def _build_system(self, profile: str) -> str:
        queries = self.role_filter_queries()
        query_list = "\n".join(f"   - {q}" for q in queries)
        return _SYSTEM_TEMPLATE.format(profile=profile, queries=query_list)

    def role_filter_queries(self) -> list[str]:
        if not self.role_filter:
            return SEARCH_QUERIES
        term = self.role_filter.lower()
        filtered = [q for q in SEARCH_QUERIES if term in q.lower()]
        return filtered if filtered else SEARCH_QUERIES

    # ── Tool dispatcher ────────────────────────────────────────────────────────

    def _dispatch(self, tool_name: str, tool_input: dict) -> str:
        """
        Execute a tool call and return the result as a JSON string.

        score_job_fit and draft_cover_letter are fulfilled by Claude itself:
        we re-invoke the model with the tool inputs and let it generate the
        answer, then return that answer as the tool result.
        """
        if tool_name == "search_jobs":
            results = search_jobs(tool_input["query"])
            return json.dumps(results)

        if tool_name == "fetch_job_posting":
            text = fetch_job_posting(tool_input["url"])
            return text

        if tool_name in ("score_job_fit", "draft_cover_letter"):
            return self._claude_tool_response(tool_name, tool_input)

        if tool_name == "save_results":
            paths = save_results(
                tool_input["jobs_json"],
                tool_input["cover_letters_json"],
            )
            return json.dumps({"saved": paths})

        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    def _claude_tool_response(self, tool_name: str, tool_input: dict) -> str:
        """
        Ask Claude to fulfil score_job_fit or draft_cover_letter directly.
        Uses a focused one-shot call with the same profile context.
        """
        profile = self._load_profile()

        if tool_name == "score_job_fit":
            prompt = (
                f"Score how well this candidate fits the following job.\n\n"
                f"## Candidate Profile\n{profile}\n\n"
                f"## Job\nTitle: {tool_input['job_title']}\n"
                f"Company: {tool_input['company']}\n\n"
                f"Description:\n{tool_input['job_description']}\n\n"
                "Return ONLY a valid JSON object with keys: "
                "score (integer 0-10), strengths (array of strings), "
                "gaps (array of strings), recommendation (one of: apply, consider, skip)."
            )
        else:  # draft_cover_letter
            prompt = (
                f"Draft a tailored cover letter for this job.\n\n"
                f"## Candidate Profile\n{profile}\n\n"
                f"## Job\nTitle: {tool_input['job_title']}\n"
                f"Company: {tool_input['company']}\n\n"
                f"Description:\n{tool_input['job_description']}\n\n"
                "Return ONLY the cover letter as polished markdown (no extra commentary)."
            )

        resp = self.client.messages.create(
            model=_MODEL,
            max_tokens=1024,
            temperature=_TEMP,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text

    # ── Main agentic loop ──────────────────────────────────────────────────────

    def run(self) -> str:
        profile = self._load_profile()
        system  = self._build_system(profile)

        messages: list[dict] = [
            {
                "role": "user",
                "content": (
                    "Please run the full job search pipeline as described in your instructions. "
                    "Search all the specified queries, score every job you find, draft cover "
                    "letters for the top matches, and save everything. Then give me a summary."
                ),
            }
        ]

        print(f"[job-agent] Starting agentic loop (model={_MODEL}, max_iter={_MAX_ITER})")
        start = time.time()

        for iteration in range(_MAX_ITER):
            resp = self.client.messages.create(
                model=_MODEL,
                max_tokens=4096,
                temperature=_TEMP,
                system=system,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

            # Append assistant turn
            messages.append({"role": "assistant", "content": resp.content})

            stop_reason = resp.stop_reason
            print(f"[job-agent] iter={iteration + 1} stop_reason={stop_reason}")

            if stop_reason == "end_turn":
                # Extract final text
                final = next(
                    (b.text for b in resp.content if hasattr(b, "text")),
                    "Done.",
                )
                elapsed = time.time() - start
                print(f"[job-agent] Completed in {elapsed:.1f}s after {iteration + 1} iterations.")
                return final

            if stop_reason != "tool_use":
                print(f"[job-agent] Unexpected stop_reason={stop_reason}. Exiting loop.")
                break

            # Process all tool calls in this turn
            tool_results = []
            for block in resp.content:
                if block.type != "tool_use":
                    continue
                tool_name  = block.name
                tool_input = block.input
                tool_id    = block.id
                print(f"[job-agent]   tool_call: {tool_name}({list(tool_input.keys())})")

                try:
                    result_text = self._dispatch(tool_name, tool_input)
                except Exception as exc:  # noqa: BLE001
                    result_text = json.dumps({"error": str(exc)})
                    print(f"[job-agent]   ERROR in {tool_name}: {exc}")

                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": tool_id,
                    "content":     result_text,
                })

            messages.append({"role": "user", "content": tool_results})

        return "Job search loop ended (max iterations reached)."
