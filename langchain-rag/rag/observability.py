"""Langfuse observability integration for LangChain RAG pipeline.

Provides trace-level visibility into:
  - LLM calls (model, tokens, latency, cost)
  - Retriever lookups (query, returned docs)
  - Chain composition (input/output at each step)

Gracefully returns None when Langfuse credentials are absent,
so the pipeline runs identically with or without tracing.
"""

from __future__ import annotations

import os


def get_langfuse_handler():
    """Return a Langfuse CallbackHandler if credentials are configured.

    Reads from environment variables (auto-loaded from .env by run.py):
      - LANGFUSE_SECRET_KEY
      - LANGFUSE_PUBLIC_KEY
      - LANGFUSE_HOST (defaults to https://cloud.langfuse.com)

    Returns None when keys are absent, allowing the chain to run
    without tracing.
    """
    secret = os.getenv("LANGFUSE_SECRET_KEY")
    public = os.getenv("LANGFUSE_PUBLIC_KEY")

    if not secret or not public:
        return None

    try:
        from langfuse.callback import CallbackHandler

        handler = CallbackHandler()
        return handler
    except ImportError:
        print("[WARN] langfuse not installed. Run: pip install langfuse")
        return None
    except Exception as exc:
        print(f"[WARN] Langfuse init failed: {exc}")
        return None
