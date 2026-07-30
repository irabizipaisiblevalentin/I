"""
I Programming Language — Register Allocator Subsystem

Graph-coloring register allocation with live interval analysis,
conservative coalescing, and spill management.
"""

from __future__ import annotations

from compiler.native.register.allocator import (
    AllocationResult,
    GraphColoringAllocator,
    InterferenceGraph,
    PhysicalRegister,
    RegisterAllocator,
    RegisterClass,
)
from compiler.native.register.coalescing import (
    CoalescingOptimizer,
    Move,
    coalesce,
)
from compiler.native.register.liveness import (
    LiveInterval,
    LiveRangeAnalysis,
)
from compiler.native.register.spill import (
    SpillManager,
    StackSlot,
)

__all__ = [
    # liveness
    "LiveInterval",
    "LiveRangeAnalysis",
    # allocator
    "AllocationResult",
    "GraphColoringAllocator",
    "InterferenceGraph",
    "PhysicalRegister",
    "RegisterAllocator",
    "RegisterClass",
    # coalescing
    "CoalescingOptimizer",
    "Move",
    "coalesce",
    # spill
    "SpillManager",
    "StackSlot",
]
