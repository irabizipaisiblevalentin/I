"""serialization — Object serialization for the I language.

Provides conversion between objects and byte/string representations.
"""

from __future__ import annotations

import base64
import binascii
import json
import pickle
import struct
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Pickle
# ---------------------------------------------------------------------------

def to_pickle(obj: Any) -> bytes:
    """Serialize object to pickle bytes."""
    return pickle.dumps(obj)


def from_pickle(data: bytes) -> Any:
    """Deserialize pickle bytes to object. WARNING: do not use with untrusted data."""
    return pickle.loads(data)


# ---------------------------------------------------------------------------
# Base64
# ---------------------------------------------------------------------------

def to_base64(data: bytes) -> str:
    """Encode bytes to base64 string."""
    return base64.b64encode(data).decode("ascii")


def from_base64(s: str) -> bytes:
    """Decode base64 string to bytes."""
    return base64.b64decode(s)


def to_base64url(data: bytes) -> str:
    """URL-safe base64 encoding."""
    return base64.urlsafe_b64encode(data).decode("ascii")


def from_base64url(s: str) -> bytes:
    return base64.urlsafe_b64decode(s)


# ---------------------------------------------------------------------------
# Hex
# ---------------------------------------------------------------------------

def to_hex(data: bytes) -> str:
    """Encode bytes to hex string."""
    return binascii.hexlify(data).decode("ascii")


def from_hex(s: str) -> bytes:
    """Decode hex string to bytes."""
    return binascii.unhexlify(s)


# ---------------------------------------------------------------------------
# Binary (struct)
# ---------------------------------------------------------------------------

def pack(fmt: str, *values: Any) -> bytes:
    """Pack values into bytes using struct format."""
    return struct.pack(fmt, *values)


def unpack(fmt: str, data: bytes) -> tuple:
    """Unpack bytes using struct format."""
    return struct.unpack(fmt, data)


# ---------------------------------------------------------------------------
# JSON (re-exports for convenience)
# ---------------------------------------------------------------------------

def to_json(obj: Any, indent: Optional[int] = None) -> str:
    """Serialize to JSON string."""
    return json.dumps(obj, indent=indent, ensure_ascii=False)


def from_json(s: str) -> Any:
    """Deserialize from JSON string."""
    return json.loads(s)
