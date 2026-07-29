"""unicode — Unicode utilities for the I language.

Provides character classification, properties, normalization, and
encoding/decoding utilities. All functions are Unicode-first.
"""

from __future__ import annotations

import codecs
import unicodedata
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Character classification
# ---------------------------------------------------------------------------

def is_upper(ch: str) -> bool:
    """Check if character is uppercase."""
    return ch.isupper()


def is_lower(ch: str) -> bool:
    """Check if character is lowercase."""
    return ch.islower()


def is_title(ch: str) -> bool:
    """Check if character is titlecase."""
    return ch.istitle()


def is_digit(ch: str) -> bool:
    """Check if character is a digit."""
    return ch.isdigit()


def is_alpha(ch: str) -> bool:
    """Check if character is alphabetic."""
    return ch.isalpha()


def is_alnum(ch: str) -> bool:
    """Check if character is alphanumeric."""
    return ch.isalnum()


def is_space(ch: str) -> bool:
    """Check if character is whitespace."""
    return ch.isspace()


def is_printable(ch: str) -> bool:
    """Check if character is printable."""
    return ch.isprintable()


def is_control(ch: str) -> bool:
    """Check if character is a control character."""
    return ch.iscontrol()


def is_punctuation(ch: str) -> bool:
    """Check if character is punctuation."""
    cat = unicodedata.category(ch)
    return cat.startswith("P")


def is_symbol(ch: str) -> bool:
    """Check if character is a symbol."""
    cat = unicodedata.category(ch)
    return cat.startswith("S")


def is_numeric(ch: str) -> bool:
    """Check if character has numeric value."""
    cat = unicodedata.category(ch)
    return cat.startswith("N")


# ---------------------------------------------------------------------------
# Character properties
# ---------------------------------------------------------------------------

def category(ch: str) -> str:
    """Unicode category (e.g. 'Lu', 'Nd', 'Zs')."""
    return unicodedata.category(ch)


def name(ch: str, default: str = "") -> str:
    """Unicode name (e.g. 'LATIN CAPITAL LETTER A')."""
    return unicodedata.name(ch, default)


def lookup(name: str) -> str:
    """Look up character by name. Raises ValueError if not found."""
    return unicodedata.lookup(name)


def combining(ch: str) -> int:
    """Combining class (0 = non-combining)."""
    return unicodedata.combining(ch)


def east_asian_width(ch: str) -> str:
    """East Asian width property."""
    return unicodedata.east_asian_width(ch)


def numeric_value(ch: str) -> Optional[float]:
    """Numeric value of character, or None."""
    try:
        return unicodedata.numeric(ch)
    except (ValueError, TypeError):
        return None


def digit_value(ch: str) -> Optional[int]:
    """Digit value for decimal digits."""
    try:
        return int(ch)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def normalize(s: str, form: str = "NFC") -> str:
    """Unicode normalization. form: NFC, NFD, NFKC, NFKD."""
    return unicodedata.normalize(form, s)


def is_normalized(s: str, form: str = "NFC") -> bool:
    """Check if string is in given normalization form."""
    return unicodedata.is_normalized(form, s)


def strip_combining(s: str) -> str:
    """Remove combining characters (accents)."""
    return "".join(ch for ch in s if unicodedata.combining(ch) == 0)


# ---------------------------------------------------------------------------
# Encoding / decoding
# ---------------------------------------------------------------------------

def encode(s: str, encoding: str = "utf-8") -> bytes:
    """Encode string to bytes."""
    return s.encode(encoding)


def decode(data: bytes, encoding: str = "utf-8") -> str:
    """Decode bytes to string."""
    return data.decode(encoding)


def code_point(ch: str) -> int:
    """Unicode code point of first character."""
    return ord(ch)


def from_code_point(cp: int) -> str:
    """Character from code point."""
    return chr(cp)


def code_points(s: str) -> List[int]:
    """List of code points for all characters."""
    return [ord(ch) for ch in s]


def from_code_points(cps: List[int]) -> str:
    """String from list of code points."""
    return "".join(chr(cp) for cp in cps)


# ---------------------------------------------------------------------------
# UTF-8 utilities
# ---------------------------------------------------------------------------

def utf8_bytes(s: str) -> int:
    """Number of UTF-8 bytes needed for string."""
    return len(s.encode("utf-8"))


def utf8_encoded(s: str) -> List[int]:
    """List of UTF-8 byte values."""
    return list(s.encode("utf-8"))


# ---------------------------------------------------------------------------
# Character iteration
# ---------------------------------------------------------------------------

def chars(s: str) -> List[str]:
    """Split string into individual characters."""
    return list(s)


def reverse(s: str) -> str:
    """Reverse string respecting grapheme clusters (basic)."""
    return s[::-1]


def graphemes(s: str) -> List[str]:
    """Split into grapheme clusters (simple: by combining class)."""
    result: List[str] = []
    current: List[str] = []
    for ch in s:
        if current and unicodedata.combining(ch) == 0:
            result.append("".join(current))
            current = [ch]
        else:
            current.append(ch)
    if current:
        result.append("".join(current))
    return result
