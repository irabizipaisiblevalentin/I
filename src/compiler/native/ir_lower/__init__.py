"""
Instruction selection / IR lowering subsystem.

Transforms LIR (Low-Level IR) into target-specific Machine IR (MIR)
with physical registers and concrete target instructions.
"""

from __future__ import annotations

from compiler.native.ir_lower.legalizer import (
    LegalizationError,
    Legalizer,
)
from compiler.native.ir_lower.machine import (
    MachineBasicBlock,
    MachineFunction,
    MachineInst,
    MachineModule,
    MachineOp,
    MachineOperand,
    MachineOperandKind,
)
from compiler.native.ir_lower.patterns import (
    MatchPattern,
    MatchRule,
    PatternMatcher,
    build_arm64_patterns,
    build_x86_64_patterns,
)
from compiler.native.ir_lower.selector import (
    ARM64InstructionSelector,
    InstructionSelector,
    X86_64InstructionSelector,
    select,
)

__all__ = (
    # machine
    "MachineOp",
    "MachineOperand",
    "MachineOperandKind",
    "MachineInst",
    "MachineBasicBlock",
    "MachineFunction",
    "MachineModule",
    # legalizer
    "Legalizer",
    "LegalizationError",
    # patterns
    "MatchPattern",
    "PatternMatcher",
    "MatchRule",
    "build_x86_64_patterns",
    "build_arm64_patterns",
    # selector
    "InstructionSelector",
    "X86_64InstructionSelector",
    "ARM64InstructionSelector",
    "select",
)
