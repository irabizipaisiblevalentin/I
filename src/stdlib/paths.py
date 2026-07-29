"""paths — Path manipulation for the I language.

Cross-platform path operations (works on Windows, macOS, Linux).
"""

from __future__ import annotations

import os
import posixpath
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def join(*parts: str) -> str:
    """Join path components."""
    return os.path.join(*parts)


def stem(path: str) -> str:
    """Filename without extension."""
    return os.path.splitext(os.path.basename(path))[0]


def ext(path: str) -> str:
    """File extension (including dot)."""
    return os.path.splitext(path)[1]


def basename(path: str) -> str:
    """Final component of path."""
    return os.path.basename(path)


def dirname(path: str) -> str:
    """Directory containing the path."""
    return os.path.dirname(path)


def parent(path: str) -> str:
    """Parent directory."""
    return os.path.dirname(path)


def filename(path: str) -> str:
    """Same as basename — final component."""
    return os.path.basename(path)


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def normalize(path: str) -> str:
    """Normalize path (resolve . and ..)."""
    return os.path.normpath(path)


def absolute(path: str) -> str:
    """Convert to absolute path."""
    return os.path.abspath(path)


def real(path: str) -> str:
    """Resolve symlinks and return real path."""
    return os.path.realpath(path)


def rel(path: str, start: str = ".") -> str:
    """Compute relative path from start."""
    return os.path.relpath(path, start)


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------

def is_absolute(path: str) -> bool:
    return os.path.isabs(path)


def is_relative(path: str) -> bool:
    return not os.path.isabs(path)


def exists(path: str) -> bool:
    return os.path.exists(path)


def is_file(path: str) -> bool:
    return os.path.isfile(path)


def is_dir(path: str) -> bool:
    return os.path.isdir(path)


def is_link(path: str) -> bool:
    return os.path.islink(path)


def same(a: str, b: str) -> bool:
    """Check if paths refer to the same file."""
    return os.path.samefile(a, b)


def readable(path: str) -> bool:
    return os.access(path, os.R_OK)


def writable(path: str) -> bool:
    return os.access(path, os.W_OK)


# ---------------------------------------------------------------------------
# Splitting
# ---------------------------------------------------------------------------

def split(path: str) -> Tuple[str, str]:
    """Split into (directory, filename)."""
    return os.path.split(path)


def split_ext(path: str) -> Tuple[str, str]:
    """Split into (root, extension)."""
    return os.path.splitext(path)


def parts(path: str) -> List[str]:
    """Split path into all components."""
    result: List[str] = []
    head = path
    while True:
        head, tail = os.path.split(head)
        if tail:
            result.append(tail)
        elif head:
            result.append(head)
            break
        else:
            break
    result.reverse()
    return result


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------

def to_posix(path: str) -> str:
    """Convert to POSIX-style path (forward slashes)."""
    return path.replace("\\", "/")


def to_windows(path: str) -> str:
    """Convert to Windows-style path (backslashes)."""
    return path.replace("/", "\\")


# ---------------------------------------------------------------------------
# Directory operations
# ---------------------------------------------------------------------------

def list_dir(path: str = ".") -> List[str]:
    return os.listdir(path)


def make_dirs(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def remove_file(path: str) -> None:
    os.remove(path)


def remove_dir(path: str) -> None:
    os.rmdir(path)


def walk(path: str):
    """Walk directory tree (yielding root, dirs, files)."""
    return os.walk(path)


# ---------------------------------------------------------------------------
# Home and temp
# ---------------------------------------------------------------------------

def home() -> str:
    """User home directory."""
    return os.path.expanduser("~")


def cwd() -> str:
    """Current working directory."""
    return os.getcwd()


def temp() -> str:
    """System temp directory."""
    import tempfile
    return tempfile.gettempdir()
