"""
Comprehensive Parser Test Suite

Tests all aspects of the I language parser:
- Statement parsing
- Expression parsing
- Operator precedence
- Block structure
- Error recovery
- Edge cases
"""

import pytest

from src.compiler.parser import Parser, parse
from src.compiler.parser.errors import ParseErrorCode
from src.compiler.ast.nodes import (
    Program,
    LiteralExpr,
    IdentifierExpr,
    BinaryExpr,
    LogicalExpr,
    UnaryExpr,
    AssignmentExpr,
    CompoundAssignmentExpr,
    CallExpr,
    ConstructorExpr,
    GetExpr,
    SetExpr,
    IndexExpr,
    SliceExpr,
    SelfExpr,
    SuperExpr,
    ListExpr,
    DictExpr,
    TupleExpr,
    LambdaExpr,
    IfExpr,
    BlockExpr,
    ExpressionStmt,
    VarStmt,
    BlockStmt,
    IfStmt,
    ElifBranch,
    WhileStmt,
    UntilStmt,
    ForStmt,
    ForEachStmt,
    BreakStmt,
    ContinueStmt,
    ReturnStmt,
    FunctionStmt,
    FunctionParam,
    StructStmt,
    EnumStmt,
    ClassStmt,
    TraitStmt,
    InterfaceStmt,
    ImportStmt,
    ExportStmt,
    TryStmt,
    ThrowStmt,
)


# ══════════════════════════════════════════════════════════════════
# Helper
# ══════════════════════════════════════════════════════════════════


def parse_source(source: str) -> Program:
    """Parse source and return Program."""
    ast, errors = parse(source)
    return ast


def parse_no_errors(source: str) -> Program:
    """Parse source expecting no errors."""
    ast, errors = parse(source)
    assert len(errors) == 0, f"Expected no errors, got: {errors}"
    return ast


def get_stmts(source: str) -> list:
    """Parse and get statement list."""
    return parse_no_errors(source).statements


def get_first_stmt(source: str):
    """Parse and get first statement."""
    stmts = get_stmts(source)
    assert len(stmts) > 0, "No statements parsed"
    return stmts[0]


def get_first_expr(source: str):
    """Parse and get first expression (from ExpressionStmt)."""
    stmt = get_first_stmt(source)
    assert isinstance(stmt, ExpressionStmt), f"Expected ExpressionStmt, got {type(stmt)}"
    return stmt.expression


# ══════════════════════════════════════════════════════════════════
# Literal Tests
# ══════════════════════════════════════════════════════════════════


class TestLiterals:
    """Tests for literal expressions."""

    def test_integer_literal(self):
        expr = get_first_expr("42")
        assert isinstance(expr, LiteralExpr)
        assert expr.value == 42

    def test_float_literal(self):
        expr = get_first_expr("3.14")
        assert isinstance(expr, LiteralExpr)
        assert expr.value == 3.14

    def test_string_literal(self):
        expr = get_first_expr('"hello"')
        assert isinstance(expr, LiteralExpr)
        assert expr.value == "hello"

    def test_true_literal(self):
        expr = get_first_expr("yego")
        assert isinstance(expr, LiteralExpr)
        assert expr.value is True

    def test_false_literal(self):
        expr = get_first_expr("oya")
        assert isinstance(expr, LiteralExpr)
        assert expr.value is False

    def test_null_literal(self):
        expr = get_first_expr("ubusa")
        assert isinstance(expr, LiteralExpr)
        assert expr.value is None

    def test_english_true(self):
        expr = get_first_expr("true")
        assert isinstance(expr, LiteralExpr)
        assert expr.value is True

    def test_english_false(self):
        expr = get_first_expr("false")
        assert isinstance(expr, LiteralExpr)
        assert expr.value is False

    def test_english_null(self):
        expr = get_first_expr("null")
        assert isinstance(expr, LiteralExpr)
        assert expr.value is None


# ══════════════════════════════════════════════════════════════════
# Identifier Tests
# ══════════════════════════════════════════════════════════════════


class TestIdentifiers:
    """Tests for identifier expressions."""

    def test_simple_identifier(self):
        expr = get_first_expr("x")
        assert isinstance(expr, IdentifierExpr)
        assert expr.name.lexeme == "x"

    def test_underscore_identifier(self):
        expr = get_first_expr("_private")
        assert isinstance(expr, IdentifierExpr)
        assert expr.name.lexeme == "_private"


