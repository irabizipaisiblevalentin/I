"""crypto — Cryptographic functions for the I language.

Provides hashing, HMAC, and basic encryption utilities.
Uses only standard library crypto (no external dependencies).
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from typing import Optional


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def hash_md5(data: bytes) -> str:
    """MD5 hash (not for security, only for checksums)."""
    return hashlib.md5(data).hexdigest()


def hash_sha1(data: bytes) -> str:
    """SHA-1 hash."""
    return hashlib.sha1(data).hexdigest()


def hash_sha256(data: bytes) -> str:
    """SHA-256 hash."""
    return hashlib.sha256(data).hexdigest()


def hash_sha512(data: bytes) -> str:
    """SHA-512 hash."""
    return hashlib.sha512(data).hexdigest()


def hash_file(path: str, algorithm: str = "sha256") -> str:
    """Hash file contents."""
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# HMAC
# ---------------------------------------------------------------------------

def hmac_sha256(key: bytes, message: bytes) -> str:
    """HMAC-SHA256."""
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def hmac_sha512(key: bytes, message: bytes) -> str:
    """HMAC-SHA512."""
    return hmac.new(key, message, hashlib.sha512).hexdigest()


# ---------------------------------------------------------------------------
# Random bytes
# ---------------------------------------------------------------------------

def random_bytes(n: int) -> bytes:
    """Cryptographically secure random bytes."""
    return secrets.token_bytes(n)


def random_hex(n: int) -> str:
    """Cryptographically secure random hex string."""
    return secrets.token_hex(n)


def random_url_safe(n: int) -> str:
    """URL-safe random token."""
    return secrets.token_urlsafe(n)


def compare_digest(a: bytes, b: bytes) -> bool:
    """Constant-time comparison (prevents timing attacks)."""
    return hmac.compare_digest(a, b)
