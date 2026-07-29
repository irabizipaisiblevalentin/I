"""
Workspace-specific errors.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional


class WorkspaceError(Exception):
    """Base class for workspace errors."""
    
    def __init__(self, message: str, path: Optional[Path] = None):
        """
        Initialize workspace error.
        
        Args:
            message: Error message
            path: Optional path associated with error
        """
        super().__init__(message)
        self.path = path


class ConfigNotFoundError(WorkspaceError):
    """Configuration file not found."""
    
    def __init__(self, path: Path, search_paths: Optional[List[Path]] = None):
        """
        Initialize config not found error.
        
        Args:
            path: Path that was searched
            search_paths: All paths that were searched
        """
        self.search_paths = search_paths or []
        message = f"Configuration file not found: {path}"
        if self.search_paths:
            message += f"\nSearched: {', '.join(str(p) for p in self.search_paths)}"
        super().__init__(message, path)


class ConfigParseError(WorkspaceError):
    """Configuration file could not be parsed."""
    
    def __init__(self, path: Path, reason: str, line: Optional[int] = None, column: Optional[int] = None):
        """
        Initialize config parse error.
        
        Args:
            path: Path to configuration file
            reason: Reason for parse failure
            line: Optional line number
            column: Optional column number
        """
        self.reason = reason
        self.line = line
        self.column = column
        
        message = f"Failed to parse configuration: {path}"
        if line is not None:
            message += f":{line}"
            if column is not None:
                message += f":{column}"
        message += f"\n{reason}"
        
        super().__init__(message, path)


class ConfigValidationError(WorkspaceError):
    """Configuration validation failed."""
    
    def __init__(self, path: Path, errors: List[str]):
        """
        Initialize config validation error.
        
        Args:
            path: Path to configuration file
            errors: List of validation errors
        """
        self.errors = errors
        message = f"Configuration validation failed: {path}\n"
        message += "\n".join(f"  - {error}" for error in errors)
        super().__init__(message, path)


class WorkspaceMemberError(WorkspaceError):
    """Workspace member error."""
    
    def __init__(self, message: str, member_path: Optional[Path] = None):
        """
        Initialize workspace member error.
        
        Args:
            message: Error message
            member_path: Optional path to workspace member
        """
        super().__init__(message, member_path)
