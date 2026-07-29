"""Inkingi (Column) layout for vertical stacking of children."""

from enum import Enum
from typing import Any, List, Optional


class Alignment(Enum):
    """Alignment options for layout children."""

    START = "start"
    CENTER = "center"
    END = "end"
    STRETCH = "stretch"


class Inkingi:
    """Inkingi (Column) layout - arranges children vertically.

    Args:
        children: Initial list of child elements.
        spacing: Vertical space between children.
        padding: Padding around the layout edge.
        alignment: Horizontal alignment of children.
        cross_alignment: Vertical alignment (cross axis).
        width: Fixed width of the column.
        height: Fixed height of the column.
        scrollable: Whether the column supports scrolling.
    """

    def __init__(
        self,
        children: Optional[List[Any]] = None,
        spacing: float = 0.0,
        padding: float = 0.0,
        alignment: Alignment = Alignment.START,
        cross_alignment: Alignment = Alignment.START,
        width: Optional[float] = None,
        height: Optional[float] = None,
        scrollable: bool = False,
    ) -> None:
        self._children: List[Any] = children if children is not None else []
        self._spacing: float = spacing
        self._padding: float = padding
        self._alignment: Alignment = alignment
        self._cross_alignment: Alignment = cross_alignment
        self._width: Optional[float] = width
        self._height: Optional[float] = height
        self._scrollable: bool = scrollable

    @property
    def children(self) -> List[Any]:
        """List of child elements in the column."""
        return self._children

    @property
    def spacing(self) -> float:
        """Vertical space between children."""
        return self._spacing

    @spacing.setter
    def spacing(self, value: float) -> None:
        self._spacing = value

    @property
    def padding(self) -> float:
        """Padding around the layout edge."""
        return self._padding

    @padding.setter
    def padding(self, value: float) -> None:
        self._padding = value

    @property
    def alignment(self) -> Alignment:
        """Horizontal alignment of children."""
        return self._alignment

    @alignment.setter
    def alignment(self, value: Alignment) -> None:
        self._alignment = value

    @property
    def cross_alignment(self) -> Alignment:
        """Vertical (cross axis) alignment."""
        return self._cross_alignment

    @cross_alignment.setter
    def cross_alignment(self, value: Alignment) -> None:
        self._cross_alignment = value

    @property
    def width(self) -> Optional[float]:
        """Fixed width of the column."""
        return self._width

    @width.setter
    def width(self, value: Optional[float]) -> None:
        self._width = value

    @property
    def height(self) -> Optional[float]:
        """Fixed height of the column."""
        return self._height

    @height.setter
    def height(self, value: Optional[float]) -> None:
        self._height = value

    @property
    def scrollable(self) -> bool:
        """Whether the column supports scrolling."""
        return self._scrollable

    @scrollable.setter
    def scrollable(self, value: bool) -> None:
        self._scrollable = value

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
        """Remove all children from the column."""
        self._children.clear()

    def get_child(self, index: int) -> Any:
        """Get a child element by index.

        Args:
            index: The index of the child.

        Returns:
            The child element at the given index.

        Raises:
            IndexError: If the index is out of range.
        """
        return self._children[index]
