"""
Comprehensive Lexer Test Suite

Tests all aspects of the I language lexer:
- Token types
- Keywords (Kinyarwanda + English)
- Identifiers (ASCII + Unicode)
- Number literals
- String literals
- Comments
- Operators
- Delimiters
- Error handling
- Edge cases
"""


from src.compiler.lexer import (
    LexerError,
    LexerErrorCode,
    Token,
    TokenType,
    tokenize,
)

# ══════════════════════════════════════════════════════════════════
# Helper
# ══════════════════════════════════════════════════════════════════


def lex(source: str) -> list[Token]:
    """Tokenize and return non-EOF, non-NEWLINE tokens."""
    tokens, _ = tokenize(source)
    return [t for t in tokens if t.type not in (TokenType.EOF, TokenType.NEWLINE)]


def lex_all(source: str) -> list[Token]:
    """Tokenize and return all tokens."""
    tokens, _ = tokenize(source)
    return tokens


def lex_errors(source: str) -> list[LexerError]:
    """Tokenize and return errors."""
    _, errors = tokenize(source)
    return errors


def assert_token_type(source: str, expected: TokenType) -> None:
    """Assert that source produces a single token of expected type."""
    tokens = lex(source)
    assert len(tokens) == 1
    assert tokens[0].type == expected


def assert_tokens(source: str, *expected_types: TokenType) -> None:
    """Assert that source produces tokens of expected types."""
    tokens = lex(source)
    actual = [t.type for t in tokens]
    assert actual == list(expected_types)


# ══════════════════════════════════════════════════════════════════
# Token Structure Tests
# ══════════════════════════════════════════════════════════════════


class TestTokenStructure:
    """Tests for Token data structure."""

    def test_token_creation(self):
        """Test creating a token."""
        token = Token(
            type=TokenType.INTEGER,
            lexeme="42",
            location=None,
            value=42,
        )
        assert token.type == TokenType.INTEGER
        assert token.lexeme == "42"
        assert token.value == 42

    def test_token_repr(self):
        """Test token string representation."""
        from src.compiler.lexer.token import TokenLocation
        loc = TokenLocation(line=1, column=1, offset=0, span=1)
        token = Token(type=TokenType.PLUS, lexeme="+", location=loc)
        assert "PLUS" in repr(token)

    def test_token_is_keyword(self):
        """Test keyword detection."""
        from src.compiler.lexer.token import TokenLocation
        loc = TokenLocation(line=1, column=1, offset=0, span=4)
        token = Token(type=TokenType.KW_NIBA, lexeme="niba", location=loc)
        assert token.is_keyword()

    def test_token_is_operator(self):
        """Test operator detection."""
        from src.compiler.lexer.token import TokenLocation
        loc = TokenLocation(line=1, column=1, offset=0, span=1)
        token = Token(type=TokenType.PLUS, lexeme="+", location=loc)
        assert token.is_operator()

    def test_token_is_literal(self):
        """Test literal detection."""
        from src.compiler.lexer.token import TokenLocation
        loc = TokenLocation(line=1, column=1, offset=0, span=2)
        token = Token(type=TokenType.INTEGER, lexeme="42", location=loc, value=42)
        assert token.is_literal()


# ══════════════════════════════════════════════════════════════════
# Keyword Recognition Tests
# ══════════════════════════════════════════════════════════════════


