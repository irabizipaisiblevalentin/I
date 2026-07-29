"""
Tests for message formatting.
"""

from pathlib import Path

from src.compiler.core.formatting import MessageFormatter
from src.compiler.core.diagnostics import Diagnostic, Severity
from src.compiler.core.source import SourceFile, PositionTracker


class TestMessageFormatter:
    """Tests for MessageFormatter."""

    def test_creation(self):
        formatter = MessageFormatter()
        assert formatter is not None

    def test_format_diagnostic_without_color(self):
        formatter = MessageFormatter(use_color=False)
        source = SourceFile.from_string("hello", Path("test.il"))
        tracker = PositionTracker(source)
        span = tracker.create_span(0, 5)
        diag = Diagnostic(
            severity=Severity.ERROR,
            message="test error",
            span=span,
        )
        output = formatter.format_diagnostic(diag)
        assert "ERROR" in output
        assert "test error" in output

    def test_format_diagnostic_with_color(self):
        formatter = MessageFormatter(use_color=True)
        source = SourceFile.from_string("hello", Path("test.il"))
        tracker = PositionTracker(source)
        span = tracker.create_span(0, 5)
        diag = Diagnostic(
            severity=Severity.WARNING,
            message="test warning",
            span=span,
        )
        output = formatter.format_diagnostic(diag)
        assert "\033[" in output
        assert "WARNING" in output
        assert "test warning" in output

    def test_format_all(self):
        formatter = MessageFormatter(use_color=False)
        diag1 = Diagnostic(severity=Severity.ERROR, message="error 1")
        diag2 = Diagnostic(severity=Severity.WARNING, message="warning 2")
        output = formatter.format_all([diag1, diag2])
        assert "error 1" in output
        assert "warning 2" in output

    def test_format_with_labels(self):
        formatter = MessageFormatter(use_color=False)
        source = SourceFile.from_string("line1\nline2")
        tracker = PositionTracker(source)
        span = tracker.create_span(0, 5)
        diag = Diagnostic(
            severity=Severity.ERROR,
            message="msg",
            span=span,
        )
        diag.add_label(span, "label1")
        output = formatter.format_diagnostic(diag)
        assert "label1" in output

    def test_format_with_notes(self):
        formatter = MessageFormatter(use_color=False)
        diag = Diagnostic(
            severity=Severity.WARNING,
            message="msg",
        )
        diag.add_note("note text")
        output = formatter.format_diagnostic(diag)
        assert "note:" in output
        assert "note text" in output

    def test_severity_colors(self):
        from src.compiler.core.formatting import COLORS, Severity
        for sev in Severity:
            assert sev in COLORS
