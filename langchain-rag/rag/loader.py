"""Load .md and .feature files from the monorepo as LangChain Documents."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document


def _repo_root() -> Path:
    """Return the monorepo root (two levels above this file)."""
    return Path(__file__).resolve().parents[2]


def load_corpus(repo_root: Path | None = None) -> list[Document]:
    """Walk the monorepo and return Documents for every .md and .feature file.

    Each Document's metadata contains:
        source   — relative path from the repo root
        filetype — "markdown" or "feature"
    """
    root = repo_root or _repo_root()
    docs: list[Document] = []

    # Directories to skip (large / irrelevant)
    skip_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache"}

    for path in sorted(root.rglob("*")):
        # Skip hidden dirs and noisy dirs
        if any(part in skip_dirs for part in path.parts):
            continue
        if not path.is_file():
            continue

        suffix = path.suffix.lower()
        if suffix == ".md":
            filetype = "markdown"
        elif suffix == ".feature":
            filetype = "feature"
        else:
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore").strip()
        except OSError:
            continue

        if not content:
            continue

        rel = path.relative_to(root)
        docs.append(
            Document(
                page_content=content,
                metadata={"source": str(rel).replace("\\", "/"), "filetype": filetype},
            )
        )

    return docs
