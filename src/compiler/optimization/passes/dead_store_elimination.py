from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Store, Load


class DeadStoreEliminationPass(Pass):
    """Removes stores to locations that are overwritten before use."""

    def __init__(self) -> None:
        super().__init__("dead_store_elimination", level=1)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            for bb in func.basic_blocks:
                last_store: dict[str, int] = {}
                stores: dict[str, Store] = {}
                to_remove: list[Store] = []
                for i, inst in enumerate(bb.instructions):
                    if isinstance(inst, Store):
                        ptr = getattr(inst, "ptr", None)
                        ptr_name = ptr.name if ptr is not None and hasattr(ptr, "name") else None
                        if ptr_name:
                            if ptr_name in last_store:
                                to_remove.append(stores[ptr_name])
                                impact.instructions_eliminated += 1
                            last_store[ptr_name] = i
                            stores[ptr_name] = inst
                    elif isinstance(inst, Load):
                        ptr = getattr(inst, "ptr", None)
                        ptr_name = ptr.name if ptr is not None and hasattr(ptr, "name") else None
                        if ptr_name and ptr_name in last_store:
                            del last_store[ptr_name]
                for inst in to_remove:
                    bb.remove(inst)
                    changed = True
        return PassResult(changed=changed, impact=impact)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Dead store elimination: remove dead stores"
