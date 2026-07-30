"""
I Programming Language — Native Code Emitters

Subsystem for emitting machine code and LLVM IR from the compiler IR.
"""

from __future__ import annotations

from compiler.native.emit.arm64 import ARM64Emitter
from compiler.native.emit.llvm import LLVMCompileError, LLVMEmitter
from compiler.native.emit.x86_64 import X86_64Emitter

__all__ = [
    "LLVMEmitter",
    "LLVMCompileError",
    "X86_64Emitter",
    "ARM64Emitter",
]
