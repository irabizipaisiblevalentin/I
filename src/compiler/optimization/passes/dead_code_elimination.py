from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import (
    Return, Branch, CondBranch, Store, Call,
)


class DeadCodeEliminationPass(Pass):
    """Removes instructions whose results are never used."""

    def __init__(self) -> None:
        super().__init__("dead_code_elimination", level=0)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            used: set[str] = set()
            for arg in func.args:
                if arg.name:
                    used.add(arg.name)
            for bb in func.basic_blocks:
                for inst in bb.instructions:
                    for attr in ("a", "b", "lhs", "rhs", "condition", "value", "ptr"):
                        val = getattr(inst, attr, None)
                        if val is not None and hasattr(val, "name") and val.name:
                            used.add(val.name)
            for bb in func.basic_blocks:
                to_remove = []
                for inst in bb.instructions:
                    if hasattr(inst, "name") and inst.name:
                        if inst.name not in used and not isinstance(
                            inst, (Return, Branch, CondBranch, Store, Call)
                        ):
                            to_remove.append(inst)
                            impact.instructions_eliminated += 1
                            changed = True
                for inst in to_remove:
                    bb.remove(inst)
        return PassResult(changed=changed, impact=impact)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "high"

    def description(self) -> str:
        return "Dead code elimination: remove unused instructions"
