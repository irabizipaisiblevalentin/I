"""video — Video utilities for the I language.

Provides video format detection and basic metadata.
"""

from __future__ import annotations

import struct
from typing import Optional


class VideoInfo:
    """Video metadata."""
    __slots__ = ("format", "duration_seconds", "width", "height")

    def __init__(self, fmt: str = "", duration: float = 0.0,
                 width: int = 0, height: int = 0) -> None:
        self.format = fmt
        self.duration_seconds = duration
        self.width = width
        self.height = height

    def __repr__(self) -> str:
        return f"VideoInfo({self.format}, {self.width}x{self.height})"


def detect_format(data: bytes) -> Optional[str]:
    """Detect video format from magic bytes."""
    if data[4:8] == b"ftyp":
        brand = data[8:12].decode("ascii", errors="ignore")
        if brand in ("mp41", "mp42", "isom", "avc1", "iso5"):
            return "mp4"
        if brand in ("qt  ", "mqt "):
            return "quicktime"
    if data[:3] == b"\x1a\x45\xdf\xa3":
        return "webm"
    if data[:4] == b"\x00\x00\x00\x1c" or data[:4] == b"\x00\x00\x00\x18":
        return "mp4"
    if data[:4] == b"RIFF" and data[8:12] == b"AVI ":
        return "avi"
    if data[:4] == b"\x30\x26\xb2\x75":
        return "asf"
    return None


def video_info(data: bytes) -> Optional[VideoInfo]:
    """Get video info from raw bytes."""
    fmt = detect_format(data)
    if fmt is None:
        return None
    return VideoInfo(fmt)
