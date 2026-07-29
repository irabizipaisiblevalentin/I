"""
Path resolution utilities.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Optional


class PathResolver:
    """
    Resolves paths relative to workspace root.
    
    Provides consistent path resolution across platforms
    and handles both absolute and relative paths.
    """
    
    def __init__(self, root: Path) -> None:
        """
        Initialize path resolver.
        
        Args:
            root: Workspace root directory
        """
        self._root = root.resolve()
    
    @property
    def root(self) -> Path:
        """Workspace root directory."""
        return self._root
    
    def resolve(self, path: str) -> Path:
        """
        Resolve path relative to workspace root.
        
        If path is absolute, it is returned as-is (after resolution).
        If path is relative, it is resolved relative to workspace root.
        
        Args:
            path: Path to resolve
            
        Returns:
            Resolved absolute path
        """
        p = Path(path)
        
        if p.is_absolute():
            return p.resolve()
        
        return (self._root / p).resolve()
    
    def relative(self, path: Path) -> PurePosixPath:
        """
        Make path relative to workspace root.
        
        Args:
            path: Absolute path
            
        Returns:
            Relative path as PurePosixPath
        """
        try:
            return PurePosixPath(path.resolve().relative_to(self._root))
        except ValueError:
            # Path is not relative to root, return as-is
            return PurePosixPath(path)
    
    def canonical(self, path: Path) -> Path:
        """
        Get canonical path.
        
        Resolves symlinks and normalizes path.
        
        Args:
            path: Path to canonicalize
            
        Returns:
            Canonical path
        """
        try:
            return path.resolve()
        except (OSError, ValueError):
            # If resolution fails, return normalized path
            return path.absolute()
    
    def is_relative_to(self, path: Path) -> bool:
        """
        Check if path is relative to workspace root.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is within workspace
        """
        try:
            path.resolve().relative_to(self._root)
            return True
        except ValueError:
            return False
    
    def ensure_relative(self, path: Path) -> Path:
        """
        Ensure path is relative to workspace root.
        
        If path is absolute and within workspace, make it relative.
        Otherwise, return as-is.
        
        Args:
            path: Path to make relative
            
        Returns:
            Path relative to workspace root
        """
        resolved = path.resolve()
        
        if self.is_relative_to(resolved):
            return resolved.relative_to(self._root)
        
        return resolved
    
    def join(self, *parts: str) -> Path:
        """
        Join path parts relative to workspace root.
        
        Args:
            *parts: Path parts to join
            
        Returns:
            Joined path
        """
        return self._root.joinpath(*parts)
    
    def exists(self, path: str) -> bool:
        """
        Check if path exists relative to workspace root.
        
        Args:
            path: Path to check
            
        Returns:
            True if path exists
        """
        return self.resolve(path).exists()
    
    def is_file(self, path: str) -> bool:
        """
        Check if path is a file relative to workspace root.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is a file
        """
        return self.resolve(path).is_file()
    
    def is_dir(self, path: str) -> bool:
        """
        Check if path is a directory relative to workspace root.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is a directory
        """
        return self.resolve(path).is_dir()
