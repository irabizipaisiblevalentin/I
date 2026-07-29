"""
Memory Utilities

Arena allocator and memory tracking.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AllocationStats:
    """Memory allocation statistics."""

    total_allocated: int = 0
    total_freed: int = 0
    allocation_count: int = 0
    free_count: int = 0

    @property
    def in_use(self) -> int:
        """Bytes currently in use."""
        return self.total_allocated - self.total_freed

    @property
    def peak_usage(self) -> int:
        """Peak memory usage."""
        return self.total_allocated


class Arena:
    """
    Simple arena allocator.

    Allocates memory in bulk and frees everything at once.
    """

    def __init__(self) -> None:
        self._objects: list[Any] = []
        self._stats = AllocationStats()

    @property
    def stats(self) -> AllocationStats:
        """Allocation statistics."""
        return self._stats

    def alloc(self, obj: Any) -> Any:
        """
        Allocate an object.

        Args:
            obj: Object to allocate

        Returns:
            The allocated object
        """
        self._objects.append(obj)
        self._stats.allocation_count += 1
        self._stats.total_allocated += 1
        return obj

    def reset(self) -> None:
        """Free all allocated objects."""
        count = len(self._objects)
        self._objects.clear()
        self._stats.free_count += count
        self._stats.total_freed += count

    def __len__(self) -> int:
        return len(self._objects)


class MemoryTracker:
    """
    Tracks memory usage.
    """

    def __init__(self) -> None:
        self._arenas: dict[str, Arena] = {}

    def get_arena(self, name: str) -> Arena:
        """
        Get or create named arena.

        Args:
            name: Arena name

        Returns:
            Arena instance
        """
        if name not in self._arenas:
            self._arenas[name] = Arena()
        return self._arenas[name]

    def get_stats(self) -> dict[str, AllocationStats]:
        """Get stats for all arenas."""
        return {name: arena.stats for name, arena in self._arenas.items()}

    def reset_all(self) -> None:
        """Reset all arenas."""
        for arena in self._arenas.values():
            arena.reset()
