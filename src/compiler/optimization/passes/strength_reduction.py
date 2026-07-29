from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Mul, Add, Shl
from compiler.ir.values import IntConstant


class StrengthReductionPass(Pass):
    """Replaces expensive operations with cheaper equivalents.

    - Multiply by power of 2 -> shift left
    - Multiply by 0 -> constant 0
    - Multiply by 1 -> identity
    - Add 0 -> identity
    """

    def __init__(self) -> None:
        super().__init__("strength_reduction", level=1)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            for bb in func.basic_blocks:
                for i, inst in enumerate(list(bb.instructions)):
                    if isinstance(inst, Mul) and inst.name:
                        replacement = self._reduce_mul(inst)
                        if replacement is not None:
                            bb._instructions[i] = replacement
                            changed = True
                            impact.instructions_combined += 1
                    elif isinstance(inst, Add) and inst.name:
                        replacement = self._reduce_add(inst)
                        if replacement is not None:
                            bb._instructions[i] = replacement
                            changed = True
                            impact.instructions_combined += 1
        return PassResult(changed=changed, impact=impact)

    def _reduce_mul(self, inst):
        b_val = self._get_int_value(inst.b)
        if b_val is None:
            a_val = self._get_int_value(inst.a)
            if a_val is not None:
                b_val = a_val
                inst = type(inst)(inst.name, inst.b, inst.a)

        if b_val == 1:
            return Add(inst.name, inst.a, IntConstant(0))

        if b_val > 0 and (b_val & (b_val - 1)) == 0:
            shift_amount = b_val.bit_length() - 1
            return Shl(inst.name, inst.a, IntConstant(shift_amount))

        return None

    def _reduce_add(self, inst):
        b_val = self._get_int_value(inst.b)
        if b_val == 0:
            return Add(inst.name, inst.a, IntConstant(0))
        a_val = self._get_int_value(inst.a)
        if a_val == 0:
            return Add(inst.name, inst.b, IntConstant(0))
        return None

    def _get_int_value(self, val) -> int | None:
        if isinstance(val, IntConstant):
            return val.value
        if isinstance(val, int):
            return val
        return None

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Strength reduction: replace expensive ops with cheaper ones"
