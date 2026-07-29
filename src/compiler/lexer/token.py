"""
Token System for the I Programming Language

Defines all token types, token structure, and keyword mappings.
Authoritative source: ILS v1.0 and Lexer Design Document.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Any


class TokenType(IntEnum):
    """
    All token types for the I language.

    Using IntEnum for efficient comparison and memory usage.
    """

    # ── Literals ──────────────────────────────────────────────
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    RAW_STRING = auto()
    TRIPLE_STRING = auto()
    CHARACTER = auto()
    BOOLEAN_TRUE = auto()
    BOOLEAN_FALSE = auto()
    NULL = auto()

    # ── Identifier ────────────────────────────────────────────
    IDENTIFIER = auto()

    # ── Keywords: Control Flow ────────────────────────────────
    KW_NIBA = auto()                    # niba (if)
    KW_CYANGWA = auto()                 # cyangwa (else)
    KW_CYANGWA_NIBA = auto()            # cyangwa niba (else if)
    KW_KUGENDA = auto()                 # kugenda (continue)
    KW_GUKOMA = auto()                  # gukoma (break)
    KW_SUBIRA = auto()                  # subira (return)
    KW_TANGA_YIELD = auto()            # tanga (yield)

    # ── Keywords: Loops ───────────────────────────────────────
    KW_KORA = auto()                    # kora (do)
    KW_WIHUSE = auto()                  # wihuse (while)
    KW_KUGEZA = auto()                  # kugeza (until)
    KW_KURI = auto()                    # kuri (for)
    KW_MURI = auto()                    # muri (in)
    KW_BURI = auto()                    # buri (each)

    # ── Keywords: Declarations ────────────────────────────────
    KW_SHYIRA = auto()                  # shyira (let)
    KW_SHYIRA_KO = auto()               # shyira ko (const)
    KW_UMURIMO = auto()                 # umurimo (function)
    KW_IGICERI = auto()                 # igiceri (struct)
    KW_IKINDI = auto()                  # ikindi (enum)
    KW_URWEGO = auto()                  # urwego (class)
    KW_AKABUTO = auto()                 # akabuto (interface)
    KW_URUBINGO = auto()                # urubingo (trait)
    KW_UBWOKO = auto()                  # ubwoko (type)

    # ── Keywords: Instantiation ───────────────────────────────
    KW_KUGIRA = auto()                  # kugira (have/extends)
    KW_GUKORA = auto()                  # gukora (make/new)
    KW_NSHYA = auto()                   # nshya (new)

    # ── Keywords: Modules ─────────────────────────────────────
    KW_SHYIRAMO = auto()                # shyiramo (import)
    KW_TANGA_EXPORT = auto()            # tanga (export)
    KW_KUGIRA_NGO = auto()              # kugira ngo (as)

    # ── Keywords: Logical ─────────────────────────────────────
    KW_KANDI = auto()                   # kandi (and)
    KW_CYANGWA_LOG = auto()             # cyangwa (or)
    KW_BITEWE = auto()                  # bitewe (because)
    KW_ARI = auto()                     # ari (is)
    KW_SI = auto()                      # si (not)

    # ── Keywords: Exceptions ──────────────────────────────────
    KW_GUSHYINGURA = auto()             # gushyingura (throw)
    KW_KUBIKA = auto()                  # kubika (catch)
    KW_IKINYOMA = auto()                # ikinyoma (finally)

    # ── Keywords: Blocks ──────────────────────────────────────
    KW_IHEREZO = auto()                 # iherezo (end)

    # ── Keywords: Types / References ──────────────────────────
    KW_SELF = auto()                    # self
    KW_SUPER = auto()                   # super
    KW_TRUE_EN = auto()                 # true (English)
    KW_FALSE_EN = auto()                # false (English)
    KW_NULL_EN = auto()                 # null (English)

    # ── Arithmetic Operators ──────────────────────────────────
    PLUS = auto()                       # +
    MINUS = auto()                      # -
    STAR = auto()                       # *
    SLASH = auto()                      # /
    PERCENT = auto()                    # %
    STAR_STAR = auto()                  # **
    SLASH_SLASH = auto()                # //

    # ── Comparison Operators ──────────────────────────────────
    EQ_EQ = auto()                      # ==
    BANG_EQ = auto()                    # !=
    GT = auto()                         # >
    LT = auto()                         # <
    GT_EQ = auto()                      # >=
    LT_EQ = auto()                      # <=
    IS_EQ = auto()                      # ===
    BANG_IS_EQ = auto()                 # !==

    # ── Logical Operators ─────────────────────────────────────
    AND_AND = auto()                    # &&
    OR_OR = auto()                      # ||
    BANG = auto()                       # !

    # ── Bitwise Operators ─────────────────────────────────────
    AMP = auto()                        # &
    PIPE = auto()                       # |
    CARET = auto()                      # ^
    TILDE = auto()                      # ~
    LT_LT = auto()                      # <<
    GT_GT = auto()                      # >>
    GT_GT_GT = auto()                   # >>>

    # ── Assignment Operators ──────────────────────────────────
    EQ = auto()                         # =
    PLUS_EQ = auto()                    # +=
    MINUS_EQ = auto()                   # -=
    STAR_EQ = auto()                    # *=
    SLASH_EQ = auto()                   # /=
    PERCENT_EQ = auto()                 # %=
    STAR_STAR_EQ = auto()               # **=

    # ── Delimiters ────────────────────────────────────────────
    LPAREN = auto()                     # (
    RPAREN = auto()                     # )
    LBRACKET = auto()                   # [
    RBRACKET = auto()                   # ]
    LBRACE = auto()                     # {
    RBRACE = auto()                     # }
    COMMA = auto()                      # ,
    COLON = auto()                      # :
    SEMICOLON = auto()                  # ;
    DOT = auto()                        # .
    DOT_DOT = auto()                    # ..
    DOT_DOT_DOT = auto()                # ...
    ARROW = auto()                      # ->
    FAT_ARROW = auto()                  # =>
    QUESTION = auto()                   # ?
    QUESTION_DOT = auto()               # ?.
    AT = auto()                         # @
    BACKSLASH = auto()                  # \

    # ── Special ───────────────────────────────────────────────
    EOF = auto()
    NEWLINE = auto()

    # ── Error ─────────────────────────────────────────────────
    ERROR = auto()

    def __str__(self) -> str:
        return self.name


# ── Token Metadata ───────────────────────────────────────────────

@dataclass(frozen=True)
class TokenLocation:
    """Immutable source location for a token."""

    line: int            # 1-indexed line number
    column: int          # 1-indexed column number
    offset: int          # Byte offset from start of file
    span: int            # Length in bytes

    def __str__(self) -> str:
        return f"{self.line}:{self.column}"


@dataclass(frozen=True)
class Token:
    """
    A single token produced by the lexer.

    Immutable value type with complete metadata.
    """

    type: TokenType
    lexeme: str
    location: TokenLocation
    value: Any = None

    @property
    def line(self) -> int:
        """Line number (1-indexed)."""
        return self.location.line

    @property
    def column(self) -> int:
        """Column number (1-indexed)."""
        return self.location.column

    @property
    def offset(self) -> int:
        """Byte offset."""
        return self.location.offset

    @property
    def span(self) -> int:
        """Token length in bytes."""
        return self.location.span

    @property
    def end_offset(self) -> int:
        """End byte offset."""
        return self.location.offset + self.location.span

    def is_keyword(self) -> bool:
        """Check if this is a keyword token."""
        return TokenType.KW_NIBA <= self.type <= TokenType.KW_NULL_EN

    def is_operator(self) -> bool:
        """Check if this is an operator token."""
        return TokenType.PLUS <= self.type <= TokenType.BACKSLASH

    def is_literal(self) -> bool:
        """Check if this is a literal token."""
        return self.type in (
            TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING,
            TokenType.RAW_STRING, TokenType.TRIPLE_STRING,
            TokenType.CHARACTER, TokenType.BOOLEAN_TRUE,
            TokenType.BOOLEAN_FALSE, TokenType.NULL,
        )

    def __repr__(self) -> str:
        if self.value is not None:
            return (
                f"Token({self.type.name}, {self.lexeme!r}, "
                f"value={self.value!r}, {self.location})"
            )
        return f"Token({self.type.name}, {self.lexeme!r}, {self.location})"


# ── Keyword Mapping ──────────────────────────────────────────────

# Kinyarwanda keywords → TokenType
# Note: 'tanga' and 'cyangwa' map to multiple tokens contextually.
# The lexer resolves 'tanga' → KW_TANGA_YIELD, 'tanga' at statement
# start with following expression → KW_TANGA_EXPORT. For simplicity,
# we map 'tanga' to KW_TANGA_YIELD by default and the parser can
# reclassify. Same for 'cyangwa'.
KEYWORDS: dict[str, TokenType] = {
    # Control flow
    "niba": TokenType.KW_NIBA,
    "cyangwa": TokenType.KW_CYANGWA,
    "cyangwa_niba": TokenType.KW_CYANGWA_NIBA,
    "kugenda": TokenType.KW_KUGENDA,
    "gukoma": TokenType.KW_GUKOMA,
    "subira": TokenType.KW_SUBIRA,
    "tanga": TokenType.KW_TANGA_YIELD,

    # Loops
    "kora": TokenType.KW_KORA,
    "wihuse": TokenType.KW_WIHUSE,
    "kugeza": TokenType.KW_KUGEZA,
    "kuri": TokenType.KW_KURI,
    "muri": TokenType.KW_MURI,
    "buri": TokenType.KW_BURI,

    # Declarations
    "shyira": TokenType.KW_SHYIRA,
    "shyira_ko": TokenType.KW_SHYIRA_KO,
    "umurimo": TokenType.KW_UMURIMO,
    "igiceri": TokenType.KW_IGICERI,
    "ikindi": TokenType.KW_IKINDI,
    "urwego": TokenType.KW_URWEGO,
    "akabuto": TokenType.KW_AKABUTO,
    "urubingo": TokenType.KW_URUBINGO,
    "ubwoko": TokenType.KW_UBWOKO,

    # Instantiation
    "kugira": TokenType.KW_KUGIRA,
    "gukora": TokenType.KW_GUKORA,
    "nshya": TokenType.KW_NSHYA,

    # Modules
    "shyiramo": TokenType.KW_SHYIRAMO,
    "kugira_ngo": TokenType.KW_KUGIRA_NGO,

    # Logical
    "kandi": TokenType.KW_KANDI,
    "bitewe": TokenType.KW_BITEWE,
    "ari": TokenType.KW_ARI,
    "si": TokenType.KW_SI,

    # Exceptions
    "gushyingura": TokenType.KW_GUSHYINGURA,
    "kubika": TokenType.KW_KUBIKA,
    "ikinyoma": TokenType.KW_IKINYOMA,

    # Blocks
    "iherezo": TokenType.KW_IHEREZO,

    # References
    "self": TokenType.KW_SELF,
    "super": TokenType.KW_SUPER,

    # English aliases
    "true": TokenType.KW_TRUE_EN,
    "false": TokenType.KW_FALSE_EN,
    "null": TokenType.KW_NULL_EN,
}

# Boolean/null keyword values
KEYWORD_VALUES: dict[TokenType, Any] = {
    TokenType.BOOLEAN_TRUE: True,
    TokenType.KW_TRUE_EN: True,
    TokenType.BOOLEAN_FALSE: False,
    TokenType.KW_FALSE_EN: False,
    TokenType.NULL: None,
    TokenType.KW_NULL_EN: None,
}

# Kinyarwanda literal keywords
KINYARWANDA_LITERALS: dict[str, TokenType] = {
    "yego": TokenType.BOOLEAN_TRUE,
    "oya": TokenType.BOOLEAN_FALSE,
    "ubusa": TokenType.NULL,
}
