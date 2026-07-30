"""
Machine IR definitions — target-specific intermediate representation
with physical registers and concrete machine instructions.
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import Enum, auto
from typing import Any


class MachineOp(Enum):
    """Target-specific machine opcodes covering x86-64 and ARM64."""

    # ── Data movement ──────────────────────────────────────────────
    MOV = auto()
    MOVZX = auto()
    MOVSX = auto()
    LEA = auto()
    PUSH = auto()
    POP = auto()

    # ── Integer arithmetic ─────────────────────────────────────────
    ADD = auto()
    SUB = auto()
    IMUL = auto()
    CDQ = auto()
    IDIV = auto()
    DIV = auto()
    NEG = auto()
    INC = auto()
    DEC = auto()

    # ── Bitwise ────────────────────────────────────────────────────
    AND = auto()
    OR = auto()
    XOR = auto()
    NOT = auto()
    SHL = auto()
    SHR = auto()
    SAR = auto()

    # ── Floating-point (SSE2) ──────────────────────────────────────
    MOVSD = auto()
    ADDSD = auto()
    SUBSD = auto()
    MULSD = auto()
    DIVSD = auto()
    CVTSI2SD = auto()
    CVTTSD2SI = auto()
    UCOMISD = auto()

    # ── Comparison ─────────────────────────────────────────────────
    CMP = auto()
    SETE = auto()
    SETNE = auto()
    SETL = auto()
    SETLE = auto()
    SETG = auto()
    SETGE = auto()
    SETB = auto()
    SETBE = auto()
    SETA = auto()
    SETAE = auto()

    # ── Control flow ───────────────────────────────────────────────
    JMP = auto()
    JE = auto()
    JNE = auto()
    JL = auto()
    JLE = auto()
    JG = auto()
    JGE = auto()
    JB = auto()
    JBE = auto()
    JA = auto()
    JAE = auto()
    CALL = auto()
    RET = auto()

    # ── Stack ──────────────────────────────────────────────────────
    SUB_RSP = auto()
    ADD_RSP = auto()

    # ── ARM64 specific ─────────────────────────────────────────────
    MOV_K = auto()
    MOVN = auto()
    MOVZ = auto()
    ADD_K = auto()
    SUB_K = auto()
    MUL_K = auto()
    SDIV_K = auto()
    UDIV_K = auto()
    AND_K = auto()
    ORR = auto()
    EOR = auto()
    LSL = auto()
    LSR = auto()
    ASR = auto()
    LDR = auto()
    STR = auto()
    STP = auto()
    LDP = auto()
    B = auto()
    B_EQ = auto()
    B_NE = auto()
    B_LT = auto()
    B_LE = auto()
    B_GT = auto()
    B_GE = auto()
    B_LO = auto()
    B_LS = auto()
    B_HI = auto()
    B_HS = auto()
    BL = auto()
    CMP_K = auto()
    CSET = auto()
    CSETM = auto()
    SXTW = auto()
    FCVT = auto()
    FMOV = auto()
    FADD_K = auto()
    FSUB_K = auto()
    FMUL_K = auto()
    FDIV_K = auto()
    SCVTF = auto()
    FCVTZS = auto()
    FCMP_K = auto()

    # ── Pseudo / Meta ──────────────────────────────────────────────
    NOP = auto()
    COMMENT = auto()
    LABEL = auto()
    ALIGN = auto()
    PHI_K = auto()


class MachineOperandKind(Enum):
    """Classification of machine operand kinds."""

    REGISTER = auto()
    IMMEDIATE = auto()
    MEMORY = auto()
    LABEL = auto()
    GLOBAL = auto()


class MachineOperand:
    """A single machine operand — register, immediate, memory, or label.

    Memory operands encode base register, index register, scale, and displacement.
    """

    __slots__ = ("_kind", "_value", "_size", "_base", "_index", "_scale", "_disp")

    def __init__(
        self,
        kind: MachineOperandKind,
        value: Any = None,
        size: int = 64,
        base: str | None = None,
        index: str | None = None,
        scale: int = 1,
        disp: int = 0,
    ) -> None:
        self._kind = kind
        self._value = value
        self._size = size
        self._base = base
        self._index = index
        self._scale = scale
        self._disp = disp

    @classmethod
    def reg(cls, name: str, size: int = 64) -> MachineOperand:
        return cls(MachineOperandKind.REGISTER, name, size=size)

    @classmethod
    def imm(cls, value: int, size: int = 64) -> MachineOperand:
        return cls(MachineOperandKind.IMMEDIATE, value, size=size)

    @classmethod
    def mem(
        cls,
        base: str,
        disp: int = 0,
        index: str | None = None,
        scale: int = 1,
        size: int = 64,
    ) -> MachineOperand:
        return cls(
            MachineOperandKind.MEMORY, None, size=size,
            base=base, index=index, scale=scale, disp=disp,
        )

    @classmethod
    def mem_disp(cls, disp: int, size: int = 64) -> MachineOperand:
        return cls(
            MachineOperandKind.MEMORY, None, size=size,
            base=None, index=None, scale=1, disp=disp,
        )

    @classmethod
    def label(cls, name: str, size: int = 64) -> MachineOperand:
        return cls(MachineOperandKind.LABEL, name, size=size)

    @classmethod
    def global_ref(cls, name: str, size: int = 64) -> MachineOperand:
        return cls(MachineOperandKind.GLOBAL, name, size=size)

    @property
    def kind(self) -> MachineOperandKind:
        return self._kind

    @property
    def value(self) -> Any:
        return self._value

    @property
    def size(self) -> int:
        return self._size

    @property
    def register_name(self) -> str:
        assert self._kind == MachineOperandKind.REGISTER
        return str(self._value)

    @property
    def imm_value(self) -> int:
        assert self._kind == MachineOperandKind.IMMEDIATE
        return int(self._value)

    @property
    def label_name(self) -> str:
        assert self._kind in (MachineOperandKind.LABEL, MachineOperandKind.GLOBAL)
        return str(self._value)

    @property
    def base(self) -> str | None:
        return self._base

    @property
    def index(self) -> str | None:
        return self._index

    @property
    def scale(self) -> int:
        return self._scale

    @property
    def disp(self) -> int:
        return self._disp

    def is_reg(self) -> bool:
        return self._kind == MachineOperandKind.REGISTER

    def is_imm(self) -> bool:
        return self._kind == MachineOperandKind.IMMEDIATE

    def is_mem(self) -> bool:
        return self._kind == MachineOperandKind.MEMORY

    def is_label(self) -> bool:
        return self._kind == MachineOperandKind.LABEL

    def is_global(self) -> bool:
        return self._kind == MachineOperandKind.GLOBAL

    def __repr__(self) -> str:
        if self._kind == MachineOperandKind.REGISTER:
            return f"%{self._value}"
        if self._kind == MachineOperandKind.IMMEDIATE:
            return f"${self._value}"
        if self._kind == MachineOperandKind.MEMORY:
            parts = []
            if self._base:
                parts.append(f"%{self._base}")
            if self._index:
                parts.append(f"%{self._index}*{self._scale}")
            if self._disp != 0:
                parts.append(f"{self._disp:+d}")
            return f"[{'+'.join(parts)}]" if parts else f"[{self._disp}]"
        if self._kind == MachineOperandKind.LABEL:
            return f"&{self._value}"
        if self._kind == MachineOperandKind.GLOBAL:
            return f"@{self._value}"
        return repr(self._value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MachineOperand):
            return NotImplemented
        return (
            self._kind == other._kind
            and self._value == other._value
            and self._size == other._size
            and self._base == other._base
            and self._index == other._index
            and self._scale == other._scale
            and self._disp == other._disp
        )

    def __hash__(self) -> int:
        return hash((
            self._kind, self._value, self._size,
            self._base, self._index, self._scale, self._disp,
        ))


class MachineInst:
    """A single machine instruction with opcode, operands, and metadata."""

    __slots__ = ("_opcode", "_operands", "_comment", "_debug")

    def __init__(
        self,
        opcode: MachineOp,
        operands: Sequence[MachineOperand] | None = None,
        comment: str = "",
    ) -> None:
        self._opcode = opcode
        self._operands = list(operands) if operands else []
        self._comment = comment
        self._debug = ""

    @property
    def opcode(self) -> MachineOp:
        return self._opcode

    @property
    def operands(self) -> list[MachineOperand]:
        return list(self._operands)

    @property
    def comment(self) -> str:
        return self._comment

    @comment.setter
    def comment(self, value: str) -> None:
        self._comment = value

    @property
    def debug(self) -> str:
        return self._debug

    @debug.setter
    def debug(self, value: str) -> None:
        self._debug = value

    def add_operand(self, op: MachineOperand) -> None:
        self._operands.append(op)

    @property
    def defs(self) -> list[MachineOperand]:
        """Return operands defined (written) by this instruction."""
        if not self._operands:
            return []
        if self._opcode in (
            MachineOp.CMP, MachineOp.CMP_K,
            MachineOp.UCOMISD, MachineOp.FCMP_K,
            MachineOp.JMP, MachineOp.JE, MachineOp.JNE,
            MachineOp.JL, MachineOp.JLE, MachineOp.JG, MachineOp.JGE,
            MachineOp.JB, MachineOp.JBE, MachineOp.JA, MachineOp.JAE,
            MachineOp.B, MachineOp.B_EQ, MachineOp.B_NE,
            MachineOp.B_LT, MachineOp.B_LE, MachineOp.B_GT, MachineOp.B_GE,
            MachineOp.B_LO, MachineOp.B_LS, MachineOp.B_HI, MachineOp.B_HS,
            MachineOp.RET, MachineOp.STORE, MachineOp.STR, MachineOp.STP,
            MachineOp.PUSH, MachineOp.POP,
        ):
            return []
        if self._opcode in (
            MachineOp.CDQ, MachineOp.IDIV, MachineOp.DIV,
        ):
            return [self._operands[0]] if self._operands else []
        if self._opcode in (
            MachineOp.MOV, MachineOp.ADD, MachineOp.SUB,
            MachineOp.IMUL, MachineOp.AND, MachineOp.OR, MachineOp.XOR,
            MachineOp.SHL, MachineOp.SHR, MachineOp.SAR,
            MachineOp.MOVSD, MachineOp.ADDSD, MachineOp.SUBSD,
            MachineOp.MULSD, MachineOp.DIVSD,
            MachineOp.CVTSI2SD, MachineOp.CVTTSD2SI,
            MachineOp.MOVZX, MachineOp.MOVSX, MachineOp.LEA,
            MachineOp.NEG, MachineOp.NOT, MachineOp.INC, MachineOp.DEC,
        ):
            return [self._operands[0]] if self._operands else []
        if self._opcode in (MachineOp.SETE, MachineOp.SETNE, MachineOp.SETL,
                            MachineOp.SETLE, MachineOp.SETG, MachineOp.SETGE,
                            MachineOp.SETB, MachineOp.SETBE, MachineOp.SETA,
                            MachineOp.SETAE, MachineOp.CSET, MachineOp.CSETM):
            return list(self._operands)
        return list(self._operands)

    @property
    def uses(self) -> list[MachineOperand]:
        """Return operands used (read) by this instruction."""
        if not self._operands:
            return []
        if self._opcode in (
            MachineOp.CDQ, MachineOp.RET, MachineOp.NOP,
        ):
            return []
        if self._opcode in (
            MachineOp.MOV, MachineOp.ADD, MachineOp.SUB,
            MachineOp.IMUL, MachineOp.AND, MachineOp.OR, MachineOp.XOR,
            MachineOp.SHL, MachineOp.SHR, MachineOp.SAR,
            MachineOp.MOVSD, MachineOp.ADDSD, MachineOp.SUBSD,
            MachineOp.MULSD, MachineOp.DIVSD,
            MachineOp.CVTSI2SD, MachineOp.CVTTSD2SI,
        ):
            return self._operands[1:] if len(self._operands) > 1 else []
        return self._operands

    def is_terminator(self) -> bool:
        return self._opcode in (
            MachineOp.RET, MachineOp.JMP, MachineOp.JE, MachineOp.JNE,
            MachineOp.JL, MachineOp.JLE, MachineOp.JG, MachineOp.JGE,
            MachineOp.JB, MachineOp.JBE, MachineOp.JA, MachineOp.JAE,
            MachineOp.B, MachineOp.B_EQ, MachineOp.B_NE,
            MachineOp.B_LT, MachineOp.B_LE, MachineOp.B_GT, MachineOp.B_GE,
            MachineOp.B_LO, MachineOp.B_LS, MachineOp.B_HI, MachineOp.B_HS,
            MachineOp.CALL,
        )

    def is_call(self) -> bool:
        return self._opcode in (MachineOp.CALL, MachineOp.BL)

    def is_return(self) -> bool:
        return self._opcode == MachineOp.RET

    def is_branch(self) -> bool:
        return self._opcode in (
            MachineOp.JMP, MachineOp.JE, MachineOp.JNE,
            MachineOp.JL, MachineOp.JLE, MachineOp.JG, MachineOp.JGE,
            MachineOp.JB, MachineOp.JBE, MachineOp.JA, MachineOp.JAE,
            MachineOp.B, MachineOp.B_EQ, MachineOp.B_NE,
            MachineOp.B_LT, MachineOp.B_LE, MachineOp.B_GT, MachineOp.B_GE,
            MachineOp.B_LO, MachineOp.B_LS, MachineOp.B_HI, MachineOp.B_HS,
        )

    def is_unconditional_branch(self) -> bool:
        return self._opcode in (MachineOp.JMP, MachineOp.B)

    def is_conditional_branch(self) -> bool:
        return self.is_branch() and not self.is_unconditional_branch()

    def __repr__(self) -> str:
        ops = ", ".join(str(o) for o in self._operands)
        comment = f"  # {self._comment}" if self._comment else ""
        return f"  {self._opcode.name} {ops}{comment}"


class MachineBasicBlock:
    """A basic block of machine instructions with control flow information."""

    __slots__ = (
        "_name", "_instructions", "_preds", "_succs",
        "_label", "_loop_depth",
    )

    def __init__(self, name: str = "") -> None:
        self._name = name
        self._instructions: list[MachineInst] = []
        self._preds: list[MachineBasicBlock] = []
        self._succs: list[MachineBasicBlock] = []
        self._label = name
        self._loop_depth = 0

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._label = value

    @property
    def instructions(self) -> list[MachineInst]:
        return list(self._instructions)

    @property
    def predecessors(self) -> list[MachineBasicBlock]:
        return list(self._preds)

    @property
    def successors(self) -> list[MachineBasicBlock]:
        return list(self._succs)

    @property
    def loop_depth(self) -> int:
        return self._loop_depth

    @loop_depth.setter
    def loop_depth(self, value: int) -> None:
        self._loop_depth = value

    @property
    def terminator(self) -> MachineInst | None:
        if self._instructions and self._instructions[-1].is_terminator():
            return self._instructions[-1]
        return None

    @property
    def is_empty(self) -> bool:
        return len(self._instructions) == 0

    def append(self, inst: MachineInst) -> None:
        self._instructions.append(inst)

    def prepend(self, inst: MachineInst) -> None:
        self._instructions.insert(0, inst)

    def insert_before(self, ref: MachineInst, inst: MachineInst) -> None:
        idx = self._instructions.index(ref)
        self._instructions.insert(idx, inst)

    def insert_after(self, ref: MachineInst, inst: MachineInst) -> None:
        idx = self._instructions.index(ref)
        self._instructions.insert(idx + 1, inst)

    def remove(self, inst: MachineInst) -> None:
        if inst in self._instructions:
            self._instructions.remove(inst)

    def replace(self, old: MachineInst, new: MachineInst) -> None:
        idx = self._instructions.index(old)
        self._instructions[idx] = new

    def add_predecessor(self, block: MachineBasicBlock) -> None:
        if block not in self._preds:
            self._preds.append(block)

    def remove_predecessor(self, block: MachineBasicBlock) -> None:
        if block in self._preds:
            self._preds.remove(block)

    def add_successor(self, block: MachineBasicBlock) -> None:
        if block not in self._succs:
            self._succs.append(block)

    def remove_successor(self, block: MachineBasicBlock) -> None:
        if block in self._succs:
            self._succs.remove(block)

    def clear(self) -> None:
        self._instructions.clear()

    def live_in(self) -> set[str]:
        """Registers live at entry (placeholder for liveness analysis)."""
        return set()

    def live_out(self) -> set[str]:
        """Registers live at exit (placeholder for liveness analysis)."""
        return set()

    def __iter__(self):
        return iter(self._instructions)

    def __len__(self) -> int:
        return len(self._instructions)

    def __getitem__(self, idx: int) -> MachineInst:
        return self._instructions[idx]

    def __repr__(self) -> str:
        count = len(self._instructions)
        term = self.terminator
        term_str = f", term={term.opcode.name}" if term else ""
        return f"MachineBasicBlock({self._name}, {count} insts{term_str})"


class MachineFunction:
    """A function composed of machine basic blocks with register and frame info."""

    __slots__ = (
        "_name", "_blocks", "_frame_size", "_used_regs",
        "_callee_saved", "_has_calls", "_signature",
    )

    def __init__(self, name: str) -> None:
        self._name = name
        self._blocks: list[MachineBasicBlock] = []
        self._frame_size = 0
        self._used_regs: set[str] = set()
        self._callee_saved: list[str] = []
        self._has_calls = False
        self._signature: object | None = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def blocks(self) -> list[MachineBasicBlock]:
        return list(self._blocks)

    @property
    def frame_size(self) -> int:
        return self._frame_size

    @frame_size.setter
    def frame_size(self, value: int) -> None:
        self._frame_size = value

    @property
    def used_regs(self) -> set[str]:
        return self._used_regs

    @property
    def callee_saved(self) -> list[str]:
        return list(self._callee_saved)

    @callee_saved.setter
    def callee_saved(self, value: list[str]) -> None:
        self._callee_saved = list(value)

    @property
    def has_calls(self) -> bool:
        return self._has_calls

    @has_calls.setter
    def has_calls(self, value: bool) -> None:
        self._has_calls = value

    @property
    def signature(self) -> object | None:
        return self._signature

    @signature.setter
    def signature(self, value: object) -> None:
        self._signature = value

    @property
    def entry_block(self) -> MachineBasicBlock | None:
        return self._blocks[0] if self._blocks else None

    @property
    def block_count(self) -> int:
        return len(self._blocks)

    @property
    def instruction_count(self) -> int:
        return sum(len(b) for b in self._blocks)

    def append_block(self, block: MachineBasicBlock) -> None:
        self._blocks.append(block)

    def insert_block(self, index: int, block: MachineBasicBlock) -> None:
        self._blocks.insert(index, block)

    def remove_block(self, block: MachineBasicBlock) -> None:
        if block in self._blocks:
            self._blocks.remove(block)
            for other in self._blocks:
                other.remove_predecessor(block)
                other.remove_successor(block)

    def get_block(self, name: str) -> MachineBasicBlock | None:
        for b in self._blocks:
            if b.name == name:
                return b
        return None

    def add_reg_use(self, reg: str) -> None:
        self._used_regs.add(reg)

    def mark_has_calls(self) -> None:
        self._has_calls = True

    def __iter__(self):
        return iter(self._blocks)

    def __len__(self) -> int:
        return len(self._blocks)

    def __getitem__(self, idx: int) -> MachineBasicBlock:
        return self._blocks[idx]

    def __repr__(self) -> str:
        return (
            f"MachineFunction({self._name}, "
            f"{self.block_count} blocks, "
            f"{self.instruction_count} insts, "
            f"frame={self._frame_size})"
        )


class MachineModule:
    """A module containing machine functions and global declarations."""

    __slots__ = ("_name", "_functions", "_globals")

    def __init__(self, name: str = "") -> None:
        self._name = name
        self._functions: list[MachineFunction] = []
        self._globals: list[dict[str, Any]] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def functions(self) -> list[MachineFunction]:
        return list(self._functions)

    @property
    def globals(self) -> list[dict[str, Any]]:
        return list(self._globals)

    def add_function(self, func: MachineFunction) -> None:
        self._functions.append(func)

    def get_function(self, name: str) -> MachineFunction | None:
        for f in self._functions:
            if f.name == name:
                return f
        return None

    def add_global(self, name: str, size: int, alignment: int = 8) -> None:
        self._globals.append({"name": name, "size": size, "alignment": alignment})

    def __repr__(self) -> str:
        return f"MachineModule({self._name}, {len(self._functions)} functions)"
