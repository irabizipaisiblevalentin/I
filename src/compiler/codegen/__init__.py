"""
Code Generation package for the I programming language.

This package contains the bytecode generation components.
"""

from compiler.codegen.bytecode import OpCode, Instruction, Chunk
from compiler.codegen.generator import CodeGenerator, generate

__all__ = [
    'OpCode',
    'Instruction',
    'Chunk',
    'CodeGenerator',
    'generate',
]
