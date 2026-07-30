"""
Legalization — converts illegal operations to target-legal ones.

Handles unsupported types (i128 -> pairs, i1 -> i8), unsupported operations
(divide on ARM64), and expands/narrows/promotes operations as needed.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

from compiler.ir.lir import (
    LIRBlock,
    LIRFunction,
    LIRInstKind,
    LIRInstruction,
)

if TYPE_CHECKING:
    from compiler.native.target.kind import TargetKind


class LegalizationError(Exception):
    """Raised when an operation cannot be legalized for the target."""


class LegalizationAction(Enum):
    """The action required to legalize an operation."""

    LEGAL = auto()
    EXPAND = auto()
    NARROW = auto()
    PROMOTE = auto()
    REPLACE = auto()
    CUSTOM = auto()


class Legalizer:
    """Converts illegal LIR operations to target-legal equivalents.

    Performs type legalization (e.g., i128 -> two i64) and operation
    legalization (e.g., divide on ARM64) before instruction selection.
    """

    __slots__ = ("_target_kind", "_warnings")

    def __init__(self, target_kind: TargetKind) -> None:
        self._target_kind = target_kind
        self._warnings: list[str] = []

    @property
    def warnings(self) -> list[str]:
        return list(self._warnings)

    def legalize_function(self, function: LIRFunction) -> LIRFunction:
        """Legalize all operations in *function* for the target.

        Returns a new LIRFunction with legalized instructions.
        """
        result = LIRFunction(function.name)
        result._return_type = function.return_type

        for param_name, param_type in function.params:
            result._params.append((param_name, param_type))

        result._num_locals = function.num_locals
        result._is_leaf = function.is_leaf

        for block in function:
            new_block = LIRBlock(block.label)
            result.append_block(new_block)
            for inst in block:
                legal = self._legalize_inst(inst, result, new_block)
                if legal:
                    if isinstance(legal, list):
                        for li in legal:
                            new_block.append(li)
                    else:
                        new_block.append(legal)

        self._rebuild_cfg(result)
        return result

    def _legalize_inst(
        self,
        inst: LIRInstruction,
        func: LIRFunction,
        block: LIRBlock,
    ) -> LIRInstruction | list[LIRInstruction] | None:
        kind = inst.kind
        dest = inst.dest if inst.dest else None
        ops = inst.operands

        # ── Type legalization: i1 is not natively supported ───────────
        if kind in (
            LIRInstKind.IADD, LIRInstKind.ISUB, LIRInstKind.IMUL,
            LIRInstKind.IDIV, LIRInstKind.IMOD,
            LIRInstKind.IAND, LIRInstKind.IOR, LIRInstKind.IXOR,
            LIRInstKind.ISHL, LIRInstKind.ISHR,
            LIRInstKind.MOVE,
        ):
            if dest and self._is_i1_operand(dest, func):
                return self._promote_i1_binop(inst, dest, ops)
            return inst

        if kind in (
            LIRInstKind.LOAD_VAR, LIRInstKind.LOAD_PARAM,
            LIRInstKind.LOAD_FIELD, LIRInstKind.LOAD_ELEMENT,
        ):
            if dest and self._is_i1_operand(dest, func):
                return self._promote_i1_load(inst, dest, ops)
            return inst

        if kind == LIRInstKind.RETURN and ops:
            if self._is_i1_operand(ops[0], func):
                return self._promote_i1_return(inst, ops)
            return inst

        # ── Target-specific legalization ──────────────────────────────
        if self._target_kind.value in ("arm64", "arm32"):
            return self._legalize_arm64(inst, kind, dest, ops, func, block)
        if self._target_kind.value in ("riscv64", "riscv32"):
            return self._legalize_riscv(inst, kind, dest, ops, func, block)

        return inst

    def _promote_i1_binop(
        self,
        inst: LIRInstruction,
        dest: str,
        ops: list[str],
    ) -> LIRInstruction:
        """Promote i1 operands to i8 for binary operations."""
        promoted_ops = []
        for op in ops:
            promoted_ops.append(f"{op}.i8")
        result = LIRInstruction(inst.kind, dest, promoted_ops)
        result.comment = "promoted i1 to i8"
        return result

    def _promote_i1_load(
        self,
        inst: LIRInstruction,
        dest: str,
        ops: list[str],
    ) -> LIRInstruction:
        """Promote i1 load to i8 load, then truncate."""
        tmp = f"{dest}.i8"
        load_i8 = LIRInstruction(inst.kind, tmp, ops)
        load_i8.comment = "promoted i1 load to i8"
        trunc = LIRInstruction(LIRInstKind.I2I, dest, [tmp])
        trunc.comment = "trunc i8 to i1"
        return [load_i8, trunc]

    def _promote_i1_return(
        self,
        inst: LIRInstruction,
        ops: list[str],
    ) -> list[LIRInstruction]:
        """Extend i1 return value to i8 before returning."""
        tmp = f"{ops[0]}.i8"
        ext = LIRInstruction(LIRInstKind.I2I, tmp, ops)
        ext.comment = "ext i1 to i8 for return"
        ret = LIRInstruction(LIRInstKind.RETURN, None, [tmp])
        return [ext, ret]

    def _is_i1_operand(self, name: str, func: LIRFunction) -> bool:
        """Check if an operand name corresponds to an i1 type."""
        for param_name, param_type in func.params:
            if param_name == name:
                return hasattr(param_type, 'kind') and param_type.kind.value == 'INTEGER'
        return False

    def _legalize_arm64(
        self,
        inst: LIRInstruction,
        kind: LIRInstKind,
        dest: str | None,
        ops: list[str],
        func: LIRFunction,
        block: LIRBlock,
    ) -> LIRInstruction | list[LIRInstruction] | None:
        """ARM64 legalization: expand SDIV/UDIV/IMOD that lack hardware support
        for certain forms, and handle i128."""
        if kind in (LIRInstKind.IDIV, LIRInstKind.IMOD):
            if len(ops) >= 2:
                return self._expand_sdiv_for_arm(inst, kind, dest, ops)
            return inst
        return inst

    def _expand_sdiv_for_arm(
        self,
        inst: LIRInstruction,
        kind: LIRInstKind,
        dest: str | None,
        ops: list[str],
    ) -> list[LIRInstruction]:
        """ARM64 has sdiv/udiv natively, but imod needs expansion.

        imod a, b -> t = sdiv a, b; result = a - t * b
        """
        if kind == LIRInstKind.IMOD:
            t = f"{dest}.quot"
            div = LIRInstruction(LIRInstKind.IDIV, t, ops)
            mul = LIRInstruction(LIRInstKind.IMUL, f"{dest}.mul", [t, ops[1]])
            sub = LIRInstruction(LIRInstKind.ISUB, dest, [ops[0], f"{dest}.mul"])
            div.comment = "expanded imod: div"
            mul.comment = "expanded imod: mul"
            sub.comment = "expanded imod: sub"
            return [div, mul, sub]
        return [inst]

    def _legalize_riscv(
        self,
        inst: LIRInstruction,
        kind: LIRInstKind,
        dest: str | None,
        ops: list[str],
        func: LIRFunction,
        block: LIRBlock,
    ) -> LIRInstruction | list[LIRInstruction] | None:
        """RISC-V legalization placeholder."""
        if kind in (LIRInstKind.IMUL, LIRInstKind.IDIV, LIRInstKind.IMOD):
            if len(ops) >= 2:
                return self._expand_sdiv_for_arm(inst, kind, dest, ops)
            return inst
        return inst

    def _rebuild_cfg(self, func: LIRFunction) -> None:
        """Rebuild predecessor/successor edges after legalization."""
        for block in func:
            block._predecessors.clear()
            block._successors.clear()

        block_map: dict[str, LIRBlock] = {
            block.label: block for block in func
        }

        for block in func:
            term = block.terminator
            if term is None:
                continue
            for op in term.operands:
                if op in block_map:
                    target = block_map[op]
                    block.add_successor(target)
                    target.add_predecessor(block)

    def legalize_module(
        self,
        functions: list[LIRFunction],
    ) -> list[LIRFunction]:
        """Legalize all functions in a list."""
        return [self.legalize_function(f) for f in functions]


def legalize_function(
    function: LIRFunction,
    target_kind: TargetKind,
) -> LIRFunction:
    """Convenience function to legalize a single function."""
    legalizer = Legalizer(target_kind)
    return legalizer.legalize_function(function)
