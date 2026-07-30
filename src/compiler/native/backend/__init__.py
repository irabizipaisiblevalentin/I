"""
Native compiler backends.

This package defines the abstract backend interface and provides
a registry and manager for discovering and using backends at runtime.
"""

from __future__ import annotations

from compiler.native.backend.base import (
    Backend,
    BackendCapabilities,
    BackendError,
    BackendFeature,
    BackendKind,
)
from compiler.native.backend.manager import BackendManager
from compiler.native.backend.registry import BackendRegistry

__all__ = [
    "Backend",
    "BackendCapabilities",
    "BackendError",
    "BackendFeature",
    "BackendKind",
    "BackendManager",
    "BackendRegistry",
]
