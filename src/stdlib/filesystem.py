"""filesystem — Filesystem operations for the I language.

Higher-level filesystem operations: copy trees, disk usage,
file watching, and temporary files.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------

def copy(src: str, dst: str) -> None:
    """Copy file (preserves metadata)."""
    shutil.copy2(src, dst)


def copy_tree(src: str, dst: str) -> None:
    """Recursively copy directory tree."""
    shutil.copytree(src, dst, dirs_exist_ok=True)


def move(src: str, dst: str) -> None:
    """Move/rename file or directory."""
    shutil.move(src, dst)


def delete(path: str) -> None:
    """Delete file."""
    os.remove(path)


def delete_tree(path: str) -> None:
    """Recursively delete directory tree."""
    shutil.rmtree(path)


def make_dir(path: str) -> None:
    """Create directory (including parents)."""
    os.makedirs(path, exist_ok=True)


def make_temp_dir(prefix: str = "") -> str:
    """Create and return a temporary directory path."""
    return tempfile.mkdtemp(prefix=prefix)


def make_temp_file(suffix: str = "", prefix: str = "tmp") -> str:
    """Create and return a temporary file path."""
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    os.close(fd)
    return path


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def exists(path: str) -> bool:
    return os.path.exists(path)


def is_file(path: str) -> bool:
    return os.path.isfile(path)


def is_dir(path: str) -> bool:
    return os.path.isdir(path)


def is_link(path: str) -> bool:
    return os.path.islink(path)


def file_size(path: str) -> int:
    """File size in bytes."""
    return os.path.getsize(path)


def file_mtime(path: str) -> float:
    """Last modification time (Unix timestamp)."""
    return os.path.getmtime(path)


def file_stat(path: str):
    """Os.stat_result for path."""
    return os.stat(path)


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------

def list_dir(path: str = ".") -> List[str]:
    return os.listdir(path)


def list_files(path: str = ".") -> List[str]:
    """List only files (not directories)."""
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]


def list_dirs(path: str = ".") -> List[str]:
    """List only directories."""
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]


def glob(path: str, pattern: str) -> List[str]:
    """Glob pattern matching."""
    import glob as _glob
    return _glob.glob(os.path.join(path, pattern))


def walk_files(path: str) -> List[str]:
    """Recursively list all files."""
    result: List[str] = []
    for root, dirs, files in os.walk(path):
        for f in files:
            result.append(os.path.join(root, f))
    return result


# ---------------------------------------------------------------------------
# Disk usage
# ---------------------------------------------------------------------------

def disk_usage(path: str) -> Tuple[int, int, int]:
    """Return (total, used, free) in bytes."""
    usage = shutil.disk_usage(path)
    return (usage.total, usage.used, usage.free)


def dir_size(path: str) -> int:
    """Total size of directory in bytes."""
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    return total


# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------

def chmod(path: str, mode: int) -> None:
    os.chmod(path, mode)


def readable(path: str) -> bool:
    return os.access(path, os.R_OK)


def writable(path: str) -> bool:
    return os.access(path, os.W_OK)


def executable(path: str) -> bool:
    return os.access(path, os.X_OK)


# ---------------------------------------------------------------------------
# Symlinks
# ---------------------------------------------------------------------------

def symlink(src: str, dst: str) -> None:
    """Create symbolic link."""
    os.symlink(src, dst)


def readlink(path: str) -> str:
    """Read symbolic link target."""
    return os.readlink(path)
