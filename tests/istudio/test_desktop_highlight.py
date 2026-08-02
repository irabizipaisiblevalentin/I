"""Tests for istudio.desktop.highlight — syntax tokenizer."""

from __future__ import annotations

from src.istudio.desktop.highlight import BUILTINS, KEYWORDS, LITERALS, _classify_word, tokenize_line


def test_keyword_kinyarwanda_classified():
    assert _classify_word("niba") == "keyword"
    assert _classify_word("kora") == "keyword"
    assert _classify_word("umurimo") == "keyword"
    assert _classify_word("subira") == "keyword"


def test_keyword_english_aliases_classified():
    assert _classify_word("if") == "keyword"
    assert _classify_word("function") == "keyword"
    assert _classify_word("let") == "keyword"


def test_literals_classified():
    for literal in LITERALS:
        assert _classify_word(literal) == "constant"


def test_builtins_classified():
    assert _classify_word("andika") == "builtin"
    assert _classify_word("print") == "builtin"


def test_plain_identifiers():
    assert _classify_word("x") == "plain"
    assert _classify_word("muraho") == "plain"


def test_tokenize_keyword_and_string():
    tokens = tokenize_line('andika "Muraho"')
    tags = [tag for _, _, tag in tokens]
    assert "builtin" in tags
    assert "string" in tags


def test_tokenize_numbers():
    tokens = tokenize_line("let x = 42 3.14")
    tags = [tag for _, _, tag in tokens]
    assert tags.count("number") == 2


def test_tokenize_comments():
    tokens = tokenize_line("# comment // too")
    tags = [tag for _, _, tag in tokens]
    assert tags.count("comment") == 1


def test_tokenize_block_comment():
    tokens = tokenize_line("/* block */")
    assert any(tag == "comment" for _, _, tag in tokens)


def test_tokenize_operators():
    tokens = tokenize_line("a + b == c")
    tags = [tag for _, _, tag in tokens]
    assert tags.count("operator") == 2


def test_spans_cover_text():
    line = "if x >= 2 { andika(x) } # done"
    tokens = tokenize_line(line)
    assert tokens
    for start, end, tag in tokens:
        assert start >= 0
        assert end > start
        assert end <= len(line)


def test_keyword_frozensets_are_complete():
    assert "niba" in KEYWORDS
    assert "subira" in KEYWORDS
    assert "if" in KEYWORDS
    assert "yego" in LITERALS
    assert "andika" in BUILTINS
