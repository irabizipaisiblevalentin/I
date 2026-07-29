from __future__ import annotations

from typing import Any, Callable, Optional

from .ikoresho import Ikoresho


class IkubazaItem:
    """Represents a single item in a navigation bar.

    Attributes:
        title: Display label for the item.
        icon: Optional icon name or path.
        badge: Optional badge count or text to show on the item.
        on_select: Callback specific to this item.
    """

    def __init__(
        self,
        title: str = "",
        icon: Optional[str] = None,
        badge: Optional[Any] = None,
        on_select: Optional[Callable[[], Any]] = None,
    ) -> None:
        self.title: str = title
        self.icon: Optional[str] = icon
        self.badge: Optional[Any] = badge
        self.on_select: Optional[Callable[[], Any]] = on_select


class Ikubaza(Ikoresho):
    """Navigation bar component for top app bars and bottom nav bars.

    Manages a collection of tab-style items with selection tracking.

    Attributes:
        items: List of IkubazaItem entries.
        selected_index: Index of the currently selected item.
        on_select: Callback with the selected index and item.
        color: Foreground / accent colour.
        background: Background colour of the bar.
    """

    def __init__(
        self,
        items: Optional[list[IkubazaItem]] = None,
        selected_index: int = 0,
        on_select: Optional[Callable[[int, IkubazaItem], Any]] = None,
        color: Optional[str] = None,
        background: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._items: list[IkubazaItem] = items or []
        self._selected_index: int = max(0, min(selected_index, len(self._items) - 1))
        self._on_select: Optional[Callable[[int, IkubazaItem], Any]] = on_select
        self._color: Optional[str] = color
        self._background: Optional[str] = background

    # --- Properties ---

    @property
    def items(self) -> list[IkubazaItem]:
        return list(self._items)

    @items.setter
    def items(self, value: list[IkubazaItem]) -> None:
        self._items = list(value)
        if self._selected_index >= len(self._items):
            self._selected_index = max(0, len(self._items) - 1)

    @property
    def selected_index(self) -> int:
        return self._selected_index

    @selected_index.setter
    def selected_index(self, value: int) -> None:
        if 0 <= value < len(self._items):
            self._selected_index = value

    @property
    def on_select(self) -> Optional[Callable[[int, IkubazaItem], Any]]:
        return self._on_select

    @on_select.setter
    def on_select(self, value: Optional[Callable[[int, IkubazaItem], Any]]) -> None:
        self._on_select = value

    @property
    def color(self) -> Optional[str]:
        return self._color

    @color.setter
    def color(self, value: Optional[str]) -> None:
        self._color = value

    @property
    def background(self) -> Optional[str]:
        return self._background

    @background.setter
    def background(self, value: Optional[str]) -> None:
        self._background = value

    # --- Methods ---

    def select(self, index: int) -> None:
        if 0 <= index < len(self._items):
            self._selected_index = index
            item = self._items[index]
            if item.on_select is not None:
                item.on_select()
            if self._on_select is not None:
                self._on_select(index, item)

    def set_items(self, items: list[IkubazaItem]) -> None:
        self.items = items

    def set_badge(self, index: int, badge: Any) -> None:
        if 0 <= index < len(self._items):
            self._items[index].badge = badge

    def render(self) -> dict[str, Any]:
        return {
            "type": "Ikubaza",
            "selected_index": self._selected_index,
            "item_count": len(self._items),
            "color": self._color,
            "background": self._background,
            "visible": self._visible,
        }


class IkubazaHejuru(Ikubaza):
    """TopAppBar — a top navigation bar with a title and actions.

    Attributes:
        title: Primary title text displayed in the bar.
        actions: List of IkubazaItem rendered as action icons.
        back_button: Whether to show a back/up navigation button.
        on_back: Callback when the back button is pressed.
    """

    def __init__(
        self,
        title: str = "",
        actions: Optional[list[IkubazaItem]] = None,
        back_button: bool = False,
        on_back: Optional[Callable[[], Any]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._title: str = title
        self._action_items: list[IkubazaItem] = actions or []
        self._back_button: bool = back_button
        self._on_back: Optional[Callable[[], Any]] = on_back

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value

    @property
    def actions(self) -> list[IkubazaItem]:
        return list(self._action_items)

    @actions.setter
    def actions(self, value: list[IkubazaItem]) -> None:
        self._action_items = list(value)

    @property
    def back_button(self) -> bool:
        return self._back_button

    @back_button.setter
    def back_button(self, value: bool) -> None:
        self._back_button = value

    @property
    def on_back(self) -> Optional[Callable[[], Any]]:
        return self._on_back

    @on_back.setter
    def on_back(self, value: Optional[Callable[[], Any]]) -> None:
        self._on_back = value

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "IkubazaHejuru"
        base["title"] = self._title
        base["back_button"] = self._back_button
        base["action_count"] = len(self._action_items)
        return base


class IkubazaHasi(Ikubaza):
    """BottomNavigationBar — a bottom tab bar with badges.

    Renders navigation items horizontally at the bottom of the
    screen with optional badge indicators.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "IkubazaHasi"
        return base
