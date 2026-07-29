from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from compiler.optimization.registry import PassRegistry

def register_default_passes(registry: PassRegistry) -> None:
    from compiler.optimization.passes.constant_folding import ConstantFoldingPass
    from compiler.optimization.passes.constant_propagation import ConstantPropagationPass
    from compiler.optimization.passes.dead_code_elimination import DeadCodeEliminationPass
    from compiler.optimization.passes.dead_store_elimination import DeadStoreEliminationPass
    from compiler.optimization.passes.copy_propagation import CopyPropagationPass
    from compiler.optimization.passes.strength_reduction import StrengthReductionPass
    from compiler.optimization.passes.common_subexpression import CommonSubexpressionEliminationPass
    from compiler.optimization.passes.function_inlining import FunctionInliningPass
    from compiler.optimization.passes.tail_call import TailCallOptimizationPass
    from compiler.optimization.passes.loop_invariant_code_motion import LoopInvariantCodeMotionPass
    from compiler.optimization.passes.loop_unrolling import LoopUnrollingPass
    from compiler.optimization.passes.loop_simplification import LoopSimplificationPass
    from compiler.optimization.passes.branch_simplification import BranchSimplificationPass
    from compiler.optimization.passes.jump_threading import JumpThreadingPass
    from compiler.optimization.passes.redundant_load_elimination import RedundantLoadEliminationPass
    from compiler.optimization.passes.redundant_store_elimination import RedundantStoreEliminationPass
    from compiler.optimization.passes.memory_coalescing import MemoryCoalescingPass
    from compiler.optimization.passes.object_lifetime import ObjectLifetimeOptimizationPass
    from compiler.optimization.passes.allocation_hoisting import AllocationHoistingPass
    from compiler.optimization.passes.peephole import PeepholeOptimizationPass
    from compiler.optimization.passes.instruction_combining import InstructionCombiningPass
    from compiler.optimization.passes.control_flow_simplification import ControlFlowSimplificationPass
    from compiler.optimization.passes.switch_optimization import SwitchOptimizationPass
    from compiler.optimization.passes.sparse_ccp import SparseConditionalConstantPropagationPass
    from compiler.optimization.passes.ssa_cleanup import SSACleanupPass

    all_passes = [
        ConstantFoldingPass, ConstantPropagationPass, DeadCodeEliminationPass,
        DeadStoreEliminationPass, CopyPropagationPass, StrengthReductionPass,
        CommonSubexpressionEliminationPass, FunctionInliningPass, TailCallOptimizationPass,
        LoopInvariantCodeMotionPass, LoopUnrollingPass, LoopSimplificationPass,
        BranchSimplificationPass, JumpThreadingPass, RedundantLoadEliminationPass,
        RedundantStoreEliminationPass, MemoryCoalescingPass, ObjectLifetimeOptimizationPass,
        AllocationHoistingPass, PeepholeOptimizationPass, InstructionCombiningPass,
        ControlFlowSimplificationPass, SwitchOptimizationPass,
        SparseConditionalConstantPropagationPass, SSACleanupPass,
    ]
    for cls in all_passes:
        name = cls.__name__.removesuffix("Pass").removesuffix("Optimization")
        name_lower = ""
        for i, c in enumerate(name):
            if c.isupper() and i > 0 and name[i - 1].islower():
                name_lower += "_"
            name_lower += c.lower()
        registry.register_pass(cls, name=name_lower, description=cls.__doc__ or "")
