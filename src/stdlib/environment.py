"""environment — Environment and configuration for the I language.

Provides environment variable management, path resolution, and
platform-specific configuration.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional


def get(key: str, default: str = "") -> str:
    """Get environment variable."""
    return os.environ.get(key, default)


def set_var(key: str, value: str) -> None:
    """Set environment variable."""
    os.environ[key] = value


def unset(key: str) -> bool:
    """Remove environment variable. Returns True if it existed."""
    if key in os.environ:
        del os.environ[key]
        return True
    return False


def has(key: str) -> bool:
    return key in os.environ


def all_vars() -> Dict[str, str]:
    return dict(os.environ)


def keys() -> List[str]:
    return list(os.environ.keys())


def values() -> List[str]:
    return list(os.environ.values())


def items() -> List[tuple]:
    return list(os.environ.items())


def home_dir() -> str:
    return os.path.expanduser("~")


def temp_dir() -> str:
    import tempfile
    return tempfile.gettempdir()


def working_dir() -> str:
    return os.getcwd()


def path_list() -> List[str]:
    """PATH as a list."""
    return os.environ.get("PATH", "").split(os.pathsep)


def is_windows() -> bool:
    return sys.platform == "win32"


def is_linux() -> bool:
    return sys.platform == "linux"


def is_macos() -> bool:
    return sys.platform == "darwin"


def ensure(key: str) -> str:
    """Get env var or raise if missing."""
    val = os.environ.get(key)
    if val is None:
        raise EnvironmentError(f"environment variable not set: {key}")
    return val
