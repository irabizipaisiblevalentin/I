"""ububiko — Database / Storage modules for the I mobile platform.

Provides local database management with offline-first sync,
migration, and cloud synchronization support.
"""

from __future__ import annotations

from mobile.ububiko.ububiko import (
    ConflictStrategy,
    DatabaseConfig,
    Ububiko,
)

__all__ = [
    "ConflictStrategy",
    "DatabaseConfig",
    "Ububiko",
]
