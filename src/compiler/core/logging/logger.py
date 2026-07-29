"""
Logger implementation.
"""

from __future__ import annotations

import inspect

from .formatter import ColoredFormatter
from .handler import ConsoleHandler, LogHandler
from .level import LogLevel
from .record import LogRecord

# Global logger registry
_loggers: dict[str, Logger] = {}


class Logger:
    """
    Main logger class.

    Provides structured logging for the I compiler.
    """

    def __init__(
        self,
        name: str,
        level: LogLevel = LogLevel.INFO,
        handlers: list[LogHandler] | None = None,
    ) -> None:
        """
        Initialize logger.

        Args:
            name: Logger name
            level: Minimum log level
            handlers: Log handlers
        """
        self._name = name
        self._level = level
        self._handlers: list[LogHandler] = handlers or []
        self._parent: Logger | None = None

        # Add default console handler if no handlers provided
        if not self._handlers:
            handler = ConsoleHandler(formatter=ColoredFormatter())
            handler.set_level(level)
            self._handlers.append(handler)

    @property
    def name(self) -> str:
        """Logger name."""
        return self._name

    @property
    def level(self) -> LogLevel:
        """Minimum log level."""
        return self._level

    def set_level(self, level: LogLevel) -> None:
        """Set minimum log level."""
        self._level = level
        for handler in self._handlers:
            handler.set_level(level)

    def add_handler(self, handler: LogHandler) -> None:
        """Add log handler."""
        self._handlers.append(handler)

    def remove_handler(self, handler: LogHandler) -> None:
        """Remove log handler."""
        self._handlers.remove(handler)

    def trace(self, message: str, **extra) -> None:
        """Log trace message."""
        self._log(LogLevel.TRACE, message, extra)

    def debug(self, message: str, **extra) -> None:
        """Log debug message."""
        self._log(LogLevel.DEBUG, message, extra)

    def info(self, message: str, **extra) -> None:
        """Log info message."""
        self._log(LogLevel.INFO, message, extra)

    def warning(self, message: str, **extra) -> None:
        """Log warning message."""
        self._log(LogLevel.WARNING, message, extra)

    def error(self, message: str, **extra) -> None:
        """Log error message."""
        self._log(LogLevel.ERROR, message, extra)

    def critical(self, message: str, **extra) -> None:
        """Log critical message."""
        self._log(LogLevel.CRITICAL, message, extra)

    def _log(self, level: LogLevel, message: str, extra: dict) -> None:
        """Log a message."""
        if level < self._level:
            return

        # Get caller info
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_back:
            caller = frame.f_back.f_back
            module = caller.f_globals.get("__name__")
            function = caller.f_code.co_name
            line = caller.f_lineno
        else:
            module = None
            function = None
            line = None

        record = LogRecord(
            level=level,
            message=message,
            logger_name=self._name,
            module=module,
            function=function,
            line=line,
            extra=extra,
        )

        # Emit to handlers
        for handler in self._handlers:
            handler.emit(record)

    def flush(self) -> None:
        """Flush all handlers."""
        for handler in self._handlers:
            handler.flush()

    def child(self, name: str) -> Logger:
        """
        Create child logger.

        Args:
            name: Child logger name

        Returns:
            Child logger
        """
        child_name = f"{self._name}.{name}"
        child = Logger(child_name, self._level, self._handlers.copy())
        child._parent = self
        return child


def get_logger(name: str = "ilang", level: LogLevel = LogLevel.INFO) -> Logger:
    """
    Get or create logger.

    Args:
        name: Logger name
        level: Minimum log level

    Returns:
        Logger instance
    """
    if name not in _loggers:
        _loggers[name] = Logger(name, level)

    return _loggers[name]
