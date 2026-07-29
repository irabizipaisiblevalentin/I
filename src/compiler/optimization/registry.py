from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compiler.optimization.base import Analysis, Pass


# ──────────────────────────────────────────────────────────────────────
# AnalysisInfo
# ──────────────────────────────────────────────────────────────────────

class AnalysisInfo:
    __slots__ = (
        "name",
        "analysis_class",
        "required",
        "produced",
        "invalidated",
        "complexity",
        "performance_impact",
        "description",
        "registered_at",
    )

    def __init__(
        self,
        name: str,
        analysis_class: type[Analysis],
        required: list[str],
        produced: list[str],
        invalidated: list[str],
        complexity: str,
        performance_impact: str,
        description: str,
    ) -> None:
        self.name = name
        self.analysis_class = analysis_class
        self.required = list(required)
        self.produced = list(produced)
        self.invalidated = list(invalidated)
        self.complexity = complexity
        self.performance_impact = performance_impact
        self.description = description
        self.registered_at = time.monotonic()

    def create(self) -> Analysis:
        return self.analysis_class()


# ──────────────────────────────────────────────────────────────────────
# PassInfo
# ──────────────────────────────────────────────────────────────────────

class PassInfo:
    __slots__ = (
        "name",
        "pass_class",
        "level",
        "required",
        "produced",
        "invalidated",
        "dependencies",
        "complexity",
        "performance_impact",
        "description",
        "registered_at",
    )

    def __init__(
        self,
        name: str,
        pass_class: type[Pass],
        level: int,
        required: list[str],
        produced: list[str],
        invalidated: list[str],
        dependencies: list[str],
        complexity: str,
        performance_impact: str,
        description: str,
    ) -> None:
        self.name = name
        self.pass_class = pass_class
        self.level = level
        self.required = list(required)
        self.produced = list(produced)
        self.invalidated = list(invalidated)
        self.dependencies = list(dependencies)
        self.complexity = complexity
        self.performance_impact = performance_impact
        self.description = description
        self.registered_at = time.monotonic()

    def create(self) -> Pass:
        return self.pass_class()


# ──────────────────────────────────────────────────────────────────────
# PassRegistry
# ──────────────────────────────────────────────────────────────────────

class PassRegistry:
    __slots__ = ("_passes", "_analyses", "_pass_by_name", "_analysis_by_name")

    def __init__(self) -> None:
        self._passes: list[PassInfo] = []
        self._analyses: list[AnalysisInfo] = []
        self._pass_by_name: dict[str, PassInfo] = {}
        self._analysis_by_name: dict[str, AnalysisInfo] = {}

    # ── registration ──

    def register_pass(
        self,
        pass_class: type[Pass],
        *,
        name: str | None = None,
        level: int = 0,
        required: list[str] | None = None,
        produced: list[str] | None = None,
        invalidated: list[str] | None = None,
        dependencies: list[str] | None = None,
        complexity: str = "O(n)",
        performance_impact: str = "low",
        description: str = "",
    ) -> None:
        resolved_name = name if name is not None else pass_class.__name__
        info = PassInfo(
            name=resolved_name,
            pass_class=pass_class,
            level=level,
            required=required or [],
            produced=produced or [],
            invalidated=invalidated or [],
            dependencies=dependencies or [],
            complexity=complexity,
            performance_impact=performance_impact,
            description=description,
        )
        self._passes.append(info)
        self._pass_by_name[resolved_name] = info

    def register_analysis(
        self,
        analysis_class: type[Analysis],
        *,
        name: str | None = None,
        required: list[str] | None = None,
        produced: list[str] | None = None,
        invalidated: list[str] | None = None,
        complexity: str = "O(n)",
        performance_impact: str = "low",
        description: str = "",
    ) -> None:
        resolved_name = name if name is not None else analysis_class.__name__
        info = AnalysisInfo(
            name=resolved_name,
            analysis_class=analysis_class,
            required=required or [],
            produced=produced or [],
            invalidated=invalidated or [],
            complexity=complexity,
            performance_impact=performance_impact,
            description=description,
        )
        self._analyses.append(info)
        self._analysis_by_name[resolved_name] = info

    # ── lookups ──

    def get_pass(self, name: str) -> PassInfo | None:
        return self._pass_by_name.get(name)

    def get_analysis(self, name: str) -> AnalysisInfo | None:
        return self._analysis_by_name.get(name)

    def all_passes(self) -> list[PassInfo]:
        return list(self._passes)

    def all_analyses(self) -> list[AnalysisInfo]:
        return list(self._analyses)

    def passes_at_level(self, level: int) -> list[PassInfo]:
        return [p for p in self._passes if p.level <= level]

    def analysis_names(self) -> list[str]:
        return list(self._analysis_by_name.keys())

    def pass_names(self) -> list[str]:
        return list(self._pass_by_name.keys())

    # ── factory ──

    def create_pass(self, name: str) -> Pass:
        info = self._pass_by_name.get(name)
        if info is None:
            raise KeyError(f"pass not registered: {name!r}")
        return info.create()

    def create_analysis(self, name: str) -> Analysis:
        info = self._analysis_by_name.get(name)
        if info is None:
            raise KeyError(f"analysis not registered: {name!r}")
        return info.create()
