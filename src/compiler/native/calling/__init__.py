"""
Calling convention management for native code generation.
"""

from __future__ import annotations

from compiler.native.calling.convention import (
    ArgLocation,
    ARM64Convention,
    CallingConvention,
    MicrosoftConvention,
    SystemVConvention,
    select_convention,
)

__all__ = [
    "CallingConvention",
    "ArgLocation",
    "SystemVConvention",
    "MicrosoftConvention",
    "ARM64Convention",
    "select_convention",
]
