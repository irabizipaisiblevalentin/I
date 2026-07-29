from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Load, Store


class MemoryCoalescingPass(Pass):
    """Store-to-load forwarding: when a value is stored and immediately
    loaded from the same location, replace the load with the stored value."""

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("memory_coalescing", level=2)

    def run(self, module: IRModule, ctx: object) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            for bb in func.basic_blocks:
                i = 0
                while i < len(bb.instructions) - 1:
                    curr = bb.instructions[i]
                    nxt = bb.instructions[i + 1]
                    if isinstance(curr, Store) and isinstance(nxt, Load):
                        curr_ptr = getattr(curr, 'ptr', None) or getattr(curr, 'pointer', None)
                        nxt_ptr = getattr(nxt, 'ptr', None)
                        if (curr_ptr is not None and nxt_ptr is not None
                                and hasattr(curr_ptr, 'name') and hasattr(nxt_ptr, 'name')
                                and curr_ptr.name == nxt_ptr.name):
                            store_value = curr.value
                            if hasattr(nxt, 'name') and nxt.name:
                                self._replace_uses_in_block(bb, nxt.name, store_value)
                            bb._instructions.pop(i + 1)
                            impact.instructions_eliminated += 1
                            changed = True
                            continue
                    i += 1
        return PassResult(changed=changed, impact=impact)

    def _replace_uses_in_block(self, bb, old_name: str, new_value) -> None:
        for inst in bb.instructions:
            for attr in ('a', 'b', 'lhs', 'rhs', 'condition', 'value', 'ptr'):
                val = getattr(inst, attr, None)
                if val is not None and hasattr(val, 'name') and val.name == old_name:
                    object.__setattr__(inst, attr, new_value)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Memory coalescing: store-to-load forwarding"
