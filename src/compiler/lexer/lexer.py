"""
Lexer Engine for the I Programming Language

DFA-based lexical analyzer implementing the complete tokenization
pipeline: Source → UTF-8 Reader → DFA Engine → Keyword Resolver → Token Stream
"""

from __future__ import annotations

import sys
import unicodedata
from typing import Any, List, Optional

from .token import (
    KEYWORDS,
    KEYWORD_VALUES,
    KINYARWANDA_BOOLEANS,
    Token,
    TokenLocation,
    TokenType,
)
from .errors import LexerError, LexerErrorCode, LexerErrorCollector


# ── Maximum values ────────────────────────────────────────────
MAX_I64 = (2**63) - 1


class Lexer:
    """
    Production-quality lexer for the I programming language.
    
    Implements DFA-based tokenization with:
    - Complete keyword recognition (Kinyarwanda + English)
    - Unicode identifier support
    - All number formats (decimal, hex, octal, binary, float, scientific)
    - All string formats (regular, raw, triple-quoted, escape sequences)
    - All comment formats (single-line, multi-line, documentation)
    - Bilingual error reporting with recovery
    - Source location tracking
    """

    def __init__(self, source: str, filename: str = "<stdin>") -> None:
        """
        Initialize lexer.
        
        Args:
            source: Source code string
            filename: Source filename for error messages
        """
        self._source = source
        self._filename = filename
        self._pos = 0
        self._line = 1
        self._column = 1
        self._tokens: List[Token] = []
        self._errors = LexerErrorCollector()
        self._start_pos = 0
        self._start_line = 1
        self._start_column = 1

    @property
    def tokens(self) -> List[Token]:
        """Tokenized output."""
        return self._tokens

    @property
    def errors(self) -> LexerErrorCollector:
        """Error collector."""
        return self._errors

    @property
    def has_errors(self) -> bool:
        """Check if any errors occurred."""
        return self._errors.has_errors

    def tokenize(self) -> List[Token]:
        """
        Tokenize the entire source.
        
        Returns:
            List of tokens including EOF
        """
        while not self._is_at_end:
            if self._errors.should_abort:
                break
            self._scan_token()

        self._tokens.append(self._make_token(TokenType.EOF, ""))
        return self._tokens

    # ── Core Scanner ───────────────────────────────────────────

    def _scan_token(self) -> None:
        """Scan a single token."""
        self._skip_whitespace()

        if self._is_at_end:
            return

        self._start_pos = self._pos
        self._start_line = self._line
        self._start_column = self._column
        char = self._peek()

        # ── Newlines ──────────────────────────────────────────
        if char == "\n":
            self._advance()
            self._tokens.append(
                self._make_token(TokenType.NEWLINE, "\\n")
            )
            return

        # ── Single-character tokens ───────────────────────────
        single = self._single_char_token(char)
        if single is not None:
            self._advance()
            self._tokens.append(self._make_token(single, char))
            return

        # ── Multi-character operators ─────────────────────────
        if self._scan_operator():
            return

        # ── Comments ──────────────────────────────────────────
        if char == "#":
            self._scan_comment()
            return

        # ── String literals ───────────────────────────────────
        if char == '"':
            self._scan_string()
            return

        if char == "'":
            self._scan_character()
            return

        # ── Numbers ───────────────────────────────────────────
        if self._is_digit(char):
            self._scan_number()
            return

        # ── Identifiers and keywords ──────────────────────────
        if self._is_identifier_start(char):
            self._scan_identifier()
            return

        # ── At-sign ───────────────────────────────────────────
        if char == "@":
            self._advance()
            self._tokens.append(self._make_token(TokenType.AT, "@"))
            return

        # ── Backslash ─────────────────────────────────────────
        if char == "\\":
            self._advance()
            self._tokens.append(self._make_token(TokenType.BACKSLASH, "\\"))
            return

        # ── Unknown character ─────────────────────────────────
        self._errors.add(
            LexerErrorCode.LEX001_INVALID_CHAR,
            self._line,
            self._column,
            self._pos,
            char=char,
        )
        self._advance()

    # ── Single-character tokens ────────────────────────────────

    def _single_char_token(self, char: str) -> Optional[TokenType]:
        """Map single character to token type."""
        mapping = {
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            ",": TokenType.COMMA,
            ":": TokenType.COLON,
            ";": TokenType.SEMICOLON,
            "~": TokenType.TILDE,
        }
        return mapping.get(char)

    # ── Multi-character operators ──────────────────────────────

    def _scan_operator(self) -> bool:
        """Scan multi-character operators. Returns True if an operator was scanned."""
        char = self._peek()

        if char == "+":
            self._advance()
            if self._match("="):
                self._emit(TokenType.PLUS_EQ, "+=")
            else:
                self._emit(TokenType.PLUS, "+")
            return True

        if char == "-":
            self._advance()
            if self._match(">"):
                self._emit(TokenType.ARROW, "->")
            elif self._match("="):
                self._emit(TokenType.MINUS_EQ, "-=")
            else:
                self._emit(TokenType.MINUS, "-")
            return True

        if char == "*":
            self._advance()
            if self._match("*"):
                if self._match("="):
                    self._emit(TokenType.STAR_STAR_EQ, "**=")
                else:
                    self._emit(TokenType.STAR_STAR, "**")
            elif self._match("="):
                self._emit(TokenType.STAR_EQ, "*=")
            else:
                self._emit(TokenType.STAR, "*")
            return True

        if char == "/":
            self._advance()
            if self._match("/"):
                if self._match("="):
                    self._emit(TokenType.SLASH_EQ, "/=")
                else:
                    self._emit(TokenType.SLASH_SLASH, "//")
            elif self._match("="):
                self._emit(TokenType.SLASH_EQ, "/=")
            else:
                self._emit(TokenType.SLASH, "/")
            return True

        if char == "%":
            self._advance()
            if self._match("="):
                self._emit(TokenType.PERCENT_EQ, "%=")
            else:
                self._emit(TokenType.PERCENT, "%")
            return True

        if char == "=":
            self._advance()
            if self._match("="):
                if self._match("="):
                    self._emit(TokenType.IS_EQ, "===")
                else:
                    self._emit(TokenType.EQ_EQ, "==")
            elif self._match(">"):
                self._emit(TokenType.FAT_ARROW, "=>")
            else:
                self._emit(TokenType.EQ, "=")
            return True

        if char == "!":
            self._advance()
            if self._match("="):
                if self._match("="):
                    self._emit(TokenType.BANG_IS_EQ, "!==")
                else:
                    self._emit(TokenType.BANG_EQ, "!=")
            else:
                self._emit(TokenType.BANG, "!")
            return True

        if char == "<":
            self._advance()
            if self._match("="):
                self._emit(TokenType.LT_EQ, "<=")
            elif self._match("<"):
                self._emit(TokenType.LT_LT, "<<")
            else:
                self._emit(TokenType.LT, "<")
            return True

        if char == ">":
            self._advance()
            if self._match("="):
                self._emit(TokenType.GT_EQ, ">=")
            elif self._match(">"):
                if self._match(">"):
                    self._emit(TokenType.GT_GT_GT, ">>>")
                else:
                    self._emit(TokenType.GT_GT, ">>")
            else:
                self._emit(TokenType.GT, ">")
            return True

        if char == "&":
            self._advance()
            if self._match("&"):
                self._emit(TokenType.AND_AND, "&&")
            else:
                self._emit(TokenType.AMP, "&")
            return True

        if char == "|":
            self._advance()
            if self._match("|"):
                self._emit(TokenType.OR_OR, "||")
            else:
                self._emit(TokenType.PIPE, "|")
            return True

        if char == "^":
            self._advance()
            self._emit(TokenType.CARET, "^")
            return True

        if char == ".":
            self._advance()
            if self._match("."):
                if self._match("."):
                    self._emit(TokenType.DOT_DOT_DOT, "...")
                else:
                    self._emit(TokenType.DOT_DOT, "..")
            else:
                self._emit(TokenType.DOT, ".")
            return True

        if char == "?":
            self._advance()
            if self._match("."):
                self._emit(TokenType.QUESTION_DOT, "?.")
            else:
                self._emit(TokenType.QUESTION, "?")
            return True

        return False

    # ── Comments ───────────────────────────────────────────────

    def _scan_comment(self) -> None:
        """Scan comment (# single-line, #= multi-line, /// doc)."""
        self._advance()  # consume #

        # Documentation comment: ///
        if self._match("/") and self._match("/"):
            while not self._is_at_end and self._peek() != "\n":
                self._advance()
            self._errors.record_success()
            return

        # Multi-line comment: #= ... =#
        if self._match("="):
            self._scan_multiline_comment()
            return

        # Single-line comment: # ...
        while not self._is_at_end and self._peek() != "\n":
            self._advance()
        self._errors.record_success()

    def _scan_multiline_comment(self) -> None:
        """Scan #= ... =# multi-line comment."""
        depth = 1
        while not self._is_at_end and depth > 0:
            char = self._peek()
            if char == "\n":
                self._line += 1
                self._column = 1
                self._pos += 1
            elif char == "=" and self._peek_next() == "#":
                self._pos += 2
                self._column += 2
                depth -= 1
            elif char == "#" and self._peek_next() == "=":
                self._pos += 2
                self._column += 2
                depth += 1
            else:
                self._advance()

        if depth > 0:
            self._errors.add(
                LexerErrorCode.LEX006_UNTERMINATED_COMMENT,
                self._line,
                self._column,
                self._pos,
            )
        else:
            self._errors.record_success()

    # ── Strings ────────────────────────────────────────────────

    def _scan_string(self) -> None:
        """Scan string literal (regular, triple-quoted)."""
        start_line = self._line
        start_col = self._column

        self._advance()  # consume opening "

        # Triple-quoted string: """..."""
        if self._peek() == '"' and self._peek_next() == '"':
            self._advance()  # consume second "
            self._advance()  # consume third "
            self._scan_triple_string()
            return

        # Regular string
        self._scan_regular_string()

    def _scan_regular_string(self) -> None:
        """Scan regular double-quoted string."""
        parts: list[str] = []

        while not self._is_at_end:
            char = self._peek()
            if char == '"':
                self._advance()  # consume closing "
                value = "".join(parts)
                self._emit(TokenType.STRING, value)
                self._errors.record_success()
                return
            if char == "\n":
                self._errors.add(
                    LexerErrorCode.LEX002_UNTERMINATED_STRING,
                    self._line,
                    self._column,
                    self._pos,
                )
                return
            if char == "\\":
                escape = self._scan_escape()
                if escape is not None:
                    parts.append(escape)
                continue
            self._advance()
            parts.append(char)

        self._errors.add(
            LexerErrorCode.LEX002_UNTERMINATED_STRING,
            self._line,
            self._column,
            self._pos,
        )

    def _scan_triple_string(self) -> None:
        """Scan triple-quoted string."""
        parts: list[str] = []

        while not self._is_at_end:
            char = self._peek()
            if char == '"':
                if (
                    self._peek_next() == '"'
                    and self._peek_ahead(2) == '"'
                ):
                    self._advance()
                    self._advance()
                    self._advance()
                    value = "".join(parts)
                    self._emit(TokenType.TRIPLE_STRING, value)
                    self._errors.record_success()
                    return
                else:
                    self._advance()
                    parts.append(char)
                    continue
            if char == "\\":
                escape = self._scan_escape()
                if escape is not None:
                    parts.append(escape)
                continue
            if char == "\n":
                self._line += 1
                self._column = 1
            self._advance()
            parts.append(char)

        self._errors.add(
            LexerErrorCode.LEX011_UNTERMINATED_TRIPLE_STRING,
            self._line,
            self._column,
            self._pos,
        )

    def _scan_escape(self) -> Optional[str]:
        """Scan escape sequence. Returns the decoded character or None on error."""
        self._advance()  # consume backslash
        if self._is_at_end:
            return None

        char = self._peek()
        self._advance()

        escape_map = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            "\\": "\\",
            '"': '"',
            "'": "'",
            "0": "\0",
        }

        if char in escape_map:
            return escape_map[char]

        if char == "u":
            return self._scan_unicode_escape(4)
        if char == "U":
            return self._scan_unicode_escape(8)

        self._errors.add(
            LexerErrorCode.LEX005_INVALID_ESCAPE,
            self._line,
            self._column,
            self._pos,
            char=char,
        )
        return char

    def _scan_unicode_escape(self, hex_len: int) -> Optional[str]:
        """Scan \\uXXXX or \\UXXXXXXXX escape."""
        hex_str = ""
        for _ in range(hex_len):
            if self._is_at_end or not self._is_hex_digit(self._peek()):
                self._errors.add(
                    LexerErrorCode.LEX005_INVALID_ESCAPE,
                    self._line,
                    self._column,
                    self._pos,
                    char="u",
                )
                return None
            hex_str += self._advance()

        try:
            codepoint = int(hex_str, 16)
            return chr(codepoint)
        except (ValueError, OverflowError):
            self._errors.add(
                LexerErrorCode.LEX005_INVALID_ESCAPE,
                self._line,
                self._column,
                self._pos,
                char="u",
            )
            return None

    # ── Character literals ─────────────────────────────────────

    def _scan_character(self) -> None:
        """Scan single-quoted character literal."""
        self._advance()  # consume opening '

        if self._is_at_end:
            self._errors.add(
                LexerErrorCode.LEX009_UNTERMINATED_CHAR,
                self._line,
                self._column,
                self._pos,
            )
            return

        char = self._peek()
        if char == "\\":
            value = self._scan_escape()
        else:
            self._advance()
            value = char

        if self._is_at_end or self._peek() != "'":
            self._errors.add(
                LexerErrorCode.LEX009_UNTERMINATED_CHAR,
                self._line,
                self._column,
                self._pos,
            )
            return

        self._advance()  # consume closing '
        self._emit(TokenType.CHARACTER, value)
        self._errors.record_success()

    # ── Numbers ────────────────────────────────────────────────

    def _scan_number(self) -> None:
        """Scan numeric literal."""
        start = self._pos
        char = self._peek()

        # Hex: 0x...
        if char == "0" and self._peek_next() in ("x", "X"):
            self._scan_hex_number()
            return

        # Octal: 0o...
        if char == "0" and self._peek_next() in ("o", "O"):
            self._scan_octal_number()
            return

        # Binary: 0b...
        if char == "0" and self._peek_next() in ("b", "B"):
            self._scan_binary_number()
            return

        # Decimal / Float
        self._scan_decimal_number()

    def _scan_hex_number(self) -> None:
        """Scan hexadecimal number."""
        self._advance()  # 0
        self._advance()  # x

        hex_str = ""
        while not self._is_at_end and (self._is_hex_digit(self._peek()) or self._peek() == "_"):
            if self._peek() != "_":
                hex_str += self._peek()
            self._advance()

        try:
            value = int(hex_str, 16)
            if value > MAX_I64:
                self._errors.add(
                    LexerErrorCode.LEX007_INTEGER_OVERFLOW,
                    self._line,
                    self._column,
                    self._pos,
                )
                value = MAX_I64
            self._emit(TokenType.INTEGER, value)
            self._errors.record_success()
        except ValueError:
            self._errors.add(
                LexerErrorCode.LEX003_INVALID_NUMBER,
                self._line,
                self._column,
                self._pos,
            )

    def _scan_octal_number(self) -> None:
        """Scan octal number."""
        self._advance()  # 0
        self._advance()  # o

        oct_str = ""
        while not self._is_at_end and (self._is_octal_digit(self._peek()) or self._peek() == "_"):
            if self._peek() != "_":
                oct_str += self._peek()
            self._advance()

        try:
            value = int(oct_str, 8)
            if value > MAX_I64:
                self._errors.add(
                    LexerErrorCode.LEX007_INTEGER_OVERFLOW,
                    self._line,
                    self._column,
                    self._pos,
                )
                value = MAX_I64
            self._emit(TokenType.INTEGER, value)
            self._errors.record_success()
        except ValueError:
            self._errors.add(
                LexerErrorCode.LEX003_INVALID_NUMBER,
                self._line,
                self._column,
                self._pos,
            )

    def _scan_binary_number(self) -> None:
        """Scan binary number."""
        self._advance()  # 0
        self._advance()  # b

        bin_str = ""
        while not self._is_at_end and (self._peek() in ("0", "1") or self._peek() == "_"):
            if self._peek() != "_":
                bin_str += self._peek()
            self._advance()

        try:
            value = int(bin_str, 2)
            if value > MAX_I64:
                self._errors.add(
                    LexerErrorCode.LEX007_INTEGER_OVERFLOW,
                    self._line,
                    self._column,
                    self._pos,
                )
                value = MAX_I64
            self._emit(TokenType.INTEGER, value)
            self._errors.record_success()
        except ValueError:
            self._errors.add(
                LexerErrorCode.LEX003_INVALID_NUMBER,
                self._line,
                self._column,
                self._pos,
            )

    def _scan_decimal_number(self) -> None:
        """Scan decimal number (integer or float with optional exponent)."""
        # Integer part
        while not self._is_at_end and (self._is_digit(self._peek()) or self._peek() == "_"):
            self._advance()

        is_float = False

        # Fractional part
        if (
            not self._is_at_end
            and self._peek() == "."
            and self._peek_next() is not None
            and self._is_digit(self._peek_next())
        ):
            is_float = True
            self._advance()  # consume .
            while not self._is_at_end and (self._is_digit(self._peek()) or self._peek() == "_"):
                self._advance()

        # Exponent part
        if not self._is_at_end and self._peek() in ("e", "E"):
            is_float = True
            self._advance()
            if not self._is_at_end and self._peek() in ("+", "-"):
                self._advance()
            while not self._is_at_end and self._is_digit(self._peek()):
                self._advance()

        lexeme = self._get_lexeme()

        if is_float:
            try:
                value = float(lexeme)
                self._emit(TokenType.FLOAT, value)
                self._errors.record_success()
            except ValueError:
                self._errors.add(
                    LexerErrorCode.LEX003_INVALID_NUMBER,
                    self._line,
                    self._column,
                    self._pos,
                )
        else:
            try:
                value = int(lexeme)
                if value > MAX_I64:
                    self._errors.add(
                        LexerErrorCode.LEX007_INTEGER_OVERFLOW,
                        self._line,
                        self._column,
                        self._pos,
                    )
                    value = MAX_I64
                self._emit(TokenType.INTEGER, value)
                self._errors.record_success()
            except ValueError:
                self._errors.add(
                    LexerErrorCode.LEX003_INVALID_NUMBER,
                    self._line,
                    self._column,
                    self._pos,
                )

    # ── Identifiers and Keywords ───────────────────────────────

    def _scan_identifier(self) -> None:
        """Scan identifier or keyword."""
        while not self._is_at_end and self._is_identifier_part(self._peek()):
            self._advance()

        text = self._get_lexeme()

        # Check Kinyarwanda boolean/null literals
        if text in KINYARWANDA_BOOLEANS:
            token_type = KINYARWANDA_BOOLEANS[text]
            self._emit(token_type, KEYWORD_VALUES[token_type])
            self._errors.record_success()
            return

        # Check keywords
        if text in KEYWORDS:
            token_type = KEYWORDS[text]
            value = KEYWORD_VALUES.get(token_type)
            self._emit(token_type, value)
            self._errors.record_success()
            return

        # Regular identifier
        self._emit(TokenType.IDENTIFIER)
        self._errors.record_success()

    # ── Whitespace ─────────────────────────────────────────────

    def _skip_whitespace(self) -> None:
        """Skip whitespace (spaces, tabs, carriage returns)."""
        while not self._is_at_end:
            char = self._peek()
            if char in (" ", "\t", "\r"):
                self._advance()
            else:
                break

    # ── Primitive Operations ───────────────────────────────────

    def _advance(self) -> str:
        """Consume and return current character."""
        char = self._source[self._pos]
        self._pos += 1
        if char == "\n":
            self._line += 1
            self._column = 1
        else:
            self._column += 1
        return char

    def _peek(self) -> Optional[str]:
        """Look at current character without consuming."""
        if self._pos >= len(self._source):
            return None
        return self._source[self._pos]

    def _peek_next(self) -> Optional[str]:
        """Look at next character without consuming."""
        if self._pos + 1 >= len(self._source):
            return None
        return self._source[self._pos + 1]

    def _peek_ahead(self, offset: int) -> Optional[str]:
        """Look ahead by offset characters."""
        idx = self._pos + offset
        if idx >= len(self._source):
            return None
        return self._source[idx]

    def _match(self, expected: str) -> bool:
        """Match and consume expected character."""
        if self._is_at_end or self._source[self._pos] != expected:
            return False
        self._advance()
        return True

    @property
    def _is_at_end(self) -> bool:
        """Check if at end of source."""
        return self._pos >= len(self._source)

    def _get_lexeme(self) -> str:
        """Get lexeme from start position to current position."""
        # We need to track start position
        return self._source[self._start_pos:self._pos]

    def _make_token(self, token_type: TokenType, lexeme: str) -> Token:
        """Create a token with full location metadata."""
        location = TokenLocation(
            line=self._line,
            column=self._column - len(lexeme) if lexeme else self._column,
            offset=self._pos - len(lexeme) if lexeme else self._pos,
            span=len(lexeme.encode("utf-8")),
        )
        return Token(type=token_type, lexeme=lexeme, location=location)

    def _emit(self, token_type: TokenType, value: Any = None) -> None:
        """Create and emit a token."""
        lexeme = self._get_lexeme()
        token = Token(
            type=token_type,
            lexeme=lexeme,
            location=TokenLocation(
                line=self._start_line,
                column=self._start_column,
                offset=self._start_pos,
                span=self._pos - self._start_pos,
            ),
            value=value,
        )
        self._tokens.append(token)

    def _is_digit(self, char: Optional[str]) -> bool:
        """Check if character is a digit."""
        return char is not None and char.isdigit()

    def _is_hex_digit(self, char: Optional[str]) -> bool:
        """Check if character is a hex digit."""
        return char is not None and (
            char.isdigit() or char.lower() in "abcdef"
        )

    def _is_octal_digit(self, char: Optional[str]) -> bool:
        """Check if character is an octal digit."""
        return char is not None and char in "01234567"

    def _is_identifier_start(self, char: Optional[str]) -> bool:
        """Check if character can start an identifier."""
        if char is None:
            return False
        if char.isascii() and (char.isalpha() or char == "_"):
            return True
        if char.isalpha() and not char.isascii():
            return True
        return False

    def _is_identifier_part(self, char: Optional[str]) -> bool:
        """Check if character can be part of an identifier."""
        if char is None:
            return False
        if char.isascii() and (char.isalnum() or char == "_"):
            return True
        if char.isalnum() and not char.isascii():
            return True
        return False


# ── Convenience Function ────────────────────────────────────────

def tokenize(source: str, filename: str = "<stdin>") -> tuple[List[Token], List[LexerError]]:
    """
    Tokenize source code.
    
    Args:
        source: Source code string
        filename: Source filename
        
    Returns:
        Tuple of (tokens, errors)
    """
    lexer = Lexer(source, filename)
    tokens = lexer.tokenize()
    return tokens, lexer.errors.errors