class TestKeywords:
    """Tests for keyword recognition."""

    def test_control_flow_keywords(self):
        """Test control flow keywords."""
        assert_token_type("niba", TokenType.KW_NIBA)
        assert_token_type("cyangwa", TokenType.KW_CYANGWA)
        assert_token_type("cyangwa_niba", TokenType.KW_CYANGWA_NIBA)
        assert_token_type("kugenda", TokenType.KW_KUGENDA)
        assert_token_type("gukoma", TokenType.KW_GUKOMA)
        assert_token_type("subira", TokenType.KW_SUBIRA)
        assert_token_type("tanga", TokenType.KW_TANGA_YIELD)

    def test_loop_keywords(self):
        """Test loop keywords."""
        assert_token_type("kora", TokenType.KW_KORA)
        assert_token_type("wihuse", TokenType.KW_WIHUSE)
        assert_token_type("kugeza", TokenType.KW_KUGEZA)
        assert_token_type("kuri", TokenType.KW_KURI)
        assert_token_type("muri", TokenType.KW_MURI)
        assert_token_type("buri", TokenType.KW_BURI)

    def test_declaration_keywords(self):
        """Test declaration keywords."""
        assert_token_type("shyira", TokenType.KW_SHYIRA)
        assert_token_type("shyira_ko", TokenType.KW_SHYIRA_KO)
        assert_token_type("umurimo", TokenType.KW_UMURIMO)
        assert_token_type("igiceri", TokenType.KW_IGICERI)
        assert_token_type("ikindi", TokenType.KW_IKINDI)
        assert_token_type("urwego", TokenType.KW_URWEGO)
        assert_token_type("akabuto", TokenType.KW_AKABUTO)
        assert_token_type("urubingo", TokenType.KW_URUBINGO)
        assert_token_type("ubwoko", TokenType.KW_UBWOKO)

    def test_instantiation_keywords(self):
        """Test instantiation keywords."""
        assert_token_type("kugira", TokenType.KW_KUGIRA)
        assert_token_type("gukora", TokenType.KW_GUKORA)
        assert_token_type("nshya", TokenType.KW_NSHYA)

    def test_module_keywords(self):
        """Test module keywords."""
        assert_token_type("shyiramo", TokenType.KW_SHYIRAMO)
        assert_token_type("kugira_ngo", TokenType.KW_KUGIRA_NGO)

    def test_logical_keywords(self):
        """Test logical keywords."""
        assert_token_type("kandi", TokenType.KW_KANDI)
        assert_token_type("bitewe", TokenType.KW_BITEWE)
        assert_token_type("ari", TokenType.KW_ARI)
        assert_token_type("si", TokenType.KW_SI)

    def test_exception_keywords(self):
        """Test exception keywords."""
        assert_token_type("gushyingura", TokenType.KW_GUSHYINGURA)
        assert_token_type("kubika", TokenType.KW_KUBIKA)
        assert_token_type("ikinyoma", TokenType.KW_IKINYOMA)

    def test_block_keywords(self):
        """Test block keywords."""
        assert_token_type("iherezo", TokenType.KW_IHEREZO)

    def test_type_keywords(self):
        """Test type keywords."""
        assert_token_type("self", TokenType.KW_SELF)
        assert_token_type("super", TokenType.KW_SUPER)

    def test_english_boolean_keywords(self):
        """Test English boolean keywords."""
        assert_token_type("true", TokenType.KW_TRUE_EN)
        assert_token_type("false", TokenType.KW_FALSE_EN)
        assert_token_type("null", TokenType.KW_NULL_EN)

    def test_kinyarwanda_literals(self):
        """Test Kinyarwanda literal keywords."""
        assert_token_type("yego", TokenType.BOOLEAN_TRUE)
        assert_token_type("oya", TokenType.BOOLEAN_FALSE)
        assert_token_type("ubusa", TokenType.NULL)


# ══════════════════════════════════════════════════════════════════
# Identifier Tests
# ══════════════════════════════════════════════════════════════════


class TestIdentifiers:
    """Tests for identifier handling."""

    def test_simple_identifier(self):
        """Test simple identifiers."""
        assert_token_type("name", TokenType.IDENTIFIER)
        assert_token_type("_private", TokenType.IDENTIFIER)
        assert_token_type("camelCase", TokenType.IDENTIFIER)

    def test_identifier_with_underscore(self):
        """Test identifiers with underscores."""
        assert_token_type("my_var", TokenType.IDENTIFIER)
        assert_token_type("_leading", TokenType.IDENTIFIER)
        assert_token_type("trailing_", TokenType.IDENTIFIER)

    def test_unicode_identifier(self):
        """Test Unicode identifiers."""
        tokens = lex("umurimo")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.KW_UMURIMO

    def test_kinyarwanda_identifier(self):
        """Test Kinyarwanda identifiers."""
        tokens = lex("igice")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.IDENTIFIER

    def test_not_identifier_start_with_digit(self):
        """Test that identifiers can't start with digit."""
        assert_tokens("123abc", TokenType.INTEGER, TokenType.IDENTIFIER)

    def test_keyword_vs_identifier(self):
        """Test that keywords are recognized over identifiers."""
        tokens = lex("niba")
        assert tokens[0].type == TokenType.KW_NIBA

        tokens = lex("nibaX")
        assert tokens[0].type == TokenType.IDENTIFIER


