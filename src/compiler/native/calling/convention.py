"""
Calling conventions for x86-64 (System V / Microsoft) and ARM64.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from compiler.ir.function import IRFunction
from compiler.ir.types import (
    FloatType,
    IntegerType,
    IRType,
    IRTypeKind,
    PointerType,
    VectorType,
)

if TYPE_CHECKING:
    from compiler.ir.types import IRFunctionType
    from compiler.native.target.desc import TargetDescription


@dataclass(frozen=True, slots=True)
class ArgLocation:
    """Describes where a function argument is passed."""
    register: str | None = None
    stack_offset: int | None = None
    float_reg: str | None = None

    @property
    def is_register(self) -> bool:
        return self.register is not None or self.float_reg is not None

    @property
    def is_stack(self) -> bool:
        return self.stack_offset is not None


class CallingConvention(ABC):
    """Abstract base for target-specific calling conventions."""

    __slots__ = ()

    @abstractmethod
    def assign_args(self, func_type: IRFunctionType) -> list[ArgLocation]:
        ...

    @abstractmethod
    def return_register(self, return_type: IRType) -> str:
        ...

    @abstractmethod
    def caller_saved_registers(self) -> tuple[str, ...]:
        ...

    @abstractmethod
    def callee_saved_registers(self) -> tuple[str, ...]:
        ...

    @abstractmethod
    def arg_registers(self) -> tuple[str, ...]:
        ...

    @abstractmethod
    def shadow_space_bytes(self) -> int:
        ...

    @abstractmethod
    def stack_alignment(self) -> int:
        ...

    def is_float_type(self, t: IRType) -> bool:
        return t.kind == IRTypeKind.FLOAT

    def is_integer_or_pointer(self, t: IRType) -> bool:
        return t.kind in (IRTypeKind.INTEGER, IRTypeKind.POINTER)

    def type_width(self, t: IRType) -> int:
        if isinstance(t, IntegerType):
            return t.bit_width
        if isinstance(t, FloatType):
            return t.bit_width
        if isinstance(t, PointerType):
            return 64
        if isinstance(t, VectorType):
            return t.element_count * self.type_width(t.element_type)
        return 64


class SystemVConvention(CallingConvention):
    """System V AMD64 ABI calling convention."""

    __slots__ = ()

    INT_ARG_REGS: tuple[str, ...] = ("rdi", "rsi", "rdx", "rcx", "r8", "r9")
    FLOAT_ARG_REGS: tuple[str, ...] = ("xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7")
    RETURN_INT_REGS: tuple[str, ...] = ("rax", "rdx")
    RETURN_FLOAT_REGS: tuple[str, ...] = ("xmm0", "xmm1")

    def assign_args(self, func_type: IRFunctionType) -> list[ArgLocation]:
        locations: list[ArgLocation] = []
        int_idx = 0
        float_idx = 0
        stack_offset = 0

        for param_type in func_type.param_types:
            if self.is_float_type(param_type):
                if float_idx < len(self.FLOAT_ARG_REGS):
                    locations.append(ArgLocation(float_reg=self.FLOAT_ARG_REGS[float_idx]))
                    float_idx += 1
                else:
                    locations.append(ArgLocation(stack_offset=stack_offset))
                    stack_offset += 8
            else:
                if int_idx < len(self.INT_ARG_REGS):
                    locations.append(ArgLocation(register=self.INT_ARG_REGS[int_idx]))
                    int_idx += 1
                else:
                    locations.append(ArgLocation(stack_offset=stack_offset))
                    stack_offset += 8

        return locations

    def return_register(self, return_type: IRType) -> str:
        if self.is_float_type(return_type):
            return "xmm0"
        return "rax"

    def caller_saved_registers(self) -> tuple[str, ...]:
        return (
            "rax", "rcx", "rdx", "rsi", "rdi", "r8", "r9", "r10", "r11",
            "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7",
            "xmm8", "xmm9", "xmm10", "xmm11", "xmm12", "xmm13", "xmm14", "xmm15",
        )

    def callee_saved_registers(self) -> tuple[str, ...]:
        return ("rbx", "rbp", "r12", "r13", "r14", "r15")

    def arg_registers(self) -> tuple[str, ...]:
        return self.INT_ARG_REGS + self.FLOAT_ARG_REGS

    def shadow_space_bytes(self) -> int:
        return 0

    def stack_alignment(self) -> int:
        return 16


class MicrosoftConvention(CallingConvention):
    """Microsoft x64 ABI calling convention."""

    __slots__ = ()

    INT_ARG_REGS: tuple[str, ...] = ("rcx", "rdx", "r8", "r9")
    FLOAT_ARG_REGS: tuple[str, ...] = ("xmm0", "xmm1", "xmm2", "xmm3")
    RETURN_INT_REGS: tuple[str, ...] = ("rax",)
    RETURN_FLOAT_REGS: tuple[str, ...] = ("xmm0",)

    def assign_args(self, func_type: IRFunctionType) -> list[ArgLocation]:
        locations: list[ArgLocation] = []
        int_idx = 0
        float_idx = 0
        stack_offset = 0

        for param_type in func_type.param_types:
            if self.is_float_type(param_type):
                if float_idx < len(self.FLOAT_ARG_REGS):
                    locations.append(ArgLocation(float_reg=self.FLOAT_ARG_REGS[float_idx]))
                    float_idx += 1
                else:
                    locations.append(ArgLocation(stack_offset=stack_offset + 32))
                    stack_offset += 8
            else:
                if int_idx < len(self.INT_ARG_REGS):
                    locations.append(ArgLocation(register=self.INT_ARG_REGS[int_idx]))
                    int_idx += 1
                else:
                    locations.append(ArgLocation(stack_offset=stack_offset + 32))
                    stack_offset += 8

        return locations

    def return_register(self, return_type: IRType) -> str:
        if self.is_float_type(return_type):
            return "xmm0"
        return "rax"

    def caller_saved_registers(self) -> tuple[str, ...]:
        return (
            "rax", "rcx", "rdx", "r8", "r9", "r10", "r11",
            "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5",
            "xmm6", "xmm7", "xmm8", "xmm9", "xmm10", "xmm11",
            "xmm12", "xmm13", "xmm14", "xmm15",
        )

    def callee_saved_registers(self) -> tuple[str, ...]:
        return ("rbx", "rbp", "rdi", "rsi", "r12", "r13", "r14", "r15")

    def arg_registers(self) -> tuple[str, ...]:
        return self.INT_ARG_REGS + self.FLOAT_ARG_REGS

    def shadow_space_bytes(self) -> int:
        return 32

    def stack_alignment(self) -> int:
        return 16


class ARM64Convention(CallingConvention):
    """ARM64 ABI calling convention."""

    __slots__ = ()

    INT_ARG_REGS: tuple[str, ...] = tuple(f"x{i}" for i in range(8))
    FLOAT_ARG_REGS: tuple[str, ...] = tuple(f"v{i}" for i in range(8))
    RETURN_INT_REGS: tuple[str, ...] = ("x0",)
    RETURN_FLOAT_REGS: tuple[str, ...] = ("v0",)

    def assign_args(self, func_type: IRFunctionType) -> list[ArgLocation]:
        locations: list[ArgLocation] = []
        int_idx = 0
        float_idx = 0
        stack_offset = 0

        for param_type in func_type.param_types:
            if self.is_float_type(param_type):
                if float_idx < len(self.FLOAT_ARG_REGS):
                    locations.append(ArgLocation(float_reg=self.FLOAT_ARG_REGS[float_idx]))
                    float_idx += 1
                else:
                    locations.append(ArgLocation(stack_offset=stack_offset))
                    stack_offset += 8
            else:
                if int_idx < len(self.INT_ARG_REGS):
                    locations.append(ArgLocation(register=self.INT_ARG_REGS[int_idx]))
                    int_idx += 1
                else:
                    locations.append(ArgLocation(stack_offset=stack_offset))
                    stack_offset += 8

        return locations

    def return_register(self, return_type: IRType) -> str:
        if self.is_float_type(return_type):
            return "v0"
        return "x0"

    def caller_saved_registers(self) -> tuple[str, ...]:
        return tuple(f"x{i}" for i in range(19)) + tuple(f"v{i}" for i in range(8)) + tuple(f"v{i}" for i in range(16, 32))

    def callee_saved_registers(self) -> tuple[str, ...]:
        return tuple(f"x{i}" for i in range(19, 30)) + tuple(f"v{i}" for i in range(8, 16))

    def arg_registers(self) -> tuple[str, ...]:
        return self.INT_ARG_REGS + self.FLOAT_ARG_REGS

    def shadow_space_bytes(self) -> int:
        return 0

    def stack_alignment(self) -> int:
        return 16


_CONVENTION_CACHE: dict[str, CallingConvention] = {}

_SYSTEM_V = SystemVConvention()
_MICROSOFT = MicrosoftConvention()
_ARM64_C = ARM64Convention()


def select_convention(
    target: TargetDescription,
    function: IRFunction | None = None,
) -> CallingConvention:
    """Select the appropriate calling convention for the given target."""
    from compiler.native.target.kind import TargetKind

    if target.kind == TargetKind.ARM64:
        return _ARM64_C

    triple = target.triple.lower()
    if "windows" in triple or "msvc" in triple:
        return _MICROSOFT

    return _SYSTEM_V
