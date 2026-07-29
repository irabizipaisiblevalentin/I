from __future__ import annotations

from enum import IntEnum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from compiler.ir.module import IRModule
    from compiler.optimization.cache import AnalysisCache
    from compiler.optimization.stats import StatisticsEngine


# ──────────────────────────────────────────────────────────────────────
# OptimizationLevel
# ──────────────────────────────────────────────────────────────────────

class OptimizationLevel(IntEnum):
    O0 = auto()
    O1 = auto()
    O2 = auto()
    O3 = auto()
    OS = auto()
    OZ = auto()
    OFAST = auto()


# ──────────────────────────────────────────────────────────────────────
# OptimizationContext
# ──────────────────────────────────────────────────────────────────────

class OptimizationContext:
    __slots__ = (
        "_module",
        "_level",
        "_stats",
        "_cache",
        "_options",
        "_pass_count",
        "_iteration",
        "_max_iterations",
        "_changed",
    )

    def __init__(
        self,
        module: IRModule,
        level: OptimizationLevel = OptimizationLevel.O2,
        stats: StatisticsEngine | None = None,
        cache: AnalysisCache | None = None,
    ) -> None:
        self._module = module
        self._level = level
        self._stats = stats
        self._cache = cache
        self._options: dict[str, Any] = {}
        self._pass_count = 0
        self._iteration = 0
        self._max_iterations = 4
        self._changed = False

    @property
    def module(self) -> IRModule:
        return self._module

    @property
    def level(self) -> OptimizationLevel:
        return self._level

    @property
    def stats(self) -> StatisticsEngine:
        return self._stats

    @property
    def cache(self) -> AnalysisCache:
        return self._cache

    @property
    def pass_count(self) -> int:
        return self._pass_count

    @property
    def iteration(self) -> int:
        return self._iteration

    @property
    def max_iterations(self) -> int:
        return self._max_iterations

    @property
    def changed(self) -> bool:
        return self._changed

    def increment_pass_count(self) -> None:
        self._pass_count += 1

    def set_iteration(self, n: int) -> None:
        self._iteration = n

    def mark_changed(self) -> None:
        self._changed = True

    def reset_changed(self) -> None:
        self._changed = False

    def get_option(self, key: str, default: Any = None) -> Any:
        return self._options.get(key, default)

    def set_option(self, key: str, value: Any) -> None:
        self._options[key] = value

    def clone_for(self, module: IRModule) -> OptimizationContext:
        ctx = OptimizationContext(
            module=module,
            level=self._level,
            stats=self._stats,
            cache=self._cache,
        )
        ctx._options = dict(self._options)
        ctx._max_iterations = self._max_iterations
        return ctx
