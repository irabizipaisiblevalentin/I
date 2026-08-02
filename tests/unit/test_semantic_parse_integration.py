"""
End-to-end integration tests: source -> lexer -> parser -> semantic analyzer.

Tests verify the full pipeline produces correct semantic diagnostics
on real I language source code.
"""

from compiler.parser import parse
from compiler.semantic import SemanticAnalyzer, SemanticErrorCode


def _analyze_source(source: str):
    """Parse source, then run semantic analysis. Returns (Program, analyzer)."""
    prog, parse_errors = parse(source)
    assert not parse_errors, f"Parse errors: {parse_errors}"
    analyzer = SemanticAnalyzer()
    analyzer.analyze(prog)
    return prog, analyzer


class TestParseSemanticIntegration:
    def test_empty_program(self):
        _, a = _analyze_source("")
        assert not a.has_errors

    def test_variable_declaration(self):
        _, a = _analyze_source("shyira x = 10")
        assert not a.has_errors

    def test_const_declaration(self):
        _, a = _analyze_source("shyira_ko PI = 3.14")
        assert not a.has_errors

    def test_var_with_type_annotation(self):
        _, a = _analyze_source("shyira x: int = 10")
        assert not a.has_errors

    def test_function_declaration(self):
        _, a = _analyze_source("""
umurimo foo() kora
    subira 42
iherezo
""")
        assert not a.has_errors

    def test_function_with_params(self):
        _, a = _analyze_source("""
umurimo add(a, b) kora
    subira a + b
iherezo
""")
        assert not a.has_errors

    def test_function_with_return_type(self):
        _, a = _analyze_source("""
umurimo add(a: int, b: int) -> int kora
    subira a + b
iherezo
""")
        assert not a.has_errors

    def test_struct_declaration(self):
        _, a = _analyze_source("""
igiceri Point kora
    x: int
    y: int
iherezo
""")
        assert not a.has_errors

    def test_enum_declaration(self):
        _, a = _analyze_source("""
ikindi Color kora
    RED
    GREEN
    BLUE
iherezo
""")
        assert not a.has_errors

    def test_class_declaration(self):
        _, a = _analyze_source("""
urwego Animal kora
    umurimo speak() -> string kora
        subira "Sound"
    iherezo
iherezo
""")
        assert not a.has_errors

    def test_class_with_method(self):
        _, a = _analyze_source("""
urwego Animal kora
    umurimo speak() -> string kora
        subira "Sound"
    iherezo
iherezo
""")
        assert not a.has_errors

    def test_class_with_parent(self):
        _, a = _analyze_source("""
urwego Animal kora
iherezo

urwego Dog kugira Animal kora
iherezo
""")
        assert not a.has_errors

    def test_if_statement(self):
        _, a = _analyze_source("""
niba yego kora
    shyira x = 1
iherezo
""")
        assert not a.has_errors

    def test_if_else(self):
        _, a = _analyze_source("""
niba yego kora
    shyira x = 1
cyangwa
    shyira x = 2
iherezo
""")
        assert not a.has_errors

    def test_while_loop(self):
        _, a = _analyze_source("""
shyira x = 0
wihuse x < 10 kora
    x = x + 1
iherezo
""")
        assert not a.has_errors

    def test_for_loop(self):
        _, a = _analyze_source("""
kuri i = 0 kugeza 10 kora
    shyira x = i
iherezo
""")
        assert not a.has_errors

    def test_for_each_loop(self):
        _, a = _analyze_source("""
shyira items = []
buri item muri items kora
    andika item
iherezo
""")
        assert not a.has_errors

    def test_try_catch(self):
        _, a = _analyze_source("""
kora
    shyira x = 1
kubika e
    andika "error"
iherezo
""")
        assert not a.has_errors

    def test_import_export(self):
        _, a = _analyze_source("""
shyira x = 42
tanga x
""")
        assert not a.has_errors

    def test_break_inside_loop(self):
        _, a = _analyze_source("""
wihuse yego kora
    gukoma
iherezo
""")
        assert not a.has_errors

    def test_continue_inside_loop(self):
        _, a = _analyze_source("""
wihuse yego kora
    kugenda
iherezo
""")
        assert not a.has_errors

    def test_return_inside_function(self):
        _, a = _analyze_source("""
umurimo foo() kora
    subira 42
iherezo
""")
        assert not a.has_errors

    def test_expression_statement(self):
        _, a = _analyze_source("andika 42")
        assert not a.has_errors

    def test_multiple_statements(self):
        _, a = _analyze_source("""
shyira x = 1
shyira y = 2
andika x + y
""")
        assert not a.has_errors

    def test_list_literal(self):
        _, a = _analyze_source("shyira items = [1, 2, 3]")
        assert not a.has_errors

    def test_dict_literal(self):
        _, a = _analyze_source("shyira map = {\"a\": 1, \"b\": 2}")
        assert not a.has_errors

    def test_complex_program(self):
        _, a = _analyze_source("""
shyira_ko PI = 3.14159

umurimo add(a: int, b: int) -> int kora
    subira a + b
iherezo

urwego Calculator kora
    umurimo double(x: int) -> int kora
        subira add(x, x)
    iherezo
iherezo

shyira result = add(10, 20)
andika result
""")
        assert not a.has_errors

    def test_kinyarwanda_hello_world(self):
        _, a = _analyze_source("""
umurimo main() kora
    andika "Muraho, isi!"
iherezo
""")
        assert not a.has_errors


