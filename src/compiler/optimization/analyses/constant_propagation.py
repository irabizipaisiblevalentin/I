from __future__ import annotations
from compiler.optimization.base import Analysis, AnalysisResult
from compiler.ir.module import IRModule
from compiler.ir.instructions import Instruction, Opcode
from compiler.ir.values import IntConstant, FloatConstant, BoolConstant, Argument


class ConstValue:
    __slots__ = ("value", "kind")

    def __init__(self, value: object, kind: str) -> None:
        self.value = value
        self.kind = kind


class ConstantPropagationResult(AnalysisResult):
    __slots__ = ("_constants", "_function_constants")

    def __init__(self, module: IRModule) -> None:
        super().__init__("constant_propagation")
        self._constants: dict[str, dict[str, object]] = {}
        self._function_constants: dict[str, dict[str, bool]] = {}
        self._compute(module)

    def _compute(self, module: IRModule) -> None:
        for fname, func in module.functions.items():
            consts: dict[str, object] = {}
            changed = True
            while changed:
                changed = False
                for bb in func.basic_blocks:
                    for inst in bb.instructions:
                        if not hasattr(inst, "name") or not inst.name:
                            continue
                        if inst.name in consts:
                            continue
                        if isinstance(inst, (Argument,)):
                            continue
                        if inst.opcode in (Opcode.ADD, Opcode.SUB, Opcode.MUL,
                                           Opcode.FADD, Opcode.FSUB, Opcode.FMUL):
                            lhs_val = self._resolve(inst.lhs, consts)
                            rhs_val = self._resolve(inst.rhs, consts)
                            if lhs_val is not None and rhs_val is not None:
                                result = self._eval_binary(inst.opcode, lhs_val, rhs_val)
                                if result is not None:
                                    consts[inst.name] = result
                                    changed = True
                        elif inst.opcode in (Opcode.SDIV, Opcode.UDIV, Opcode.FDIV):
                            lhs_val = self._resolve(inst.lhs, consts)
                            rhs_val = self._resolve(inst.rhs, consts)
                            if (lhs_val is not None and rhs_val is not None
                                    and rhs_val != 0 and rhs_val != 0.0):
                                result = self._eval_binary(inst.opcode, lhs_val, rhs_val)
                                if result is not None:
                                    consts[inst.name] = result
                                    changed = True
                        elif inst.opcode in (Opcode.SREM, Opcode.UREM, Opcode.FREM):
                            lhs_val = self._resolve(inst.lhs, consts)
                            rhs_val = self._resolve(inst.rhs, consts)
                            if (lhs_val is not None and rhs_val is not None
                                    and rhs_val != 0 and rhs_val != 0.0):
                                result = self._eval_binary(inst.opcode, lhs_val, rhs_val)
                                if result is not None:
                                    consts[inst.name] = result
                                    changed = True
                        elif inst.opcode in (Opcode.AND, Opcode.OR, Opcode.XOR,
                                             Opcode.SHL, Opcode.LSHR, Opcode.ASHR):
                            lhs_val = self._resolve(inst.lhs, consts)
                            rhs_val = self._resolve(inst.rhs, consts)
                            if isinstance(lhs_val, int) and isinstance(rhs_val, int):
                                result = self._eval_bitwise(inst.opcode, lhs_val, rhs_val)
                                if result is not None:
                                    consts[inst.name] = result
                                    changed = True
                        elif inst.opcode == Opcode.NOT:
                            operand_val = self._resolve(inst.operand, consts)
                            if isinstance(operand_val, bool):
                                consts[inst.name] = not operand_val
                                changed = True
                            elif isinstance(operand_val, int):
                                consts[inst.name] = ~operand_val
                                changed = True
                        elif inst.opcode == Opcode.NEG:
                            operand_val = self._resolve(inst.operand, consts)
                            if isinstance(operand_val, (int, float)):
                                consts[inst.name] = -operand_val
                                changed = True
                        elif inst.opcode == Opcode.FNEG:
                            operand_val = self._resolve(inst.operand, consts)
                            if isinstance(operand_val, float):
                                consts[inst.name] = -operand_val
                                changed = True
            is_const: dict[str, bool] = {}
            for n in consts:
                is_const[n] = True
            for arg in func.args:
                if arg.name:
                    is_const[arg.name] = False
            self._constants[fname] = consts
            self._function_constants[fname] = is_const

    def _resolve(self, val: object, consts: dict[str, object]) -> object | None:
        if val is None:
            return None
        if isinstance(val, bool):
            return val
        if isinstance(val, int):
            return val
        if isinstance(val, float):
            return val
        if isinstance(val, IntConstant):
            return val.value
        if isinstance(val, FloatConstant):
            return val.value
        if isinstance(val, BoolConstant):
            return val.value
        if hasattr(val, "name") and val.name in consts:
            return consts[val.name]
        if hasattr(val, "name"):
            return None
        return None

    def _eval_binary(self, opcode: Opcode, lhs: object, rhs: object) -> object | None:
        if opcode == Opcode.ADD:
            return lhs + rhs
        if opcode == Opcode.SUB:
            return lhs - rhs
        if opcode == Opcode.MUL:
            return lhs * rhs
        if opcode == Opcode.SDIV:
            if isinstance(rhs, int) and rhs == 0:
                return None
            return lhs // rhs
        if opcode == Opcode.UDIV:
            if isinstance(rhs, int) and rhs == 0:
                return None
            return lhs // rhs
        if opcode == Opcode.FDIV:
            if isinstance(rhs, float) and rhs == 0.0:
                return None
            return lhs / rhs
        if opcode == Opcode.SREM:
            if isinstance(rhs, int) and rhs == 0:
                return None
            return lhs % rhs
        if opcode == Opcode.UREM:
            if isinstance(rhs, int) and rhs == 0:
                return None
            return lhs % rhs
        if opcode == Opcode.FREM:
            if isinstance(rhs, float) and rhs == 0.0:
                return None
            return lhs % rhs
        if opcode == Opcode.FADD:
            return lhs + rhs
        if opcode == Opcode.FSUB:
            return lhs - rhs
        if opcode == Opcode.FMUL:
            return lhs * rhs
        return None

    def _eval_bitwise(self, opcode: Opcode, lhs: int, rhs: int) -> int | None:
        if opcode == Opcode.AND:
            return lhs & rhs
        if opcode == Opcode.OR:
            return lhs | rhs
        if opcode == Opcode.XOR:
            return lhs ^ rhs
        if opcode == Opcode.SHL:
            return lhs << rhs
        if opcode == Opcode.LSHR:
            return lhs >> rhs
        if opcode == Opcode.ASHR:
            return lhs >> rhs
        return None

    @property
    def constants(self) -> dict[str, dict[str, object]]:
        return self._constants

    def is_constant(self, func_name: str, value_name: str) -> bool:
        return value_name in self._constants.get(func_name, {})

    def get_constant(self, func_name: str, value_name: str) -> object | None:
        return self._constants.get(func_name, {}).get(value_name)

    def constant_values(self, func_name: str) -> dict[str, object]:
        return dict(self._constants.get(func_name, {}))


class ConstantPropagationAnalysis(Analysis):
    def __init__(self) -> None:
        super().__init__("constant_propagation")

    def run(self, module: IRModule, ctx) -> ConstantPropagationResult:
        return ConstantPropagationResult(module)

    def estimated_complexity(self) -> str:
        return "O(n^2)"

    def performance_impact(self) -> str:
        return "low"

    def description(self) -> str:
        return "Constant propagation and folding analysis"
