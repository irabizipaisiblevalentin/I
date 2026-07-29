"""collections — Data structure operations for the I language.

Provides list, map, set, and tuple operations with functional
programming utilities (map, filter, reduce, zip, enumerate).
"""

from __future__ import annotations

import functools
import itertools
from typing import (
    Any, Callable, Dict, Hashable, Iterable, Iterator,
    List, Optional, Sequence, Set, Tuple, TypeVar, Union,
)


T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")
R = TypeVar("R")


# ---------------------------------------------------------------------------
# List operations
# ---------------------------------------------------------------------------

def list_new(*items: Any) -> List[Any]:
    """Create a new list from items."""
    return list(items)


def list_of(size: int, default: Any = None) -> List[Any]:
    """Create a list of given size with default values."""
    return [default] * size


def list_copy(lst: List[Any]) -> List[Any]:
    """Shallow copy a list."""
    return lst[:]


def list_append(lst: List[Any], value: Any) -> None:
    """Append value to list (mutates in place)."""
    lst.append(value)


def list_prepend(lst: List[Any], value: Any) -> None:
    """Prepend value to list (mutates in place)."""
    lst.insert(0, value)


def list_insert(lst: List[Any], index: int, value: Any) -> None:
    """Insert value at index (mutates in place)."""
    lst.insert(index, value)


def list_remove(lst: List[Any], value: Any) -> bool:
    """Remove first occurrence of value. Returns True if found."""
    try:
        lst.remove(value)
        return True
    except ValueError:
        return False


def list_pop(lst: List[Any], index: int = -1) -> Any:
    """Remove and return item at index. Raises IndexError if empty."""
    return lst.pop(index)


def list_contains(lst: List[Any], value: Any) -> bool:
    """Return True if value is in list."""
    return value in lst


def list_index(lst: List[Any], value: Any) -> int:
    """Return index of first occurrence. Raises ValueError if not found."""
    return lst.index(value)


def list_count(lst: List[Any], value: Any) -> int:
    """Count occurrences of value."""
    return lst.count(value)


def list_reverse(lst: List[Any]) -> List[Any]:
    """Return reversed copy."""
    return lst[::-1]


def list_reverse_mutate(lst: List[Any]) -> None:
    """Reverse list in place."""
    lst.reverse()


def list_sort(lst: List[Any], key: Optional[Callable] = None, reverse: bool = False) -> List[Any]:
    """Return sorted copy."""
    return sorted(lst, key=key, reverse=reverse)


def list_sort_mutate(lst: List[Any], key: Optional[Callable] = None, reverse: bool = False) -> None:
    """Sort list in place."""
    lst.sort(key=key, reverse=reverse)


def list_flatten(lst: List[Any]) -> List[Any]:
    """Flatten one level of nesting."""
    result: List[Any] = []
    for item in lst:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result


def list_flat_map(lst: List[Any], fn: Callable) -> List[Any]:
    """Map then flatten one level."""
    result: List[Any] = []
    for item in lst:
        mapped = fn(item)
        if isinstance(mapped, list):
            result.extend(mapped)
        else:
            result.append(mapped)
    return result


