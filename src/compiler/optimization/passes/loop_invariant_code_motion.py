from __future__ import annotations

from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Add, Sub, Mul, ICmp, Load, Alloca, Branch
from compiler.ir.basic_block import BasicBlock
from compiler.ir.values import IntConstant


class LoopInvariantCodeMotionPass(Pass):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("loop_invariant_code_motion", level=2)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for fname, func in module.functions.items():
            if len(func.basic_blocks) < 2:
                continue
            for tail in func.basic_blocks:
                for header in tail.successors:
                    header_idx = func.basic_blocks.index(header) if header in func.basic_blocks else -1
                    tail_idx = func.basic_blocks.index(tail) if tail in func.basic_blocks else -1
                    if header_idx < 0 or tail_idx < 0:
                        continue
                    if header_idx >= tail_idx:
                        continue
                    loop_blocks = []
                    for idx in range(header_idx, tail_idx + 1):
                        loop_blocks.append(func.basic_blocks[idx])
                    loop_set = set(loop_blocks)
                    preheader = self._get_or_create_preheader(func, header)
                    moved = True
                    while moved:
                        moved = False
                        for loop_bb in loop_blocks:
                            for inst in list(loop_bb._instructions):
                                if self._is_loop_invariant(inst, func, loop_set):
                                    if inst in loop_bb._instructions:
                                        loop_bb._instructions.remove(inst)
                                        insert_pos = max(0, len(preheader._instructions) - 1)
                                        preheader._instructions.insert(insert_pos, inst)
                                        impact.instructions_eliminated += 1
                                        changed = True
                                        moved = True
                                        break
                            if moved:
                                break
        return PassResult(changed=changed, impact=impact)

    def _get_or_create_preheader(self, func, header):
        if header.predecessors:
            non_loop_preds = [p for p in header.predecessors if p in func.basic_blocks]
            if len(non_loop_preds) == 1:
                return non_loop_preds[0]
        preheader = BasicBlock(f"{header.name}_preheader")
        preheader.append(Branch(header))
        header.add_predecessor(preheader)
        idx = func.basic_blocks.index(header) if header in func.basic_blocks else 0
        func.insert_block(idx, preheader)
        return preheader

    def _is_loop_invariant(self, inst, func, loop_blocks) -> bool:
        if isinstance(inst, (Add, Sub, Mul, ICmp)):
            for attr in ['a', 'b']:
                val = getattr(inst, attr, None)
                if val is not None:
                    if hasattr(val, 'name') and val in func.args:
                        return False
                    if hasattr(val, 'name'):
                        for bb in loop_blocks:
                            for i in bb.instructions:
                                if hasattr(i, 'name') and i.name == val.name:
                                    return False
            return True
        if isinstance(inst, Alloca):
            return True
        return False

    def estimated_complexity(self) -> str:
        return "O(n^2)"

    def performance_impact(self) -> str:
        return "high"

    def description(self) -> str:
        return "Loop invariant code motion"
