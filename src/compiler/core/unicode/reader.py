"""
UTF-8 Reader

Provides streaming UTF-8 character reading.
"""

from __future__ import annotations

from typing import Optional


class UTF8Reader:
    """
    Streaming UTF-8 character reader.
    
    Reads characters from a string with position tracking.
    """
    
    def __init__(self, content: str) -> None:
        """
        Initialize reader.
        
        Args:
            content: Input string
        """
        self._content = content
        self._pos = 0
        self._line = 1
        self._column = 1
    
    @property
    def position(self) -> int:
        """Current byte offset."""
        return self._pos
    
    @property
    def line(self) -> int:
        """Current line number (1-indexed)."""
        return self._line
    
    @property
    def column(self) -> int:
        """Current column number (1-indexed)."""
        return self._column
    
    @property
    def is_eof(self) -> bool:
        """Check if at end of input."""
        return self._pos >= len(self._content)
    
    @property
    def remaining(self) -> int:
        """Number of characters remaining."""
        return len(self._content) - self._pos
    
    def peek(self, offset: int = 0) -> Optional[str]:
        """
        Peek at character without consuming.
        
        Args:
            offset: Offset from current position
            
        Returns:
            Character or None at EOF
        """
        pos = self._pos + offset
        if pos >= len(self._content):
            return None
        return self._content[pos]
    
    def read(self) -> Optional[str]:
        """
        Read and consume next character.
        
        Returns:
            Character or None at EOF
        """
        if self.is_eof:
            return None
        
        char = self._content[self._pos]
        self._pos += 1
        
        if char == "\n":
            self._line += 1
            self._column = 1
        else:
            self._column += 1
        
        return char
    
    def read_while(self, predicate) -> str:
        """
        Read characters while predicate is true.
        
        Args:
            predicate: Function taking char, returning bool
            
        Returns:
            Read string
        """
        result = []
        while not self.is_eof:
            char = self.peek()
            if char is None or not predicate(char):
                break
            result.append(self.read())
        return "".join(result)
    
    def read_until(self, target: str) -> str:
        """
        Read until target character.
        
        Args:
            target: Target character
            
        Returns:
            Read string (not including target)
        """
        result = []
        while not self.is_eof:
            char = self.peek()
            if char == target:
                break
            result.append(self.read())
        return "".join(result)
    
    def skip(self, count: int = 1) -> None:
        """
        Skip characters.
        
        Args:
            count: Number of characters to skip
        """
        for _ in range(count):
            self.read()
    
    def save(self) -> int:
        """Save current position."""
        return self._pos
    
    def restore(self, position: int) -> None:
        """Restore saved position."""
        self._pos = position
        self._recalculate_position()
    
    def _recalculate_position(self) -> None:
        """Recalculate line and column from position."""
        self._line = 1
        self._column = 1
        for i in range(self._pos):
            if self._content[i] == "\n":
                self._line += 1
                self._column = 1
            else:
                self._column += 1
