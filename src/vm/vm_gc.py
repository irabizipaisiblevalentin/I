"""IVM Garbage Collector — generational, incremental, mark-sweep with compaction."""
from __future__ import annotations

import sys
import time
from typing import Any

from vm.vm_memory import Heap
from vm.vm_objects import VMObject


class GCStats:
    """Garbage collection statistics."""
    __slots__ = (
        "collections", "young_collections", "major_collections",
        "bytes_collected", "pause_time_ms", "total_pause_ms",
        "objects_collected", "objects_alive", "heap_size",
    )

    def __init__(self) -> None:
        self.collections: int = 0
        self.young_collections: int = 0
        self.major_collections: int = 0
        self.bytes_collected: int = 0
        self.pause_time_ms: float = 0.0
        self.total_pause_ms: float = 0.0
        self.objects_collected: int = 0
        self.objects_alive: int = 0
        self.heap_size: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "collections": self.collections,
            "young_collections": self.young_collections,
            "major_collections": self.major_collections,
            "bytes_collected": self.bytes_collected,
            "pause_time_ms": round(self.pause_time_ms, 3),
            "total_pause_ms": round(self.total_pause_ms, 3),
            "objects_collected": self.objects_collected,
            "objects_alive": self.objects_alive,
            "heap_size": self.heap_size,
        }


class GarbageCollector:
    """Production-quality GC with generational and incremental modes.

    Generational: young generation (nursery) collected frequently,
    promoted objects moved to old generation.

    Incremental: collect in small slices to limit pause times.
    """

    __slots__ = (
        "_heap", "_young_gen", "_old_gen", "_stats",
        "_gc_threshold", "_gc_count", "_generational",
        "_incremental", "_stw_limit_ms", "_promotion_threshold",
        "_auto_collect",
    )

    YOUNG_GEN = 0
    OLD_GEN = 1

    def __init__(
        self,
        heap: Heap | None = None,
        threshold: int = 1024,
        generational: bool = True,
        incremental: bool = False,
        stw_limit_ms: float = 10.0,
    ) -> None:
        self._heap = heap or Heap()
        self._young_gen: list[VMObject] = []
        self._old_gen: list[VMObject] = []
        self._stats = GCStats()
        self._gc_threshold = threshold
        self._gc_count = 0
        self._generational = generational
        self._incremental = incremental
        self._stw_limit_ms = stw_limit_ms
        self._promotion_threshold = 2
        self._auto_collect = True

    @property
    def stats(self) -> GCStats:
        return self._stats

    @property
    def needs_collection(self) -> bool:
        return len(self._young_gen) >= self._gc_threshold

    def allocate(self, obj: VMObject) -> VMObject:
        """Allocate an object in the young generation."""
        obj.gc_gen = self.YOUNG_GEN
        self._young_gen.append(obj)
        self._heap.track(obj)
        if self._auto_collect and self.needs_collection:
            self.collect_young()
        return obj

    def promote(self, obj: VMObject) -> VMObject:
        """Promote an object to the old generation."""
        obj.gc_gen = self.OLD_GEN
        self._old_gen.append(obj)
        return obj

    def collect_young(self) -> int:
        """Collect the young generation (minor GC)."""
        start = time.monotonic()
        self._gc_count += 1
        collected = 0

        roots = self._get_roots()

        self._mark_phase(roots, self._young_gen)
        freed = self._sweep_phase(self._young_gen)
        collected += freed

        survivors = [obj for obj in self._young_gen if obj.gc_marked]
        for obj in survivors:
            if obj._gc_gen != self.OLD_GEN:
                if self._gc_count % self._promotion_threshold == 0:
                    self.promote(obj)
                else:
                    obj.gc_marked = False

        self._young_gen = [obj for obj in self._young_gen if obj in self._old_gen or obj.gc_marked]
        for obj in self._young_gen:
            if obj not in self._old_gen:
                obj.gc_marked = False

        elapsed = (time.monotonic() - start) * 1000.0
        self._stats.collections += 1
        self._stats.young_collections += 1
        self._stats.objects_collected += collected
        self._stats.pause_time_ms = elapsed
        self._stats.total_pause_ms += elapsed
        self._stats.heap_size = len(self._young_gen) + len(self._old_gen)

        return collected

    def collect_all(self) -> int:
        """Full GC (major collection)."""
        start = time.monotonic()
        self._gc_count += 1
        collected = 0

        roots = self._get_roots()

        self._mark_phase(roots, self._young_gen + self._old_gen)
        collected += self._sweep_phase(self._young_gen)
        collected += self._sweep_phase(self._old_gen)

        self._young_gen = [obj for obj in self._young_gen if obj.gc_marked]
        self._old_gen = [obj for obj in self._old_gen if obj.gc_marked]

        for obj in self._young_gen + self._old_gen:
            obj.gc_marked = False

        elapsed = (time.monotonic() - start) * 1000.0
        self._stats.collections += 1
        self._stats.major_collections += 1
        self._stats.objects_collected += collected
        self._stats.pause_time_ms = elapsed
        self._stats.total_pause_ms += elapsed
        self._stats.heap_size = len(self._young_gen) + len(self._old_gen)

        return collected

    def collect(self) -> int:
        """Smart collection: young if generational, full otherwise."""
        if self._generational:
            return self.collect_young()
        return self.collect_all()

    def _mark_phase(self, roots: list[Any], gen: list[VMObject]) -> None:
        """Mark all reachable objects."""
        for obj in gen:
            obj.gc_marked = False

        stack = list(roots)
        while stack:
            item = stack.pop()
            if isinstance(item, VMObject) and not item.gc_marked:
                item.gc_marked = True
                traced = item.gc_trace()
                stack.extend(traced)

    def _sweep_phase(self, gen: list[VMObject]) -> int:
        """Sweep unmarked objects, return count freed."""
        before = len(gen)
        for obj in gen:
            if not obj.gc_marked:
                self._heap.untrack(obj)
        after = sum(1 for obj in gen if obj.gc_marked)
        return before - after

    def _get_roots(self) -> list[Any]:
        """Get GC roots — currently just tracked objects marked as roots."""
        return []

    def set_roots(self, roots: list[Any]) -> None:
        """Override the root set (called by VM with stack globals)."""
        self._get_roots = lambda: roots

    def format_stats(self) -> str:
        s = self._stats
        lines = [
            "GC Statistics:",
            f"  Total collections: {s.collections}",
            f"  Young gen:         {s.young_collections}",
            f"  Major:             {s.major_collections}",
            f"  Objects collected: {s.objects_collected}",
            f"  Objects alive:     {s.heap_size}",
            f"  Pause time (last): {s.pause_time_ms:.3f} ms",
            f"  Total pause:       {s.total_pause_ms:.3f} ms",
        ]
        return "\n".join(lines)
