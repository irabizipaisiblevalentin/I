"""yaml — YAML parsing and generation for the I language.

Provides YAML loading and dumping with safe defaults.
Requires PyYAML to be installed.
"""

from __future__ import annotations

from typing import Any, Optional, TextIO

try:
    import yaml as _yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


def _check() -> None:
    if not _HAS_YAML:
        raise ImportError("PyYAML is not installed. Install with: pip install pyyaml")


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load(s: str) -> Any:
    """Parse YAML string."""
    _check()
    return _yaml.safe_load(s)


def load_file(path: str, encoding: str = "utf-8") -> Any:
    """Parse YAML file."""
    _check()
    with open(path, "r", encoding=encoding) as f:
        return _yaml.safe_load(f)


def load_all(s: str) -> list:
    """Parse all YAML documents from string."""
    _check()
    return list(_yaml.safe_load_all(s))


def load_all_file(path: str, encoding: str = "utf-8") -> list:
    """Parse all YAML documents from file."""
    _check()
    with open(path, "r", encoding=encoding) as f:
        return list(_yaml.safe_load_all(f))


# ---------------------------------------------------------------------------
# Dumping
# ---------------------------------------------------------------------------

def dumps(obj: Any, indent: int = 2, default_flow_style: Optional[bool] = None,
          sort_keys: bool = False) -> str:
    """Serialize object to YAML string."""
    _check()
    return _yaml.dump(
        obj,
        default_flow_style=default_flow_style,
        indent=indent,
        sort_keys=sort_keys,
        allow_unicode=True,
    )


def dump(obj: Any, fp: TextIO, indent: int = 2) -> None:
    """Serialize object to file-like object."""
    _check()
    _yaml.dump(obj, fp, indent=indent, allow_unicode=True)


def dump_file(obj: Any, path: str, encoding: str = "utf-8") -> None:
    """Serialize object to YAML file."""
    _check()
    with open(path, "w", encoding=encoding) as f:
        _yaml.dump(obj, f, allow_unicode=True)


# ---------------------------------------------------------------------------
# Safe operations
# ---------------------------------------------------------------------------

def try_load(s: str, default: Any = None) -> Any:
    """Parse YAML string, return default on failure."""
    try:
        return load(s)
    except Exception:
        return default


def try_load_file(path: str, default: Any = None, encoding: str = "utf-8") -> Any:
    """Parse YAML file, return default on failure."""
    try:
        return load_file(path, encoding)
    except Exception:
        return default