# ══════════════════════════════════════════════════════════════════
# Number Literals Tests
# ══════════════════════════════════════════════════════════════════


class TestNumberLiterals:
    """Tests for number literal handling."""

    def test_integer(self):
        """Test integer literals."""
        tokens = lex("42")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == 42

    def test_zero(self):
        """Test zero literal."""
        tokens = lex("0")
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == 0

    def test_large_integer(self):
        """Test large integer."""
        tokens = lex("1234567890")
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == 1234567890

    def test_integer_with_underscores(self):
        """Test integer with underscores."""
        tokens = lex("1_000_000")
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == 1000000

    def test_hex_number(self):
        """Test hex literal."""
        tokens = lex("0xFF")
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == 255

    def test_hex_uppercase(self):
        """Test hex uppercase."""
        tokens = lex("0XAB")
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == 0xAB

    def test_hex_with_underscores(self):
        """Test hex with underscores."""
        tokens = lex("0xFF_FF")
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == 0xFFFF

    def test_octal_number(self):
        """Test octal literal."""
        tokens = lex("0o77")
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == 0o77

    def test_octal_with_underscores(self):
        """Test octal with underscores."""
        tokens = lex("0o1_234")
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == 0o1234

    def test_binary_number(self):
        """Test binary literal."""
        tokens = lex("0b1010")
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == 10

    def test_binary_with_underscores(self):
        """Test binary with underscores."""
        tokens = lex("0b1_000_000")
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[0].value == 64

    def test_float(self):
        """Test float literal."""
        tokens = lex("3.14")
        assert tokens[0].type == TokenType.FLOAT
        assert tokens[0].value == 3.14

    def test_float_no_integer_part(self):
        """Test float without integer part."""
        tokens = lex(".5")
        assert tokens[0].type == TokenType.FLOAT
        assert tokens[0].value == 0.5

    def test_float_with_exponent(self):
        """Test float with exponent."""
        tokens = lex("1e10")
        assert tokens[0].type == TokenType.FLOAT
        assert tokens[0].value == 1e10

    def test_float_with_negative_exponent(self):
        """Test float with negative exponent."""
        tokens = lex("1e-5")
        assert tokens[0].type == TokenType.FLOAT
        assert tokens[0].value == 1e-5

    def test_float_with_positive_exponent(self):
        """Test float with positive exponent."""
        tokens = lex("1E+5")
        assert tokens[0].type == TokenType.FLOAT
        assert tokens[0].value == 1e5

    def test_float_full(self):
        """Test full float with fractional and exponent."""
        tokens = lex("3.14e2")
        assert tokens[0].type == TokenType.FLOAT
        assert tokens[0].value == 314.0


# ══════════════════════════════════════════════════════════════════
# String Literals Tests
# ══════════════════════════════════════════════════════════════════


