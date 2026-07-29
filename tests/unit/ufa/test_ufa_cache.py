"""Tests for UFA cache layer."""

import time
import pytest
from ufa.cache import Cache, CacheManager


class TestCache:
    def test_set_get(self):
        c = Cache()
        c.set("key", "value")
        assert c.get("key") == "value"

    def test_missing_key(self):
        c = Cache()
        assert c.get("missing") is None

    def test_has(self):
        c = Cache()
        c.set("x", 1)
        assert c.has("x")
        assert not c.has("y")

    def test_delete(self):
        c = Cache()
        c.set("x", 1)
        assert c.delete("x")
        assert not c.has("x")

    def test_ttl_expiry(self):
        c = Cache()
        c.set("x", 1, ttl=0.01)
        time.sleep(0.02)
        assert c.get("x") is None

    def test_lru_eviction(self):
        c = Cache(max_size=2)
        c.set("a", 1)
        c.set("b", 2)
        c.set("c", 3)
        assert c.size() == 2

    def test_get_or_set(self):
        c = Cache()
        val = c.get_or_set("x", lambda: "computed")
        assert val == "computed"
        val2 = c.get_or_set("x", lambda: "other")
        assert val2 == "computed"

    def test_clear(self):
        c = Cache()
        c.set("a", 1)
        c.set("b", 2)
        count = c.clear()
        assert count == 2
        assert c.size() == 0

    def test_cleanup(self):
        c = Cache()
        c.set("a", 1, ttl=0.01)
        c.set("b", 2)
        time.sleep(0.02)
        removed = c.cleanup()
        assert removed == 1

    def test_keys(self):
        c = Cache()
        c.set("a", 1)
        c.set("b", 2)
        assert set(c.keys()) == {"a", "b"}

    def test_stats(self):
        c = Cache()
        c.set("x", 1)
        c.get("x")
        c.get("y")
        stats = c.stats
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_hit_count(self):
        c = Cache()
        c.set("x", 1)
        c.get("x")
        c.get("x")
        entry = c._entries["x"]
        assert entry.hit_count == 2


class TestCacheManager:
    def test_get_or_create(self):
        mgr = CacheManager()
        c = mgr.get_or_create("region1")
        c.set("a", 1)
        assert mgr.get("region1").get("a") == 1

    def test_regions(self):
        mgr = CacheManager()
        mgr.get_or_create("a")
        mgr.get_or_create("b")
        assert set(mgr.regions()) == {"a", "b"}

    def test_remove(self):
        mgr = CacheManager()
        mgr.get_or_create("x")
        assert mgr.remove("x")
        assert mgr.get("x") is None

    def test_clear_all(self):
        mgr = CacheManager()
        mgr.get_or_create("a").set("x", 1)
        mgr.get_or_create("b").set("y", 2)
        total = mgr.clear_all()
        assert total == 2

    def test_stats(self):
        mgr = CacheManager()
        mgr.get_or_create("a").set("x", 1)
        stats = mgr.stats()
        assert "a" in stats
