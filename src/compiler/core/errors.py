"""
Unified Exception Hierarchy

Provides a consistent exception hierarchy for the I compiler.
All compiler-specific exceptions inherit from a common base.
"""

from __future__ import annotations

from typing import Any


class IError(Exception):
    """
    Base exception for all I compiler errors.

    All exceptions raised within the compiler should inherit from this class.
    """

    def __init__(
        self,
        message: str,
        code: str = "I000",
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize error.

        Args:
            message: Human-readable error message
            code: Error code string
            details: Optional structured error details
        """
        super().__init__(message)
        self.code = code
        self.details = details or {}


class CompilerError(IError):
    """
    Base compiler error.

    Raised when compilation fails at any stage.
    """

    def __init__(
        self,
        message: str,
        code: str = "C000",
        stage: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize compiler error.

        Args:
            message: Error message
            code: Error code
            stage: Compiler stage where error occurred
            details: Optional structured details
        """
        super().__init__(message, code, details)
        self.stage = stage


class ConfigError(IError):
    """
    Configuration error.

    Raised when compiler configuration is invalid or missing.
    """

    def __init__(
        self,
        message: str,
        path: str | None = None,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize config error.

        Args:
            message: Error message
            path: Path to config file
            field: Specific config field with error
            details: Optional structured details
        """
        super().__init__(message, "C001", details)
        self.path = path
        self.field = field


class FileIOError(IError):
    """
    File input/output error.

    Raised when file operations fail.
    """

    def __init__(
        self,
        message: str,
        path: str | None = None,
        operation: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize file IO error.

        Args:
            message: Error message
            path: File path
            operation: Operation being performed
            details: Optional structured details
        """
        super().__init__(message, "I001", details)
        self.path = path
        self.operation = operation


class InternalError(IError):
    """
    Internal compiler error.

    Raised when the compiler encounters an unexpected internal state.
    This indicates a bug in the compiler itself.
    """

    def __init__(
        self,
        message: str,
        component: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize internal error.

        Args:
            message: Error message
            component: Compiler component
            details: Optional structured details
        """
        super().__init__(message, "I999", details)
        self.component = component


class ValidationError(IError):
    """
    Validation error.

    Raised when input validation fails.
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize validation error.

        Args:
            message: Error message
            field: Field being validated
            value: Invalid value
            details: Optional structured details
        """
        super().__init__(message, "V000", details)
        self.field = field
        self.value = value


class PanicError(IError):
    """
    Fatal compiler error.

    Raised when the compiler cannot continue execution safely.
    Represents an unrecoverable error.
    """

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize panic.

        Args:
            message: Error message
            context: Optional context information
        """
        super().__init__(message, "P000", context)


__all__ = [
    "IError",
    "CompilerError",
    "ConfigError",
    "FileIOError",
    "InternalError",
    "ValidationError",
    "PanicError",
]
