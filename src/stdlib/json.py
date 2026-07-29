"""json — JSON encoding and decoding for the I language.

Provides safe JSON parsing with configurable options.
"""

from __future__ import annotations

import json as _json
from typing import Any, Callable, Optional, TextIO


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------

def dumps(obj: Any, indent: Optional[int] = None, sort_keys: bool = False,
          ensure_ascii: bool = True, separators: Optional[tuple] = None) -> str:
    """Serialize object to JSON string."""
    kwargs: dict[str, Any] = {"ensure_ascii": ensure_ascii}
    if indent is not None:
        kwargs["indent"] = indent
    if sort_keys:
        kwargs["sort_keys"] = True
    if separators is not None:
        kwargs["separators"] = separators
    return _json.dumps(obj, **kwargs)


def dump(obj: Any, fp: TextIO, indent: Optional[int] = None,
         sort_keys: bool = False) -> None:
    """Serialize object to file-like object."""
    _json.dump(obj, fp, indent=indent, sort_keys=sort_keys)


def to_file(obj: Any, path: str, indent: Optional[int] = 2,
            encoding: str = "utf-8") -> None:
    """Serialize object to JSON file."""
    with open(path, "w", encoding=encoding) as f:
        _json.dump(obj, f, indent=indent)


def compact(obj: Any) -> str:
    """Compact JSON (no whitespace)."""
    return _json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


# ---------------------------------------------------------------------------
# Decoding
# ---------------------------------------------------------------------------

def loads(s: str) -> Any:
    """Deserialize JSON string."""
    return _json.loads(s)


def load(fp: TextIO) -> Any:
    """Deserialize from file-like object."""
    return _json.load(fp)


def from_file(path: str, encoding: str = "utf-8") -> Any:
    """Deserialize from JSON file."""
    with open(path, "r", encoding=encoding) as f:
        return _json.load(f)


# ---------------------------------------------------------------------------
# Safe operations
# ---------------------------------------------------------------------------

def try_loads(s: str, default: Any = None) -> Any:
    """Parse JSON, return default on failure."""
    try:
        return _json.loads(s)
    except (_json.JSONDecodeError, ValueError):
        return default


def try_from_file(path: str, default: Any = None, encoding: str = "utf-8") -> Any:
    """Read JSON file, return default on failure."""
    try:
        return from_file(path, encoding)
    except (OSError, _json.JSONDecodeError):
        return default


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def is_valid(s: str) -> bool:
    """Check if string is valid JSON."""
    try:
        _json.loads(s)
        return True
    except (_json.JSONDecodeError, ValueError):
        return False


def validate(s: str) -> Optional[str]:
    """Validate JSON string. Returns error message or None if valid."""
    try:
        _json.loads(s)
        return None
    except (_json.JSONDecodeError, ValueError) as e:
        return str(e)


# ---------------------------------------------------------------------------
# Transformation
# ---------------------------------------------------------------------------

def prettify(s: str) -> str:
    """Pretty-print a JSON string."""
    obj = _json.loads(s)
    return _json.dumps(obj, indent=2, ensure_ascii=False)


def minify(s: str) -> str:
    """Minify a JSON string (remove whitespace)."""
    obj = _json.loads(s)
    return _json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def patch(s: str, updates: dict) -> str:
    """Apply updates to a JSON string and return new JSON."""
    obj = _json.loads(s)
    if isinstance(obj, dict):
        obj.update(updates)
    return _json.dumps(obj, indent=2, ensure_ascii=False)
