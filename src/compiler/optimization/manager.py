from __future__ import annotations

from compiler.ir.module import IRModule
from compiler.optimization.context import OptimizationLevel
from compiler.optimization.pipeline import PipelineConfig
from compiler.optimization.stats import OptimizationReport


# ──────────────────────────────────────────────────────────────────────
# OptimizationManager
# ──────────────────────────────────────────────────────────────────────

class OptimizationManager:
    """Top-level optimization driver."""
    __slots__ = ("_pipeline", "_registry")

    def __init__(self, config: PipelineConfig | None = None) -> None:
        from compiler.optimization.registry import PassRegistry
        from compiler.optimization.pipeline import OptimizationPipeline

        self._registry = PassRegistry()

        from compiler.optimization.passes._register import register_default_passes
        register_default_passes(self._registry)

        from compiler.optimization.analyses._register import register_default_analyses
        register_default_analyses(self._registry)

        self._pipeline = OptimizationPipeline(self._registry, config)
        self._pipeline.build_default_pipeline()

    @property
    def registry(self):
        return self._registry

    @property
    def pipeline(self):
        return self._pipeline

    def optimize(
        self, module: IRModule, level: OptimizationLevel = OptimizationLevel.O2
    ) -> OptimizationReport:
        """Run full optimization pipeline. Returns report."""
        from compiler.optimization.context import OptimizationContext
        from compiler.optimization.stats import StatisticsEngine

        from compiler.optimization.cache import AnalysisCache

        stats = StatisticsEngine()
        cache = AnalysisCache()

        ctx = OptimizationContext(
            module=module,
            level=level,
            stats=stats,
            cache=cache,
        )

        return self._pipeline.run_fixed_point(module, ctx)

    def optimize_module(
        self, module: IRModule, level: int = 2
    ) -> OptimizationReport:
        """Convenience: accept int level (0-6)."""
        from compiler.optimization.context import OptimizationLevel

        level_map = {
            0: OptimizationLevel.O0,
            1: OptimizationLevel.O1,
            2: OptimizationLevel.O2,
            3: OptimizationLevel.O3,
            4: OptimizationLevel.OS,
            5: OptimizationLevel.OZ,
            6: OptimizationLevel.OFAST,
        }
        opt_level = level_map.get(level, OptimizationLevel.O2)
        return self.optimize(module, opt_level)

    def run_pass(
        self,
        module: IRModule,
        pass_name: str,
        level: OptimizationLevel = OptimizationLevel.O2,
    ) -> None:
        """Run a single named pass."""
        from compiler.optimization.context import OptimizationContext
        from compiler.optimization.stats import StatisticsEngine
        from compiler.optimization.cache import AnalysisCache

        stats = StatisticsEngine()
        cache = AnalysisCache()

        ctx = OptimizationContext(
            module=module,
            level=level,
            stats=stats,
            cache=cache,
        )

        self._pipeline.run_single_pass(module, ctx, pass_name)

    def available_passes(self) -> list[str]:
        return self._registry.pass_names()

    def available_analyses(self) -> list[str]:
        return self._registry.analysis_names()

    def summary(self) -> str:
        """Return human-readable summary of registered passes and analyses."""
        lines = ["Optimization Manager Summary", ""]

        passes = self._registry.all_passes()
        analyses = self._registry.all_analyses()

        lines.append(f"Registered passes ({len(passes)}):")
        for info in sorted(passes, key=lambda p: (p.level, p.name)):
            lines.append(
                f"  [{info.level}] {info.name}: {info.description or '(no description)'}"
            )

        lines.append("")
        lines.append(f"Registered analyses ({len(analyses)}):")
        for info in sorted(analyses, key=lambda a: a.name):
            lines.append(
                f"  {info.name}: {info.description or '(no description)'}"
            )

        lines.append("")
        lines.append(f"Pipeline levels configured:")
        for level_val in sorted(self._pipeline._pass_lists.keys()):
            pass_list = self._pipeline._pass_lists[level_val]
            lines.append(f"  Level {level_val}: {len(pass_list)} passes")

        return "\n".join(lines)
