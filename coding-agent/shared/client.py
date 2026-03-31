"""Shared Anthropic client and model constants."""

import os
from pathlib import Path

from anthropic import Anthropic

# claude-opus-4-6: 200K context, adaptive thinking, 128K max output
MODEL = "claude-opus-4-6"


def get_client() -> Anthropic:
    """Return a configured Anthropic client.

    Reads ANTHROPIC_API_KEY from the environment or a .env file in the
    coding-agent/ directory.
    """
    # Load .env from coding-agent/ if present
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is not set.\n"
            "Copy .env.example → .env and add your key, "
            "or export ANTHROPIC_API_KEY=<key>."
        )
    return Anthropic(api_key=api_key)


def get_repo_root() -> Path:
    """Return the absolute path to the monorepo root.

    Priority:
      1. REPO_ROOT environment variable
      2. Parent of the coding-agent/ directory (default)
    """
    env_root = os.environ.get("REPO_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return Path(__file__).parent.parent.parent.resolve()
