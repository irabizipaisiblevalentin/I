"""
Parser Error System

Bilingual error reporting for the I language parser.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

from ..lexer.token import Token


class ParseErrorCode(Enum):
    """Parser error codes."""

    PARS001_UNEXPECTED_TOKEN = "PARS001"
    PARS002_MISSING_TOKEN = "PARS002"
    PARS003_INVALID_EXPRESSION = "PARS003"
    PARS004_UNTERMINATED_BLOCK = "PARS004"
    PARS005_INVALID_ASSIGNMENT = "PARS005"
    PARS006_MISSING_BLOCK_END = "PARS006"
    PARS007_INVALID_STATEMENT = "PARS007"
    PARS008_TOO_MANY_ERRORS = "PARS008"


ERROR_MESSAGES: dict[ParseErrorCode, tuple[str, str]] = {
    ParseErrorCode.PARS001_UNEXPECTED_TOKEN: (
        "Unexpected token '{found}', expected '{expected}'",
        "Ikimenyetso '{found}' ntikemewe, byitezwe '{expected}'",
    ),
    ParseErrorCode.PARS002_MISSING_TOKEN: (
        "Missing token '{expected}'",
        "Ikimenyetso '{expected}' kiribwa",
    ),
    ParseErrorCode.PARS003_INVALID_EXPRESSION: (
        "Invalid expression",
        "Ibisobanuro bitari byemewe",
    ),
    ParseErrorCode.PARS004_UNTERMINATED_BLOCK: (
        "Unterminated block (expected 'iherezo')",
        "Urubuga rutagifungiye (byitezwe 'iherezo')",
    ),
    ParseErrorCode.PARS005_INVALID_ASSIGNMENT: (
        "Invalid assignment target",
        "Intego y'ibyizwa ntari byemewe",
    ),
    ParseErrorCode.PARS006_MISSING_BLOCK_END: (
        "Missing 'iherezo' to close block",
        "'iherezo' iribwa kurufungura urubuga",
    ),
    ParseErrorCode.PARS007_INVALID_STATEMENT: (
        "Invalid statement",
        "Ijambo ry'ibikorwa ntari ryemewe",
    ),
    ParseErrorCode.PARS008_TOO_MANY_ERRORS: (
        "Too many syntax errors, aborting",
        "Amakosa menshi cyane, irahagarika",
    ),
}


@dataclass
class ParseError:
    """A single parser error with bilingual messages."""

    code: ParseErrorCode
    token: Token
    expected: str = ""
    found: str = ""

    @property
    def message_en(self) -> str:
        template, _ = ERROR_MESSAGES[self.code]
        return template.format(found=self.found, expected=self.expected)

    @property
    def message_rw(self) -> str:
        _, template = ERROR_MESSAGES[self.code]
        return template.format(found=self.found, expected=self.expected)

    @property
    def line(self) -> int:
        return self.token.line

    @property
    def column(self) -> int:
        return self.token.column

    def __str__(self) -> str:
        parts = [
            f"{self.code.value}",
            f"at {self.line}:{self.column}",
            f"- {self.message_en}",
        ]
        if self.expected:
            parts.append(f"\n  Kinyarwanda: {self.message_rw}")
        return " ".join(parts[:3]) + "".join(parts[3:])


class ParseErrorCollector:
    """
    Collects parser errors with abort conditions.
    
    - Max 100 errors per parse
    - Aborts after 10 consecutive errors without successful statement
    """

    MAX_ERRORS = 100
    MAX_CONSECUTIVE = 10

    def __init__(self) -> None:
        self._errors: List[ParseError] = []
        self._consecutive = 0

    @property
    def errors(self) -> List[ParseError]:
        return self._errors.copy()

    @property
    def has_errors(self) -> bool:
        return len(self._errors) > 0

    @property
    def should_abort(self) -> bool:
        return len(self._errors) >= self.MAX_ERRORS

    def record_success(self) -> None:
        self._consecutive = 0

    def add(
        self,
        code: ParseErrorCode,
        token: Token,
        expected: str = "",
        found: str = "",
    ) -> Optional[ParseError]:
        if self.should_abort:
            return None

        error = ParseError(
            code=code,
            token=token,
            expected=expected,
            found=found,
        )
        self._errors.append(error)
        self._consecutive += 1

        if self._consecutive >= self.MAX_CONSECUTIVE:
            abort = ParseError(
                code=ParseErrorCode.PARS008_TOO_MANY_ERRORS,
                token=token,
            )
            self._errors.append(abort)

        return error

    def clear(self) -> None:
        self._errors.clear()
        self._consecutive = 0

    def format_all(self) -> str:
        return "\n".join(str(e) for e in self._errors)
