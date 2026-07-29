"""cache — Caching layer with multiple backends.

Provides in-memory, LRU, TTL-based, and distributed cache abstractions.
"""

from __future__ import annotations

import enum
import threading
import time
from typing import Any, Callable, Dict, List, Optional


class CacheBackend(enum.IntEnum):
    MEMORY = 0
    LRU = 1
    TTL = 2


class CacheEntry:
    """A single cached value."""
    __slots__ = ("key", "value", "created_at", "expires_at", "hit_count")

    def __init__(self, key: str, value: Any,
                 ttl_sec: Optional[float] = None) -> None:
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.expires_at = (self.created_at + ttl_sec) if ttl_sec else None
        self.hit_count = 0

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    @property
    def age_sec(self) -> float:
        return time.time() - self.created_at


class Cache:
    """In-memory cache with TTL and LRU support."""

    def __init__(self, max_size: int = 1000,
                 default_ttl: Optional[float] = None) -> None:
        self._entries: Dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.Lock()
        self._hit_count = 0
        self._miss_count = 0

    def get(self, key: str) -> Optional[Any]:
        entry = self._entries.get(key)
        if entry is None:
            self._miss_count += 1
            return None
        if entry.is_expired:
            self._evict(key)
            self._miss_count += 1
            return None
        entry.hit_count += 1
        self._hit_count += 1
        return entry.value

    def set(self, key: str, value: Any,
            ttl: Optional[float] = None) -> None:
        with self._lock:
            if len(self._entries) >= self._max_size and key not in self._entries:
                self._evict_lru()
            ttl_sec = ttl if ttl is not None else self._default_ttl
            self._entries[key] = CacheEntry(key, value, ttl_sec)

    def has(self, key: str) -> bool:
        entry = self._entries.get(key)
        if entry is None:
            return False
        if entry.is_expired:
            self._evict(key)
            return False
        return True

    def delete(self, key: str) -> bool:
        return self._evict(key)

    def get_or_set(self, key: str, factory: Callable,
                   ttl: Optional[float] = None) -> Any:
        val = self.get(key)
        if val is not None:
            return val
        val = factory()
        self.set(key, val, ttl)
        return val

    def _evict(self, key: str) -> bool:
        with self._lock:
            if key in self._entries:
                del self._entries[key]
                return True
        return False

    def _evict_lru(self) -> None:
        if not self._entries:
            return
        lru_key = min(self._entries, key=lambda k: self._entries[k].hit_count)
        del self._entries[lru_key]

    def clear(self) -> int:
        with self._lock:
            count = len(self._entries)
            self._entries.clear()
            return count

    def cleanup(self) -> int:
        """Remove all expired entries. Returns count removed."""
        expired = [k for k, v in self._entries.items() if v.is_expired]
        for k in expired:
            self._evict(k)
        return len(expired)

    def keys(self) -> List[str]:
        return list(self._entries.keys())

    def size(self) -> int:
        return len(self._entries)

    @property
    def stats(self) -> Dict[str, int]:
        total = self._hit_count + self._miss_count
        return {
            "hits": self._hit_count,
            "misses": self._miss_count,
            "hit_rate": int(self._hit_count / total * 100) if total > 0 else 0,
            "size": len(self._entries),
            "max_size": self._max_size,
        }


class CacheManager:
    """Multi-cache manager supporting named cache regions."""

    def __init__(self) -> None:
        self._caches: Dict[str, Cache] = {}

    def get_or_create(self, name: str, max_size: int = 1000,
                      default_ttl: Optional[float] = None) -> Cache:
        if name not in self._caches:
            self._caches[name] = Cache(max_size, default_ttl)
        return self._caches[name]

    def get(self, name: str) -> Optional[Cache]:
        return self._caches.get(name)

    def remove(self, name: str) -> bool:
        if name in self._caches:
            del self._caches[name]
            return True
        return False

    def clear_all(self) -> int:
        total = 0
        for cache in self._caches.values():
            total += cache.clear()
        return total

    def cleanup_all(self) -> int:
        total = 0
        for cache in self._caches.values():
            total += cache.cleanup()
        return total

    def regions(self) -> List[str]:
        return list(self._caches.keys())

    def stats(self) -> Dict[str, Dict[str, int]]:
        return {name: cache.stats for name, cache in self._caches.items()}
