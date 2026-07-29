"""
I Programming Language Parser

Recursive descent parser with Pratt expression parsing.
Transforms token stream into validated AST.
"""

from .parser import Parser, parse
from .errors import ParseError, ParseErrorCode, ParseErrorCollector

__all__ = [
    "Parser",
    "parse",
    "ParseError",
    "ParseErrorCode",
    "ParseErrorCollector",
]
