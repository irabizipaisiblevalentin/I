from __future__ import annotations
from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import (
    Call, Return, Branch, CondBranch, Add, Sub, Mul,
    Load, Store, Alloca, ICmp, ICmpPredicate, Unreachable,
)
from compiler.ir.values import IntConstant, Value


class FunctionInliningPass(Pass):
    """Inlines small single-block functions at their call sites.

    Strategy:
    1. Identify small callees (<= max_instructions, single basic block)
    2. For each call site, copy callee instructions inline
    3. Replace argument references with actual parameter values
    4. Replace Return with the caller's continuation
    """

    __slots__ = ("_max_instructions", "_max_depth")

    def __init__(self, max_instructions: int = 5, max_depth: int = 1) -> None:
        super().__init__("function_inlining", level=2)
        self._max_instructions = max_instructions
        self._max_depth = max_depth

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for _ in range(self._max_depth):
            did_inline = False
            for callee_name, callee_func in list(module.functions.items()):
                if callee_name.startswith("_") or callee_func.is_declaration:
                    continue
                total = sum(len(bb.instructions) for bb in callee_func.basic_blocks)
                total -= sum(1 for bb in callee_func.basic_blocks for i in bb.instructions if isinstance(i, Return))
                if total > self._max_instructions:
                    continue
                if len(callee_func.basic_blocks) != 1:
                    continue
                for caller_name, caller_func in list(module.functions.items()):
                    if caller_name == callee_name:
                        continue
                    for bb in list(caller_func.basic_blocks):
                        result = self._inline_callees(
                            module, caller_func, bb, callee_name, callee_func
                        )
                        if result:
                            did_inline = True
                            changed = True
                            impact.functions_inlined += 1
                            impact.instructions_eliminated += 1
            if not did_inline:
                break

        return PassResult(changed=changed, impact=impact)

    def _inline_callees(
        self, module, caller, bb, callee_name, callee_func
    ) -> bool:
        inlined = False
        for i, inst in enumerate(list(bb.instructions)):
            if not isinstance(inst, Call):
                continue
            call_callee = inst.function if hasattr(inst, 'function') else None
            if call_callee is None:
                continue
            call_name = call_callee.name if hasattr(call_callee, 'name') else str(call_callee)
            if call_name != callee_name:
                continue
            args = list(inst.args) if hasattr(inst, 'args') else []
            callee_bb = callee_func.basic_blocks[0]
            arg_map = {}
            for j, param in enumerate(callee_func.args):
                if j < len(args):
                    arg_map[param.name] = args[j]
            insert_point = bb.instructions.index(inst)
            for ci in callee_bb.instructions:
                new_inst = self._clone_instruction(ci, arg_map)
                if new_inst is None:
                    continue
                if isinstance(ci, Return) and inst.name:
                    if ci.value is not None:
                        mapped = self._map_operand(ci.value, arg_map)
                        from compiler.ir.instructions import Add
                        proxy = _NameProxy(inst.name)
                        store_like = Add(inst.name, mapped, IntConstant(0))
                        bb.instructions.insert(insert_point, store_like)
                        insert_point += 1
                    inlined = True
                else:
                    bb.instructions.insert(insert_point, new_inst)
                    insert_point += 1
            if inst in bb.instructions:
                bb.instructions.remove(inst)
            inlined = True
        return inlined

    def _clone_instruction(self, inst, arg_map):
        if isinstance(inst, Return):
            return None
        if isinstance(inst, Add):
            a = self._map_operand(inst.a, arg_map)
            b = self._map_operand(inst.b, arg_map)
            return Add(inst.name, a, b) if inst.name else None
        if isinstance(inst, Sub):
            a = self._map_operand(inst.a, arg_map)
            b = self._map_operand(inst.b, arg_map)
            return Sub(inst.name, a, b) if inst.name else None
        if isinstance(inst, Mul):
            a = self._map_operand(inst.a, arg_map)
            b = self._map_operand(inst.b, arg_map)
            return Mul(inst.name, a, b) if inst.name else None
        if isinstance(inst, Load):
            ptr = self._map_operand(inst.ptr, arg_map) if hasattr(inst, 'ptr') else None
            return Load(inst.name, ptr) if inst.name and ptr else None
        if isinstance(inst, ICmp):
            a = self._map_operand(inst.a, arg_map)
            b = self._map_operand(inst.b, arg_map)
            return ICmp(inst.name, inst.predicate, a, b) if inst.name else None
        if isinstance(inst, Alloca):
            return Alloca(inst.name, inst.alloca_type) if inst.name else None
        return None

    def _map_operand(self, operand, arg_map):
        if hasattr(operand, 'name') and operand.name in arg_map:
            return arg_map[operand.name]
        return operand

    def estimated_complexity(self) -> str:
        return "O(n * m)"

    def performance_impact(self) -> str:
        return "high"

    def description(self) -> str:
        return "Function inlining for small functions"


class _NameProxy:
    __slots__ = ("_name",)
    def __init__(self, name: str) -> None:
        self._name = name
    @property
    def name(self) -> str:
        return self._name
