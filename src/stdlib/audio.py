"""audio — Audio utilities for the I language.

Provides audio format detection and metadata extraction.
"""

from __future__ import annotations

import struct
from typing import Optional


class AudioInfo:
    """Audio metadata."""
    __slots__ = ("format", "duration_seconds", "sample_rate", "channels", "bitrate")

    def __init__(self, fmt: str = "", duration: float = 0.0,
                 sample_rate: int = 0, channels: int = 0, bitrate: int = 0) -> None:
        self.format = fmt
        self.duration_seconds = duration
        self.sample_rate = sample_rate
        self.channels = channels
        self.bitrate = bitrate

    def __repr__(self) -> str:
        return f"AudioInfo({self.format}, {self.duration_seconds:.1f}s)"


def detect_format(data: bytes) -> Optional[str]:
    """Detect audio format from magic bytes."""
    if data[:4] == b"fLaC":
        return "flac"
    if data[:4] == b"ID3" or data[:3] == b"\xff\xfb\xff":
        return "mp3"
    if data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        return "wav"
    if data[:4] == b"OggS":
        return "ogg"
    return None


def wav_info(data: bytes) -> Optional[AudioInfo]:
    """Extract info from WAV data."""
    if data[:4] != b"RIFF" or data[8:12] != b"WAVE":
        return None
    if len(data) < 44:
        return None
    channels = struct.unpack("<H", data[22:24])[0]
    sample_rate = struct.unpack("<I", data[24:28])[0]
    byte_rate = struct.unpack("<I", data[28:32])[0]
    bits = struct.unpack("<H", data[34:36])[0]
    bitrate = byte_rate * 8
    data_size = struct.unpack("<I", data[40:44])[0]
    duration = data_size / byte_rate if byte_rate > 0 else 0
    return AudioInfo("wav", duration, sample_rate, channels, bitrate)


def audio_info(data: bytes) -> Optional[AudioInfo]:
    """Get audio info from raw bytes."""
    fmt = detect_format(data)
    if fmt is None:
        return None
    if fmt == "wav":
        return wav_info(data)
    return AudioInfo(fmt)
