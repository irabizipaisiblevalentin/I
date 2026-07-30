"""
Instruction Selector — transforms LIR into target-specific Machine IR.

Provides an abstract base class and concrete implementations for x86-64
and ARM64, mapping LIR instructions to physical register machine instructions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from compiler.ir.lir import (
    LIRFunction,
    LIRInstKind,
    LIRInstruction,
)
from compiler.native.ir_lower.legalizer import Legalizer
from compiler.native.ir_lower.machine import (
    MachineBasicBlock,
    MachineFunction,
    MachineInst,
    MachineModule,
    MachineOp,
    MachineOperand,
)
from compiler.native.ir_lower.patterns import (
    PatternMatcher,
    build_arm64_patterns,
    build_x86_64_patterns,
)

if TYPE_CHECKING:
    from compiler.native.target.desc import TargetDescription
    from compiler.native.target.kind import TargetKind


class InstructionSelector(ABC):
    """Abstract base class for instruction selection.

    Subclasses implement target-specific lowering from LIR to Machine IR.
    """

    __slots__ = ("_patterns", "_legalizer")

    def __init__(self, target_kind: TargetKind) -> None:
        self._legalizer = Legalizer(target_kind)

    @property
    def legalizer(self) -> Legalizer:
        return self._legalizer

    @abstractmethod
    def _build_patterns(self) -> PatternMatcher:
        """Return the target-specific pattern matcher."""
        ...

    @abstractmethod
    def _lower_instruction(
        self,
        inst: LIRInstruction,
        block: MachineBasicBlock,
        func: MachineFunction,
        ctx: Any,
    ) -> list[MachineInst]:
        """Lower a single LIR instruction into one or more machine instructions."""
        ...

    def select(self, function: LIRFunction) -> MachineFunction:
        """Lower an LIR function to a MachineFunction.

        Performs legalization, instruction selection via pattern matching,
        basic block ordering, and jump fixup.
        """
        legalized = self._legalizer.legalize_function(function)
        mfunc = MachineFunction(legalized.name)
        ctx: dict[str, Any] = {}

        block_map: dict[str, MachineBasicBlock] = {}
        for lir_block in legalized:
            mblock = MachineBasicBlock(lir_block.label)
            mfunc.append_block(mblock)
            block_map[lir_block.label] = mblock

        for lir_block in legalized:
            mblock = block_map[lir_block.label]
            for lir_inst in lir_block:
                if lir_inst.is_terminator:
                    lowered = self._lower_terminator(lir_inst, mblock, mfunc, ctx, block_map)
                else:
                    lowered = self._lower_instruction(lir_inst, mblock, mfunc, ctx)
                for mi in lowered:
                    mblock.append(mi)
                    self._track_reg_uses(mi, mfunc)

        self._fixup_jumps(mfunc, block_map)
        self._compute_frame_size(mfunc, legalized)

        return mfunc

    def _lower_terminator(
        self,
        inst: LIRInstruction,
        block: MachineBasicBlock,
        func: MachineFunction,
        ctx: Any,
        block_map: dict[str, MachineBasicBlock],
    ) -> list[MachineInst]:
        """Lower a terminator instruction, handling control flow."""
        return self._lower_instruction(inst, block, func, ctx)

    def _track_reg_uses(self, inst: MachineInst, func: MachineFunction) -> None:
        """Track which physical registers are used by an instruction."""
        for op in inst.operands:
            if op.is_reg():
                func.add_reg_use(op.register_name)
            elif op.is_mem():
                if op.base:
                    func.add_reg_use(op.base)
                if op.index:
                    func.add_reg_use(op.index)

    def _fixup_jumps(
        self,
        func: MachineFunction,
        block_map: dict[str, MachineBasicBlock],
    ) -> None:
        """Fix up jump targets and basic block ordering.

        Ensures:
        - Conditional branches that fall through to the next block are optimized.
        - Unconditional branches to the next block are removed.
        - Block order follows a natural layout.
        """
        for mblock in func:
            term = mblock.terminator
            if term is None:
                continue
            if term.is_unconditional_branch():
                target_label = self._get_jump_target(term)
                target_idx = self._find_block_index(func, target_label)
                block_idx = self._find_block_index(func, mblock.label)
                if target_idx is not None and block_idx is not None:
                    if target_idx == block_idx + 1:
                        mblock.remove(term)
            elif term.is_conditional_branch():
                target_label = self._get_jump_target(term)
                target_idx = self._find_block_index(func, target_label)
                block_idx = self._find_block_index(func, mblock.label)
                if target_idx is not None and block_idx is not None:
                    if target_idx == block_idx + 1:
                        mblock.remove(term)
                        if mblock.instructions and mblock.instructions[-1].is_unconditional_branch():
                            mblock.remove(mblock.instructions[-1])

        self._ensure_terminated(func)

    def _get_jump_target(self, inst: MachineInst) -> str | None:
        """Extract the target label from a jump instruction."""
        for op in inst.operands:
            if op.is_label():
                return op.label_name
        return None

    def _find_block_index(
        self, func: MachineFunction, label: str,
    ) -> int | None:
        """Find the index of a block by label."""
        for i, b in enumerate(func):
            if b.label == label:
                return i
        return None

    def _ensure_terminated(self, func: MachineFunction) -> None:
        """Ensure every basic block ends with a terminator."""
        for mblock in func:
            if mblock.terminator is not None:
                continue
            if mblock.instructions:
                last = mblock.instructions[-1]
                if not last.is_terminator():
                    if last.opcode in (MachineOp.CALL, MachineOp.BL):
                        mblock.append(MachineInst(MachineOp.RET))

    def _compute_frame_size(
        self,
        mfunc: MachineFunction,
        lir_func: LIRFunction,
    ) -> None:
        """Compute the stack frame size from local variable count and alignment."""
        frame_size = lir_func.num_locals * 8
        frame_size = (frame_size + 15) & ~15
        mfunc.frame_size = frame_size

    def select_module(
        self,
        functions: list[LIRFunction],
        module_name: str = "",
    ) -> MachineModule:
        """Lower a list of LIR functions into a MachineModule."""
        mmod = MachineModule(module_name)
        for func in functions:
            mmod.add_function(self.select(func))
        return mmod


class X86_64InstructionSelector(InstructionSelector):  # noqa: N801
    """x86-64 specific instruction lowering.

    Maps LIR instructions to x86-64 machine instructions with proper
    handling of operand sizes, condition codes, and addressing modes.
    """

    __slots__ = ("_patterns",)

    ICMP_TO_JCC: dict[LIRInstKind, MachineOp] = {
        LIRInstKind.ICMP_EQ: MachineOp.JE,
        LIRInstKind.ICMP_NE: MachineOp.JNE,
        LIRInstKind.ICMP_LT: MachineOp.JL,
        LIRInstKind.ICMP_LE: MachineOp.JLE,
        LIRInstKind.ICMP_GT: MachineOp.JG,
        LIRInstKind.ICMP_GE: MachineOp.JGE,
    }

    ICMP_TO_SETCC: dict[LIRInstKind, MachineOp] = {
        LIRInstKind.ICMP_EQ: MachineOp.SETE,
        LIRInstKind.ICMP_NE: MachineOp.SETNE,
        LIRInstKind.ICMP_LT: MachineOp.SETL,
        LIRInstKind.ICMP_LE: MachineOp.SETLE,
        LIRInstKind.ICMP_GT: MachineOp.SETG,
        LIRInstKind.ICMP_GE: MachineOp.SETGE,
    }

    FCMP_TO_JCC: dict[LIRInstKind, MachineOp] = {
        LIRInstKind.FCMP_EQ: MachineOp.JE,
        LIRInstKind.FCMP_NE: MachineOp.JNE,
        LIRInstKind.FCMP_LT: MachineOp.JB,
        LIRInstKind.FCMP_LE: MachineOp.JBE,
        LIRInstKind.FCMP_GT: MachineOp.JA,
        LIRInstKind.FCMP_GE: MachineOp.JAE,
    }

    COND_BR_TO_JCC: dict[LIRInstKind, MachineOp] = {
        LIRInstKind.BREQ: MachineOp.JE,
        LIRInstKind.BRNE: MachineOp.JNE,
        LIRInstKind.BRLT: MachineOp.JL,
        LIRInstKind.BRGE: MachineOp.JGE,
    }

    def __init__(self) -> None:
        from compiler.native.target.kind import TargetKind
        super().__init__(TargetKind.X86_64)
        self._patterns = self._build_patterns()

    def _build_patterns(self) -> PatternMatcher:
        return build_x86_64_patterns()

    def _lower_instruction(
        self,
        inst: LIRInstruction,
        block: MachineBasicBlock,
        func: MachineFunction,
        ctx: Any,
    ) -> list[MachineInst]:
        kind = inst.kind
        ops = inst.operands
        dest = inst.dest

        result = self._patterns.apply_peephole(kind, ops, dest, ctx)
        if result is not None:
            return result

        result = self._patterns.match(kind, ops, dest, ctx)
        if result is not None:
            return result

        # ── Direct lowering for unmapped instructions ───────────────
        if kind == LIRInstKind.IADD:
            return self._lower_binary(MachineOp.ADD, dest, ops)
        if kind == LIRInstKind.ISUB:
            return self._lower_binary(MachineOp.SUB, dest, ops)
        if kind == LIRInstKind.IMUL:
            return self._lower_binary(MachineOp.IMUL, dest, ops)

        if kind == LIRInstKind.IDIV:
            return self._lower_idiv(dest, ops)
        if kind == LIRInstKind.IMOD:
            return self._lower_imod(dest, ops)

        if kind in (LIRInstKind.IAND, LIRInstKind.IOR, LIRInstKind.IXOR):
            mop_map = {
                LIRInstKind.IAND: MachineOp.AND,
                LIRInstKind.IOR: MachineOp.OR,
                LIRInstKind.IXOR: MachineOp.XOR,
            }
            return self._lower_binary(mop_map[kind], dest, ops)

        if kind == LIRInstKind.ISHL:
            return self._lower_binary(MachineOp.SHL, dest, ops)
        if kind == LIRInstKind.ISHR:
            return self._lower_binary(MachineOp.SHR, dest, ops)

        if kind in (LIRInstKind.FADD, LIRInstKind.FSUB, LIRInstKind.FMUL, LIRInstKind.FDIV):
            mop_map = {
                LIRInstKind.FADD: MachineOp.ADDSD,
                LIRInstKind.FSUB: MachineOp.SUBSD,
                LIRInstKind.FMUL: MachineOp.MULSD,
                LIRInstKind.FDIV: MachineOp.DIVSD,
            }
            return self._lower_fp_binary(mop_map[kind], dest, ops)

        if kind in (LIRInstKind.ICMP_EQ, LIRInstKind.ICMP_NE,
                    LIRInstKind.ICMP_LT, LIRInstKind.ICMP_LE,
                    LIRInstKind.ICMP_GT, LIRInstKind.ICMP_GE):
            return self._lower_icmp(kind, dest, ops)

        if kind in (LIRInstKind.FCMP_EQ, LIRInstKind.FCMP_NE,
                    LIRInstKind.FCMP_LT, LIRInstKind.FCMP_LE,
                    LIRInstKind.FCMP_GT, LIRInstKind.FCMP_GE):
            return self._lower_fcmp(kind, dest, ops)

        if kind in (LIRInstKind.LOAD_VAR, LIRInstKind.LOAD_PARAM,
                    LIRInstKind.LOAD_FIELD, LIRInstKind.LOAD_ELEMENT):
            return self._lower_load(dest, ops)

        if kind == LIRInstKind.STORE_VAR:
            return self._lower_store(ops)

        if kind == LIRInstKind.LOAD_CONST:
            return self._lower_load_const(dest, ops)

        if kind == LIRInstKind.MOVE:
            return self._lower_move(dest, ops)

        if kind == LIRInstKind.ALLOCA:
            return self._lower_alloca(ops)

        if kind == LIRInstKind.CALL:
            return self._lower_call(dest, ops)

        if kind == LIRInstKind.RETURN:
            return self._lower_return(ops)

        if kind == LIRInstKind.BR:
            return self._lower_br(ops)

        if kind in (LIRInstKind.BREQ, LIRInstKind.BRNE,
                    LIRInstKind.BRLT, LIRInstKind.BRGE):
            return self._lower_cond_br(kind, ops)

        if kind in (LIRInstKind.I2I, LIRInstKind.I2F, LIRInstKind.F2I,
                    LIRInstKind.F2F, LIRInstKind.I2P, LIRInstKind.P2I):
            return self._lower_cast(kind, dest, ops)

        if kind == LIRInstKind.NOP:
            return [MachineInst(MachineOp.NOP)]

        return [MachineInst(MachineOp.NOP, comment=f"unsupported {kind.name}")]

    def _lower_binary(
        self,
        mop: MachineOp,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower a binary arithmetic/logic operation."""
        if not dest or len(ops) < 2:
            return []
        return [MachineInst(mop, [
            MachineOperand.reg(dest),
            MachineOperand.reg(ops[1]),
        ], comment=f"{ops[0]} {mop.name} {ops[1]}")]

    def _lower_fp_binary(
        self,
        mop: MachineOp,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower a floating-point binary operation (SSE2)."""
        if not dest or len(ops) < 2:
            return []
        return [MachineInst(mop, [
            MachineOperand.reg(dest),
            MachineOperand.reg(ops[1]),
        ], comment=f"fp {ops[0]} {mop.name} {ops[1]}")]

    def _lower_idiv(
        self,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower signed integer division: cdq + idiv."""
        if not dest or len(ops) < 2:
            return []
        return [
            MachineInst(MachineOp.MOV, [MachineOperand.reg("rax"), MachineOperand.reg(ops[0])],
                        comment="idiv: move lhs to rax"),
            MachineInst(MachineOp.CDQ, comment="idiv: sign-extend rax to rdx:rax"),
            MachineInst(MachineOp.IDIV, [MachineOperand.reg(ops[1])],
                        comment="idiv: divide rdx:rax by rhs"),
            MachineInst(MachineOp.MOV, [MachineOperand.reg(dest), MachineOperand.reg("rax")],
                        comment="idiv: move result"),
        ]

    def _lower_imod(
        self,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower signed integer modulo: cdq + idiv, result in rdx."""
        if not dest or len(ops) < 2:
            return []
        return [
            MachineInst(MachineOp.MOV, [MachineOperand.reg("rax"), MachineOperand.reg(ops[0])],
                        comment="imod: move lhs to rax"),
            MachineInst(MachineOp.CDQ, comment="imod: sign-extend rax to rdx:rax"),
            MachineInst(MachineOp.IDIV, [MachineOperand.reg(ops[1])],
                        comment="imod: divide rdx:rax by rhs"),
            MachineInst(MachineOp.MOV, [MachineOperand.reg(dest), MachineOperand.reg("rdx")],
                        comment="imod: move remainder from rdx"),
        ]

    def _lower_icmp(
        self,
        kind: LIRInstKind,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower integer comparison: cmp + setcc."""
        if len(ops) < 2:
            return []
        result: list[MachineInst] = [
            MachineInst(MachineOp.CMP, [
                MachineOperand.reg(ops[1]), MachineOperand.reg(ops[0]),
            ], comment=f"cmp {ops[0]}, {ops[1]}"),
        ]
        setcc_op = self.ICMP_TO_SETCC.get(kind, MachineOp.SETE)
        if dest:
            result.append(
                MachineInst(setcc_op, [MachineOperand.reg(dest)],
                            comment=f"{kind.name} -> {dest}")
            )
        return result

    def _lower_fcmp(
        self,
        kind: LIRInstKind,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower floating-point comparison: ucomisd + setcc."""
        if len(ops) < 2:
            return []
        result: list[MachineInst] = [
            MachineInst(MachineOp.UCOMISD, [
                MachineOperand.reg(ops[0]), MachineOperand.reg(ops[1]),
            ], comment=f"fcmp {ops[0]}, {ops[1]}"),
        ]
        setcc_op = self.ICMP_TO_SETCC.get(kind, MachineOp.SETE)
        if dest:
            result.append(
                MachineInst(setcc_op, [MachineOperand.reg(dest)],
                            comment=f"{kind.name} -> {dest}")
            )
        return result

    def _lower_load(
        self,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower a memory load: mov reg, [address]."""
        if not dest or not ops:
            return []
        return [MachineInst(MachineOp.MOV, [
            MachineOperand.reg(dest),
            MachineOperand.mem(ops[0]),
        ], comment=f"load {dest} from {ops[0]}")]

    def _lower_store(
        self,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower a memory store: mov [address], reg."""
        if len(ops) < 2:
            return []
        return [MachineInst(MachineOp.MOV, [
            MachineOperand.mem(ops[1]),
            MachineOperand.reg(ops[0]),
        ], comment=f"store {ops[0]} to {ops[1]}")]

    def _lower_load_const(
        self,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower loading an immediate constant: mov reg, imm."""
        if not dest or not ops:
            return []
        imm_val = self._parse_imm(ops[0])
        return [MachineInst(MachineOp.MOV, [
            MachineOperand.reg(dest),
            MachineOperand.imm(imm_val),
        ], comment=f"load const {imm_val}")]

    def _lower_move(
        self,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower a register move: mov dest, src."""
        if not dest or not ops:
            return []
        return [MachineInst(MachineOp.MOV, [
            MachineOperand.reg(dest),
            MachineOperand.reg(ops[0]),
        ], comment=f"move {ops[0]} -> {dest}")]

    def _lower_alloca(
        self,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower stack allocation: sub rsp, size."""
        size = self._parse_imm(ops[0]) if ops else 8
        aligned = (size + 15) & ~15
        return [MachineInst(MachineOp.SUB_RSP, [
            MachineOperand.imm(aligned),
        ], comment=f"alloca {size} (aligned {aligned})")]

    def _lower_call(
        self,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower a function call: call target."""
        if not ops:
            return []
        callee = ops[0]
        result: list[MachineInst] = [
            MachineInst(MachineOp.CALL, [MachineOperand.reg(callee)],
                        comment=f"call {callee}"),
        ]
        if dest:
            result.append(
                MachineInst(MachineOp.MOV, [
                    MachineOperand.reg(dest),
                    MachineOperand.reg("rax"),
                ], comment=f"move return value to {dest}")
            )
        result.insert(0, MachineInst(
            MachineOp.COMMENT, comment=f"call args: {', '.join(ops[1:])}"
        ))
        return result

    def _lower_return(
        self,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower a return: mov rax, val + ret."""
        if ops:
            return [
                MachineInst(MachineOp.MOV, [
                    MachineOperand.reg("rax"),
                    MachineOperand.reg(ops[0]),
                ], comment="return value"),
                MachineInst(MachineOp.RET),
            ]
        return [MachineInst(MachineOp.RET)]

    def _lower_br(
        self,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower an unconditional branch: jmp label."""
        if not ops:
            return []
        return [MachineInst(MachineOp.JMP, [MachineOperand.label(ops[0])])]

    def _lower_cond_br(
        self,
        kind: LIRInstKind,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower a conditional branch: cmp + jcc."""
        if len(ops) < 2:
            return []
        jcc_op = self.COND_BR_TO_JCC.get(kind, MachineOp.JE)
        target = ops[1] if len(ops) > 1 else ""
        return [
            MachineInst(MachineOp.CMP, [
                MachineOperand.reg(ops[0]),
                MachineOperand.imm(0),
            ], comment=f"cond_br {kind.name}"),
            MachineInst(jcc_op, [MachineOperand.label(target)],
                        comment=f"branch to {target}"),
        ]

    def _lower_cast(
        self,
        kind: LIRInstKind,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower a type conversion operation."""
        if not dest or not ops:
            return []
        if kind == LIRInstKind.I2I:
            return [MachineInst(MachineOp.MOV, [
                MachineOperand.reg(dest),
                MachineOperand.reg(ops[0]),
            ], comment="int extend/trunc")]
        if kind == LIRInstKind.I2F:
            return [MachineInst(MachineOp.CVTSI2SD, [
                MachineOperand.reg(dest),
                MachineOperand.reg(ops[0]),
            ], comment="int to float")]
        if kind == LIRInstKind.F2I:
            return [MachineInst(MachineOp.CVTTSD2SI, [
                MachineOperand.reg(dest),
                MachineOperand.reg(ops[0]),
            ], comment="float to int")]
        if kind in (LIRInstKind.I2P, LIRInstKind.P2I):
            return [MachineInst(MachineOp.MOV, [
                MachineOperand.reg(dest),
                MachineOperand.reg(ops[0]),
            ], comment="ptr/int cast")]
        return [MachineInst(MachineOp.MOV, [
            MachineOperand.reg(dest),
            MachineOperand.reg(ops[0]),
        ], comment=f"cast {kind.name}")]

    @staticmethod
    def _parse_imm(op: str) -> int:
        """Parse an immediate value from a string."""
        try:
            return int(op)
        except ValueError:
            pass
        try:
            return int(float(op))
        except ValueError:
            pass
        return 0

    def select_module(
        self,
        functions: list[LIRFunction],
        module_name: str = "",
    ) -> MachineModule:
        """Lower all functions in a list to a MachineModule."""
        mmod = MachineModule(module_name)
        for func in functions:
            mmod.add_function(self.select(func))
        return mmod


class ARM64InstructionSelector(InstructionSelector):
    """ARM64 specific instruction lowering.

    Maps LIR instructions to ARM64 machine instructions with proper
    handling of register naming (x0-x30), condition flags, and
    ARM64-specific features like LDR/STR, B.cond, and BL.
    """

    __slots__ = ("_patterns",)

    ICMP_TO_BCC: dict[LIRInstKind, MachineOp] = {
        LIRInstKind.ICMP_EQ: MachineOp.B_EQ,
        LIRInstKind.ICMP_NE: MachineOp.B_NE,
        LIRInstKind.ICMP_LT: MachineOp.B_LT,
        LIRInstKind.ICMP_LE: MachineOp.B_LE,
        LIRInstKind.ICMP_GT: MachineOp.B_GT,
        LIRInstKind.ICMP_GE: MachineOp.B_GE,
    }

    ICMP_TO_CSET: dict[LIRInstKind, MachineOp] = {
        LIRInstKind.ICMP_EQ: MachineOp.CSET,
        LIRInstKind.ICMP_NE: MachineOp.CSET,
        LIRInstKind.ICMP_LT: MachineOp.CSET,
        LIRInstKind.ICMP_LE: MachineOp.CSET,
        LIRInstKind.ICMP_GT: MachineOp.CSET,
        LIRInstKind.ICMP_GE: MachineOp.CSET,
    }

    COND_BR_TO_BCC: dict[LIRInstKind, MachineOp] = {
        LIRInstKind.BREQ: MachineOp.B_EQ,
        LIRInstKind.BRNE: MachineOp.B_NE,
        LIRInstKind.BRLT: MachineOp.B_LT,
        LIRInstKind.BRGE: MachineOp.B_GE,
    }

    def __init__(self) -> None:
        from compiler.native.target.kind import TargetKind
        super().__init__(TargetKind.ARM64)
        self._patterns = self._build_patterns()

    def _build_patterns(self) -> PatternMatcher:
        return build_arm64_patterns()

    def _lower_instruction(
        self,
        inst: LIRInstruction,
        block: MachineBasicBlock,
        func: MachineFunction,
        ctx: Any,
    ) -> list[MachineInst]:
        kind = inst.kind
        ops = inst.operands
        dest = inst.dest

        result = self._patterns.apply_peephole(kind, ops, dest, ctx)
        if result is not None:
            return result

        result = self._patterns.match(kind, ops, dest, ctx)
        if result is not None:
            return result

        # ── Direct lowering ─────────────────────────────────────────
        if kind in (LIRInstKind.IADD, LIRInstKind.ISUB, LIRInstKind.IMUL):
            mop_map = {
                LIRInstKind.IADD: MachineOp.ADD_K,
                LIRInstKind.ISUB: MachineOp.SUB_K,
                LIRInstKind.IMUL: MachineOp.MUL_K,
            }
            return self._lower_binary(mop_map[kind], dest, ops)

        if kind == LIRInstKind.IDIV:
            return self._lower_binary(MachineOp.SDIV_K, dest, ops)

        if kind in (LIRInstKind.IAND, LIRInstKind.IOR, LIRInstKind.IXOR):
            mop_map = {
                LIRInstKind.IAND: MachineOp.AND_K,
                LIRInstKind.IOR: MachineOp.ORR,
                LIRInstKind.IXOR: MachineOp.EOR,
            }
            return self._lower_binary(mop_map[kind], dest, ops)

        if kind in (LIRInstKind.ISHL, LIRInstKind.ISHR):
            mop_map = {
                LIRInstKind.ISHL: MachineOp.LSL,
                LIRInstKind.ISHR: MachineOp.LSR,
            }
            return self._lower_binary(mop_map[kind], dest, ops)

        if kind in (LIRInstKind.FADD, LIRInstKind.FSUB, LIRInstKind.FMUL, LIRInstKind.FDIV):
            mop_map = {
                LIRInstKind.FADD: MachineOp.FADD_K,
                LIRInstKind.FSUB: MachineOp.FSUB_K,
                LIRInstKind.FMUL: MachineOp.FMUL_K,
                LIRInstKind.FDIV: MachineOp.FDIV_K,
            }
            return self._lower_fp_binary(mop_map[kind], dest, ops)

        if kind in (LIRInstKind.ICMP_EQ, LIRInstKind.ICMP_NE,
                    LIRInstKind.ICMP_LT, LIRInstKind.ICMP_LE,
                    LIRInstKind.ICMP_GT, LIRInstKind.ICMP_GE):
            return self._lower_icmp(kind, dest, ops)

        if kind in (LIRInstKind.LOAD_VAR, LIRInstKind.LOAD_PARAM,
                    LIRInstKind.LOAD_FIELD, LIRInstKind.LOAD_ELEMENT):
            return self._lower_load(dest, ops)

        if kind == LIRInstKind.STORE_VAR:
            return self._lower_store(ops)

        if kind == LIRInstKind.LOAD_CONST:
            return self._lower_load_const(dest, ops)

        if kind == LIRInstKind.MOVE:
            return self._lower_move(dest, ops)

        if kind == LIRInstKind.ALLOCA:
            return self._lower_alloca(ops)

        if kind == LIRInstKind.CALL:
            return self._lower_call(dest, ops)

        if kind == LIRInstKind.RETURN:
            return self._lower_return(ops)

        if kind == LIRInstKind.BR:
            return self._lower_br(ops)

        if kind in (LIRInstKind.BREQ, LIRInstKind.BRNE,
                    LIRInstKind.BRLT, LIRInstKind.BRGE):
            return self._lower_cond_br(kind, ops)

        if kind in (LIRInstKind.I2I, LIRInstKind.I2F, LIRInstKind.F2I,
                    LIRInstKind.F2F, LIRInstKind.I2P, LIRInstKind.P2I):
            return self._lower_cast(kind, dest, ops)

        if kind == LIRInstKind.NOP:
            return [MachineInst(MachineOp.NOP)]

        return [MachineInst(MachineOp.NOP, comment=f"unsupported {kind.name}")]

    def _lower_binary(
        self,
        mop: MachineOp,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        if not dest or len(ops) < 2:
            return []
        return [MachineInst(mop, [
            MachineOperand.reg(dest),
            MachineOperand.reg(ops[0]),
            MachineOperand.reg(ops[1]),
        ])]

    def _lower_fp_binary(
        self,
        mop: MachineOp,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        if not dest or len(ops) < 2:
            return []
        return [MachineInst(mop, [
            MachineOperand.reg(dest),
            MachineOperand.reg(ops[0]),
            MachineOperand.reg(ops[1]),
        ])]

    def _lower_icmp(
        self,
        kind: LIRInstKind,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        if len(ops) < 2:
            return []
        result: list[MachineInst] = [
            MachineInst(MachineOp.CMP_K, [
                MachineOperand.reg(ops[1]),
                MachineOperand.reg(ops[0]),
            ]),
        ]
        if dest:
            result.append(
                MachineInst(MachineOp.CSET, [MachineOperand.reg(dest)],
                            comment=f"{kind.name}")
            )
        return result

    def _lower_load(
        self,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        if not dest or not ops:
            return []
        return [MachineInst(MachineOp.LDR, [
            MachineOperand.reg(dest),
            MachineOperand.mem(ops[0]),
        ])]

    def _lower_store(
        self,
        ops: list[str],
    ) -> list[MachineInst]:
        if len(ops) < 2:
            return []
        return [MachineInst(MachineOp.STR, [
            MachineOperand.mem(ops[1]),
            MachineOperand.reg(ops[0]),
        ])]

    def _lower_load_const(
        self,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        if not dest or not ops:
            return []
        imm_val = self._parse_imm(ops[0])
        return [MachineInst(MachineOp.MOV_K, [
            MachineOperand.reg(dest),
            MachineOperand.imm(imm_val),
        ])]

    def _lower_move(
        self,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        if not dest or not ops:
            return []
        return [MachineInst(MachineOp.MOV_K, [
            MachineOperand.reg(dest),
            MachineOperand.reg(ops[0]),
        ])]

    def _lower_alloca(
        self,
        ops: list[str],
    ) -> list[MachineInst]:
        """Lower stack allocation: sub sp, sp, size."""
        size = self._parse_imm(ops[0]) if ops else 16
        aligned = (size + 15) & ~15
        return [MachineInst(MachineOp.SUB_K, [
            MachineOperand.reg("sp"),
            MachineOperand.reg("sp"),
            MachineOperand.imm(aligned),
        ])]

    def _lower_call(
        self,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        if not ops:
            return []
        result: list[MachineInst] = [
            MachineInst(MachineOp.BL, [MachineOperand.reg(ops[0])],
                        comment=f"call {ops[0]}"),
        ]
        if dest:
            result.append(
                MachineInst(MachineOp.MOV_K, [
                    MachineOperand.reg(dest),
                    MachineOperand.reg("x0"),
                ], comment="return value"),
            )
        return result

    def _lower_return(
        self,
        ops: list[str],
    ) -> list[MachineInst]:
        if ops:
            return [
                MachineInst(MachineOp.MOV_K, [
                    MachineOperand.reg("x0"),
                    MachineOperand.reg(ops[0]),
                ]),
                MachineInst(MachineOp.RET),
            ]
        return [MachineInst(MachineOp.RET)]

    def _lower_br(
        self,
        ops: list[str],
    ) -> list[MachineInst]:
        if not ops:
            return []
        return [MachineInst(MachineOp.B, [MachineOperand.label(ops[0])])]

    def _lower_cond_br(
        self,
        kind: LIRInstKind,
        ops: list[str],
    ) -> list[MachineInst]:
        if len(ops) < 2:
            return []
        bcc_op = self.COND_BR_TO_BCC.get(kind, MachineOp.B_EQ)
        return [
            MachineInst(MachineOp.CMP_K, [
                MachineOperand.reg(ops[0]),
                MachineOperand.imm(0),
            ]),
            MachineInst(bcc_op, [MachineOperand.label(ops[1])]),
        ]

    def _lower_cast(
        self,
        kind: LIRInstKind,
        dest: str | None,
        ops: list[str],
    ) -> list[MachineInst]:
        if not dest or not ops:
            return []
        if kind == LIRInstKind.I2I:
            return [MachineInst(MachineOp.MOV_K, [
                MachineOperand.reg(dest),
                MachineOperand.reg(ops[0]),
            ])]
        if kind == LIRInstKind.I2F:
            return [MachineInst(MachineOp.SCVTF, [
                MachineOperand.reg(dest),
                MachineOperand.reg(ops[0]),
            ])]
        if kind == LIRInstKind.F2I:
            return [MachineInst(MachineOp.FCVTZS, [
                MachineOperand.reg(dest),
                MachineOperand.reg(ops[0]),
            ])]
        return [MachineInst(MachineOp.MOV_K, [
            MachineOperand.reg(dest),
            MachineOperand.reg(ops[0]),
        ])]

    @staticmethod
    def _parse_imm(op: str) -> int:
        try:
            return int(op)
        except ValueError:
            pass
        try:
            return int(float(op))
        except ValueError:
            pass
        return 0


def select(
    function: LIRFunction,
    target: TargetDescription,
) -> MachineFunction:
    """Select and lower an LIR function to a MachineFunction for the given target.

    Args:
        function: The LIR function to lower.
        target: The target architecture description.

    Returns:
        A MachineFunction with target-specific machine instructions.

    Raises:
        ValueError: If the target architecture is unsupported.
    """
    selector = _create_selector(target)
    return selector.select(function)


def select_module(
    functions: list[LIRFunction],
    target: TargetDescription,
    module_name: str = "",
) -> MachineModule:
    """Lower a list of LIR functions into a MachineModule for the given target."""
    selector = _create_selector(target)
    return selector.select_module(functions, module_name)


def _create_selector(
    target: TargetDescription,
) -> InstructionSelector:
    """Factory: create the appropriate instruction selector for the target."""
    from compiler.native.target.kind import TargetKind

    if target.kind == TargetKind.X86_64:
        return X86_64InstructionSelector()
    if target.kind == TargetKind.ARM64:
        return ARM64InstructionSelector()
    raise ValueError(f"Unsupported target architecture: {target.kind}")


def ctx_getattr(ctx: Any, attr: str, default: Any = None) -> Any:
    """Safely get an attribute from a context object."""
    if isinstance(ctx, dict):
        return ctx.get(attr, default)
    return getattr(ctx, attr, default)