def list_unique(lst: List[Any]) -> List[Any]:
    """Remove duplicates, preserving order."""
    seen: Set[int] = set()
    result: List[Any] = []
    for item in lst:
        key = id(item) if not isinstance(item, Hashable) else hash(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def list_chunk(lst: List[Any], size: int) -> List[List[Any]]:
    """Split list into chunks of given size."""
    return [lst[i:i + size] for i in range(0, len(lst), size)]


def list_zip(*lists: List[Any]) -> List[List[Any]]:
    """Zip multiple lists together."""
    return [list(t) for t in itertools.zip_longest(*lists)]


def list_enumerate(lst: List[Any], start: int = 0) -> List[Tuple[int, Any]]:
    """Enumerate a list."""
    return list(enumerate(lst, start))


def list_slice(lst: List[Any], start: int = 0, stop: Optional[int] = None, step: int = 1) -> List[Any]:
    """Slice a list."""
    return lst[start:stop:step]


def list_rotate(lst: List[Any], n: int) -> List[Any]:
    """Rotate list by n positions."""
    if not lst:
        return []
    n = n % len(lst)
    return lst[n:] + lst[:n]


def list_sample(lst: List[Any], k: int = 1) -> List[Any]:
    """Return k random elements without replacement."""
    import random as _random
    if k > len(lst):
        raise ValueError("sample larger than population")
    return _random.sample(lst, k)


# ---------------------------------------------------------------------------
# Functional operations
# ---------------------------------------------------------------------------

def map_list(fn: Callable, lst: Iterable[Any]) -> List[Any]:
    """Map function over list."""
    return list(map(fn, lst))


def filter_list(fn: Optional[Callable], lst: Iterable[Any]) -> List[Any]:
    """Filter list by predicate. If fn is None, removes falsy values."""
    if fn is None:
        return [x for x in lst if x]
    return list(filter(fn, lst))


def reduce_list(fn: Callable, lst: Iterable[Any], initial: Any = None) -> Any:
    """Reduce list with binary function."""
    if initial is not None:
        return functools.reduce(fn, lst, initial)
    return functools.reduce(fn, lst)


def any_match(fn: Callable, lst: Iterable[Any]) -> bool:
    """Return True if any element satisfies predicate."""
    return any(fn(x) for x in lst)


def all_match(fn: Callable, lst: Iterable[Any]) -> bool:
    """Return True if all elements satisfy predicate."""
    return all(fn(x) for x in lst)


def find_first(fn: Callable, lst: Iterable[Any]) -> Any:
    """Return first element matching predicate, or None."""
    for item in lst:
        if fn(item):
            return item
    return None


def find_last(fn: Callable, lst: Iterable[Any]) -> Any:
    """Return last element matching predicate, or None."""
    result = None
    for item in lst:
        if fn(item):
            result = item
    return result


# ---------------------------------------------------------------------------
# Map (dict) operations
# ---------------------------------------------------------------------------

def map_new(**kwargs: Any) -> Dict[Any, Any]:
    """Create a new dict from keyword arguments."""
    return dict(kwargs)


def map_from_pairs(pairs: Sequence[Tuple[Any, Any]]) -> Dict[Any, Any]:
    """Create dict from list of (key, value) pairs."""
    return dict(pairs)


def map_keys(d: Dict[Any, Any]) -> List[Any]:
    """Return list of keys."""
    return list(d.keys())


def map_values(d: Dict[Any, Any]) -> List[Any]:
    """Return list of values."""
    return list(d.values())


def map_items(d: Dict[Any, Any]) -> List[Tuple[Any, Any]]:
    """Return list of (key, value) pairs."""
    return list(d.items())


def map_get(d: Dict[Any, Any], key: Any, default: Any = None) -> Any:
    """Get value by key with default."""
    return d.get(key, default)


def map_has(d: Dict[Any, Any], key: Any) -> bool:
    """Return True if key exists."""
    return key in d


def map_put(d: Dict[Any, Any], key: Any, value: Any) -> None:
    """Set key-value pair (mutates)."""
    d[key] = value


def map_remove(d: Dict[Any, Any], key: Any) -> bool:
    """Remove key. Returns True if key existed."""
    if key in d:
        del d[key]
        return True
    return False


def map_merge(a: Dict[Any, Any], b: Dict[Any, Any]) -> Dict[Any, Any]:
    """Merge two dicts (b overrides a)."""
    result = dict(a)
    result.update(b)
    return result


def map_filter(fn: Callable, d: Dict[Any, Any]) -> Dict[Any, Any]:
    """Filter dict by predicate on (key, value)."""
    return {k: v for k, v in d.items() if fn(k, v)}


def map_map_values(fn: Callable, d: Dict[Any, Any]) -> Dict[Any, Any]:
    """Map function over values."""
    return {k: fn(v) for k, v in d.items()}


# ---------------------------------------------------------------------------
# Set operations
# ---------------------------------------------------------------------------

def set_new(*items: Any) -> Set[Any]:
    """Create a new set."""
    return set(items)


def set_union(a: Set[Any], b: Set[Any]) -> Set[Any]:
    """Union of two sets."""
    return a | b


def set_intersection(a: Set[Any], b: Set[Any]) -> Set[Any]:
    """Intersection of two sets."""
    return a & b


def set_difference(a: Set[Any], b: Set[Any]) -> Set[Any]:
    """Difference (a - b)."""
    return a - b


def set_symmetric_difference(a: Set[Any], b: Set[Any]) -> Set[Any]:
    """Symmetric difference."""
    return a ^ b


def set_is_subset(a: Set[Any], b: Set[Any]) -> bool:
    """Return True if a is subset of b."""
    return a <= b


def set_is_superset(a: Set[Any], b: Set[Any]) -> bool:
    """Return True if a is superset of b."""
    return a >= b


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def group_by(lst: Iterable[T], key_fn: Callable[[T], Any]) -> Dict[Any, List[T]]:
    """Group elements by key function."""
    groups: Dict[Any, List[T]] = {}
    for item in lst:
        key = key_fn(item)
        groups.setdefault(key, []).append(item)
    return groups


def partition(lst: Iterable[T], predicate: Callable[[T], bool]) -> Tuple[List[T], List[T]]:
    """Partition into (true_list, false_list)."""
    truthy: List[T] = []
    falsy: List[T] = []
    for item in lst:
        if predicate(item):
            truthy.append(item)
        else:
            falsy.append(item)
    return truthy, falsy


def frequency(lst: Iterable[T]) -> Dict[T, int]:
    """Count frequency of each element."""
    counts: Dict[T, int] = {}
    for item in lst:
        counts[item] = counts.get(item, 0) + 1
    return counts


def sliding_window(lst: Sequence[T], size: int) -> List[Tuple[T, ...]]:
    """Generate sliding windows of given size."""
    return [tuple(lst[i:i + size]) for i in range(len(lst) - size + 1)]
