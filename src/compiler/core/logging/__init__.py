"""
Logging Framework

Provides structured logging for the I compiler.
"""

from .formatter import ColoredFormatter, LogFormatter, PlainFormatter
from .handler import ConsoleHandler, FileHandler, LogHandler
from .level import LogLevel
from .logger import Logger, get_logger
from .record import LogRecord

__all__ = [
    "Logger",
    "get_logger",
    "LogLevel",
    "LogHandler",
    "ConsoleHandler",
    "FileHandler",
    "LogFormatter",
    "PlainFormatter",
    "ColoredFormatter",
    "LogRecord",
]
