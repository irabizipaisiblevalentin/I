"""
I Programming Language Compiler Package.

This package contains the complete compiler implementation for the I programming language.
"""

__version__ = "1.0.0"
__author__ = "Irabizi Paisible Valentin"

from compiler.lexer import Lexer, LexerError, tokenize, Token, TokenType
from compiler.parser import Parser, ParseError, parse
from compiler.semantic import SemanticAnalyzer, SemanticErrorCollection, analyze
from compiler.codegen import CodeGenerator, generate, OpCode, Chunk
from compiler.compiler import Compiler

__all__ = [
    # Version info
    '__version__',
    '__author__',
    
    # Lexer
    'Lexer',
    'LexerError',
    'tokenize',
    'Token',
    'TokenType',
    
    # Parser
    'Parser',
    'ParseError',
    'parse',
    
    # Semantic Analyzer
    'SemanticAnalyzer',
    'SemanticErrorCollection',
    'analyze',
    
    # Code Generator
    'CodeGenerator',
    'generate',
    'OpCode',
    'Chunk',
    
    # Main Compiler
    'Compiler',
]
