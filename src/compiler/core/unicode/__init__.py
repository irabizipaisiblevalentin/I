"""
Unicode Utilities

Provides UTF-8 reading and Unicode character utilities.
"""

from .reader import UTF8Reader
from .utils import (
    is_identifier_start,
    is_identifier_part,
    is_valid_identifier,
    get_char_info,
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
