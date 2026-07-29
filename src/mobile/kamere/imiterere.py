"""Imiterere (State) generic state management class."""

from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")

OnChangeCallback = Callable[[T, T], None]


class Imiterere(Generic[T]):
    """Imiterere (State) - generic state container with observer support.

    Manages a single value of type T and notifies registered callbacks
    whenever the value changes.

    Args:
        initial_value: The initial state value.

    Example:
        >>> count = Imiterere(0)
        >>> count.set(5)
        >>> count.get()
        5
        >>> count.previous_value
        0
    """

    def __init__(self, initial_value: T) -> None:
        self._value: T = initial_value
        self._previous_value: T = initial_value
        self._observers: Dict[int, OnChangeCallback[T]] = {}
        self._next_observer_id: int = 0

    @property
    def value(self) -> T:
        """Current state value."""
        return self._value

    @value.setter
    def value(self, new_value: T) -> None:
        self.set(new_value)

    @property
    def previous_value(self) -> T:
        """The value before the most recent change."""
        return self._previous_value

    @property
    def changed(self) -> bool:
        """Whether the current value differs from the initial or last reset value."""
        return self._value != self._previous_value

    def set(self, new_value: T) -> None:
        """Set a new state value and notify observers if changed.

        Args:
            new_value: The new value to set.
        """
        if new_value != self._value:
            old_value = self._value
            self._previous_value = old_value
            self._value = new_value
            self.notify(old_value, new_value)

    def get(self) -> T:
        """Get the current state value.

        Returns:
            The current value.
        """
        return self._value

    def reset(self) -> None:
        """Reset the state to its previous value."""
        self._value = self._previous_value

    def observe(self, callback: OnChangeCallback[T]) -> int:
        """Register an observer callback for state changes.

        Args:
            callback: A callable that receives (old_value, new_value).

        Returns:
            An observer ID that can be used with unobserve().
        """
        observer_id = self._next_observer_id
        self._observers[observer_id] = callback
        self._next_observer_id += 1
        return observer_id

    def unobserve(self, observer_id: int) -> bool:
        """Remove a previously registered observer.

        Args:
            observer_id: The ID returned by observe().

        Returns:
            True if the observer was found and removed, False otherwise.
        """
        return self._observers.pop(observer_id, None) is not None

    def notify(self, old_value: T, new_value: T) -> None:
        """Notify all registered observers of a state change.

        Args:
            old_value: The previous value.
            new_value: The new value.
        """
        for callback in self._observers.values():
            callback(old_value, new_value)
