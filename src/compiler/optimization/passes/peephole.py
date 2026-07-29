from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Add, Sub, Mul, ICmp, ICmpPredicate
from compiler.ir.values import IntConstant, BoolConstant


class PeepholeOptimizationPass(Pass):
    """Local peephole patterns:
    - Add x, 0 -> x
    - Sub x, 0 -> x
    - Mul x, 1 -> x
    - Mul x, 0 -> 0
    - Sub x, x -> 0
    - ICmp EQ x, x -> true
    """

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("peephole_optimization", level=1)

    def run(self, module: IRModule, ctx: object) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            for bb in func.basic_blocks:
                for i, inst in enumerate(bb.instructions):
                    replacement = None
                    if isinstance(inst, Add) and inst.name:
                        replacement = self._fold_add(inst)
                    elif isinstance(inst, Sub) and inst.name:
                        replacement = self._fold_sub(inst)
                    elif isinstance(inst, Mul) and inst.name:
                        replacement = self._fold_mul(inst)
                    elif isinstance(inst, ICmp) and inst.name:
                        replacement = self._fold_icmp(inst)

                    if replacement is not None:
                        bb._instructions[i] = replacement
                        impact.instructions_combined += 1
                        changed = True
        return PassResult(changed=changed, impact=impact)

    def _get_int(self, val) -> int | None:
        if isinstance(val, IntConstant):
            return val.value
        if isinstance(val, int):
            return val
        return None

    def _fold_add(self, inst):
        b_val = self._get_int(inst.b)
        if b_val == 0:
            from compiler.ir.instructions import Add as AddInst
            return AddInst(inst.name, inst.a, IntConstant(0))
        a_val = self._get_int(inst.a)
        if a_val == 0:
            from compiler.ir.instructions import Add as AddInst
            return AddInst(inst.name, inst.b, IntConstant(0))
        return None

    def _fold_sub(self, inst):
        a_name = inst.a.name if hasattr(inst.a, 'name') else None
        b_name = inst.b.name if hasattr(inst.b, 'name') else None
        if a_name and b_name and a_name == b_name:
            return IntConstant(0)
        b_val = self._get_int(inst.b)
        if b_val == 0:
            from compiler.ir.instructions import Add as AddInst
            return AddInst(inst.name, inst.a, IntConstant(0))
        return None

    def _fold_mul(self, inst):
        b_val = self._get_int(inst.b)
        if b_val == 1:
            from compiler.ir.instructions import Add as AddInst
            return AddInst(inst.name, inst.a, IntConstant(0))
        if b_val == 0:
            return IntConstant(0)
        a_val = self._get_int(inst.a)
        if a_val == 1:
            from compiler.ir.instructions import Add as AddInst
            return AddInst(inst.name, inst.b, IntConstant(0))
        if a_val == 0:
            return IntConstant(0)
        return None

    def _fold_icmp(self, inst):
        if inst.predicate == ICmpPredicate.EQ:
            a_name = inst.lhs.name if hasattr(inst.lhs, 'name') else None
            b_name = inst.rhs.name if hasattr(inst.rhs, 'name') else None
            if a_name and b_name and a_name == b_name:
                return BoolConstant(True)
        return None

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Peephole optimization: local instruction patterns"
