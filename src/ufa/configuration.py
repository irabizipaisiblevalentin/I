"""configuration — Unified configuration system.

Supports hierarchical config, environment variables, remote config,
secrets, profiles, and deep merge operations.
"""

from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, List, Optional


class Configuration:
    """Hierarchical configuration with dot-notation access and deep merge."""

    def __init__(self, data: Optional[Dict[str, Any]] = None) -> None:
        self._data: Dict[str, Any] = data or {}
        self._env_prefix: str = ""
        self._loaded_from: List[str] = []

    @property
    def data(self) -> Dict[str, Any]:
        return dict(self._data)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value using dot-notation (e.g. 'server.port')."""
        keys = key.split(".")
        val = self._data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return default
        return val

    def set(self, key: str, value: Any) -> None:
        """Set a value using dot-notation."""
        keys = key.split(".")
        d = self._data
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    def has(self, key: str) -> bool:
        keys = key.split(".")
        val = self._data
        for k in keys:
            if isinstance(val, dict) and k in val:
                val = val[k]
            else:
                return False
        return True

    def delete(self, key: str) -> bool:
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

    def merge(self, other: Dict[str, Any]) -> None:
        """Deep merge another dict into this configuration."""
        self._data = _deep_merge(self._data, other)

    def override(self, other: Dict[str, Any]) -> None:
        """Shallow override (replace at top level)."""
        self._data.update(other)

    def subset(self, prefix: str) -> "Configuration":
        """Extract a sub-configuration by prefix."""
        val = self.get(prefix)
        if isinstance(val, dict):
            return Configuration(val)
        return Configuration()

    def flatten(self, prefix: str = "") -> Dict[str, str]:
        """Flatten to dot-notation string dict (for env var export)."""
        result = {}
        _flatten_dict(self._data, prefix, result)
        return result

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)

    def load_env(self, prefix: str = "I_", separator: str = "__") -> int:
        """Load environment variables with prefix into config.
        
        Example: I_SERVER__PORT=8080 -> config.server.port = 8080
        """
        self._env_prefix = prefix
        count = 0
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower().replace(separator, ".")
                self.set(config_key, _coerce_env_value(value))
                count += 1
        return count

    def load_file(self, path: str) -> bool:
        """Load configuration from a JSON file."""
        if not os.path.isfile(path):
            return False
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self.merge(data)
                self._loaded_from.append(path)
                return True
        except (json.JSONDecodeError, OSError):
            pass
        return False

    def load_dict(self, data: Dict[str, Any]) -> None:
        self.merge(data)

    def save(self, path: str, indent: int = 2) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=indent, ensure_ascii=False)

    def get_or_default(self, key: str, default_factory: Callable) -> Any:
        val = self.get(key)
        if val is None:
            return default_factory()
        return val

    def keys(self) -> List[str]:
        return list(self._data.keys())

    def values(self) -> List[Any]:
        return list(self._data.values())

    def items(self) -> List[tuple]:
        return list(self._data.items())

    def __contains__(self, key: str) -> bool:
        return self.has(key)

    def __getitem__(self, key: str) -> Any:
        val = self.get(key)
        if val is None:
            raise KeyError(key)
        return val

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    def __repr__(self) -> str:
        return f"Configuration({self._data})"


class Profiles:
    """Profile-based configuration switching."""

    def __init__(self) -> None:
        self._profiles: Dict[str, Configuration] = {}
        self._active: str = "development"

    @property
    def active(self) -> str:
        return self._active

    def add(self, name: str, config: Configuration) -> None:
        self._profiles[name] = config

    def activate(self, name: str) -> None:
        if name not in self._profiles:
            raise ValueError(f"unknown profile: {name}")
        self._active = name

    def get(self, name: Optional[str] = None) -> Optional[Configuration]:
        return self._profiles.get(name or self._active)

    def profiles(self) -> List[str]:
        return list(self._profiles.keys())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

from typing import Callable

def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _flatten_dict(d: Dict[str, Any], prefix: str, result: Dict[str, str]) -> None:
    for key, value in d.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            _flatten_dict(value, full_key, result)
        else:
            result[full_key] = str(value)


def _coerce_env_value(value: str) -> Any:
    if value.lower() in ("true", "yes", "1"):
        return True
    if value.lower() in ("false", "no", "0"):
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value
