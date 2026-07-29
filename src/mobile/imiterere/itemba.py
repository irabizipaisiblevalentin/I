"""Itemba (Stack) layout for overlapping children."""

from enum import Enum
from typing import Any, List, Optional


class Alignment(Enum):
    """Alignment options for stack children."""

    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


class Itemba:
    """Itemba (Stack) layout - stacks children on top of each other.

    The last child added is rendered on top by default.

    Args:
        children: Initial list of child elements.
        alignment: Default alignment for all children.
        width: Fixed width of the stack.
        height: Fixed height of the stack.
    """

    def __init__(
        self,
        children: Optional[List[Any]] = None,
        alignment: Alignment = Alignment.TOP_LEFT,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ) -> None:
        self._children: List[Any] = children if children is not None else []
        self._alignment: Alignment = alignment
        self._width: Optional[float] = width
        self._height: Optional[float] = height

    @property
    def children(self) -> List[Any]:
        """List of child elements in the stack."""
        return self._children

    @property
    def alignment(self) -> Alignment:
        """Default alignment for all children."""
        return self._alignment

    @alignment.setter
    def alignment(self, value: Alignment) -> None:
        self._alignment = value

    @property
    def width(self) -> Optional[float]:
        """Fixed width of the stack."""
        return self._width

    @width.setter
    def width(self, value: Optional[float]) -> None:
        self._width = value

    @property
    def height(self) -> Optional[float]:
        """Fixed height of the stack."""
        return self._height

    @height.setter
    def height(self, value: Optional[float]) -> None:
        self._height = value

    def add(self, child: Any, index: Optional[int] = None) -> None:
        """Add a child element at the specified index or at the top.

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
        """Remove all children from the stack."""
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

    def bring_to_front(self, child: Any) -> bool:
        """Move a child to the top of the stacking order.

        Args:
            child: The element to bring to the front.

        Returns:
            True if the child was found and moved, False otherwise.
        """
        try:
            self._children.remove(child)
            self._children.append(child)
            return True
        except ValueError:
            return False

    def send_to_back(self, child: Any) -> bool:
        """Move a child to the bottom of the stacking order.

        Args:
            child: The element to send to the back.

        Returns:
            True if the child was found and moved, False otherwise.
        """
        try:
            self._children.remove(child)
            self._children.insert(0, child)
            return True
        except ValueError:
            return False
