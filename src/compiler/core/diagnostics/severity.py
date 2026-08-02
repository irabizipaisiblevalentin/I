"""
Diagnostic severity levels.
"""

from __future__ import annotations

from enum import IntEnum


class Severity(IntEnum):
    """Diagnostic severity levels."""

    DEBUG = 0
    NOTE = 10
    HELP = 20
    WARNING = 30
    ERROR = 40
    BUG = 50

    @classmethod
    def from_string(cls, name: str) -> Severity:
        """Parse severity from string."""
        mapping = {
            "DEBUG": cls.DEBUG,
            "NOTE": cls.NOTE,
            "HELP": cls.HELP,
            "WARN": cls.WARNING,
            "WARNING": cls.WARNING,
            "ERROR": cls.ERROR,
            "BUG": cls.BUG,
        }

        upper = name.upper()
        if upper not in mapping:
            raise ValueError(f"Unknown severity: {name}")

        return mapping[upper]
