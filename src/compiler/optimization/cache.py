from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compiler.optimization.base import AnalysisResult


# ──────────────────────────────────────────────────────────────────────
# AnalysisCache
# ──────────────────────────────────────────────────────────────────────

class AnalysisCache:
    __slots__ = (
        "_cache",
        "_dependencies",
        "_reverse_deps",
        "_hits",
        "_misses",
        "_invalidations",
    )

    def __init__(self) -> None:
        self._cache: dict[str, AnalysisResult] = {}
        self._dependencies: dict[str, set[str]] = {}
        self._reverse_deps: dict[str, set[str]] = {}
        self._hits = 0
        self._misses = 0
        self._invalidations = 0

    # ── public API ──

    @property
    def dependencies(self) -> dict[str, set[str]]:
        return self._dependencies

    def get(self, name: str) -> AnalysisResult | None:
        result = self._cache.get(name)
        if result is not None:
            self._hits += 1
            return result
        self._misses += 1
        return None

    def put(self, name: str, result: AnalysisResult) -> None:
        self._cache[name] = result

    def is_valid(self, name: str) -> bool:
        return name in self._cache

    def invalidate(self, name: str) -> None:
        visited: set[str] = set()
        queue: deque[str] = deque()

        if name in self._cache:
            queue.append(name)

        for dependent in self._reverse_deps.get(name, set()):
            queue.append(dependent)

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            if current in self._cache:
                del self._cache[current]
                self._invalidations += 1

            for dependent in self._reverse_deps.get(current, set()):
                if dependent not in visited:
                    queue.append(dependent)

    def invalidate_all(self) -> None:
        count = len(self._cache)
        self._cache.clear()
        self._invalidations += count

    def register_dependency(self, analysis_name: str, depends_on: str) -> None:
        if analysis_name not in self._dependencies:
            self._dependencies[analysis_name] = set()
        self._dependencies[analysis_name].add(depends_on)

        if depends_on not in self._reverse_deps:
            self._reverse_deps[depends_on] = set()
        self._reverse_deps[depends_on].add(analysis_name)

    def stats(self) -> dict[str, int]:
        return {
            "hits": self._hits,
            "misses": self._misses,
            "invalidations": self._invalidations,
        }
