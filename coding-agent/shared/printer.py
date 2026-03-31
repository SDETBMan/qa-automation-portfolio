"""Terminal output helpers for streaming agent messages."""

import json
from typing import Any


# ANSI colour codes — fall back to plain text in non-TTY environments
_CYAN   = "\033[36m"
_YELLOW = "\033[33m"
_GREEN  = "\033[32m"
_RED    = "\033[31m"
_GREY   = "\033[90m"
_BOLD   = "\033[1m"
_RESET  = "\033[0m"


def divider(title: str = "", width: int = 72) -> None:
    """Print a horizontal rule, optionally with a centred title."""
    if title:
        pad = (width - len(title) - 2) // 2
        print(f"\n{_BOLD}{'─' * pad} {title} {'─' * (width - pad - len(title) - 2)}{_RESET}")
    else:
        print(f"\n{'─' * width}")


def print_message(message: Any) -> None:
    """Pretty-print a single BetaMessage from the tool runner.

    Colour scheme:
      Cyan   → agent text / reasoning
      Yellow → tool call name + truncated input
      Grey   → stop_reason
    """
    for block in message.content:
        if block.type == "text" and block.text.strip():
            print(f"\n{_CYAN}[AGENT]{_RESET} {block.text}")
        elif block.type == "tool_use":
            print(f"\n{_YELLOW}[TOOL → {block.name}]{_RESET}")
            if block.input:
                raw = json.dumps(block.input, indent=2)
                # Keep output scannable — truncate after 400 chars
                if len(raw) > 400:
                    raw = raw[:397] + "..."
                # Indent each line for readability
                for line in raw.splitlines():
                    print(f"  {line}")

    if getattr(message, "stop_reason", None):
        print(f"\n{_GREY}[stop_reason: {message.stop_reason}]{_RESET}")


def print_section(label: str, content: str, colour: str = _GREEN) -> None:
    """Print a named output section (plan, result, etc.)."""
    divider(label)
    print(f"{colour}{content}{_RESET}")
    divider()


def print_error(message: str) -> None:
    print(f"\n{_RED}[ERROR]{_RESET} {message}")


def print_success(message: str) -> None:
    print(f"\n{_GREEN}[SUCCESS]{_RESET} {message}")
