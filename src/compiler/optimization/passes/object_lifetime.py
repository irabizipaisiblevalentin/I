from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Alloca, Store, Load
from compiler.ir.values import Value


class ObjectLifetimeOptimizationPass(Pass):
    """Removes dead allocas that are never loaded.

    Only removes allocas when the ratio of dead allocas to total instructions
    is high enough to justify the optimization.
    """

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("object_lifetime_optimization", level=2)

    def run(self, module: IRModule, ctx: object) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            allocas = {}
            total_insts = 0
            for bb in func.basic_blocks:
                for inst in bb.instructions:
                    total_insts += 1
                    if isinstance(inst, Alloca) and inst.name:
                        allocas[inst.name] = inst

            if not allocas:
                continue

            loaded_names = set()
            stored_names = set()
            for bb in func.basic_blocks:
                for inst in bb.instructions:
                    if isinstance(inst, Load):
                        ptr = getattr(inst, 'ptr', None)
                        if ptr and hasattr(ptr, 'name'):
                            loaded_names.add(ptr.name)
                    if isinstance(inst, Store):
                        ptr = getattr(inst, 'ptr', None) or getattr(inst, 'pointer', None)
                        if ptr and hasattr(ptr, 'name'):
                            stored_names.add(ptr.name)
                    for attr in ('a', 'b', 'lhs', 'rhs', 'condition', 'value'):
                        val = getattr(inst, attr, None)
                        if val and hasattr(val, 'name'):
                            loaded_names.add(val.name)

            dead_allocas = []
            for name, alloca_inst in allocas.items():
                if name not in loaded_names and name not in stored_names:
                    dead_allocas.append(alloca_inst)

            if not dead_allocas:
                continue

            dead_ratio = len(dead_allocas) / max(total_insts, 1)
            if dead_ratio < 0.3:
                continue

            for alloca_inst in dead_allocas:
                for bb in func.basic_blocks:
                    if alloca_inst in bb.instructions:
                        bb.instructions.remove(alloca_inst)
                        impact.instructions_eliminated += 1
                        impact.bytes_saved += 8
                        changed = True
                        break
                for bb in func.basic_blocks:
                    to_remove = []
                    for inst in bb.instructions:
                        if isinstance(inst, Store):
                            ptr = getattr(inst, 'ptr', None) or getattr(inst, 'pointer', None)
                            if ptr and hasattr(ptr, 'name') and ptr.name == alloca_inst.name:
                                to_remove.append(inst)
                    for inst in to_remove:
                        bb.instructions.remove(inst)
                        impact.instructions_eliminated += 1
                        changed = True

        return PassResult(changed=changed, impact=impact)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Object lifetime optimization: eliminate dead allocas"
