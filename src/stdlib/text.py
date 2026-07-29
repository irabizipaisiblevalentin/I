"""text — String manipulation and text processing for the I language.

Provides a consistent, Unicode-first API for working with strings:
case conversion, searching, splitting, joining, formatting, validation,
and text transformation.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Callable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Case conversion
# ---------------------------------------------------------------------------

def to_upper(s: str) -> str:
    """Convert string to uppercase. / Guhindura intege yose hejuru."""
    return s.upper()


def to_lower(s: str) -> str:
    """Convert string to lowercase. / Guhindura intege yose hasi."""
    return s.lower()


def to_title(s: str) -> str:
    """Convert string to title case. / Guhindura ubwoko bw'isakazwa."""
    return s.title()


def to_case_fold(s: str) -> str:
    """Case-insensitive comparison form. / Ubwoko bushingiye ku gihe."""
    return s.casefold()


# ---------------------------------------------------------------------------
# Searching
# ---------------------------------------------------------------------------

def contains(haystack: str, needle: str) -> bool:
    """Return True if *needle* is found in *haystack*."""
    return needle in haystack


def starts_with(s: str, prefix: str) -> bool:
    """Return True if *s* starts with *prefix*."""
    return s.startswith(prefix)


def ends_with(s: str, suffix: str) -> bool:
    """Return True if *s* ends with *suffix*."""
    return s.endswith(suffix)


def find(s: str, sub: str, start: int = 0, end: Optional[int] = None) -> int:
    """Return lowest index of *sub* in *s*, or -1 if not found."""
    return s.find(sub, start, end or len(s))


def rfind(s: str, sub: str, start: int = 0, end: Optional[int] = None) -> int:
    """Return highest index of *sub* in *s*, or -1 if not found."""
    return s.rfind(sub, start, end or len(s))


def index_of(s: str, sub: str, start: int = 0) -> int:
    """Like find but raises ValueError if not found."""
    idx = s.find(sub, start)
    if idx == -1:
        raise ValueError(f"substring not found: {sub!r}")
    return idx


def count(s: str, sub: str) -> int:
    """Count non-overlapping occurrences of *sub* in *s*."""
    return s.count(sub)


def regex_search(s: str, pattern: str) -> Optional[re.Match]:
    """Search for a regex pattern. Returns Match or None."""
    return re.search(pattern, s)


def regex_find_all(s: str, pattern: str) -> List[re.Match]:
    """Find all matches of a regex pattern."""
    return list(re.finditer(pattern, s))


# ---------------------------------------------------------------------------
# Splitting and joining
# ---------------------------------------------------------------------------

def split(s: str, delimiter: str = "", max_split: int = -1) -> List[str]:
    """Split string by delimiter. Empty delimiter splits on whitespace."""
    if delimiter == "":
        return s.split(None, max_split if max_split >= 0 else -1)
    return s.split(delimiter, max_split if max_split >= 0 else -1)


def rsplit(s: str, delimiter: str = "", max_split: int = -1) -> List[str]:
    """Split from the right."""
    if delimiter == "":
        return s.rsplit(None, max_split if max_split >= 0 else -1)
    return s.rsplit(delimiter, max_split if max_split >= 0 else -1)


def join(parts: Sequence[str], delimiter: str = "") -> str:
    """Join strings with delimiter."""
    return delimiter.join(parts)


def lines(s: str) -> List[str]:
    """Split string into lines."""
    return s.splitlines()


# ---------------------------------------------------------------------------
# Trimming and padding
# ---------------------------------------------------------------------------

def trim(s: str, chars: Optional[str] = None) -> str:
    """Strip leading and trailing characters."""
    return s.strip(chars)


def ltrim(s: str, chars: Optional[str] = None) -> str:
    """Strip leading characters."""
    return s.lstrip(chars)


def rtrim(s: str, chars: Optional[str] = None) -> str:
    """Strip trailing characters."""
    return s.rstrip(chars)


def pad_left(s: str, width: int, fill: str = " ") -> str:
    """Pad string on the left to *width*."""
    return s.rjust(width, fill)


def pad_right(s: str, width: int, fill: str = " ") -> str:
    """Pad string on the right to *width*."""
    return s.ljust(width, fill)


def pad_center(s: str, width: int, fill: str = " ") -> str:
    """Center string within *width*."""
    return s.center(width, fill)


# ---------------------------------------------------------------------------
# Replacement
# ---------------------------------------------------------------------------

def replace(s: str, old: str, new: str, max_count: int = -1) -> str:
    """Replace occurrences of *old* with *new*."""
    if max_count < 0:
        return s.replace(old, new)
    return s.replace(old, new, max_count)


def regex_replace(s: str, pattern: str, replacement: str) -> str:
    """Replace regex matches with replacement string."""
    return re.sub(pattern, replacement, s)


# ---------------------------------------------------------------------------
# Tests and validation
# ---------------------------------------------------------------------------

def is_empty(s: str) -> bool:
    """Return True if string is empty or whitespace only."""
    return not s or s.isspace()


def is_blank(s: str) -> bool:
    """Return True if string is empty or whitespace only."""
    return s.isspace() if s else True


def is_numeric(s: str) -> bool:
    """Return True if string represents a number."""
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def is_alpha(s: str) -> bool:
    """Return True if all characters are alphabetic."""
    return s.isalpha()


def is_alphanumeric(s: str) -> bool:
    """Return True if all characters are alphanumeric."""
    return s.isalnum()


def is_identifier(s: str) -> bool:
    """Return True if string is a valid I language identifier."""
    return s.isidentifier()


# ---------------------------------------------------------------------------
# Transformation
# ---------------------------------------------------------------------------

def reverse(s: str) -> str:
    """Reverse a string."""
    return s[::-1]


def repeat(s: str, count: int) -> str:
    """Repeat string *count* times."""
    return s * count


def truncate(s: str, max_len: int, suffix: str = "...") -> str:
    """Truncate string to *max_len* characters, appending *suffix*."""
    if len(s) <= max_len:
        return s
    return s[: max_len - len(suffix)] + suffix


def wrap(s: str, width: int) -> str:
    """Word-wrap string to *width* characters per line."""
    words = s.split()
    lines_out: List[str] = []
    current_line: List[str] = []
    current_len = 0
    for word in words:
        if current_len + len(word) + (1 if current_line else 0) > width:
            if current_line:
                lines_out.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)
        else:
            current_line.append(word)
            current_len += len(word) + (1 if len(current_line) > 1 else 0)
    if current_line:
        lines_out.append(" ".join(current_line))
    return "\n".join(lines_out)


def normalize(s: str, form: str = "NFC") -> str:
    """Unicode normalization. Form: NFC, NFD, NFKC, NFKD."""
    return unicodedata.normalize(form, s)


def strip_accents(s: str) -> str:
    """Remove diacritical marks (accents) from characters."""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def template(s: str, **kwargs: Any) -> str:
    """Simple template substitution: 'Hello {name}' → 'Hello World'."""
    return s.format(**kwargs)


def pad_numeric(value: int, width: int, fill: str = "0") -> str:
    """Format number with zero-padding."""
    return str(value).zfill(width)


def pluralize(count: int, singular: str, plural: Optional[str] = None) -> str:
    """Return singular or plural form based on count."""
    if count == 1:
        return singular
    if plural is None:
        return singular + "s"
    return plural