class TestStringLiterals:
    """Tests for string literal handling."""

    def test_simple_string(self):
        """Test simple string."""
        tokens = lex('"hello"')
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello"

    def test_empty_string(self):
        """Test empty string."""
        tokens = lex('""')
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == ""

    def test_string_with_space(self):
        """Test string with space."""
        tokens = lex('"hello world"')
        assert tokens[0].value == "hello world"

    def test_string_escape_newline(self):
        """Test string with newline escape."""
        tokens = lex('"hello\\nworld"')
        assert tokens[0].value == "hello\nworld"

    def test_string_escape_tab(self):
        """Test string with tab escape."""
        tokens = lex('"hello\\tworld"')
        assert tokens[0].value == "hello\tworld"

    def test_string_escape_backslash(self):
        """Test string with backslash escape."""
        tokens = lex('"hello\\\\"')
        assert tokens[0].value == "hello\\"

    def test_string_escape_quote(self):
        """Test string with quote escape."""
        tokens = lex('"hello\\""')
        assert tokens[0].value == 'hello"'

    def test_string_escape_null(self):
        """Test string with null escape."""
        tokens = lex('"hello\\0world"')
        assert tokens[0].value == "hello\0world"

    def test_string_unicode_escape(self):
        """Test string with Unicode escape."""
        tokens = lex('"\\u0041"')
        assert tokens[0].value == "A"

    def test_string_long_unicode_escape(self):
        """Test string with long Unicode escape."""
        tokens = lex('"\\U0001F600"')
        assert tokens[0].value == "\U0001F600"

    def test_triple_string(self):
        """Test triple-quoted string."""
        tokens = lex('"""hello"""')
        assert tokens[0].type == TokenType.TRIPLE_STRING
        assert tokens[0].value == "hello"

    def test_triple_string_multiline(self):
        """Test triple-quoted multiline string."""
        source = '"""\nhello\nworld\n"""'
        tokens = lex(source)
        assert tokens[0].type == TokenType.TRIPLE_STRING
        assert "hello" in tokens[0].value
        assert "world" in tokens[0].value


# ══════════════════════════════════════════════════════════════════
# Character Literals Tests
# ══════════════════════════════════════════════════════════════════


class TestCharacterLiterals:
    """Tests for character literal handling."""

    def test_simple_char(self):
        """Test simple character."""
        tokens = lex("'a'")
        assert tokens[0].type == TokenType.CHARACTER
        assert tokens[0].value == "a"

    def test_digit_char(self):
        """Test digit character."""
        tokens = lex("'0'")
        assert tokens[0].type == TokenType.CHARACTER
        assert tokens[0].value == "0"

    def test_unicode_char(self):
        """Test Unicode character."""
        tokens = lex("'ñ'")
        assert tokens[0].type == TokenType.CHARACTER
        assert tokens[0].value == "ñ"

    def test_escape_char(self):
        """Test escape character."""
        tokens = lex("'\\n'")
        assert tokens[0].type == TokenType.CHARACTER
        assert tokens[0].value == "\n"


# ══════════════════════════════════════════════════════════════════
# Comment Tests
# ══════════════════════════════════════════════════════════════════


class TestComments:
    """Tests for comment handling."""

    def test_single_line_comment(self):
        """Test single-line comment is skipped."""
        tokens = lex("42 # this is a comment")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.INTEGER

    def test_multi_line_comment(self):
        """Test multi-line comment is skipped."""
        source = "42 #= this is\na comment =# 42"
        tokens = lex(source)
        assert len(tokens) == 2
        assert all(t.type == TokenType.INTEGER for t in tokens)

    def test_nested_multi_line_comment(self):
        """Test nested multi-line comment."""
        source = "#= outer #= inner =# =#"
        tokens, errors = tokenize(source)
        assert len(errors) == 0

    def test_doc_comment(self):
        """Test documentation comment (#//) is skipped."""
        tokens = lex("#// this is a doc comment\n42")
        assert len(tokens) == 1
        assert tokens[0].type == TokenType.INTEGER

    def test_unterminated_comment(self):
        """Test unterminated multi-line comment error."""
        source = "#= unterminated"
        errors = lex_errors(source)
        assert any(e.code == LexerErrorCode.LEX006_UNTERMINATED_COMMENT for e in errors)


# ══════════════════════════════════════════════════════════════════
# Operator Tests
# ══════════════════════════════════════════════════════════════════