# ══════════════════════════════════════════════════════════════════
# Binary Expression Tests
# ══════════════════════════════════════════════════════════════════


class TestBinaryExpressions:
    """Tests for binary expressions."""

    def test_addition(self):
        expr = get_first_expr("1 + 2")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == "+"

    def test_subtraction(self):
        expr = get_first_expr("1 - 2")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == "-"

    def test_multiplication(self):
        expr = get_first_expr("1 * 2")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == "*"

    def test_division(self):
        expr = get_first_expr("1 / 2")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == "/"

    def test_modulo(self):
        expr = get_first_expr("1 % 2")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == "%"

    def test_power(self):
        expr = get_first_expr("2 ** 3")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == "**"

    def test_equal(self):
        expr = get_first_expr("1 == 2")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == "=="

    def test_not_equal(self):
        expr = get_first_expr("1 != 2")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == "!="

    def test_greater(self):
        expr = get_first_expr("1 > 2")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == ">"

    def test_less(self):
        expr = get_first_expr("1 < 2")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == "<"

    def test_greater_equal(self):
        expr = get_first_expr("1 >= 2")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == ">="

    def test_less_equal(self):
        expr = get_first_expr("1 <= 2")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == "<="


# ══════════════════════════════════════════════════════════════════
# Logical Expression Tests
# ══════════════════════════════════════════════════════════════════


class TestLogicalExpressions:
    """Tests for logical expressions."""

    def test_and(self):
        expr = get_first_expr("x kandi y")
        assert isinstance(expr, LogicalExpr)
        assert expr.operator.lexeme == "kandi"

    def test_or(self):
        expr = get_first_expr("x cyangwa y")
        assert isinstance(expr, LogicalExpr)
        assert expr.operator.lexeme == "cyangwa"

    def test_and_operator(self):
        expr = get_first_expr("x && y")
        assert isinstance(expr, LogicalExpr)
        assert expr.operator.lexeme == "&&"

    def test_or_operator(self):
        expr = get_first_expr("x || y")
        assert isinstance(expr, LogicalExpr)
        assert expr.operator.lexeme == "||"

    def test_not(self):
        expr = get_first_expr("si x")
        assert isinstance(expr, UnaryExpr)
        assert expr.operator.lexeme == "si"

    def test_bang(self):
        expr = get_first_expr("!x")
        assert isinstance(expr, UnaryExpr)
        assert expr.operator.lexeme == "!"


# ══════════════════════════════════════════════════════════════════
# Precedence Tests
# ══════════════════════════════════════════════════════════════════


class TestPrecedence:
    """Tests for operator precedence."""

    def test_add_before_mul(self):
        expr = get_first_expr("1 + 2 * 3")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == "+"
        assert isinstance(expr.right, BinaryExpr)
        assert expr.right.operator.lexeme == "*"

    def test_mul_before_add(self):
        expr = get_first_expr("1 * 2 + 3")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == "+"
        assert isinstance(expr.left, BinaryExpr)
        assert expr.left.operator.lexeme == "*"

    def test_power_right_assoc(self):
        expr = get_first_expr("2 ** 3 ** 4")
        assert isinstance(expr, BinaryExpr)
        assert expr.operator.lexeme == "**"
        assert isinstance(expr.right, BinaryExpr)
        assert expr.right.operator.lexeme == "**"

    def test_comparison_before_logical(self):
        expr = get_first_expr("1 < 2 kandi 3 > 4")
        assert isinstance(expr, LogicalExpr)
        assert isinstance(expr.left, BinaryExpr)
        assert isinstance(expr.right, BinaryExpr)


# ══════════════════════════════════════════════════════════════════
# Assignment Tests
# ══════════════════════════════════════════════════════════════════


