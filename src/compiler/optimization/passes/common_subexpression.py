from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Add, Sub, Mul, Load, Store
from compiler.ir.values import Value


class CommonSubexpressionEliminationPass(Pass):
    """Eliminates redundant identical computations within a basic block.

    When the same expression (same opcode, same operands) is computed twice,
    the second computation is replaced by referencing the first result.
    """

    def __init__(self) -> None:
        super().__init__("common_subexpression_elimination", level=2)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassResult()
        changed = False
        for func in module.functions.values():
            for bb in func.basic_blocks:
                exprs: dict[tuple, str] = {}
                to_remove: list = []
                for inst in bb.instructions:
                    key = self._expr_key(inst)
                    if key is not None and inst.name:
                        if key in exprs:
                            self._replace_uses(bb, inst.name, exprs[key])
                            to_remove.append(inst)
                            impact.impact.instructions_eliminated += 1
                            changed = True
                        else:
                            exprs[key] = inst.name
                for inst in to_remove:
                    bb.remove(inst)
        return PassResult(changed=changed, impact=impact.impact)

    def _replace_uses(self, bb, old_name: str, new_name: str) -> None:
        for inst in bb.instructions:
            for i, op in enumerate(inst.operands):
                if hasattr(op, "name") and op.name == old_name:
                    inst.set_operand(i, _make_proxy(new_name))

    def _expr_key(self, inst) -> tuple | None:
        if isinstance(inst, (Add, Sub, Mul)):
            a_name = inst.a.name if hasattr(inst.a, "name") else str(inst.a)
            b_name = inst.b.name if hasattr(inst.b, "name") else str(inst.b)
            op = type(inst).__name__
            return (op, a_name, b_name)
        if isinstance(inst, Load):
            ptr_name = inst.ptr.name if hasattr(inst, 'ptr') and hasattr(inst.ptr, 'name') else str(getattr(inst, 'ptr', ''))
            return ("load", ptr_name)
        return None

    def estimated_complexity(self) -> str:
        return "O(n^2)"

    def performance_impact(self) -> str:
        return "high"

    def description(self) -> str:
        return "Common subexpression elimination"


class _NameProxy:
    """Lightweight stand-in for a Value that has a name."""
    __slots__ = ("_name",)

    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name


def _make_proxy(new_name: str) -> _NameProxy:
    return _NameProxy(new_name)
