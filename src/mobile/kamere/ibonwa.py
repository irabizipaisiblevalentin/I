"""Ibonwa (Observable) reactive state with computed and dependent state support."""

from typing import (Any, Callable, Dict, Generic, List, Optional, Set, Tuple,
                    TypeVar)

from .imiterere import Imiterere, OnChangeCallback

T = TypeVar("T")
U = TypeVar("U")


class Ibonwa(Imiterere[T]):
    """Ibonwa (Observable) - reactive state with computed/dependent state.

    Extends Imiterere with lazy computed values and condition-based triggers.

    Args:
        initial_value: The initial state value.
        dependencies: Optional list of observed dependencies.
        lazy: Whether computation is deferred until value is accessed.
    """

    def __init__(
        self,
        initial_value: T,
        dependencies: Optional[List[Imiterere[Any]]] = None,
        lazy: bool = True,
    ) -> None:
        super().__init__(initial_value)
        self._observers: Dict[int, OnChangeCallback[T]] = {}
        self._dependencies: List[Imiterere[Any]] = dependencies or []
        self._computed: bool = False
        self._lazy: bool = lazy
        self._compute_fn: Optional[Callable[..., T]] = None
        self._when_conditions: List[Tuple[Callable[[T], bool], Callable[[T], None]]] = []
        self._dependency_observers: Dict[int, int] = {}
        self._setup_dependency_tracking()

    @property
    def observers(self) -> Dict[int, OnChangeCallback[T]]:
        """Registered observer callbacks."""
        return self._observers

    @property
    def dependencies(self) -> List[Imiterere[Any]]:
        """List of observed dependencies."""
        return self._dependencies

    @property
    def computed(self) -> bool:
        """Whether this observable uses a computed value."""
        return self._computed

    @property
    def lazy(self) -> bool:
        """Whether computation is deferred until value is accessed."""
        return self._lazy

    def _setup_dependency_tracking(self) -> None:
        """Set up internal observers for each dependency."""
        for dep in self._dependencies:
            observer_id = self._next_observer_id
            self._next_observer_id += 1
            dep_obs_id = dep.observe(lambda old, new, oid=observer_id: self._on_dependency_changed(oid))
            self._dependency_observers[observer_id] = dep_obs_id

    def _on_dependency_changed(self, observer_id: int) -> None:
        """Handle a change in one of the dependencies."""
        if not self._lazy:
            self.compute()

    def subscribe(self, callback: OnChangeCallback[T]) -> int:
        """Subscribe a callback for state changes.

        Args:
            callback: A callable that receives (old_value, new_value).

        Returns:
            A subscription ID.
        """
        return self.observe(callback)

    def unsubscribe(self, observer_id: int) -> bool:
        """Unsubscribe a previously registered callback.

        Args:
            observer_id: The ID returned by subscribe().

        Returns:
            True if the observer was found and removed, False otherwise.
        """
        return self.unobserve(observer_id)

    def compute(self, fn: Optional[Callable[..., T]] = None) -> T:
        """Compute or recompute the value using the provided function.

        If no function is provided, uses the previously set compute function.

        Args:
            fn: A function that computes a new value from dependencies.

        Returns:
            The computed value.
        """
        if fn is not None:
            self._compute_fn = fn
            self._computed = True
        if self._compute_fn is not None:
            dep_values = [dep.get() for dep in self._dependencies]
            new_value = self._compute_fn(*dep_values)
            super().set(new_value)
        return self.get()

    def when(
        self, condition: Callable[[T], bool], callback: Callable[[T], None]
    ) -> Callable[[], None]:
        """Register a condition-based trigger.

        The callback is invoked whenever the condition evaluates to True
        after a state change.

        Args:
            condition: A function that takes the current value and returns bool.
            callback: A function to invoke when the condition is met.

        Returns:
            A function to cancel the when trigger.
        """
        entry = (condition, callback)
        self._when_conditions.append(entry)

        def cancel() -> None:
            try:
                self._when_conditions.remove(entry)
            except ValueError:
                pass

        return cancel

    def notify(self, old_value: T, new_value: T) -> None:
        """Notify observers and evaluate when conditions.

        Args:
            old_value: The previous value.
            new_value: The new value.
        """
        super().notify(old_value, new_value)
        for condition, callback in self._when_conditions:
            if condition(new_value):
                callback(new_value)


