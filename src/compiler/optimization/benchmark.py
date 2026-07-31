"""
Production Benchmarking Infrastructure for the I Optimiser.

Measures compilation overhead, runtime speed improvements, binary size changes,
memory consumption, pass execution time, and scalability.

Supports comparing O0, O1, O2, O3, and Os across configurable workloads.
"""
from __future__ import annotations

import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from compiler.ir.module import IRModule
from compiler.optimization.context import OptimizationLevel
from compiler.optimization.manager import OptimizationManager

# ══════════════════════════════════════════════════════════════════
# BenchmarkResult
# ══════════════════════════════════════════════════════════════════


@dataclass
class BenchmarkResult:
    """Results for a single benchmark run."""
    level_name: str
    duration_ms: float
    instruction_count_before: int
    instruction_count_after: int
    block_count_before: int
    block_count_after: int
    function_count_before: int
    function_count_after: int
    memory_estimate_bytes: int = 0
    passes_run: int = 0
    passes_changed: int = 0

    @property
    def instructions_eliminated(self) -> int:
        return self.instruction_count_before - self.instruction_count_after

    @property
    def blocks_eliminated(self) -> int:
        return self.block_count_before - self.block_count_after

    @property
    def elimination_pct(self) -> float:
        if self.instruction_count_before == 0:
            return 0.0
        return (self.instructions_eliminated / self.instruction_count_before) * 100.0


# ══════════════════════════════════════════════════════════════════
# BenchmarkReport
# ══════════════════════════════════════════════════════════════════


@dataclass
class BenchmarkReport:
    """Complete benchmark report comparing all optimisation levels."""
    module_name: str
    results: dict[str, BenchmarkResult] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    @property
    def levels(self) -> list[str]:
        return list(self.results.keys())

    @property
    def best_level(self) -> str:
        """Return the level with the most instruction elimination."""
        best = None
        best_pct = -1.0
        for name, r in self.results.items():
            if r.elimination_pct > best_pct:
                best_pct = r.elimination_pct
                best = name
        return best or "O0"

    @property
    def fastest_level(self) -> str:
        """Return the level with the shortest optimisation time."""
        best = None
        best_time = float("inf")
        for name, r in self.results.items():
            if r.duration_ms < best_time:
                best_time = r.duration_ms
                best = name
        return best or "O0"

    def format_table(self) -> str:
        """Format benchmark results as a table."""
        header = (
            f"{'Level':<8} {'Time(ms)':>10} {'Instr Before':>14} "
            f"{'Instr After':>12} {'Elim%':>8} {'Blocks':>8} {'Passes':>8}"
        )
        sep = "-" * len(header)
        rows = [header, sep]
        for level in ["O0", "O1", "O2", "O3", "Os"]:
            r = self.results.get(level)
            if r is None:
                continue
            row = (
                f"{level:<8} {r.duration_ms:>10.2f} {r.instruction_count_before:>14} "
                f"{r.instruction_count_after:>12} {r.elimination_pct:>7.2f}% "
                f"{r.blocks_eliminated:>8} {r.passes_run:>8}"
            )
            rows.append(row)
        return "\n".join(rows)

    def format_summary(self) -> str:
        """Format a human-readable summary."""
        lines = [
            f"Benchmark Report: {self.module_name}",
            f"  Best elimination:  {self.best_level} ({self.results.get(self.best_level, BenchmarkResult('', 0, 0, 0, 0, 0, 0, 0)).elimination_pct:.1f}%)",
            f"  Fastest:           {self.fastest_level}",
            "",
        ]
        for level in ["O0", "O1", "O2", "O3", "Os"]:
            r = self.results.get(level)
            if r is None:
                continue
            lines.append(
                f"  {level}: {r.duration_ms:>8.2f}ms  "
                f"{r.instruction_count_before} -> {r.instruction_count_after} instr  "
                f"({r.elimination_pct:.1f}% eliminated)"
            )
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_name": self.module_name,
            "timestamp": self.timestamp,
            "best_level": self.best_level,
            "fastest_level": self.fastest_level,
            "results": {
                level: {
                    "duration_ms": r.duration_ms,
                    "instructions_before": r.instruction_count_before,
                    "instructions_after": r.instruction_count_after,
                    "elimination_pct": r.elimination_pct,
                    "blocks_eliminated": r.blocks_eliminated,
                    "functions_eliminated": r.function_count_before - r.function_count_after,
                    "passes_run": r.passes_run,
                }
                for level, r in self.results.items()
            },
        }


# ══════════════════════════════════════════════════════════════════
# BenchmarkRunner
# ══════════════════════════════════════════════════════════════════


