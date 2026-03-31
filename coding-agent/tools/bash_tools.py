"""Shell execution tool — run arbitrary commands and capture output.

SECURITY NOTE: run_bash executes arbitrary shell commands.  In production,
wrap this with an allowlist or sandboxed container.  For this portfolio demo,
it runs in the same process with the same permissions as the Python interpreter.
"""

import subprocess

from anthropic import beta_tool


@beta_tool
def run_bash(command: str, cwd: str = "", timeout: int = 60) -> str:
    """Execute a shell command and return combined stdout + stderr.

    Args:
        command: The shell command to run (passed to /bin/sh -c on Unix).
        cwd: Working directory for the command.  Defaults to current directory.
        timeout: Maximum seconds to wait before killing the process (default 60).
    """
    kwargs: dict = {
        "shell": True,
        "capture_output": True,
        "text": True,
        "timeout": timeout,
    }
    if cwd:
        kwargs["cwd"] = cwd

    try:
        result = subprocess.run(command, **kwargs)
        parts: list[str] = []
        if result.stdout.strip():
            parts.append(f"STDOUT:\n{result.stdout.rstrip()}")
        if result.stderr.strip():
            parts.append(f"STDERR:\n{result.stderr.rstrip()}")
        parts.append(f"EXIT CODE: {result.returncode}")
        return "\n\n".join(parts) or "(no output)"
    except subprocess.TimeoutExpired:
        return f"ERROR: command timed out after {timeout}s"
    except Exception as exc:
        return f"ERROR running command: {exc}"
