"""
LIR — Low-Level Intermediate Representation

Prepares programs for VM, native compiler, bytecode generation,
and machine code generation. LIR resembles a portable assembly
language while remaining architecture-independent.

LIR is the final IR before target-specific code generation.
"""
from __future__ import annotations

from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

from .module import IRModule
from .function import IRFunction
from .basic_block import BasicBlock
from .types import IRType, IRVoid
from .values import Value, Constant, IntConstant
from .instructions import Instruction

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple


# ══════════════════════════════════════════════════════════════════
# LIR Instruction Kinds
# ══════════════════════════════════════════════════════════════════


class LIRInstKind(Enum):
    """LIR instruction categories (portable assembly style)."""
    # Data movement
    LOAD_CONST = auto()
    LOAD_VAR = auto()
    STORE_VAR = auto()
    LOAD_PARAM = auto()
    LOAD_FIELD = auto()
    STORE_FIELD = auto()
    LOAD_ELEMENT = auto()
    STORE_ELEMENT = auto()
    LOAD_GLOBAL = auto()
    STORE_GLOBAL = auto()
    MOVE = auto()
    SWAP = auto()
    # Arithmetic
    IADD = auto()
    ISUB = auto()
    IMUL = auto()
    IDIV = auto()
    IMOD = auto()
    FADD = auto()
    FSUB = auto()
    FMUL = auto()
    FDIV = auto()
    # Bitwise
    IAND = auto()
    IOR = auto()
    IXOR = auto()
    ISHL = auto()
    ISHR = auto()
    # Comparison
    ICMP_EQ = auto()
    ICMP_NE = auto()
    ICMP_LT = auto()
    ICMP_LE = auto()
    ICMP_GT = auto()
    ICMP_GE = auto()
    FCMP_EQ = auto()
    FCMP_NE = auto()
    FCMP_LT = auto()
    FCMP_LE = auto()
    FCMP_GT = auto()
    FCMP_GE = auto()
    # Conversion
    I2F = auto()
    F2I = auto()
    I2I = auto()
    F2F = auto()
    I2P = auto()
    P2I = auto()
    # Control flow
    BR = auto()
    BREQ = auto()
    BRNE = auto()
    BRLT = auto()
    BRGE = auto()
    RETURN = auto()
    CALL = auto()
    TAIL_CALL = auto()
    # Stack
    PUSH = auto()
    POP = auto()
    ALLOCA = auto()
    FREE = auto()
    # Atomic
    CAS = auto()
    ATOMIC_LOAD = auto()
    ATOMIC_STORE = auto()
    # Special
    NOP = auto()
    UNREACHABLE = auto()
    PHI = auto()


# ══════════════════════════════════════════════════════════════════
# LIR Instruction
# ══════════════════════════════════════════════════════════════════


class LIRInstruction:
    """A single LIR instruction — portable assembly style."""
    __slots__ = ("_kind", "_dest", "_operands", "_source_ref",
                 "_is_debug", "_comment")

    def __init__(
        self,
        kind: LIRInstKind,
        dest: Optional[str] = None,
        operands: Optional[List[str]] = None,
    ) -> None:
        object.__setattr__(self, "_kind", kind)
        object.__setattr__(self, "_dest", dest)
        object.__setattr__(self, "_operands", list(operands) if operands else [])
        object.__setattr__(self, "_source_ref", None)
        object.__setattr__(self, "_is_debug", False)
        object.__setattr__(self, "_comment", "")

    @property
    def kind(self) -> LIRInstKind:
        return self._kind

    @property
    def dest(self) -> Optional[str]:
        return self._dest

    @property
    def operands(self) -> List[str]:
        return list(self._operands)

    @property
    def source_ref(self):
        return self._source_ref

    @source_ref.setter
    def source_ref(self, ref) -> None:
        object.__setattr__(self, "_source_ref", ref)

    @property
    def is_debug(self) -> bool:
        return self._is_debug

    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, value: str) -> None:
        object.__setattr__(self, "_comment", value)

    @property
    def is_terminator(self) -> bool:
        return self._kind in (
            LIRInstKind.RETURN, LIRInstKind.BR, LIRInstKind.BREQ,
            LIRInstKind.BRNE, LIRInstKind.BRLT, LIRInstKind.BRGE,
            LIRInstKind.UNREACHABLE,
        )

    @property
    def is_branch(self) -> bool:
        return self._kind in (
            LIRInstKind.BR, LIRInstKind.BREQ, LIRInstKind.BRNE,
            LIRInstKind.BRLT, LIRInstKind.BRGE,
        )

    def __repr__(self) -> str:
        dest = f"{self._dest} = " if self._dest else ""
        ops = ", ".join(self._operands)
        return f"{dest}{self._kind.name} {ops}"


