from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Branch


class ControlFlowSimplificationPass(Pass):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("control_flow_simplification", level=1)

    def run(self, module: IRModule, ctx: object) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            entry_block = func.entry_block
            to_remove: list = []
            for bb in func.basic_blocks:
                if bb is entry_block:
                    continue
                non_branch = [inst for inst in bb._instructions if not isinstance(inst, Branch)]
                if len(non_branch) == 0 and len(bb._instructions) > 0:
                    branch = bb._instructions[-1]
                    if isinstance(branch, Branch) and hasattr(branch, 'target'):
                        target = branch.target
                        if target and hasattr(target, 'name'):
                            target_block = func.get_block(target.name)
                            if target_block:
                                for pred in list(bb.predecessors):
                                    if bb in pred._successors:
                                        pred._successors.remove(bb)
                                    if target_block not in pred._successors:
                                        pred._successors.append(target_block)
                                    if pred not in target_block._predecessors:
                                        target_block._predecessors.append(pred)
                                to_remove.append(bb)
                                impact.instructions_eliminated += 1
                                changed = True
            for bb in to_remove:
                if bb in func.basic_blocks:
                    func._blocks.remove(bb)
        return PassResult(changed=changed, impact=impact)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Control flow simplification: merge and remove empty blocks"
