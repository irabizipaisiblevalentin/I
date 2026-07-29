from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Add, Mul
from compiler.ir.values import IntConstant


class CopyPropagationPass(Pass):
    """Replaces copy-like instructions with their source values."""

    def __init__(self) -> None:
        super().__init__("copy_propagation", level=1)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            copies: dict[str, object] = {}
            changed_this = True
            while changed_this:
                changed_this = False
                for bb in func.basic_blocks:
                    for inst in bb.instructions:
                        for attr in ("a", "b"):
                            val = getattr(inst, attr, None)
                            if val is not None and hasattr(val, "name") and val.name in copies:
                                setattr(inst, attr, copies[val.name])
                                changed_this = True
                                changed = True
                    for inst in bb.instructions:
                        if isinstance(inst, Add) and inst.name:
                            b = getattr(inst, "b", None)
                            b_val = self._get_int(b)
                            if b_val == 0 and hasattr(inst.a, "name") and inst.name not in copies:
                                copies[inst.name] = inst.a
                        if isinstance(inst, Mul) and inst.name:
                            b = getattr(inst, "b", None)
                            b_val = self._get_int(b)
                            if b_val == 1 and hasattr(inst.a, "name") and inst.name not in copies:
                                copies[inst.name] = inst.a
        return PassResult(changed=changed, impact=impact)

    def _get_int(self, val):
        if isinstance(val, IntConstant):
            return val.value
        if isinstance(val, int):
            return val
        return None

    def estimated_complexity(self) -> str:
        return "O(n^2)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Copy propagation: replace copies with original values"
