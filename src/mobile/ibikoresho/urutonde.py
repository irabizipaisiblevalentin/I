from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Optional

from .ikoresho import Ikoresho


class ScrollDirection(Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class Urutonde(Ikoresho):
    """List component for displaying a scrollable collection of items.

    Supports both vertical and horizontal scrolling, pull-to-refresh,
    pagination, item separation, and press handling.

    Attributes:
        items: The data items to render.
        item_builder: Callable that returns a component for each item.
        scroll_direction: Scroll axis.
        separator: Component or widget rendered between items.
        on_item_press: Callback invoked with the pressed item.
        empty_text: Text shown when the list is empty.
        refreshing: Whether a refresh operation is in progress.
        on_refresh: Callback for pull-to-refresh.
        pagination: Whether pagination is enabled.
        on_load_more: Callback to load the next page.
        has_more: Whether additional pages are available.
    """

    def __init__(
        self,
        items: Optional[list[Any]] = None,
        item_builder: Optional[Callable[[Any, int], Ikoresho]] = None,
        scroll_direction: ScrollDirection = ScrollDirection.VERTICAL,
        separator: Optional[Any] = None,
        on_item_press: Optional[Callable[[Any], Any]] = None,
        empty_text: str = "Nta kintu",
        refreshing: bool = False,
        on_refresh: Optional[Callable[[], Any]] = None,
        pagination: bool = False,
        on_load_more: Optional[Callable[[], Any]] = None,
        has_more: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._items: list[Any] = items or []
        self._item_builder: Optional[Callable[[Any, int], Ikoresho]] = item_builder
        self._scroll_direction: ScrollDirection = scroll_direction
        self._separator: Optional[Any] = separator
        self._on_item_press: Optional[Callable[[Any], Any]] = on_item_press
        self._empty_text: str = empty_text
        self._refreshing: bool = refreshing
        self._on_refresh: Optional[Callable[[], Any]] = on_refresh
        self._pagination: bool = pagination
        self._on_load_more: Optional[Callable[[], Any]] = on_load_more
        self._has_more: bool = has_more

    # --- Properties ---

    @property
    def items(self) -> list[Any]:
        return list(self._items)

    @items.setter
    def items(self, value: list[Any]) -> None:
        self._items = list(value)

    @property
    def item_builder(self) -> Optional[Callable[[Any, int], Ikoresho]]:
        return self._item_builder

    @item_builder.setter
    def item_builder(self, value: Optional[Callable[[Any, int], Ikoresho]]) -> None:
        self._item_builder = value

    @property
    def scroll_direction(self) -> ScrollDirection:
        return self._scroll_direction

    @scroll_direction.setter
    def scroll_direction(self, value: ScrollDirection) -> None:
        self._scroll_direction = value

    @property
    def separator(self) -> Optional[Any]:
        return self._separator

    @separator.setter
    def separator(self, value: Optional[Any]) -> None:
        self._separator = value

    @property
    def on_item_press(self) -> Optional[Callable[[Any], Any]]:
        return self._on_item_press

    @on_item_press.setter
    def on_item_press(self, value: Optional[Callable[[Any], Any]]) -> None:
        self._on_item_press = value

    @property
    def empty_text(self) -> str:
        return self._empty_text

    @empty_text.setter
    def empty_text(self, value: str) -> None:
        self._empty_text = value

    @property
    def refreshing(self) -> bool:
        return self._refreshing

    @refreshing.setter
    def refreshing(self, value: bool) -> None:
        self._refreshing = value

    @property
    def on_refresh(self) -> Optional[Callable[[], Any]]:
        return self._on_refresh

    @on_refresh.setter
    def on_refresh(self, value: Optional[Callable[[], Any]]) -> None:
        self._on_refresh = value

    @property
    def pagination(self) -> bool:
        return self._pagination

    @pagination.setter
    def pagination(self, value: bool) -> None:
        self._pagination = value

    @property
    def on_load_more(self) -> Optional[Callable[[], Any]]:
        return self._on_load_more

    @on_load_more.setter
    def on_load_more(self, value: Optional[Callable[[], Any]]) -> None:
        self._on_load_more = value

    @property
    def has_more(self) -> bool:
        return self._has_more

    @has_more.setter
    def has_more(self, value: bool) -> None:
        self._has_more = value

    # --- Methods ---

    def reload(self) -> None:
        self._refreshing = True
        if self._on_refresh is not None:
            self._on_refresh()
        self._refreshing = False

    def append(self, item: Any) -> None:
        self._items.append(item)

    def remove(self, item: Any) -> None:
        try:
            self._items.remove(item)
        except ValueError:
            pass

    def clear(self) -> None:
        self._items.clear()

    def scroll_to(self, index: int, animated: bool = True) -> None:
        if index < 0 or index >= len(self._items):
            return
        # In a real implementation this would call the underlying
        # scroll-to-index API of the platform.
        pass

    def notify_item_changed(self, index: int) -> None:
        if index < 0 or index >= len(self._items):
            return
        # Triggers a re-render of the item at the given index.
        pass

    def _load_more(self) -> None:
        if self._pagination and self._has_more and self._on_load_more is not None:
            self._on_load_more()

    def render(self) -> dict[str, Any]:
        return {
            "type": "Urutonde",
            "item_count": len(self._items),
            "scroll_direction": self._scroll_direction.value,
            "empty": len(self._items) == 0,
            "empty_text": self._empty_text,
            "refreshing": self._refreshing,
            "pagination": self._pagination,
            "has_more": self._has_more,
            "visible": self._visible,
        }


class UrutondeIgikubo(Urutonde):
    """ListView – a vertically scrolling list with built-in item
    recycling and separator support.

    This subclass specialises Urutonde for the common case of a
    single-column vertical list.
    """

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("scroll_direction", ScrollDirection.VERTICAL)
        super().__init__(**kwargs)

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "UrutondeIgikubo"
        return base


class UrutondeGikoni(Urutonde):
    """GridList – a scrollable grid of items arranged in columns.

    Adds grid-specific properties such as column count and spacing.

    Attributes:
        column_count: Number of columns in the grid.
        spacing: Gap between items in pixels.
    """

    def __init__(
        self,
        column_count: int = 2,
        spacing: int = 8,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._column_count: int = max(1, column_count)
        self._spacing: int = max(0, spacing)

    @property
    def column_count(self) -> int:
        return self._column_count

    @column_count.setter
    def column_count(self, value: int) -> None:
        self._column_count = max(1, value)

    @property
    def spacing(self) -> int:
        return self._spacing

    @spacing.setter
    def spacing(self, value: int) -> None:
        self._spacing = max(0, value)

    def render(self) -> dict[str, Any]:
        base = super().render()
        base["type"] = "UrutondeGikoni"
        base["column_count"] = self._column_count
        base["spacing"] = self._spacing
        return base
