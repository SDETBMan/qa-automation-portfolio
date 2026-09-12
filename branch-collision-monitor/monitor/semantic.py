"""
semantic.py — Claude-powered semantic diff analysis.

Optional module: requires ANTHROPIC_API_KEY to be set.
Gracefully skipped when the key is absent.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .analyzer import SemanticOverlap


def _get_client():
    """Return a configured Anthropic client, or None if unavailable."""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            pass

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        from anthropic import Anthropic
        return Anthropic(api_key=api_key)
    except ImportError:
        print("[WARN] anthropic package not installed. Skipping semantic analysis.")
        return None


_SYSTEM = """\
You are a senior software engineer analyzing two diffs that modify the same file \
from different branches. Determine whether these changes are likely to cause a \
merge conflict or logical inconsistency.

Respond with ONLY valid JSON (no markdown fences) in this exact schema:
{
  "conflict_likelihood": "high" | "medium" | "low" | "none",
  "explanation": "<1-2 sentence explanation>",
  "functions_affected": ["<function or section names that overlap>"]
}
"""


def analyze_pair(
    client,
    file_path: str,
    branch_a: str,
    diff_a: str,
    branch_b: str,
    diff_b: str,
) -> SemanticOverlap:
    """Ask Claude to assess conflict likelihood between two diffs on the same file."""
    user_prompt = (
        f"File: {file_path}\n\n"
        f"--- Branch: {branch_a} ---\n{diff_a[:3000]}\n\n"
        f"--- Branch: {branch_b} ---\n{diff_b[:3000]}"
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20250514",
            max_tokens=512,
            system=_SYSTEM,
            messages=[{"role": "user", "content": user_prompt}],
        )

        text = response.content[0].text.strip()
        data = json.loads(text)

        return SemanticOverlap(
            file_path=file_path,
            branch_a=branch_a,
            branch_b=branch_b,
            conflict_likelihood=data.get("conflict_likelihood", "none"),
            explanation=data.get("explanation", ""),
            functions_affected=data.get("functions_affected", []),
        )

    except (json.JSONDecodeError, Exception) as exc:
        print(f"[WARN] Semantic analysis failed for {file_path}: {exc}")
        return SemanticOverlap(
            file_path=file_path,
            branch_a=branch_a,
            branch_b=branch_b,
            conflict_likelihood="none",
            explanation=f"Analysis failed: {exc}",
        )


def run_semantic_analysis(
    overlapping_files: list[dict],
    max_calls: int = 10,
) -> list[SemanticOverlap]:
    """Run semantic analysis on overlapping files.

    Args:
        overlapping_files: List of dicts with keys:
            file_path, branch_a, diff_a, branch_b, diff_b
        max_calls: Maximum number of API calls to make.

    Returns:
        List of SemanticOverlap results.
    """
    client = _get_client()
    if client is None:
        print("[INFO] ANTHROPIC_API_KEY not set. Skipping semantic analysis.")
        return []

    results: list[SemanticOverlap] = []
    for i, item in enumerate(overlapping_files[:max_calls]):
        print(f"[INFO] Semantic analysis {i + 1}/{min(len(overlapping_files), max_calls)}: {item['file_path']}")
        result = analyze_pair(
            client=client,
            file_path=item["file_path"],
            branch_a=item["branch_a"],
            diff_a=item["diff_a"],
            branch_b=item["branch_b"],
            diff_b=item["diff_b"],
        )
        results.append(result)

    return results
