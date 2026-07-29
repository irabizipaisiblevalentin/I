"""
I Programming Language Lexer

Production-quality lexical analyzer for the I programming language.
Transforms source code (.i files) into validated token streams.
"""

from .errors import (
    ERROR_MESSAGES,
    ERROR_SUGGESTIONS,
    LexerError,
    LexerErrorCode,
    LexerErrorCollector,
)
from .lexer import Lexer, tokenize
from .token import (
    KEYWORD_VALUES,
    KEYWORDS,
    KINYARWANDA_LITERALS,
    Token,
    TokenLocation,
    TokenType,
)

__all__ = [
    # Token system
    "TokenType",
    "Token",
    "TokenLocation",
    "KEYWORDS",
    "KEYWORD_VALUES",
    "KINYARWANDA_LITERALS",
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
