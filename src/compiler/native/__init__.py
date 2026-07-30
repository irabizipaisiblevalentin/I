"""
I Programming Language — Native Compiler

Native code generation backend abstraction layer supporting LLVM,
Cranelift, and custom x86-64 / ARM64 backends.
"""

from __future__ import annotations

from compiler.native.backend.base import (
    Backend,
    BackendCapabilities,
    BackendError,
    BackendFeature,
    BackendKind,
)
from compiler.native.backend.manager import BackendManager
from compiler.native.backend.registry import BackendRegistry
from compiler.native.compiler import NativeCompiler, NativeCompilerResult
from compiler.native.link.result import CompileResult, OutputFormat

# Re-export shared types from target / link modules
from compiler.native.target.kind import TargetKind

__all__ = [
    # Backend kind enum
    "BackendKind",
    # Backend features
    "BackendFeature",
    # Backend capabilities
    "BackendCapabilities",
    # Abstract backend
    "Backend",
    # Error
    "BackendError",
    # Registry
    "BackendRegistry",
    # Manager
    "BackendManager",
    # High-level compiler
    "NativeCompiler",
    "NativeCompilerResult",
    # Target kind
    "TargetKind",
    # Compilation result
    "CompileResult",
    "OutputFormat",
]
