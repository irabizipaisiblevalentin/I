"""
I Programming Language Lexer

Production-quality lexical analyzer for the I programming language.
Transforms source code (.i files) into validated token streams.
"""

from .token import (
    KEYWORDS,
    KEYWORD_VALUES,
    KINYARWANDA_BOOLEANS,
    Token,
    TokenLocation,
    TokenType,
)
from .lexer import Lexer, tokenize
from .errors import (
    LexerError,
    LexerErrorCode,
    LexerErrorCollector,
    ERROR_MESSAGES,
    ERROR_SUGGESTIONS,
)

__all__ = [
    # Token system
    "TokenType",
    "Token",
    "TokenLocation",
    "KEYWORDS",
    "KEYWORD_VALUES",
    "KINYARWANDA_BOOLEANS",
    # Lexer
    "Lexer",
    "tokenize",
    # Errors
    "LexerError",
    "LexerErrorCode",
    "LexerErrorCollector",
    "ERROR_MESSAGES",
    "ERROR_SUGGESTIONS",
]
