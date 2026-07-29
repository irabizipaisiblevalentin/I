from __future__ import annotations

from typing import Any, Optional

from .ikoresho import Ikoresho


class Umubare(Ikoresho):
    """Progress indicator component (abstract base).

    Represents a visual progress indicator with both determinate
    (0.0–1.0) and indeterminate modes. Provides animation support.

    Attributes:
        value: Progress value between 0.0 and 1.0 (None for indeterminate).
        indeterminate: Whether the indicator is in indeterminate mode.
        color: Primary colour of the indicator.
        track_color: Colour of the background track.
        size: Size of the indicator in pixels.
        stroke_width: Thickness of the indicator stroke in pixels.
    """

    def __init__(
        self,
        value: Optional[float] = None,
        indeterminate: bool = False,
        color: Optional[str] = None,
        track_color: Optional[str] = None,
        size: int = 40,
        stroke_width: int = 4,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._value: Optional[float] = value
        self._indeterminate: bool = indeterminate
        self._color: Optional[str] = color
        self._track_color: Optional[str] = track_color
        self._size: int = max(1, size)
        self._stroke_width: int = max(1, stroke_width)
        self._target_value: Optional[float] = value
        self._animation_in_progress: bool = False

    # --- Properties ---

    @property
    def value(self) -> Optional[float]:
        return self._value

    @value.setter
    def value(self, new_value: Optional[float]) -> None:
        if new_value is not None:
            self._value = max(0.0, min(1.0, new_value))
        else:
            self._value = None

    @property
    def indeterminate(self) -> bool:
        return self._indeterminate

    @indeterminate.setter
    def indeterminate(self, value: bool) -> None:
        self._indeterminate = value

    @property
    def color(self) -> Optional[str]:
        return self._color

    @color.setter
    def color(self, value: Optional[str]) -> None:
        self._color = value

    @property
    def track_color(self) -> Optional[str]:
        return self._track_color

    @track_color.setter
    def track_color(self, value: Optional[str]) -> None:
        self._track_color = value

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        self._size = max(1, value)

    @property
    def stroke_width(self) -> int:
        return self._stroke_width

    @stroke_width.setter
    def stroke_width(self, value: int) -> None:
        self._stroke_width = max(1, value)

    # --- Methods ---

    def set_value(self, value: float) -> None:
        self._value = max(0.0, min(1.0, value))

    def set_indeterminate(self, indeterminate: bool) -> None:
        self._indeterminate = indeterminate

    def animate_to(self, target: float, duration_ms: int = 300) -> None:
        self._target_value = max(0.0, min(1.0, target))
        self._animation_in_progress = True

    def render(self) -> dict[str, Any]:
        return {
            "type": "Umubare",
            "value": self._value,
            "indeterminate": self._indeterminate,
            "color": self._color,
            "track_color": self._track_color,
            "size": self._size,
            "stroke_width": self._stroke_width,
            "visible": self._visible,
        }


class UmubareMuzunguruko(Umubare):
    """CircularProgressIndicator — a circular progress ring.

    Renders progress as an arc of a circle. In indeterminate mode
    the ring spins continuously.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "UmubareMuzunguruko"
        return base


class UmubareMuremure(Umubare):
    """LinearProgressIndicator — a horizontal progress bar.

    Renders progress as a filled horizontal bar. In indeterminate
    mode the bar shows a moving striped animation.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "UmubareMuremure"
        return base
