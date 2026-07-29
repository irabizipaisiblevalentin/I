"""Urusobete (Grid) layout for arranging children in a grid pattern."""

from typing import Any, List, Optional, Tuple


class Urusobete:
    """Urusobete (Grid) layout - arranges children in a grid.

    Args:
        columns: Number of columns in the grid.
        children: Initial list of child elements.
        spacing: Space between grid items (horizontal, vertical) or a single value.
        padding: Padding around the layout edge.
        item_aspect_ratio: Optional aspect ratio (width/height) for grid items.
    """

    def __init__(
        self,
        columns: int = 2,
        children: Optional[List[Any]] = None,
        spacing: float = 0.0,
        padding: float = 0.0,
        item_aspect_ratio: Optional[float] = None,
    ) -> None:
        if columns < 1:
            raise ValueError("columns must be at least 1")
        self._columns: int = columns
        self._children: List[Any] = children if children is not None else []
        self._spacing: float = spacing
        self._padding: float = padding
        self._item_aspect_ratio: Optional[float] = item_aspect_ratio

    @property
    def columns(self) -> int:
        """Number of columns in the grid."""
        return self._columns

    @columns.setter
    def columns(self, value: int) -> None:
        if value < 1:
            raise ValueError("columns must be at least 1")
        self._columns = value

    @property
    def children(self) -> List[Any]:
        """List of child elements in the grid."""
        return self._children

    @property
    def spacing(self) -> float:
        """Space between grid items."""
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
    def item_aspect_ratio(self) -> Optional[float]:
        """Aspect ratio (width/height) for grid items."""
        return self._item_aspect_ratio

    @item_aspect_ratio.setter
    def item_aspect_ratio(self, value: Optional[float]) -> None:
        self._item_aspect_ratio = value

    @property
    def row_count(self) -> int:
        """Number of rows currently occupied in the grid."""
        if self._columns == 0 or not self._children:
            return 0
        return (len(self._children) + self._columns - 1) // self._columns

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
        """Remove all children from the grid."""
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

    def get_item_position(self, index: int) -> Tuple[int, int]:
        """Get the (row, column) position of a child by index.

        Args:
            index: The index of the child.

        Returns:
            A tuple of (row, column) for the child position.

        Raises:
            IndexError: If the index is out of range.
        """
        if index < 0 or index >= len(self._children):
            raise IndexError("child index out of range")
        row = index // self._columns
        col = index % self._columns
        return (row, col)