class TestAssignment:
    """Tests for assignment expressions."""

    def test_simple_assignment(self):
        expr = get_first_expr("x = 42")
        assert isinstance(expr, AssignmentExpr)

    def test_compound_plus(self):
        expr = get_first_expr("x += 1")
        assert isinstance(expr, CompoundAssignmentExpr)
        assert expr.operator.lexeme == "+="

    def test_compound_minus(self):
        expr = get_first_expr("x -= 1")
        assert isinstance(expr, CompoundAssignmentExpr)
        assert expr.operator.lexeme == "-="

    def test_compound_times(self):
        expr = get_first_expr("x *= 2")
        assert isinstance(expr, CompoundAssignmentExpr)
        assert expr.operator.lexeme == "*="

    def test_compound_divide(self):
        expr = get_first_expr("x /= 2")
        assert isinstance(expr, CompoundAssignmentExpr)
        assert expr.operator.lexeme == "/="


# ══════════════════════════════════════════════════════════════════
# Call Expression Tests
# ══════════════════════════════════════════════════════════════════


class TestCallExpressions:
    """Tests for call expressions."""

    def test_simple_call(self):
        expr = get_first_expr("foo()")
        assert isinstance(expr, CallExpr)

    def test_call_with_args(self):
        expr = get_first_expr("foo(1, 2, 3)")
        assert isinstance(expr, CallExpr)
        assert len(expr.arguments) == 3

    def test_method_call(self):
        expr = get_first_expr("obj.method()")
        assert isinstance(expr, CallExpr)
        assert isinstance(expr.callee, GetExpr)

    def test_chained_calls(self):
        expr = get_first_expr("a().b()")
        assert isinstance(expr, CallExpr)
        assert isinstance(expr.callee, GetExpr)


# ══════════════════════════════════════════════════════════════════
# Index Expression Tests
# ══════════════════════════════════════════════════════════════════


class TestIndexExpressions:
    """Tests for index expressions."""

    def test_index(self):
        expr = get_first_expr("arr[0]")
        assert isinstance(expr, IndexExpr)

    def test_slice(self):
        expr = get_first_expr("arr[1:3]")
        assert isinstance(expr, SliceExpr)

    def test_slice_start_only(self):
        expr = get_first_expr("arr[1:]")
        assert isinstance(expr, SliceExpr)
        assert expr.end is None


# ══════════════════════════════════════════════════════════════════
# Collection Literal Tests
# ══════════════════════════════════════════════════════════════════


class TestCollectionLiterals:
    """Tests for collection literals."""

    def test_empty_list(self):
        expr = get_first_expr("[]")
        assert isinstance(expr, ListExpr)
        assert len(expr.elements) == 0

    def test_list_with_elements(self):
        expr = get_first_expr("[1, 2, 3]")
        assert isinstance(expr, ListExpr)
        assert len(expr.elements) == 3

    def test_empty_dict(self):
        expr = get_first_expr("{}")
        assert isinstance(expr, DictExpr)
        assert len(expr.keys) == 0

    def test_dict_with_pairs(self):
        expr = get_first_expr('{ "a": 1, "b": 2 }')
        assert isinstance(expr, DictExpr)
        assert len(expr.keys) == 2


# ══════════════════════════════════════════════════════════════════
# Statement Tests
# ══════════════════════════════════════════════════════════════════


class TestStatements:
    """Tests for statement parsing."""

    def test_var_declaration(self):
        stmt = get_first_stmt("shyira x = 42")
        assert isinstance(stmt, VarStmt)
        assert stmt.name.lexeme == "x"
        assert not stmt.is_const

    def test_const_declaration(self):
        stmt = get_first_stmt("shyira_ko x = 42")
        assert isinstance(stmt, VarStmt)
        assert stmt.is_const

    def test_var_with_type(self):
        stmt = get_first_stmt("shyira x : umubare = 42")
        assert isinstance(stmt, VarStmt)
        assert stmt.type_annotation is not None

    def test_expression_statement(self):
        stmt = get_first_stmt("foo()")
        assert isinstance(stmt, ExpressionStmt)

    def test_break_statement(self):
        stmt = get_first_stmt("gukoma")
        assert isinstance(stmt, BreakStmt)

    def test_continue_statement(self):
        stmt = get_first_stmt("kugenda")
        assert isinstance(stmt, ContinueStmt)

    def test_return_statement(self):
        stmt = get_first_stmt("subira 42")
        assert isinstance(stmt, ReturnStmt)
        assert stmt.value is not None

    def test_return_no_value(self):
        stmt = get_first_stmt("subira")
        assert isinstance(stmt, ReturnStmt)
        assert stmt.value is None


# ══════════════════════════════════════════════════════════════════
# Block Structure Tests
# ══════════════════════════════════════════════════════════════════


