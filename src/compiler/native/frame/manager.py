"""
Stack frame manager — computes frame layout and generates prologue/epilogue.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compiler.ir.function import IRFunction
    from compiler.native.target.desc import TargetDescription


class FrameOption(Enum):
    RED_ZONE = auto()
    STACK_CANARY = auto()
    GUARD_PAGE = auto()
    OMIT_FRAME_POINTER = auto()


@dataclass
class FrameOptions:
    flags: frozenset[FrameOption] = field(default_factory=frozenset)

    @property
    def red_zone(self) -> bool:
        return FrameOption.RED_ZONE in self.flags

    @property
    def stack_canary(self) -> bool:
        return FrameOption.STACK_CANARY in self.flags

    @property
    def guard_page(self) -> bool:
        return FrameOption.GUARD_PAGE in self.flags

    @property
    def omit_frame_pointer(self) -> bool:
        return FrameOption.OMIT_FRAME_POINTER in self.flags

    @classmethod
    def default(cls) -> FrameOptions:
        return cls(frozenset())

    @classmethod
    def optimized(cls) -> FrameOptions:
        return cls(frozenset({FrameOption.OMIT_FRAME_POINTER}))

    @classmethod
    def secure(cls) -> FrameOptions:
        return cls(frozenset({FrameOption.STACK_CANARY}))


@dataclass
class StackFrame:
    """Layout of a single function's stack frame."""

    local_size: int = 0
    spill_size: int = 0
    saved_regs_size: int = 0
    shadow_space: int = 0
    canary_size: int = 0
    alignment: int = 16
    leaf_function: bool = False
    has_return_address: bool = True
    options: FrameOptions = field(default_factory=FrameOptions.default)

    _local_offsets: dict[int, int] = field(default_factory=dict)
    _arg_offsets: dict[int, int] = field(default_factory=dict)
    _spill_offsets: dict[int, int] = field(default_factory=dict)

    @property
    def frame_size(self) -> int:
        """Total stack frame size before alignment."""
        return (
            self.local_size
            + self.spill_size
            + self.saved_regs_size
            + self.shadow_space
            + self.canary_size
        )

    @property
    def aligned_frame_size(self) -> int:
        """Frame size rounded up to stack alignment."""
        return _align_up(self.frame_size, self.alignment)

    @property
    def total_frame_size(self) -> int:
        """Total including return address slot (pushed rbp)."""
        total = self.aligned_frame_size
        if self.has_return_address:
            total += 8
        return total

    @property
    def red_zone_size(self) -> int:
        if self.leaf_function and self.options.red_zone:
            return 128
        return 0

    def local_offset(self, index: int) -> int:
        return self._local_offsets.get(index, 0)

    def arg_offset(self, index: int) -> int:
        return self._arg_offsets.get(index, 0)

    def spill_slot_offset(self, index: int) -> int:
        return self._spill_offsets.get(index, 0)


class FrameManager:
    """Manages stack frame layout for compiled functions."""

    __slots__ = ("_options",)

    def __init__(self, options: FrameOptions | None = None) -> None:
        self._options = options or FrameOptions.default()

    def allocate_frame(
        self,
        function: IRFunction,
        target: TargetDescription,
        saved_regs: int = 0,
        spill_slots: int = 0,
        local_var_sizes: list[int] | None = None,
        shadow_space: int | None = None,
    ) -> StackFrame:

        if local_var_sizes is None:
            local_var_sizes = []

        is_leaf = self._is_leaf_function(function)
        alignment = self._stack_alignment(target)

        if shadow_space is None:
            shadow_space = self._shadow_space_for_target(target)

        local_total = sum(local_var_sizes)
        spill_total = spill_slots * 8

        frame = StackFrame(
            local_size=local_total,
            spill_size=spill_total,
            saved_regs_size=saved_regs * 8,
            shadow_space=shadow_space,
            canary_size=8 if self._options.stack_canary else 0,
            alignment=alignment,
            leaf_function=is_leaf,
            has_return_address=not self._options.omit_frame_pointer,
            options=self._options,
        )

        offset = 0
        for i, sz in enumerate(local_var_sizes):
            offset -= sz
            offset = _align_down(offset, sz) if sz > 1 else offset
            frame._local_offsets[i] = offset

        for i in range(spill_slots):
            frame._spill_offsets[i] = offset - 8 * (i + 1)

        for i in range(len(function.func_type.param_types)):
            frame._arg_offsets[i] = 16 + i * 8

        return frame

    def local_offset(self, frame: StackFrame, index: int) -> int:
        return frame.local_offset(index)

    def arg_offset(self, frame: StackFrame, index: int) -> int:
        return frame.arg_offset(index)

    def spill_slot_offset(self, frame: StackFrame, index: int) -> int:
        return frame.spill_slot_offset(index)

    def prologue_bytes(
        self,
        function: IRFunction,
        target: TargetDescription,
        frame: StackFrame | None = None,
    ) -> bytes:
        if frame is None:
            frame = self.allocate_frame(function, target)

        buf = bytearray()

        if frame.has_return_address:
            buf.extend(b"\x55")
            buf.extend(b"\x48\x89\xe5")

        total = frame.aligned_frame_size
        if total > 0:
            if total < 128:
                buf.extend(b"\x48\x83\xec" + total.to_bytes(1, "little"))
            else:
                buf.extend(b"\x48\x81\xec" + total.to_bytes(4, "little"))

        if frame.options.stack_canary:
            buf.extend(b"\x48\x8b\x04\x25\x28\x00\x00\x00")
            buf.extend(b"\x48\x89\x44\x24" + (frame.aligned_frame_size - 8).to_bytes(1, "little"))

        return bytes(buf)

    def epilogue_bytes(
        self,
        function: IRFunction,
        target: TargetDescription,
        frame: StackFrame | None = None,
    ) -> bytes:
        if frame is None:
            frame = self.allocate_frame(function, target)

        buf = bytearray()

        if frame.options.stack_canary:
            off = frame.aligned_frame_size - 8
            buf.extend(b"\x48\x8b\x44\x24" + off.to_bytes(1, "little"))
            buf.extend(b"\x48\x33\x04\x25\x28\x00\x00\x00")

        total = frame.aligned_frame_size
        if total > 0:
            if total < 128:
                buf.extend(b"\x48\x83\xc4" + total.to_bytes(1, "little"))
            else:
                buf.extend(b"\x48\x81\xc4" + total.to_bytes(4, "little"))

        if frame.has_return_address:
            buf.extend(b"\x5d")

        buf.extend(b"\xc3")

        return bytes(buf)

    def _is_leaf_function(self, function: IRFunction) -> bool:
        for block in function:
            for inst in block:
                from compiler.ir.instructions import Call
                if isinstance(inst, Call):
                    return False
        return True

    def _stack_alignment(self, target: TargetDescription) -> int:
        from compiler.native.target.kind import TargetKind
        if target.kind in (TargetKind.X86_64, TargetKind.ARM64):
            return 16
        if target.kind == TargetKind.X86_32:
            return 4
        return 8

    def _shadow_space_for_target(self, target: TargetDescription) -> int:
        triple = target.triple.lower()
        if "windows" in triple or "msvc" in triple:
            return 32
        return 0


def _align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def _align_down(value: int, alignment: int) -> int:
    return value // alignment * alignment
