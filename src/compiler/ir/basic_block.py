"""
IR Basic Block

A basic block is a maximal sequence of non-terminating instructions
that ends with exactly one terminator instruction. Basic blocks are
the nodes of the control flow graph.
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .values import Value, ValueKind
from .types import IRType, IR_LABEL

if TYPE_CHECKING:
    from typing import Iterator, List
    from .instructions import Instruction, TerminatorInst
    from .function import IRFunction


# ══════════════════════════════════════════════════════════════════
# Basic Block
# ══════════════════════════════════════════════════════════════════


class BasicBlock(Value):
    """A basic block — sequence of instructions ending with a terminator."""
    __slots__ = ("_instructions", "_function", "_predecessors",
                 "_successors", "_attributes", "_is_landing_pad")

    def __init__(self, name: str = "") -> None:
        super().__init__(name, IR_LABEL)
        object.__setattr__(self, "_instructions", [])
        object.__setattr__(self, "_function", None)
        object.__setattr__(self, "_predecessors", [])
        object.__setattr__(self, "_successors", [])
        object.__setattr__(self, "_attributes", [])
        object.__setattr__(self, "_is_landing_pad", False)

    def _value_kind(self) -> ValueKind:
        return ValueKind.BASIC_BLOCK

    # ── Properties ───────────────────────────────────────────────

    @property
    def function(self) -> Optional[IRFunction]:
        return self._function

    @function.setter
    def function(self, func: Optional[IRFunction]) -> None:
        object.__setattr__(self, "_function", func)

    @property
    def instructions(self) -> List[Instruction]:
        return list(self._instructions)

    @property
    def non_terminating(self) -> List[Instruction]:
        """All instructions except the terminator."""
        if self._instructions and self._instructions[-1].is_terminator:
            return self._instructions[:-1]
        return list(self._instructions)

    @property
    def terminator(self) -> Optional[TerminatorInst]:
        """The terminating instruction, if any."""
        from .instructions import TerminatorInst
        if self._instructions and isinstance(self._instructions[-1], TerminatorInst):
            return self._instructions[-1]
        return None

    @property
    def predecessors(self) -> List[BasicBlock]:
        return list(self._predecessors)

    @property
    def successors(self) -> List[BasicBlock]:
        return list(self._successors)

    @property
    def is_empty(self) -> bool:
        return len(self._instructions) == 0

    @property
    def is_landing_pad(self) -> bool:
        return self._is_landing_pad

    @property
    def instruction_count(self) -> int:
        return len(self._instructions)

    # ── Mutation ─────────────────────────────────────────────────

    def append(self, instruction: Instruction) -> None:
        """Append an instruction to the block."""
        self._instructions.append(instruction)
        instruction.parent = self

    def insert_before(self, reference: Instruction, instruction: Instruction) -> None:
        """Insert an instruction before a reference instruction."""
        idx = self._instructions.index(reference)
        self._instructions.insert(idx, instruction)
        instruction.parent = self

    def insert_after(self, reference: Instruction, instruction: Instruction) -> None:
        """Insert an instruction after a reference instruction."""
        idx = self._instructions.index(reference) + 1
        self._instructions.insert(idx, instruction)
        instruction.parent = self

    def remove(self, instruction: Instruction) -> None:
        """Remove an instruction from the block."""
        if instruction in self._instructions:
            self._instructions.remove(instruction)
            if instruction.parent is self:
                instruction.parent = None

    def replace(self, old: Instruction, new: Instruction) -> None:
        """Replace an instruction with another."""
        idx = self._instructions.index(old)
        self._instructions[idx] = new
        new.parent = self
        old.parent = None

    def add_predecessor(self, block: BasicBlock) -> None:
        """Add a predecessor block."""
        if block not in self._predecessors:
            self._predecessors.append(block)

    def remove_predecessor(self, block: BasicBlock) -> None:
        """Remove a predecessor block."""
        if block in self._predecessors:
            self._predecessors.remove(block)

    def add_successor(self, block: BasicBlock) -> None:
        """Add a successor block."""
        if block not in self._successors:
            self._successors.append(block)

    def remove_successor(self, block: BasicBlock) -> None:
        """Remove a successor block."""
        if block in self._successors:
            self._successors.remove(block)

    def clear(self) -> None:
        """Remove all instructions."""
        for inst in self._instructions:
            inst.parent = None
        self._instructions.clear()

    # ── Iteration ────────────────────────────────────────────────

    def __iter__(self) -> Iterator[Instruction]:
        return iter(self._instructions)

    def __len__(self) -> int:
        return len(self._instructions)

    def __getitem__(self, index: int) -> Instruction:
        return self._instructions[index]

    def __repr__(self) -> str:
        label = self._name if self._name else "unnamed"
        return f"block:{label}"
