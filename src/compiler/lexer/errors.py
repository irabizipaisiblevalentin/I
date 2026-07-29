"""
Lexer Error System

Bilingual error reporting with recovery for the I language lexer.
Every error includes: code, location, English message, Kinyarwanda message,
explanation, and possible solution.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LexerErrorCode(Enum):
    """Lexer error codes."""

    LEX001_INVALID_CHAR = "LEX001"
    LEX002_UNTERMINATED_STRING = "LEX002"
    LEX003_INVALID_NUMBER = "LEX003"
    LEX005_INVALID_ESCAPE = "LEX005"
    LEX006_UNTERMINATED_COMMENT = "LEX006"
    LEX007_INTEGER_OVERFLOW = "LEX007"
    LEX009_UNTERMINATED_CHAR = "LEX009"
    LEX010_UNTERMINATED_RAW_STRING = "LEX010"
    LEX011_UNTERMINATED_TRIPLE_STRING = "LEX011"


# Error messages: (English, Kinyarwanda)
ERROR_MESSAGES: dict[LexerErrorCode, tuple[str, str]] = {
    LexerErrorCode.LEX001_INVALID_CHAR: (
        "Invalid character '{char}'",
        "Ikimenyetso '{char}' nticyemewe",
    ),
    LexerErrorCode.LEX002_UNTERMINATED_STRING: (
        "Unterminated string literal",
        "Ijambo ritagifungiye",
    ),
    LexerErrorCode.LEX003_INVALID_NUMBER: (
        "Invalid number format",
        "Ibaneco ry'ubwoko butari busanzwe",
    ),
    LexerErrorCode.LEX005_INVALID_ESCAPE: (
        "Unknown escape sequence '\\{char}'",
        "Igice kitashyizwe mu buryo '\\{char}'",
    ),
    LexerErrorCode.LEX006_UNTERMINATED_COMMENT: (
        "Unterminated multi-line comment (expected '=#')",
        "Ijambo ry'ubusuzuma ryafunguwe (byitezwe '=#')",
    ),
    LexerErrorCode.LEX007_INTEGER_OVERFLOW: (
        "Integer literal exceeds maximum value (2^63 - 1)",
        "Inameco ryarenze urugero rukuru (2^63 - 1)",
    ),
    LexerErrorCode.LEX009_UNTERMINATED_CHAR: (
        "Unterminated character literal",
        "Ikimenyetso gitagifungiye",
    ),
    LexerErrorCode.LEX010_UNTERMINATED_RAW_STRING: (
        "Unterminated raw string",
        "Ijambo ry'ubwoko raw ritagifungiye",
    ),
    LexerErrorCode.LEX011_UNTERMINATED_TRIPLE_STRING: (
        "Unterminated multi-line string (expected '\"\"\"')",
        "Ijambo ry'ubwoko rirenze umurongo ritagifungiye",
    ),
}

# Suggestions for each error
ERROR_SUGGESTIONS: dict[LexerErrorCode, str] = {
    LexerErrorCode.LEX001_INVALID_CHAR:
        "Remove or replace the character with a valid one",
    LexerErrorCode.LEX002_UNTERMINATED_STRING:
        "Add a closing double quote '\"' at the end of the string",
    LexerErrorCode.LEX003_INVALID_NUMBER:
        "Ensure the number follows the format: digits, optionally with '.' and exponent",
    LexerErrorCode.LEX005_INVALID_ESCAPE:
        "Use a valid escape: \\n, \\t, \\r, \\\\, \\\", \\', \\0, \\uXXXX, \\UXXXXXXXX",
    LexerErrorCode.LEX006_UNTERMINATED_COMMENT:
        "Add '=#' to close the multi-line comment",
    LexerErrorCode.LEX007_INTEGER_OVERFLOW:
        "Use a smaller integer value or split into multiple operations",
    LexerErrorCode.LEX009_UNTERMINATED_CHAR:
        "Add a closing single quote \"'\" at the end of the character",
    LexerErrorCode.LEX010_UNTERMINATED_RAW_STRING:
        "Add a closing '\"' after the raw string content",
    LexerErrorCode.LEX011_UNTERMINATED_TRIPLE_STRING:
        "Add '\"\"\"' to close the multi-line string",
}


@dataclass
class LexerError:
    """
    A single lexer error with bilingual messages.
    """

    code: LexerErrorCode
    line: int
    column: int
    offset: int
    char: str = ""
    severity: str = "ERROR"

    @property
    def message_en(self) -> str:
        """English message."""
        template, _ = ERROR_MESSAGES[self.code]
        return template.format(char=self.char)

    @property
    def message_rw(self) -> str:
        """Kinyarwanda message."""
        _, template = ERROR_MESSAGES[self.code]
        return template.format(char=self.char)

    @property
    def suggestion(self) -> str:
        """Suggested fix."""
        return ERROR_SUGGESTIONS.get(self.code, "")

    @property
    def title(self) -> str:
        """Error title."""
        return self.code.value

    def __str__(self) -> str:
        parts = [
            f"{self.code.value}",
            f"at {self.line}:{self.column}",
            f"- {self.message_en}",
        ]
        if self.char:
            parts.append(f"('{self.char}')")
        parts.append(f"\n  Kinyarwanda: {self.message_rw}")
        parts.append(f"  Suggestion: {self.suggestion}")
        return " ".join(parts[:4]) + "".join(parts[4:])


class LexerErrorCollector:
    """
    Collects lexer errors during tokenization.

    Enforces limits: max 100 errors per file, aborts after
    10 consecutive errors without successful tokenization.
    """

    MAX_ERRORS = 100
    MAX_CONSECUTIVE_ERRORS = 10

    def __init__(self) -> None:
        self._errors: list[LexerError] = []
        self._consecutive_errors = 0

    @property
    def errors(self) -> list[LexerError]:
        """All collected errors."""
        return self._errors.copy()

    @property
    def error_count(self) -> int:
        """Number of errors."""
        return len(self._errors)

    @property
    def has_errors(self) -> bool:
        """Check if any errors were collected."""
        return len(self._errors) > 0

    @property
    def should_abort(self) -> bool:
        """Check if lexer should abort due to too many errors."""
        return (
            len(self._errors) >= self.MAX_ERRORS
            or self._consecutive_errors >= self.MAX_CONSECUTIVE_ERRORS
        )

    def record_success(self) -> None:
        """Record successful tokenization (resets consecutive counter)."""
        self._consecutive_errors = 0

    def add(
        self,
        code: LexerErrorCode,
        line: int,
        column: int,
        offset: int,
        char: str = "",
    ) -> LexerError:
        """
        Add an error.

        Returns the created error, or None if abort conditions met.
        """
        if self.should_abort:
            return None

        error = LexerError(
            code=code,
            line=line,
            column=column,
            offset=offset,
            char=char,
        )
        self._errors.append(error)

        self._consecutive_errors += 1

        return error

    def clear(self) -> None:
        """Clear all errors."""
        self._errors.clear()
        self._consecutive_errors = 0

    def format_all(self) -> str:
        """Format all errors as a string."""
        return "\n".join(str(e) for e in self._errors)