class TestOperators:
    """Tests for operator recognition."""

    def test_arithmetic_operators(self):
        """Test arithmetic operators."""
        assert_token_type("+", TokenType.PLUS)
        assert_token_type("-", TokenType.MINUS)
        assert_token_type("*", TokenType.STAR)
        assert_token_type("/", TokenType.SLASH)
        assert_token_type("%", TokenType.PERCENT)
        assert_token_type("**", TokenType.STAR_STAR)
        assert_token_type("//", TokenType.SLASH_SLASH)

    def test_comparison_operators(self):
        """Test comparison operators."""
        assert_token_type("==", TokenType.EQ_EQ)
        assert_token_type("!=", TokenType.BANG_EQ)
        assert_token_type(">", TokenType.GT)
        assert_token_type("<", TokenType.LT)
        assert_token_type(">=", TokenType.GT_EQ)
        assert_token_type("<=", TokenType.LT_EQ)
        assert_token_type("===", TokenType.IS_EQ)
        assert_token_type("!==", TokenType.BANG_IS_EQ)

    def test_logical_operators(self):
        """Test logical operators."""
        assert_token_type("&&", TokenType.AND_AND)
        assert_token_type("||", TokenType.OR_OR)
        assert_token_type("!", TokenType.BANG)

    def test_bitwise_operators(self):
        """Test bitwise operators."""
        assert_token_type("&", TokenType.AMP)
        assert_token_type("|", TokenType.PIPE)
        assert_token_type("^", TokenType.CARET)
        assert_token_type("~", TokenType.TILDE)
        assert_token_type("<<", TokenType.LT_LT)
        assert_token_type(">>", TokenType.GT_GT)
        assert_token_type(">>>", TokenType.GT_GT_GT)

    def test_assignment_operators(self):
        """Test assignment operators."""
        assert_token_type("=", TokenType.EQ)
        assert_token_type("+=", TokenType.PLUS_EQ)
        assert_token_type("-=", TokenType.MINUS_EQ)
        assert_token_type("*=", TokenType.STAR_EQ)
        assert_token_type("/=", TokenType.SLASH_EQ)
        assert_token_type("%=", TokenType.PERCENT_EQ)
        assert_token_type("**=", TokenType.STAR_STAR_EQ)

    def test_arrow_operators(self):
        """Test arrow operators."""
        assert_token_type("->", TokenType.ARROW)
        assert_token_type("=>", TokenType.FAT_ARROW)

    def test_dot_operators(self):
        """Test dot operators."""
        assert_token_type(".", TokenType.DOT)
        assert_token_type("..", TokenType.DOT_DOT)
        assert_token_type("...", TokenType.DOT_DOT_DOT)

    def test_question_operators(self):
        """Test question operators."""
        assert_token_type("?", TokenType.QUESTION)
        assert_token_type("?.", TokenType.QUESTION_DOT)

    def test_at_sign(self):
        """Test @ operator."""
        assert_token_type("@", TokenType.AT)

    def test_backslash(self):
        """Test \\ operator."""
        assert_token_type("\\", TokenType.BACKSLASH)

    def test_minus_arrow(self):
        """Test -> arrow."""
        assert_tokens("->", TokenType.ARROW)

    def test_plus_equals(self):
        """Test += operator."""
        assert_tokens("+=", TokenType.PLUS_EQ)


# ══════════════════════════════════════════════════════════════════
# Delimiter Tests
# ══════════════════════════════════════════════════════════════════


class TestDelimiters:
    """Tests for delimiter recognition."""

    def test_parentheses(self):
        """Test parentheses."""
        assert_token_type("(", TokenType.LPAREN)
        assert_token_type(")", TokenType.RPAREN)

    def test_brackets(self):
        """Test brackets."""
        assert_token_type("[", TokenType.LBRACKET)
        assert_token_type("]", TokenType.RBRACKET)

    def test_braces(self):
        """Test braces."""
        assert_token_type("{", TokenType.LBRACE)
        assert_token_type("}", TokenType.RBRACE)

    def test_comma(self):
        """Test comma."""
        assert_token_type(",", TokenType.COMMA)

    def test_colon(self):
        """Test colon."""
        assert_token_type(":", TokenType.COLON)

    def test_semicolon(self):
        """Test semicolon."""
        assert_token_type(";", TokenType.SEMICOLON)

    def test_tilde(self):
        """Test tilde."""
        assert_token_type("~", TokenType.TILDE)


# ══════════════════════════════════════════════════════════════════
# Whitespace and Newline Tests
# ══════════════════════════════════════════════════════════════════


