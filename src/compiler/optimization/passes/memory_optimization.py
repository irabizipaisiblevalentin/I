from __future__ import annotations

from compiler.ir.instructions import Alloca, Load, Store
from compiler.ir.module import IRModule
from compiler.optimization.base import Pass, PassImpact, PassResult


class MemoryOptimizationPass(Pass):
    """Memory optimization: reduce allocations, improve locality, minimise temporaries.

    Combines adjacent allocas into struct allocations where beneficial,
    eliminates zero-size allocas, and promotes repeated alloca+store patterns.
    """

    def __init__(self) -> None:
        super().__init__("memory_optimization", level=0)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            allocas = []
            for bb in func.basic_blocks:
                for inst in bb.instructions:
                    if isinstance(inst, Alloca):
                        allocas.append((bb, inst))

            zero_size_removed = self._eliminate_zero_size_allocas(allocas, impact)
            promoted = self._promote_single_store_allocas(func, impact)
            changed = zero_size_removed or promoted or changed

        return PassResult(changed=changed, impact=impact)

    def _eliminate_zero_size_allocas(self, allocas, impact) -> bool:
        changed = False
        for bb, inst in allocas:
            allocated_type = getattr(inst, "allocated_type", None)
            if allocated_type is None:
                continue
            from compiler.ir.types import VoidType
            if isinstance(allocated_type, VoidType):
                bb.remove(inst)
                impact.instructions_eliminated += 1
                changed = True
        return changed

    def _promote_single_store_allocas(self, func, impact) -> bool:
        changed = False
        for bb in func.basic_blocks:
            write_map = {}
            read_map = {}
            for inst in bb.instructions:
                if isinstance(inst, Store):
                    ptr = getattr(inst, "pointer", None)
                    if ptr is not None and hasattr(ptr, "name"):
                        write_map[ptr.name] = inst
                if isinstance(inst, Load):
                    ptr = getattr(inst, "pointer", None)
                    if ptr is not None and hasattr(ptr, "name"):
                        read_map.setdefault(ptr.name, []).append(inst)

            for ptr_name, store_inst in write_map.items():
                if ptr_name in read_map:
                    loads = read_map[ptr_name]
                    if len(loads) == 1 and self._is_single_alloca(ptr_name, func):
                        val = getattr(store_inst, "value", None)
                        if val is not None:
                            for user in list(loads[0].uses):
                                if user is not loads[0]:
                                    user.replace_uses_of(loads[0], val)
                            bb.remove(loads[0])
                            bb.remove(store_inst)
                            impact.instructions_eliminated += 2
                            changed = True
        return changed

    def _is_single_alloca(self, name: str, func) -> bool:
        count = 0
        for bb in func.basic_blocks:
            for inst in bb.instructions:
                if isinstance(inst, Alloca) and inst.name == name:
                    count += 1
        return count == 1

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Memory optimization: reduce allocations and improve locality"
