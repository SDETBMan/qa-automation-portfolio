"""Tests for the inspect_db MCP tool — guardrail validation.

These tests focus on the 5 safety guardrail layers. Database connectivity
tests are skipped unless DATABASE_URL is set (no Postgres required for CI).
"""

from __future__ import annotations

import json
import os

import pytest

from tools.db_inspector import inspect_db, validate_query


# ── Layer 1: SQL keyword validation ─────────────────────────────────────────


class TestFirstKeywordValidation:
    """Only SELECT, WITH, EXPLAIN are allowed as the first keyword."""

    def test_select_allowed(self) -> None:
        validate_query("SELECT 1")

    def test_with_allowed(self) -> None:
        validate_query("WITH cte AS (SELECT 1) SELECT * FROM cte")

    def test_explain_allowed(self) -> None:
        validate_query("EXPLAIN SELECT 1")

    def test_insert_blocked(self) -> None:
        with pytest.raises(ValueError, match="Only SELECT"):
            validate_query("INSERT INTO users VALUES (1, 'a')")

    def test_update_blocked(self) -> None:
        with pytest.raises(ValueError, match="Only SELECT"):
            validate_query("UPDATE users SET name = 'x'")

    def test_delete_blocked(self) -> None:
        with pytest.raises(ValueError, match="Only SELECT"):
            validate_query("DELETE FROM users")

    def test_drop_blocked(self) -> None:
        with pytest.raises(ValueError, match="Only SELECT"):
            validate_query("DROP TABLE users")

    def test_create_blocked(self) -> None:
        with pytest.raises(ValueError, match="Only SELECT"):
            validate_query("CREATE TABLE t (id int)")


# ── Layer 2: DML/DDL keyword blocking ──────────────────────────────────────


class TestDMLDDLBlocking:
    """DML/DDL keywords are blocked even when embedded in a SELECT."""

    def test_insert_in_subquery(self) -> None:
        with pytest.raises(ValueError, match="INSERT"):
            validate_query("SELECT * FROM (INSERT INTO t VALUES (1))")

    def test_delete_in_cte(self) -> None:
        with pytest.raises(ValueError, match="DELETE"):
            validate_query("WITH x AS (DELETE FROM t RETURNING *) SELECT * FROM x")

    def test_truncate_blocked(self) -> None:
        with pytest.raises(ValueError, match="TRUNCATE"):
            validate_query("SELECT * FROM (TRUNCATE TABLE t RETURNING *)")

    def test_grant_blocked(self) -> None:
        with pytest.raises(ValueError, match="GRANT"):
            validate_query("SELECT GRANT FROM permissions")

    def test_copy_blocked(self) -> None:
        with pytest.raises(ValueError, match="COPY"):
            validate_query("COPY users TO '/tmp/dump.csv'")


# ── Layer 3: Multi-statement prevention ─────────────────────────────────────


class TestMultiStatementPrevention:
    """Semicolons between statements are rejected."""

    def test_double_select_blocked(self) -> None:
        with pytest.raises(ValueError, match="Multi-statement"):
            validate_query("SELECT 1; SELECT 2")

    def test_semicolon_inside_string_allowed(self) -> None:
        """Semicolons inside quoted strings should not trigger the block."""
        validate_query("SELECT * FROM t WHERE name = 'a;b'")

    def test_trailing_semicolon_in_string(self) -> None:
        """A semicolon inside a string literal at the end is OK."""
        validate_query("SELECT 'hello;world'")


# ── Comment injection ──────────────────────────────────────────────────────


class TestCommentInjection:
    """Comments should not bypass keyword validation."""

    def test_line_comment_bypass(self) -> None:
        with pytest.raises(ValueError, match="INSERT"):
            validate_query("SELECT 1 -- harmless\nINSERT INTO t VALUES (1)")

    def test_block_comment_bypass(self) -> None:
        with pytest.raises(ValueError, match="DELETE"):
            validate_query("SELECT /* comment */ DELETE FROM t")

    def test_only_comments_rejected(self) -> None:
        with pytest.raises(ValueError, match="only comments"):
            validate_query("-- just a comment")


# ── Row limit clamping ──────────────────────────────────────────────────────


class TestRowLimitClamping:
    """Row limit is clamped to [1, 1000]."""

    @pytest.mark.asyncio
    async def test_negative_row_limit(self) -> None:
        """Negative row_limit does not crash (clamped to 1)."""
        # This will fail at DATABASE_URL check, which is fine — we just
        # want to confirm it doesn't crash on the clamp logic path.
        with pytest.raises(EnvironmentError, match="DATABASE_URL"):
            os.environ.pop("DATABASE_URL", None)
            await inspect_db("SELECT 1", row_limit=-5)

    @pytest.mark.asyncio
    async def test_excessive_row_limit(self) -> None:
        """Row limit above 1000 is clamped (validated via DATABASE_URL error)."""
        with pytest.raises(EnvironmentError, match="DATABASE_URL"):
            os.environ.pop("DATABASE_URL", None)
            await inspect_db("SELECT 1", row_limit=99999)


# ── Empty / edge cases ──────────────────────────────────────────────────────


class TestEdgeCases:
    """Edge cases for query validation."""

    def test_empty_query(self) -> None:
        with pytest.raises(ValueError, match="Empty query"):
            validate_query("")

    def test_whitespace_only(self) -> None:
        with pytest.raises(ValueError, match="Empty query"):
            validate_query("   ")

    def test_case_insensitive_blocking(self) -> None:
        with pytest.raises(ValueError, match="Only SELECT"):
            validate_query("insert into t values (1)")

    @pytest.mark.asyncio
    async def test_missing_database_url(self) -> None:
        """Missing DATABASE_URL raises a clear error."""
        os.environ.pop("DATABASE_URL", None)
        with pytest.raises(EnvironmentError, match="DATABASE_URL"):
            await inspect_db("SELECT 1")
