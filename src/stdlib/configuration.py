"""configuration — Configuration file management for the I language.

Provides loading, saving, and merging of configuration from
multiple sources (files, environment variables, defaults).
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional


class Config:
    """Hierarchical configuration store."""

    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
        self._data: Dict[str, Any] = dict(data) if data else {}
        self._defaults: Dict[str, Any] = {}
        self._env_prefix: str = ""

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-separated key."""
        keys = key.split(".")
        val = self._data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, key: str, value: Any) -> None:
        """Set config value by dot-separated key."""
        keys = key.split(".")
        d = self._data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def remove(self, key: str) -> bool:
        """Remove key. Returns True if existed."""
        keys = key.split(".")
        d = self._data
        for k in keys[:-1]:
            if not isinstance(d, dict) or k not in d:
                return False
            d = d[k]
        if isinstance(d, dict) and keys[-1] in d:
            del d[keys[-1]]
            return True
        return False

    def keys(self) -> List[str]:
        return list(self._data.keys())

    def values(self) -> List[Any]:
        return list(self._data.values())

    def items(self) -> List[tuple]:
        return list(self._data.items())

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)

    def merge(self, other: Dict[str, Any]) -> None:
        """Deep merge another dict into this config."""
        self._deep_merge(self._data, other)

    def set_default(self, key: str, value: Any) -> None:
        """Set default value (only if not already set)."""
        if self.get(key) is None:
            self.set(key, value)

    def load_env(self, prefix: str = "I_") -> None:
        """Load environment variables with given prefix."""
        self._env_prefix = prefix
        for key, val in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower().replace("_", ".")
                self.set(config_key, val)

    def load_dict(self, data: Dict[str, Any]) -> None:
        self._data.update(data)

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                Config._deep_merge(base[key], value)
            else:
                base[key] = value
        return base

    def __repr__(self) -> str:
        return f"Config({self._data!r})"

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key: str) -> bool:
        return self.has(key)


def load_file(path: str, format: str = "json", encoding: str = "utf-8") -> Config:
    """Load configuration from file."""
    config = Config()
    if format == "json":
        with open(path, "r", encoding=encoding) as f:
            config.load_dict(json.load(f))
    return config


def save_file(config: Config, path: str, format: str = "json",
              encoding: str = "utf-8", indent: int = 2) -> None:
    """Save configuration to file."""
    if format == "json":
        with open(path, "w", encoding=encoding) as f:
            json.dump(config.to_dict(), f, indent=indent)


def merge(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple config dicts (last wins)."""
    result: Dict[str, Any] = {}
    for cfg in configs:
        Config._deep_merge(result, cfg)
    return result
