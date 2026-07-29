from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from .ikoresho import Ikoresho


class TextTransform(Enum):
    NONE = "none"
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    CAPITALIZE = "capitalize"


class FontWeight(Enum):
    NORMAL = "normal"
    BOLD = "bold"
    LIGHT = "light"
    MEDIUM = "medium"
    SEMI_BOLD = "semibold"


class Ikimenyetso(Ikoresho):
    """Text / Label component for displaying read-only text.

    Attributes:
        text: The string content to display.
        font_size: Size of the font in pixels.
        font_weight: Weight / boldness of the font.
        color: Text color.
        text_align: Horizontal alignment (left, center, right).
        line_height: Line height multiplier or pixel value.
        max_lines: Maximum number of lines before truncation.
        overflow: Overflow behaviour (clip, ellipsis, fade).
        text_transform: Text transformation preset.
    """

    def __init__(
        self,
        text: str = "",
        font_size: Optional[int] = None,
        font_weight: FontWeight = FontWeight.NORMAL,
        color: Optional[str] = None,
        text_align: Optional[str] = None,
        line_height: Optional[float] = None,
        max_lines: Optional[int] = None,
        overflow: Optional[str] = None,
        text_transform: TextTransform = TextTransform.NONE,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._text: str = text
        self._font_size: Optional[int] = font_size
        self._font_weight: FontWeight = font_weight
        self._color: Optional[str] = color
        self._text_align: Optional[str] = text_align
        self._line_height: Optional[float] = line_height
        self._max_lines: Optional[int] = max_lines
        self._overflow: Optional[str] = overflow
        self._text_transform: TextTransform = text_transform

    # --- Properties ---

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @property
    def font_size(self) -> Optional[int]:
        return self._font_size

    @font_size.setter
    def font_size(self, value: Optional[int]) -> None:
        self._font_size = value

    @property
    def font_weight(self) -> FontWeight:
        return self._font_weight

    @font_weight.setter
    def font_weight(self, value: FontWeight) -> None:
        self._font_weight = value

    @property
    def color(self) -> Optional[str]:
        return self._color

    @color.setter
    def color(self, value: Optional[str]) -> None:
        self._color = value

    @property
    def text_align(self) -> Optional[str]:
        return self._text_align

    @text_align.setter
    def text_align(self, value: Optional[str]) -> None:
        self._text_align = value

    @property
    def line_height(self) -> Optional[float]:
        return self._line_height

    @line_height.setter
    def line_height(self, value: Optional[float]) -> None:
        self._line_height = value

    @property
    def max_lines(self) -> Optional[int]:
        return self._max_lines

    @max_lines.setter
    def max_lines(self, value: Optional[int]) -> None:
        self._max_lines = value

    @property
    def overflow(self) -> Optional[str]:
        return self._overflow

    @overflow.setter
    def overflow(self, value: Optional[str]) -> None:
        self._overflow = value

    @property
    def text_transform(self) -> TextTransform:
        return self._text_transform

    @text_transform.setter
    def text_transform(self, value: TextTransform) -> None:
        self._text_transform = value

    # --- Methods ---

    def set_text(self, text: str) -> None:
        self._text = text

    def _apply_transform(self) -> str:
        if self._text_transform == TextTransform.UPPERCASE:
            return self._text.upper()
        elif self._text_transform == TextTransform.LOWERCASE:
            return self._text.lower()
        elif self._text_transform == TextTransform.CAPITALIZE:
            return self._text.capitalize()
        return self._text

    def measure(self) -> tuple[int, int]:
        text_content = self._apply_transform()
        char_width = self._font_size or 14
        line_count = max(1, text_content.count("\n") + 1)
        max_line_len = max((len(line) for line in text_content.split("\n")), default=0)
        width = max_line_len * char_width
        height = line_count * (self._line_height or 1.2) * (self._font_size or 14)
        return (int(width), int(height))

    def render(self) -> dict[str, Any]:
        return {
            "type": "Ikimenyetso",
            "text": self._apply_transform(),
            "font_size": self._font_size,
            "font_weight": self._font_weight.value,
            "color": self._color,
            "text_align": self._text_align,
            "line_height": self._line_height,
            "max_lines": self._max_lines,
            "overflow": self._overflow,
            "visible": self._visible,
        }


class Umutwe(Ikimenyetso):
    """Heading component with semantic levels 1-6.

    Attributes:
        level: Heading level (1-6), each with a preset font size.
    """

    _LEVEL_SIZES: dict[int, int] = {
        1: 32, 2: 28, 3: 24, 4: 20, 5: 18, 6: 16,
    }

    def __init__(
        self,
        text: str = "",
        level: int = 1,
        color: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        font_size = kwargs.pop("font_size", None) or self._LEVEL_SIZES.get(level, 24)
        font_weight = kwargs.pop("font_weight", None) or FontWeight.BOLD
        super().__init__(
            text=text,
            font_size=font_size,
            font_weight=font_weight,
            color=color,
            **kwargs,
        )
        self._level: int = level

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, value: int) -> None:
        self._level = max(1, min(6, value))
        self._font_size = self._LEVEL_SIZES.get(self._level, 24)

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "Umutwe"
        base["level"] = self._level
        return base


class Ibara(Ikimenyetso):
    """Paragraph component for body text.

    Provides a sensible default font size (16px) and line
    height (1.5) optimised for readability.
    """

    def __init__(
        self,
        text: str = "",
        **kwargs: Any,
    ) -> None:
        kwargs.setdefault("font_size", 16)
        kwargs.setdefault("line_height", 1.5)
        super().__init__(text=text, **kwargs)

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "Ibara"
        return base
