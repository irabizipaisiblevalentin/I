"""
Workspace Configuration

Manages I project discovery, loading, and configuration.
"""

from .config import Config, Dependency, DependencySource, ProfileConfig, WorkspaceConfig
from .errors import (
    ConfigNotFoundError,
    ConfigParseError,
    ConfigValidationError,
    WorkspaceError,
    WorkspaceMemberError,
)
from .loader import ConfigLoader
from .resolver import PathResolver
from .validator import ConfigValidator, ValidationError
from .workspace import Workspace

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
