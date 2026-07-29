"""system — System information and interaction for the I language.

Provides OS info, platform detection, resource limits, and system commands.
"""

from __future__ import annotations

import os
import platform
import sys
from typing import Any, Dict, List, Optional


def os_name() -> str:
    """Operating system name ('Windows', 'Linux', 'Darwin')."""
    return platform.system()


def os_version() -> str:
    return platform.version()


def platform_name() -> str:
    """Full platform identifier."""
    return platform.platform()


def arch() -> str:
    """CPU architecture ('AMD64', 'ARM64', etc.)."""
    return platform.machine()


def python_version() -> str:
    return platform.python_version()


def hostname() -> str:
    return platform.node()


def cpu_count() -> Optional[int]:
    """Number of CPUs (or None if undetermined)."""
    return os.cpu_count()


def env(key: str, default: str = "") -> str:
    """Get environment variable."""
    return os.environ.get(key, default)


def set_env(key: str, value: str) -> None:
    os.environ[key] = value


def env_vars() -> Dict[str, str]:
    return dict(os.environ)


def exit(code: int = 0) -> None:
    sys.exit(code)


def get_argv() -> List[str]:
    return sys.argv


def get_stdin() -> Any:
    return sys.stdin


def get_stdout() -> Any:
    return sys.stdout


def get_stderr() -> Any:
    return stderr if 'stderr' in dir() else sys.stderr


def pid() -> int:
    return os.getpid()


def ppid() -> int:
    return os.getppid()
