"""
Error codes.
"""

from __future__ import annotations

from enum import Enum


class ErrorCode(Enum):
    """Compiler error codes."""

    # Lexer errors (1xxx)
    LEXER_INVALID_CHARACTER = "E1001"
    LEXER_UNTERMINATED_STRING = "E1002"
    LEXER_UNTERMINATED_COMMENT = "E1003"
    LEXER_INVALID_NUMBER = "E1004"
    LEXER_INVALID_UNICODE = "E1005"

    # Parser errors (2xxx)
    PARSER_EXPECTED_TOKEN = "E2001"
    PARSER_UNEXPECTED_TOKEN = "E2002"
    PARSER_MISSING_SEMICOLON = "E2003"
    PARSER_MISSING_PAREN = "E2004"
    PARSER_INVALID_EXPRESSION = "E2005"
    PARSER_INVALID_STATEMENT = "E2006"

    # Semantic errors (3xxx)
    SEMANTIC_UNDEFINED_VARIABLE = "E3001"
    SEMANTIC_UNDEFINED_FUNCTION = "E3002"
    SEMANTIC_UNDEFINED_TYPE = "E3003"
    SEMANTIC_DUPLICATE_DEFINITION = "E3004"
    SEMANTIC_TYPE_MISMATCH = "E3005"
    SEMANTIC_INVALID_ASSIGNMENT = "E3006"
    SEMANTIC_MISSING_RETURN = "E3007"

    # Type errors (4xxx)
    TYPE_ERROR = "E4001"
    TYPE_MISMATCH = "E4002"
    TYPE_NOT_CALLABLE = "E4003"
    TYPE_NOT_SUBSCRIPTABLE = "E4004"
    TYPE_OUT_OF_RANGE = "E4005"

    # IR errors (5xxx)
    IR_INVALID_INSTRUCTION = "E5001"
    IR_STACK_OVERFLOW = "E5002"
    IR_INVALID_OPERAND = "E5003"

    # Runtime errors (6xxx)
    RUNTIME_ERROR = "E6001"
    RUNTIME_TYPE_ERROR = "E6002"
    RUNTIME_INDEX_ERROR = "E6003"
    RUNTIME_NULL_ERROR = "E6004"
    RUNTIME_DIVISION_BY_ZERO = "E6005"

    # IO errors (7xxx)
    IO_FILE_NOT_FOUND = "E7001"
    IO_PERMISSION_DENIED = "E7002"
    IO_READ_ERROR = "E7003"
    IO_WRITE_ERROR = "E7004"

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_value(cls, value: str) -> ErrorCode:
        """Parse error code from string."""
        for code in cls:
            if code.value == value:
                return code
        raise ValueError(f"Unknown error code: {value}")
