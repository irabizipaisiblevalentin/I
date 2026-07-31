from __future__ import annotations

from abc import ABC
from typing import Any, Optional


class Ikoresho(ABC):
    """Base class that all UI components extend.

    Provides core properties and methods for the component hierarchy,
    visibility, enabling, layout, and lifecycle management.

    Attributes:
        id: Unique identifier for this component.
        parent: Parent component in the UI tree.
        children: Child components.
        visible: Whether the component is currently visible.
        enabled: Whether the component is interactive.
        style: Dictionary of CSS-like style properties.
        layout_params: Layout configuration (e.g. flex, padding, margin).
        tag: Arbitrary metadata tag.
        accessibility_label: Accessible label for screen readers.
        accessibility_hint: Accessible hint for screen readers.
    """

    def __init__(
        self,
        component_id: Optional[str] = None,
        visible: bool = True,
        enabled: bool = True,
        style: Optional[dict[str, Any]] = None,
        layout_params: Optional[dict[str, Any]] = None,
        tag: Any = None,
        accessibility_label: Optional[str] = None,
        accessibility_hint: Optional[str] = None,
    ) -> None:
        self._id: Optional[str] = component_id
        self._parent: Optional[Ikoresho] = None
        self._children: list[Ikoresho] = []
        self._visible: bool = visible
        self._enabled: bool = enabled
        self._style: dict[str, Any] = style or {}
        self._layout_params: dict[str, Any] = layout_params or {}
        self._tag: Any = tag
        self._accessibility_label: Optional[str] = accessibility_label
        self._accessibility_hint: Optional[str] = accessibility_hint

    # --- Properties ---

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: Optional[str]) -> None:
        self._id = value

    @property
    def parent(self) -> Optional[Ikoresho]:
        return self._parent

    @parent.setter
    def parent(self, value: Optional[Ikoresho]) -> None:
        self._parent = value

    @property
    def children(self) -> list[Ikoresho]:
        return list(self._children)

    @property
    def visible(self) -> bool:
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._visible = value

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    @property
    def style(self) -> dict[str, Any]:
        return self._style

    @style.setter
    def style(self, value: dict[str, Any]) -> None:
        self._style = value

    @property
    def layout_params(self) -> dict[str, Any]:
        return self._layout_params

    @layout_params.setter
    def layout_params(self, value: dict[str, Any]) -> None:
        self._layout_params = value

    @property
    def tag(self) -> Any:
        return self._tag

    @tag.setter
    def tag(self, value: Any) -> None:
        self._tag = value

    @property
    def accessibility_label(self) -> Optional[str]:
        return self._accessibility_label

    @accessibility_label.setter
    def accessibility_label(self, value: Optional[str]) -> None:
        self._accessibility_label = value

    @property
    def accessibility_hint(self) -> Optional[str]:
        return self._accessibility_hint

    @accessibility_hint.setter
    def accessibility_hint(self, value: Optional[str]) -> None:
        self._accessibility_hint = value

    # --- Public methods ---

    def show(self) -> None:
        self._visible = True

    def hide(self) -> None:
        self._visible = False

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled

    def find_by_id(self, component_id: str) -> Optional[Ikoresho]:
        if self._id == component_id:
            return self
        for child in self._children:
            result = child.find_by_id(component_id)
            if result is not None:
                return result
        return None

    def add_child(self, child: Ikoresho) -> None:
        child._parent = self
        self._children.append(child)

    def remove_child(self, child: Ikoresho) -> None:
        if child in self._children:
            self._children.remove(child)
            child._parent = None

    def render(self) -> Any:
        raise NotImplementedError

    def dispose(self) -> None:
        for child in self._children:
            child.dispose()
        self._children.clear()
        self._parent = None

    def measure(self) -> tuple[int, int]:
        return (0, 0)

    def layout(self) -> None:
        pass
