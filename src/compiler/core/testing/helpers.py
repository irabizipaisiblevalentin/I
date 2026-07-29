"""
Test helpers.
"""

from __future__ import annotations

from pathlib import Path

from ..context import CompilerContext
from ..diagnostics.engine import DiagnosticEngine
from ..source.file import SourceFile


class CompilerTestHelper:
    """
    Helper for compiler tests.
    """

    def __init__(self) -> None:
        self._context = CompilerContext()

    @property
    def context(self) -> CompilerContext:
        """Compiler context."""
        return self._context

    @property
    def diagnostics(self) -> DiagnosticEngine:
        """Diagnostic engine."""
        return self._context.diagnostics

    def reset(self) -> None:
        """Reset test context."""
        self._context.reset()

    def add_source(
        self,
        content: str,
        path: Path | None = None,
    ) -> SourceFile:
        """
        Add source to context.

        Args:
            content: Source content
            path: Optional path

        Returns:
            SourceFile instance
        """
        source = SourceFile.from_string(content, path)
        self._context.add_source(source)
        return source

    def assert_no_errors(self) -> None:
        """Assert no errors were reported."""
        assert not self.diagnostics.has_errors, (
            f"Expected no errors, got {self.diagnostics.error_count}: "
            f"{self.diagnostics.format_all()}"
        )

    def assert_errors(self, count: int | None = None) -> None:
        """Assert errors were reported."""
        assert self.diagnostics.has_errors, "Expected errors but found none"

        if count is not None:
            assert self.diagnostics.error_count == count, (
                f"Expected {count} errors, got {self.diagnostics.error_count}"
            )

    def assert_warning_count(self, count: int) -> None:
        """Assert warning count."""
        assert self.diagnostics.warning_count == count, (
            f"Expected {count} warnings, got {self.diagnostics.warning_count}"
        )

    def get_error_messages(self) -> list[str]:
        """Get all error messages."""
        return [d.message for d in self.diagnostics.get_errors()]
