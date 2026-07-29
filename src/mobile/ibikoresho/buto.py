from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Optional

from .ikoresho import Ikoresho


class ButoSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class ButoVariant(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    OUTLINE = "outline"
    TEXT = "text"


class Buto(Ikoresho):
    """Button component for user interaction.

    Supports multiple sizes, variants, icons, loading state, and
    press handling.

    Attributes:
        text: Label displayed on the button.
        on_press: Callback invoked when the button is pressed.
        enabled: Whether the button responds to user interaction.
        loading: Whether the button shows a loading indicator.
        style: Additional style overrides.
        color: Background color of the button.
        text_color: Color of the button text.
        border_radius: Corner radius in pixels.
        padding: Internal padding as (horizontal, vertical) or int.
        icon: Optional icon name or path.
        size: Size preset from ButoSize.
        variant: Visual variant from ButoVariant.
    """

    def __init__(
        self,
        text: str = "",
        on_press: Optional[Callable[[], Any]] = None,
        enabled: bool = True,
        loading: bool = False,
        style: Optional[dict[str, Any]] = None,
        color: Optional[str] = None,
        text_color: Optional[str] = None,
        border_radius: Optional[int] = None,
        padding: Any = None,
        icon: Optional[str] = None,
        size: ButoSize = ButoSize.MEDIUM,
        variant: ButoVariant = ButoVariant.PRIMARY,
        **kwargs: Any,
    ) -> None:
        super().__init__(enabled=enabled, style=style, **kwargs)
        self._text: str = text
        self._on_press: Optional[Callable[[], Any]] = on_press
        self._loading: bool = loading
        self._color: Optional[str] = color
        self._text_color: Optional[str] = text_color
        self._border_radius: Optional[int] = border_radius
        self._padding: Any = padding
        self._icon: Optional[str] = icon
        self._size: ButoSize = size
        self._variant: ButoVariant = variant

    # --- Properties ---

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @property
    def on_press(self) -> Optional[Callable[[], Any]]:
        return self._on_press

    @on_press.setter
    def on_press(self, value: Optional[Callable[[], Any]]) -> None:
        self._on_press = value

    @property
    def loading(self) -> bool:
        return self._loading

    @loading.setter
    def loading(self, value: bool) -> None:
        self._loading = value

    @property
    def color(self) -> Optional[str]:
        return self._color

    @color.setter
    def color(self, value: Optional[str]) -> None:
        self._color = value

    @property
    def text_color(self) -> Optional[str]:
        return self._text_color

    @text_color.setter
    def text_color(self, value: Optional[str]) -> None:
        self._text_color = value

    @property
    def border_radius(self) -> Optional[int]:
        return self._border_radius

    @border_radius.setter
    def border_radius(self, value: Optional[int]) -> None:
        self._border_radius = value

    @property
    def padding(self) -> Any:
        return self._padding

    @padding.setter
    def padding(self, value: Any) -> None:
        self._padding = value

    @property
    def icon(self) -> Optional[str]:
        return self._icon

    @icon.setter
    def icon(self, value: Optional[str]) -> None:
        self._icon = value

    @property
    def size(self) -> ButoSize:
        return self._size

    @size.setter
    def size(self, value: ButoSize) -> None:
        self._size = value

    @property
    def variant(self) -> ButoVariant:
        return self._variant

    @variant.setter
    def variant(self, value: ButoVariant) -> None:
        self._variant = value

    # --- Methods ---

    def press(self) -> None:
        if self._enabled and not self._loading and self._on_press is not None:
            self._on_press()

    def set_loading(self, loading: bool) -> None:
        self._loading = loading

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def set_text(self, text: str) -> None:
        self._text = text

    def render(self) -> dict[str, Any]:
        return {
            "type": "Buto",
            "text": self._text,
            "loading": self._loading,
            "color": self._color,
            "text_color": self._text_color,
            "border_radius": self._border_radius,
            "padding": self._padding,
            "icon": self._icon,
            "size": self._size.value,
            "variant": self._variant.value,
            "enabled": self._enabled,
            "visible": self._visible,
        }
