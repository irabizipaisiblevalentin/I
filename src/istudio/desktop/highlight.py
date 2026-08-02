"""I STUDIO Desktop — syntax highlighting tokenizer (pure, headless-testable).

The tokenizer knows nothing about tkinter; the editor widget consumes its
output to apply text tags. Because I is a Kinyarwanda-first language, both
the Kinyarwanda keywords (from the lexer) and the English aliases understood
by the I Studio language server are highlighted.
"""

from __future__ import annotations

import re

KEYWORDS = frozenset({
    "niba", "cyangwa", "cyangwa_niba", "kugenda", "gukoma", "subira", "tanga",
    "kora", "wihuse", "kugeza", "kuri", "muri", "buri",
    "shyira", "shyira_ko", "umurimo", "igiceri", "ikindi", "urwego", "akabuto",
    "urubingo", "ubwoko", "kugira", "gukora", "nshya",
    "shyiramo", "kugira_ngo",
    "kandi", "bitewe", "ari", "si",
    "gushyingura", "kubika", "ikinyoma",
    "iherezo", "self", "super",
    "if", "else", "for", "while", "return", "function", "let", "const",
    "class", "import", "from", "export", "match", "try", "catch", "throw",
    "async", "await", "var",
})

LITERALS = frozenset({"yego", "oya", "ubusa", "true", "false", "null"})

BUILTINS = frozenset({
    "andika", "soma", "uburengero", "ubwoko",
    "shobora_int", "shobora_float", "shobora_umuntu", "shobora_bool",
    "gukoma_func",
    "print", "len", "range", "type", "int", "str", "float", "list", "dict",
    "map", "filter", "reduce", "open", "read", "write",
})

Token = tuple[int, int, str]

_COMMENT = re.compile(r"//[^\n]*|#[^\n]*|/\*.*?\*/", re.DOTALL)
_STRING = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
_NUMBER = re.compile(r"(?<!\w)\d+(\.\d+)?(?!\w)")
_WORD = re.compile(r"\w+")
_OPERATOR = re.compile(r"[+\-*/%=<>!&|^~?:]+|[(){}\[\];,.]")


def tokenize_line(line: str) -> list[Token]:
    """Return (start, end, tag) spans for one line of source text.

    Tag names are the plain names used as tkinter tag suffixes, e.g.
    ``keyword``, ``string``, ``number``, ``comment``, ``builtin``.
    """
    tokens: list[Token] = []
    pos = 0
    length = len(line)

    while pos < length:
        comment = _COMMENT.match(line, pos)
        if comment and comment.start() == pos:
            tokens.append((pos, comment.end(), "comment"))
            pos = comment.end()
            continue

        string = _STRING.match(line, pos)
        if string and string.start() == pos:
            tokens.append((pos, string.end(), "string"))
            pos = string.end()
            continue

        number = _NUMBER.match(line, pos)
        if number and number.start() == pos:
            tokens.append((pos, number.end(), "number"))
            pos = number.end()
            continue

        char = line[pos]
        if char.isalnum() or char == "_":
            word = _WORD.match(line, pos)
            if word:
                text = word.group(0)
                tag = _classify_word(text)
                tokens.append((pos, word.end(), tag))
                pos = word.end()
                continue

        operator = _OPERATOR.match(line, pos)
        if operator and operator.start() == pos:
            tokens.append((pos, operator.end(), "operator"))
            pos = operator.end()
            continue

        pos += 1

    return tokens


def _classify_word(word: str) -> str:
    if word in KEYWORDS:
        return "keyword"
    if word in LITERALS:
        return "constant"
    if word in BUILTINS:
        return "builtin"
    return "plain"
