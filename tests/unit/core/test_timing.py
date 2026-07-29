"""
Tests for timing utilities.
"""

from src.compiler.core.timing import Timer, TimingCollector, TimingEntry


class TestTimer:
    """Tests for Timer."""

    def test_start_stop(self):
        timer = Timer()
        timer.start()
        timer.stop()
        assert timer.elapsed >= 0

    def test_reset(self):
        timer = Timer()
        timer.start()
        timer.stop()
        timer.reset()
        assert timer.elapsed == 0.0

    def test_elapsed_without_start(self):
        timer = Timer()
        assert timer.elapsed == 0.0

    def test_running_elapsed(self):
        timer = Timer()
        timer.start()
        elapsed = timer.elapsed
        assert elapsed >= 0

    def test_multiple_start_stop(self):
        timer = Timer()
        timer.start()
        timer.stop()
        first = timer.elapsed
        timer.start()
        timer.stop()
        assert timer.elapsed >= first


class TestTimingEntry:
    """Tests for TimingEntry."""

    def test_creation(self):
        entry = TimingEntry(name="test", elapsed=1.5)
        assert entry.name == "test"
        assert entry.elapsed == 1.5
        assert entry.count == 1

    def test_average(self):
        entry = TimingEntry(name="test", elapsed=10.0, count=5)
        assert entry.average == 2.0

    def test_average_zero_count(self):
        entry = TimingEntry(name="test", elapsed=0.0, count=0)
        assert entry.average == 0.0


class TestTimingCollector:
    """Tests for TimingCollector."""

    def test_record(self):
        collector = TimingCollector()
        collector.record("test", 1.0)
        entry = collector.get_entry("test")
        assert entry is not None
        assert entry.elapsed == 1.0

    def test_record_accumulates(self):
        collector = TimingCollector()
        collector.record("test", 1.0)
        collector.record("test", 2.0)
        entry = collector.get_entry("test")
        assert entry.elapsed == 3.0
        assert entry.count == 2

    def test_get_entries(self):
        collector = TimingCollector()
        collector.record("a", 1.0)
        collector.record("b", 2.0)
        entries = collector.get_entries()
        assert len(entries) == 2

    def test_get_entry_missing(self):
        collector = TimingCollector()
        assert collector.get_entry("missing") is None

    def test_clear(self):
        collector = TimingCollector()
        collector.record("test", 1.0)
        collector.clear()
        assert collector.get_entry("test") is None

    def test_measure(self):
        collector = TimingCollector()
        with collector.measure("block"):
            pass
        entry = collector.get_entry("block")
        assert entry is not None
        assert entry.elapsed >= 0
        assert entry.count == 1

    def test_format_report(self):
        collector = TimingCollector()
        collector.record("parse", 0.5)
        collector.record("compile", 2.0)
        report = collector.format_report()
        assert "Timing Report" in report
        assert "parse" in report
        assert "compile" in report
        assert "ms" in report