class TestWhitespace:
    """Tests for whitespace handling."""

    def test_spaces_skipped(self):
        """Test that spaces are skipped."""
        tokens = lex("42   +   42")
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[1].type == TokenType.PLUS
        assert tokens[2].type == TokenType.INTEGER

    def test_tabs_skipped(self):
        """Test that tabs are skipped."""
        tokens = lex("42\t+\t42")
        assert len(tokens) == 3

    def test_newlines_tracked(self):
        """Test that newlines produce tokens."""
        tokens = lex_all("42\n42")
        newlines = [t for t in tokens if t.type == TokenType.NEWLINE]
        assert len(newlines) == 1

    def test_multiple_newlines(self):
        """Test multiple newlines."""
        tokens = lex_all("42\n\n\n42")
        newlines = [t for t in tokens if t.type == TokenType.NEWLINE]
        assert len(newlines) == 3


# ══════════════════════════════════════════════════════════════════
# Source Location Tests
# ══════════════════════════════════════════════════════════════════


class TestSourceLocation:
    """Tests for source location tracking."""

    def test_first_token_location(self):
        """Test first token location."""
        tokens, _ = tokenize("hello")
        token = tokens[0]
        assert token.line == 1
        assert token.column == 1
        assert token.offset == 0

    def test_token_after_space(self):
        """Test token after space."""
        tokens, _ = tokenize("  hello")
        token = tokens[0]
        assert token.column == 3

    def test_token_on_second_line(self):
        """Test token on second line."""
        tokens, _ = tokenize("hello\nworld")
        hello = tokens[0]
        world = tokens[2]  # after NEWLINE
        assert hello.line == 1
        assert world.line == 2

    def test_span(self):
        """Test token span."""
        tokens, _ = tokenize("hello")
        token = tokens[0]
        assert token.span == 5  # "hello" is 5 bytes


# ══════════════════════════════════════════════════════════════════
# Error Handling Tests
# ══════════════════════════════════════════════════════════════════


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_character(self):
        """Test invalid character error."""
        errors = lex_errors("`")
        assert len(errors) > 0
        assert errors[0].code == LexerErrorCode.LEX001_INVALID_CHAR

    def test_unterminated_string(self):
        """Test unterminated string error."""
        errors = lex_errors('"hello')
        assert len(errors) > 0
        assert errors[0].code == LexerErrorCode.LEX002_UNTERMINATED_STRING

    def test_invalid_escape_sequence(self):
        """Test invalid escape sequence error."""
        errors = lex_errors('"\\q"')
        assert len(errors) > 0
        assert errors[0].code == LexerErrorCode.LEX005_INVALID_ESCAPE

    def test_unterminated_comment(self):
        """Test unterminated comment error."""
        errors = lex_errors("#= hello")
        assert len(errors) > 0
        assert errors[0].code == LexerErrorCode.LEX006_UNTERMINATED_COMMENT

    def test_error_recovery(self):
        """Test error recovery continues tokenizing."""
        tokens, errors = tokenize("42 ` 42")
        assert len(errors) > 0
        # Should still have tokens after the error
        ints = [t for t in tokens if t.type == TokenType.INTEGER]
        assert len(ints) >= 2

    def test_bilingual_error_message(self):
        """Test error has bilingual messages."""
        errors = lex_errors("`")
        assert len(errors) > 0
        error = errors[0]
        assert error.message_en
        assert error.message_rw

    def test_error_suggestion(self):
        """Test error has suggestion."""
        errors = lex_errors('"hello')
        assert len(errors) > 0
        assert errors[0].suggestion

    def test_error_location(self):
        """Test error has correct location."""
        errors = lex_errors("42 `")
        assert len(errors) > 0
        assert errors[0].line == 1
        assert errors[0].column == 4


