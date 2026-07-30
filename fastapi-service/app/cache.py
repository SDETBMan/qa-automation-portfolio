"""
cache.py -- Redis caching layer for the FastAPI service.

Provides a read-through cache that sits between endpoints and the
in-memory store.  When Redis is unavailable the app works identically
to before -- every operation is a graceful no-op that logs a warning
instead of raising.

Cache key scheme:
  fastapi:products:list       GET /products
  fastapi:products:{id}       GET /products/{id}
  fastapi:users:list          GET /users
  fastapi:users:{id}          GET /users/{id}

TTL defaults to 300 s and is configurable via the REDIS_CACHE_TTL env var.
"""

from __future__ import annotations

import json
import os

import redis as _redis


_PREFIX = "fastapi:"
_DEFAULT_TTL = 300


class Cache:
    """Thin wrapper around a Redis client with graceful fallback."""

    def __init__(self, redis_client: _redis.Redis | None = ...) -> None:
        if redis_client is ...:
            # Production path: connect using REDIS_URL or skip.
            url = os.getenv("REDIS_URL")
            if url:
                try:
                    self._client: _redis.Redis | None = _redis.from_url(
                        url, decode_responses=True,
                    )
                    self._client.ping()
                except Exception:  # noqa: BLE001
                    print("[WARN] Redis not reachable; caching disabled.")
                    self._client = None
            else:
                self._client = None
        else:
            # Test / manual injection path.
            self._client = redis_client

        self._ttl = int(os.getenv("REDIS_CACHE_TTL", str(_DEFAULT_TTL)))
        self.hits: int = 0
        self.misses: int = 0

    # ── core operations ───────────────────────────────────────────────

    def get(self, key: str) -> str | None:
        """Return cached JSON string or None (miss / unavailable)."""
        if self._client is None:
            return None
        try:
            value = self._client.get(f"{_PREFIX}{key}")
            if value is not None:
                self.hits += 1
            else:
                self.misses += 1
            return value
        except Exception:  # noqa: BLE001
            print(f"[WARN] Cache GET failed for {key}")
            return None

    def set(self, key: str, value: object, ttl: int | None = None) -> bool:
        """Serialize *value* to JSON and store under *key*."""
        if self._client is None:
            return False
        try:
            self._client.set(
                f"{_PREFIX}{key}",
                json.dumps(value),
                ex=ttl or self._ttl,
            )
            return True
        except Exception:  # noqa: BLE001
            print(f"[WARN] Cache SET failed for {key}")
            return False

    def delete(self, key: str) -> bool:
        """Remove a single key."""
        if self._client is None:
            return False
        try:
            self._client.delete(f"{_PREFIX}{key}")
            return True
        except Exception:  # noqa: BLE001
            print(f"[WARN] Cache DELETE failed for {key}")
            return False

    def delete_pattern(self, pattern: str) -> bool:
        """Remove all keys matching *pattern* (e.g. ``products:*``)."""
        if self._client is None:
            return False
        try:
            cursor = 0
            while True:
                cursor, keys = self._client.scan(
                    cursor=cursor, match=f"{_PREFIX}{pattern}",
                )
                if keys:
                    self._client.delete(*keys)
                if cursor == 0:
                    break
            return True
        except Exception:  # noqa: BLE001
            print(f"[WARN] Cache DELETE_PATTERN failed for {pattern}")
            return False

    def flush(self) -> bool:
        """Remove all keys under the app prefix."""
        return self.delete_pattern("*")

    # ── health / diagnostics ──────────────────────────────────────────

    def is_connected(self) -> bool:
        if self._client is None:
            return False
        try:
            return self._client.ping()
        except Exception:  # noqa: BLE001
            return False

    def reset_counters(self) -> None:
        self.hits = 0
        self.misses = 0


cache = Cache()
