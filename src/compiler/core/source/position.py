"""
Source Position and Span Tracking
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .file import SourceFile


@dataclass(frozen=True)
class Position:
    """
    Position in source file.
    
    Immutable value type representing a single point in source code.
    """
    
    offset: int
    line: int
    column: int
    
    def __post_init__(self) -> None:
        if self.line < 1:
            raise ValueError(f"Line must be >= 1, got {self.line}")
        if self.column < 1:
            raise ValueError(f"Column must be >= 1, got {self.column}")
        if self.offset < 0:
            raise ValueError(f"Offset must be >= 0, got {self.offset}")
    
    def __str__(self) -> str:
        return f"{self.line}:{self.column}"
    
    def __lt__(self, other: Position) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return (self.line, self.column) < (other.line, other.column)
    
    def __le__(self, other: Position) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return (self.line, self.column) <= (other.line, other.column)
    
    def __gt__(self, other: Position) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return (self.line, self.column) > (other.line, other.column)
    
    def __ge__(self, other: Position) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return (self.line, self.column) >= (other.line, other.column)


@dataclass(frozen=True)
class Span:
    """
    Span of source code.
    
    Represents a range in a source file from start to end.
    """
    
    source: SourceFile
    start: Position
    end: Position
    
    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("End position must be >= start position")
    
    @property
    def length(self) -> int:
        """Span length in characters."""
        return self.end.offset - self.start.offset
    
    @property
    def text(self) -> str:
        """Text content of span."""
        return self.source.content[self.start.offset:self.end.offset]
    
    @property
    def line_count(self) -> int:
        """Number of lines in span."""
        return self.end.line - self.start.line + 1
    
    def contains(self, position: Position) -> bool:
        """
        Check if span contains a position.
        
        Args:
            position: Position to check
            
        Returns:
            True if position is within span
        """
        return self.start <= position <= self.end
    
    def overlaps(self, other: Span) -> bool:
        """
        Check if span overlaps with another.
        
        Args:
            other: Other span
            
        Returns:
            True if spans overlap
        """
        return self.start <= other.end and other.start <= self.end
    
    def __str__(self) -> str:
        return f"{self.source.name}:{self.start}-{self.end}"
    
    def __repr__(self) -> str:
        return (
            f"Span(source={self.source.name}, "
            f"start={self.start}, end={self.end})"
        )


class PositionTracker:
    """
    Tracks positions in a source file.
    
    Converts byte offsets to line:column positions.
    """
    
    def __init__(self, source: SourceFile) -> None:
        """
        Initialize tracker.
        
        Args:
            source: Source file
        """
        self._source = source
        self._line_starts: Optional[list[int]] = None
    
    def _build_line_starts(self) -> None:
        """Build line start offsets."""
        self._line_starts = [0]
        for i, char in enumerate(self._source.content):
            if char == "\n":
                self._line_starts.append(i + 1)
    
    @property
    def line_starts(self) -> list[int]:
        """Line start offsets."""
        if self._line_starts is None:
            self._build_line_starts()
        return self._line_starts
    
    def offset_to_position(self, offset: int) -> Position:
        """
        Convert byte offset to position.
        
        Args:
            offset: Byte offset
            
        Returns:
            Position
        """
        if offset < 0 or offset > len(self._source.content):
            raise ValueError(f"Offset {offset} out of range")
        
        # Binary search for line
        lo, hi = 0, len(self.line_starts) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if self.line_starts[mid] <= offset:
                lo = mid + 1
            else:
                hi = mid
        
        line = lo
        if line > 0 and self.line_starts[line] > offset:
            line -= 1
        
        column = offset - self.line_starts[line] + 1
        
        return Position(offset=offset, line=line + 1, column=column)
    
    def position_to_offset(self, position: Position) -> int:
        """
        Convert position to byte offset.
        
        Args:
            position: Position
            
        Returns:
            Byte offset
        """
        if position.line < 1 or position.line > len(self.line_starts):
            raise ValueError(f"Line {position.line} out of range")
        
        return self.line_starts[position.line - 1] + position.column - 1
    
    def create_span(
        self,
        start_offset: int,
        end_offset: int,
    ) -> Span:
        """
        Create span from offsets.
        
        Args:
            start_offset: Start byte offset
            end_offset: End byte offset
            
        Returns:
            Span
        """
        return Span(
            source=self._source,
            start=self.offset_to_position(start_offset),
            end=self.offset_to_position(end_offset),
        )