# ══════════════════════════════════════════════════════════════════
# Edge Case Tests
# ══════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_source(self):
        """Test empty source."""
        tokens, _ = tokenize("")
        assert len(tokens) == 1  # just EOF
        assert tokens[0].type == TokenType.EOF

    def test_whitespace_only(self):
        """Test whitespace-only source."""
        tokens, _ = tokenize("   \t\t  ")
        assert tokens[-1].type == TokenType.EOF

    def test_comment_only(self):
        """Test comment-only source."""
        tokens, _ = tokenize("# just a comment")
        assert tokens[-1].type == TokenType.EOF

    def test_multiple_tokens(self):
        """Test multiple tokens."""
        tokens = lex("42 + 42")
        assert len(tokens) == 3
        assert tokens[0].type == TokenType.INTEGER
        assert tokens[1].type == TokenType.PLUS
        assert tokens[2].type == TokenType.INTEGER

    def test_consecutive_operators(self):
        """Test consecutive operators."""
        tokens = lex("=====")
        # Greedy matching: === ==
        types = [t.type for t in tokens]
        assert types == [TokenType.IS_EQ, TokenType.EQ_EQ]

    def test_dot_dot_dot(self):
        """Test ... (spread)."""
        tokens = lex("...")
        assert tokens[0].type == TokenType.DOT_DOT_DOT

    def test_question_dot(self):
        """Test ?. (optional chaining)."""
        tokens = lex("?.")
        assert tokens[0].type == TokenType.QUESTION_DOT

    def test_fat_arrow(self):
        """Test => (fat arrow)."""
        tokens = lex("=>")
        assert tokens[0].type == TokenType.FAT_ARROW

    def test_minus_arrow(self):
        """Test -> (arrow)."""
        tokens = lex("->")
        assert tokens[0].type == TokenType.ARROW

    def test_triple_question(self):
        """Test >>> (unsigned right shift)."""
        tokens = lex(">>>")
        assert tokens[0].type == TokenType.GT_GT_GT

    def test_triple_equal(self):
        """Test === (identity)."""
        tokens = lex("===")
        assert tokens[0].type == TokenType.IS_EQ

    def test_bang_equal_equal(self):
        """Test !== (not identity)."""
        tokens = lex("!==")
        assert tokens[0].type == TokenType.BANG_IS_EQ


# ══════════════════════════════════════════════════════════════════
# Kinyarwanda Source Code Tests
# ══════════════════════════════════════════════════════════════════


class TestKinyarwandaSource:
    """Tests for Kinyarwanda source code."""

    def test_hello_world(self):
        """Test Hello World in Kinyarwanda."""
        source = """
# Iyumuriro rya mbere
shyira izina = "Amakuru y'Isi"
"""
        tokens, errors = tokenize(source)
        assert len(errors) == 0

    def test_function_definition(self):
        """Test function definition."""
        source = """
umurimo soma(umubare) kora
    subira umubare * 2
iherezo
"""
        tokens, errors = tokenize(source)
        assert len(errors) == 0
        funcs = [t for t in tokens if t.type == TokenType.KW_UMURIMO]
        assert len(funcs) == 1

    def test_if_else(self):
        """Test if/else."""
        source = """
niba umubare > 0 kora
    # nuko umubare munsi
    kandi
"""
        tokens, errors = tokenize(source)
        assert len(errors) == 0

    def test_loop(self):
        """Test for loop."""
        source = """
kuri i = 0 kugeza 10 kora
    # ikintu
iherezo
"""
        tokens, errors = tokenize(source)
        assert len(errors) == 0

    def test_kinyarwanda_keywords_in_context(self):
        """Test multiple Kinyarwanda keywords."""
        source = """
shyira x = 5
niba x > 0 kora
    subira x
cyangwa
    subira 0
iherezo
"""
        tokens, errors = tokenize(source)
        assert len(errors) == 0


# ══════════════════════════════════════════════════════════════════
# Performance Tests
# ══════════════════════════════════════════════════════════════════


class TestPerformance:
    """Performance tests for the lexer."""

    def test_large_file(self):
        """Test lexer with large input."""
        source = "\n".join(f"shyira x{i} = {i}" for i in range(1000))
        tokens, errors = tokenize(source)
        assert len(errors) == 0
        assert len(tokens) > 3000

    def test_many_strings(self):
        """Test lexer with many strings."""
        source = "\n".join(f'"string_{i}"' for i in range(100))
        tokens, errors = tokenize(source)
        assert len(errors) == 0
        strings = [t for t in tokens if t.type == TokenType.STRING]
        assert len(strings) == 100

    def test_unicode_source(self):
        """Test lexer with Unicode source."""
        source = """
# Iyi ni ingero y'ibikoresho bya Kinyarwanda
shyira igiciro = 100
niba igiciro > 50 kora
    subira "kirenze"
iherezo
"""
        tokens, errors = tokenize(source)
        assert len(errors) == 0
