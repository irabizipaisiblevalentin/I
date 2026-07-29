from __future__ import annotations

from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Call, Return, Branch, Alloca, Load, Store
from compiler.ir.values import IntConstant


class TailCallOptimizationPass(Pass):
    """Converts tail recursion to loops.

    Pattern: if the last instruction is `Return(Call(self, ...))`,
    replace with argument stores + branch to entry.
    """

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("tail_call_optimization", level=2)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for fname, func in module.functions.items():
            if func.is_declaration:
                continue
            for bb in func.basic_blocks:
                if len(bb._instructions) < 2:
                    continue
                last = bb._instructions[-1]
                second_last = bb._instructions[-2]
                if not (isinstance(last, Return) and isinstance(second_last, Call)):
                    continue
                call = second_last
                call_result = last.value
                if call_result is None or not hasattr(call_result, 'name') or call_result.name != call.name:
                    continue
                callee_name = call.function.name if hasattr(call.function, 'name') else str(call.function)
                if callee_name != fname:
                    continue
                args = list(call.arguments) if hasattr(call, 'arguments') else []
                entry_block = func.entry_block
                if entry_block is None:
                    continue
                bb._instructions.pop()
                bb._instructions.pop()
                for i, arg in enumerate(args):
                    if i < len(func.args):
                        param = func.args[i]
                        store = Store(arg, param)
                        bb._instructions.append(store)
                bb._instructions.append(Branch(entry_block))
                impact.instructions_eliminated += 2
                impact.instructions_combined += len(args) + 1
                changed = True
                break
        return PassResult(changed=changed, impact=impact)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Tail call optimization: convert tail recursion to loops"
