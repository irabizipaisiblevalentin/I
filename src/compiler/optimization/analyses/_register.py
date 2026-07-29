from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from compiler.optimization.registry import PassRegistry

def register_default_analyses(registry: PassRegistry) -> None:
    from compiler.optimization.analyses.control_flow import ControlFlowAnalysis
    from compiler.optimization.analyses.data_flow import DataFlowAnalysis
    from compiler.optimization.analyses.liveness import LivenessAnalysis
    from compiler.optimization.analyses.reachability import ReachabilityAnalysis
    from compiler.optimization.analyses.escape import EscapeAnalysis
    from compiler.optimization.analyses.alias import AliasAnalysis
    from compiler.optimization.analyses.dominance import DominanceAnalysis
    from compiler.optimization.analyses.loop import LoopAnalysis
    from compiler.optimization.analyses.call_graph import CallGraphAnalysis
    from compiler.optimization.analyses.side_effect import SideEffectAnalysis
    from compiler.optimization.analyses.memory_access import MemoryAccessAnalysis
    from compiler.optimization.analyses.constant_propagation import ConstantPropagationAnalysis
    
    for cls in [ControlFlowAnalysis, DataFlowAnalysis, LivenessAnalysis,
                ReachabilityAnalysis, EscapeAnalysis, AliasAnalysis,
                DominanceAnalysis, LoopAnalysis, CallGraphAnalysis,
                SideEffectAnalysis, MemoryAccessAnalysis, ConstantPropagationAnalysis]:
        registry.register_analysis(cls, name=cls.__name__.removesuffix("Analysis").lower(),
                                   description=cls.__doc__ or "")
