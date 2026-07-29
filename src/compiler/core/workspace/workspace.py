"""
Workspace management.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from .config import Config
from .errors import ConfigNotFoundError, WorkspaceMemberError
from .loader import ConfigLoader
from .resolver import PathResolver
from .validator import ConfigValidator, ValidationError


class Workspace:
    """
    Main workspace interface.
    
    Represents an I project workspace, providing access to
    configuration, workspace members, and path resolution.
    """
    
    def __init__(self, root: Path, config: Config) -> None:
        """
        Initialize workspace.
        
        Args:
            root: Workspace root directory
            config: Workspace configuration
        """
        self._root = root.resolve()
        self._config = config
        self._resolver = PathResolver(root)
        self._validator = ConfigValidator()
        self._members: Optional[List[Path]] = None
    
    @classmethod
    def load(cls, path: Path) -> Workspace:
        """
        Load workspace from path.
        
        Searches for configuration file starting from path
        and moving up directory hierarchy.
        
        Args:
            path: Path to start search from
            
        Returns:
            Loaded workspace
            
        Raises:
            ConfigNotFoundError: If no configuration file found
        """
        loader = ConfigLoader()
        
        # Try to find config file
        config_path = loader.find_config(path)
        if config_path is None:
            raise ConfigNotFoundError(
                path / "ilang.toml",
                search_paths=[path],
            )
        
        # Load configuration
        config = loader.load(config_path)
        
        # Workspace root is directory containing config file
        root = config_path.parent
        
        return cls(root, config)
    
    @classmethod
    def load_from_config(cls, config_path: Path) -> Workspace:
        """
        Load workspace from configuration file path.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Loaded workspace
            
        Raises:
            ConfigNotFoundError: If configuration file does not exist
        """
        loader = ConfigLoader()
        config = loader.load(config_path)
        root = config_path.parent
        return cls(root, config)
    
    @property
    def root(self) -> Path:
        """Workspace root directory."""
        return self._root
    
    @property
    def config(self) -> Config:
        """Workspace configuration."""
        return self._config
    
    @property
    def resolver(self) -> PathResolver:
        """Path resolver for this workspace."""
        return self._resolver
    
    @property
    def members(self) -> List[Path]:
        """
        List of workspace member paths.
        
        Returns:
            List of absolute paths to workspace members
        """
        if self._members is None:
            self._members = self._resolve_members()
        return self._members
    
    def resolve_path(self, path: str) -> Path:
        """
        Resolve path relative to workspace root.
        
        Args:
            path: Path to resolve
            
        Returns:
            Resolved absolute path
        """
        return self._resolver.resolve(path)
    
    def get_member(self, name: str) -> Optional[Path]:
        """
        Get workspace member by name.
        
        Args:
            name: Member name
            
        Returns:
            Path to member, or None if not found
        """
        for member in self.members:
            if member.name == name:
                return member
        return None
    
    def validate(self) -> List[ValidationError]:
        """
        Validate workspace configuration.
        
        Returns:
            List of validation errors (empty if valid)
        """
        return self._validator.validate(self._config, self._root / "ilang.toml")
    
    def is_valid(self) -> bool:
        """
        Check if workspace configuration is valid.
        
        Returns:
            True if valid, False otherwise
        """
        return len(self.validate()) == 0
    
    def _resolve_members(self) -> List[Path]:
        """
        Resolve workspace member paths.
        
        Returns:
            List of resolved member paths
        """
        if self._config.workspace is None:
            return []
        
        members: List[Path] = []
        for member_path in self._config.workspace.members:
            resolved = self._resolver.resolve(member_path)
            
            if not resolved.is_dir():
                raise WorkspaceMemberError(
                    f"Workspace member not found: {member_path}",
                    resolved,
                )
            
            members.append(resolved)
        
        return members
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Workspace(root={self._root}, name={self._config.name})"
    
    def __eq__(self, other: object) -> bool:
        """Equality check."""
        if not isinstance(other, Workspace):
            return NotImplemented
        return self._root == other._root
    
    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        return hash(self._root)
