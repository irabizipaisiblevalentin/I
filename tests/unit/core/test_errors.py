"""
Tests for the unified exception hierarchy.
"""

import pytest

from src.compiler.core.errors import (
    IError,
    CompilerError,
    ConfigError,
    FileIOError,
    InternalError,
    ValidationError,
    Panic,
)


class TestIError:
    """Tests for base IError."""

    def test_creation(self):
        error = IError("test message")
        assert str(error) == "test message"
        assert error.code == "I000"
        assert error.details == {}

    def test_with_details(self):
        error = IError("test", details={"key": "value"})
        assert error.details == {"key": "value"}

    def test_custom_code(self):
        error = IError("test", code="X001")
        assert error.code == "X001"


class TestCompilerError:
    """Tests for CompilerError."""

    def test_default_code(self):
        error = CompilerError("compilation failed")
        assert error.code == "C000"
        assert error.stage is None

    def test_with_stage(self):
        error = CompilerError("parse error", stage="parsing")
        assert error.stage == "parsing"


class TestConfigError:
    """Tests for ConfigError."""

    def test_creation(self):
        error = ConfigError("invalid config", path="config.toml", field="optimization")
        assert error.code == "C001"
        assert error.path == "config.toml"
        assert error.field == "optimization"


class TestFileIOError:
    """Tests for FileIOError."""

    def test_creation(self):
        error = FileIOError("file not found", path="/test/file.il", operation="read")
        assert error.code == "I001"
        assert error.path == "/test/file.il"
        assert error.operation == "read"


class TestInternalError:
    """Tests for InternalError."""

    def test_creation(self):
        error = InternalError("unexpected state", component="optimizer")
        assert error.code == "I999"
        assert error.component == "optimizer"


class TestValidationError:
    """Tests for ValidationError."""

    def test_creation(self):
        error = ValidationError("invalid value", field="count", value=-1)
        assert error.code == "V000"
        assert error.field == "count"
        assert error.value == -1


class TestPanic:
    """Tests for Panic."""

    def test_creation(self):
        error = Panic("fatal error", context={"phase": "codegen"})
        assert error.code == "P000"
        assert error.details == {"phase": "codegen"}


class TestInheritance:
    """Tests for exception hierarchy."""

    def test_all_are_ierror(self):
        assert isinstance(CompilerError("x"), IError)
        assert isinstance(ConfigError("x"), IError)
        assert isinstance(FileIOError("x"), IError)
        assert isinstance(InternalError("x"), IError)
        assert isinstance(ValidationError("x"), IError)
        assert isinstance(Panic("x"), IError)

    def test_compilererror_is_exception(self):
        assert issubclass(CompilerError, Exception)
        assert issubclass(IError, Exception)
