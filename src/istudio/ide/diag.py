"""I STUDIO IDE — source analysis (real lexer/parser/semantic pipeline).

Maps compiler errors onto Monaco/LSP-style diagnostics:
    {"range": {"start": {line, character}, "end": {line, character}},
     "severity": 1|2|3|4, "message": str, "source": "compiler", "code": str}

Also exposes light completion / hover / symbol / format helpers used by the
language service endpoint.

NOTE: analysis runs in the server process; the server wraps calls in a watchdog
so that pathological inputs (which can hang the parser) cannot block the IDE.
"""

from __future__ import annotations

from typing import Any

from compiler.ast.nodes import SourceLocation
from compiler.lexer import tokenize
from compiler.parser import parse

_SEVERITY_MAP = {
    "error": 1,
    "warning": 2,
    "info": 3,
    "hint": 4,
}


def _loc_to_range(location: SourceLocation | None) -> dict[str, Any] | None:
    if location is None:
        return None
    start_line = getattr(location, "start_line", 0) or getattr(location, "line", 0) or 0
    start_col = getattr(location, "start_column", 0) or getattr(location, "column", 0) or 0
    end_line = getattr(location, "end_line", 0) or start_line
    end_col = getattr(location, "end_column", 0) or start_col
    if start_line <= 0:
        return None
    return {
        "start": {"line": start_line, "character": start_col},
        "end": {"line": end_line, "character": end_col},
    }


def _diag(code: str, message: str, line: int, column: int, severity: int = 1) -> dict[str, Any]:
    return {
        "range": {
            "start": {"line": line, "character": column},
            "end": {"line": line, "character": column + 1},
        },
        "severity": severity,
        "message": message,
        "source": "compiler",
        "code": code,
    }


def analyze_source(source: str, filename: str = "unnamed.i") -> list[dict[str, Any]]:
    """Analyze I source with the real compiler pipeline."""
    diagnostics: list[dict[str, Any]] = []

    try:
        tokens, lex_errors = tokenize(source, filename)
    except Exception as exc:  # noqa: BLE001
        return [_diag("LEX", f"Lexer failure: {exc}", 1, 1)]

    for err in lex_errors:
        try:
            diagnostics.append(
                _diag(
                    getattr(err, "code", "LEX").name if hasattr(getattr(err, "code", None), "name") else "LEX",
                    getattr(err, "message_en", str(err)),
                    getattr(err, "line", 1),
                    max(0, getattr(err, "column", 0) - 1),
                    1,
                )
            )
        except Exception:  # noqa: BLE001
            diagnostics.append(_diag("LEX", str(err), 1, 1))

    try:
        program, parse_errors = parse(source)
    except Exception as exc:  # noqa: BLE001
        diagnostics.append(_diag("PARSE", f"Parser failure: {exc}", 1, 1))
        return diagnostics

    for err in parse_errors:
        try:
            diagnostics.append(
                _diag(
                    getattr(err, "code", "PARSE").name if hasattr(getattr(err, "code", None), "name") else "PARSE",
                    getattr(err, "message_en", str(err)),
                    getattr(err, "line", 1),
                    max(0, getattr(err, "column", 0) - 1),
                    1,
                )
            )
        except Exception:  # noqa: BLE001
            diagnostics.append(_diag("PARSE", str(err), 1, 1))

    if not lex_errors and not parse_errors:
        try:
            from compiler.semantic import analyze

            collection = analyze(program, filename)
            for diag in collection.diagnostics:
                loc = getattr(diag, "location", None)
                rng = _loc_to_range(loc)
                if rng is None:
                    continue
                severity = _SEVERITY_MAP.get(str(getattr(diag, "severity", "")).lower(), 1)
                diagnostics.append(
                    {
                        "range": rng,
                        "severity": severity,
                        "message": getattr(diag, "message_en", "") or getattr(diag, "message_rw", ""),
                        "source": "compiler",
                        "code": getattr(getattr(diag, "code", None), "name", "SEM") or "SEM",
                    }
                )
        except Exception:  # noqa: BLE001 — semantic layer is best-effort
            pass

    return diagnostics


# ── Completion ──────────────────────────────────────────────────────────────

_KEYWORDS: list[str] = []
try:
    from compiler.lexer.token import KEYWORDS

    _KEYWORDS = sorted(KEYWORDS)
except Exception:  # noqa: BLE001
    _KEYWORDS = [
        "andika", "subira", "niba", "cyangwa", "cyangwa_niba", "iherezo",
        "wihuse", "kuri", "buri", "muri", "kugeza", "umurimo", "shyira",
        "shyira_ko", "igiceri", "ukuri", "ikinyoma", "kora", "nga", "kubika",
    ]

_BUILTIN_DOCS: dict[str, str] = {
    "andika": "Print a value to standard output.",
    "soma": "Read a line from standard input.",
    "shobora_umuntu": "Convert a value to text (string).",
    "uburengero": "Floor a numeric value.",
}

