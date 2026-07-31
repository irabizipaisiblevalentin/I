from __future__ import annotations

from compiler.ir.instructions import Branch, CondBranch, Return
from compiler.ir.module import IRModule
from compiler.ir.values import BoolConstant
from compiler.optimization.base import Pass, PassImpact, PassResult


class RedundantBranchEliminationPass(Pass):
    """Redundant branch elimination: simplify unnecessary branches.

    Removes branches to blocks that themselves contain only an unconditional
    branch (tail merging). Also eliminates branches where the condition is
    known to be constant.
    """

    def __init__(self) -> None:
        super().__init__("redundant_branch_elimination", level=0)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            c1 = self._eliminate_trivial_branches(func, impact)
            c2 = self._eliminate_constant_cond_branches(func, impact)
            c3 = self._eliminate_redundant_indirection(func, impact)
            if c1 or c2 or c3:
                changed = True
        return PassResult(changed=changed, impact=impact)

    def _eliminate_trivial_branches(self, func, impact) -> bool:
        changed = False
        for bb in list(func.basic_blocks):
            if bb is func.entry_block:
                continue
            if len(bb.instructions) != 1:
                continue
            term = bb.instructions[-1]
            if isinstance(term, Branch) and len(bb.predecessors) > 0:
                target = term.target
                for pred in list(bb.predecessors):
                    pred_term = pred.instructions[-1]
                    if isinstance(pred_term, Branch):
                        pred_term.target = target
                        target.add_predecessor(pred)
                        bb.remove_predecessor(pred)
                if len(bb.predecessors) == 0:
                    func.remove_block(bb)
                    impact.instructions_eliminated += 1
                    changed = True
        return changed

    def _eliminate_constant_cond_branches(self, func, impact) -> bool:
        changed = False
        for bb in list(func.basic_blocks):
            term = bb.instructions[-1] if bb.instructions else None
            if not isinstance(term, CondBranch):
                continue
            cond = term.condition
            if not isinstance(cond, BoolConstant):
                continue
            target = term.true_block if cond.value else term.false_block
            new_branch = Branch(target)
            bb.remove(term)
            bb.append(new_branch)
            impact.instructions_eliminated += 1
            changed = True
        return changed

    def _eliminate_redundant_indirection(self, func, impact) -> bool:
        changed = False
        for bb in list(func.basic_blocks):
            term = bb.instructions[-1] if bb.instructions else None
            if not isinstance(term, Branch):
                continue
            target = term.target
            if target is bb:
                continue
            if len(target.instructions) != 1:
                continue
            target_term = target.instructions[-1]
            if isinstance(target_term, Return) and len(target.predecessors) == 1:
                bb.remove(term)
                bb.append(Return(target_term.value))
                func.remove_block(target)
                impact.instructions_eliminated += 1
                changed = True
        return changed

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Redundant branch elimination: simplify unnecessary branches"
