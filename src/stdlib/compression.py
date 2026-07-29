"""compression — Data compression for the I language.

Provides zlib, gzip, and deflate compression/decompression.
"""

from __future__ import annotations

import gzip
import zlib
from typing import Optional


# ---------------------------------------------------------------------------
# Zlib
# ---------------------------------------------------------------------------

def compress(data: bytes, level: int = 6) -> bytes:
    """Compress data using zlib."""
    return zlib.compress(data, level)


def decompress(data: bytes, wbits: int = 15, bufsize: int = 16384) -> bytes:
    """Decompress zlib data."""
    return zlib.decompress(data, wbits, bufsize)


def decompress_to_size(data: bytes, size: int, wbits: int = 15) -> bytes:
    """Decompress with expected size."""
    return zlib.decompress(data, wbits, size)


# ---------------------------------------------------------------------------
# Gzip
# ---------------------------------------------------------------------------

def gzip_compress(data: bytes, compresslevel: int = 9) -> bytes:
    """Compress data using gzip."""
    return gzip.compress(data, compresslevel=compresslevel)


def gzip_decompress(data: bytes) -> bytes:
    """Decompress gzip data."""
    return gzip.decompress(data)


def compress_file(src: str, dst: str, compresslevel: int = 9) -> None:
    """Compress a file with gzip."""
    with open(src, "rb") as f_in:
        with gzip.open(dst, "wb", compresslevel=compresslevel) as f_out:
            f_out.write(f_in.read())


def decompress_file(src: str, dst: str) -> None:
    """Decompress a gzip file."""
    with gzip.open(src, "rb") as f_in:
        with open(dst, "wb") as f_out:
            f_out.write(f_in.read())


# ---------------------------------------------------------------------------
# CRC32
# ---------------------------------------------------------------------------

def crc32(data: bytes) -> int:
    """Compute CRC32 checksum."""
    return zlib.crc32(data) & 0xFFFFFFFF


# ---------------------------------------------------------------------------
# Adler32
# ---------------------------------------------------------------------------

def adler32(data: bytes) -> int:
    """Compute Adler32 checksum."""
    return zlib.adler32(data) & 0xFFFFFFFF
