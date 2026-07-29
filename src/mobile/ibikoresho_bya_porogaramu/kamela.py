"""kamela — Camera management for the I mobile platform.

Provides camera capture, preview, recording, and configuration
for both front and back cameras.
"""

from __future__ import annotations

import enum
from typing import Any, Optional, Tuple


class CameraPosition(enum.Enum):
    """Physical location of the camera on the device."""

    INYUMA = "back"
    IMERE = "front"


class CameraFlash(enum.Enum):
    """Flash mode for camera capture."""

    AUTO = "auto"
    ON = "on"
    OFF = "off"


class CameraConfig:
    """Configuration parameters for the camera sensor.

    Attributes:
        position: Which camera to use (back or front).
        flash: Flash mode during capture.
        resolution: Capture resolution as (width, height) in pixels.
        aspect_ratio: Aspect ratio string (e.g. "16:9", "4:3").
    """

    def __init__(
        self,
        position: CameraPosition = CameraPosition.INYUMA,
        flash: CameraFlash = CameraFlash.AUTO,
        resolution: Optional[Tuple[int, int]] = None,
        aspect_ratio: str = "16:9",
    ) -> None:
        self.position = position
        self.flash = flash
        self.resolution: Tuple[int, int] = resolution or (1920, 1080)
        self.aspect_ratio = aspect_ratio


class Kamela:
    """Camera manager for mobile device cameras.

    Controls camera hardware for photo capture, video recording,
    and live preview. Supports switching between front and back cameras
    and adjusting flash, zoom, and focus settings.
    """

    def __init__(self, initial_config: Optional[CameraConfig] = None) -> None:
        self._config: CameraConfig = initial_config or CameraConfig()
        self._is_open: bool = False
        self._position: CameraPosition = self._config.position
        self._flash: CameraFlash = self._config.flash
        self._preview: bool = False
        self._zoom: float = 1.0
        self._focus: Tuple[float, float] = (0.5, 0.5)
        self._recording: bool = False

    # -- Properties -----------------------------------------------------------

    @property
    def position(self) -> CameraPosition:
        """Current active camera position."""
        return self._position

    @property
    def flash(self) -> CameraFlash:
        """Current flash mode."""
        return self._flash

    @property
    def config(self) -> CameraConfig:
        """Full camera configuration."""
        return self._config

    @property
    def is_open(self) -> bool:
        """Whether the camera is currently open."""
        return self._is_open

    @property
    def preview(self) -> bool:
        """Whether live preview is active."""
        return self._preview

    # -- Lifecycle ------------------------------------------------------------

    def open(self) -> bool:
        """Open the camera hardware for capture.

        Returns:
            True if the camera was successfully opened.
        """
        if self._is_open:
            return True
        self._is_open = True
        return True

    def close(self) -> bool:
        """Release the camera hardware.

        Stops preview and recording before closing.

        Returns:
            True if the camera was successfully closed.
        """
        if not self._is_open:
            return True
        if self._recording:
            self.stop_recording()
        if self._preview:
            self.stop_preview()
        self._is_open = False
        return True

    # -- Capture --------------------------------------------------------------

    def take_photo(self) -> Optional[bytes]:
        """Capture a single photo from the camera.

        Returns:
            Raw image bytes if capture succeeded, None otherwise.
        """
        if not self._is_open:
            return None
        return b"<photo_data>"

    def start_recording(self, file_path: Optional[str] = None) -> bool:
        """Begin video recording.

        Args:
            file_path: Optional path to save the recording.

        Returns:
            True if recording started successfully.
        """
        if not self._is_open or self._recording:
            return False
        self._recording = True
        return True

    def stop_recording(self) -> Optional[str]:
        """Stop the active video recording.

        Returns:
            Path to the recorded video file, or None if not recording.
        """
        if not self._recording:
            return None
        self._recording = False
        return "/path/to/recording.mp4"

    # -- Controls -------------------------------------------------------------

    def switch_camera(self) -> CameraPosition:
        """Toggle between front and back cameras.

        Returns:
            The new active camera position.
        """
        if self._position == CameraPosition.INYUMA:
            self._position = CameraPosition.IMERE
        else:
            self._position = CameraPosition.INYUMA
        self._config.position = self._position
        return self._position

    def set_flash(self, mode: CameraFlash) -> None:
        """Set the camera flash mode.

        Args:
            mode: The desired flash mode.
        """
        self._flash = mode
        self._config.flash = mode

    def set_zoom(self, level: float) -> None:
        """Adjust the zoom level.

        Args:
            level: Zoom multiplier (1.0 = no zoom).
        """
        self._zoom = max(1.0, min(level, 10.0))

    def set_focus(self, x: float, y: float) -> None:
        """Set the focus point.

        Args:
            x: Horizontal focus position (0.0 – 1.0).
            y: Vertical focus position (0.0 – 1.0).
        """
        self._focus = (max(0.0, min(x, 1.0)), max(0.0, min(y, 1.0)))

    # -- Preview --------------------------------------------------------------

    def start_preview(self) -> bool:
        """Start the camera preview stream.

        Returns:
            True if preview started successfully.
        """
        if not self._is_open or self._preview:
            return False
        self._preview = True
        return True

    def stop_preview(self) -> bool:
        """Stop the camera preview stream.

        Returns:
            True if preview was stopped.
        """
        if not self._preview:
            return False
        self._preview = False
        return True

    def __repr__(self) -> str:
        return (
            f"Kamela(position={self._position.value}, "
            f"flash={self._flash.value}, open={self._is_open})"
        )
