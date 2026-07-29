"""io — Input/output operations for the I language.

Provides file reading/writing, streams, buffered I/O, and
text/binary mode operations.
"""

from __future__ import annotations

import io as _io
import os
from typing import BinaryIO, List, Optional, TextIO, Union


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------

def read_file(path: str, encoding: str = "utf-8") -> str:
    """Read entire file as string."""
    with open(path, "r", encoding=encoding) as f:
        return f.read()


def read_bytes(path: str) -> bytes:
    """Read entire file as bytes."""
    with open(path, "rb") as f:
        return f.read()


def write_file(path: str, content: str, encoding: str = "utf-8") -> int:
    """Write string to file. Returns bytes written."""
    with open(path, "w", encoding=encoding) as f:
        return f.write(content)


def write_bytes(path: str, data: bytes) -> int:
    """Write bytes to file. Returns bytes written."""
    with open(path, "wb") as f:
        return f.write(data)


def append_file(path: str, content: str, encoding: str = "utf-8") -> int:
    """Append string to file."""
    with open(path, "a", encoding=encoding) as f:
        return f.write(content)


def read_lines(path: str, encoding: str = "utf-8") -> List[str]:
    """Read file as list of lines (stripped)."""
    with open(path, "r", encoding=encoding) as f:
        return [line.rstrip("\n\r") for line in f]


def write_lines(path: str, lines: List[str], encoding: str = "utf-8") -> None:
    """Write list of lines to file."""
    with open(path, "w", encoding=encoding) as f:
        for line in lines:
            f.write(line + "\n")


def exists(path: str) -> bool:
    """Check if file or directory exists."""
    return os.path.exists(path)


def is_file(path: str) -> bool:
    """Check if path is a file."""
    return os.path.isfile(path)


def is_dir(path: str) -> bool:
    """Check if path is a directory."""
    return os.path.isdir(path)


def size(path: str) -> int:
    """File size in bytes."""
    return os.path.getsize(path)


def remove(path: str) -> None:
    """Remove a file."""
    os.remove(path)


def rename(old: str, new: str) -> None:
    """Rename/move a file."""
    os.rename(old, new)


def copy_file(src: str, dst: str) -> None:
    """Copy a file."""
    import shutil
    shutil.copy2(src, dst)


def mkdir(path: str, parents: bool = True) -> None:
    """Create directory."""
    os.makedirs(path, exist_ok=parents)


def list_dir(path: str = ".") -> List[str]:
    """List directory contents."""
    return os.listdir(path)


def temp_dir() -> str:
    """Create and return a temporary directory path."""
    import tempfile
    return tempfile.mkdtemp()


def temp_file(suffix: str = "", prefix: str = "tmp") -> str:
    """Create and return a temporary file path."""
    import tempfile
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    os.close(fd)
    return path


# ---------------------------------------------------------------------------
# Streams
# ---------------------------------------------------------------------------

class MemoryStream:
    """In-memory byte stream."""

    def __init__(self, initial: bytes = b"") -> None:
        self._buffer = _io.BytesIO(initial)

    def read(self, n: int = -1) -> bytes:
        return self._buffer.read(n)

    def write(self, data: bytes) -> int:
        return self._buffer.write(data)

    def seek(self, offset: int, whence: int = 0) -> int:
        return self._buffer.seek(offset, whence)

    def tell(self) -> int:
        return self._buffer.tell()

    def getvalue(self) -> bytes:
        return self._buffer.getvalue()

    def close(self) -> None:
        self._buffer.close()


class StringStream:
    """In-memory text stream."""

    def __init__(self, initial: str = "") -> None:
        self._buffer = _io.StringIO(initial)

    def read(self, n: int = -1) -> str:
        return self._buffer.read(n)

    def write(self, s: str) -> int:
        return self._buffer.write(s)

    def seek(self, offset: int, whence: int = 0) -> int:
        return self._buffer.seek(offset, whence)

    def tell(self) -> int:
        return self._buffer.tell()

    def getvalue(self) -> str:
        return self._buffer.getvalue()

    def close(self) -> None:
        self._buffer.close()


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def copy_stream(src: Union[BinaryIO, TextIO], dst: Union[BinaryIO, TextIO], buf_size: int = 8192) -> int:
    """Copy between streams. Returns bytes/chars copied."""
    total = 0
    while True:
        chunk = src.read(buf_size)
        if not chunk:
            break
        dst.write(chunk)
        total += len(chunk)
    return total
