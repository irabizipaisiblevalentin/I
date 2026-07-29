"""
Logging Framework

Provides structured logging for the I compiler.
"""

from .logger import Logger, get_logger
from .level import LogLevel
from .handler import LogHandler, ConsoleHandler, FileHandler
from .formatter import LogFormatter, PlainFormatter, ColoredFormatter
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
