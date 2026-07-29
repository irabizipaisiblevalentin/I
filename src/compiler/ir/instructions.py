"""
IR Instructions

All instruction types for the three-level IR (HIR, MIR, LIR).
Each instruction produces a value (except terminators which transfer control).
Instructions are mutable: operands can change during optimization passes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

from .types import IRType, IRVoid, IR_LABEL
from .values import Value, Constant

if TYPE_CHECKING:
    from typing import List, Optional, Tuple
    from .basic_block import BasicBlock
    from .metadata import Metadata


# ══════════════════════════════════════════════════════════════════
# Opcode Enumeration
# ══════════════════════════════════════════════════════════════════


class Opcode(Enum):
    """All IR opcodes grouped by category."""
    # ── Terminators ──────────────────────
    BRANCH = auto()
    COND_BRANCH = auto()
    SWITCH = auto()
    RETURN = auto()
    UNREACHABLE = auto()
    # ── Arithmetic ───────────────────────
    ADD = auto()
    SUB = auto()
    MUL = auto()
    SDIV = auto()
    UDIV = auto()
    SREM = auto()
    UREM = auto()
    FADD = auto()
    FSUB = auto()
    FMUL = auto()
    FDIV = auto()
    FREM = auto()
    # ── Bitwise ──────────────────────────
    AND = auto()
    OR = auto()
    XOR = auto()
    SHL = auto()
    LSHR = auto()
    ASHR = auto()
    # ── Unary ────────────────────────────
    NOT = auto()
    NEG = auto()
    FNEG = auto()
    # ── Comparison ───────────────────────
    ICMP = auto()
    FCMP = auto()
    # ── Memory ───────────────────────────
    ALLOCA = auto()
    LOAD = auto()
    STORE = auto()
    GEP = auto()
    MEMCPY = auto()
    MEMSET = auto()
    # ── Cast ─────────────────────────────
    TRUNC = auto()
    ZEXT = auto()
    SEXT = auto()
    FPTRUNC = auto()
    FPEXT = auto()
    UITOFP = auto()
    SITOFP = auto()
    FPTOUI = auto()
    FPTOSI = auto()
    PTRTOINT = auto()
    INTTOPTR = auto()
    BITCAST = auto()
    ADDRSPACECAST = auto()
    # ── Control Flow ─────────────────────
    PHI = auto()
    CALL = auto()
    INVOKE = auto()
    LANDING_PAD = auto()
    # ── Aggregate ────────────────────────
    EXTRACT_VALUE = auto()
    INSERT_VALUE = auto()
    # ── Vector ───────────────────────────
    EXTRACT_ELEMENT = auto()
    INSERT_ELEMENT = auto()
    SHUFFLE_VECTOR = auto()
    # ── Atomic ───────────────────────────
    ATOMICRMW = auto()
    CMPXCHG = auto()
    FENCE = auto()
    # ── Exceptional ──────────────────────
    RESUME = auto()


# ══════════════════════════════════════════════════════════════════
# Comparison Predicates
# ══════════════════════════════════════════════════════════════════


class ICmpPredicate(Enum):
    """Integer comparison predicates."""
    EQ = auto()
    NE = auto()
    UGT = auto()
    UGE = auto()
    ULT = auto()
    ULE = auto()
    SGT = auto()
    SGE = auto()
    SLT = auto()
    SLE = auto()


class FCmpPredicate(Enum):
    """Floating-point comparison predicates."""
    FALSE = auto()
    OEQ = auto()
    OGT = auto()
    OGE = auto()
    OLT = auto()
    OLE = auto()
    ONE = auto()
    ORD = auto()
    UEQ = auto()
    UGT = auto()
    UGE = auto()
    ULT = auto()
    ULE = auto()
    UNE = auto()
    UNO = auto()
    TRUE = auto()


# ══════════════════════════════════════════════════════════════════
# Instruction (Abstract Base)
# ══════════════════════════════════════════════════════════════════


class Instruction(Value):
    """Base class for all IR instructions."""
    __slots__ = ("_opcode", "_operands", "_parent", "_metadata",
                 "_dbg_location")

    def __init__(
        self,
        name: str,
        opcode: Opcode,
        result_type: IRType,
        operands: Optional[List[Value]] = None,
    ) -> None:
        super().__init__(name, result_type)
        object.__setattr__(self, "_opcode", opcode)
        object.__setattr__(self, "_operands", list(operands) if operands else [])
        object.__setattr__(self, "_parent", None)
        object.__setattr__(self, "_metadata", {})
        object.__setattr__(self, "_dbg_location", None)

        for op in self._operands:
            if isinstance(op, Value):
                op.add_use(self)

    def _value_kind(self) -> 'ValueKind':
        from .values import ValueKind
        return ValueKind.INSTRUCTION

    @property
    def opcode(self) -> Opcode:
        return self._opcode

    @property
    def operands(self) -> List[Value]:
        return self._operands

    @property
    def parent(self) -> Optional[BasicBlock]:
        return self._parent

    @parent.setter
    def parent(self, block: Optional[BasicBlock]) -> None:
        object.__setattr__(self, "_parent", block)

    @property
    def result_type(self) -> IRType:
        return self._type

    @property
    def is_terminator(self) -> bool:
        return False

    @property
    def is_binary_op(self) -> bool:
        return False

    @property
    def is_comparison(self) -> bool:
        return False

    @property
    def is_memory_op(self) -> bool:
        return False

    @property
    def is_cast(self) -> bool:
        return False

    @property
    def dbg_location(self) -> Optional[Metadata]:
        return self._dbg_location

    @dbg_location.setter
    def dbg_location(self, loc: Optional[Metadata]) -> None:
        object.__setattr__(self, "_dbg_location", loc)

    def set_operand(self, index: int, value: Value) -> None:
        """Replace an operand, updating use chains."""
        old = self._operands[index]
        if isinstance(old, Value):
            old.remove_use(self)
        self._operands[index] = value
        if isinstance(value, Value):
            value.add_use(self)

    def replace_uses_of(self, old_val: Value, new_val: Value) -> None:
        """Replace all uses of old_val with new_val in this instruction."""
        for i, op in enumerate(self._operands):
            if op is old_val:
                self.set_operand(i, new_val)

    def clone_metadata_from(self, other: Instruction) -> None:
        """Copy metadata from another instruction."""
        object.__setattr__(self, "_metadata", dict(other._metadata))
        object.__setattr__(self, "_dbg_location", other._dbg_location)

    def __repr__(self) -> str:
        ops = ", ".join(repr(o) for o in self._operands)
        return f"{self._name}: {self._type} = {self._opcode.name} {ops}"


class TerminatorInst(Instruction):
    """Base class for terminator instructions."""
    __slots__ = ()

    @property
    def is_terminator(self) -> bool:
        return True


# ══════════════════════════════════════════════════════════════════
# Terminator Instructions
# ══════════════════════════════════════════════════════════════════


class Branch(TerminatorInst):
    """Unconditional branch to a target block."""
    __slots__ = ()

    def __init__(self, target: BasicBlock) -> None:
        super().__init__("", Opcode.BRANCH, IRVoid(), [target])

    @property
    def target(self) -> BasicBlock:
        return self._operands[0]

    @target.setter
    def target(self, block: BasicBlock) -> None:
        self.set_operand(0, block)


class CondBranch(TerminatorInst):
    """Conditional branch: if condition then true_block else false_block."""
    __slots__ = ()

    def __init__(
        self,
        condition: Value,
        true_block: BasicBlock,
        false_block: BasicBlock,
    ) -> None:
        super().__init__("", Opcode.COND_BRANCH, IRVoid(),
                         [condition, true_block, false_block])

    @property
    def condition(self) -> Value:
        return self._operands[0]

    @condition.setter
    def condition(self, value: Value) -> None:
        self.set_operand(0, value)

    @property
    def true_block(self) -> BasicBlock:
        return self._operands[1]

    @property
    def false_block(self) -> BasicBlock:
        return self._operands[2]


class Switch(TerminatorInst):
    """Switch instruction."""
    __slots__ = ("_cases", "_default")

    def __init__(
        self,
        value: Value,
        default: BasicBlock,
        cases: Optional[List[Tuple[Constant, BasicBlock]]] = None,
    ) -> None:
        ops: List[Value] = [value, default]
        super().__init__("", Opcode.SWITCH, IRVoid(), ops)
        object.__setattr__(self, "_cases", list(cases) if cases else [])
        object.__setattr__(self, "_default", default)

    @property
    def value(self) -> Value:
        return self._operands[0]

    @property
    def default(self) -> BasicBlock:
        return self._default

    @property
    def cases(self) -> List[Tuple[Constant, BasicBlock]]:
        return self._cases


class Return(TerminatorInst):
    """Return instruction."""
    __slots__ = ()

    def __init__(self, value: Optional[Value] = None) -> None:
        ops: List[Value] = [value] if value is not None else []
        super().__init__("", Opcode.RETURN, IRVoid(), ops)

    @property
    def value(self) -> Optional[Value]:
        return self._operands[0] if self._operands else None


class Unreachable(TerminatorInst):
    """Unreachable — marks code that cannot execute."""
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("", Opcode.UNREACHABLE, IRVoid(), [])


# ══════════════════════════════════════════════════════════════════
# Binary Arithmetic Instructions
# ══════════════════════════════════════════════════════════════════


class BinaryOp(Instruction):
    """Base class for binary arithmetic/logic operations."""
    __slots__ = ()

    @property
    def is_binary_op(self) -> bool:
        return True

    @property
    def lhs(self) -> Value:
        return self._operands[0]

    @property
    def rhs(self) -> Value:
        return self._operands[1]

    @property
    def a(self) -> Value:
        """Alias for lhs — used by optimization passes."""
        return self._operands[0]

    @property
    def b(self) -> Value:
        """Alias for rhs — used by optimization passes."""
        return self._operands[1]


class Add(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.ADD, lhs.type, [lhs, rhs])


class Sub(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.SUB, lhs.type, [lhs, rhs])


class Mul(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.MUL, lhs.type, [lhs, rhs])


class SDiv(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.SDIV, lhs.type, [lhs, rhs])


class UDiv(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.UDIV, lhs.type, [lhs, rhs])


class SRem(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.SREM, lhs.type, [lhs, rhs])


class URem(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.UREM, lhs.type, [lhs, rhs])


class FAdd(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.FADD, lhs.type, [lhs, rhs])


class FSub(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.FSUB, lhs.type, [lhs, rhs])


class FMul(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.FMUL, lhs.type, [lhs, rhs])


class FDiv(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.FDIV, lhs.type, [lhs, rhs])


class FRem(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.FREM, lhs.type, [lhs, rhs])


# ══════════════════════════════════════════════════════════════════
# Bitwise Instructions
# ══════════════════════════════════════════════════════════════════


class And(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.AND, lhs.type, [lhs, rhs])


class Or(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.OR, lhs.type, [lhs, rhs])


class Xor(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.XOR, lhs.type, [lhs, rhs])


class Shl(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.SHL, lhs.type, [lhs, rhs])


class LShr(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.LSHR, lhs.type, [lhs, rhs])


class AShr(BinaryOp):
    def __init__(self, name: str, lhs: Value, rhs: Value) -> None:
        super().__init__(name, Opcode.ASHR, lhs.type, [lhs, rhs])


# ══════════════════════════════════════════════════════════════════
# Unary Instructions
# ══════════════════════════════════════════════════════════════════


class UnaryOp(Instruction):
    """Base class for unary operations."""
    __slots__ = ()

    @property
    def operand(self) -> Value:
        return self._operands[0]


class Not(UnaryOp):
    def __init__(self, name: str, operand: Value) -> None:
        super().__init__(name, Opcode.NOT, operand.type, [operand])


class Neg(UnaryOp):
    def __init__(self, name: str, operand: Value) -> None:
        super().__init__(name, Opcode.NEG, operand.type, [operand])


class FNeg(UnaryOp):
    def __init__(self, name: str, operand: Value) -> None:
        super().__init__(name, Opcode.FNEG, operand.type, [operand])


# ══════════════════════════════════════════════════════════════════
# Comparison Instructions
# ══════════════════════════════════════════════════════════════════


class ICmp(Instruction):
    """Integer comparison."""
    __slots__ = ("_predicate",)

    def __init__(
        self,
        name: str,
        predicate: ICmpPredicate,
        lhs: Value,
        rhs: Value,
    ) -> None:
        from .types import IR_I1
        super().__init__(name, Opcode.ICMP, IR_I1, [lhs, rhs])
        object.__setattr__(self, "_predicate", predicate)

    @property
    def is_comparison(self) -> bool:
        return True

    @property
    def predicate(self) -> ICmpPredicate:
        return self._predicate

    @property
    def lhs(self) -> Value:
        return self._operands[0]

    @property
    def rhs(self) -> Value:
        return self._operands[1]


class FCmp(Instruction):
    """Floating-point comparison."""
    __slots__ = ("_predicate",)

    def __init__(
        self,
        name: str,
        predicate: FCmpPredicate,
        lhs: Value,
        rhs: Value,
    ) -> None:
        from .types import IR_I1
        super().__init__(name, Opcode.FCMP, IR_I1, [lhs, rhs])
        object.__setattr__(self, "_predicate", predicate)

    @property
    def is_comparison(self) -> bool:
        return True

    @property
    def predicate(self) -> FCmpPredicate:
        return self._predicate

    @property
    def lhs(self) -> Value:
        return self._operands[0]

    @property
    def rhs(self) -> Value:
        return self._operands[1]


# ══════════════════════════════════════════════════════════════════
# Memory Instructions
# ══════════════════════════════════════════════════════════════════


class Alloca(Instruction):
    """Stack allocation."""
    __slots__ = ("_allocated_type", "_num_elements", "_alignment")

    def __init__(
        self,
        name: str,
        allocated_type: IRType,
        num_elements: Optional[Value] = None,
        alignment: int = 0,
    ) -> None:
        from .types import PointerType
        super().__init__(name, Opcode.ALLOCA, PointerType(allocated_type),
                         [num_elements] if num_elements else [])
        object.__setattr__(self, "_allocated_type", allocated_type)
        object.__setattr__(self, "_num_elements", num_elements)
        object.__setattr__(self, "_alignment", alignment)

    @property
    def allocated_type(self) -> IRType:
        return self._allocated_type

    @property
    def num_elements(self) -> Optional[Value]:
        return self._num_elements

    @property
    def alignment(self) -> int:
        return self._alignment

    @property
    def is_memory_op(self) -> bool:
        return True


class Load(Instruction):
    """Load value from memory."""
    __slots__ = ("_alignment", "_volatile")

    def __init__(
        self,
        name: str,
        pointee_type: IRType,
        pointer: Value,
        alignment: int = 0,
        volatile: bool = False,
    ) -> None:
        super().__init__(name, Opcode.LOAD, pointee_type, [pointer])
        object.__setattr__(self, "_alignment", alignment)
        object.__setattr__(self, "_volatile", volatile)

    @property
    def pointer(self) -> Value:
        return self._operands[0]

    @property
    def alignment(self) -> int:
        return self._alignment

    @property
    def volatile(self) -> bool:
        return self._volatile

    @property
    def is_memory_op(self) -> bool:
        return True


class Store(Instruction):
    """Store value to memory."""
    __slots__ = ("_alignment", "_volatile")

    def __init__(
        self,
        value: Value,
        pointer: Value,
        alignment: int = 0,
        volatile: bool = False,
    ) -> None:
        super().__init__("", Opcode.STORE, IRVoid(), [value, pointer])
        object.__setattr__(self, "_alignment", alignment)
        object.__setattr__(self, "_volatile", volatile)

    @property
    def value(self) -> Value:
        return self._operands[0]

    @property
    def pointer(self) -> Value:
        return self._operands[1]

    @property
    def ptr(self) -> Value:
        """Alias for pointer — used by optimization passes."""
        return self._operands[1]

    @property
    def alignment(self) -> int:
        return self._alignment

    @property
    def volatile(self) -> bool:
        return self._volatile

    @property
    def is_memory_op(self) -> bool:
        return True


class GEP(Instruction):
    """GetElementPtr — pointer arithmetic for array/struct indexing."""
    __slots__ = ("_source_type", "_in_bounds")

    def __init__(
        self,
        name: str,
        source_type: IRType,
        pointer: Value,
        indices: List[Value],
        in_bounds: bool = False,
    ) -> None:
        from .types import PointerType
        super().__init__(name, Opcode.GEP, PointerType(source_type),
                         [pointer] + indices)
        object.__setattr__(self, "_source_type", source_type)
        object.__setattr__(self, "_in_bounds", in_bounds)

    @property
    def source_type(self) -> IRType:
        return self._source_type

    @property
    def pointer(self) -> Value:
        return self._operands[0]

    @property
    def indices(self) -> List[Value]:
        return self._operands[1:]

    @property
    def in_bounds(self) -> bool:
        return self._in_bounds

    @property
    def is_memory_op(self) -> bool:
        return True


class MemCpy(Instruction):
    """Memory copy."""
    __slots__ = ("_is_volatile",)

    def __init__(
        self,
        dest: Value,
        src: Value,
        length: Value,
        is_volatile: bool = False,
    ) -> None:
        super().__init__("", Opcode.MEMCPY, IRVoid(), [dest, src, length])
        object.__setattr__(self, "_is_volatile", is_volatile)


class MemSet(Instruction):
    """Memory set."""
    __slots__ = ("_is_volatile",)

    def __init__(
        self,
        dest: Value,
        value: Value,
        length: Value,
        is_volatile: bool = False,
    ) -> None:
        super().__init__("", Opcode.MEMSET, IRVoid(), [dest, value, length])
        object.__setattr__(self, "_is_volatile", is_volatile)


# ══════════════════════════════════════════════════════════════════
# Cast Instructions
# ══════════════════════════════════════════════════════════════════


class CastInst(Instruction):
    """Base class for cast operations."""
    __slots__ = ()

    @property
    def is_cast(self) -> bool:
        return True

    @property
    def source_value(self) -> Value:
        return self._operands[0]


class Trunc(CastInst):
    def __init__(self, name: str, value: Value, dest_type: IRType) -> None:
        super().__init__(name, Opcode.TRUNC, dest_type, [value])


class ZExt(CastInst):
    def __init__(self, name: str, value: Value, dest_type: IRType) -> None:
        super().__init__(name, Opcode.ZEXT, dest_type, [value])


class SExt(CastInst):
    def __init__(self, name: str, value: Value, dest_type: IRType) -> None:
        super().__init__(name, Opcode.SEXT, dest_type, [value])


class FPTrunc(CastInst):
    def __init__(self, name: str, value: Value, dest_type: IRType) -> None:
        super().__init__(name, Opcode.FPTRUNC, dest_type, [value])


class FPExt(CastInst):
    def __init__(self, name: str, value: Value, dest_type: IRType) -> None:
        super().__init__(name, Opcode.FPEXT, dest_type, [value])


class UIToFP(CastInst):
    def __init__(self, name: str, value: Value, dest_type: IRType) -> None:
        super().__init__(name, Opcode.UITOFP, dest_type, [value])


class SIToFP(CastInst):
    def __init__(self, name: str, value: Value, dest_type: IRType) -> None:
        super().__init__(name, Opcode.SITOFP, dest_type, [value])


class FPToUI(CastInst):
    def __init__(self, name: str, value: Value, dest_type: IRType) -> None:
        super().__init__(name, Opcode.FPTOUI, dest_type, [value])


class FPToSI(CastInst):
    def __init__(self, name: str, value: Value, dest_type: IRType) -> None:
        super().__init__(name, Opcode.FPTOSI, dest_type, [value])


class PtrToInt(CastInst):
    def __init__(self, name: str, value: Value, dest_type: IRType) -> None:
        super().__init__(name, Opcode.PTRTOINT, dest_type, [value])


class IntToPtr(CastInst):
    def __init__(self, name: str, value: Value, dest_type: IRType) -> None:
        super().__init__(name, Opcode.INTTOPTR, dest_type, [value])


class BitCast(CastInst):
    def __init__(self, name: str, value: Value, dest_type: IRType) -> None:
        super().__init__(name, Opcode.BITCAST, dest_type, [value])


class AddrSpaceCast(CastInst):
    def __init__(self, name: str, value: Value, dest_type: IRType) -> None:
        super().__init__(name, Opcode.ADDRSPACECAST, dest_type, [value])


# ══════════════════════════════════════════════════════════════════
# Control Flow Instructions
# ══════════════════════════════════════════════════════════════════


class Phi(Instruction):
    """Phi node — selects a value based on which predecessor edge was taken."""
    __slots__ = ("_incoming",)

    def __init__(
        self,
        name: str,
        typ: IRType,
        incoming: Optional[List[Tuple[Value, BasicBlock]]] = None,
    ) -> None:
        super().__init__(name, Opcode.PHI, typ, [])
        object.__setattr__(self, "_incoming", list(incoming) if incoming else [])

    @property
    def incoming(self) -> List[Tuple[Value, BasicBlock]]:
        return self._incoming

    def add_incoming(self, value: Value, block: BasicBlock) -> None:
        """Add an incoming value/block pair."""
        self._incoming.append((value, block))
        if isinstance(value, Value):
            value.add_use(self)

    def remove_incoming(self, block: BasicBlock) -> Optional[Value]:
        """Remove the incoming value associated with a block."""
        for i, (val, blk) in enumerate(self._incoming):
            if blk is block:
                val.remove_use(self)
                self._incoming.pop(i)
                return val
        return None

    def get_incoming_for(self, block: BasicBlock) -> Optional[Value]:
        """Get the value associated with a specific predecessor."""
        for val, blk in self._incoming:
            if blk is block:
                return val
        return None


class Call(Instruction):
    """Function call."""
    __slots__ = ("_func_type", "_arguments", "_calling_conv", "_attributes")

    def __init__(
        self,
        name: str,
        func_type: IRType,
        function: Value,
        arguments: Optional[List[Value]] = None,
    ) -> None:
        from .types import IRFunctionType, IRVoid
        ret = func_type.return_type if isinstance(func_type, IRFunctionType) else IRVoid()
        super().__init__(name, Opcode.CALL, ret,
                         [function] + (list(arguments) if arguments else []))
        object.__setattr__(self, "_func_type", func_type)
        object.__setattr__(self, "_arguments", list(arguments) if arguments else [])
        object.__setattr__(self, "_calling_conv", "")
        object.__setattr__(self, "_attributes", {})

    @property
    def function(self) -> Value:
        return self._operands[0]

    @property
    def callee(self) -> Value:
        """Alias for function — used by optimization passes."""
        return self._operands[0]

    @property
    def arguments(self) -> List[Value]:
        return self._arguments

    @property
    def func_type(self) -> IRType:
        return self._func_type


class Invoke(Instruction):
    """Invoke — call with exception handling."""
    __slots__ = ("_func_type", "_normal_block", "_unwind_block", "_arguments")

    def __init__(
        self,
        name: str,
        func_type: IRType,
        function: Value,
        arguments: List[Value],
        normal_block: BasicBlock,
        unwind_block: BasicBlock,
    ) -> None:
        from .types import IRFunctionType, IRVoid
        ret = func_type.return_type if isinstance(func_type, IRFunctionType) else IRVoid()
        super().__init__(name, Opcode.INVOKE, ret,
                         [function] + arguments + [normal_block, unwind_block])
        object.__setattr__(self, "_func_type", func_type)
        object.__setattr__(self, "_arguments", list(arguments))
        object.__setattr__(self, "_normal_block", normal_block)
        object.__setattr__(self, "_unwind_block", unwind_block)

    @property
    def function(self) -> Value:
        return self._operands[0]

    @property
    def arguments(self) -> List[Value]:
        return self._arguments

    @property
    def normal_block(self) -> BasicBlock:
        return self._normal_block

    @property
    def unwind_block(self) -> BasicBlock:
        return self._unwind_block


class LandingPad(Instruction):
    """Landing pad for exception handling."""
    __slots__ = ("_catch_types", "_cleanup")

    def __init__(
        self,
        name: str,
        result_type: IRType,
        catch_types: Optional[List[Value]] = None,
        cleanup: bool = False,
    ) -> None:
        super().__init__(name, Opcode.LANDING_PAD, result_type,
                         list(catch_types) if catch_types else [])
        object.__setattr__(self, "_catch_types", list(catch_types) if catch_types else [])
        object.__setattr__(self, "_cleanup", cleanup)


class Resume(Instruction):
    """Resume exception propagation."""
    __slots__ = ()

    def __init__(self, value: Value) -> None:
        super().__init__("", Opcode.RESUME, value.type, [value])


# ══════════════════════════════════════════════════════════════════
# Aggregate Instructions
# ══════════════════════════════════════════════════════════════════


class ExtractValue(Instruction):
    """Extract a value from an aggregate."""
    __slots__ = ("_indices",)

    def __init__(
        self,
        name: str,
        aggregate: Value,
        indices: List[int],
    ) -> None:
        super().__init__(name, Opcode.EXTRACT_VALUE, aggregate.type, [aggregate])
        object.__setattr__(self, "_indices", list(indices))

    @property
    def aggregate(self) -> Value:
        return self._operands[0]

    @property
    def indices(self) -> List[int]:
        return self._indices


class InsertValue(Instruction):
    """Insert a value into an aggregate."""
    __slots__ = ("_indices",)

    def __init__(
        self,
        name: str,
        aggregate: Value,
        element: Value,
        indices: List[int],
    ) -> None:
        super().__init__(name, Opcode.INSERT_VALUE, aggregate.type,
                         [aggregate, element])
        object.__setattr__(self, "_indices", list(indices))

    @property
    def aggregate(self) -> Value:
        return self._operands[0]

    @property
    def element(self) -> Value:
        return self._operands[1]

    @property
    def indices(self) -> List[int]:
        return self._indices


# ══════════════════════════════════════════════════════════════════
# Vector Instructions
# ══════════════════════════════════════════════════════════════════


class ExtractElement(Instruction):
    """Extract a single element from a vector."""
    __slots__ = ()

    def __init__(self, name: str, vector: Value, index: Value) -> None:
        from .types import VectorType
        elem = vector.type.element_type if isinstance(vector.type, VectorType) else vector.type
        super().__init__(name, Opcode.EXTRACT_ELEMENT, elem, [vector, index])


class InsertElement(Instruction):
    """Insert a single element into a vector."""
    __slots__ = ()

    def __init__(self, name: str, vector: Value, element: Value, index: Value) -> None:
        super().__init__(name, Opcode.INSERT_ELEMENT, vector.type,
                         [vector, element, index])


class ShuffleVector(Instruction):
    """Shuffle two vectors using an index mask."""
    __slots__ = ()

    def __init__(self, name: str, v1: Value, v2: Value, mask: Value) -> None:
        super().__init__(name, Opcode.SHUFFLE_VECTOR, v1.type, [v1, v2, mask])


# ══════════════════════════════════════════════════════════════════
# Atomic Instructions
# ══════════════════════════════════════════════════════════════════


class AtomicRMW(Instruction):
    """Atomic read-modify-write."""
    __slots__ = ("_operation", "_ordering")

    def __init__(
        self,
        name: str,
        operation: str,
        pointer: Value,
        value: Value,
        ordering: str = "seq_cst",
    ) -> None:
        super().__init__(name, Opcode.ATOMICRMW, value.type, [pointer, value])
        object.__setattr__(self, "_operation", operation)
        object.__setattr__(self, "_ordering", ordering)


class CmpXchg(Instruction):
    """Compare-and-exchange."""
    __slots__ = ("_success_ordering", "_failure_ordering", "_weak")

    def __init__(
        self,
        name: str,
        pointer: Value,
        cmp_val: Value,
        new_val: Value,
        success_ordering: str = "seq_cst",
        failure_ordering: str = "seq_cst",
        weak: bool = False,
    ) -> None:
        super().__init__(name, Opcode.CMPXCHG, cmp_val.type,
                         [pointer, cmp_val, new_val])
        object.__setattr__(self, "_success_ordering", success_ordering)
        object.__setattr__(self, "_failure_ordering", failure_ordering)
        object.__setattr__(self, "_weak", weak)


class Fence(Instruction):
    """Memory fence."""
    __slots__ = ("_ordering",)

    def __init__(self, ordering: str = "seq_cst") -> None:
        super().__init__("", Opcode.FENCE, IRVoid(), [])
        object.__setattr__(self, "_ordering", ordering)


# ══════════════════════════════════════════════════════════════════
# Instruction Factory
# ══════════════════════════════════════════════════════════════════


def create_instruction(
    opcode: Opcode,
    name: str,
    result_type: Optional[IRType] = None,
    operands: Optional[List[Value]] = None,
    **kwargs,
) -> Instruction:
    """Factory function to create an instruction by opcode."""
    from .types import IRVoid
    if result_type is None:
        result_type = IRVoid()
    instr = Instruction(name, opcode, result_type, operands or [])
    return instr
