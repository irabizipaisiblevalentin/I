"""mikorofone — Microphone / Audio recording for the I mobile platform.

Provides audio capture, streaming, and amplitude monitoring
with support for multiple audio formats.
"""

from __future__ import annotations

import enum
from typing import List, Optional


class AudioFormat(enum.Enum):
    """Supported audio encoding formats."""

    AAC = "aac"
    MP3 = "mp3"
    WAV = "wav"
    PCM = "pcm"


class Mikorofone:
    """Microphone / Audio recording manager.

    Handles audio capture from the device microphone, supports
    recording to file, real-time streaming, and amplitude monitoring
    across several encoding formats.
    """

    def __init__(self) -> None:
        self._recording: bool = False
        self._streaming: bool = False
        self._format: AudioFormat = AudioFormat.AAC
        self._permission: bool = False
        self._amplitude: float = 0.0

    # -- Properties -----------------------------------------------------------

    @property
    def is_recording(self) -> bool:
        """Whether audio is currently being recorded."""
        return self._recording

    @property
    def has_permission(self) -> bool:
        """Whether microphone permission has been granted."""
        return self._permission

    # -- Recording ------------------------------------------------------------

    def start_recording(
        self,
        file_path: Optional[str] = None,
        format: AudioFormat = AudioFormat.AAC,
    ) -> bool:
        """Start recording audio from the microphone.

        Args:
            file_path: Path to save the audio file. A default path is
                used if not provided.
            format: The audio encoding format.

        Returns:
            True if recording started successfully.
        """
        if not self._permission or self._recording:
            return False
        self._format = format
        self._recording = True
        return True

    def stop_recording(self) -> Optional[str]:
        """Stop the active audio recording.

        Returns:
            Path to the recorded audio file, or None if not recording.
        """
        if not self._recording:
            return None
        self._recording = False
        return "/path/to/recording." + self._format.value

    # -- Streaming ------------------------------------------------------------

    def start_streaming(self) -> bool:
        """Start streaming audio data in real time.

        Returns:
            True if streaming started successfully.
        """
        if not self._permission or self._streaming:
            return False
        self._streaming = True
        return True

    def stop_streaming(self) -> bool:
        """Stop the real-time audio stream.

        Returns:
            True if streaming was stopped.
        """
        if not self._streaming:
            return False
        self._streaming = False
        return True

    # -- Monitoring -----------------------------------------------------------

    def get_amplitude(self) -> float:
        """Get the current audio amplitude level.

        Returns:
            A float between 0.0 and 1.0 representing amplitude.
        """
        return self._amplitude

    def __repr__(self) -> str:
        return (
            f"Mikorofone(recording={self._recording}, "
            f"streaming={self._streaming}, permission={self._permission})"
        )
