from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compiler.ir.module import IRModule
    from compiler.optimization.context import OptimizationContext, OptimizationLevel
    from compiler.optimization.registry import PassRegistry
    from compiler.optimization.stats import OptimizationReport


# ──────────────────────────────────────────────────────────────────────
# PipelineConfig
# ──────────────────────────────────────────────────────────────────────

class PipelineConfig:
    """Configuration for a pipeline run."""
    __slots__ = (
        "max_fixed_point_iterations",
        "enable_statistics",
        "enable_debug",
        "enable_verification",
        "debug_output_dir",
        "dump_all_ir",
        "dump_changed_only",
        "timeout_seconds",
        "custom_pass_order",
    )

    def __init__(self) -> None:
        self.max_fixed_point_iterations = 4
        self.enable_statistics = True
        self.enable_debug = False
        self.enable_verification = True
        self.debug_output_dir = ""
        self.dump_all_ir = False
        self.dump_changed_only = True
        self.timeout_seconds = 0.0
        self.custom_pass_order: list[str] | None = None


# ──────────────────────────────────────────────────────────────────────
# OptimizationPipeline
# ──────────────────────────────────────────────────────────────────────

class OptimizationPipeline:
    """Manages pass execution at different optimization levels."""
    __slots__ = ("_registry", "_config", "_pass_lists")

    def __init__(self, registry: PassRegistry, config: PipelineConfig | None = None) -> None:
        self._registry = registry
        self._config = config or PipelineConfig()
        self._pass_lists: dict[int, list[str]] = {}

    @property
    def config(self) -> PipelineConfig:
        return self._config

    def get_passes(self, level: OptimizationLevel) -> list[str]:
        """Get ordered list of passes for the given level. Uses scheduler."""
        from compiler.optimization.scheduler import OptimizationScheduler
        scheduler = OptimizationScheduler(self._registry)
        if self._config.custom_pass_order is not None:
            scheduler._custom_order = self._config.custom_pass_order
        return scheduler.schedule_all_at_level(level.value)

    def build_default_pipeline(self) -> None:
        """Populate _pass_lists with default pass orderings per level."""
        from compiler.optimization.context import OptimizationLevel

        o1 = [
            "constant_folding",
            "dead_code_elimination",
        ]
        o2 = o1 + [
            "constant_propagation",
            "copy_propagation",
            "common_subexpression_elimination",
        ]
        o3 = o2 + [
            "function_inlining",
            "loop_invariant_code_motion",
            "loop_unrolling",
            "strength_reduction",
            "tail_call_optimization",
            "instruction_combining",
            "peephole_optimization",
        ]
        os_passes = o1 + [
            "constant_propagation",
            "copy_propagation",
            "instruction_combining",
            "peephole_optimization",
            "strength_reduction",
        ]
        oz_passes = [
            "constant_folding",
            "dead_code_elimination",
            "peephole_optimization",
            "instruction_combining",
        ]
        ofast = o3 + [
            "devirtualization",
            "memory_optimization",
        ]

        all_pass_names = set(self._registry.pass_names())

        self._pass_lists = {
            OptimizationLevel.O0.value: [],
            OptimizationLevel.O1.value: [n for n in o1 if n in all_pass_names],
            OptimizationLevel.O2.value: [n for n in o2 if n in all_pass_names],
            OptimizationLevel.O3.value: [n for n in o3 if n in all_pass_names],
            OptimizationLevel.OS.value: [n for n in os_passes if n in all_pass_names],
            OptimizationLevel.OZ.value: [n for n in oz_passes if n in all_pass_names],
            OptimizationLevel.OFAST.value: [n for n in ofast if n in all_pass_names],
        }

    def run(self, module: IRModule, ctx: OptimizationContext) -> OptimizationReport:
        """Run all passes for the context's optimization level. Returns report."""
        from compiler.optimization.stats import StatisticsEngine

        self._verify_ir(module, "pipeline input")

        level = ctx.level
        passes = self.get_passes(level)

        stats = ctx.stats
        if stats is None:
            stats = StatisticsEngine()
            ctx._stats = stats

        for pass_name in passes:
            self.run_single_pass(module, ctx, pass_name)

        return stats.generate_report(module.name)

    def run_fixed_point(self, module: IRModule, ctx: OptimizationContext) -> OptimizationReport:
        """Run passes repeatedly until no changes or max iterations reached."""
        from compiler.optimization.stats import StatisticsEngine

        self._verify_ir(module, "pipeline input")

        max_iters = self._config.max_fixed_point_iterations
        stats = ctx.stats
        if stats is None:
            stats = StatisticsEngine()
            ctx._stats = stats

        for iteration in range(max_iters):
            ctx.set_iteration(iteration)
            ctx.reset_changed()

            passes = self.get_passes(ctx.level)
            any_changed = False

            for pass_name in passes:
                before = module.instruction_count
                self.run_single_pass(module, ctx, pass_name)
                after = module.instruction_count
                if before != after:
                    any_changed = True

            if not any_changed:
                break

        return stats.generate_report(module.name)

    def run_single_pass(
        self, module: IRModule, ctx: OptimizationContext, pass_name: str
    ) -> None:
        """Run a single named pass."""
        info = self._registry.get_pass(pass_name)
        if info is None:
            return

        stats = ctx.stats
        if stats is not None:
            stats.start_pass(pass_name)

        before_instr = module.instruction_count
        before_blocks = module.block_count
        before_funcs = module.function_count
        before_bytes = self._estimate_bytes(module)

        inst = info.create()
        result = inst.run(module, ctx)

        after_instr = module.instruction_count
        after_blocks = module.block_count
        after_funcs = module.function_count
        after_bytes = self._estimate_bytes(module)

        if stats is not None:
            stats.end_pass(pass_name, changed=result.changed, details=result.details)
            stats.record_instruction_count(before_instr, after_instr)
            stats.record_block_count(before_blocks, after_blocks)
            stats.record_function_count(before_funcs, after_funcs)
            stats.record_byte_count(before_bytes, after_bytes)

        ctx.increment_pass_count()
        if result.changed:
            ctx.mark_changed()

    def _verify_ir(self, module: IRModule, phase: str) -> None:
        """Verify IR structural integrity. Raises RuntimeError on failure."""
        if not self._config.enable_verification:
            return
        from compiler.ir.validator import IRValidator

        validator = IRValidator()
        validator.validate_module(module)
        if not validator.is_valid:
            details = "; ".join(validator.errors[:3])
            raise RuntimeError(f"IR validation failed after {phase}: {details}")

    def _count_instructions(self, module: IRModule) -> int:
        return module.instruction_count

    def _count_blocks(self, module: IRModule) -> int:
        return module.block_count

    def _count_functions(self, module: IRModule) -> int:
        return module.function_count

    def _estimate_bytes(self, module: IRModule) -> int:
        count = 0
        for func in module.functions:
            for block in func:
                count += len(block) * 8
        count += module.global_count * 8
        return count