_FUNCTION_PATTERN_HINTS = (
    "umurimo ",
    "umurimo(",
)


def completions_at(source: str, line: int, column: int) -> list[dict[str, Any]]:
    """Completion items for (1-based line, 0-based column)."""
    tokens, _ = tokenize(source)
    lines = source.split("\n")
    current = lines[line - 1] if 0 <= line - 1 < len(lines) else ""
    before = current[:column]

    word_chars = ""
    for ch in reversed(before):
        if ch.isalnum() or ch == "_":
            word_chars = ch + word_chars
        else:
            break

    is_identifier_start = bool(word_chars) and word_chars[0].isalpha()
    items: list[dict[str, Any]] = []

    for kw in _KEYWORDS:
        if not word_chars or (kw.startswith(word_chars)):
            items.append(
                {
                    "label": kw,
                    "kind": 14,  # Monaco Keyword
                    "detail": "keyword",
                    "insertText": kw,
                    "filterText": kw,
                }
            )

    for name, doc in _BUILTIN_DOCS.items():
        if not word_chars or name.startswith(word_chars):
            items.append(
                {
                    "label": name,
                    "kind": 12,  # Monaco Function
                    "detail": "builtin",
                    "documentation": doc,
                    "insertText": name,
                }
            )

    if is_identifier_start:
        seen = set()
        for tok in tokens:
            lexeme = getattr(tok, "lexeme", "")
            if lexeme.isidentifier() and lexeme.lower() not in _KEYWORDS and lexeme not in seen:
                seen.add(lexeme)
                items.append(
                    {
                        "label": lexeme,
                        "kind": 6,  # Monaco Variable
                        "detail": "identifier",
                        "insertText": lexeme,
                    }
                )

    return items


def hover_at(source: str, line: int, column: int) -> dict[str, Any] | None:
    """Return hover markdown for the token under the cursor, or None."""
    tokens, _ = tokenize(source)
    for tok in tokens:
        tok_line = getattr(tok, "line", 0)
        tok_col = getattr(tok, "column", 0)
        if tok_line != line:
            continue
        if tok_col <= column < tok_col + len(getattr(tok, "lexeme", "")):
            lexeme = getattr(tok, "lexeme", "")
            if lexeme in _BUILTIN_DOCS:
                return {"contents": [{"language": "text", "value": f"**{lexeme}** — {_BUILTIN_DOCS[lexeme]}"}]}
            if lexeme in _KEYWORDS:
                return {"contents": [{"language": "text", "value": f"**{lexeme}** — I language keyword"}]}
            if lexeme.isidentifier():
                return {"contents": [{"language": "text", "value": f"`{lexeme}`"}]}
    return None


def symbols_of(source: str, filename: str = "unnamed.i") -> list[dict[str, Any]]:
    """Outline symbols from the real AST (functions, structs, enums)."""
    try:
        program, parse_errors = parse(source)
    except Exception:  # noqa: BLE001
        return []
    if parse_errors:
        return []

    result: list[dict[str, Any]] = []
    # Monaco DocumentSymbolKind: 5=Class, 9=Enum, 10=Interface, 11=Function,
    # 6=Method, 12=Variable, 13=Constant, 22=Struct
    kinds = {
        "FUNCTION_DECL": 11,
        "STRUCT_DECL": 22,
        "ENUM_DECL": 9,
        "CLASS_DECL": 5,
        "TRAIT_DECL": 10,
        "INTERFACE_DECL": 10,
        "METHOD": 6,
        "PROPERTY": 7,
        "VARIABLE_DECL": 12,
        "CONSTANT_DECL": 13,
    }

    def visit(node: Any) -> None:
        for child in getattr(node, "children", lambda: [])():
            visit(child)
        ntype = getattr(node, "node_type", None)
        ntype_name = getattr(ntype, "name", None) or (str(ntype) if ntype else None)
        kind = kinds.get(ntype_name or "")
        if kind is None:
            return
        name = getattr(node, "name", None)
        if not isinstance(name, str):
            name = getattr(name, "name", None)
        if not name:
            return
        rng = _loc_to_range(getattr(node, "span", None))
        if rng is None:
            return
        result.append({"name": str(name), "kind": kind, "range": rng, "selectionRange": rng})

    visit(program)
    return result


def format_source(source: str) -> str:
    """Best-effort formatter: normalized 4-space indentation for block bodies."""
    out_lines: list[str] = []
    indent = 0
    block_keywords = ("niba ", "cyangwa_niba ", "cyangwa ", "wihuse ", "kuri ", "buri ", "umurimo ", "igiceri ")
    closers = ("iherezo",)
    for raw in source.split("\n"):
        stripped = raw.rstrip()
        if not stripped.strip():
            out_lines.append("")
            continue
        head = stripped.lstrip()
        if head.startswith(closers):
            indent = max(0, indent - 1)
        out_lines.append("    " * indent + head)
        if head.startswith(block_keywords) or head.endswith(":"):
            indent += 1
    return "\n".join(out_lines).rstrip() + "\n"
