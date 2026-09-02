"""MCP tool for read-only Postgres database inspection.

Provides safe, read-only SQL query execution with 5 guardrail layers:
  1. SQL keyword validation — only SELECT, WITH, EXPLAIN allowed
  2. DML/DDL blocking — 16 keywords blocked via word-boundary regex
  3. Multi-statement prevention — semicolons rejected
  4. Read-only transaction — connection.set_session(readonly=True)
  5. Row limit cap — clamped to [1, 1000], fetched via fetchmany()
"""

from __future__ import annotations

import json
import os
import re
import time

from utils.datadog_reporter import report_tool_call

# ── Guardrail constants ─────────────────────────────────────────────────────

_ALLOWED_FIRST_KEYWORDS = {"SELECT", "WITH", "EXPLAIN"}

_BLOCKED_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "GRANT", "REVOKE", "COMMIT", "ROLLBACK", "BEGIN",
    "SAVEPOINT", "COPY", "EXECUTE", "LOCK",
}

_BLOCKED_PATTERN = re.compile(
    r"\b(" + "|".join(_BLOCKED_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


# ── Validation ──────────────────────────────────────────────────────────────

def validate_query(query: str) -> None:
    """Apply all safety checks to a SQL query string.

    Raises ValueError with a descriptive message on any violation.
    """
    stripped = query.strip()
    if not stripped:
        raise ValueError("Empty query")

    # Layer 3: Multi-statement prevention
    # Remove quoted strings before checking for semicolons
    no_strings = re.sub(r"'[^']*'", "", stripped)
    if ";" in no_strings:
        raise ValueError(
            "Multi-statement queries are not allowed. "
            "Submit one query at a time."
        )

    # Strip comments for keyword analysis
    no_comments = re.sub(r"--[^\n]*", "", stripped)
    no_comments = re.sub(r"/\*.*?\*/", "", no_comments, flags=re.DOTALL)
    no_comments = no_comments.strip()

    if not no_comments:
        raise ValueError("Query contains only comments")

    # Layer 1: First keyword must be SELECT, WITH, or EXPLAIN
    first_word = no_comments.split()[0].upper()
    if first_word not in _ALLOWED_FIRST_KEYWORDS:
        raise ValueError(
            f"Only SELECT, WITH, and EXPLAIN queries are allowed. "
            f"Got: {first_word}"
        )

    # Layer 2: Block DML/DDL keywords anywhere in the query
    match = _BLOCKED_PATTERN.search(no_comments)
    if match:
        raise ValueError(
            f"Blocked keyword detected: {match.group(0).upper()}. "
            f"Only read-only queries are allowed."
        )


# ── Tool implementation ─────────────────────────────────────────────────────

async def inspect_db(
    query: str,
    row_limit: int = 100,
    timeout_seconds: int = 30,
) -> str:
    """Execute a read-only SQL query against a Postgres database.

    Five safety guardrails prevent any data modification:
    1. Only SELECT/WITH/EXPLAIN allowed as first keyword
    2. DML/DDL keywords (INSERT, UPDATE, DELETE, DROP, etc.) blocked
    3. Multi-statement queries (semicolons) rejected
    4. Connection set to read-only mode at the session level
    5. Row count capped at 1000

    Args:
        query: SQL SELECT query to execute.
        row_limit: Maximum rows to return (1-1000, default 100).
        timeout_seconds: Query timeout in seconds (1-120, default 30).

    Returns:
        JSON with columns, rows, row_count, truncated flag,
        and execution_time_ms.
    """
    start = time.time()
    error = None
    try:
        # Validate query against guardrails
        validate_query(query)

        # Clamp row_limit (Layer 5)
        row_limit = max(1, min(row_limit, 1000))
        timeout_seconds = max(1, min(timeout_seconds, 120))

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise EnvironmentError(
                "DATABASE_URL environment variable is not set. "
                "Set it to a PostgreSQL connection string: "
                "postgresql://user:pass@host:port/db"
            )

        import psycopg2

        conn = psycopg2.connect(database_url)
        try:
            # Layer 4: Read-only session
            conn.set_session(readonly=True, autocommit=True)

            with conn.cursor() as cur:
                # Set statement timeout
                cur.execute(
                    f"SET statement_timeout = '{timeout_seconds * 1000}'"
                )
                query_start = time.time()
                cur.execute(query)

                columns = [desc[0] for desc in cur.description] if cur.description else []
                rows = cur.fetchmany(row_limit + 1)  # Fetch one extra to detect truncation

                truncated = len(rows) > row_limit
                if truncated:
                    rows = rows[:row_limit]

                execution_time_ms = round((time.time() - query_start) * 1000, 2)

                # Convert rows to list of lists for JSON serialization
                serialized_rows = []
                for row in rows:
                    serialized_rows.append(
                        [str(v) if v is not None else None for v in row]
                    )

                output = {
                    "columns": columns,
                    "rows": serialized_rows,
                    "row_count": len(serialized_rows),
                    "truncated": truncated,
                    "execution_time_ms": execution_time_ms,
                }
                return json.dumps(output, indent=2)
        finally:
            conn.close()
    except Exception as exc:
        error = str(exc)
        raise
    finally:
        duration_ms = (time.time() - start) * 1000
        report_tool_call("inspect_db", duration_ms, error)
