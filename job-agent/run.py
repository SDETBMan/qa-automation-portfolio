#!/usr/bin/env python3
"""
run.py — CLI entry point for job-agent.

Usage:
    python run.py
    python run.py --role "SDET"        # narrow search to a role keyword

Environment variables (set in .env or shell):
    ANTHROPIC_API_KEY   required
    TAVILY_API_KEY      required
    DD_API_KEY          optional — DataDog metrics
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass  # dotenv is optional — env vars may already be set

try:
    import agentops as _agentops
    _AGENTOPS_AVAILABLE = True
except ImportError:
    _AGENTOPS_AVAILABLE = False


def _check_env() -> list[str]:
    """Return list of missing required env vars (empty list = all present)."""
    return [k for k in ("ANTHROPIC_API_KEY", "TAVILY_API_KEY") if not os.getenv(k)]


def main() -> None:
    parser = argparse.ArgumentParser(description="Claude-powered job search agent")
    parser.add_argument(
        "--role",
        default=os.getenv("ROLE_FILTER", ""),
        help="Optional role keyword to narrow search queries (e.g. 'SDET')",
    )
    args = parser.parse_args()

    missing = _check_env()
    if missing:
        print(f"[job-agent] Skipping run: missing environment variables: {', '.join(missing)}")
        print("            Add them to job-agent/.env or export them in your shell.")
        print("[job-agent] Exiting gracefully (exit 0).")
        return

    # Import here so dotenv is loaded first
    import anthropic
    from agent.job_hunter import JobHunter
    from utils.datadog_reporter import send_run_metrics, send_api_latency

    ao_key = os.getenv("AGENTOPS_API_KEY")
    ao_active = bool(_AGENTOPS_AVAILABLE and ao_key)
    if ao_active:
        _agentops.init(api_key=ao_key, default_tags=["job-agent"])

    role_filter = args.role.strip() or None
    hunter      = JobHunter(role_filter=role_filter)

    print()
    print("=" * 60)
    print("  job-agent — Claude-powered job search")
    if role_filter:
        print(f"  Role filter: {role_filter}")
    print("=" * 60)
    print()

    success = False
    elapsed_ms = 0.0
    summary = ""
    try:
        start = time.time()
        summary = hunter.run()
        elapsed_ms = (time.time() - start) * 1000
        success = True
    except anthropic.AuthenticationError:
        summary = "Anthropic API key is invalid or expired. No results produced."
        print(f"[job-agent] {summary}")
    except anthropic.RateLimitError:
        summary = "Anthropic API rate limit exceeded (quota may be exhausted). No results produced."
        print(f"[job-agent] {summary}")
    except anthropic.APIStatusError as exc:
        summary = f"Anthropic API error (HTTP {exc.status_code}). No results produced."
        print(f"[job-agent] {summary}")
    finally:
        if ao_active:
            _agentops.end_session("Success" if success else "Fail")

    print()
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(summary)
    print()

    # Count output files for DataDog metrics
    output_dir   = Path(__file__).parent / "output"
    jobs_files   = list(output_dir.glob("jobs_*.md"))
    letters_dir  = output_dir / "cover_letters"
    letter_files = list(letters_dir.glob("*.md")) if letters_dir.exists() else []

    if elapsed_ms > 0:
        send_api_latency(elapsed_ms)
    send_run_metrics(
        jobs_found=0,             # updated by save_results; approximate here
        jobs_scored=len(jobs_files),
        cover_letters_drafted=len(letter_files),
        duration_ms=elapsed_ms,
    )

    print(f"[job-agent] Output files in: {output_dir}")
    print()


if __name__ == "__main__":
    main()
