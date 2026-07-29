"""
Unicode Utilities

Utilities for working with Unicode identifiers and strings.
"""

from __future__ import annotations

import unicodedata
from typing import Optional


# Kinyarwanda character ranges (extended Latin + diacritics)
# These are used for valid identifier characters
KINYARWANDA_CHARS = set("abdefghiklmnoprstuvwyzaAcdefgHikLMnoprstuvwyZ")
KINYARWANDA_DIACRITICS = set("àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ")
KINYARWANDA_CHARS.update(KINYARWANDA_DIACRITICS)


def is_identifier_start(char: str) -> bool:
    """
    Check if character can start an identifier.
    
    Args:
        char: Character to check
        
    Returns:
        True if valid identifier start
    """
    if not char:
        return False
    
    # ASCII letters and underscore
    if char.isascii() and (char.isalpha() or char == "_"):
        return True
    
    # Unicode letters
    if char.isalpha() and not char.isascii():
        return True
    
    return False


def is_identifier_part(char: str) -> bool:
    """
    Check if character can be part of an identifier.
    
    Args:
        char: Character to check
        
    Returns:
        True if valid identifier part
    """
    if not char:
        return False
    
    # ASCII alphanumeric and underscore
    if char.isascii() and (char.isalnum() or char == "_"):
        return True
    
    # Unicode alphanumeric
    if char.isalnum() and not char.isascii():
        return True
    
    return False


def is_valid_identifier(name: str) -> bool:
    """
    Check if string is a valid identifier.
    
    Args:
        name: String to check
        
    Returns:
        True if valid identifier
    """
    if not name:
        return False
    
    if not is_identifier_start(name[0]):
        return False
    
    for char in name[1:]:
        if not is_identifier_part(char):
            return False
    
    return True


def get_char_info(char: str) -> dict:
    """
    Get Unicode character information.
    
    Args:
        char: Single character
        
    Returns:
        Dictionary with character info
    """
    return {
        "char": char,
        "name": unicodedata.name(char, "UNKNOWN"),
        "category": unicodedata.category(char),
        "is_alpha": char.isalpha(),
        "is_digit": char.isdigit(),
        "is_alnum": char.isalnum(),
        "is_space": char.isspace(),
        "is_printable": char.isprintable(),
    }


def normalize_identifier(name: str) -> str:
    """
    Normalize an identifier.
    
    Args:
        name: Identifier to normalize
        
    Returns:
        Normalized identifier
    """
    # Normalize Unicode
    normalized = unicodedata.normalize("NFKC", name)
    
    # Lowercase
    return normalized.lower()