# ══════════════════════════════════════════════════════════════════
# LIR Basic Block
# ══════════════════════════════════════════════════════════════════


class LIRBlock:
    """A basic block in LIR — sequence of LIR instructions."""
    __slots__ = ("_label", "_instructions", "_predecessors", "_successors")

    def __init__(self, label: str = "") -> None:
        object.__setattr__(self, "_label", label)
        object.__setattr__(self, "_instructions", [])
        object.__setattr__(self, "_predecessors", [])
        object.__setattr__(self, "_successors", [])

    @property
    def label(self) -> str:
        return self._label

    @property
    def instructions(self) -> List[LIRInstruction]:
        return list(self._instructions)

    @property
    def predecessors(self) -> List[LIRBlock]:
        return list(self._predecessors)

    @property
    def successors(self) -> List[LIRBlock]:
        return list(self._successors)

    @property
    def terminator(self) -> Optional[LIRInstruction]:
        if self._instructions and self._instructions[-1].is_terminator:
            return self._instructions[-1]
        return None

    @property
    def instruction_count(self) -> int:
        return len(self._instructions)

    def append(self, inst: LIRInstruction) -> None:
        self._instructions.append(inst)

    def add_predecessor(self, block: LIRBlock) -> None:
        if block not in self._predecessors:
            self._predecessors.append(block)

    def add_successor(self, block: LIRBlock) -> None:
        if block not in self._successors:
            self._successors.append(block)

    def __repr__(self) -> str:
        return f"LIRBlock({self._label}, {self.instruction_count} insts)"

    def __iter__(self):
        return iter(self._instructions)


# ══════════════════════════════════════════════════════════════════
# LIR Function
# ══════════════════════════════════════════════════════════════════


class LIRFunction:
    """LIR function — collection of LIR basic blocks."""
    __slots__ = ("_name", "_blocks", "_params", "_return_type",
                 "_num_locals", "_is_leaf")

    def __init__(self, name: str) -> None:
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_blocks", [])
        object.__setattr__(self, "_params", [])
        object.__setattr__(self, "_return_type", IRVoid())
        object.__setattr__(self, "_num_locals", 0)
        object.__setattr__(self, "_is_leaf", False)

    @property
    def name(self) -> str:
        return self._name

    @property
    def blocks(self) -> List[LIRBlock]:
        return list(self._blocks)

    @property
    def params(self) -> List[Tuple[str, IRType]]:
        return list(self._params)

    @property
    def return_type(self) -> IRType:
        return self._return_type

    @property
    def num_locals(self) -> int:
        return self._num_locals

    @property
    def is_leaf(self) -> bool:
        return self._is_leaf

    @property
    def entry_block(self) -> Optional[LIRBlock]:
        return self._blocks[0] if self._blocks else None

    @property
    def block_count(self) -> int:
        return len(self._blocks)

    def append_block(self, block: LIRBlock) -> None:
        self._blocks.append(block)

    def allocate_local(self) -> int:
        """Allocate a new local variable slot."""
        n = self._num_locals
        self._num_locals += 1
        return n

    def __iter__(self):
        return iter(self._blocks)

    def __repr__(self) -> str:
        return f"LIRFunction({self._name}, {self.block_count} blocks)"


# ══════════════════════════════════════════════════════════════════
# LIR Module
# ══════════════════════════════════════════════════════════════════


