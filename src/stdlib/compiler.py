"""compiler — Compiler utilities for the I language.

Provides access to the compiler pipeline from within the standard library.
"""

from __future__ import annotations

import sys
import os
from typing import Any, Optional


def version() -> str:
    """Return the I compiler version."""
    return "0.1.0"


def compile_source(source: str, filename: str = "<string>") -> Any:
    """Compile I source code to bytecode."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from compiler.lexer.lexer import Lexer
    from compiler.parser.parser import Parser
    from compiler.codegen.generator import CodeGenerator

    tokens = Lexer(source, filename).tokenize()
    ast = Parser(tokens).parse()
    gen = CodeGenerator()
    gen.generate(ast)
    return gen.get_chunk()


def disassemble(chunk: Any) -> str:
    """Disassemble a bytecode chunk to human-readable form."""
    if hasattr(chunk, "disassemble"):
        return chunk.disassemble()
    return str(chunk)
