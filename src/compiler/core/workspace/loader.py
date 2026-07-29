"""
Configuration file loading.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

from .config import Config
from .errors import ConfigNotFoundError, ConfigParseError


class ConfigLoader:
    """
    Loads configuration from files.
    
    Supports TOML, YAML, and JSON configuration formats.
    TOML is the primary format for I projects.
    """
    
    # Supported configuration file names (in order of preference)
    CONFIG_NAMES = [
        "ilang.toml",
        "ilang.yaml",
        "ilang.yml",
        "ilang.json",
        ".ilang.toml",
        ".ilang.yaml",
        ".ilang.yml",
        ".ilang.json",
    ]
    
    def __init__(self) -> None:
        """Initialize configuration loader."""
        self._cache: Dict[Path, Config] = {}
    
    def find_config(self, start_path: Path) -> Optional[Path]:
        """
        Find configuration file by searching up from start_path.
        
        Args:
            start_path: Path to start searching from
            
        Returns:
            Path to configuration file, or None if not found
        """
        current = start_path.resolve()
        
        while True:
            for name in self.CONFIG_NAMES:
                config_path = current / name
                if config_path.is_file():
                    return config_path
            
            # Move to parent directory
            parent = current.parent
            if parent == current:
                # Reached filesystem root
                break
            current = parent
        
        return None
    
    def load(self, path: Path) -> Config:
        """
        Load configuration from path.
        
        Args:
            path: Path to configuration file
            
        Returns:
            Loaded configuration
            
        Raises:
            ConfigNotFoundError: If file does not exist
            ConfigParseError: If file cannot be parsed
        """
        path = path.resolve()
        
        # Check cache
        if path in self._cache:
            return self._cache[path]
        
        # Validate file exists
        if not path.is_file():
            raise ConfigNotFoundError(path)
        
        # Determine format and load
        data = self._load_file(path)
        
        # Parse configuration
        try:
            config = Config.from_dict(data)
        except Exception as e:
            raise ConfigParseError(path, str(e))
        
        # Cache and return
        self._cache[path] = config
        return config
    
    def load_from_directory(self, directory: Path) -> Config:
        """
        Load configuration from directory.
        
        Searches for configuration file in directory.
        
        Args:
            directory: Directory to search in
            
        Returns:
            Loaded configuration
            
        Raises:
            ConfigNotFoundError: If no configuration file found
            ConfigParseError: If file cannot be parsed
        """
        config_path = self.find_config(directory)
        if config_path is None:
            raise ConfigNotFoundError(
                directory / "ilang.toml",
                search_paths=[directory / name for name in self.CONFIG_NAMES],
            )
        return self.load(config_path)
    
    def clear_cache(self) -> None:
        """Clear configuration cache."""
        self._cache.clear()
    
    def _load_file(self, path: Path) -> Dict[str, Any]:
        """
        Load file based on extension.
        
        Args:
            path: Path to file
            
        Returns:
            Parsed data
            
        Raises:
            ConfigParseError: If file cannot be parsed
        """
        suffix = path.suffix.lower()
        
        try:
            if suffix == ".toml":
                return self._load_toml(path)
            elif suffix in (".yaml", ".yml"):
                return self._load_yaml(path)
            elif suffix == ".json":
                return self._load_json(path)
            else:
                # Try TOML as default
                return self._load_toml(path)
        except Exception as e:
            raise ConfigParseError(path, str(e))
    
    def _load_toml(self, path: Path) -> Dict[str, Any]:
        """
        Load TOML file.
        
        Args:
            path: Path to TOML file
            
        Returns:
            Parsed data
        """
        try:
            import tomllib
        except ImportError:
            # Python < 3.11
            try:
                import tomli as tomllib
            except ImportError:
                raise ConfigParseError(
                    path,
                    "TOML support not available. Install tomli: pip install tomli"
                )
        
        with open(path, "rb") as f:
            return tomllib.load(f)
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """
        Load YAML file.
        
        Args:
            path: Path to YAML file
            
        Returns:
            Parsed data
        """
        try:
            import yaml
        except ImportError:
            raise ConfigParseError(
                path,
                "YAML support not available. Install PyYAML: pip install pyyaml"
            )
        
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """
        Load JSON file.
        
        Args:
            path: Path to JSON file
            
        Returns:
            Parsed data
        """
        import json
        
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
