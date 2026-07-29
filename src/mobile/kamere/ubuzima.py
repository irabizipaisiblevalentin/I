"""Ubuzima (Lifecycle-aware state) for lifecycle management."""

from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, TypeVar

T = TypeVar("T")


class Ubuzima(Enum):
    """Ubuzima (Lifecycle) states for components."""

    KUREMWE = auto()
    """"Created" - the component has been instantiated."""
    KURAMUKA = auto()
    """"Started" - the component is starting."""
    KIGEZWEHO = auto()
    """"Resumed" - the component is active and visible."""
    KURAHAGURIKA = auto()
    """"Paused" - the component is partially visible but not in focus."""
    KURAHAGARARA = auto()
    """"Stopped" - the component is no longer visible."""
    KURASENZWE = auto()
    """"Destroyed" - the component has been disposed."""


UbuzimaCallback = Callable[[], None]


class UbuzimaManager:
    """UbuzimaManager manages lifecycle state and observers.

    Args:
        initial_state: The starting lifecycle state.
    """

    def __init__(self, initial_state: Ubuzima = Ubuzima.KUREMWE) -> None:
        self._state: Ubuzima = initial_state
        self._observers: Dict[int, UbuzimaCallback] = {}
        self._state_observers: Dict[Ubuzima, List[int]] = {}
        self._next_observer_id: int = 0

    def current_state(self) -> Ubuzima:
        """Return the current lifecycle state.

        Returns:
            The current Ubuzima state.
        """
        return self._state

    def add_observer(self, callback: UbuzimaCallback) -> int:
        """Register a general observer for any lifecycle transition.

        Args:
            callback: Called on every state transition.

        Returns:
            An observer ID.
        """
        observer_id = self._next_observer_id
        self._observers[observer_id] = callback
        self._next_observer_id += 1
        return observer_id

    def remove_observer(self, observer_id: int) -> bool:
        """Remove a previously registered observer.

        Args:
            observer_id: The ID returned by add_observer().

        Returns:
            True if the observer was found and removed, False otherwise.
        """
        return self._observers.pop(observer_id, None) is not None

    def observe(self, state: Ubuzima, callback: UbuzimaCallback) -> int:
        """Register a callback for when a specific state is entered.

        Args:
            state: The state to observe.
            callback: Called when the given state is entered.

        Returns:
            An observer ID.
        """
        observer_id = self._next_observer_id
        self._observers[observer_id] = callback
        self._next_observer_id += 1
        if state not in self._state_observers:
            self._state_observers[state] = []
        self._state_observers[state].append(observer_id)
        return observer_id

    def unobserve(self, observer_id: int) -> bool:
        """Remove a state-specific observer.

        Args:
            observer_id: The ID returned by observe().

        Returns:
            True if the observer was found and removed, False otherwise.
        """
        return self.remove_observer(observer_id)

    def transition_to(self, new_state: Ubuzima) -> None:
        """Move to a new lifecycle state and notify observers.

        Args:
            new_state: The target lifecycle state.
        """
        if new_state == self._state:
            return
        self._state = new_state
        for observer in self._observers.values():
            observer()
        if new_state in self._state_observers:
            for obs_id in self._state_observers[new_state]:
                callback = self._observers.get(obs_id)
                if callback:
                    callback()


class UbuzimaAware:
    """UbuzimaAware mixin for lifecycle-aware components.

    Provides lifecycle hooks that subclasses can override to react to
    state transitions.

    Example:
        >>> class MyComponent(UbuzimaAware):
        ...     def on_create(self) -> None:
        ...         print("Component created")
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._manager: UbuzimaManager = UbuzimaManager(Ubuzima.KUREMWE)

    @property
    def ubuzima_manager(self) -> UbuzimaManager:
        """The lifecycle manager instance."""
        return self._manager

    @property
    def state(self) -> Ubuzima:
        """Current lifecycle state."""
        return self._manager.current_state()

    def on_create(self) -> None:
        """Called when the component is created (KUREMWE)."""

    def on_start(self) -> None:
        """Called when the component starts (KURAMUKA)."""

    def on_resume(self) -> None:
        """Called when the component resumes (KIGEZWEHO)."""

    def on_pause(self) -> None:
        """Called when the component is paused (KURAHAGURIKA)."""

    def on_stop(self) -> None:
        """Called when the component is stopped (KURAHAGARARA)."""

    def on_destroy(self) -> None:
        """Called when the component is destroyed (KURASENZWE)."""

    def _transition(self, new_state: Ubuzima) -> None:
        """Perform a lifecycle transition, invoking the appropriate hook.

        Args:
            new_state: The state to transition to.
        """
        hook_map: Dict[Ubuzima, Callable[[], None]] = {
            Ubuzima.KUREMWE: self.on_create,
            Ubuzima.KURAMUKA: self.on_start,
            Ubuzima.KIGEZWEHO: self.on_resume,
            Ubuzima.KURAHAGURIKA: self.on_pause,
            Ubuzima.KURAHAGARARA: self.on_stop,
            Ubuzima.KURASENZWE: self.on_destroy,
        }
        self._manager.transition_to(new_state)
        hook = hook_map.get(new_state)
        if hook:
            hook()

    def save_state(self) -> Dict[str, Any]:
        """Save the current component state for restoration.

        Override in subclasses to persist custom state.

        Returns:
            A dictionary representing the saved state.
        """
        return {
            "state": self._manager.current_state().name,
        }

    def restore_state(self, saved_state: Dict[str, Any]) -> None:
        """Restore a previously saved component state.

        Args:
            saved_state: The state dictionary from save_state().
        """
        state_name = saved_state.get("state", "KUREMWE")
        try:
            state = Ubuzima[state_name]
            self._manager = UbuzimaManager(state)
        except KeyError:
            self._manager = UbuzimaManager(Ubuzima.KUREMWE)
