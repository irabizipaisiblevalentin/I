"""image — Image utilities for the I language.

Provides basic image metadata and format detection.
Full image processing requires Pillow (optional).
"""

from __future__ import annotations

import struct
from typing import Optional, Tuple


class ImageInfo:
    """Image metadata."""
    __slots__ = ("width", "height", "format", "has_alpha")

    def __init__(self, width: int, height: int, fmt: str, alpha: bool = False) -> None:
        self.width = width
        self.height = height
        self.format = fmt
        self.has_alpha = alpha

    def __repr__(self) -> str:
        return f"ImageInfo({self.width}x{self.height}, {self.format})"


def detect_format(data: bytes) -> Optional[str]:
    """Detect image format from magic bytes."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if data[:2] == b"\xff\xd8":
        return "jpeg"
    if data[:4] == b"GIF8":
        return "gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    if data[:4] in (b"II\x2a\x00", b"MM\x00\x2a"):
        return "tiff"
    return None


def png_dimensions(data: bytes) -> Optional[Tuple[int, int]]:
    """Extract width/height from PNG data."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    if len(data) < 24:
        return None
    width = struct.unpack(">I", data[16:20])[0]
    height = struct.unpack(">I", data[20:24])[0]
    return (width, height)


def jpeg_dimensions(data: bytes) -> Optional[Tuple[int, int]]:
    """Extract width/height from JPEG data (basic SOF0 marker)."""
    if data[:2] != b"\xff\xd8":
        return None
    offset = 2
    while offset < len(data) - 1:
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            if offset + 9 < len(data):
                h = struct.unpack(">H", data[offset + 5:offset + 7])[0]
                w = struct.unpack(">H", data[offset + 7:offset + 9])[0]
                return (w, h)
            return None
        if marker == 0xD9:
            return None
        if 0xE0 <= marker <= 0xFE:
            length = struct.unpack(">H", data[offset + 2:offset + 4])[0]
            offset += 2 + length
        else:
            offset += 2
    return None


def image_info(data: bytes) -> Optional[ImageInfo]:
    """Get image info from raw bytes."""
    fmt = detect_format(data)
    if fmt is None:
        return None
    dims = None
    if fmt == "png":
        dims = png_dimensions(data)
    elif fmt == "jpeg":
        dims = jpeg_dimensions(data)
    if dims:
        return ImageInfo(dims[0], dims[1], fmt)
    return None
