"""
Log handlers.
"""

from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from .formatter import LogFormatter, PlainFormatter
from .level import LogLevel
from .record import LogRecord


class LogHandler(ABC):
    """Base log handler."""
    
    def __init__(self, formatter: Optional[LogFormatter] = None) -> None:
        """
        Initialize handler.
        
        Args:
            formatter: Log formatter
        """
        self._formatter = formatter or PlainFormatter()
        self._level = LogLevel.INFO
    
    @property
    def level(self) -> LogLevel:
        """Minimum log level."""
        return self._level
    
    @level.setter
    def level(self, level: LogLevel) -> None:
        """Set minimum log level."""
        self._level = level
    
    def set_level(self, level: LogLevel) -> None:
        """Set minimum log level."""
        self._level = level
    
    def is_enabled(self, level: LogLevel) -> bool:
        """
        Check if level is enabled.
        
        Args:
            level: Log level to check
            
        Returns:
            True if level is enabled
        """
        return level >= self._level
    
    def emit(self, record: LogRecord) -> None:
        """
        Emit a log record.
        
        Args:
            record: Log record to emit
        """
        if self.is_enabled(record.level):
            self._emit(record)
    
    @abstractmethod
    def _emit(self, record: LogRecord) -> None:
        """
        Emit a log record (implementation).
        
        Args:
            record: Log record to emit
        """
        ...
    
    def flush(self) -> None:
        """Flush handler."""
        pass
    
    def close(self) -> None:
        """Close handler."""
        pass


class ConsoleHandler(LogHandler):
    """Console log handler."""
    
    def __init__(
        self,
        stream=None,
        formatter: Optional[LogFormatter] = None,
    ) -> None:
        """
        Initialize console handler.
        
        Args:
            stream: Output stream (default: stderr)
            formatter: Log formatter
        """
        super().__init__(formatter)
        self._stream = stream or sys.stderr
    
    def _emit(self, record: LogRecord) -> None:
        """Write record to console."""
        message = self._formatter.format(record)
        self._stream.write(message + "\n")
        self._stream.flush()
    
    def flush(self) -> None:
        """Flush stream."""
        self._stream.flush()


class FileHandler(LogHandler):
    """File log handler."""
    
    def __init__(
        self,
        path: Path,
        formatter: Optional[LogFormatter] = None,
        encoding: str = "utf-8",
    ) -> None:
        """
        Initialize file handler.
        
        Args:
            path: Log file path
            formatter: Log formatter
            encoding: File encoding
        """
        super().__init__(formatter)
        self._path = path
        self._encoding = encoding
        self._file = None
    
    def _ensure_file(self) -> None:
        """Ensure file is open."""
        if self._file is None:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._file = open(self._path, "a", encoding=self._encoding)
    
    def _emit(self, record: LogRecord) -> None:
        """Write record to file."""
        self._ensure_file()
        message = self._formatter.format(record)
        self._file.write(message + "\n")
    
    def flush(self) -> None:
        """Flush file."""
        if self._file:
            self._file.flush()
    
    def close(self) -> None:
        """Close file."""
        if self._file:
            self._file.close()
            self._file = None
