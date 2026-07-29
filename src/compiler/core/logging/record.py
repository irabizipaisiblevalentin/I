"""
Log record.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

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
    module: Optional[str] = None
    function: Optional[str] = None
    line: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """String representation."""
        parts = [
            self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            self.level.name_short,
            f"[{self.logger_name}]",
            self.message,
        ]
        return " ".join(parts)
