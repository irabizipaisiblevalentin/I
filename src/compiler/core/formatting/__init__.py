"""
Message Formatting

Formats diagnostics for terminal output.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..diagnostics.severity import Severity

if TYPE_CHECKING:
    from ..diagnostics.diagnostic import Diagnostic, Label


# ANSI color codes
COLORS = {
    Severity.DEBUG: "\033[37m",
    Severity.NOTE: "\033[36m",
    Severity.HELP: "\033[36m",
    Severity.WARNING: "\033[33m",
    Severity.ERROR: "\033[31m",
    Severity.BUG: "\033[35m",
}
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


class MessageFormatter:
    """
    Formats diagnostic messages for terminal output.
    """

    def __init__(self, use_color: bool = True) -> None:
        """
        Initialize formatter.

        Args:
            use_color: Whether to use ANSI colors
        """
        self._use_color = use_color

    def format_diagnostic(self, diagnostic: Diagnostic) -> str:
        """
        Format a diagnostic message.

        Args:
            diagnostic: Diagnostic to format

        Returns:
            Formatted string
        """
        parts: list[str] = []

        # Severity and code
        severity_str = diagnostic.severity.name
        if diagnostic.code:
            severity_str += f" {diagnostic.code}"

        if self._use_color:
            color = COLORS.get(diagnostic.severity, "")
            parts.append(f"{color}{BOLD}{severity_str}{RESET}")
        else:
            parts.append(severity_str)

        # Location
        if diagnostic.span:
            parts.append(f" --> {diagnostic.span}")

        parts.append("")

        # Message
        if self._use_color:
            parts.append(f"{BOLD}{diagnostic.message}{RESET}")
        else:
            parts.append(diagnostic.message)

        # Labels
        if diagnostic.labels:
            parts.extend(self._format_labels(diagnostic.labels))

        # Notes
        for note in diagnostic.notes:
            parts.append(f"  {DIM}note:{RESET} {note}")

        return "\n".join(parts)

    def _format_labels(self, labels: list[Label]) -> list[str]:
        """Format labels."""
        result: list[str] = []

        for label in labels:
            if self._use_color:
                result.append(
                    f"  {COLORS.get(label.severity, '')}"
                    f"{label.span.start}{RESET}: "
                    f"{label.message}"
                )
            else:
                result.append(
                    f"  {label.span.start}: {label.message}"
                )

        return result

    def format_all(self, diagnostics: list[Diagnostic]) -> str:
        """
        Format multiple diagnostics.

        Args:
            diagnostics: List of diagnostics

        Returns:
            Formatted string
        """
        return "\n\n".join(
            self.format_diagnostic(d) for d in diagnostics
        )