class IbonwaOrutonde(Imiterere[List[T]]):
    """IbonwaOrutonde (ObservableList) - reactive list with change tracking.

    Provides list mutation methods that trigger state change notifications.

    Args:
        initial_items: Initial list of items.
    """

    def __init__(self, initial_items: Optional[List[T]] = None) -> None:
        super().__init__(initial_items if initial_items is not None else [])

    def append(self, item: T) -> None:
        """Append an item to the list.

        Args:
            item: The item to append.
        """
        new_list = self._value.copy()
        new_list.append(item)
        self.set(new_list)

    def insert(self, index: int, item: T) -> None:
        """Insert an item at the specified index.

        Args:
            index: The position to insert at.
            item: The item to insert.
        """
        new_list = self._value.copy()
        new_list.insert(index, item)
        self.set(new_list)

    def remove(self, item: T) -> bool:
        """Remove the first occurrence of an item.

        Args:
            item: The item to remove.

        Returns:
            True if the item was found and removed, False otherwise.
        """
        try:
            new_list = self._value.copy()
            new_list.remove(item)
            self.set(new_list)
            return True
        except ValueError:
            return False

    def pop(self, index: int = -1) -> T:
        """Remove and return an item at the given index.

        Args:
            index: The index to pop from (default last).

        Returns:
            The removed item.
        """
        new_list = self._value.copy()
        result = new_list.pop(index)
        self.set(new_list)
        return result

    def clear(self) -> None:
        """Remove all items from the list."""
        self.set([])

    def extend(self, items: List[T]) -> None:
        """Extend the list with additional items.

        Args:
            items: Items to append.
        """
        new_list = self._value.copy()
        new_list.extend(items)
        self.set(new_list)

    def sort(self, key: Optional[Callable[[T], Any]] = None, reverse: bool = False) -> None:
        """Sort the list in place.

        Args:
            key: Key function for sorting.
            reverse: Whether to sort in reverse order.
        """
        new_list = self._value.copy()
        new_list.sort(key=key, reverse=reverse)
        self.set(new_list)

    def filter(self, predicate: Callable[[T], bool]) -> "IbonwaOrutonde[T]":
        """Create a new ObservableList filtered by predicate.

        Args:
            predicate: Filter function.

        Returns:
            A new ObservableList with filtered items.
        """
        return IbonwaOrutonde([item for item in self._value if predicate(item)])

    def map(self, transform: Callable[[T], U]) -> "IbonwaOrutonde[U]":
        """Create a new ObservableList with transformed items.

        Args:
            transform: Transform function.

        Returns:
            A new ObservableList with transformed items.
        """
        return IbonwaOrutonde([transform(item) for item in self._value])

    def __getitem__(self, index: int) -> T:
        return self._value[index]

    def __setitem__(self, index: int, value: T) -> None:
        new_list = self._value.copy()
        new_list[index] = value
        self.set(new_list)

    def __len__(self) -> int:
        return len(self._value)

    def __iter__(self):
        return iter(self._value)


class IbonwaInzuzi(Imiterere[Dict[Any, T]]):
    """IbonwaInzuzi (ObservableMap) - reactive dictionary with change tracking.

    Args:
        initial_items: Initial dictionary of items.
    """

    def __init__(self, initial_items: Optional[Dict[Any, T]] = None) -> None:
        super().__init__(initial_items if initial_items is not None else {})

    def set_item(self, key: Any, value: T) -> None:
        """Set a key-value pair.

        Args:
            key: The key to set.
            value: The value to associate.
        """
        new_dict = self._value.copy()
        new_dict[key] = value
        self.set(new_dict)

    def get_item(self, key: Any, default: Optional[T] = None) -> Optional[T]:
        """Get a value by key.

        Args:
            key: The key to look up.
            default: Value returned if key is not found.

        Returns:
            The value associated with the key, or default.
        """
        return self._value.get(key, default)

    def remove_item(self, key: Any) -> bool:
        """Remove a key-value pair by key.

        Args:
            key: The key to remove.

        Returns:
            True if the key was found and removed, False otherwise.
        """
        if key in self._value:
            new_dict = self._value.copy()
            del new_dict[key]
            self.set(new_dict)
            return True
        return False

    def clear(self) -> None:
        """Remove all entries from the map."""
        self.set({})

    def update(self, other: Dict[Any, T]) -> None:
        """Update the map with key-value pairs from another dict.

        Args:
            other: Dictionary of items to merge in.
        """
        new_dict = self._value.copy()
        new_dict.update(other)
        self.set(new_dict)

    def keys(self) -> Set[Any]:
        """Return the set of keys in the map."""
        return set(self._value.keys())

    def values(self) -> List[T]:
        """Return the list of values in the map."""
        return list(self._value.values())

    def __getitem__(self, key: Any) -> T:
        return self._value[key]

    def __setitem__(self, key: Any, value: T) -> None:
        self.set_item(key, value)

    def __delitem__(self, key: Any) -> None:
        self.remove_item(key)

    def __len__(self) -> int:
        return len(self._value)

    def __contains__(self, key: Any) -> bool:
        return key in self._value
