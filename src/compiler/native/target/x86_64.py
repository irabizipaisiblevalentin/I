"""
x86-64 target architecture description.
"""

from __future__ import annotations

from compiler.native.target.desc import TargetDescription
from compiler.native.target.kind import TargetKind


class X86_64Features:  # noqa: N801
    """Feature flags for x86-64."""

    __slots__ = ("sse2", "avx", "avx2", "avx512")

    def __init__(
        self,
        sse2: bool = True,
        avx: bool = False,
        avx2: bool = False,
        avx512: bool = False,
    ) -> None:
        self.sse2 = sse2
        self.avx = avx
        self.avx2 = avx2
        self.avx512 = avx512

    def to_frozenset(self) -> frozenset[str]:
        features: set[str] = set()
        if self.sse2:
            features.add("sse2")
        if self.avx:
            features.add("avx")
        if self.avx2:
            features.add("avx2")
        if self.avx512:
            features.add("avx512")
        return frozenset(features)

    def __repr__(self) -> str:
        parts = [k for k in ("sse2", "avx", "avx2", "avx512") if getattr(self, k)]
        return f"X86_64Features({', '.join(parts)})"


class X86_64Registers:  # noqa: N801
    """Register information for x86-64."""

    __slots__ = ()

    GPR: tuple[str, ...] = (
        "rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp",
        "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15",
    )

    XMM: tuple[str, ...] = tuple(f"xmm{i}" for i in range(16))

    _CALLER_SAVED_GPR: tuple[str, ...] = (
        "rax", "rcx", "rdx", "rsi", "rdi", "r8", "r9", "r10", "r11",
    )

    _CALLEE_SAVED_GPR: tuple[str, ...] = (
        "rbx", "rbp", "rsp", "r12", "r13", "r14", "r15",
    )

    _ARG_GPR: tuple[str, ...] = ("rdi", "rsi", "rdx", "rcx", "r8", "r9")
    _ARG_XMM: tuple[str, ...] = tuple(f"xmm{i}" for i in range(8))

    @classmethod
    def caller_saved(cls) -> tuple[str, ...]:
        return cls._CALLER_SAVED_GPR + cls.XMM

    @classmethod
    def callee_saved(cls) -> tuple[str, ...]:
        return cls._CALLEE_SAVED_GPR

    @classmethod
    def arg_registers(cls) -> tuple[str, ...]:
        return cls._ARG_GPR + cls._ARG_XMM

    @staticmethod
    def is_gpr(name: str) -> bool:
        return name.lower() in X86_64Registers.GPR

    @staticmethod
    def is_xmm(name: str) -> bool:
        return name.lower().startswith("xmm") and len(name) > 3 and name[3:].isdigit()


class X86_64Target:  # noqa: N801
    """Target description for x86-64."""

    __slots__ = ("features", "target")

    def __init__(self, features: X86_64Features | None = None) -> None:
        self.features = features or X86_64Features()
        self.target = TargetDescription(
            kind=TargetKind.X86_64,
            bits=64,
            triple="x86_64-unknown-unknown",
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
        return (
            "rax", "rcx", "rdx", "rsi", "rdi", "r8", "r9", "r10", "r11",
            "rbx", "r12", "r13", "r14", "r15",
            "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6", "xmm7",
            "xmm8", "xmm9", "xmm10", "xmm11", "xmm12", "xmm13", "xmm14", "xmm15",
        )

    @property
    def registers(self) -> type[X86_64Registers]:
        return X86_64Registers
