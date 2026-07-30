"""
Pattern matching rules for instruction selection.

Defines a rule-based system for matching LIR instruction patterns and
replacing them with target-specific machine instruction sequences.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from compiler.ir.lir import LIRInstKind

if TYPE_CHECKING:
    from compiler.native.ir_lower.machine import MachineInst


# Type alias for a predicate function that checks if a pattern matches
PredicateFn = Callable[[list[str], str | None, Any], bool]
# Type alias for an emit function that produces machine instructions
EmitFn = Callable[[list[str], str | None, Any], list[Any]]


@dataclass(frozen=True)
class MatchPattern:
    """A pattern that matches a specific LIR instruction configuration.

    A pattern specifies the opcode to match, optional operand/destination
    predicates, and a result template for generating machine instructions.
    """

    opcode: LIRInstKind
    operand_predicate: PredicateFn | None = None
    dest_predicate: PredicateFn | None = None
    priority: int = 0

    def matches(
        self,
        opcode: LIRInstKind,
        operands: list[str],
        dest: str | None,
        ctx: Any = None,
    ) -> bool:
        """Check if this pattern matches the given instruction."""
        if self.opcode != opcode:
            return False
        if self.operand_predicate and not self.operand_predicate(operands, dest, ctx):
            return False
        if self.dest_predicate and not self.dest_predicate([dest] if dest else [], dest, ctx):
            return False
        return True


@dataclass
class MatchRule:
    """A complete matching rule: pattern + predicate + result emission.

    When the pattern matches, the emitter is called to produce zero or
    more machine instructions.
    """

    name: str
    pattern: MatchPattern
    emitter: EmitFn
    is_peephole: bool = False

    def apply(
        self,
        opcode: LIRInstKind,
        operands: list[str],
        dest: str | None,
        ctx: Any = None,
    ) -> list[Any] | None:
        """Apply this rule if the pattern matches.

        Returns the emitted machine instructions, or None if no match.
        """
        if not self.pattern.matches(opcode, operands, dest, ctx):
            return None
        return self.emitter(operands, dest, ctx)


class PatternMatcher:
    """Rule-based instruction selector using pattern matching.

    Maintains an ordered list of MatchRules and applies the first
    matching rule for each LIR instruction. Supports both normal
    lowering rules and peephole optimization rules.
    """

    __slots__ = ("_rules", "_peephole_rules")

    def __init__(self) -> None:
        self._rules: list[MatchRule] = []
        self._peephole_rules: list[MatchRule] = []

    def add_rule(self, rule: MatchRule) -> None:
        """Add a lowering rule. Rules are tried in order of addition."""
        self._rules.append(rule)

    def add_peephole_rule(self, rule: MatchRule) -> None:
        """Add a peephole optimization rule."""
        self._peephole_rules.append(rule)

    def add_rules(self, rules: Sequence[MatchRule]) -> None:
        """Add multiple lowering rules."""
        self._rules.extend(rules)

    def match(
        self,
        opcode: LIRInstKind,
        operands: list[str],
        dest: str | None,
        ctx: Any = None,
    ) -> list[Any] | None:
        """Try all rules in order, returning the first match."""
        for rule in self._rules:
            result = rule.apply(opcode, operands, dest, ctx)
            if result is not None:
                return result
        return None

    def apply_peephole(
        self,
        opcode: LIRInstKind,
        operands: list[str],
        dest: str | None,
        ctx: Any = None,
    ) -> list[Any] | None:
        """Apply peephole optimization rules."""
        for rule in self._peephole_rules:
            result = rule.apply(opcode, operands, dest, ctx)
            if result is not None:
                return result
        return None

    @property
    def rules(self) -> list[MatchRule]:
        return list(self._rules)

    @property
    def peephole_rules(self) -> list[MatchRule]:
        return list(self._peephole_rules)

    def clear(self) -> None:
        self._rules.clear()
        self._peephole_rules.clear()


# ── Helper predicates ──────────────────────────────────────────────

def _is_immediate(operands: list[str], _dest: str | None, _ctx: Any) -> bool:
    """Check if the first operand is an immediate (numeric) value."""
    if not operands:
        return False
    try:
        int(operands[0])
        return True
    except ValueError:
        pass
    try:
        float(operands[0])
        return True
    except ValueError:
        pass
    return False


def _is_zero(operands: list[str], _dest: str | None, _ctx: Any) -> bool:
    if not operands:
        return False
    try:
        return int(operands[0]) == 0
    except ValueError:
        return operands[0] in ("0", "0.0")


def _is_one(operands: list[str], _dest: str | None, _ctx: Any) -> bool:
    if not operands:
        return False
    try:
        return int(operands[0]) == 1
    except ValueError:
        return operands[0] == "1"


def _has_i1_dest(
    _operands: list[str], dest: str | None, ctx: Any,
) -> bool:
    return dest is not None


def _always(
    _operands: list[str], _dest: str | None, _ctx: Any,
) -> bool:
    return True


# ── Emitter builders ───────────────────────────────────────────────

def _emit_single(op: Any) -> EmitFn:
    """Create an emitter that produces a single machine instruction."""
    from compiler.native.ir_lower.machine import MachineInst

    def emit(
        operands: list[str], dest: str | None, ctx: Any,
    ) -> list[MachineInst]:
        return [MachineInst(op)]

    return emit


def _emit_with_operands(mop: Any) -> EmitFn:
    """Create an emitter that passes operands through to a machine instruction."""
    from compiler.native.ir_lower.machine import MachineInst, MachineOperand

    def emit(
        operands: list[str], dest: str | None, ctx: Any,
    ) -> list[MachineInst]:
        mobs = []
        for op in operands:
            mobs.append(_to_machine_operand(op))
        if dest:
            mobs.insert(0, MachineOperand.reg(dest))
        return [MachineInst(mop, mobs)]

    return emit


def _to_machine_operand(op: str) -> Any:
    """Convert an LIR operand string to a MachineOperand."""
    from compiler.native.ir_lower.machine import MachineOperand
    try:
        val = int(op)
        return MachineOperand.imm(val)
    except ValueError:
        pass
    try:
        val = float(op)
        return MachineOperand.imm(int(val))
    except ValueError:
        pass
    if op.startswith("%") or op.startswith("r") or op.startswith("x"):
        return MachineOperand.reg(op)
    if op.startswith(".") or op.startswith("L"):
        return MachineOperand.label(op)
    return MachineOperand.reg(op)


# ── Peephole emitters ──────────────────────────────────────────────

def _emit_nop(
    _operands: list[str], _dest: str | None, _ctx: Any,
) -> list[Any]:
    """Emit a NOP (used for identity operations like add 0, mul 1)."""
    from compiler.native.ir_lower.machine import MachineInst, MachineOp
    return [MachineInst(MachineOp.NOP)]


def _emit_copy(
    _operands: list[str], dest: str | None, ctx: Any,
) -> list[Any]:
    """Emit a register copy (used for shift by 0)."""
    from compiler.native.ir_lower.machine import MachineInst, MachineOp, MachineOperand
    if not dest:
        return _emit_nop(_operands, dest, ctx)
    return [MachineInst(MachineOp.MOV, [MachineOperand.reg(dest), MachineOperand.reg(_operands[0])])]


# ── Build concrete pattern sets ────────────────────────────────────

def _add_alu_rules(matcher: PatternMatcher, add_op: Any, sub_op: Any, mul_op: Any) -> None:
    """Add ALU operation rules (add, sub, mul)."""
    from compiler.native.ir_lower.machine import MachineInst, MachineOperand

    def make_alu_emitter(mop: Any) -> EmitFn:
        def emit(operands: list[str], dest: str | None, ctx: Any) -> list[MachineInst]:
            if not dest:
                return []
            ops = [MachineOperand.reg(dest)]
            for op in operands:
                ops.append(_to_machine_operand(op))
            return [MachineInst(mop, ops)]
        return emit

    matcher.add_rule(MatchRule(
        name=f"add_{add_op.name}",
        pattern=MatchPattern(LIRInstKind.IADD),
        emitter=make_alu_emitter(add_op),
    ))
    matcher.add_rule(MatchRule(
        name=f"sub_{sub_op.name}",
        pattern=MatchPattern(LIRInstKind.ISUB),
        emitter=make_alu_emitter(sub_op),
    ))
    matcher.add_rule(MatchRule(
        name=f"mul_{mul_op.name}",
        pattern=MatchPattern(LIRInstKind.IMUL),
        emitter=make_alu_emitter(mul_op),
    ))


def _add_bitwise_rules(matcher: PatternMatcher, and_op: Any, or_op: Any, xor_op: Any) -> None:
    """Add bitwise operation rules."""
    from compiler.native.ir_lower.machine import MachineInst, MachineOperand

    def make_bitwise_emitter(mop: Any) -> EmitFn:
        def emit(operands: list[str], dest: str | None, ctx: Any) -> list[MachineInst]:
            if not dest:
                return []
            ops = [MachineOperand.reg(dest)]
            for op in operands:
                ops.append(_to_machine_operand(op))
            return [MachineInst(mop, ops)]
        return emit

    matcher.add_rule(MatchRule(
        name=f"and_{and_op.name}",
        pattern=MatchPattern(LIRInstKind.IAND),
        emitter=make_bitwise_emitter(and_op),
    ))
    matcher.add_rule(MatchRule(
        name=f"or_{or_op.name}",
        pattern=MatchPattern(LIRInstKind.IOR),
        emitter=make_bitwise_emitter(or_op),
    ))
    matcher.add_rule(MatchRule(
        name=f"xor_{xor_op.name}",
        pattern=MatchPattern(LIRInstKind.IXOR),
        emitter=make_bitwise_emitter(xor_op),
    ))


def _add_shift_rules(matcher: PatternMatcher, shl_op: Any, shr_op: Any, ashr_op: Any) -> None:
    """Add shift operation rules."""
    from compiler.native.ir_lower.machine import MachineInst, MachineOperand

    def make_shift_emitter(mop: Any) -> EmitFn:
        def emit(operands: list[str], dest: str | None, ctx: Any) -> list[MachineInst]:
            if not dest:
                return []
            ops = [MachineOperand.reg(dest)]
            for op in operands:
                ops.append(_to_machine_operand(op))
            return [MachineInst(mop, ops)]
        return emit

    matcher.add_rule(MatchRule(
        name=f"shl_{shl_op.name}",
        pattern=MatchPattern(LIRInstKind.ISHL),
        emitter=make_shift_emitter(shl_op),
    ))
    matcher.add_rule(MatchRule(
        name=f"shr_{shr_op.name}",
        pattern=MatchPattern(LIRInstKind.ISHR),
        emitter=make_shift_emitter(shr_op),
    ))


def _add_fp_rules(matcher: PatternMatcher) -> None:
    """Add floating-point operation rules for x86-64 (SSE2)."""
    from compiler.native.ir_lower.machine import MachineInst, MachineOp, MachineOperand

    fp_ops = [
        (LIRInstKind.FADD, MachineOp.ADDSD),
        (LIRInstKind.FSUB, MachineOp.SUBSD),
        (LIRInstKind.FMUL, MachineOp.MULSD),
        (LIRInstKind.FDIV, MachineOp.DIVSD),
    ]

    for lir_op, mach_op in fp_ops:
        def make_fp_emitter(mop: Any) -> EmitFn:
            def emit(operands: list[str], dest: str | None, ctx: Any) -> list[MachineInst]:
                if not dest:
                    return []
                ops = [MachineOperand.reg(dest)]
                for op in operands:
                    ops.append(_to_machine_operand(op))
                return [MachineInst(mop, ops)]
            return emit

        matcher.add_rule(MatchRule(
            name=f"fp_{lir_op.name}",
            pattern=MatchPattern(lir_op),
            emitter=make_fp_emitter(mach_op),
        ))


def _add_load_store_rules(matcher: PatternMatcher) -> None:
    """Add load and store operation rules."""
    from compiler.native.ir_lower.machine import MachineInst, MachineOp, MachineOperand

    matcher.add_rule(MatchRule(
        name="load_var",
        pattern=MatchPattern(LIRInstKind.LOAD_VAR),
        emitter=lambda ops, dest, ctx: (
            [MachineInst(MachineOp.MOV, [
                MachineOperand.reg(dest), MachineOperand.mem(ops[0]),
            ])] if dest else []
        ),
    ))

    matcher.add_rule(MatchRule(
        name="store_var",
        pattern=MatchPattern(LIRInstKind.STORE_VAR),
        emitter=lambda ops, _dest, _ctx: (
            [MachineInst(MachineOp.MOV, [
                MachineOperand.mem(ops[1]), MachineOperand.reg(ops[0]),
            ])]
        ),
    ))

    matcher.add_rule(MatchRule(
        name="load_const",
        pattern=MatchPattern(LIRInstKind.LOAD_CONST),
        emitter=lambda ops, dest, ctx: (
            [MachineInst(MachineOp.MOV, [
                MachineOperand.reg(dest), _to_machine_operand(ops[0]),
            ])] if dest else []
        ),
    ))

    matcher.add_rule(MatchRule(
        name="move",
        pattern=MatchPattern(LIRInstKind.MOVE),
        emitter=lambda ops, dest, ctx: (
            [MachineInst(MachineOp.MOV, [
                MachineOperand.reg(dest), MachineOperand.reg(ops[0]),
            ])] if dest else []
        ),
    ))


def _add_control_flow_rules(matcher: PatternMatcher) -> None:
    """Add control flow operation rules."""
    from compiler.native.ir_lower.machine import MachineInst, MachineOp, MachineOperand

    matcher.add_rule(MatchRule(
        name="br",
        pattern=MatchPattern(LIRInstKind.BR),
        emitter=lambda ops, _dest, _ctx: (
            [MachineInst(MachineOp.JMP, [MachineOperand.label(ops[0])])]
        ),
    ))

    matcher.add_rule(MatchRule(
        name="call",
        pattern=MatchPattern(LIRInstKind.CALL),
        emitter=lambda ops, dest, ctx: (
            [MachineInst(MachineOp.CALL, [MachineOperand.reg(ops[0])])]
        ),
    ))

    matcher.add_rule(MatchRule(
        name="return_void",
        pattern=MatchPattern(LIRInstKind.RETURN),
        emitter=lambda _ops, _dest, _ctx: [MachineInst(MachineOp.RET)],
    ))

    matcher.add_rule(MatchRule(
        name="alloca",
        pattern=MatchPattern(LIRInstKind.ALLOCA),
        emitter=lambda ops, _dest, _ctx: (
            [MachineInst(MachineOp.SUB_RSP, [MachineOperand.imm(int(ops[0]) if ops else 8)])]
        ),
    ))


def _add_peephole_rules(matcher: PatternMatcher) -> None:
    """Add peephole optimization rules."""
    matcher.add_peephole_rule(MatchRule(
        name="add_zero",
        pattern=MatchPattern(
            LIRInstKind.IADD,
            operand_predicate=lambda ops, _d, _c: len(ops) > 1 and (
                ops[1] == "0" or ops[1] == "$0"
            ),
        ),
        emitter=_emit_nop,
        is_peephole=True,
    ))

    matcher.add_peephole_rule(MatchRule(
        name="sub_zero",
        pattern=MatchPattern(
            LIRInstKind.ISUB,
            operand_predicate=lambda ops, _d, _c: len(ops) > 1 and (
                ops[1] == "0" or ops[1] == "$0"
            ),
        ),
        emitter=_emit_nop,
        is_peephole=True,
    ))

    matcher.add_peephole_rule(MatchRule(
        name="mul_one",
        pattern=MatchPattern(
            LIRInstKind.IMUL,
            operand_predicate=lambda ops, _d, _c: len(ops) > 1 and (
                ops[1] == "1" or ops[1] == "$1"
            ),
        ),
        emitter=_emit_copy,
        is_peephole=True,
    ))

    matcher.add_peephole_rule(MatchRule(
        name="mul_zero",
        pattern=MatchPattern(
            LIRInstKind.IMUL,
            operand_predicate=lambda ops, _d, _c: len(ops) > 1 and (
                ops[1] == "0" or ops[1] == "$0"
            ),
        ),
        emitter=_emit_nop,
        is_peephole=True,
    ))

    matcher.add_peephole_rule(MatchRule(
        name="shift_by_zero",
        pattern=MatchPattern(
            LIRInstKind.ISHL,
            operand_predicate=lambda ops, _d, _c: len(ops) > 1 and (
                ops[1] == "0" or ops[1] == "$0"
            ),
        ),
        emitter=_emit_copy,
        is_peephole=True,
    ))

    matcher.add_peephole_rule(MatchRule(
        name="shr_by_zero",
        pattern=MatchPattern(
            LIRInstKind.ISHR,
            operand_predicate=lambda ops, _d, _c: len(ops) > 1 and (
                ops[1] == "0" or ops[1] == "$0"
            ),
        ),
        emitter=_emit_copy,
        is_peephole=True,
    ))

    matcher.add_peephole_rule(MatchRule(
        name="and_with_self",
        pattern=MatchPattern(
            LIRInstKind.IAND,
            operand_predicate=lambda ops, _d, _c: len(ops) > 1 and ops[0] == ops[1],
        ),
        emitter=_emit_copy,
        is_peephole=True,
    ))

    matcher.add_peephole_rule(MatchRule(
        name="or_with_self",
        pattern=MatchPattern(
            LIRInstKind.IOR,
            operand_predicate=lambda ops, _d, _c: len(ops) > 1 and ops[0] == ops[1],
        ),
        emitter=_emit_copy,
        is_peephole=True,
    ))

    matcher.add_peephole_rule(MatchRule(
        name="xor_with_self",
        pattern=MatchPattern(
            LIRInstKind.IXOR,
            operand_predicate=lambda ops, _d, _c: len(ops) > 1 and ops[0] == ops[1],
        ),
        emitter=_emit_nop,
        is_peephole=True,
    ))


def _add_arm64_specific_rules(matcher: PatternMatcher) -> None:
    """Add ARM64-specific instruction selection patterns."""
    from compiler.native.ir_lower.machine import MachineInst, MachineOp, MachineOperand

    matcher.add_rule(MatchRule(
        name="arm64_load",
        pattern=MatchPattern(LIRInstKind.LOAD_VAR),
        emitter=lambda ops, dest, ctx: (
            [MachineInst(MachineOp.LDR, [
                MachineOperand.reg(dest), MachineOperand.mem(ops[0]),
            ])] if dest else []
        ),
    ))

    matcher.add_rule(MatchRule(
        name="arm64_store",
        pattern=MatchPattern(LIRInstKind.STORE_VAR),
        emitter=lambda ops, _dest, _ctx: (
            [MachineInst(MachineOp.STR, [
                MachineOperand.mem(ops[1]), MachineOperand.reg(ops[0]),
            ])]
        ),
    ))

    matcher.add_rule(MatchRule(
        name="arm64_br",
        pattern=MatchPattern(LIRInstKind.BR),
        emitter=lambda ops, _dest, _ctx: (
            [MachineInst(MachineOp.B, [MachineOperand.label(ops[0])])]
        ),
    ))

    matcher.add_rule(MatchRule(
        name="arm64_call",
        pattern=MatchPattern(LIRInstKind.CALL),
        emitter=lambda ops, dest, ctx: (
            [MachineInst(MachineOp.BL, [MachineOperand.reg(ops[0])])]
        ),
    ))

    matcher.add_rule(MatchRule(
        name="arm64_return",
        pattern=MatchPattern(LIRInstKind.RETURN),
        emitter=lambda _ops, _dest, _ctx: [MachineInst(MachineOp.RET)],
    ))

    _add_alu_rules(matcher, MachineOp.ADD_K, MachineOp.SUB_K, MachineOp.MUL_K)
    _add_bitwise_rules(matcher, MachineOp.AND_K, MachineOp.ORR, MachineOp.EOR)
    _add_shift_rules(matcher, MachineOp.LSL, MachineOp.LSR, MachineOp.ASR)


def build_x86_64_patterns() -> PatternMatcher:
    """Build the complete pattern set for x86-64 instruction selection."""
    from compiler.native.ir_lower.machine import MachineOp

    matcher = PatternMatcher()

    _add_alu_rules(matcher, MachineOp.ADD, MachineOp.SUB, MachineOp.IMUL)
    _add_bitwise_rules(matcher, MachineOp.AND, MachineOp.OR, MachineOp.XOR)
    _add_shift_rules(matcher, MachineOp.SHL, MachineOp.SHR, MachineOp.SAR)
    _add_fp_rules(matcher)
    _add_load_store_rules(matcher)
    _add_control_flow_rules(matcher)
    _add_peephole_rules(matcher)

    return matcher


def build_arm64_patterns() -> PatternMatcher:
    """Build the complete pattern set for ARM64 instruction selection."""
    matcher = PatternMatcher()

    _add_arm64_specific_rules(matcher)
    _add_peephole_rules(matcher)

    return matcher
