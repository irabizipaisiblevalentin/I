from __future__ import annotations

from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Store


class RedundantStoreEliminationPass(Pass):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("redundant_store_elimination", level=2)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            for bb in func.basic_blocks:
                stores: dict[str, str] = {}
                to_remove: list = []
                for inst in bb.instructions:
                    if isinstance(inst, Store):
                        ptr = getattr(inst, 'ptr', None)
                        val = getattr(inst, 'value', None)
                        ptr_name = ptr.name if ptr is not None and hasattr(ptr, 'name') else None
                        val_name = val.name if val is not None and hasattr(val, 'name') else str(val)
                        if ptr_name:
                            if ptr_name in stores and stores[ptr_name] == val_name:
                                to_remove.append(inst)
                                impact.instructions_eliminated += 1
                                changed = True
                            else:
                                stores[ptr_name] = val_name
                    elif hasattr(inst, 'name'):
                        ptr_name = None
                        for attr in ['ptr', 'addr', 'location']:
                            p = getattr(inst, attr, None)
                            if p is not None and hasattr(p, 'name'):
                                ptr_name = p.name
                                break
                        if ptr_name and ptr_name in stores:
                            del stores[ptr_name]
                for inst in to_remove:
                    bb.remove(inst)
        return PassResult(changed=changed, impact=impact)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Redundant store elimination"
