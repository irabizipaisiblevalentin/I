from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Add, Sub, Mul, ICmp, ICmpPredicate, Return
from compiler.ir.values import IntConstant


class InstructionCombiningPass(Pass):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("instruction_combining", level=1)

    def run(self, module: IRModule, ctx: object) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            for bb in func.basic_blocks:
                for i, inst in enumerate(bb.instructions):
                    if isinstance(inst, Add) and inst.name:
                        if isinstance(inst.a, type(inst)):
                            inner = inst.a
                            b_val = inst.b.value if isinstance(inst.b, IntConstant) else None
                            inner_b_val = inner.b.value if isinstance(inner.b, IntConstant) else None
                            if b_val is not None and inner_b_val is not None:
                                combined_val = b_val + inner_b_val
                                new_inst = Add(inst.name, inner.a, IntConstant(combined_val))
                                bb.instructions[i] = new_inst
                                impact.instructions_combined += 1
                                changed = True
        return PassResult(changed=changed, impact=impact)

    def estimated_complexity(self) -> str:
        return "O(n^2)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Instruction combining: merge instruction sequences"
