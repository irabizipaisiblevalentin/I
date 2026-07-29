from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Branch, CondBranch
from compiler.ir.values import BoolConstant, IntConstant


class SparseConditionalConstantPropagationPass(Pass):
    """Sparse Conditional Constant Propagation.

    Eliminates dead branches based on constant conditions and
    simplifies unconditional branches to blocks containing only
    another branch.
    """

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("sparse_conditional_constant_propagation", level=2)

    def run(self, module: IRModule, ctx: object) -> PassResult:
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
                        impact.instructions_eliminated += 1
                        changed = True
                elif isinstance(last, Branch):
                    result = self._simplify_branch(func, bb, last)
                    if result:
                        impact.instructions_eliminated += 1
                        changed = True
        return PassResult(changed=changed, impact=impact)

    def _simplify_cond_branch(self, func, bb, inst) -> bool:
        cond = inst.condition
        target = None
        dead_block = None

        if isinstance(cond, BoolConstant):
            if cond.value:
                target = inst.true_block
                dead_block = inst.false_block
            else:
                target = inst.false_block
                dead_block = inst.true_block
        elif isinstance(cond, IntConstant):
            if cond.value != 0:
                target = inst.true_block
                dead_block = inst.false_block
            else:
                target = inst.false_block
                dead_block = inst.true_block

        if target is not None:
            bb.instructions[-1] = Branch(target)
            if dead_block is not None and hasattr(dead_block, 'name'):
                dead_bb = func.get_block(dead_block.name)
                if dead_bb is not None:
                    self._disconnect_block(dead_bb)
            return True
        return False

    def _simplify_branch(self, func, bb, inst) -> bool:
        target = inst.target
        if target is None or not hasattr(target, 'name'):
            return False
        target_block = func.get_block(target.name)
        if target_block is None:
            return False
        non_branch = [i for i in target_block.instructions if not isinstance(i, Branch)]
        if len(non_branch) == 0 and len(target_block.instructions) > 0:
            nested = target_block.instructions[0]
            if isinstance(nested, Branch):
                inst.target = nested.target
                return True
        return False

    def _disconnect_block(self, block) -> None:
        for pred in list(block.predecessors):
            if block in pred.successors:
                pred.successors.remove(block)
        block.predecessors.clear()

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "high"

    def description(self) -> str:
        return "Sparse conditional constant propagation"
