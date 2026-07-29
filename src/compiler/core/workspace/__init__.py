"""
Workspace Configuration

Manages I project discovery, loading, and configuration.
"""

from .config import Config, Dependency, DependencySource, WorkspaceConfig, ProfileConfig
from .loader import ConfigLoader
from .validator import ConfigValidator, ValidationError
from .resolver import PathResolver
from .workspace import Workspace
from .errors import (
    WorkspaceError,
    ConfigNotFoundError,
    ConfigParseError,
    ConfigValidationError,
    WorkspaceMemberError,
)

__all__ = [
    # Main classes
    "Workspace",
    "Config",
    "Dependency",
    "DependencySource",
    "WorkspaceConfig",
    "ProfileConfig",
    
    # Utilities
    "ConfigLoader",
    "ConfigValidator",
    "ValidationError",
    "PathResolver",
    
    # Errors
    "WorkspaceError",
    "ConfigNotFoundError",
    "ConfigParseError",
    "ConfigValidationError",
    "WorkspaceMemberError",
]
