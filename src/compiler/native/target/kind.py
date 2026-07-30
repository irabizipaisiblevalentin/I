"""
Target architecture kinds.
"""

from __future__ import annotations

from enum import Enum


class TargetKind(Enum):
    """Target architecture kinds supported by the native compiler."""

    X86_64 = "x86_64"
    X86_32 = "x86_32"
    ARM64 = "arm64"
    ARM32 = "arm32"
    RISCV64 = "riscv64"
    RISCV32 = "riscv32"
    WASM32 = "wasm32"
    WASM64 = "wasm64"
