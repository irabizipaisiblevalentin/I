"""
Core Utilities

Provides common utility functions for the I compiler.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator
from typing import Any, TypeVar

T = TypeVar("T")
U = TypeVar("U")


def clamp[T](value: T, min_value: T, max_value: T) -> T:
    """
    Clamp a value between min and max.

    Args:
        value: Value to clamp
        min_value: Minimum bound
        max_value: Maximum bound

    Returns:
        Clamped value
    """
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def group_by[T, U](items: list[T], key_fn: Callable[[T], U]) -> dict[U, list[T]]:
    """
    Group items by a key function.

    Args:
        items: Items to group
        key_fn: Key extraction function

    Returns:
        Dictionary mapping keys to item lists
    """
    result: dict[U, list[T]] = {}
    for item in items:
        key = key_fn(item)
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result


def unique[T](items: list[T]) -> list[T]:
    """
    Return unique items preserving order.

    Args:
        items: Items to deduplicate

    Returns:
        Deduplicated list
    """
    seen: set[T] = set()
    result: list[T] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def flatten[T](items: list[list[T]]) -> list[T]:
    """
    Flatten a list of lists.

    Args:
        items: Nested list

    Returns:
        Flattened list
    """
    return [item for sublist in items for item in sublist]


def chunks[T](items: list[T], size: int) -> Iterator[list[T]]:
    """
    Split list into chunks.

    Args:
        items: List to split
        size: Chunk size

    Yields:
        Chunks of the list
    """
    for i in range(0, len(items), size):
        yield items[i:i + size]


def find[T](items: list[T], predicate: Callable[[T], bool]) -> T | None:
    """
    Find first item matching predicate.

    Args:
        items: Items to search
        predicate: Match function

    Returns:
        First match or None
    """
    for item in items:
        if predicate(item):
            return item
    return None


def find_index[T](items: list[T], predicate: Callable[[T], bool]) -> int:
    """
    Find index of first item matching predicate.

    Args:
        items: Items to search
        predicate: Match function

    Returns:
        Index or -1
    """
    for i, item in enumerate(items):
        if predicate(item):
            return i
    return -1


def partition[T](items: list[T], predicate: Callable[[T], bool]) -> tuple[list[T], list[T]]:
    """
    Partition items by predicate.

    Args:
        items: Items to partition
        predicate: Partition function

    Returns:
        Tuple of (matching, non-matching)
    """
    matched: list[T] = []
    unmatched: list[T] = []
    for item in items:
        if predicate(item):
            matched.append(item)
        else:
            unmatched.append(item)
    return matched, unmatched


def merge_dicts(*dicts: dict[str, Any]) -> dict[str, Any]:
    """
    Merge dictionaries (later keys override earlier).

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Merged dictionary
    """
    result: dict[str, Any] = {}
    for d in dicts:
        result.update(d)
    return result


def camel_to_snake(name: str) -> str:
    """
    Convert CamelCase to snake_case.

    Args:
        name: CamelCase string

    Returns:
        snake_case string
    """
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s2 = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def snake_to_camel(name: str) -> str:
    """
    Convert snake_case to CamelCase.

    Args:
        name: snake_case string

    Returns:
        CamelCase string
    """
    return "".join(word.capitalize() for word in name.split("_"))


def pluralize(count: int, singular: str, plural: str | None = None) -> str:
    """
    Pluralize word based on count.

    Args:
        count: Item count
        singular: Singular form
        plural: Plural form (default: singular + 's')

    Returns:
        Properly pluralized word
    """
    if count == 1:
        return singular
    return plural or (singular + "s")


def format_bytes(size: int) -> str:
    """
    Format byte size as human-readable string.

    Args:
        size: Size in bytes

    Returns:
        Human-readable size string
    """
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}PB"


def format_duration(seconds: float) -> str:
    """
    Format duration as human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Human-readable duration string
    """
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.0f}us"
    if seconds < 1:
        return f"{seconds * 1_000:.1f}ms"
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes = int(seconds // 60)
    secs = seconds - minutes * 60
    return f"{minutes}m {secs:.1f}s"


__all__ = [
    "clamp",
    "group_by",
    "unique",
    "flatten",
    "chunks",
    "find",
    "find_index",
    "partition",
    "merge_dicts",
    "camel_to_snake",
    "snake_to_camel",
    "pluralize",
    "format_bytes",
    "format_duration",
]
