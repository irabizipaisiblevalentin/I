"""
Diagnostic engine.

Collects and manages diagnostics during compilation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .diagnostic import Diagnostic
from .severity import Severity

if TYPE_CHECKING:
    from ..source.position import Span


class DiagnosticEngine:
    """
    Diagnostic collection engine.

    Collects diagnostics during compilation and provides
    methods for reporting errors, warnings, and hints.
    """

    def __init__(self) -> None:
        self._diagnostics: list[Diagnostic] = []
        self._errors: int = 0
        self._warnings: int = 0

    @property
    def diagnostics(self) -> list[Diagnostic]:
        """All diagnostics."""
        return self._diagnostics.copy()

    @property
    def error_count(self) -> int:
        """Number of errors."""
        return self._errors

    @property
    def warning_count(self) -> int:
        """Number of warnings."""
        return self._warnings

    @property
    def has_errors(self) -> bool:
        """Check if any errors were reported."""
        return self._errors > 0

    def emit(
        self,
        severity: Severity,
        message: str,
        span: Span | None = None,
        code: str | None = None,
    ) -> Diagnostic:
        """
        Emit a diagnostic.

        Args:
            severity: Diagnostic severity
            message: Error message
            span: Source location
            code: Error code

        Returns:
            Created diagnostic
        """
        diagnostic = Diagnostic(
            severity=severity,
            message=message,
            span=span,
            code=code,
        )

        self._diagnostics.append(diagnostic)

        if severity >= Severity.ERROR:
            self._errors += 1
        elif severity == Severity.WARNING:
            self._warnings += 1

        return diagnostic

    def error(
        self,
        message: str,
        span: Span | None = None,
        code: str | None = None,
    ) -> Diagnostic:
        """Report an error."""
        return self.emit(Severity.ERROR, message, span, code)

    def warning(
        self,
        message: str,
        span: Span | None = None,
        code: str | None = None,
    ) -> Diagnostic:
        """Report a warning."""
        return self.emit(Severity.WARNING, message, span, code)

    def note(
        self,
        message: str,
        span: Span | None = None,
    ) -> Diagnostic:
        """Report a note."""
        return self.emit(Severity.NOTE, message, span)

    def help(
        self,
        message: str,
        span: Span | None = None,
    ) -> Diagnostic:
        """Report a help message."""
        return self.emit(Severity.HELP, message, span)

    def clear(self) -> None:
        """Clear all diagnostics."""
        self._diagnostics.clear()
        self._errors = 0
        self._warnings = 0

    def get_errors(self) -> list[Diagnostic]:
        """Get all error diagnostics."""
        return [d for d in self._diagnostics if d.is_error]

    def get_warnings(self) -> list[Diagnostic]:
        """Get all warning diagnostics."""
        return [d for d in self._diagnostics if d.is_warning]

    def format_all(self) -> str:
        """Format all diagnostics."""
        return "\n".join(str(d) for d in self._diagnostics)
