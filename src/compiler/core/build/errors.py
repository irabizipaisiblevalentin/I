"""
Build-specific errors.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional


class BuildError(Exception):
    """Base class for build errors."""
    
    def __init__(self, message: str, code: str = "B000"):
        """
        Initialize build error.
        
        Args:
            message: Error message
            code: Error code
        """
        super().__init__(message)
        self.code = code


class TaskError(BuildError):
    """Build task execution error."""
    
    def __init__(
        self,
        message: str,
        task_name: str,
        task_type: str,
        cause: Optional[Exception] = None,
    ):
        """
        Initialize task error.
        
        Args:
            message: Error message
            task_name: Name of failed task
            task_type: Type of failed task
            cause: Optional underlying exception
        """
        self.task_name = task_name
        self.task_type = task_type
        self.cause = cause
        
        full_message = f"[{task_type}] Task '{task_name}' failed: {message}"
        if cause:
            full_message += f"\nCause: {cause}"
        
        super().__init__(full_message, "B001")


class CacheError(BuildError):
    """Build cache error."""
    
    def __init__(self, message: str, cache_path: Optional[Path] = None):
        """
        Initialize cache error.
        
        Args:
            message: Error message
            cache_path: Optional path to cache file
        """
        self.cache_path = cache_path
        full_message = f"Cache error: {message}"
        if cache_path:
            full_message += f" ({cache_path})"
        super().__init__(full_message, "B005")


class BuildTimeoutError(BuildError):
    """Build timeout exceeded."""
    
    def __init__(self, timeout: float, task_name: Optional[str] = None):
        """
        Initialize timeout error.
        
        Args:
            timeout: Timeout in seconds
            task_name: Optional task that timed out
        """
        self.timeout = timeout
        self.task_name = task_name
        
        message = f"Build timed out after {timeout}s"
        if task_name:
            message += f" (task: {task_name})"
        
        super().__init__(message, "B006")


class BuildMemoryError(BuildError):
    """Build out of memory."""
    
    def __init__(self, limit: Optional[int] = None):
        """
        Initialize memory error.
        
        Args:
            limit: Memory limit in bytes
        """
        self.limit = limit
        
        message = "Build ran out of memory"
        if limit:
            message += f" (limit: {limit / 1024 / 1024:.1f}MB)"
        
        super().__init__(message, "B007")


class CircularDependencyError(BuildError):
    """Circular dependency detected."""
    
    def __init__(self, cycle: List[str]):
        """
        Initialize circular dependency error.
        
        Args:
            cycle: List of tasks forming the cycle
        """
        self.cycle = cycle
        message = f"Circular dependency detected: {' -> '.join(cycle)}"
        super().__init__(message, "B004")