class TestSemanticErrorsFromParse:
    """Tests that parse + semantic analysis correctly catches errors."""

    def test_duplicate_variable(self):
        _, a = _analyze_source("""
shyira x = 1
shyira x = 2
""")
        assert a.has_errors
        codes = [d.code for d in a.diagnostics.diagnostics]
        assert any(c == SemanticErrorCode.SEM100_DUPLICATE_VARIABLE for c in codes)

    def test_duplicate_function(self):
        _, a = _analyze_source("""
umurimo foo() kora
iherezo
umurimo foo() kora
iherezo
""")
        assert a.has_errors
        codes = [d.code for d in a.diagnostics.diagnostics]
        assert any(c == SemanticErrorCode.SEM101_DUPLICATE_FUNCTION for c in codes)

    def test_return_outside_function(self):
        _, a = _analyze_source("subira 42")
        assert a.has_errors
        codes = [d.code for d in a.diagnostics.diagnostics]
        assert any(c == SemanticErrorCode.SEM304_RETURN_OUTSIDE_FUNCTION for c in codes)

    def test_break_outside_loop(self):
        _, a = _analyze_source("gukoma")
        assert a.has_errors
        codes = [d.code for d in a.diagnostics.diagnostics]
        assert any(c == SemanticErrorCode.SEM305_BREAK_OUTSIDE_LOOP for c in codes)

    def test_continue_outside_loop(self):
        _, a = _analyze_source("kugenda")
        assert a.has_errors
        codes = [d.code for d in a.diagnostics.diagnostics]
        assert any(c == SemanticErrorCode.SEM306_CONTINUE_OUTSIDE_LOOP for c in codes)

    def test_reserved_keyword_as_variable(self):
        from compiler.ast.nodes import LiteralExpr, Program, VarDecl
        from compiler.semantic import SemanticAnalyzer
        from compiler.semantic.errors import SemanticErrorCode
        prog = Program(declarations=[
            VarDecl(name="niba", initializer=LiteralExpr(42), type_annotation=None, is_const=False, location=None),
        ])
        a = SemanticAnalyzer()
        a.analyze(prog)
        assert a.has_errors
        codes = [d.code for d in a.diagnostics.diagnostics]
        assert any(c == SemanticErrorCode.SEM110_RESERVED_KEYWORD for c in codes)

    def test_assignment_to_undefined(self):
        _, a = _analyze_source("nonexistent = 42")
        assert a.has_errors
        codes = [d.code for d in a.diagnostics.diagnostics]
        assert any(c == SemanticErrorCode.SEM200_UNDEFINED_VARIABLE for c in codes)

    def test_export_undefined(self):
        _, a = _analyze_source("tanga nonexistent")
        assert a.has_errors
        codes = [d.code for d in a.diagnostics.diagnostics]
        assert any(c == SemanticErrorCode.SEM404_EXPORT_NOT_FOUND for c in codes)