class TestBlockStructure:
    """Tests for kora/iherezo block structure."""

    def test_empty_block(self):
        stmt = get_first_stmt("iherezo")
        assert isinstance(stmt, BlockStmt)
        assert len(stmt.statements) == 0

    def test_block_with_statements(self):
        stmts = get_stmts("""
shyira x = 1
shyira y = 2
""")
        assert len(stmts) == 2

    def test_nested_blocks(self):
        stmts = get_stmts("""
niba x > 0 kora
    shyira y = 1
iherezo
""")
        assert len(stmts) == 1
        assert isinstance(stmts[0], IfStmt)


# ══════════════════════════════════════════════════════════════════
# If Statement Tests
# ══════════════════════════════════════════════════════════════════


class TestIfStatements:
    """Tests for if/elif/else statements."""

    def test_simple_if(self):
        stmt = get_first_stmt("niba x > 0 kora iherezo")
        assert isinstance(stmt, IfStmt)
        assert len(stmt.elif_branches) == 0
        assert stmt.else_branch is None

    def test_if_else(self):
        stmt = get_first_stmt("""
niba x > 0 kora
    subira 1
cyangwa
    subira 0
iherezo
""")
        assert isinstance(stmt, IfStmt)
        assert stmt.else_branch is not None

    def test_if_elif_else(self):
        stmt = get_first_stmt("""
niba x > 0 kora
    subira 1
cyangwa_niba x < 0 kora
    subira -1
cyangwa
    subira 0
iherezo
""")
        assert isinstance(stmt, IfStmt)
        assert len(stmt.elif_branches) == 1
        assert stmt.else_branch is not None

    def test_multiple_elif(self):
        stmt = get_first_stmt("""
niba a kora iherezo
cyangwa_niba b kora iherezo
cyangwa_niba c kora iherezo
iherezo
""")
        assert isinstance(stmt, IfStmt)
        assert len(stmt.elif_branches) == 2


# ══════════════════════════════════════════════════════════════════
# Loop Statement Tests
# ══════════════════════════════════════════════════════════════════


class TestLoopStatements:
    """Tests for loop statements."""

    def test_while_loop(self):
        stmt = get_first_stmt("wihuse x > 0 kora iherezo")
        assert isinstance(stmt, WhileStmt)

    def test_until_loop(self):
        stmt = get_first_stmt("kugeza x == 0 kora iherezo")
        assert isinstance(stmt, UntilStmt)

    def test_for_loop(self):
        stmt = get_first_stmt("kuri i = 0 kugeza 10 kora iherezo")
        assert isinstance(stmt, ForStmt)
        assert stmt.variable.lexeme == "i"

    def test_for_each_loop(self):
        stmt = get_first_stmt("buri x muri items kora iherezo")
        assert isinstance(stmt, ForEachStmt)
        assert stmt.element.lexeme == "x"


# ══════════════════════════════════════════════════════════════════
# Function Declaration Tests
# ══════════════════════════════════════════════════════════════════


class TestFunctionDeclaration:
    """Tests for function declarations."""

    def test_simple_function(self):
        stmt = get_first_stmt("umurimo foo() kora iherezo")
        assert isinstance(stmt, FunctionStmt)
        assert stmt.name.lexeme == "foo"

    def test_function_with_params(self):
        stmt = get_first_stmt("umurimo add(a, b) kora iherezo")
        assert isinstance(stmt, FunctionStmt)
        assert len(stmt.parameters) == 2

    def test_function_with_return_type(self):
        stmt = get_first_stmt("umurimo add(a) -> umubare kora iherezo")
        assert isinstance(stmt, FunctionStmt)
        assert stmt.return_type is not None

    def test_function_with_param_types(self):
        stmt = get_first_stmt("umurimo add(a : umubare, b : umubare) kora iherezo")
        assert isinstance(stmt, FunctionStmt)
        assert stmt.parameters[0].type_annotation is not None


# ══════════════════════════════════════════════════════════════════
# Class Declaration Tests
# ══════════════════════════════════════════════════════════════════


