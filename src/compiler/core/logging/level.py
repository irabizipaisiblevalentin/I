"""
Log levels.
"""

from __future__ import annotations

from enum import IntEnum


class LogLevel(IntEnum):
    """Log severity levels."""

    TRACE = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    @classmethod
    def from_string(cls, name: str) -> LogLevel:
        """
        Parse log level from string.

        Args:
            name: Level name (case-insensitive)

        Returns:
            LogLevel instance
        """
        mapping = {
            "TRACE": cls.TRACE,
            "DEBUG": cls.DEBUG,
            "INFO": cls.INFO,
            "WARN": cls.WARNING,
            "WARNING": cls.WARNING,
            "ERROR": cls.ERROR,
            "CRIT": cls.CRITICAL,
            "CRITICAL": cls.CRITICAL,
        }

        upper = name.upper()
        if upper not in mapping:
            raise ValueError(f"Unknown log level: {name}")

        return mapping[upper]

    @property
    def name_short(self) -> str:
        """Short level name."""
        return self.name[:4]
