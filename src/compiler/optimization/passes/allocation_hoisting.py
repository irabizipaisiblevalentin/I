from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Alloca


class AllocationHoistingPass(Pass):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("allocation_hoisting", level=2)

    def run(self, module: IRModule, ctx: object) -> PassResult:
        impact = PassImpact()
        changed = False
        for fname, func in module.functions.items():
            for bb in func.basic_blocks:
                for succ in bb.successors:
                    succ_idx = func.basic_blocks.index(succ) if succ in func.basic_blocks else -1
                    bb_idx = func.basic_blocks.index(bb) if bb in func.basic_blocks else -1
                    if succ_idx < bb_idx and succ_idx >= 0:
                        for inst in list(bb.instructions):
                            if isinstance(inst, Alloca):
                                preheader = func.basic_blocks[succ_idx]
                                bb.instructions.remove(inst)
                                preheader.instructions.insert(max(0, len(preheader.instructions) - 1), inst)
                                impact.instructions_eliminated += 1
                                changed = True
        return PassResult(changed=changed, impact=impact)

    def estimated_complexity(self) -> str:
        return "O(n^2)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Allocation hoisting: move loop-invariant allocas to preheader"
