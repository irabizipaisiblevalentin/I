"""
IR Function

Represents a function in the IR. Contains basic blocks, arguments,
and function-level attributes. A function is both a Value (can be
referenced) and a container for its body.
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .values import Value, ValueKind, Argument
from .types import IRType, IRFunctionType, IRVoid
from .attributes import AttributeSet

if TYPE_CHECKING:
    from typing import Iterator, List
    from .basic_block import BasicBlock
    from .instructions import Instruction
    from .metadata import Metadata


# ══════════════════════════════════════════════════════════════════
# IR Function
# ══════════════════════════════════════════════════════════════════


class IRFunction(Value):
    """An IR function — collection of basic blocks with arguments."""
    __slots__ = ("_func_type", "_blocks", "_args", "_attributes",
                 "_module", "_is_declaration", "_metadata")

    def __init__(
        self,
        name: str,
        func_type: IRFunctionType,
    ) -> None:
        super().__init__(name, func_type)
        object.__setattr__(self, "_func_type", func_type)
        object.__setattr__(self, "_blocks", [])
        object.__setattr__(self, "_args", [])
        object.__setattr__(self, "_attributes", AttributeSet())
        object.__setattr__(self, "_module", None)
        object.__setattr__(self, "_is_declaration", True)
        object.__setattr__(self, "_metadata", {})

        # Create argument objects
        for i, pt in enumerate(func_type.param_types):
            arg = Argument(f"arg{i}", pt, i)
            arg.parent = self
            self._args.append(arg)

    def _value_kind(self) -> ValueKind:
        return ValueKind.FUNCTION

    # ── Properties ───────────────────────────────────────────────

    @property
    def func_type(self) -> IRFunctionType:
        return self._func_type

    @property
    def return_type(self) -> IRType:
        return self._func_type.return_type

    @property
    def blocks(self) -> List[BasicBlock]:
        return list(self._blocks)

    @property
    def basic_blocks(self) -> List[BasicBlock]:
        """Alias for blocks — used by optimization passes."""
        return list(self._blocks)

    def get_block(self, name: str) -> Optional[BasicBlock]:
        """Find a block by name."""
        for b in self._blocks:
            if b.name == name:
                return b
        return None

    @property
    def args(self) -> List[Argument]:
        return list(self._args)

    @property
    def attributes(self) -> AttributeSet:
        return self._attributes

    @property
    def module(self):
        return self._module

    @module.setter
    def module(self, mod) -> None:
        object.__setattr__(self, "_module", mod)

    @property
    def is_declaration(self) -> bool:
        return self._is_declaration

    @property
    def entry_block(self) -> Optional[BasicBlock]:
        """The first basic block (function entry)."""
        return self._blocks[0] if self._blocks else None

    @property
    def block_count(self) -> int:
        return len(self._blocks)

    @property
    def instruction_count(self) -> int:
        return sum(b.instruction_count for b in self._blocks)

    @property
    def metadata(self) -> dict:
        return self._metadata

    # ── Block Management ─────────────────────────────────────────

    def append_block(self, block: BasicBlock) -> None:
        """Add a basic block to the function."""
        if block not in self._blocks:
            self._blocks.append(block)
            block.function = self
            object.__setattr__(self, "_is_declaration", False)

    def insert_block(self, index: int, block: BasicBlock) -> None:
        """Insert a basic block at a specific position."""
        self._blocks.insert(index, block)
        block.function = self
        object.__setattr__(self, "_is_declaration", False)

    def remove_block(self, block: BasicBlock) -> None:
        """Remove a basic block from the function."""
        if block in self._blocks:
            self._blocks.remove(block)
            block.function = None
            # Remove all predecessor/successor references
            for other in self._blocks:
                other.remove_predecessor(block)
                other.remove_successor(block)

    def move_block(self, block: BasicBlock, new_index: int) -> None:
        """Move a block to a new position."""
        if block in self._blocks:
            self._blocks.remove(block)
            self._blocks.insert(new_index, block)

    def replace_block(self, old_block: BasicBlock, new_block: BasicBlock) -> None:
        """Replace a block with another."""
        idx = self._blocks.index(old_block)
        self._blocks[idx] = new_block
        new_block.function = self
        old_block.function = None

    # ── Iteration ────────────────────────────────────────────────

    def __iter__(self) -> Iterator[BasicBlock]:
        return iter(self._blocks)

    def __len__(self) -> int:
        return len(self._blocks)

    def __getitem__(self, index: int) -> BasicBlock:
        return self._blocks[index]

    def __repr__(self) -> str:
        kind = "declare" if self._is_declaration else "define"
        return f"@{self._name} ({kind}, {self.block_count} blocks)"
