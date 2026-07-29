"""
Configuration loader.
"""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any

from .schema import ConfigError, ConfigSchema
from .types import CompilerConfig

# Default config file names
CONFIG_FILE_NAMES = ["ilang.toml", "ilang.json", ".ilangrc"]


class ConfigLoader:
    """
    Loads compiler configuration from files and environment.

    Supports TOML and JSON formats.
    """

    def __init__(self, root: Path | None = None) -> None:
        """
        Initialize loader.

        Args:
            root: Root directory to search for config files
        """
        self._root = root or Path.cwd()
        self._config: CompilerConfig | None = None

    @property
    def root(self) -> Path:
        """Root directory."""
        return self._root

    def find_config_file(self) -> Path | None:
        """
        Find configuration file in root directory.

        Returns:
            Path to config file, or None if not found
        """
        for name in CONFIG_FILE_NAMES:
            path = self._root / name
            if path.exists():
                return path
        return None

    def load_file(self, path: Path) -> dict[str, Any]:
        """
        Load configuration from file.

        Args:
            path: Path to config file

        Returns:
            Configuration dictionary
        """
        suffix = path.suffix.lower()

        if suffix == ".toml":
            return self._load_toml(path)
        elif suffix == ".json":
            return self._load_json(path)
        else:
            raise ConfigError(f"Unsupported config format: {suffix}")

    def _load_toml(self, path: Path) -> dict[str, Any]:
        """Load TOML file."""
        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            raise ConfigError(f"Failed to load TOML config: {e}")

    def _load_json(self, path: Path) -> dict[str, Any]:
        """Load JSON file."""
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise ConfigError(f"Failed to load JSON config: {e}")

    def validate(self, data: dict[str, Any]) -> CompilerConfig:
        """
        Validate and create config from data.

        Args:
            data: Configuration dictionary

        Returns:
            Validated CompilerConfig

        Raises:
            ConfigError: If validation fails
        """
        errors = ConfigSchema.validate(data)
        if errors:
            raise ConfigError(f"Invalid configuration: {'; '.join(errors)}")

        if "build" in data:
            build_errors = ConfigSchema.validate_build(data["build"])
            if build_errors:
                raise ConfigError(f"Invalid build config: {'; '.join(build_errors)}")

        if "features" in data:
            feature_errors = ConfigSchema.validate_features(data["features"])
            if feature_errors:
                raise ConfigError(f"Invalid feature flags: {'; '.join(feature_errors)}")

        config = CompilerConfig.from_dict(data)
        config.root = self._root
        return config

    def load(self, path: Path | None = None) -> CompilerConfig:
        """
        Load configuration.

        Args:
            path: Optional path to config file. If None, searches for default.

        Returns:
            CompilerConfig instance
        """
        if path is None:
            path = self.find_config_file()

        if path is None:
            return CompilerConfig(root=self._root)

        data = self.load_file(path)
        self._config = self.validate(data)
        return self._config

    def get_config(self) -> CompilerConfig:
        """Get loaded configuration."""
        if self._config is None:
            return self.load()
        return self._config


def load_config(
    root: Path | None = None,
    path: Path | None = None,
) -> CompilerConfig:
    """
    Load configuration from file.

    Args:
        root: Root directory
        path: Optional config file path

    Returns:
        CompilerConfig instance
    """
    loader = ConfigLoader(root)
    return loader.load(path)
