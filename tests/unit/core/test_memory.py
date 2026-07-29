"""
Tests for memory utilities.
"""

from src.compiler.core.memory import Arena, MemoryTracker, AllocationStats


class TestAllocationStats:
    """Tests for AllocationStats."""

    def test_initial(self):
        stats = AllocationStats()
        assert stats.total_allocated == 0
        assert stats.total_freed == 0
        assert stats.in_use == 0
        assert stats.peak_usage == 0

    def test_in_use(self):
        stats = AllocationStats(total_allocated=10, total_freed=3)
        assert stats.in_use == 7


class TestArena:
    """Tests for Arena."""

    def test_alloc(self):
        arena = Arena()
        obj = arena.alloc("hello")
        assert obj == "hello"
        assert len(arena) == 1

    def test_alloc_multiple(self):
        arena = Arena()
        arena.alloc(1)
        arena.alloc(2)
        arena.alloc(3)
        assert len(arena) == 3

    def test_reset(self):
        arena = Arena()
        arena.alloc("x")
        arena.alloc("y")
        arena.reset()
        assert len(arena) == 0

    def test_stats_after_alloc(self):
        arena = Arena()
        arena.alloc("a")
        arena.alloc("b")
        assert arena.stats.allocation_count == 2
        assert arena.stats.total_allocated >= 2

    def test_stats_after_reset(self):
        arena = Arena()
        arena.alloc("a")
        arena.alloc("b")
        arena.reset()
        assert arena.stats.free_count == 2
        assert arena.stats.total_freed == 2


class TestMemoryTracker:
    """Tests for MemoryTracker."""

    def test_get_arena(self):
        tracker = MemoryTracker()
        arena = tracker.get_arena("test")
        assert arena is not None
        assert isinstance(arena, Arena)

    def test_get_arena_same_name(self):
        tracker = MemoryTracker()
        a1 = tracker.get_arena("shared")
        a2 = tracker.get_arena("shared")
        assert a1 is a2

    def test_get_stats(self):
        tracker = MemoryTracker()
        arena = tracker.get_arena("main")
        arena.alloc("data")
        stats = tracker.get_stats()
        assert "main" in stats
        assert stats["main"].allocation_count == 1

    def test_reset_all(self):
        tracker = MemoryTracker()
        tracker.get_arena("a").alloc(1)
        tracker.get_arena("b").alloc(2)
        tracker.reset_all()
        assert tracker.get_arena("a").stats.free_count == 1
        assert tracker.get_arena("b").stats.free_count == 1
