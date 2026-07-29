"""
Log record.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .level import LogLevel


@dataclass
class LogRecord:
    """
    Single log record.

    Represents a single log event with all associated metadata.
    """

    level: LogLevel
    message: str
    logger_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    module: str | None = None
    function: str | None = None
    line: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation."""
        parts = [
            self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            self.level.name_short,
            f"[{self.logger_name}]",
            self.message,
        ]
        return " ".join(parts)
