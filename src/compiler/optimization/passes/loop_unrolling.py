from __future__ import annotations

from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Add, Sub, Mul, Branch, CondBranch
from compiler.ir.values import IntConstant


class LoopUnrollingPass(Pass):
    """Unrolls small loop bodies by duplicating instructions."""

    __slots__ = ("_max_unroll",)

    def __init__(self, max_unroll: int = 4) -> None:
        super().__init__("loop_unrolling", level=2)
        self._max_unroll = max_unroll

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for fname, func in list(module.functions.items()):
            for bb in func.basic_blocks:
                for inst in list(bb.instructions):
                    if isinstance(inst, Branch):
                        target = getattr(inst, 'target', None)
                        if target and hasattr(target, 'name'):
                            target_block = func.get_block(target.name)
                            if target_block and target_block in func.basic_blocks:
                                target_idx = func.basic_blocks.index(target_block)
                                bb_idx = func.basic_blocks.index(bb) if bb in func.basic_blocks else -1
                                if target_idx <= bb_idx and len(bb.instructions) <= self._max_unroll:
                                    body_copy = []
                                    for orig in target_block.instructions:
                                        copied = self._copy_instruction(orig)
                                        if copied is not None:
                                            body_copy.append(copied)
                                    insert_idx = bb._instructions.index(inst)
                                    bb._instructions[insert_idx:insert_idx + 1] = body_copy
                                    impact.instructions_eliminated += 1
                                    impact.instructions_combined += len(body_copy)
                                    changed = True
        return PassResult(changed=changed, impact=impact)

    def _copy_instruction(self, inst):
        if isinstance(inst, Branch):
            return Branch(inst.target)
        if isinstance(inst, CondBranch):
            return CondBranch(inst.condition, inst.true_block, inst.false_block)
        if isinstance(inst, Add):
            return Add(inst.name, inst.a, inst.b)
        if isinstance(inst, Sub):
            return Sub(inst.name, inst.a, inst.b)
        if isinstance(inst, Mul):
            return Mul(inst.name, inst.a, inst.b)
        return None

    def estimated_complexity(self) -> str:
        return "O(n^2)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Loop unrolling for small loop bodies"
