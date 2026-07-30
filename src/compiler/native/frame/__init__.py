"""
Stack frame management for native code generation.
"""

from __future__ import annotations

from compiler.native.frame.manager import (
    FrameManager,
    FrameOption,
    FrameOptions,
    StackFrame,
)

__all__ = [
    "StackFrame",
    "FrameManager",
    "FrameOption",
    "FrameOptions",
]
