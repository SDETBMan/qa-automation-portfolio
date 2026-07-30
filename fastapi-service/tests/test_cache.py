"""
test_cache.py -- 15 tests covering the Redis caching layer.

Classes:
  TestCacheHitMiss        (5)  products/users list + single item miss->hit, 404 not cached
  TestCacheInvalidation   (4)  POST/PUT/DELETE invalidate correct keys, cross-resource isolation
  TestCacheTTL            (1)  entry expires after TTL
  TestGracefulDegradation (3)  app works with _client=None, is_connected False, ops are no-ops
  TestCacheUtility        (2)  key prefix, flush removes all app keys
"""

import time

from app.cache import cache


# -- Hit / Miss ------------------------------------------------------------

class TestCacheHitMiss:
    """Verify cache-miss populates and cache-hit returns cached data."""

    def test_products_list_miss_then_hit(self, client):
        assert cache.hits == 0 and cache.misses == 0

        # First call: cache miss -- data comes from store.
        r1 = client.get("/products")
        assert r1.status_code == 200
        assert cache.misses == 1

        # Second call: cache hit.
        r2 = client.get("/products")
        assert r2.status_code == 200
        assert cache.hits == 1
        assert r1.json() == r2.json()

    def test_single_product_miss_then_hit(self, client):
        r1 = client.get("/products/1")
        assert r1.status_code == 200
        assert cache.misses == 1

        r2 = client.get("/products/1")
        assert r2.status_code == 200
        assert cache.hits == 1
        assert r1.json() == r2.json()

    def test_users_list_miss_then_hit(self, client):
        r1 = client.get("/users")
        assert r1.status_code == 200
        assert cache.misses == 1

        r2 = client.get("/users")
        assert r2.status_code == 200
        assert cache.hits == 1

    def test_single_user_miss_then_hit(self, client):
        r1 = client.get("/users/5")
        assert r1.status_code == 200
        assert cache.misses == 1

        r2 = client.get("/users/5")
        assert r2.status_code == 200
        assert cache.hits == 1

    def test_404_not_cached(self, client):
        """A 404 response must NOT be cached."""
        r1 = client.get("/products/9999")
        assert r1.status_code == 404

        # No cache hit recorded on the second 404.
        r2 = client.get("/products/9999")
        assert r2.status_code == 404
        assert cache.hits == 0


# -- Invalidation ----------------------------------------------------------

class TestCacheInvalidation:
    """Mutation endpoints must evict the affected cache keys."""

    def test_post_invalidates_list(self, client):
        # Warm the list cache.
        client.get("/products")
        assert cache.misses == 1

        # Create a product -- list cache should be gone.
        client.post("/products", json={"name": "New", "price": 1.0, "inventory": 1})
        r = client.get("/products")
        assert r.status_code == 200
        assert cache.misses == 2  # miss again, not a hit

    def test_put_invalidates_item_and_list(self, client):
        # Warm item and list caches.
        client.get("/products/1")
        client.get("/products")
        assert cache.misses == 2

        # Update product 1.
        client.put("/products/1", json={"name": "Updated", "price": 0.01, "inventory": 0})

        # Both should be misses now.
        client.get("/products/1")
        client.get("/products")
        assert cache.misses == 4

    def test_delete_invalidates_item_and_list(self, client):
        # Warm caches.
        client.get("/products/1")
        client.get("/products")

        # Delete product 1.
        r = client.delete("/products/1")
        assert r.status_code == 204

        # List is a miss (re-populated from store).
        client.get("/products")
        assert cache.misses == 3  # original 2 + 1 new miss

    def test_product_mutation_does_not_affect_user_cache(self, client):
        """User cache must survive product mutations (cross-resource isolation)."""
        client.get("/users")
        assert cache.misses == 1

        client.post("/products", json={"name": "X", "price": 1.0, "inventory": 0})

        # Users should still be a hit.
        client.get("/users")
        assert cache.hits == 1


# -- TTL -------------------------------------------------------------------

class TestCacheTTL:
    """Cache entry should expire after the configured TTL."""

    def test_entry_expires_after_ttl(self, client):
        # Manually set a key with a 1-second TTL.
        cache.set("products:list", [{"id": 1, "name": "t", "price": 1, "inventory": 0}], ttl=1)
        assert cache.get("products:list") is not None

        time.sleep(1.1)
        assert cache.get("products:list") is None


# -- Graceful degradation --------------------------------------------------

class TestGracefulDegradation:
    """The app must work when Redis is completely unavailable."""

    def test_endpoints_work_without_redis(self, client):
        cache._client = None  # simulate no Redis

        r = client.get("/products")
        assert r.status_code == 200
        assert len(r.json()) == 6

        r = client.get("/users/1")
        assert r.status_code == 200
        assert r.json()["username"] == "standard_user"

    def test_is_connected_returns_false(self):
        cache._client = None
        assert cache.is_connected() is False

    def test_operations_are_noops(self):
        cache._client = None
        assert cache.get("anything") is None
        assert cache.set("anything", "v") is False
        assert cache.delete("anything") is False
        assert cache.flush() is False


# -- Utility ---------------------------------------------------------------

class TestCacheUtility:
    """Key-prefix namespacing and flush behaviour."""

    def test_key_prefix(self):
        """All keys stored by Cache carry the ``fastapi:`` prefix."""
        cache.set("products:list", [])
        keys = list(cache._client.scan_iter("fastapi:*"))
        assert any("fastapi:products:list" in k for k in keys)

    def test_flush_removes_all_app_keys(self):
        cache.set("products:list", [])
        cache.set("users:list", [])
        cache.flush()
        assert cache.get("products:list") is None
        assert cache.get("users:list") is None
