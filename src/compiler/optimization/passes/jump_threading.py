from __future__ import annotations

from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Branch, CondBranch


class JumpThreadingPass(Pass):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("jump_threading", level=2)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            for bb in func.basic_blocks:
                if len(bb._instructions) == 0:
                    continue
                last = bb._instructions[-1]
                if isinstance(last, Branch):
                    target = last.target
                    if target and hasattr(target, 'name'):
                        target_block = func.get_block(target.name)
                        if target_block and len(target_block.predecessors) == 1:
                            if len(target_block._instructions) > 0 and isinstance(target_block._instructions[-1], Branch):
                                new_target = target_block._instructions[-1].target
                                last.target = new_target
                                impact.instructions_combined += 1
                                changed = True
                elif isinstance(last, CondBranch):
                    true_target = last.true_block
                    false_target = last.false_block
                    new_true = true_target
                    new_false = false_target
                    if true_target and hasattr(true_target, 'name'):
                        true_block = func.get_block(true_target.name)
                        if true_block and len(true_block.predecessors) == 1:
                            if len(true_block._instructions) > 0 and isinstance(true_block._instructions[-1], Branch):
                                new_true = true_block._instructions[-1].target
                    if false_target and hasattr(false_target, 'name'):
                        false_block = func.get_block(false_target.name)
                        if false_block and len(false_block.predecessors) == 1:
                            if len(false_block._instructions) > 0 and isinstance(false_block._instructions[-1], Branch):
                                new_false = false_block._instructions[-1].target
                    if new_true is not true_target or new_false is not false_target:
                        bb._instructions[-1] = CondBranch(last.condition, new_true, new_false)
                        impact.instructions_combined += 1
                        changed = True
        return PassResult(changed=changed, impact=impact)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Jump threading: skip trivial blocks"