class TestCommentsAndWhitespace:
    """Tests that comments and whitespace don't interfere."""

    def test_program_with_comments(self):
        _, a = _analyze_source("""
# This is a comment
shyira x = 10  # inline comment
# Another comment
shyira y = 20
# Final comment
""")
        assert not a.has_errors

    def test_comment_only(self):
        _, a = _analyze_source("# Just a comment")
        assert not a.has_errors

    def test_function_with_comment_body(self):
        _, a = _analyze_source("""
umurimo foo() kora
    # This is the body
    # Still the body
    subira 42
iherezo
""")
        assert not a.has_errors

    def test_class_with_comment_body(self):
        _, a = _analyze_source("""
urwego MyClass kora
    # class body comment
    shyira x = 1
iherezo
""")
        assert not a.has_errors

    def test_loop_with_comment_body(self):
        _, a = _analyze_source("""
kuri i = 0 kugeza 10 kora
    # loop body
iherezo
""")
        assert not a.has_errors

    def test_if_with_comment_body(self):
        _, a = _analyze_source("""
niba yego kora
    # if body
cyangwa
    # else body
iherezo
""")
        assert not a.has_errors


class TestUndefinedVariableInCalls:
    """Undefined identifiers inside call arguments must be reported."""

    def test_undefined_variable_as_print_argument(self):
        _, a = _analyze_source("andika y")
        assert a.has_errors
        codes = {d.code for d in a.diagnostics.diagnostics}
        assert SemanticErrorCode.SEM200_UNDEFINED_VARIABLE in codes

    def test_undefined_variable_inside_binary_expr_argument(self):
        _, a = _analyze_source("shyira a = 10\nandika a + b")
        assert a.has_errors
        codes = {d.code for d in a.diagnostics.diagnostics}
        assert SemanticErrorCode.SEM200_UNDEFINED_VARIABLE in codes

    def test_undefined_variable_in_user_function_call(self):
        _, a = _analyze_source("""
umurimo umubare(x) kora
    subira x
iherezo
andika umubare(nonexistent)
""")
        assert a.has_errors
        codes = {d.code for d in a.diagnostics.diagnostics}
        assert SemanticErrorCode.SEM200_UNDEFINED_VARIABLE in codes

    def test_defined_variables_in_calls_still_pass(self):
        _, a = _analyze_source("""
shyira y = 42
andika y
""")
        assert not a.has_errors


class TestBilingualDiagnostics:
    """Tests that diagnostics produce bilingual messages."""

    def test_bilingual_duplicate_variable(self):
        _, a = _analyze_source("""
shyira x = 1
shyira x = 2
""")
        diag = a.diagnostics.diagnostics[0]
        msg_rw = diag.message_rw
        msg_en = diag.message_en
        assert isinstance(msg_rw, str) and len(msg_rw) > 0
        assert isinstance(msg_en, str) and len(msg_en) > 0

    def test_bilingual_return_outside_function(self):
        _, a = _analyze_source("subira 42")
        diag = a.diagnostics.diagnostics[0]
        assert "subira" in diag.message_rw or "return" in diag.message_en
        assert "function" in diag.message_en or "umurimo" in diag.message_rw

    def test_diagnostic_has_location(self):
        _, a = _analyze_source("subira 42")
        diag = a.diagnostics.diagnostics[0]
        assert diag.location.line > 0
        assert diag.location.file == "<input>"
