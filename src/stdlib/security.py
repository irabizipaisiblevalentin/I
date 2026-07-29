"""security — Security utilities for the I language.

Provides input sanitization, password validation, and safe defaults.
"""

from __future__ import annotations

import html
import re
import secrets
import string
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Password generation
# ---------------------------------------------------------------------------

def generate_password(length: int = 16, include_special: bool = True) -> str:
    """Generate a cryptographically secure password."""
    chars = string.ascii_letters + string.digits
    if include_special:
        chars += "!@#$%^&*()-_=+"
    return "".join(secrets.choice(chars) for _ in range(length))


def password_strength(password: str) -> Tuple[int, str]:
    """Evaluate password strength. Returns (score 0-4, label)."""
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[!@#$%^&*()\-_=+]", password):
        score += 1
    score = min(score, 4)
    labels = ["very weak", "weak", "fair", "strong", "very strong"]
    return score, labels[score]


# ---------------------------------------------------------------------------
# Input sanitization
# ---------------------------------------------------------------------------

def escape_html(s: str) -> str:
    """Escape HTML special characters."""
    return html.escape(s)


def unescape_html(s: str) -> str:
    """Unescape HTML entities."""
    return html.unescape(s)


def sanitize_filename(name: str) -> str:
    """Remove or replace unsafe characters from filenames."""
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)


def strip_html(s: str) -> str:
    """Remove HTML tags (simple regex)."""
    return re.sub(r"<[^>]+>", "", s)


def strip_control_chars(s: str) -> str:
    """Remove control characters."""
    return "".join(ch for ch in s if ch.isprintable() or ch in "\n\r\t")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def is_valid_email(email: str) -> bool:
    """Basic email validation."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_strong_password(password: str, min_length: int = 8) -> bool:
    """Check if password meets strength requirements."""
    if len(password) < min_length:
        return False
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[!@#$%^&*()\-_=+]", password))
    return all([has_upper, has_lower, has_digit, has_special])


# ---------------------------------------------------------------------------
# Token generation
# ---------------------------------------------------------------------------

def generate_token(length: int = 32) -> str:
    """Generate a secure URL-safe token."""
    return secrets.token_urlsafe(length)


def generate_api_key() -> str:
    """Generate an API key."""
    return secrets.token_hex(32)


def generate_salt(length: int = 16) -> str:
    """Generate a random salt."""
    return secrets.token_hex(length)
