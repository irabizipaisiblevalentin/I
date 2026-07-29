"""
Tests for Source Abstraction.
"""

from pathlib import Path

import pytest

from src.compiler.core.source import SourceFile, Position, Span, PositionTracker


# ============================================================================
# SourceFile Tests
# ============================================================================


class TestSourceFile:
    """Tests for SourceFile."""
    
    def test_from_string(self):
        """Test creating from string."""
        source = SourceFile.from_string("line 1\nline 2\nline 3")
        
        assert source.name == "<string>"
        assert source.line_count == 3
    
    def test_lines(self):
        """Test line access."""
        source = SourceFile.from_string("line 1\nline 2")
        
        assert len(source.lines) == 2
        assert source.get_line(1) == "line 1"
        assert source.get_line(2) == "line 2"
    
    def test_hash(self):
        """Test content hash."""
        source = SourceFile.from_string("content")
        
        assert source.hash is not None
        assert len(source.hash) == 64  # SHA-256


# ============================================================================
# Position Tests
# ============================================================================


class TestPosition:
    """Tests for Position."""
    
    def test_creation(self):
        """Test creating position."""
        pos = Position(offset=10, line=3, column=5)
        
        assert pos.offset == 10
        assert pos.line == 3
        assert pos.column == 5
    
    def test_invalid_line(self):
        """Test invalid line number."""
        with pytest.raises(ValueError):
            Position(offset=0, line=0, column=1)
    
    def test_invalid_column(self):
        """Test invalid column number."""
        with pytest.raises(ValueError):
            Position(offset=0, line=1, column=0)
    
    def test_comparison(self):
        """Test position comparison."""
        pos1 = Position(offset=0, line=1, column=1)
        pos2 = Position(offset=5, line=2, column=1)
        
        assert pos1 < pos2
        assert pos1 <= pos2
        assert pos2 > pos1
        assert pos2 >= pos1
    
    def test_str(self):
        """Test string representation."""
        pos = Position(offset=0, line=3, column=5)
        
        assert str(pos) == "3:5"


# ============================================================================
# Span Tests
# ============================================================================


class TestSpan:
    """Tests for Span."""
    
    def test_creation(self):
        """Test creating span."""
        source = SourceFile.from_string("hello world")
        start = Position(offset=0, line=1, column=1)
        end = Position(offset=5, line=1, column=6)
        
        span = Span(source=source, start=start, end=end)
        
        assert span.length == 5
        assert span.text == "hello"
    
    def test_contains(self):
        """Test position containment."""
        source = SourceFile.from_string("hello")
        start = Position(offset=0, line=1, column=1)
        end = Position(offset=5, line=1, column=6)
        span = Span(source=source, start=start, end=end)
        
        pos_in = Position(offset=2, line=1, column=3)
        pos_out = Position(offset=10, line=1, column=11)
        
        assert span.contains(pos_in)
        assert not span.contains(pos_out)
    
    def test_overlaps(self):
        """Test span overlap."""
        source = SourceFile.from_string("hello world")
        
        span1 = Span(
            source=source,
            start=Position(offset=0, line=1, column=1),
            end=Position(offset=5, line=1, column=6),
        )
        span2 = Span(
            source=source,
            start=Position(offset=3, line=1, column=4),
            end=Position(offset=8, line=1, column=9),
        )
        
        assert span1.overlaps(span2)
        assert span2.overlaps(span1)


# ============================================================================
# PositionTracker Tests
# ============================================================================


class TestPositionTracker:
    """Tests for PositionTracker."""
    
    def test_offset_to_position(self):
        """Test converting offset to position."""
        source = SourceFile.from_string("line 1\nline 2\nline 3")
        tracker = PositionTracker(source)
        
        pos = tracker.offset_to_position(8)
        
        assert pos.line == 2
        assert pos.column == 2
    
    def test_position_to_offset(self):
        """Test converting position to offset."""
        source = SourceFile.from_string("line 1\nline 2\nline 3")
        tracker = PositionTracker(source)
        
        pos = Position(offset=0, line=2, column=2)
        offset = tracker.position_to_offset(pos)
        
        assert offset == 8
    
    def test_create_span(self):
        """Test creating span from offsets."""
        source = SourceFile.from_string("hello world")
        tracker = PositionTracker(source)
        
        span = tracker.create_span(0, 5)
        
        assert span.text == "hello"
        assert span.start.line == 1
        assert span.end.line == 1
