"""ikiganiro — Activity/Screen management for the I mobile platform.

Ikiganiro represents a single screen or activity in a mobile application,
managing its own lifecycle, state, and view hierarchy.
"""

from __future__ import annotations

import enum
from typing import Any, Dict, List, Optional


class ActivityState(enum.Enum):
    """Lifecycle states for an Ikiganiro activity."""

    KUREMWE = "created"
    KURAMUKA = "starting"
    KIGEZWEHO = "resumed"
    KURAHAGURIKA = "pausing"
    KURAHAGARARA = "stopped"
    KURASENZWE = "destroyed"


class Ikiganiro:
    """Represents a single screen or activity in a mobile application.

    Manages its own lifecycle: create, start, resume, pause, stop, destroy.
    Each Ikiganiro can have child screens and maintains a view hierarchy.
    """

    def __init__(
        self,
        activity_id: str,
        title: str = "",
        parent: Optional[Ikiganiro] = None,
    ) -> None:
        self._id = activity_id
        self._title = title
        self._state = ActivityState.KUREMWE
        self._params: Dict[str, Any] = {}
        self._children: List[Ikiganiro] = []
        self._parent: Optional[Ikiganiro] = parent
        self._views: Dict[str, Any] = {}
        self._saved_state: Dict[str, Any] = {}
        self._content: Any = None

    # -- Properties -----------------------------------------------------------

    @property
    def id(self) -> str:
        """Unique identifier for this activity."""
        return self._id

    @property
    def title(self) -> str:
        """Display title for this activity."""
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value

    @property
    def state(self) -> ActivityState:
        """Current lifecycle state."""
        return self._state

    @property
    def params(self) -> Dict[str, Any]:
        """Parameters passed to this activity."""
        return self._params

    @params.setter
    def params(self, value: Dict[str, Any]) -> None:
        self._params = dict(value)

    @property
    def children(self) -> List[Ikiganiro]:
        """Child activities or fragments."""
        return list(self._children)

    @property
    def parent(self) -> Optional[Ikiganiro]:
        """Parent activity, if this is a child."""
        return self._parent

    @parent.setter
    def parent(self, value: Optional[Ikiganiro]) -> None:
        self._parent = value

    # -- Lifecycle ------------------------------------------------------------

    def on_create(self) -> None:
        """Called when the activity is first created.

        Subclasses should override to perform one-time setup.
        """
        self._state = ActivityState.KUREMWE
        if self._parent is not None:
            self._parent._children.append(self)

    def on_start(self) -> None:
        """Called when the activity becomes visible.

        Subclasses should override to start interactive elements.
        """
        self._state = ActivityState.KURAMUKA

    def on_resume(self) -> None:
        """Called when the activity comes to the foreground.

        Subclasses should override to resume animations or sensors.
        """
        self._state = ActivityState.KIGEZWEHO

    def on_pause(self) -> None:
        """Called when the activity goes to the background.

        Subclasses should override to pause ongoing work.
        """
        self._state = ActivityState.KURAHAGURIKA

    def on_stop(self) -> None:
        """Called when the activity is no longer visible.

        Subclasses should override to release heavy resources.
        """
        self._state = ActivityState.KURAHAGARARA

    def on_destroy(self) -> None:
        """Called when the activity is being destroyed.

        Subclasses should override to clean up all resources.
        """
        self._state = ActivityState.KURASENZWE
        self._views.clear()
        self._children.clear()
        self._content = None

    # -- Content and Views ----------------------------------------------------

    def set_content(self, view: Any) -> None:
        """Set the root content view for this activity.

        Args:
            view: The root view object (platform-specific).
        """
        self._content = view

    def find_view_by_id(self, view_id: str) -> Optional[Any]:
        """Find a view by its identifier within this activity.

        Args:
            view_id: The identifier of the view to find.

        Returns:
            The view if found, None otherwise.
        """
        return self._views.get(view_id)

    # -- State Persistence ----------------------------------------------------

    def save_state(self) -> Dict[str, Any]:
        """Save the current state of this activity.

        Returns:
            A dictionary representing the saved state.
        """
        self._saved_state = {
            "id": self._id,
            "title": self._title,
            "params": dict(self._params),
            "state": self._state.value,
        }
        return dict(self._saved_state)

    def restore_state(self, state: Dict[str, Any]) -> None:
        """Restore a previously saved activity state.

        Args:
            state: The state dictionary from save_state.
        """
        self._saved_state = dict(state)
        self._title = state.get("title", self._title)
        saved_params = state.get("params", {})
        if isinstance(saved_params, dict):
            self._params.update(saved_params)
        state_value = state.get("state", "")
        for s in ActivityState:
            if s.value == state_value:
                self._state = s
                break

    def add_child(self, child: Ikiganiro) -> None:
        """Add a child activity.

        Args:
            child: The child Ikiganiro to add.
        """
        if child not in self._children:
            self._children.append(child)
            child._parent = self

    def remove_child(self, child: Ikiganiro) -> None:
        """Remove a child activity.

        Args:
            child: The child Ikiganiro to remove.
        """
        if child in self._children:
            self._children.remove(child)
            child._parent = None

    def __repr__(self) -> str:
        return (
            f"Ikiganiro(id={self._id!r}, title={self._title!r}, "
            f"state={self._state.name})"
        )
