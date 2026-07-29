"""
Log formatters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .level import LogLevel
from .record import LogRecord


class LogFormatter(ABC):
    """Base log formatter."""

    @abstractmethod
    def format(self, record: LogRecord) -> str:
        """
        Format log record.

        Args:
            record: Log record to format

        Returns:
            Formatted string
        """
        ...


class PlainFormatter(LogFormatter):
    """Plain text formatter."""

    def __init__(self, fmt: str = "%(timestamp)s %(level)s [%(name)s] %(message)s") -> None:
        """
        Initialize formatter.

        Args:
            fmt: Format string
        """
        self._fmt = fmt

    def format(self, record: LogRecord) -> str:
        """Format log record."""
        return self._fmt % {
            "timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "level": record.level.name_short,
            "name": record.logger_name,
            "message": record.message,
            "module": record.module or "",
            "function": record.function or "",
            "line": record.line or 0,
        }


class ColoredFormatter(LogFormatter):
    """Colored terminal formatter."""

    # ANSI color codes
    COLORS = {
        LogLevel.TRACE: "\033[37m",      # White
        LogLevel.DEBUG: "\033[36m",      # Cyan
        LogLevel.INFO: "\033[32m",       # Green
        LogLevel.WARNING: "\033[33m",    # Yellow
        LogLevel.ERROR: "\033[31m",      # Red
        LogLevel.CRITICAL: "\033[35m",   # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.level, "")

        return (
            f"{color}"
            f"{record.timestamp.strftime('%H:%M:%S')} "
            f"{record.level.name_short:5s} "
            f"[{record.logger_name}] "
            f"{record.message}"
            f"{self.RESET}"
        )


class JsonFormatter(LogFormatter):
    """JSON formatter."""

    def format(self, record: LogRecord) -> str:
        """Format log record as JSON."""
        import json

        data = {
            "timestamp": record.timestamp.isoformat(),
            "level": record.level.name,
            "logger": record.logger_name,
            "message": record.message,
        }

        if record.module:
            data["module"] = record.module
        if record.function:
            data["function"] = record.function
        if record.line:
            data["line"] = record.line
        if record.extra:
            data["extra"] = record.extra

        return json.dumps(data)
