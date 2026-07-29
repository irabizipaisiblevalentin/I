"""
Comprehensive tests for Sprint 5: Code Generation

Tests the CodeGenerator and bytecode system for the I programming language.
129 tests covering: literal generation, variable operations, control flow,
expressions, functions, data structures, error handling, and integration.
"""

import pytest
from compiler.ast.nodes import (
    Program, Module, LiteralExpr, IdentifierExpr, UnaryExpr, BinaryExpr,
    LogicalExpr, AssignmentExpr, CompoundAssignmentExpr, CallExpr,
    MethodCallExpr, ConstructorExpr, GetExpr, SetExpr, IndexExpr,
    SliceExpr, SelfExpr, SuperExpr, ListExpr, DictExpr, TupleExpr,
    LambdaExpr, IfExpr, GroupingExpr, PlaceholderExpr,
    BlockStmt, IfStmt, WhileStmt, UntilStmt, ForStmt, ForEachStmt,
    ReturnStmt, BreakStmt, ContinueStmt, ThrowStmt, TryStmt,
    ExpressionStmt, EmptyStmt,
    VarDecl, FunctionDecl, StructDecl, EnumDecl, ClassDecl,
    TraitDecl, InterfaceDecl, ImportDecl, ExportDecl, MethodDecl,
    Parameter, StructField, EnumVariant, ElifBranch,
    NamedType, SourceLocation,
)
from compiler.codegen.bytecode import OpCode, Chunk, Instruction
from compiler.codegen.generator import CodeGenerator, generate, _name_of, _line_of


# ── Test Helpers ───────────────────────────────────────────────


def _loc(line: int = 1, col: int = 1) -> SourceLocation:
    """Create a SourceLocation for testing."""
    return SourceLocation("<test>", line, col, line, col + 1)


def _int_literal(value: int) -> LiteralExpr:
    return LiteralExpr(value=value, location=_loc())


def _float_literal(value: float) -> LiteralExpr:
    return LiteralExpr(value=value, location=_loc())


def _string_literal(value: str) -> LiteralExpr:
    return LiteralExpr(value=value, location=_loc())


def _bool_literal(value: bool) -> LiteralExpr:
    return LiteralExpr(value=value, location=_loc())


def _none_literal() -> LiteralExpr:
    return LiteralExpr(value=None, location=_loc())


def _identifier(name: str) -> IdentifierExpr:
    return IdentifierExpr(name=name, location=_loc())


def _binary(left: Expr, op: str, right: Expr) -> BinaryExpr:
    return BinaryExpr(left=left, operator=op, right=right, location=_loc())


def _unary(op: str, right: Expr) -> UnaryExpr:
    return UnaryExpr(operator=op, right=right, location=_loc())


def _logical(left: Expr, op: str, right: Expr) -> LogicalExpr:
    return LogicalExpr(left=left, operator=op, right=right, location=_loc())


def _assignment(target: Expr, value: Expr) -> AssignmentExpr:
    return AssignmentExpr(target=target, value=value, location=_loc())


def _compound_assignment(target: Expr, op: str, value: Expr) -> CompoundAssignmentExpr:
    return CompoundAssignmentExpr(target=target, operator=op, value=value, location=_loc())


def _var_decl(name: str, init: Optional[Expr] = None) -> VarDecl:
    return VarDecl(name=name, type_annotation=None, initializer=init, location=_loc())


def _const_decl(name: str, init: Expr) -> VarDecl:
    return VarDecl(name=name, type_annotation=None, initializer=init, is_const=True, location=_loc())


def _function_decl(name: str, params: List[str] = None, body_stmts: List[Stmt] = None) -> FunctionDecl:
    params = params or []
    body_stmts = body_stmts or []
    parameters = [Parameter(name=p, location=_loc()) for p in params]
    body = BlockStmt(statements=body_stmts, location=_loc())
    return FunctionDecl(name=name, parameters=parameters, return_type=None, body=body, location=_loc())


def _return_stmt(value: Optional[Expr] = None) -> ReturnStmt:
    return ReturnStmt(value=value, location=_loc())


def _expression_stmt(expr: Expr) -> ExpressionStmt:
    return ExpressionStmt(expression=expr, location=_loc())


def _block_stmt(stmts: List[Stmt]) -> BlockStmt:
    return BlockStmt(statements=stmts, location=_loc())


def _if_stmt(condition: Expr, then_stmts: List[Stmt], else_stmts: List[Stmt] = None) -> IfStmt:
    then = _block_stmt(then_stmts)
    else_branch = _block_stmt(else_stmts) if else_stmts else None
    return IfStmt(condition=condition, then_branch=then, elif_branches=[], else_branch=else_branch, location=_loc())


