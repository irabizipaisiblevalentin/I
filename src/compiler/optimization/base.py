from __future__ import annotations

import abc
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compiler.optimization.context import OptimizationContext
    from compiler.ir.module import IRModule


# ──────────────────────────────────────────────────────────────────────
# AnalysisResult
# ──────────────────────────────────────────────────────────────────────

class AnalysisResult:
    __slots__ = ("_name", "_timestamp")

    def __init__(self, name: str) -> None:
        self._name = name
        self._timestamp = time.monotonic()

    @property
    def name(self) -> str:
        return self._name

    @property
    def timestamp(self) -> float:
        return self._timestamp

    def invalidate(self) -> None:
        self._timestamp = 0.0


# ──────────────────────────────────────────────────────────────────────
# Analysis
# ──────────────────────────────────────────────────────────────────────

class Analysis(abc.ABC):
    __slots__ = ("_name", "_required", "_produced", "_invalidated")

    def __init__(self, name: str) -> None:
        self._name = name
        self._required: list[str] = []
        self._produced: list[str] = []
        self._invalidated: list[str] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def required_analyses(self) -> list[str]:
        return self._required

    @property
    def produced_analyses(self) -> list[str]:
        return self._produced

    @property
    def invalidated_analyses(self) -> list[str]:
        return self._invalidated

    @abc.abstractmethod
    def run(self, module: IRModule, ctx: OptimizationContext) -> AnalysisResult:
        ...

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "none"


# ──────────────────────────────────────────────────────────────────────
# PassImpact
# ──────────────────────────────────────────────────────────────────────

class PassImpact:
    __slots__ = (
        "instructions_eliminated",
        "instructions_combined",
        "functions_inlined",
        "bytes_saved",
        "estimated_speedup",
    )

    def __init__(self) -> None:
        self.instructions_eliminated = 0
        self.instructions_combined = 0
        self.functions_inlined = 0
        self.bytes_saved = 0
        self.estimated_speedup = 1.0


# ──────────────────────────────────────────────────────────────────────
# PassResult
# ──────────────────────────────────────────────────────────────────────

class PassResult:
    __slots__ = ("_changed", "_impact", "_details")

    def __init__(
        self,
        changed: bool = False,
        impact: PassImpact | None = None,
        details: str = "",
    ) -> None:
        self._changed = changed
        self._impact = impact if impact is not None else PassImpact()
        self._details = details

    @property
    def changed(self) -> bool:
        return self._changed

    @property
    def impact(self) -> PassImpact:
        return self._impact

    @property
    def details(self) -> str:
        return self._details


# ──────────────────────────────────────────────────────────────────────
# Pass
# ──────────────────────────────────────────────────────────────────────

class Pass(abc.ABC):
    __slots__ = (
        "_name",
        "_level",
        "_required",
        "_produced",
        "_invalidated",
        "_dependencies",
        "_enabled",
    )

    def __init__(self, name: str, level: int = 0) -> None:
        self._name = name
        self._level = level
        self._required: list[str] = []
        self._produced: list[str] = []
        self._invalidated: list[str] = []
        self._dependencies: list[str] = []
        self._enabled = True

    @property
    def name(self) -> str:
        return self._name

    @property
    def level(self) -> int:
        return self._level

    @property
    def required_analyses(self) -> list[str]:
        return self._required

    @property
    def produced_analyses(self) -> list[str]:
        return self._produced

    @property
    def invalidated_analyses(self) -> list[str]:
        return self._invalidated

    @property
    def dependencies(self) -> list[str]:
        return self._dependencies

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    @abc.abstractmethod
    def run(self, module: IRModule, ctx: OptimizationContext) -> PassResult:
        ...

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "none"

    def description(self) -> str:
        return self._name
