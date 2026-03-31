"""File system tools — read, write, list.

The @beta_tool decorator generates a JSON schema from the function signature
and docstring Args section.  The tool runner uses this schema when registering
the tool with Claude and calls the function automatically when Claude invokes it.
"""

from pathlib import Path

from anthropic import beta_tool


@beta_tool
def read_file(path: str) -> str:
    """Read the full text content of a file.

    Args:
        path: Absolute or relative path to the file.
    """
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"ERROR: file not found — {path}"
    except Exception as exc:
        return f"ERROR reading {path}: {exc}"


@beta_tool
def write_file(path: str, content: str) -> str:
    """Write text content to a file, creating parent directories if needed.

    Args:
        path: Absolute or relative path to write to.
        content: The full text content to write.
    """
    try:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} characters to {path}"
    except Exception as exc:
        return f"ERROR writing {path}: {exc}"


@beta_tool
def list_files(directory: str, pattern: str = "**/*") -> str:
    """List files in a directory that match a glob pattern.

    Args:
        directory: The directory to search.
        pattern: Glob pattern relative to directory (default: **/*).
    """
    try:
        base = Path(directory)
        if not base.exists():
            return f"ERROR: directory not found — {directory}"
        matches = sorted(p for p in base.glob(pattern) if p.is_file())
        if not matches:
            return "No files matched."
        return "\n".join(str(p.relative_to(base)) for p in matches)
    except Exception as exc:
        return f"ERROR listing {directory}: {exc}"
