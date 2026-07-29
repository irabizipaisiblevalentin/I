from __future__ import annotations

from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Load, Store


class RedundantLoadEliminationPass(Pass):
    """Eliminates redundant loads from the same pointer within a basic block.

    If a pointer is loaded twice without an intervening store, the second
    load is replaced by referencing the first load's result.
    """

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("redundant_load_elimination", level=2)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            for bb in func.basic_blocks:
                loads: dict[str, str] = {}
                to_remove: list = []
                for inst in bb.instructions:
                    if isinstance(inst, Load) and inst.name:
                        ptr = getattr(inst, 'ptr', None)
                        ptr_name = ptr.name if ptr is not None and hasattr(ptr, 'name') else None
                        if ptr_name and ptr_name in loads:
                            self._replace_uses_after(bb, inst.name, loads[ptr_name])
                            to_remove.append(inst)
                            impact.instructions_eliminated += 1
                            changed = True
                        elif ptr_name:
                            loads[ptr_name] = inst.name
                    elif isinstance(inst, Store):
                        ptr = getattr(inst, 'ptr', None) or getattr(inst, 'pointer', None)
                        ptr_name = ptr.name if ptr is not None and hasattr(ptr, 'name') else None
                        if ptr_name:
                            loads.pop(ptr_name, None)
                        for load_name in list(loads.keys()):
                            loads.pop(load_name, None)
                for inst in to_remove:
                    bb.remove(inst)

        return PassResult(changed=changed, impact=impact)

    def _replace_uses_after(self, bb, old_name: str, new_name: str) -> None:
        found_old = False
        for inst in bb.instructions:
            if hasattr(inst, 'name') and inst.name == old_name:
                found_old = True
            if not found_old:
                continue
            for attr in ('a', 'b', 'lhs', 'rhs', 'condition', 'value', 'ptr'):
                val = getattr(inst, attr, None)
                if val is not None and hasattr(val, 'name') and val.name == old_name:
                    proxy = _NameProxy(new_name)
                    object.__setattr__(inst, attr, proxy)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "high"

    def description(self) -> str:
        return "Redundant load elimination"


class _NameProxy:
    __slots__ = ("_name",)

    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name