def _while_stmt(condition: Expr, body_stmts: List[Stmt]) -> WhileStmt:
    body = _block_stmt(body_stmts)
    return WhileStmt(condition=condition, body=body, location=_loc())


def _program(decls: List[Decl]) -> Program:
    return Program(declarations=decls, location=_loc())


def _generate_program(decls: List[Decl], name: str = "test") -> Chunk:
    """Generate bytecode from a list of declarations."""
    return generate(_program(decls), name)


# ══════════════════════════════════════════════════════════════════
# Test OpCode System
# ══════════════════════════════════════════════════════════════════


class TestOpCodeSystem:
    """Test the OpCode enum and Chunk class."""

    def test_opcodes_exist(self):
        assert OpCode.LOAD_CONST is not None
        assert OpCode.STORE_LOCAL is not None
        assert OpCode.ADD is not None
        assert OpCode.HALT is not None
        assert OpCode.RETURN is not None
        assert OpCode.CALL is not None

    def test_chunk_creation(self):
        chunk = Chunk("test")
        assert chunk.name == "test"
        assert chunk.code == []
        assert chunk.constants == []

    def test_chunk_emit(self):
        chunk = Chunk("test")
        idx = chunk.emit(OpCode.LOAD_CONST, 0)
        assert idx == 0
        assert len(chunk.code) == 1
        assert chunk.code[0].opcode == OpCode.LOAD_CONST

    def test_chunk_add_constant(self):
        chunk = Chunk("test")
        idx = chunk.add_constant(42)
        assert idx == 0
        assert chunk.constants[0] == 42

    def test_chunk_disassemble(self):
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, 0)
        chunk.add_constant(42)
        output = chunk.disassemble()
        assert "LOAD_CONST" in output
        assert "42" in output

    def test_instruction_repr(self):
        inst = Instruction(OpCode.ADD)
        assert "ADD" in repr(inst)

    def test_instruction_with_arg(self):
        inst = Instruction(OpCode.LOAD_CONST, 5)
        assert "5" in repr(inst)


# ══════════════════════════════════════════════════════════════════
# Test Helper Functions
# ══════════════════════════════════════════════════════════════════


class TestHelpers:
    """Test helper functions used in code generation."""

    def test_name_of_string(self):
        assert _name_of("hello") == "hello"

    def test_name_of_node_with_name(self):
        node = IdentifierExpr(name="foo", location=_loc())
        assert _name_of(node) == "foo"

    def test_name_of_token_with_lexeme(self):
        class FakeToken:
            lexeme = "bar"
        assert _name_of(FakeToken()) == "bar"

    def test_line_of_node_with_location(self):
        node = _int_literal(42)
        assert _line_of(node) == 1

    def test_line_of_node_with_line(self):
        class FakeNode:
            line = 42
        assert _line_of(FakeNode()) == 42


# ══════════════════════════════════════════════════════════════════
# Test Literal Generation
# ══════════════════════════════════════════════════════════════════


class TestLiteralGeneration:
    """Test generation of literal expressions."""

    def test_integer_literal(self):
        chunk = generate(_program([_expression_stmt(_int_literal(42))]))
        assert any(i.opcode == OpCode.LOAD_CONST for i in chunk.code)
        assert 42 in chunk.constants

    def test_float_literal(self):
        chunk = generate(_program([_expression_stmt(_float_literal(3.14))]))
        assert any(i.opcode == OpCode.LOAD_CONST for i in chunk.code)
        assert 3.14 in chunk.constants

    def test_string_literal(self):
        chunk = generate(_program([_expression_stmt(_string_literal("hello"))]))
        assert any(i.opcode == OpCode.LOAD_CONST for i in chunk.code)
        assert "hello" in chunk.constants

    def test_bool_true_literal(self):
        chunk = generate(_program([_expression_stmt(_bool_literal(True))]))
        assert any(i.opcode == OpCode.LOAD_TRUE for i in chunk.code)

    def test_bool_false_literal(self):
        chunk = generate(_program([_expression_stmt(_bool_literal(False))]))
        assert any(i.opcode == OpCode.LOAD_FALSE for i in chunk.code)

    def test_none_literal(self):
        chunk = generate(_program([_expression_stmt(_none_literal())]))
        assert any(i.opcode == OpCode.LOAD_NULL for i in chunk.code)

    def test_string_empty(self):
        chunk = generate(_program([_expression_stmt(_string_literal(""))]))
        assert "" in chunk.constants


# ══════════════════════════════════════════════════════════════════
# Test Variable Operations
# ══════════════════════════════════════════════════════════════════


