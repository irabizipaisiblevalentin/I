from __future__ import annotations

from typing import Any

# ──────────────────────────────────────────────────────────────────────
# Lazy import registry
# ──────────────────────────────────────────────────────────────────────

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # context
    "OptimizationContext": ("compiler.optimization.context", "OptimizationContext"),
    "OptimizationLevel": ("compiler.optimization.context", "OptimizationLevel"),
    # cache
    "AnalysisCache": ("compiler.optimization.cache", "AnalysisCache"),
    # stats
    "StatisticsEngine": ("compiler.optimization.stats", "StatisticsEngine"),
    "OptimizationReport": ("compiler.optimization.stats", "OptimizationReport"),
    "PassStats": ("compiler.optimization.stats", "PassStats"),
    # registry
    "PassRegistry": ("compiler.optimization.registry", "PassRegistry"),
    "PassInfo": ("compiler.optimization.registry", "PassInfo"),
    "AnalysisInfo": ("compiler.optimization.registry", "AnalysisInfo"),
    # scheduler
    "OptimizationScheduler": ("compiler.optimization.scheduler", "OptimizationScheduler"),
    # pipeline
    "OptimizationPipeline": ("compiler.optimization.pipeline", "OptimizationPipeline"),
    # manager
    "OptimizationManager": ("compiler.optimization.manager", "OptimizationManager"),

    # ── base classes ──
    "Analysis": ("compiler.optimization.base", "Analysis"),
    "AnalysisResult": ("compiler.optimization.base", "AnalysisResult"),
    "Pass": ("compiler.optimization.base", "Pass"),
    "PassResult": ("compiler.optimization.base", "PassResult"),
    "PassImpact": ("compiler.optimization.base", "PassImpact"),

    # ── analyses ──
    "ControlFlowAnalysis": ("compiler.optimization.analyses.control_flow", "ControlFlowAnalysis"),
    "DataFlowAnalysis": ("compiler.optimization.analyses.data_flow", "DataFlowAnalysis"),
    "LivenessAnalysis": ("compiler.optimization.analyses.liveness", "LivenessAnalysis"),
    "ReachabilityAnalysis": ("compiler.optimization.analyses.reachability", "ReachabilityAnalysis"),
    "EscapeAnalysis": ("compiler.optimization.analyses.escape", "EscapeAnalysis"),
    "AliasAnalysis": ("compiler.optimization.analyses.alias", "AliasAnalysis"),
    "DominanceAnalysis": ("compiler.optimization.analyses.dominance", "DominanceAnalysis"),
    "LoopAnalysis": ("compiler.optimization.analyses.loop", "LoopAnalysis"),
    "CallGraphAnalysis": ("compiler.optimization.analyses.call_graph", "CallGraphAnalysis"),
    "SideEffectAnalysis": ("compiler.optimization.analyses.side_effect", "SideEffectAnalysis"),
    "MemoryAccessAnalysis": ("compiler.optimization.analyses.memory_access", "MemoryAccessAnalysis"),
    "ConstantPropagationAnalysis": ("compiler.optimization.analyses.constant_propagation", "ConstantPropagationAnalysis"),

    # ── passes ──
    "DeadCodeElimination": ("compiler.optimization.passes.dead_code_elimination", "DeadCodeElimination"),
    "ConstantFolding": ("compiler.optimization.passes.constant_folding", "ConstantFolding"),
    "ConstantPropagation": ("compiler.optimization.passes.constant_propagation", "ConstantPropagation"),
    "CommonSubexpressionElimination": ("compiler.optimization.passes.common_subexpression_elimination", "CommonSubexpressionElimination"),
    "CopyPropagation": ("compiler.optimization.passes.copy_propagation", "CopyPropagation"),
    "FunctionInlining": ("compiler.optimization.passes.function_inlining", "FunctionInlining"),
    "LoopInvariantCodeMotion": ("compiler.optimization.passes.loop_invariant_code_motion", "LoopInvariantCodeMotion"),
    "LoopUnrolling": ("compiler.optimization.passes.loop_unrolling", "LoopUnrolling"),
    "StrengthReduction": ("compiler.optimization.passes.strength_reduction", "StrengthReduction"),
    "TailCallOptimization": ("compiler.optimization.passes.tail_call_optimization", "TailCallOptimization"),
    "InstructionCombining": ("compiler.optimization.passes.instruction_combining", "InstructionCombining"),
    "RegisterAllocation": ("compiler.optimization.passes.register_allocation", "RegisterAllocation"),
    "BasicBlockMerging": ("compiler.optimization.passes.basic_block_merging", "BasicBlockMerging"),
    "JumpThreading": ("compiler.optimization.passes.jump_threading", "JumpThreading"),
    "RedundantBranchElimination": ("compiler.optimization.passes.redundant_branch_elimination", "RedundantBranchElimination"),
    "PeepholeOptimization": ("compiler.optimization.passes.peephole_optimization", "PeepholeOptimization"),
    "MemoryOptimization": ("compiler.optimization.passes.memory_optimization", "MemoryOptimization"),
    "Devirtualization": ("compiler.optimization.passes.devirtualization", "Devirtualization"),
}

# ──────────────────────────────────────────────────────────────────────
# Lazy loading
# ──────────────────────────────────────────────────────────────────────

def __getattr__(name: str) -> Any:
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        import importlib
        module = importlib.import_module(module_path)
        value = getattr(module, attr_name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

def __dir__() -> list[str]:
    return list(globals().keys()) + list(_LAZY_IMPORTS.keys())