class LIRModule:
    """LIR module — final portable assembly representation."""
    __slots__ = ("_name", "_functions", "_globals", "_target_info")

    def __init__(self, name: str = "") -> None:
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_functions", [])
        object.__setattr__(self, "_globals", [])
        object.__setattr__(self, "_target_info", {})

    @property
    def name(self) -> str:
        return self._name

    @property
    def functions(self) -> List[LIRFunction]:
        return list(self._functions)

    @property
    def globals(self) -> List:
        return list(self._globals)

    @property
    def target_info(self) -> dict:
        return dict(self._target_info)

    @property
    def function_count(self) -> int:
        return len(self._functions)

    def add_function(self, func: LIRFunction) -> None:
        self._functions.append(func)

    def get_function(self, name: str) -> Optional[LIRFunction]:
        for f in self._functions:
            if f.name == name:
                return f
        return None

    def __repr__(self) -> str:
        return f"LIRModule({self._name}, {len(self._functions)} functions)"


# ══════════════════════════════════════════════════════════════════
# LIR Printer
# ══════════════════════════════════════════════════════════════════


class LIRPrinter:
    """Prints LIR in text format."""
    __slots__ = ()

    def print_module(self, module: LIRModule) -> str:
        """Print a complete LIR module."""
        lines = [f"; LIR Module: {module.name}", ""]
        for func in module.functions:
            lines.append(self.print_function(func))
            lines.append("")
        return "\n".join(lines)

    def print_function(self, func: LIRFunction) -> str:
        """Print a single LIR function."""
        params = ", ".join(
            f"{t} %{n}" for n, t in func.params
        )
        lines = [f"function @{func.name}({params}) -> {func.return_type} {{"]

        for block in func:
            lines.append(f"  {block.label}:")
            for inst in block:
                lines.append(f"    {inst}")
            lines.append("")

        lines.append("}")
        return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
# LIR Builder
# ══════════════════════════════════════════════════════════════════


class LIRBuilder:
    """Fluent API for building LIR instructions."""
    __slots__ = ("_block", "_func")

    def __init__(self) -> None:
        object.__setattr__(self, "_block", None)
        object.__setattr__(self, "_func", None)

    def position_at(self, block: LIRBlock) -> None:
        object.__setattr__(self, "_block", block)

    def set_function(self, func: LIRFunction) -> None:
        object.__setattr__(self, "_func", func)

    def emit(self, kind: LIRInstKind, dest: Optional[str] = None,
             operands: Optional[List[str]] = None) -> LIRInstruction:
        """Emit an instruction at the current position."""
        inst = LIRInstruction(kind, dest, operands)
        if self._block:
            self._block.append(inst)
        return inst

    def emit_br(self, target: str) -> LIRInstruction:
        return self.emit(LIRInstKind.BR, operands=[target])

    def emit_breq(self, cond: str, target: str) -> LIRInstruction:
        return self.emit(LIRInstKind.BREQ, operands=[cond, target])

    def emit_ret(self, value: Optional[str] = None) -> LIRInstruction:
        return self.emit(LIRInstKind.RETURN, operands=[value] if value else [])

    def emit_iadd(self, dest: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.IADD, dest, [lhs, rhs])

    def emit_isub(self, dest: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.ISUB, dest, [lhs, rhs])

    def emit_imul(self, dest: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.IMUL, dest, [lhs, rhs])

    def emit_move(self, dest: str, src: str) -> LIRInstruction:
        return self.emit(LIRInstKind.MOVE, dest, [src])

    def emit_load_const(self, dest: str, value: str) -> LIRInstruction:
        return self.emit(LIRInstKind.LOAD_CONST, dest, [value])

    def emit_idiv(self, dest: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.IDIV, dest, [lhs, rhs])

    def emit_imod(self, dest: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.IMOD, dest, [lhs, rhs])

    def emit_fadd(self, dest: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.FADD, dest, [lhs, rhs])

    def emit_fsub(self, dest: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.FSUB, dest, [lhs, rhs])

    def emit_fmul(self, dest: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.FMUL, dest, [lhs, rhs])

    def emit_fdiv(self, dest: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.FDIV, dest, [lhs, rhs])

    def emit_iand(self, dest: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.IAND, dest, [lhs, rhs])

    def emit_ior(self, dest: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.IOR, dest, [lhs, rhs])

    def emit_ixor(self, dest: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.IXOR, dest, [lhs, rhs])

    def emit_icmp(self, dest: str, pred: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.ICMP_EQ, dest, [pred, lhs, rhs])

    def emit_fcmp(self, dest: str, pred: str, lhs: str, rhs: str) -> LIRInstruction:
        return self.emit(LIRInstKind.FCMP_EQ, dest, [pred, lhs, rhs])

    def emit_load_var(self, dest: str, ptr: str) -> LIRInstruction:
        return self.emit(LIRInstKind.LOAD_VAR, dest, [ptr])

    def emit_store_var(self, value: str, ptr: str) -> LIRInstruction:
        return self.emit(LIRInstKind.STORE_VAR, None, [value, ptr])

    def emit_call(self, dest: Optional[str], callee: str,
                  args: Optional[List[str]] = None) -> LIRInstruction:
        return self.emit(LIRInstKind.CALL, dest, [callee] + (args or []))

    def emit_alloca(self, dest: str, size: str) -> LIRInstruction:
        return self.emit(LIRInstKind.ALLOCA, dest, [size])

    def emit_brne(self, cond: str, target: str) -> LIRInstruction:
        return self.emit(LIRInstKind.BRNE, None, [cond, target])

    def create_block(self, label: str = "") -> LIRBlock:
        n = label or f"bb{self._func.block_count if self._func else 0}"
        block = LIRBlock(n)
        if self._func:
            self._func.append_block(block)
        return block