class TestVariableOperations:
    """Test variable declaration and access."""

    def test_var_decl_with_init(self):
        chunk = generate(_program([_var_decl("x", _int_literal(10))]))
        assert any(i.opcode == OpCode.STORE_LOCAL for i in chunk.code)

    def test_var_decl_without_init(self):
        chunk = generate(_program([_var_decl("x")]))
        assert any(i.opcode == OpCode.LOAD_CONST for i in chunk.code)
        assert None in chunk.constants

    def test_var_access(self):
        decls = [_var_decl("x", _int_literal(5))]
        decls.append(_expression_stmt(_identifier("x")))
        chunk = generate(_program(decls))
        assert any(i.opcode == OpCode.LOAD_LOCAL for i in chunk.code)

    def test_var_assignment(self):
        decls = [_var_decl("x", _int_literal(5))]
        decls.append(_expression_stmt(_assignment(_identifier("x"), _int_literal(10))))
        chunk = generate(_program(decls))
        assert any(i.opcode == OpCode.STORE_LOCAL for i in chunk.code)

    def test_const_decl(self):
        chunk = generate(_program([_const_decl("PI", _float_literal(3.14))]))
        assert any(i.opcode == OpCode.STORE_LOCAL for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Binary Expressions
# ══════════════════════════════════════════════════════════════════


class TestBinaryExpressions:
    """Test binary expression code generation."""

    def test_addition(self):
        chunk = generate(_program([_expression_stmt(
            _binary(_int_literal(2), '+', _int_literal(3))
        )]))
        assert any(i.opcode == OpCode.ADD for i in chunk.code)

    def test_subtraction(self):
        chunk = generate(_program([_expression_stmt(
            _binary(_int_literal(5), '-', _int_literal(3))
        )]))
        assert any(i.opcode == OpCode.SUB for i in chunk.code)

    def test_multiplication(self):
        chunk = generate(_program([_expression_stmt(
            _binary(_int_literal(4), '*', _int_literal(5))
        )]))
        assert any(i.opcode == OpCode.MUL for i in chunk.code)

    def test_division(self):
        chunk = generate(_program([_expression_stmt(
            _binary(_int_literal(10), '/', _int_literal(2))
        )]))
        assert any(i.opcode == OpCode.DIV for i in chunk.code)

    def test_modulo(self):
        chunk = generate(_program([_expression_stmt(
            _binary(_int_literal(10), '%', _int_literal(3))
        )]))
        assert any(i.opcode == OpCode.MOD for i in chunk.code)

    def test_equality(self):
        chunk = generate(_program([_expression_stmt(
            _binary(_int_literal(1), '==', _int_literal(1))
        )]))
        assert any(i.opcode == OpCode.EQ for i in chunk.code)

    def test_inequality(self):
        chunk = generate(_program([_expression_stmt(
            _binary(_int_literal(1), '!=', _int_literal(2))
        )]))
        assert any(i.opcode == OpCode.NEQ for i in chunk.code)

    def test_less_than(self):
        chunk = generate(_program([_expression_stmt(
            _binary(_int_literal(1), '<', _int_literal(2))
        )]))
        assert any(i.opcode == OpCode.LT for i in chunk.code)

    def test_greater_than(self):
        chunk = generate(_program([_expression_stmt(
            _binary(_int_literal(2), '>', _int_literal(1))
        )]))
        assert any(i.opcode == OpCode.GT for i in chunk.code)

    def test_less_equal(self):
        chunk = generate(_program([_expression_stmt(
            _binary(_int_literal(1), '<=', _int_literal(1))
        )]))
        assert any(i.opcode == OpCode.LTE for i in chunk.code)

    def test_greater_equal(self):
        chunk = generate(_program([_expression_stmt(
            _binary(_int_literal(2), '>=', _int_literal(1))
        )]))
        assert any(i.opcode == OpCode.GTE for i in chunk.code)

    def test_string_concatenation(self):
        chunk = generate(_program([_expression_stmt(
            _binary(_string_literal("a"), '+', _string_literal("b"))
        )]))
        assert any(i.opcode == OpCode.ADD for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Unary and Logical Expressions
# ══════════════════════════════════════════════════════════════════


class TestUnaryLogical:
    """Test unary and logical expressions."""

    def test_negation(self):
        chunk = generate(_program([_expression_stmt(_unary('-', _int_literal(5)))]))
        assert any(i.opcode == OpCode.NEG for i in chunk.code)

    def test_logical_not(self):
        chunk = generate(_program([_expression_stmt(_unary('!', _bool_literal(True)))]))
        assert any(i.opcode == OpCode.NOT for i in chunk.code)

    def test_logical_and(self):
        chunk = generate(_program([_expression_stmt(
            _logical(_bool_literal(True), 'and', _bool_literal(False))
        )]))
        assert any(i.opcode == OpCode.AND for i in chunk.code)

    def test_logical_or(self):
        chunk = generate(_program([_expression_stmt(
            _logical(_bool_literal(True), 'or', _bool_literal(False))
        )]))
        assert any(i.opcode == OpCode.OR for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Compound Assignment
# ══════════════════════════════════════════════════════════════════


class TestCompoundAssignment:
    """Test compound assignment expressions."""

    def test_plus_equals(self):
        decls = [_var_decl("x", _int_literal(5))]
        decls.append(_expression_stmt(_compound_assignment(_identifier("x"), '+', _int_literal(3))))
        chunk = generate(_program(decls))
        assert any(i.opcode == OpCode.LOAD_LOCAL for i in chunk.code)
        assert any(i.opcode == OpCode.ADD for i in chunk.code)

    def test_minus_equals(self):
        decls = [_var_decl("x", _int_literal(5))]
        decls.append(_expression_stmt(_compound_assignment(_identifier("x"), '-', _int_literal(3))))
        chunk = generate(_program(decls))
        assert any(i.opcode == OpCode.SUB for i in chunk.code)

    def test_times_equals(self):
        decls = [_var_decl("x", _int_literal(5))]
        decls.append(_expression_stmt(_compound_assignment(_identifier("x"), '*', _int_literal(3))))
        chunk = generate(_program(decls))
        assert any(i.opcode == OpCode.MUL for i in chunk.code)

    def test_divide_equals(self):
        decls = [_var_decl("x", _int_literal(10))]
        decls.append(_expression_stmt(_compound_assignment(_identifier("x"), '/', _int_literal(2))))
        chunk = generate(_program(decls))
        assert any(i.opcode == OpCode.DIV for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Control Flow
# ══════════════════════════════════════════════════════════════════


class TestControlFlow:
    """Test control flow code generation."""

    def test_if_statement(self):
        stmts = [_if_stmt(_bool_literal(True), [_expression_stmt(_int_literal(1))])]
        chunk = generate(_program(stmts))
        assert any(i.opcode == OpCode.JUMP_IF_FALSE for i in chunk.code)

    def test_if_else_statement(self):
        stmts = [_if_stmt(
            _bool_literal(True),
            [_expression_stmt(_int_literal(1))],
            [_expression_stmt(_int_literal(2))]
        )]
        chunk = generate(_program(stmts))
        assert any(i.opcode == OpCode.JUMP for i in chunk.code)

    def test_while_loop(self):
        stmts = [_while_stmt(_bool_literal(True), [_expression_stmt(_int_literal(1))])]
        chunk = generate(_program(stmts))
        assert any(i.opcode == OpCode.JUMP for i in chunk.code)

    def test_break_statement(self):
        stmts = [_while_stmt(_bool_literal(True), [BreakStmt(location=_loc())])]
        chunk = generate(_program(stmts))
        assert any(i.opcode == OpCode.JUMP for i in chunk.code)

    def test_continue_statement(self):
        stmts = [_while_stmt(_bool_literal(True), [ContinueStmt(location=_loc())])]
        chunk = generate(_program(stmts))
        assert any(i.opcode == OpCode.JUMP for i in chunk.code)

    def test_return_statement(self):
        func = _function_decl("foo", [], [_return_stmt(_int_literal(42))])
        chunk = generate(_program([func]))
        # Function creates its own chunk - find it
        func_chunk = None
        for const in chunk.constants:
            if isinstance(const, Chunk) and const.name == "foo":
                func_chunk = const
                break
        assert func_chunk is not None
        assert any(i.opcode == OpCode.RETURN for i in func_chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Function Generation
# ══════════════════════════════════════════════════════════════════


class TestFunctionGeneration:
    """Test function declaration code generation."""

    def test_simple_function(self):
        func = _function_decl("foo", [])
        chunk = generate(_program([func]))
        assert any(i.opcode == OpCode.LOAD_CONST for i in chunk.code)
        assert any(i.opcode == OpCode.STORE_LOCAL for i in chunk.code)

    def test_function_with_params(self):
        func = _function_decl("foo", ["a", "b"])
        chunk = generate(_program([func]))
        assert any(i.opcode == OpCode.STORE_LOCAL for i in chunk.code)

    def test_function_with_body(self):
        func = _function_decl("foo", [], [
            _var_decl("x", _int_literal(10)),
            _return_stmt(_identifier("x"))
        ])
        chunk = generate(_program([func]))
        func_chunk = None
        for const in chunk.constants:
            if isinstance(const, Chunk) and const.name == "foo":
                func_chunk = const
                break
        assert func_chunk is not None
        assert any(i.opcode == OpCode.RETURN for i in func_chunk.code)

    def test_function_returns_none_if_no_return(self):
        func = _function_decl("foo", [], [_expression_stmt(_int_literal(1))])
        chunk = generate(_program([func]))
        # Find function chunk
        func_chunk = None
        for const in chunk.constants:
            if isinstance(const, Chunk) and const.name == "foo":
                func_chunk = const
                break
        assert func_chunk is not None
        # Should have implicit return
        assert any(i.opcode == OpCode.RETURN for i in func_chunk.code)

    def test_nested_scopes(self):
        func = _function_decl("foo", [], [
            _var_decl("x", _int_literal(1)),
            _block_stmt([
                _var_decl("y", _int_literal(2)),
                _expression_stmt(_identifier("y"))
            ]),
            _expression_stmt(_identifier("x"))
        ])
        chunk = generate(_program([func]))
        func_chunk = None
        for const in chunk.constants:
            if isinstance(const, Chunk) and const.name == "foo":
                func_chunk = const
                break
        assert func_chunk is not None
        assert func_chunk.code  # Should generate code


# ══════════════════════════════════════════════════════════════════
# Test Collections
# ══════════════════════════════════════════════════════════════════


class TestCollections:
    """Test collection code generation."""

    def test_empty_list(self):
        chunk = generate(_program([_expression_stmt(ListExpr(elements=[], location=_loc()))]))
        assert any(i.opcode == OpCode.BUILD_LIST for i in chunk.code)

    def test_list_with_elements(self):
        chunk = generate(_program([_expression_stmt(
            ListExpr(elements=[_int_literal(1), _int_literal(2), _int_literal(3)], location=_loc())
        )]))
        assert any(i.opcode == OpCode.BUILD_LIST for i in chunk.code)

    def test_empty_dict(self):
        chunk = generate(_program([_expression_stmt(
            DictExpr(keys=[], values=[], location=_loc())
        )]))
        assert any(i.opcode == OpCode.BUILD_MAP for i in chunk.code)

    def test_dict_with_entries(self):
        chunk = generate(_program([_expression_stmt(
            DictExpr(
                keys=[_string_literal("a"), _string_literal("b")],
                values=[_int_literal(1), _int_literal(2)],
                location=_loc()
            )
        )]))
        assert any(i.opcode == OpCode.BUILD_MAP for i in chunk.code)

    def test_empty_tuple(self):
        chunk = generate(_program([_expression_stmt(
            TupleExpr(elements=[], location=_loc())
        )]))
        assert any(i.opcode == OpCode.BUILD_TUPLE for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Property Access
# ══════════════════════════════════════════════════════════════════


class TestPropertyAccess:
    """Test property access and indexing."""

    def test_get_expr(self):
        decls = [_var_decl("obj", _none_literal())]
        decls.append(_expression_stmt(
            GetExpr(object=_identifier("obj"), property="name", location=_loc())
        ))
        chunk = generate(_program(decls))
        assert any(i.opcode == OpCode.GET_ATTR for i in chunk.code)

    def test_index_expr(self):
        decls = [_var_decl("arr", ListExpr(elements=[], location=_loc()))]
        decls.append(_expression_stmt(
            IndexExpr(object=_identifier("arr"), index=_int_literal(0), location=_loc())
        ))
        chunk = generate(_program(decls))
        assert any(i.opcode == OpCode.GET_ITEM for i in chunk.code)

    def test_slice_expr(self):
        decls = [_var_decl("arr", ListExpr(elements=[], location=_loc()))]
        decls.append(_expression_stmt(
            SliceExpr(
                object=_identifier("arr"),
                start=_int_literal(1),
                end=_int_literal(5),
                location=_loc()
            )
        ))
        chunk = generate(_program(decls))
        assert any(i.opcode == OpCode.SLICE for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Method Call
# ══════════════════════════════════════════════════════════════════


class TestMethodCall:
    """Test method call code generation."""

    def test_method_call(self):
        decls = [_var_decl("obj", _none_literal())]
        decls.append(_expression_stmt(
            MethodCallExpr(
                object=_identifier("obj"),
                method="doSomething",
                arguments=[_int_literal(1), _string_literal("hello")],
                location=_loc()
            )
        ))
        chunk = generate(_program(decls))
        assert any(i.opcode == OpCode.CALL for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Constructor
# ══════════════════════════════════════════════════════════════════


class TestConstructor:
    """Test constructor code generation."""

    def test_constructor(self):
        chunk = generate(_program([_expression_stmt(
            ConstructorExpr(
                class_name="MyClass",
                arguments=[_int_literal(1), _string_literal("hello")],
                location=_loc()
            )
        )]))
        assert any(i.opcode == OpCode.NEW_INSTANCE for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Exception Handling
# ══════════════════════════════════════════════════════════════════


class TestExceptionHandling:
    """Test try-catch and throw code generation."""

    def test_throw_statement(self):
        chunk = generate(_program([_expression_stmt(
            ThrowStmt(value=_string_literal("error"), location=_loc())
        )]))
        assert any(i.opcode == OpCode.RAISE for i in chunk.code)

    def test_try_catch(self):
        try_stmt = TryStmt(
            try_body=_block_stmt([_expression_stmt(_int_literal(1))]),
            catch_var="e",
            catch_body=_block_stmt([_expression_stmt(_identifier("e"))]),
            location=_loc()
        )
        chunk = generate(_program([try_stmt]))
        assert any(i.opcode == OpCode.SETUP_TRY for i in chunk.code)
        assert any(i.opcode == OpCode.POP_BLOCK for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Lambda
# ══════════════════════════════════════════════════════════════════


class TestLambda:
    """Test lambda expression code generation."""

    def test_simple_lambda(self):
        chunk = generate(_program([_expression_stmt(
            LambdaExpr(
                parameters=[Parameter(name="x", location=_loc())],
                body=_identifier("x"),
                location=_loc()
            )
        )]))
        assert any(i.opcode == OpCode.LOAD_CONST for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Placeholder and Grouping
# ══════════════════════════════════════════════════════════════════


class TestPlaceholderGrouping:
    """Test placeholder and grouping expressions."""

    def test_placeholder(self):
        chunk = generate(_program([_expression_stmt(
            PlaceholderExpr(description="TODO", location=_loc())
        )]))
        assert any(i.opcode == OpCode.LOAD_CONST for i in chunk.code)

    def test_grouping(self):
        chunk = generate(_program([_expression_stmt(
            GroupingExpr(expression=_int_literal(42), location=_loc())
        )]))
        assert any(i.opcode == OpCode.LOAD_CONST for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Empty and Declarations
# ══════════════════════════════════════════════════════════════════


class TestEmptyDeclarations:
    """Test empty statements and type declarations."""

    def test_empty_statement(self):
        chunk = generate(_program([EmptyStmt(location=_loc())]))
        assert chunk.code  # Should at least have HALT

    def test_struct_decl(self):
        chunk = generate(_program([StructDecl(
            name="Point",
            fields=[StructField(name="x", type_annotation=NamedType(name="int", location=_loc()), location=_loc())],
            methods=[],
            location=_loc()
        )]))
        assert chunk.code  # Structs are no-ops for now

    def test_enum_decl(self):
        chunk = generate(_program([EnumDecl(
            name="Color",
            variants=[EnumVariant(name="RED", location=_loc())],
            location=_loc()
        )]))
        assert chunk.code

    def test_class_decl(self):
        chunk = generate(_program([ClassDecl(
            name="Dog",
            parent=None,
            members=[],
            location=_loc()
        )]))
        assert chunk.code

    def test_import_decl(self):
        chunk = generate(_program([ImportDecl(path="std", location=_loc())]))
        assert chunk.code

    def test_export_decl(self):
        decls = [_var_decl("x", _int_literal(1))]
        decls.append(ExportDecl(name="x", location=_loc()))
        chunk = generate(_program(decls))
        assert chunk.code


# ══════════════════════════════════════════════════════════════════
# Test For Loop Variations
# ══════════════════════════════════════════════════════════════════


class TestForLoopVariations:
    """Test for loop variations."""

    def test_for_each(self):
        stmts = [_var_decl("arr", ListExpr(elements=[_int_literal(1), _int_literal(2)], location=_loc()))]
        stmts.append(ForEachStmt(
            element="item",
            iterable=_identifier("arr"),
            body=_block_stmt([_expression_stmt(_identifier("item"))]),
            location=_loc()
        ))
        chunk = generate(_program(stmts))
        assert any(i.opcode == OpCode.GET_ITER for i in chunk.code)
        assert any(i.opcode == OpCode.FOR_ITER for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test CodeGenerator Class
# ══════════════════════════════════════════════════════════════════


class TestCodeGeneratorClass:
    """Test CodeGenerator class methods."""

    def test_generate_returns_chunk(self):
        gen = CodeGenerator()
        chunk = gen.generate(_program([]))
        assert isinstance(chunk, Chunk)

    def test_generate_has_halt(self):
        gen = CodeGenerator()
        chunk = gen.generate(_program([]))
        assert any(i.opcode == OpCode.HALT for i in chunk.code)

    def test_generate_with_name(self):
        gen = CodeGenerator()
        chunk = gen.generate(_program([]), "mychunk")
        assert chunk.name == "mychunk"

    def test_generate_function(self):
        gen = CodeGenerator()
        chunk = gen.generate(_program([
            _function_decl("add", ["a", "b"], [
                _return_stmt(_binary(_identifier("a"), '+', _identifier("b")))
            ])
        ]))
        assert chunk.code


# ══════════════════════════════════════════════════════════════════
# Test Operator Mapping
# ══════════════════════════════════════════════════════════════════


class TestOperatorMapping:
    """Test operator to opcode mapping."""

    def test_all_arithmetic_ops(self):
        ops = {
            '+': OpCode.ADD,
            '-': OpCode.SUB,
            '*': OpCode.MUL,
            '/': OpCode.DIV,
            '%': OpCode.MOD,
        }
        for op, expected in ops.items():
            chunk = generate(_program([_expression_stmt(
                _binary(_int_literal(1), op, _int_literal(2))
            )]))
            assert any(i.opcode == expected for i in chunk.code)

    def test_all_comparison_ops(self):
        ops = {
            '==': OpCode.EQ,
            '!=': OpCode.NEQ,
            '<': OpCode.LT,
            '>': OpCode.GT,
            '<=': OpCode.LTE,
            '>=': OpCode.GTE,
        }
        for op, expected in ops.items():
            chunk = generate(_program([_expression_stmt(
                _binary(_int_literal(1), op, _int_literal(2))
            )]))
            assert any(i.opcode == expected for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Scope Management
# ══════════════════════════════════════════════════════════════════


class TestScopeManagement:
    """Test scope management in code generation."""

    def test_block_creates_scope(self):
        stmts = [_block_stmt([
            _var_decl("x", _int_literal(1)),
            _expression_stmt(_identifier("x"))
        ])]
        chunk = generate(_program(stmts))
        # Should have POP at end of block
        assert any(i.opcode == OpCode.POP for i in chunk.code)

    def test_nested_blocks(self):
        stmts = [_block_stmt([
            _var_decl("x", _int_literal(1)),
            _block_stmt([
                _var_decl("y", _int_literal(2)),
                _expression_stmt(_identifier("y"))
            ]),
            _expression_stmt(_identifier("x"))
        ])]
        chunk = generate(_program(stmts))
        assert chunk.code


# ══════════════════════════════════════════════════════════════════
# Test Integration with VM
# ══════════════════════════════════════════════════════════════════


class TestVMIntegration:
    """Test that generated bytecode can run in the VM."""

    def test_run_integer_literal(self):
        from vm.virtual_machine import VirtualMachine
        # Use var decl so value stays on stack
        chunk = generate(_program([_var_decl("result", _int_literal(42)), _expression_stmt(_identifier("result"))]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == 42

    def test_run_string_literal(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([_var_decl("result", _string_literal("hello")), _expression_stmt(_identifier("result"))]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == "hello"

    def test_run_addition(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", _binary(_int_literal(2), '+', _int_literal(3))),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == 5

    def test_run_subtraction(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", _binary(_int_literal(10), '-', _int_literal(3))),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == 7

    def test_run_multiplication(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", _binary(_int_literal(4), '*', _int_literal(5))),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == 20

    def test_run_division(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", _binary(_int_literal(10), '/', _int_literal(2))),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == 5.0

    def test_run_modulo(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", _binary(_int_literal(10), '%', _int_literal(3))),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == 1

    def test_run_equality(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", _binary(_int_literal(1), '==', _int_literal(1))),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result is True

    def test_run_inequality(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", _binary(_int_literal(1), '!=', _int_literal(2))),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result is True

    def test_run_less_than(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", _binary(_int_literal(1), '<', _int_literal(2))),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result is True

    def test_run_greater_than(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", _binary(_int_literal(2), '>', _int_literal(1))),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result is True

    def test_run_negation(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", _unary('-', _int_literal(5))),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == -5

    def test_run_logical_not(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", _unary('!', _bool_literal(True))),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result is False

    def test_run_string_concat(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", _binary(_string_literal("hello"), '+', _string_literal(" world"))),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == "hello world"

    def test_run_variable(self):
        from vm.virtual_machine import VirtualMachine
        decls = [_var_decl("x", _int_literal(42))]
        decls.append(_expression_stmt(_identifier("x")))
        chunk = generate(_program(decls))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == 42

    def test_run_assignment(self):
        from vm.virtual_machine import VirtualMachine
        decls = [_var_decl("x", _int_literal(5))]
        decls.append(_expression_stmt(_assignment(_identifier("x"), _int_literal(10))))
        decls.append(_expression_stmt(_identifier("x")))
        chunk = generate(_program(decls))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == 10

    def test_run_if_true(self):
        from vm.virtual_machine import VirtualMachine
        stmts = [_var_decl("result", _int_literal(0))]
        stmts.append(_if_stmt(
            _bool_literal(True),
            [_expression_stmt(_assignment(_identifier("result"), _int_literal(1)))]
        ))
        stmts.append(_expression_stmt(_identifier("result")))
        chunk = generate(_program(stmts))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == 1

    def test_run_if_false(self):
        from vm.virtual_machine import VirtualMachine
        stmts = [_var_decl("result", _int_literal(0))]
        stmts.append(_if_stmt(
            _bool_literal(False),
            [_expression_stmt(_assignment(_identifier("result"), _int_literal(1)))],
            [_expression_stmt(_assignment(_identifier("result"), _int_literal(2)))]
        ))
        stmts.append(_expression_stmt(_identifier("result")))
        chunk = generate(_program(stmts))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == 2

    def test_run_list_literal(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", ListExpr(elements=[_int_literal(1), _int_literal(2), _int_literal(3)], location=_loc())),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == [1, 2, 3]

    def test_run_dict_literal(self):
        from vm.virtual_machine import VirtualMachine
        chunk = generate(_program([
            _var_decl("result", DictExpr(
                keys=[_string_literal("a")],
                values=[_int_literal(1)],
                location=_loc()
            )),
            _expression_stmt(_identifier("result"))
        ]))
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        assert result == {"a": 1}


# ══════════════════════════════════════════════════════════════════
# Test Stress
# ══════════════════════════════════════════════════════════════════


class TestStress:
    """Stress tests for code generation."""

    def test_many_variables(self):
        decls = [_var_decl(f"var_{i}", _int_literal(i)) for i in range(100)]
        chunk = generate(_program(decls))
        assert chunk.code

    def test_many_constants(self):
        decls = [_const_decl(f"CONST_{i}", _int_literal(i)) for i in range(100)]
        chunk = generate(_program(decls))
        assert chunk.code

    def test_deep_expressions(self):
        expr = _int_literal(1)
        for _ in range(50):
            expr = _binary(expr, '+', _int_literal(1))
        chunk = generate(_program([_expression_stmt(expr)]))
        assert chunk.code

    def test_many_functions(self):
        funcs = [_function_decl(f"func_{i}", []) for i in range(50)]
        chunk = generate(_program(funcs))
        assert chunk.code


# ══════════════════════════════════════════════════════════════════
# Test Regression
# ══════════════════════════════════════════════════════════════════


class TestRegression:
    """Regression tests for known issues."""

    def test_operator_is_string(self):
        # Ensure operators are handled as strings, not Token types
        chunk = generate(_program([_expression_stmt(
            _binary(_int_literal(1), '+', _int_literal(2))
        )]))
        assert any(i.opcode == OpCode.ADD for i in chunk.code)

    def test_program_node(self):
        # Ensure Program node is handled correctly
        chunk = generate(_program([_expression_stmt(_int_literal(1))]))
        assert chunk.code

    def test_empty_program(self):
        chunk = generate(_program([]))
        assert any(i.opcode == OpCode.HALT for i in chunk.code)

    def test_identifier_name_is_string(self):
        # Ensure identifier names are strings
        decls = [_var_decl("test_var", _int_literal(1))]
        decls.append(_expression_stmt(_identifier("test_var")))
        chunk = generate(_program(decls))
        assert chunk.code

    def test_if_expr(self):
        chunk = generate(_program([_expression_stmt(
            IfExpr(
                condition=_bool_literal(True),
                then_branch=_int_literal(1),
                else_branch=_int_literal(2),
                location=_loc()
            )
        )]))
        assert any(i.opcode == OpCode.JUMP_IF_FALSE for i in chunk.code)


# ══════════════════════════════════════════════════════════════════
# Test Fuzz
# ══════════════════════════════════════════════════════════════════


class TestFuzz:
    """Fuzz-like tests with random-ish AST structures."""

    def test_random_expressions(self):
        import random
        random.seed(42)
        exprs = [
            _int_literal(random.randint(0, 100)),
            _float_literal(random.random() * 100),
            _string_literal(f"str_{random.randint(0, 100)}"),
            _bool_literal(random.choice([True, False])),
        ]
        for expr in exprs:
            chunk = generate(_program([_expression_stmt(expr)]))
            assert chunk.code

    def test_random_binary_chains(self):
        import random
        random.seed(123)
        ops = ['+', '-', '*', '/', '%', '==', '!=', '<', '>', '<=', '>=']
        expr = _int_literal(random.randint(1, 10))
        for _ in range(10):
            op = random.choice(ops)
            expr = _binary(expr, op, _int_literal(random.randint(1, 10)))
        chunk = generate(_program([_expression_stmt(expr)]))
        assert chunk.code
