"""Ikinyabiziga (Flex) layout for flexible box arrangements."""

from enum import Enum
from typing import Any, List, Optional


class FlexDirection(Enum):
    """Direction of the flex layout."""

    ROW = "row"
    COLUMN = "column"


class JustifyContent(Enum):
    """Justify content alignment options."""

    START = "start"
    CENTER = "center"
    END = "end"
    SPACE_BETWEEN = "space_between"
    SPACE_AROUND = "space_around"
    SPACE_EVENLY = "space_evenly"


class AlignItems(Enum):
    """Align items alignment options."""

    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"
    BASELINE = "baseline"


class AlignContent(Enum):
    """Align content alignment options for multi-line flex containers."""

    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"
    SPACE_BETWEEN = "space_between"
    SPACE_AROUND = "space_around"


class Ikinyabiziga:
    """Ikinyabiziga (Flex) layout - flexible box arrangement.

    Args:
        children: Initial list of child elements.
        direction: Main axis direction (row or column).
        wrap: Whether children should wrap to the next line.
        justify_content: Alignment along the main axis.
        align_items: Alignment along the cross axis.
        align_content: Alignment of multi-line content along cross axis.
        gap: Gap between flex items.
    """

    def __init__(
        self,
        children: Optional[List[Any]] = None,
        direction: FlexDirection = FlexDirection.ROW,
        wrap: bool = False,
        justify_content: JustifyContent = JustifyContent.START,
        align_items: AlignItems = AlignItems.START,
        align_content: AlignContent = AlignContent.START,
        gap: float = 0.0,
    ) -> None:
        self._children: List[Any] = children if children is not None else []
        self._direction: FlexDirection = direction
        self._wrap: bool = wrap
        self._justify_content: JustifyContent = justify_content
        self._align_items: AlignItems = align_items
        self._align_content: AlignContent = align_content
        self._gap: float = gap

    @property
    def children(self) -> List[Any]:
        """List of child elements in the flex container."""
        return self._children

    @property
    def direction(self) -> FlexDirection:
        """Main axis direction (row or column)."""
        return self._direction

    @direction.setter
    def direction(self, value: FlexDirection) -> None:
        self._direction = value

    @property
    def wrap(self) -> bool:
        """Whether children should wrap to the next line."""
        return self._wrap

    @wrap.setter
    def wrap(self, value: bool) -> None:
        self._wrap = value

    @property
    def justify_content(self) -> JustifyContent:
        """Alignment along the main axis."""
        return self._justify_content

    @justify_content.setter
    def justify_content(self, value: JustifyContent) -> None:
        self._justify_content = value

    @property
    def align_items(self) -> AlignItems:
        """Alignment along the cross axis."""
        return self._align_items

    @align_items.setter
    def align_items(self, value: AlignItems) -> None:
        self._align_items = value

    @property
    def align_content(self) -> AlignContent:
        """Alignment of multi-line content along cross axis."""
        return self._align_content

    @align_content.setter
    def align_content(self, value: AlignContent) -> None:
        self._align_content = value

    @property
    def gap(self) -> float:
        """Gap between flex items."""
        return self._gap

    @gap.setter
    def gap(self, value: float) -> None:
        self._gap = value

    def add(self, child: Any, index: Optional[int] = None) -> None:
        """Add a child element at the specified index or at the end.

        Args:
            child: The element to add.
            index: Optional position to insert at.
        """
        if index is not None:
            self._children.insert(index, child)
        else:
            self._children.append(child)

    def remove(self, child: Any) -> bool:
        """Remove a child element.

        Args:
            child: The element to remove.

        Returns:
            True if the child was found and removed, False otherwise.
        """
        try:
            self._children.remove(child)
            return True
        except ValueError:
            return False

    def clear(self) -> None:
        """Remove all children from the flex container."""
        self._children.clear()
