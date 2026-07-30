"""
Linking and result types for native compilation.
"""

from __future__ import annotations

from compiler.native.link.interface import (
    LinkerInterface,
    LinkError,
    SystemLinker,
    detect_system_linker,
)
from compiler.native.link.result import CompileResult, OutputFormat

__all__ = [
    "CompileResult",
    "OutputFormat",
    "LinkerInterface",
    "SystemLinker",
    "LinkError",
    "detect_system_linker",
]
