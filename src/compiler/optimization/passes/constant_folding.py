from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Add, Sub, Mul, ICmp, ICmpPredicate
from compiler.ir.values import IntConstant, FloatConstant, BoolConstant


class ConstantFoldingPass(Pass):
    """Folds constant arithmetic and comparison expressions."""

    def __init__(self) -> None:
        super().__init__("constant_folding", level=0)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            for bb in func.basic_blocks:
                replacements: dict[str, object] = {}
                to_remove: list = []
                for inst in bb.instructions:
                    if isinstance(inst, (Add, Sub, Mul)) and inst.name:
                        a = self._resolve(inst.a, replacements)
                        b = self._resolve(inst.b, replacements)
                        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                            try:
                                if isinstance(inst, Add):
                                    result = a + b
                                elif isinstance(inst, Sub):
                                    result = a - b
                                else:
                                    result = a * b
                                replacements[inst.name] = result
                                to_remove.append(inst)
                                impact.instructions_eliminated += 1
                                changed = True
                            except Exception:
                                pass
                    elif isinstance(inst, ICmp) and inst.name:
                        a = self._resolve(inst.lhs, replacements)
                        b = self._resolve(inst.rhs, replacements)
                        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                            result = self._eval_icmp(inst.predicate, a, b)
                            if result is not None:
                                replacements[inst.name] = result
                                to_remove.append(inst)
                                impact.instructions_eliminated += 1
                                changed = True
                for inst in to_remove:
                    bb.remove(inst)
        return PassResult(changed=changed, impact=impact)

    def _resolve(self, val, replacements: dict[str, object]):
        if val is None:
            return None
        if isinstance(val, (int, float, bool)):
            return val
        if isinstance(val, IntConstant):
            return val.value
        if isinstance(val, FloatConstant):
            return val.value
        if isinstance(val, BoolConstant):
            return val.value
        if hasattr(val, "name") and val.name in replacements:
            return replacements[val.name]
        return None

    def _eval_icmp(self, predicate, a, b):
        try:
            if predicate == ICmpPredicate.EQ:
                return a == b
            if predicate == ICmpPredicate.NE:
                return a != b
            if predicate == ICmpPredicate.SLT:
                return a < b
            if predicate == ICmpPredicate.SLE:
                return a <= b
            if predicate == ICmpPredicate.SGT:
                return a > b
            if predicate == ICmpPredicate.SGE:
                return a >= b
            if predicate == ICmpPredicate.ULT:
                return a < b
            if predicate == ICmpPredicate.ULE:
                return a <= b
            if predicate == ICmpPredicate.UGT:
                return a > b
            if predicate == ICmpPredicate.UGE:
                return a >= b
        except TypeError:
            return None
        return None

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "high"

    def description(self) -> str:
        return "Constant folding: evaluate constant expressions at compile time"
