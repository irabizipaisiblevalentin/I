"""
Abstract base classes for native code generation backends.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compiler.ir.module import IRModule
    from compiler.native.link.result import CompileResult
    from compiler.native.target.kind import TargetKind


class BackendKind(Enum):
    """Supported backend implementations."""

    LLVM = "llvm"
    CRANELIFT = "cranelift"
    CUSTOM_X86_64 = "custom_x86_64"
    CUSTOM_ARM64 = "custom_arm64"


class BackendError(Exception):
    """Base exception for all backend-related errors."""


class BackendFeature(Enum):
    """CPU feature flags a backend may support."""

    SSE2 = "sse2"
    SSE3 = "sse3"
    SSSE3 = "ssse3"
    SSE4_1 = "sse4.1"
    SSE4_2 = "sse4.2"
    AVX = "avx"
    AVX2 = "avx2"
    AVX512F = "avx512f"
    AVX512BW = "avx512bw"
    AVX512DQ = "avx512dq"
    AVX512VL = "avx512vl"
    AVX512CD = "avx512cd"
    NEON = "neon"
    SVE = "sve"
    SVE2 = "sve2"
    FP16 = "fp16"
    BMI1 = "bmi1"
    BMI2 = "bmi2"
    LZCNT = "lzcnt"
    POPCNT = "popcnt"
    AES = "aes"
    SHA = "sha"
    RDRAND = "rdrand"
    RDSEED = "rdseed"
    SGX = "sgx"
    ADX = "adx"
    FMA = "fma"
    VAES = "vaes"
    VPCLMULQDQ = "vpclmulqdq"


@dataclass(frozen=True)
class BackendCapabilities:
    """Describes the capabilities of a backend."""

    features: frozenset[BackendFeature] = field(default_factory=frozenset)
    supports_debug: bool = False
    supports_profiling: bool = False
    supports_lto: bool = False
    supports_pic: bool = False
    supports_pie: bool = False
    supports_optimization_levels: tuple[int, int] = (0, 3)
    max_vector_width: int = 128
    preferred_alignment: int = 16
    supports_inline_assembly: bool = False
    supports_coverage: bool = False
    supports_sanitizers: bool = False


class Backend(abc.ABC):
    """Abstract base class for a native code generation backend."""

    __slots__ = ()

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Human-readable backend name."""

    @property
    @abc.abstractmethod
    def kind(self) -> BackendKind:
        """Backend kind identifier."""

    @property
    @abc.abstractmethod
    def capabilities(self) -> BackendCapabilities:
        """Capabilities advertised by this backend."""

    @abc.abstractmethod
    def compile(self, module: IRModule) -> CompileResult:
        """Compile an IR module into memory (default format)."""

    @abc.abstractmethod
    def compile_to_object(
        self,
        module: IRModule,
        target: TargetKind,
        format: str = "elf",
    ) -> bytes:
        """Compile to object-file bytes."""

    @abc.abstractmethod
    def compile_to_executable(
        self,
        module: IRModule,
        target: TargetKind,
        output_path: str | Path,
    ) -> Path:
        """Compile and link into an executable at *output_path*."""
