"""
Source File Abstraction

Represents source files with metadata and content access.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


@dataclass
class SourceFile:
    """
    Represents a source file.
    
    Provides unified access to file content with metadata.
    """
    
    path: Path
    content: str
    encoding: str = "utf-8"
    timestamp: datetime = field(default_factory=datetime.now)
    _lines: Optional[List[str]] = field(default=None, repr=False)
    _hash: Optional[str] = field(default=None, repr=False)
    
    @classmethod
    def from_path(cls, path: Path, encoding: str = "utf-8") -> SourceFile:
        """
        Load source file from path.
        
        Args:
            path: File path
            encoding: File encoding
            
        Returns:
            SourceFile instance
        """
        content = path.read_text(encoding=encoding)
        stat = path.stat()
        
        return cls(
            path=path,
            content=content,
            encoding=encoding,
            timestamp=datetime.fromtimestamp(stat.st_mtime),
        )
    
    @classmethod
    def from_string(cls, content: str, path: Optional[Path] = None) -> SourceFile:
        """
        Create source file from string.
        
        Args:
            content: File content
            path: Optional path
            
        Returns:
            SourceFile instance
        """
        return cls(
            path=path or Path("<string>"),
            content=content,
        )
    
    @property
    def name(self) -> str:
        """File name."""
        return self.path.name
    
    @property
    def lines(self) -> List[str]:
        """File lines (cached)."""
        if self._lines is None:
            self._lines = self.content.splitlines(True)
        return self._lines
    
    def get_line(self, line_number: int) -> str:
        """
        Get line by number (1-indexed), stripping trailing newline.
        
        Args:
            line_number: Line number
            
        Returns:
            Line content without trailing newline
        """
        if line_number < 1 or line_number > self.line_count:
            raise IndexError(f"Line {line_number} out of range")
        return self.lines[line_number - 1].rstrip("\n\r")
    
    @property
    def line_count(self) -> int:
        """Number of lines."""
        return len(self.lines)
    
    @property
    def hash(self) -> str:
        """Content hash (cached)."""
        if self._hash is None:
            self._hash = hashlib.sha256(self.content.encode()).hexdigest()
        return self._hash
    
    def get_lines(self, start: int, end: int) -> List[str]:
        """
        Get range of lines (1-indexed, inclusive).
        
        Args:
            start: Start line
            end: End line
            
        Returns:
            List of lines
        """
        return self.lines[start - 1:end]
    
    def __len__(self) -> int:
        return len(self.content)
    
    def __str__(self) -> str:
        return f"SourceFile({self.path})"
