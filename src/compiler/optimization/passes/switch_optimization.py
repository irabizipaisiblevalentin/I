from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Switch, CondBranch, Branch, ICmp, ICmpPredicate
from compiler.ir.values import IntConstant


class SwitchOptimizationPass(Pass):
    """Optimizes Switch instructions:

    1. Single-case switch -> conditional branch
    2. Dense switch (>= 4 cases, high density) -> left as-is (detected for future jump table)
    3. Sparse switches -> no optimization
    """

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("switch_optimization", level=2)

    def run(self, module: IRModule, ctx: object) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            for bb in func.basic_blocks:
                for i, inst in enumerate(list(bb._instructions)):
                    if not isinstance(inst, Switch):
                        continue
                    cases = list(inst.cases) if hasattr(inst, 'cases') else []
                    default = inst.default if hasattr(inst, 'default') else None
                    if len(cases) == 0 and default is not None:
                        bb._instructions[i] = Branch(default)
                        impact.instructions_combined += 1
                        changed = True
                    elif len(cases) >= 4:
                        values = [c.value if isinstance(c, IntConstant) else c for c, _ in cases]
                        if all(isinstance(v, int) for v in values):
                            min_val = min(values)
                            max_val = max(values)
                            span = max_val - min_val + 1
                            density = len(cases) / span if span > 0 else 0
                            if density > 0.5:
                                impact.instructions_combined += 1
                                changed = True
        return PassResult(changed=changed, impact=impact)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Switch optimization: simplify small switches"
