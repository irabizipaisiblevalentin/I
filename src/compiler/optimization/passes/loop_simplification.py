from __future__ import annotations

from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Branch, CondBranch
from compiler.ir.basic_block import BasicBlock


class LoopSimplificationPass(Pass):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("loop_simplification", level=1)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for fname, func in module.functions.items():
            loops = self._find_loops(func)
            for header, latches in loops:
                all_preds = []
                for pred in func.basic_blocks:
                    if header in pred.successors:
                        all_preds.append(pred)
                outside_preds = [p for p in all_preds if p not in latches]
                if len(outside_preds) == 0:
                    preheader = BasicBlock(f"{header.name}.preheader")
                    preheader._instructions = [Branch(header)]
                    object.__setattr__(preheader, "_successors", [header])
                    header_idx = func.basic_blocks.index(header) if header in func.basic_blocks else 0
                    func.insert_block(header_idx, preheader)
                    object.__setattr__(header, "_predecessors", list(all_preds) + [preheader])
                    impact.instructions_combined += 1
                    changed = True
                elif len(all_preds) > 1 and len(outside_preds) >= 1:
                    has_clean_entry = (
                        len(outside_preds) == 1
                        and len(outside_preds[0].successors) == 1
                        and outside_preds[0].successors[0] is header
                    )
                    if has_clean_entry:
                        continue
                    merge = BasicBlock(f"{header.name}.merge")
                    merge._instructions = [Branch(header)]
                    object.__setattr__(merge, "_successors", [header])
                    header_idx = func.basic_blocks.index(header) if header in func.basic_blocks else 0
                    func.insert_block(header_idx, merge)
                    for pred in all_preds:
                        if header in pred._successors:
                            pred._successors.remove(header)
                        pred._successors.append(merge)
                    object.__setattr__(merge, "_predecessors", list(all_preds))
                    object.__setattr__(header, "_predecessors", [merge] + [l for l in latches if l not in all_preds])
                    impact.instructions_combined += 1
                    changed = True
        return PassResult(changed=changed, impact=impact)

    def _find_loops(self, func):
        loops = []
        seen = set()
        for bb in func.basic_blocks:
            for succ in bb.successors:
                succ_idx = func.basic_blocks.index(succ) if succ in func.basic_blocks else -1
                bb_idx = func.basic_blocks.index(bb) if bb in func.basic_blocks else -1
                if succ_idx < bb_idx and succ_idx >= 0:
                    latches = set()
                    for idx in range(succ_idx + 1, bb_idx + 1):
                        block = func.basic_blocks[idx]
                        if succ in block.successors:
                            latches.add(block)
                    latches.add(bb)
                    key = succ.name
                    if key not in seen:
                        seen.add(key)
                        loops.append((succ, latches))
        return loops

    def estimated_complexity(self) -> str:
        return "O(n^2)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Loop simplification: preheaders and single back-edges"
