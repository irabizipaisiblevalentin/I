"""
Tests for Diagnostics.
"""

import pytest

from src.compiler.core.diagnostics import (
    Severity,
    Diagnostic,
    DiagnosticEngine,
    ErrorCode,
    Hint,
    HintKind,
)
from src.compiler.core.source import SourceFile, Position, Span


# ============================================================================
# Severity Tests
# ============================================================================


class TestSeverity:
    """Tests for Severity."""
    
    def test_from_string(self):
        """Test parsing severity from string."""
        assert Severity.from_string("ERROR") == Severity.ERROR
        assert Severity.from_string("warning") == Severity.WARNING
        assert Severity.from_string("NOTE") == Severity.NOTE
    
    def test_from_string_invalid(self):
        """Test parsing invalid severity."""
        with pytest.raises(ValueError):
            Severity.from_string("INVALID")


# ============================================================================
# Diagnostic Tests
# ============================================================================


class TestDiagnostic:
    """Tests for Diagnostic."""
    
    def test_creation(self):
        """Test creating diagnostic."""
        diag = Diagnostic(
            severity=Severity.ERROR,
            message="Something went wrong",
        )
        
        assert diag.severity == Severity.ERROR
        assert diag.message == "Something went wrong"
    
    def test_add_label(self):
        """Test adding label."""
        source = SourceFile.from_string("hello")
        span = Span(
            source=source,
            start=Position(offset=0, line=1, column=1),
            end=Position(offset=5, line=1, column=6),
        )
        
        diag = Diagnostic(severity=Severity.ERROR, message="Error")
        diag.add_label(span, "here")
        
        assert len(diag.labels) == 1
    
    def test_add_note(self):
        """Test adding note."""
        diag = Diagnostic(severity=Severity.ERROR, message="Error")
        diag.add_note("This is a note")
        
        assert len(diag.notes) == 1
    
    def test_is_error(self):
        """Test error check."""
        diag = Diagnostic(severity=Severity.ERROR, message="Error")
        assert diag.is_error is True
        
        diag = Diagnostic(severity=Severity.WARNING, message="Warning")
        assert diag.is_error is False
    
    def test_str(self):
        """Test string representation."""
        diag = Diagnostic(severity=Severity.ERROR, message="Error")
        result = str(diag)
        
        assert "ERROR" in result
        assert "Error" in result


# ============================================================================
# Hint Tests
# ============================================================================


class TestHint:
    """Tests for Hint."""
    
    def test_creation(self):
        """Test creating hint."""
        hint = Hint(
            kind=HintKind.SUGGESTION,
            message="Use x instead",
        )
        
        assert hint.kind == HintKind.SUGGESTION
        assert "Use x instead" in str(hint)


# ============================================================================
# ErrorCode Tests
# ============================================================================


class TestErrorCode:
    """Tests for ErrorCode."""
    
    def test_str(self):
        """Test string representation."""
        code = ErrorCode.LEXER_INVALID_CHARACTER
        assert str(code) == "E1001"
    
    def test_from_value(self):
        """Test parsing from value."""
        code = ErrorCode.from_value("E1001")
        assert code == ErrorCode.LEXER_INVALID_CHARACTER
    
    def test_from_value_invalid(self):
        """Test parsing invalid value."""
        with pytest.raises(ValueError):
            ErrorCode.from_value("E9999")


# ============================================================================
# DiagnosticEngine Tests
# ============================================================================


class TestDiagnosticEngine:
    """Tests for DiagnosticEngine."""
    
    def test_creation(self):
        """Test creating engine."""
        engine = DiagnosticEngine()
        
        assert engine.error_count == 0
        assert engine.warning_count == 0
        assert not engine.has_errors
    
    def test_emit_error(self):
        """Test emitting error."""
        engine = DiagnosticEngine()
        engine.error("Something failed")
        
        assert engine.error_count == 1
        assert engine.has_errors
        assert len(engine.diagnostics) == 1
    
    def test_emit_warning(self):
        """Test emitting warning."""
        engine = DiagnosticEngine()
        engine.warning("Something might be wrong")
        
        assert engine.warning_count == 1
        assert not engine.has_errors
    
    def test_emit_note(self):
        """Test emitting note."""
        engine = DiagnosticEngine()
        engine.note("Additional info")
        
        assert len(engine.diagnostics) == 1
    
    def test_clear(self):
        """Test clearing diagnostics."""
        engine = DiagnosticEngine()
        engine.error("Error 1")
        engine.warning("Warning 1")
        
        engine.clear()
        
        assert engine.error_count == 0
        assert engine.warning_count == 0
        assert len(engine.diagnostics) == 0
    
    def test_get_errors(self):
        """Test getting errors."""
        engine = DiagnosticEngine()
        engine.error("Error 1")
        engine.warning("Warning 1")
        engine.error("Error 2")
        
        errors = engine.get_errors()
        assert len(errors) == 2
    
    def test_get_warnings(self):
        """Test getting warnings."""
        engine = DiagnosticEngine()
        engine.error("Error 1")
        engine.warning("Warning 1")
        engine.warning("Warning 2")
        
        warnings = engine.get_warnings()
        assert len(warnings) == 2
    
    def test_format_all(self):
        """Test formatting all diagnostics."""
        engine = DiagnosticEngine()
        engine.error("Error 1")
        engine.warning("Warning 1")
        
        output = engine.format_all()
        
        assert "Error 1" in output
        assert "Warning 1" in output
