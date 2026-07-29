"""Tests for istudio.ururimi — Language Server."""

from __future__ import annotations

from src.istudio.ururimi import LanguageServer
from src.istudio.ibikoreshingiro import DiagnosticSeverity, DocumentPosition, CompletionKind


def test_analyze_clean():
    ls = LanguageServer()
    diags = ls.analyze('function main() {\n    print("hello")\n}')
    assert len(diags) == 0


def test_analyze_unterminated_string():
    ls = LanguageServer()
    diags = ls.analyze('print("unterminated)')
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert len(errors) >= 1
    assert "Unterminated" in errors[0].message


def test_analyze_undefined_reference():
    ls = LanguageServer()
    diags = ls.analyze("undefined variable")
    warnings = [d for d in diags if d.severity == DiagnosticSeverity.WARNING]
    assert len(warnings) >= 1


def test_analyze_int_overflow():
    ls = LanguageServer()
    diags = ls.analyze("let x = 9999999999")
    overflows = [d for d in diags if d.code == "int-overflow"]
    assert len(overflows) >= 1


def test_get_completions_empty():
    ls = LanguageServer()
    items = ls.get_completions("", DocumentPosition(line=0, column=0))
    assert len(items) > 0


def test_get_completions_filtered():
    ls = LanguageServer()
    items = ls.get_completions("fu", DocumentPosition(line=0, column=2))
    assert any("function" in c.label.lower() for c in items)


def test_get_completions_kinds():
    ls = LanguageServer()
    items = ls.get_completions("", DocumentPosition(line=0, column=0))
    kinds = set(c.kind for c in items)
    assert CompletionKind.KEYWORD in kinds
    assert CompletionKind.SNIPPET in kinds


def test_get_hover_builtin():
    ls = LanguageServer()
    content = "print('hello')"
    hover = ls.get_hover(content, DocumentPosition(line=0, column=1))
    assert hover is not None
    assert len(hover.contents) > 0
    assert "print" in hover.contents[0]


def test_get_hover_non_builtin():
    ls = LanguageServer()
    content = "xyz_unknown"
    hover = ls.get_hover(content, DocumentPosition(line=0, column=0))
    assert hover is None or "xyz_unknown" not in (hover.contents[0] if hover.contents else "")


def test_get_symbols():
    ls = LanguageServer()
    content = """function main() {
    let x = 1
    class Foo {}
}"""
    symbols = ls.get_symbols(content)
    names = [s.name for s in symbols]
    assert "main" in names
    assert "x" in names
    assert "Foo" in names


def test_go_to_definition():
    ls = LanguageServer()
    content = "function foo() {}\nfoo()"
    pos = DocumentPosition(line=1, column=0)
    definition = ls.go_to_definition(content, pos)
    assert definition is not None
    assert definition.start.line == 0


def test_go_to_definition_not_found():
    ls = LanguageServer()
    content = "function foo() {}\nbar()"
    pos = DocumentPosition(line=1, column=0)
    result = ls.go_to_definition(content, pos)
    assert result is None


def test_get_references():
    ls = LanguageServer()
    content = "let x = 1\nlet y = x + x"
    refs = ls.get_references(content, DocumentPosition(line=0, column=4))
    assert len(refs) >= 2


def test_get_code_actions():
    ls = LanguageServer()
    diags = ls.analyze("undefined variable")
    actions = ls.get_code_actions(diags)
    assert len(actions) >= 1


def test_format_document():
    ls = LanguageServer()
    content = "function foo() {\nlet x = 1\n}"
    formatted = ls.format_document(content)
    assert "    " in formatted


def test_clear_diagnostics():
    ls = LanguageServer()
    ls.analyze("print('hello')", "test.i")
    assert len(ls.get_diagnostics("test.i")) == 0
    ls.analyze("undefined variable", "test2.i")
    assert len(ls.get_diagnostics("test2.i")) > 0
    ls.clear_diagnostics("test2.i")
    assert len(ls.get_diagnostics("test2.i")) == 0


def test_set_workspace_files():
    ls = LanguageServer()
    ls.set_workspace_files(["main.i", "lib.i"])
    assert ls._workspace_files == ["main.i", "lib.i"]
