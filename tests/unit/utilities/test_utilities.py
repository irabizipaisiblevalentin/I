"""
Tests for formatting, IO, memory, and timing.
"""

import time
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from src.compiler.core.formatting import MessageFormatter
from src.compiler.core.io import FileManager, normalize_path, relative_to, ensure_dir
from src.compiler.core.memory import Arena, MemoryTracker
from src.compiler.core.timing import Timer, TimingCollector
from src.compiler.core.diagnostics import Diagnostic, Severity


# ============================================================================
# MessageFormatter Tests
# ============================================================================


class TestMessageFormatter:
    """Tests for MessageFormatter."""
    
    def test_format_diagnostic(self):
        """Test formatting diagnostic."""
        formatter = MessageFormatter(use_color=False)
        diag = Diagnostic(severity=Severity.ERROR, message="Test error")
        
        result = formatter.format_diagnostic(diag)
        
        assert "ERROR" in result
        assert "Test error" in result
    
    def test_format_with_color(self):
        """Test formatting with color."""
        formatter = MessageFormatter(use_color=True)
        diag = Diagnostic(severity=Severity.ERROR, message="Test error")
        
        result = formatter.format_diagnostic(diag)
        
        assert "\033[31m" in result  # Red for errors


# ============================================================================
# FileManager Tests
# ============================================================================


class TestFileManager:
    """Tests for FileManager."""
    
    def test_read_write(self):
        """Test reading and writing files."""
        with TemporaryDirectory() as tmpdir:
            manager = FileManager(Path(tmpdir))
            
            manager.write(Path("test.txt"), "hello")
            content = manager.read(Path("test.txt"))
            
            assert content == "hello"
    
    def test_exists(self):
        """Test checking file existence."""
        with TemporaryDirectory() as tmpdir:
            manager = FileManager(Path(tmpdir))
            
            assert not manager.exists(Path("test.txt"))
            manager.write(Path("test.txt"), "hello")
            assert manager.exists(Path("test.txt"))
    
    def test_cache(self):
        """Test file caching."""
        with TemporaryDirectory() as tmpdir:
            manager = FileManager(Path(tmpdir))
            
            manager.write(Path("test.txt"), "hello")
            content1 = manager.read(Path("test.txt"))
            content2 = manager.read(Path("test.txt"))
            
            assert content1 == content2


# ============================================================================
# Path Tests
# ============================================================================


class TestPaths:
    """Tests for path utilities."""
    
    def test_normalize_path(self):
        """Test path normalization."""
        path = Path("foo") / ".." / "bar"
        normalized = normalize_path(path)
        
        assert ".." not in str(normalized)
    
    def test_relative_to(self):
        """Test relative path."""
        base = Path("/a/b")
        target = Path("/a/b/c/d")
        
        result = relative_to(target, base)
        assert result == "c/d"


# ============================================================================
# Arena Tests
# ============================================================================


class TestArena:
    """Tests for Arena."""
    
    def test_alloc(self):
        """Test allocation."""
        arena = Arena()
        
        obj = arena.alloc("test")
        
        assert obj == "test"
        assert len(arena) == 1
        assert arena.stats.allocation_count == 1
    
    def test_reset(self):
        """Test resetting arena."""
        arena = Arena()
        arena.alloc("test")
        
        arena.reset()
        
        assert len(arena) == 0
        assert arena.stats.free_count == 1


# ============================================================================
# Timer Tests
# ============================================================================


class TestTimer:
    """Tests for Timer."""
    
    def test_basic_timing(self):
        """Test basic timing."""
        timer = Timer()
        timer.start()
        time.sleep(0.01)
        elapsed = timer.stop()
        
        assert elapsed > 0
    
    def test_accumulate(self):
        """Test accumulated timing."""
        timer = Timer()
        
        timer.start()
        time.sleep(0.01)
        timer.stop()
        
        timer.start()
        time.sleep(0.01)
        timer.stop()
        
        assert timer.elapsed > 0.02


class TestTimingCollector:
    """Tests for TimingCollector."""
    
    def test_record(self):
        """Test recording timing."""
        collector = TimingCollector()
        collector.record("test", 0.1)
        
        entry = collector.get_entry("test")
        assert entry is not None
        assert entry.elapsed == 0.1
    
    def test_measure(self):
        """Test measuring context."""
        collector = TimingCollector()
        
        with collector.measure("test"):
            time.sleep(0.01)
        
        entry = collector.get_entry("test")
        assert entry is not None
        assert entry.elapsed > 0
    
    def test_format_report(self):
        """Test formatting report."""
        collector = TimingCollector()
        collector.record("fast", 0.001)
        collector.record("slow", 0.1)
        
        report = collector.format_report()
        
        assert "fast" in report
        assert "slow" in report
