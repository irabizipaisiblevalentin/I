from __future__ import annotations

from typing import Any, Callable, Optional

from .ikoresho import Ikoresho


class Ikarita(Ikoresho):
    """Card component for grouping related content.

    Cards visually bundle a title, subtitle, optional image,
    custom content, and action buttons.

    Attributes:
        title: Primary text displayed in the card header.
        subtitle: Secondary text below the title.
        content: Custom child component placed in the card body.
        image: Optional image component displayed at the top.
        actions: List of action components (typically Buto).
        elevation: Shadow depth (z-height) in dp.
        border_radius: Corner radius in pixels.
        padding: Internal padding in pixels.
        on_press: Callback invoked when the card is tapped.
    """

    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        content: Optional[Ikoresho] = None,
        image: Optional[Any] = None,
        actions: Optional[list[Ikoresho]] = None,
        elevation: int = 2,
        border_radius: int = 12,
        padding: int = 16,
        on_press: Optional[Callable[[], Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._title: str = title
        self._subtitle: str = subtitle
        self._content: Optional[Ikoresho] = content
        if self._content is not None:
            self.add_child(self._content)
        self._image: Optional[Any] = image
        self._actions: list[Ikoresho] = actions or []
        for action in self._actions:
            self.add_child(action)
        self._elevation: int = elevation
        self._border_radius: int = border_radius
        self._padding: int = padding
        self._on_press: Optional[Callable[[], Any]] = on_press

    # --- Properties ---

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value

    @property
    def subtitle(self) -> str:
        return self._subtitle

    @subtitle.setter
    def subtitle(self, value: str) -> None:
        self._subtitle = value

    @property
    def content(self) -> Optional[Ikoresho]:
        return self._content

    @content.setter
    def content(self, value: Optional[Ikoresho]) -> None:
        if self._content is not None:
            self.remove_child(self._content)
        self._content = value
        if self._content is not None:
            self.add_child(self._content)

    @property
    def image(self) -> Optional[Any]:
        return self._image

    @image.setter
    def image(self, value: Optional[Any]) -> None:
        self._image = value

    @property
    def actions(self) -> list[Ikoresho]:
        return list(self._actions)

    @actions.setter
    def actions(self, value: list[Ikoresho]) -> None:
        for action in self._actions:
            self.remove_child(action)
        self._actions = list(value)
        for action in self._actions:
            self.add_child(action)

    @property
    def elevation(self) -> int:
        return self._elevation

    @elevation.setter
    def elevation(self, value: int) -> None:
        self._elevation = max(0, value)

    @property
    def border_radius(self) -> int:
        return self._border_radius

    @border_radius.setter
    def border_radius(self, value: int) -> None:
        self._border_radius = max(0, value)

    @property
    def padding(self) -> int:
        return self._padding

    @padding.setter
    def padding(self, value: int) -> None:
        self._padding = max(0, value)

    @property
    def on_press(self) -> Optional[Callable[[], Any]]:
        return self._on_press

    @on_press.setter
    def on_press(self, value: Optional[Callable[[], Any]]) -> None:
        self._on_press = value

    # --- Methods ---

    def set_title(self, title: str) -> None:
        self._title = title

    def set_content(self, content: Ikoresho) -> None:
        self.content = content

    def add_action(self, action: Ikoresho) -> None:
        self._actions.append(action)
        self.add_child(action)

    def remove_action(self, action: Ikoresho) -> None:
        if action in self._actions:
            self._actions.remove(action)
            self.remove_child(action)

    def render(self) -> dict[str, Any]:
        return {
            "type": "Ikarita",
            "title": self._title,
            "subtitle": self._subtitle,
            "has_content": self._content is not None,
            "has_image": self._image is not None,
            "action_count": len(self._actions),
            "elevation": self._elevation,
            "border_radius": self._border_radius,
            "padding": self._padding,
            "visible": self._visible,
        }
