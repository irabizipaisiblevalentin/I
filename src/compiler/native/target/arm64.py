"""
ARM64 target architecture description.
"""

from __future__ import annotations

from compiler.native.target.desc import TargetDescription
from compiler.native.target.kind import TargetKind


class ARM64Features:
    """Feature flags for ARM64."""

    __slots__ = ("neon", "sve")

    def __init__(self, neon: bool = True, sve: bool = False) -> None:
        self.neon = neon
        self.sve = sve

    def to_frozenset(self) -> frozenset[str]:
        features: set[str] = set()
        if self.neon:
            features.add("neon")
        if self.sve:
            features.add("sve")
        return frozenset(features)

    def __repr__(self) -> str:
        parts = [k for k in ("neon", "sve") if getattr(self, k)]
        return f"ARM64Features({', '.join(parts)})"


class ARM64Registers:
    """Register information for ARM64."""

    __slots__ = ()

    GPR: tuple[str, ...] = tuple(f"x{i}" for i in range(31))

    SIMD: tuple[str, ...] = tuple(f"v{i}" for i in range(32))

    _CALLER_SAVED_GPR: tuple[str, ...] = tuple(f"x{i}" for i in range(19))
    _CALLEE_SAVED_GPR: tuple[str, ...] = tuple(f"x{i}" for i in range(19, 30))

    _CALLER_SAVED_SIMD: tuple[str, ...] = (
        tuple(f"v{i}" for i in range(8)) + tuple(f"v{i}" for i in range(16, 32))
    )
    _CALLEE_SAVED_SIMD: tuple[str, ...] = tuple(f"v{i}" for i in range(8, 16))

    _ARG_GPR: tuple[str, ...] = tuple(f"x{i}" for i in range(8))
    _ARG_SIMD: tuple[str, ...] = tuple(f"v{i}" for i in range(8))

    @classmethod
    def caller_saved(cls) -> tuple[str, ...]:
        return cls._CALLER_SAVED_GPR + cls._CALLER_SAVED_SIMD

    @classmethod
    def callee_saved(cls) -> tuple[str, ...]:
        return cls._CALLEE_SAVED_GPR + cls._CALLEE_SAVED_SIMD

    @classmethod
    def arg_registers(cls) -> tuple[str, ...]:
        return cls._ARG_GPR + cls._ARG_SIMD

    @staticmethod
    def is_gpr(name: str) -> bool:
        n = name.lower()
        if n.startswith("x") and n[1:].isdigit():
            return 0 <= int(n[1:]) <= 30
        return False

    @staticmethod
    def is_simd(name: str) -> bool:
        n = name.lower()
        if n.startswith("v") and n[1:].isdigit():
            return 0 <= int(n[1:]) <= 31
        return False


class ARM64Target:
    """Target description for ARM64."""

    __slots__ = ("features", "target")

    def __init__(self, features: ARM64Features | None = None) -> None:
        self.features = features or ARM64Features()
        self.target = TargetDescription(
            kind=TargetKind.ARM64,
            bits=64,
            triple="aarch64-unknown-unknown",
            features=self.features.to_frozenset(),
        )

    @property
    def kind(self) -> TargetKind:
        return self.target.kind

    @property
    def bits(self) -> int:
        return self.target.bits

    @property
    def triple(self) -> str:
        return self.target.triple

    @property
    def register_width(self) -> int:
        return 64

    @property
    def stack_alignment(self) -> int:
        return 16

    @property
    def endianness(self) -> str:
        return "little"

    @property
    def preferred_reg_order(self) -> tuple[str, ...]:
        return tuple(f"x{i}" for i in range(19)) + tuple(f"x{i}" for i in range(19, 30)) + tuple(f"v{i}" for i in range(32))

    @property
    def registers(self) -> type[ARM64Registers]:
        return ARM64Registers
