"""
Unicode Utilities

Provides UTF-8 reading and Unicode character utilities.
"""

from .reader import UTF8Reader
from .utils import (
    get_char_info,
    is_identifier_part,
    is_identifier_start,
    is_valid_identifier,
    normalize_identifier,
)

__all__ = [
    "UTF8Reader",
    "is_identifier_start",
    "is_identifier_part",
    "is_valid_identifier",
    "get_char_info",
    "normalize_identifier",
]
