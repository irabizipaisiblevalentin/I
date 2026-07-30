"""
Target architecture descriptions for native code generation.
"""

from __future__ import annotations

from compiler.native.target.arm64 import ARM64Features, ARM64Registers, ARM64Target
from compiler.native.target.desc import TargetDescription
from compiler.native.target.kind import TargetKind
from compiler.native.target.platform import (
    Platform,
    detect_architecture,
    detect_platform,
    detect_target,
    host_triple,
    is_linux,
    is_macos,
    is_windows,
)
from compiler.native.target.x86_64 import X86_64Features, X86_64Registers, X86_64Target

__all__ = [
    "TargetDescription",
    "TargetKind",
    "X86_64Features",
    "X86_64Registers",
    "X86_64Target",
    "ARM64Features",
    "ARM64Registers",
    "ARM64Target",
    "Platform",
    "detect_platform",
    "detect_architecture",
    "detect_target",
    "is_windows",
    "is_linux",
    "is_macos",
    "host_triple",
]
