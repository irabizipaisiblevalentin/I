from __future__ import annotations

from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Branch, CondBranch
from compiler.ir.values import BoolConstant, IntConstant


class BranchSimplificationPass(Pass):
    """Simplifies branches with constant conditions and trivial targets."""

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("branch_simplification", level=1)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            for bb in func.basic_blocks:
                if not bb.instructions:
                    continue
                last = bb.instructions[-1]
                if isinstance(last, CondBranch):
                    result = self._simplify_cond_branch(func, bb, last)
                    if result:
                        impact.instructions_combined += 1
                        changed = True
                elif isinstance(last, Branch):
                    result = self._simplify_branch(func, bb, last)
                    if result:
                        impact.instructions_combined += 1
                        changed = True
        return PassResult(changed=changed, impact=impact)

    def _simplify_cond_branch(self, func, bb, inst) -> bool:
        cond = inst.condition
        if isinstance(cond, BoolConstant):
            target = inst.true_block if cond.value else inst.false_block
            bb._instructions[-1] = Branch(target)
            return True
        if isinstance(cond, IntConstant):
            target = inst.true_block if cond.value != 0 else inst.false_block
            bb._instructions[-1] = Branch(target)
            return True
        true_block = inst.true_block
        false_block = inst.false_block
        if true_block is not None and false_block is not None:
            if true_block == false_block:
                bb._instructions[-1] = Branch(true_block)
                return True
            if hasattr(true_block, 'name'):
                true_bb = func.get_block(true_block.name)
                if (true_bb is not None and len(true_bb.instructions) == 1
                        and isinstance(true_bb.instructions[0], Branch)):
                    if true_bb.instructions[0].target == false_block:
                        bb._instructions[-1] = Branch(false_block)
                        return True
            if hasattr(false_block, 'name'):
                false_bb = func.get_block(false_block.name)
                if (false_bb is not None and len(false_bb.instructions) == 1
                        and isinstance(false_bb.instructions[0], Branch)):
                    if false_bb.instructions[0].target == true_block:
                        bb._instructions[-1] = Branch(true_block)
                        return True
        return False

    def _simplify_branch(self, func, bb, inst) -> bool:
        target = inst.target
        if target is None or not hasattr(target, 'name'):
            return False
        target_block = func.get_block(target.name)
        if target_block is None:
            return False
        if target_block is bb:
            return False
        if len(target_block.instructions) == 1 and isinstance(target_block.instructions[0], Branch):
            nested_target = target_block.instructions[0].target
            if nested_target is not None and nested_target != target:
                inst.target = nested_target
                return True
        return False

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Branch simplification: constant conditions and trivial branches"
