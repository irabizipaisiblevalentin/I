"""window — Window/display utilities for the I language.

Provides display information and basic window management abstractions.
"""

from __future__ import annotations

from typing import Optional, Tuple


class DisplayInfo:
    """Display/monitor information."""
    __slots__ = ("width", "height", "name", "is_primary")

    def __init__(self, width: int = 0, height: int = 0,
                 name: str = "", is_primary: bool = True) -> None:
        self.width = width
        self.height = height
        self.name = name
        self.is_primary = is_primary

    def __repr__(self) -> str:
        return f"DisplayInfo({self.width}x{self.height})"


class Window:
    """Abstract window handle."""

    def __init__(self, title: str = "I Window", width: int = 800, height: int = 600) -> None:
        self.title = title
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.visible = True
        self._closed = False

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def close(self) -> None:
        self._closed = True
        self.visible = False

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def move(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def set_title(self, title: str) -> None:
        self.title = title

    @property
    def is_closed(self) -> bool:
        return self._closed

    @property
    def size(self) -> Tuple[int, int]:
        return (self.width, self.height)

    @property
    def position(self) -> Tuple[int, int]:
        return (self.x, self.y)

    def __repr__(self) -> str:
        return f"Window({self.title!r}, {self.width}x{self.height})"


def get_displays():
    """Get list of available displays."""
    return [DisplayInfo(1920, 1080, "Primary", True)]


def get_primary_display() -> DisplayInfo:
    return DisplayInfo(1920, 1080, "Primary", True)


def create_window(title: str = "I Window", width: int = 800, height: int = 600) -> Window:
    return Window(title, width, height)
