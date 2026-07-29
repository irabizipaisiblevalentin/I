"""
Tests for Unicode utilities.
"""

import pytest

from src.compiler.core.unicode import (
    UTF8Reader,
    is_identifier_start,
    is_identifier_part,
    is_valid_identifier,
    get_char_info,
    normalize_identifier,
)


# ============================================================================
# UTF8Reader Tests
# ============================================================================


class TestUTF8Reader:
    """Tests for UTF8Reader."""
    
    def test_read(self):
        """Test reading characters."""
        reader = UTF8Reader("hello")
        
        assert reader.read() == "h"
        assert reader.read() == "e"
        assert reader.read() == "l"
    
    def test_peek(self):
        """Test peeking characters."""
        reader = UTF8Reader("hello")
        
        assert reader.peek() == "h"
        assert reader.peek(1) == "e"
        assert reader.peek() == "h"  # Should not consume
    
    def test_eof(self):
        """Test end of file."""
        reader = UTF8Reader("hi")
        
        assert not reader.is_eof
        reader.read()
        reader.read()
        assert reader.is_eof
        assert reader.read() is None
    
    def test_line_tracking(self):
        """Test line tracking."""
        reader = UTF8Reader("line1\nline2\nline3")
        
        assert reader.line == 1
        assert reader.column == 1
        
        reader.read()  # l
        reader.read()  # i
        reader.read()  # n
        reader.read()  # e
        reader.read()  # 1
        reader.read()  # \n
        
        assert reader.line == 2
        assert reader.column == 1
    
    def test_read_while(self):
        """Test reading while condition."""
        reader = UTF8Reader("abc123")
        
        result = reader.read_while(str.isalpha)
        assert result == "abc"
    
    def test_read_until(self):
        """Test reading until target."""
        reader = UTF8Reader("hello world")
        
        result = reader.read_until(" ")
        assert result == "hello"
    
    def test_save_restore(self):
        """Test save and restore."""
        reader = UTF8Reader("hello")
        
        reader.read()  # h
        reader.read()  # e
        saved = reader.save()
        reader.read()  # l
        reader.read()  # l
        
        reader.restore(saved)
        assert reader.peek() == "l"


# ============================================================================
# Identifier Tests
# ============================================================================


class TestIdentifierChecks:
    """Tests for identifier checking functions."""
    
    def test_identifier_start(self):
        """Test identifier start check."""
        assert is_identifier_start("a")
        assert is_identifier_start("Z")
        assert is_identifier_start("_")
        assert is_identifier_start("ñ")
        assert not is_identifier_start("1")
        assert not is_identifier_start(" ")
    
    def test_identifier_part(self):
        """Test identifier part check."""
        assert is_identifier_part("a")
        assert is_identifier_part("1")
        assert is_identifier_part("_")
        assert is_identifier_part("ñ")
        assert not is_identifier_part(" ")
    
    def test_valid_identifier(self):
        """Test valid identifier check."""
        assert is_valid_identifier("name")
        assert is_valid_identifier("_private")
        assert is_valid_identifier("camelCase")
        assert is_valid_identifier("ñame")
        assert not is_valid_identifier("123")
        assert not is_valid_identifier("")
        assert is_valid_identifier("a b") is False


class TestUnicodeUtils:
    """Tests for Unicode utilities."""
    
    def test_get_char_info(self):
        """Test getting character info."""
        info = get_char_info("A")
        
        assert info["char"] == "A"
        assert info["is_alpha"] is True
        assert info["is_digit"] is False
    
    def test_normalize_identifier(self):
        """Test identifier normalization."""
        assert normalize_identifier("Name") == "name"
        assert normalize_identifier("_PRIVATE") == "_private"
