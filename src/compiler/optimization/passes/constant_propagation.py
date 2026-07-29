from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Add, Sub, Mul
from compiler.ir.values import IntConstant, FloatConstant, BoolConstant


class ConstantPropagationPass(Pass):
    """Replaces uses of known-constant values with their constants."""

    def __init__(self) -> None:
        super().__init__("constant_propagation", level=0)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            consts: dict[str, object] = {}
            for bb in func.basic_blocks:
                for inst in bb.instructions:
                    if isinstance(inst, (IntConstant, FloatConstant, BoolConstant)) and inst.name:
                        if inst.name not in consts:
                            consts[inst.name] = inst.value
            propagated = True
            while propagated:
                propagated = False
                for bb in func.basic_blocks:
                    for inst in bb.instructions:
                        for attr in ("a", "b"):
                            val = getattr(inst, attr, None)
                            if val is not None and hasattr(val, "name") and val.name in consts:
                                replacement = self._to_const(consts[val.name])
                                if replacement is not None:
                                    setattr(inst, attr, replacement)
                                    propagated = True
                                    changed = True
        return PassResult(changed=changed, impact=impact)

    def _to_const(self, val):
        if isinstance(val, int):
            return IntConstant(val)
        if isinstance(val, float):
            return FloatConstant(val)
        if isinstance(val, bool):
            return BoolConstant(val)
        return None

    def estimated_complexity(self) -> str:
        return "O(n^2)"

    def performance_impact(self) -> str:
        return "high"

    def description(self) -> str:
        return "Propagate constant values to uses"