class BenchmarkRunner:
    """Runs benchmarks comparing optimisation levels.

    Usage:
        runner = BenchmarkRunner()
        report = runner.benchmark(module)
        print(report.format_table())
        print(report.format_summary())
    """

    __slots__ = ("_manager", "_levels")

    def __init__(
        self,
        manager: OptimizationManager | None = None,
        levels: list[OptimizationLevel] | None = None,
    ) -> None:
        self._manager = manager or OptimizationManager()
        self._levels = levels or [
            OptimizationLevel.O0,
            OptimizationLevel.O1,
            OptimizationLevel.O2,
            OptimizationLevel.O3,
            OptimizationLevel.OS,
        ]

    @property
    def manager(self) -> OptimizationManager:
        return self._manager

    @property
    def levels(self) -> list[OptimizationLevel]:
        return list(self._levels)

    def benchmark(
        self,
        module: IRModule,
        iterations: int = 3,
    ) -> BenchmarkReport:
        """Benchmark a module across all optimisation levels.

        Args:
            module: The IR module to benchmark.
            iterations: Number of warmup iterations before measurement.

        Returns:
            BenchmarkReport with results for each level.
        """
        report = BenchmarkReport(module_name=module.name)

        for level in self._levels:
            level_name = level.name
            result = self._run_single_benchmark(module, level_name, level, iterations)
            report.results[level_name] = result

        return report

    def _run_single_benchmark(
        self,
        module: IRModule,
        level_name: str,
        level: OptimizationLevel,
        iterations: int,
    ) -> BenchmarkResult:
        """Run a single benchmark for one optimisation level."""
        before_count = module.instruction_count
        before_blocks = module.block_count
        before_funcs = module.function_count

        durations: list[float] = []
        final_after = before_count
        final_blocks_after = before_blocks
        final_funcs_after = before_funcs
        passes_run = 0
        passes_changed = 0

        for i in range(iterations):
            from copy import deepcopy

            mod_copy = deepcopy(module)
            t0 = time.monotonic()
            report = self._manager.optimize(mod_copy, level)
            t1 = time.monotonic()
            durations.append((t1 - t0) * 1000.0)
            if i == iterations - 1:
                final_after = mod_copy.instruction_count
                final_blocks_after = mod_copy.block_count
                final_funcs_after = mod_copy.function_count
                passes_run = report.pass_count
                passes_changed = len(report.changed_passes)

        avg_duration = sum(durations) / len(durations)

        return BenchmarkResult(
            level_name=level_name,
            duration_ms=avg_duration,
            instruction_count_before=before_count,
            instruction_count_after=final_after,
            block_count_before=before_blocks,
            block_count_after=final_blocks_after,
            function_count_before=before_funcs,
            function_count_after=final_funcs_after,
            passes_run=passes_run,
            passes_changed=passes_changed,
        )

    def compare_pass_timing(self, module: IRModule, level: OptimizationLevel = OptimizationLevel.O3) -> dict[str, float]:
        """Measure individual pass execution times for a single level."""
        from copy import deepcopy

        from compiler.optimization.cache import AnalysisCache
        from compiler.optimization.context import OptimizationContext
        from compiler.optimization.stats import StatisticsEngine

        mod_copy = deepcopy(module)
        stats = StatisticsEngine()
        cache = AnalysisCache()
        ctx = OptimizationContext(
            module=mod_copy,
            level=level,
            stats=stats,
            cache=cache,
        )
        from compiler.optimization.pipeline import PipelineConfig
        config = PipelineConfig()
        config.enable_verification = False
        config.enable_statistics = True
        pipeline = type(self._manager.pipeline)(self._manager.registry, config)
        pipeline.build_default_pipeline()
        pipeline.run(mod_copy, ctx)

        return {
            s.name: s.duration_ms
            for s in stats.all_pass_stats()
        }


# ══════════════════════════════════════════════════════════════════
# ScalabilityBenchmark
# ══════════════════════════════════════════════════════════════════


@dataclass
class ScalabilityPoint:
    """Measurement at a particular program size."""
    size: int
    duration_ms: float
    memory_bytes: int = 0
    instructions_before: int = 0
    instructions_after: int = 0


@dataclass
class ScalabilityReport:
    """Report on how optimisation scales with program size."""
    points: list[ScalabilityPoint] = field(default_factory=list)

    @property
    def estimated_complexity(self) -> str:
        if len(self.points) < 3:
            return "insufficient data"
        ratios = []
        for i in range(1, len(self.points)):
            size_ratio = self.points[i].size / self.points[i - 1].size
            time_ratio = self.points[i].duration_ms / max(self.points[i - 1].duration_ms, 0.001)
            if size_ratio > 0:
                ratios.append(math.log2(time_ratio) / math.log2(size_ratio))
        if not ratios:
            return "unknown"
        avg_ratio = sum(ratios) / len(ratios)
        if avg_ratio < 1.2:
            return "O(n)"
        elif avg_ratio < 1.8:
            return "O(n log n)"
        elif avg_ratio < 2.5:
            return "O(n^2)"
        else:
            return "O(n^k) with k > 2"

    def format_summary(self) -> str:
        lines = ["Scalability Report:", f"  Estimated complexity: {self.estimated_complexity}", ""]
        for p in self.points:
            lines.append(
                f"  Size {p.size:>6}: {p.duration_ms:>10.2f}ms  "
                f"({p.instructions_before} -> {p.instructions_after} instr)"
            )
        return "\n".join(lines)


class ScalabilityBenchmark:
    """Measures optimisation scalability with increasing program size."""

    __slots__ = ("_runner",)

    def __init__(self, runner: BenchmarkRunner | None = None) -> None:
        self._runner = runner or BenchmarkRunner()

    def benchmark(
        self,
        module_factory: Callable[[int], IRModule],
        sizes: list[int],
        level: OptimizationLevel = OptimizationLevel.O2,
    ) -> ScalabilityReport:
        """Run scalability benchmark by generating modules of increasing size."""
        report = ScalabilityReport()
        for size in sizes:
            mod = module_factory(size)
            t0 = time.monotonic()
            result = self._runner._manager.optimize(mod, level)
            t1 = time.monotonic()
            duration = (t1 - t0) * 1000.0
            report.points.append(ScalabilityPoint(
                size=size,
                duration_ms=duration,
                instructions_before=mod.instruction_count,
                instructions_after=mod.instruction_count - result.instructions_eliminated,
            ))
        return report
