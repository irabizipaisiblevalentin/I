from __future__ import annotations

from compiler.ir.instructions import Branch
from compiler.ir.module import IRModule
from compiler.optimization.base import Pass, PassImpact, PassResult


class BasicBlockMergingPass(Pass):
    """Basic block merging: merge a block into its predecessor when there is a single
    predecessor and the predecessor has only this block as successor.

    Reduces unnecessary block boundaries and enables further optimisation.
    """

    def __init__(self) -> None:
        super().__init__("basic_block_merging", level=0)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            merged = True
            while merged:
                merged = False
                blocks = list(func.basic_blocks)
                for bb in blocks:
                    if bb is func.entry_block:
                        continue
                    preds = bb.predecessors
                    if len(preds) != 1:
                        continue
                    pred = list(preds)[0]
                    succs = pred.successors
                    if len(succs) != 1:
                        continue
                    if list(succs)[0] is not bb:
                        continue
                    if not self._is_mergeable(pred, bb):
                        continue
                    self._merge_blocks(pred, bb, func)
                    impact.instructions_eliminated += 1
                    changed = True
                    merged = True
        return PassResult(changed=changed, impact=impact)

    def _is_mergeable(self, pred, bb) -> bool:
        if not pred.instructions:
            return False
        terminator = pred.instructions[-1]
        if not isinstance(terminator, Branch):
            return False
        return True

    def _merge_blocks(self, pred, bb, func) -> None:
        """Merge bb into pred by moving all instructions and updating terminators."""
        non_term = [inst for inst in bb.instructions[:-1]]
        for inst in non_term:
            pred.append(inst)
        new_term = bb.instructions[-1]
        pred.remove(pred.instructions[-1])
        pred.append(new_term)
        for succ in list(bb.successors):
            succ.remove_predecessor(bb)
            succ.add_predecessor(pred)
        func.remove_block(bb)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "low"

    def description(self) -> str:
        return "Basic block merging: merge single-predecessor blocks"
