"""
Path utilities.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Optional


def normalize_path(path: Path) -> Path:
    """
    Normalize a path.
    
    Args:
        path: Path to normalize
        
    Returns:
        Normalized path
    """
    return path.resolve()


def relative_to(path: Path, base: Path) -> str:
    """
    Get relative path as string.
    
    Args:
        path: Target path
        base: Base path
        
    Returns:
        Relative path string (using forward slashes)
    """
    try:
        rel = path.relative_to(base)
        return str(PurePosixPath(rel))
    except ValueError:
        return str(PurePosixPath(path))


def ensure_dir(path: Path) -> Path:
    """
    Ensure directory exists.
    
    Args:
        path: Directory path
        
    Returns:
        The directory path
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def find_project_root(start: Path) -> Optional[Path]:
    """
    Find project root by looking for marker files.
    
    Args:
        start: Starting directory
        
    Returns:
        Project root or None
    """
    markers = ["ilang.toml", "ilang.json", ".git", "Cargo.toml"]
    current = start.resolve()
    
    while True:
        for marker in markers:
            if (current / marker).exists():
                return current
        
        parent = current.parent
        if parent == current:
            return None
        
        current = parent