class TestClassDeclaration:
    """Tests for class declarations."""

    def test_simple_class(self):
        stmt = get_first_stmt("urwego MyClass kora iherezo")
        assert isinstance(stmt, ClassStmt)
        assert stmt.name.lexeme == "MyClass"

    def test_class_with_parent(self):
        stmt = get_first_stmt("urwego Child kugira Parent kora iherezo")
        assert isinstance(stmt, ClassStmt)
        assert stmt.parent is not None
        assert stmt.parent.lexeme == "Parent"


# ══════════════════════════════════════════════════════════════════
# Import/Export Tests
# ══════════════════════════════════════════════════════════════════


class TestImportExport:
    """Tests for import/export statements."""

    def test_import(self):
        stmt = get_first_stmt("shyiramo math")
        assert isinstance(stmt, ImportStmt)
        assert stmt.path.lexeme == "math"

    def test_import_with_alias(self):
        stmt = get_first_stmt("shyiramo math kugira_ngo m")
        assert isinstance(stmt, ImportStmt)
        assert stmt.alias is not None
        assert stmt.alias.lexeme == "m"

    def test_export(self):
        stmt = get_first_stmt("tanga foo")
        assert isinstance(stmt, ExportStmt)
        assert stmt.name.lexeme == "foo"


# ══════════════════════════════════════════════════════════════════
# Try/Catch Tests
# ══════════════════════════════════════════════════════════════════


class TestTryCatch:
    """Tests for try/catch statements."""

    def test_try_catch(self):
        stmt = get_first_stmt("""
kora
    foo()
kubika e
    bar()
iherezo
""")
        assert isinstance(stmt, TryStmt)

    def test_throw(self):
        stmt = get_first_stmt("gushyingura ubwoko")
        assert isinstance(stmt, ThrowStmt)


# ══════════════════════════════════════════════════════════════════
# Error Recovery Tests
# ══════════════════════════════════════════════════════════════════


class TestErrorRecovery:
    """Tests for error recovery."""

    def test_missing_iherezo(self):
        """Test recovery for missing iherezo."""
        ast, errors = parse("niba x > 0 kora\n    subira 1\n")
        # Should still parse something
        assert len(ast.statements) > 0

    def test_invalid_statement(self):
        """Test recovery for invalid statement."""
        ast, errors = parse("42\nshyira x = 1")
        # Should still parse the second statement
        assert len(ast.statements) >= 1

    def test_syntax_error_recovery(self):
        """Test recovery continues after error."""
        ast, errors = parse("shyira =\nshyira y = 2")
        # Should have errors but continue parsing
        assert len(errors) > 0


# ══════════════════════════════════════════════════════════════════
# Kinyarwanda Source Code Tests
# ══════════════════════════════════════════════════════════════════


class TestKinyarwandaSource:
    """Tests for Kinyarwanda source code."""

    def test_hello_world(self):
        ast = parse_no_errors("""
shyira izina = "Amakuru y'Isi"
""")
        assert len(ast.statements) == 1

    def test_function_definition(self):
        ast = parse_no_errors("""
umurimo soma(umubare) kora
    subira umubare * 2
iherezo
""")
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], FunctionStmt)

    def test_if_else(self):
        ast = parse_no_errors("""
niba umubare > 0 kora
    subira umubare
cyangwa
    subira 0
iherezo
""")
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], IfStmt)

    def test_loop(self):
        ast = parse_no_errors("""
kuri i = 0 kugeza 10 kora
    # loop body
iherezo
""")
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], ForStmt)

    def test_class_definition(self):
        ast = parse_no_errors("""
urwego Umwanda kora
    # class body
iherezo
""")
        assert len(ast.statements) == 1
        assert isinstance(ast.statements[0], ClassStmt)


# ══════════════════════════════════════════════════════════════════
# Edge Case Tests
# ══════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_source(self):
        ast = parse_source("")
        assert len(ast.statements) == 0

    def test_comments_only(self):
        ast = parse_source("# just a comment")
        assert len(ast.statements) == 0

    def test_multiple_statements(self):
        stmts = get_stmts("shyira x = 1\nshyira y = 2\nshyira z = 3")
        assert len(stmts) == 3

    def test_deeply_nested(self):
        source = "niba a kora\n" + "    " * 10 + "niba b kora iherezo\n" + "iherezo"
        ast, errors = parse(source)
        assert len(ast.statements) > 0

    def test_unicode_source(self):
        ast = parse_no_errors('shyira igiciro = 100')
        assert len(ast.statements) == 1
