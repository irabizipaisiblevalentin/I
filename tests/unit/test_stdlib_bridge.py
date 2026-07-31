"""Tests for the stdlib import resolution and module binding."""
from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from compiler.ast.nodes import Program
from compiler.parser import parse
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.semantic.symbols import SymbolKind


def parse_and_analyze(source: str) -> tuple[Program, SemanticAnalyzer]:
    prog, parse_errors = parse(source)
    assert not parse_errors, f"Parse errors: {parse_errors}"
    analyzer = SemanticAnalyzer()
    analyzer.analyze(prog)
    return prog, analyzer


class TestStdlibImportResolution(unittest.TestCase):
    """Verify that urubuga and other stdlib modules resolve correctly."""

    def test_import_urubuga_resolves(self):
        source = """
shyiramo urubuga
"""
        program, analyzer = parse_and_analyze(source)
        self.assertFalse(analyzer.has_errors, "Import should resolve without errors")

    def test_import_urubuga_binds_to_scope(self):
        source = """
shyiramo urubuga
"""
        program, analyzer = parse_and_analyze(source)
        sym = analyzer.ctx.scopes.lookup("urubuga")
        self.assertIsNotNone(sym, "urubuga should be bound in scope")
        self.assertEqual(sym.kind, SymbolKind.MODULE, "urubuga should be a module symbol")

    def test_import_urubuga_has_exports(self):
        source = """
shyiramo urubuga
"""
        program, analyzer = parse_and_analyze(source)
        sym = analyzer.ctx.scopes.lookup("urubuga")
        self.assertIsNotNone(sym)
        self.assertIn("andika", sym.exports, "urubuga should export andika")

    def test_import_math_resolves(self):
        source = """
shyiramo math
"""
        program, analyzer = parse_and_analyze(source)
        self.assertFalse(analyzer.has_errors, "math import should resolve")
        sym = analyzer.ctx.scopes.lookup("math")
        self.assertIsNotNone(sym)
        self.assertEqual(sym.kind, SymbolKind.MODULE)

    def test_import_with_alias(self):
        source = """
shyiramo urubuga kugira_ngo u
"""
        program, analyzer = parse_and_analyze(source)
        self.assertFalse(analyzer.has_errors, "Aliased import should resolve")
        sym = analyzer.ctx.scopes.lookup("u")
        self.assertIsNotNone(sym, "Alias 'u' should be bound in scope")
        self.assertEqual(sym.kind, SymbolKind.MODULE)

    def test_unknown_module_gives_error(self):
        source = """
shyiramo nonexistent_module_xyz
"""
        program, analyzer = parse_and_analyze(source)
        self.assertTrue(analyzer.has_errors, "Unknown module should produce error")

    def test_import_preserves_across_files(self):
        source = """
shyiramo urubuga
shyiramo math
"""
        program, analyzer = parse_and_analyze(source)
        self.assertFalse(analyzer.has_errors)
        urubuga = analyzer.ctx.scopes.lookup("urubuga")
        math = analyzer.ctx.scopes.lookup("math")
        self.assertIsNotNone(urubuga)
        self.assertIsNotNone(math)

    def test_stdlib_urubuga_i_file_exists(self):
        stdlib_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "src", "stdlib", "urubuga.i"
        )
        self.assertTrue(
            os.path.isfile(stdlib_path),
            f"urubuga.i should exist at {stdlib_path}",
        )

    def test_text_import_has_exports(self):
        source = """
shyiramo text
"""
        program, analyzer = parse_and_analyze(source)
        self.assertFalse(analyzer.has_errors, "text import should resolve")
        sym = analyzer.ctx.scopes.lookup("text")
        self.assertIsNotNone(sym)
        for expected in ("uburebure", "ice", "ntoya", "nini", "koma"):
            self.assertIn(expected, sym.exports, f"text should export {expected}")


class TestStdlibMemberAccess(unittest.TestCase):
    """Verify that module member access (urubuga.andika) resolves correctly."""

    def test_module_member_access_resolves(self):
        source = """
shyiramo urubuga
shyira x = urubuga.andika("test")
"""
        program, analyzer = parse_and_analyze(source)
        self.assertFalse(analyzer.has_errors, "Module member access should resolve")

    def test_module_get_expr_returns_expected_type(self):
        source = """
shyiramo urubuga
shyira x = urubuga.andika
"""
        program, analyzer = parse_and_analyze(source)
        self.assertFalse(analyzer.has_errors)
        sym = analyzer.ctx.scopes.lookup("x")
        self.assertIsNotNone(sym)
        self.assertIsNotNone(sym.type_descriptor)


if __name__ == "__main__":
    unittest.main()