# ══════════════════════════════════════════════════════════════════
# Lowering Utilities
# ══════════════════════════════════════════════════════════════════


def lower_ir_to_lir(ir_module: IRModule) -> LIRModule:
    """Lower an IR module to LIR (simplified version).

    Full lowering would handle:
    - Register allocation
    - Instruction selection
    - Stack frame layout
    - Calling convention application
    """
    lir_module = LIRModule(ir_module.name)

    for ir_func in ir_module.functions:
        lir_func = LIRFunction(ir_func.name)
        lir_func._return_type = ir_func.return_type

        entry = LIRBlock("entry")
        lir_func.append_block(entry)

        current_block = entry
        for i, block in enumerate(ir_func):
            if i > 0:
                current_block = LIRBlock(block.name)
                lir_func.append_block(current_block)
            for inst in block:
                lir_inst = _lower_instruction(inst)
                if lir_inst:
                    if isinstance(lir_inst, list):
                        for li in lir_inst:
                            current_block.append(li)
                    else:
                        current_block.append(lir_inst)

        lir_module.add_function(lir_func)

    return lir_module


def _lower_instruction(inst: Instruction):
    from .instructions import (
        Add, Sub, Mul, SDiv, UDiv, SRem, URem,
        FAdd, FSub, FMul, FDiv, FRem,
        And, Or, Xor, Shl, LShr, AShr,
        Not, Neg, FNeg,
        ICmp, FCmp,
        Alloca, Load, Store, GEP, MemCpy, MemSet,
        Trunc, ZExt, SExt, FPTrunc, FPExt,
        UIToFP, SIToFP, FPToUI, FPToSI,
        PtrToInt, IntToPtr, BitCast, AddrSpaceCast,
        Phi, Call, Invoke, LandingPad, Resume,
        ExtractValue, InsertValue,
        ExtractElement, InsertElement, ShuffleVector,
        AtomicRMW, CmpXchg, Fence,
        Branch, CondBranch, Return, Unreachable, Switch,
    )

    name = inst.name or None

    if isinstance(inst, (Add, Sub, Mul)):
        op_map = {Add: LIRInstKind.IADD, Sub: LIRInstKind.ISUB, Mul: LIRInstKind.IMUL}
        return LIRInstruction(op_map[type(inst)], inst.name,
                              [inst.lhs.name, inst.rhs.name])

    if isinstance(inst, (SDiv, UDiv)):
        return LIRInstruction(LIRInstKind.IDIV, inst.name,
                              [inst.lhs.name, inst.rhs.name])

    if isinstance(inst, (SRem, URem)):
        return LIRInstruction(LIRInstKind.IMOD, inst.name,
                              [inst.lhs.name, inst.rhs.name])

    if isinstance(inst, (FAdd, FSub, FMul, FDiv)):
        op_map = {FAdd: LIRInstKind.FADD, FSub: LIRInstKind.FSUB,
                  FMul: LIRInstKind.FMUL, FDiv: LIRInstKind.FDIV}
        return LIRInstruction(op_map[type(inst)], inst.name,
                              [inst.lhs.name, inst.rhs.name])

    if isinstance(inst, FRem):
        return LIRInstruction(LIRInstKind.FDIV, inst.name,
                              [inst.lhs.name, inst.rhs.name])

    if isinstance(inst, (And, Or, Xor)):
        op_map = {And: LIRInstKind.IAND, Or: LIRInstKind.IOR, Xor: LIRInstKind.IXOR}
        return LIRInstruction(op_map[type(inst)], inst.name,
                              [inst.lhs.name, inst.rhs.name])

    if isinstance(inst, (Shl, LShr, AShr)):
        return LIRInstruction(LIRInstKind.ISHL, inst.name,
                              [inst.lhs.name, inst.rhs.name])

    if isinstance(inst, Not):
        return LIRInstruction(LIRInstKind.IXOR, inst.name,
                              [inst.operand.name, "-1"])

    if isinstance(inst, Neg):
        return LIRInstruction(LIRInstKind.ISUB, inst.name,
                              ["0", inst.operand.name])

    if isinstance(inst, FNeg):
        return LIRInstruction(LIRInstKind.FSUB, inst.name,
                              ["0.0", inst.operand.name])

    if isinstance(inst, ICmp):
        pred_map = {
            'EQ': LIRInstKind.ICMP_EQ, 'NE': LIRInstKind.ICMP_NE,
            'SLT': LIRInstKind.ICMP_LT, 'SLE': LIRInstKind.ICMP_LE,
            'SGT': LIRInstKind.ICMP_GT, 'SGE': LIRInstKind.ICMP_GE,
            'ULT': LIRInstKind.ICMP_LT, 'ULE': LIRInstKind.ICMP_LE,
            'UGT': LIRInstKind.ICMP_GT, 'UGE': LIRInstKind.ICMP_GE,
        }
        kind = pred_map.get(inst.predicate.name, LIRInstKind.ICMP_EQ)
        return LIRInstruction(kind, inst.name,
                              [inst.lhs.name, inst.rhs.name])

    if isinstance(inst, FCmp):
        pred_map = {
            'OEQ': LIRInstKind.FCMP_EQ, 'ONE': LIRInstKind.FCMP_NE,
            'OLT': LIRInstKind.FCMP_LT, 'OLE': LIRInstKind.FCMP_LE,
            'OGT': LIRInstKind.FCMP_GT, 'OGE': LIRInstKind.FCMP_GE,
            'UEQ': LIRInstKind.FCMP_EQ, 'UNE': LIRInstKind.FCMP_NE,
            'ULT': LIRInstKind.FCMP_LT, 'ULE': LIRInstKind.FCMP_LE,
            'UGT': LIRInstKind.FCMP_GT, 'UGE': LIRInstKind.FCMP_GE,
            'TRUE': LIRInstKind.ICMP_EQ, 'FALSE': LIRInstKind.ICMP_NE,
            'ORD': LIRInstKind.ICMP_EQ, 'UNO': LIRInstKind.ICMP_NE,
        }
        kind = pred_map.get(inst.predicate.name, LIRInstKind.FCMP_EQ)
        return LIRInstruction(kind, inst.name,
                              [inst.lhs.name, inst.rhs.name])

    if isinstance(inst, Alloca):
        return LIRInstruction(LIRInstKind.ALLOCA, inst.name,
                              [str(inst.allocated_type)])

    if isinstance(inst, Load):
        return LIRInstruction(LIRInstKind.LOAD_VAR, inst.name,
                              [inst.pointer.name])

    if isinstance(inst, Store):
        return LIRInstruction(LIRInstKind.STORE_VAR, None,
                              [inst.value.name, inst.pointer.name])

    if isinstance(inst, GEP):
        indices = [idx.name for idx in inst.indices]
        return LIRInstruction(LIRInstKind.LOAD_ELEMENT, inst.name,
                              [inst.pointer.name] + indices)

    if isinstance(inst, MemCpy):
        return LIRInstruction(LIRInstKind.NOP, None, [])

    if isinstance(inst, MemSet):
        return LIRInstruction(LIRInstKind.NOP, None, [])

    if isinstance(inst, (Trunc, ZExt, SExt, BitCast, AddrSpaceCast)):
        return LIRInstruction(LIRInstKind.I2I, inst.name,
                              [inst.source_value.name])

    if isinstance(inst, (FPTrunc, FPExt)):
        return LIRInstruction(LIRInstKind.F2F, inst.name,
                              [inst.source_value.name])

    if isinstance(inst, (UIToFP, SIToFP)):
        return LIRInstruction(LIRInstKind.I2F, inst.name,
                              [inst.source_value.name])

    if isinstance(inst, (FPToUI, FPToSI)):
        return LIRInstruction(LIRInstKind.F2I, inst.name,
                              [inst.source_value.name])

    if isinstance(inst, PtrToInt):
        return LIRInstruction(LIRInstKind.P2I, inst.name,
                              [inst.source_value.name])

    if isinstance(inst, IntToPtr):
        return LIRInstruction(LIRInstKind.I2P, inst.name,
                              [inst.source_value.name])

    if isinstance(inst, Phi):
        pairs = []
        for val, block in inst.incoming:
            pairs.append(f"{val.name}:{block.name}")
        return LIRInstruction(LIRInstKind.PHI, inst.name, pairs)

    if isinstance(inst, Call):
        args = [arg.name for arg in inst.arguments]
        return LIRInstruction(LIRInstKind.CALL, inst.name,
                              [inst.function.name] + args)

    if isinstance(inst, Invoke):
        args = [arg.name for arg in inst.arguments]
        return LIRInstruction(LIRInstKind.CALL, inst.name,
                              [inst.function.name] + args +
                              [inst.normal_block.name, inst.unwind_block.name])

    if isinstance(inst, Switch):
        result = []
        for case_val, case_block in inst.cases:
            cmp_name = f"{inst.name}_cmp" if inst.name else "sw_cmp"
            result.append(LIRInstruction(
                LIRInstKind.ICMP_EQ, cmp_name,
                [inst.value.name, case_val.name]
            ))
            result.append(LIRInstruction(
                LIRInstKind.BREQ, None, [cmp_name, case_block.name]
            ))
        result.append(LIRInstruction(
            LIRInstKind.BR, None, [inst.default.name]
        ))
        return result

    if isinstance(inst, Unreachable):
        return LIRInstruction(LIRInstKind.UNREACHABLE, None, [])

    if isinstance(inst, Return):
        val = inst.value.name if inst.value else None
        return LIRInstruction(LIRInstKind.RETURN, None, [val] if val else [])

    if isinstance(inst, Branch):
        return LIRInstruction(LIRInstKind.BR, None, [inst.target.name])

    if isinstance(inst, CondBranch):
        return [
            LIRInstruction(LIRInstKind.BREQ, None,
                           [inst.condition.name, inst.true_block.name]),
            LIRInstruction(LIRInstKind.BR, None,
                           [inst.false_block.name]),
        ]

    if isinstance(inst, LandingPad):
        return LIRInstruction(LIRInstKind.NOP, inst.name, [])

    if isinstance(inst, Resume):
        return LIRInstruction(LIRInstKind.NOP, None, [])

    if isinstance(inst, ExtractValue):
        indices = [str(i) for i in inst.indices]
        return LIRInstruction(LIRInstKind.LOAD_ELEMENT, inst.name,
                              [inst.aggregate.name] + indices)

    if isinstance(inst, InsertValue):
        indices = [str(i) for i in inst.indices]
        return LIRInstruction(LIRInstKind.STORE_ELEMENT, None,
                              [inst.element.name, inst.aggregate.name] + indices)

    if isinstance(inst, ExtractElement):
        return LIRInstruction(LIRInstKind.LOAD_ELEMENT, inst.name,
                              [inst.operands[0].name, inst.operands[1].name])

    if isinstance(inst, InsertElement):
        return LIRInstruction(LIRInstKind.STORE_ELEMENT, None,
                              [inst.operands[1].name, inst.operands[0].name,
                               inst.operands[2].name])

    if isinstance(inst, ShuffleVector):
        return LIRInstruction(LIRInstKind.NOP, inst.name, [])

    if isinstance(inst, AtomicRMW):
        return LIRInstruction(LIRInstKind.NOP, inst.name, [])

    if isinstance(inst, CmpXchg):
        return LIRInstruction(LIRInstKind.NOP, inst.name, [])

    if isinstance(inst, Fence):
        return LIRInstruction(LIRInstKind.NOP, None, [])

    return LIRInstruction(LIRInstKind.NOP, name)
