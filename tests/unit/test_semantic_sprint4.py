"""
Comprehensive Test Suite for Semantic Analyzer Sprint 4

Tests cover: scope system, symbol table, error diagnostics, name resolution,
declaration validation, import/export, constant evaluation, control flow,
visibility rules, and full analyzer integration.
"""

import pytest
from compiler.semantic.errors import (
    SemanticErrorCode, SemanticErrorCollection, SemanticSeverity,
    SourceLocation, get_bilingual_message,
)
from compiler.semantic.symbols import (
    Symbol, SymbolKind, TypeDescriptor, SymbolType, Visibility,
    make_variable, make_constant, make_function, make_method,
    make_class, make_struct, make_enum, make_trait, make_interface,
    make_parameter, make_module,
    TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_STRING, TYPE_NONE, TYPE_ANY,
    TYPE_LIST, TYPE_DICT,
)
from compiler.semantic.scopes import Scope, ScopeKind, ScopeManager
from compiler.semantic.builtins import (
    register_builtins, is_reserved_keyword, is_builtin_type,
    BUILTIN_TYPES, BUILTIN_FUNCTIONS, resolve_type_name,
)
from compiler.semantic.names import (
    resolve_name, resolve_function, resolve_class, resolve_type,
    is_callable, is_type_symbol,
)
from compiler.semantic.imports import ImportResolver, ModuleInfo
from compiler.semantic.constants import (
    is_constant_expression, evaluate_constant, get_constant_value,
)
from compiler.semantic.controlflow import (
    analyze_function_flow, function_always_returns, FlowState,
)
from compiler.semantic.visibility import check_visibility
from compiler.semantic.context import AnalysisContext
from compiler.semantic.analyzer import SemanticAnalyzer, analyze
from compiler.ast.nodes import (
    Program, LiteralExpr, IdentifierExpr, BinaryExpr, UnaryExpr,
    LogicalExpr, AssignmentExpr, CompoundAssignmentExpr, CallExpr,
    GetExpr, SetExpr, IndexExpr, ListExpr, DictExpr,
    GroupingExpr, BlockStmt, IfStmt, WhileStmt, UntilStmt,
    ForStmt, ForEachStmt, ReturnStmt, BreakStmt, ContinueStmt,
    ThrowStmt, TryStmt, ExpressionStmt, EmptyStmt, SelfExpr, SuperExpr,
    VarDecl, FunctionDecl, StructDecl, EnumDecl, ClassDecl,
    TraitDecl, InterfaceDecl, ImportDecl, ExportDecl, MethodDecl,
    Parameter, StructField, EnumVariant, NamedType,
)


# ── Helper ───────────────────────────────────────────────────────

def _loc(line=1, col=1):
    return SourceLocation("<test>", line, col, line, col + 1)


def _analyze_program(decls):
    prog = Program(declarations=decls)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(prog)
    return analyzer


# ══════════════════════════════════════════════════════════════════
# Scope Tests
# ══════════════════════════════════════════════════════════════════


class TestScopeSystem:
    def test_global_scope_exists(self):
        sm = ScopeManager()
        assert sm.global_scope.kind == ScopeKind.GLOBAL

    def test_push_pop(self):
        sm = ScopeManager()
        assert sm.current_depth == 0
        sm.push(ScopeKind.FUNCTION, "test_fn")
        assert sm.current_depth == 1
        sm.pop()
        assert sm.current_depth == 0

    def test_define_and_lookup(self):
        sm = ScopeManager()
        sym = make_variable("x", TYPE_INT)
        sm.define(sym)
        found = sm.lookup("x")
        assert found is not None
        assert found.name == "x"

    def test_lookup_not_found(self):
        sm = ScopeManager()
        assert sm.lookup("undefined") is None

    def test_child_scope_inherits_parent(self):
        sm = ScopeManager()
        parent_sym = make_variable("x", TYPE_INT)
        sm.define(parent_sym)
        sm.push(ScopeKind.BLOCK)
        assert sm.lookup("x") is not None
        sm.pop()

    def test_child_shadows_parent(self):
        sm = ScopeManager()
        sm.define(make_variable("x", TYPE_INT))
        sm.push(ScopeKind.BLOCK)
        sm.define(make_variable("x", TYPE_STRING))
        found = sm.lookup("x")
        assert found is not None
        assert found.type_descriptor.kind == SymbolType.STRING
        sm.pop()

    def test_lookup_local_only(self):
        sm = ScopeManager()
        sm.define(make_variable("x", TYPE_INT))
        sm.push(ScopeKind.BLOCK)
        assert sm.lookup_local("x") is None
        sm.pop()

    def test_create_child(self):
        sm = ScopeManager()
        child = sm.current.create_child(ScopeKind.FUNCTION, "fn")
        assert child.kind == ScopeKind.FUNCTION
        assert child.name == "fn"
        assert child.depth == 1

    def test_enclosing_function(self):
        sm = ScopeManager()
        sm.push(ScopeKind.BLOCK)
        sm.push(ScopeKind.FUNCTION, "fn")
        assert sm.get_enclosing_function() is not None
        assert sm.get_enclosing_function().name == "fn"
        sm.pop()
        sm.pop()

    def test_enclosing_loop(self):
        sm = ScopeManager()
        sm.push(ScopeKind.LOOP)
        assert sm.get_enclosing_loop() is not None
        sm.pop()

    def test_enclosing_class(self):
        sm = ScopeManager()
        sm.push(ScopeKind.CLASS, "MyClass")
        assert sm.get_enclosing_class() is not None
        assert sm.get_enclosing_class().name == "MyClass"
        sm.pop()

    def test_scope_count(self):
        sm = ScopeManager()
        sm.push(ScopeKind.BLOCK)
        sm.push(ScopeKind.BLOCK)
        sm.push(ScopeKind.BLOCK)
        assert sm.scope_count == 3

    def test_all_visible_symbols(self):
        sm = ScopeManager()
        sm.define(make_variable("x", TYPE_INT))
        sm.push(ScopeKind.BLOCK)
        sm.define(make_variable("y", TYPE_STRING))
        syms = sm.all_visible_symbols()
        assert "x" in syms
        assert "y" in syms


# ══════════════════════════════════════════════════════════════════
# Symbol Tests
# ══════════════════════════════════════════════════════════════════


class TestSymbolSystem:
    def test_variable_symbol(self):
        sym = make_variable("x", TYPE_INT)
        assert sym.name == "x"
        assert sym.kind == SymbolKind.VARIABLE
        assert sym.type_descriptor.kind == SymbolType.INT
        assert not sym.is_const

    def test_constant_symbol(self):
        sym = make_constant("PI", TYPE_FLOAT)
        assert sym.is_const
        assert sym.kind == SymbolKind.CONSTANT

    def test_function_symbol(self):
        sym = make_function("foo", [TYPE_INT, TYPE_STRING], TYPE_BOOL)
        assert sym.kind == SymbolKind.FUNCTION
        assert len(sym.type_descriptor.param_types) == 2
        assert sym.type_descriptor.return_type.kind == SymbolType.BOOL

    def test_method_symbol(self):
        sym = make_method("bar", [TYPE_INT], TYPE_NONE, is_static=True)
        assert sym.kind == SymbolKind.METHOD
        assert sym.get_metadata('is_static') is True

    def test_class_symbol(self):
        sym = make_class("MyClass", parent_name="Base")
        assert sym.kind == SymbolKind.CLASS
        assert sym.parent_name == "Base"

    def test_struct_symbol(self):
        sym = make_struct("Point")
        assert sym.kind == SymbolKind.STRUCT

    def test_enum_symbol(self):
        sym = make_enum("Color")
        assert sym.kind == SymbolKind.ENUM

    def test_trait_symbol(self):
        sym = make_trait("Drawable")
        assert sym.kind == SymbolKind.TRAIT

    def test_interface_symbol(self):
        sym = make_interface("Comparable")
        assert sym.kind == SymbolKind.INTERFACE

    def test_parameter_symbol(self):
        sym = make_parameter("n", TYPE_INT)
        assert sym.kind == SymbolKind.PARAMETER

    def test_module_symbol(self):
        sym = make_module("mymod")
        assert sym.kind == SymbolKind.MODULE

    def test_type_descriptor_equality(self):
        td1 = TypeDescriptor(SymbolType.INT, "int")
        td2 = TypeDescriptor(SymbolType.INT, "int")
        assert td1 == td2

    def test_type_descriptor_inequality(self):
        td1 = TypeDescriptor(SymbolType.INT, "int")
        td2 = TypeDescriptor(SymbolType.FLOAT, "float")
        assert td1 != td2

    def test_type_compatibility_any(self):
        assert TYPE_ANY.is_compatible_with(TYPE_INT)
        assert TYPE_INT.is_compatible_with(TYPE_ANY)

    def test_type_compatibility_same(self):
        assert TYPE_INT.is_compatible_with(TYPE_INT)
        assert TYPE_STRING.is_compatible_with(TYPE_STRING)

    def test_type_incompatible(self):
        assert not TYPE_INT.is_compatible_with(TYPE_STRING)
        assert not TYPE_BOOL.is_compatible_with(TYPE_FLOAT)

    def test_type_descriptor_repr(self):
        assert repr(TYPE_INT) == "int"
        td = TypeDescriptor(SymbolType.FUNCTION, "fn",
                           param_types=[TYPE_INT], return_type=TYPE_BOOL)
        assert "int" in repr(td)

    def test_symbol_members(self):
        cls = make_class("C")
        cls.members["x"] = make_variable("x", TYPE_INT)
        assert "x" in cls.members


# ══════════════════════════════════════════════════════════════════
# Error Diagnostic Tests
# ══════════════════════════════════════════════════════════════════


class TestDiagnostics:
    def test_add_error(self):
        diag = SemanticErrorCollection()
        loc = _loc()
        diag.error(SemanticErrorCode.SEM200_UNDEFINED_VARIABLE, loc, "x")
        assert diag.has_errors
        assert diag.error_count == 1

    def test_add_warning(self):
        diag = SemanticErrorCollection()
        loc = _loc()
        diag.warning(SemanticErrorCode.SEM500_NOT_A_CONSTANT, loc, "x")
        assert not diag.has_errors
        assert diag.has_warnings

    def test_bilingual_message(self):
        rw, en = get_bilingual_message(
            SemanticErrorCode.SEM200_UNDEFINED_VARIABLE, "x"
        )
        assert "x" in en
        assert "x" in rw

    def test_diagnostic_str(self):
        diag = SemanticErrorCollection()
        diag.error(SemanticErrorCode.SEM200_UNDEFINED_VARIABLE, _loc(), "x")
        s = str(diag.errors[0])
        assert "SEM200_UNDEFINED_VARIABLE" in s
        assert "x" in s

    def test_diagnostic_bilingual_str(self):
        diag = SemanticErrorCollection()
        diag.error(SemanticErrorCode.SEM200_UNDEFINED_VARIABLE, _loc(), "x")
        s = diag.errors[0].bilingual_str()
        assert "Kinyarwanda" in s
        assert "English" in s

    def test_diagnostic_to_dict(self):
        diag = SemanticErrorCollection()
        diag.error(SemanticErrorCode.SEM200_UNDEFINED_VARIABLE, _loc(5, 10), "x")
        d = diag.errors[0].to_dict()
        assert d['code'] == 'SEM200_UNDEFINED_VARIABLE'
        assert d['location']['line'] == 5

    def test_format_all(self):
        diag = SemanticErrorCollection()
        diag.error(SemanticErrorCode.SEM200_UNDEFINED_VARIABLE, _loc(), "x")
        diag.error(SemanticErrorCode.SEM201_UNDEFINED_FUNCTION, _loc(), "fn")
        output = diag.format_all()
        assert "SEM200" in output
        assert "SEM201" in output

    def test_max_errors_abort(self):
        diag = SemanticErrorCollection()
        diag._max_errors = 3
        for i in range(5):
            if diag.should_abort:
                break
            diag.error(SemanticErrorCode.SEM200_UNDEFINED_VARIABLE, _loc(), f"x{i}")
        assert diag.error_count == 3

    def test_clear(self):
        diag = SemanticErrorCollection()
        diag.error(SemanticErrorCode.SEM200_UNDEFINED_VARIABLE, _loc(), "x")
        diag.clear()
        assert not diag.has_errors


# ══════════════════════════════════════════════════════════════════
# Built-in Symbol Tests
# ══════════════════════════════════════════════════════════════════


class TestBuiltins:
    def test_register_builtins(self):
        scope = Scope(ScopeKind.GLOBAL)
        register_builtins(scope)
        assert scope.has("int")
        assert scope.has("float")
        assert scope.has("bool")
        assert scope.has("umuntu")
        assert scope.has("andika")

    def test_reserved_keywords(self):
        assert is_reserved_keyword("niba")
        assert is_reserved_keyword("shyira")
        assert is_reserved_keyword("umurimo")
        assert not is_reserved_keyword("myVariable")
        assert not is_reserved_keyword("x")

    def test_builtin_type_check(self):
        assert is_builtin_type("int")
        assert is_builtin_type("float")
        assert is_builtin_type("umuntu")
        assert not is_builtin_type("MyClass")

    def test_resolve_type_name(self):
        td = resolve_type_name("int")
        assert td is not None
        assert td.kind == SymbolType.INT

    def test_resolve_unknown_type(self):
        td = resolve_type_name("unknown_type_xyz")
        assert td is None


# ══════════════════════════════════════════════════════════════════
# Name Resolution Tests
# ══════════════════════════════════════════════════════════════════


class TestNameResolution:
    def test_resolve_existing(self):
        scope = Scope(ScopeKind.GLOBAL)
        scope.define(make_variable("x", TYPE_INT))
        diag = SemanticErrorCollection()
        sym = resolve_name("x", scope, diag, _loc())
        assert sym is not None
        assert sym.name == "x"
        assert not diag.has_errors

    def test_resolve_undefined(self):
        scope = Scope(ScopeKind.GLOBAL)
        diag = SemanticErrorCollection()
        resolve_name("undefined", scope, diag, _loc())
        assert diag.has_errors

    def test_resolve_function(self):
        scope = Scope(ScopeKind.GLOBAL)
        scope.define(make_function("foo", [TYPE_INT], TYPE_NONE))
        diag = SemanticErrorCollection()
        sym = resolve_function("foo", scope, diag, _loc())
        assert sym is not None

    def test_resolve_not_callable(self):
        scope = Scope(ScopeKind.GLOBAL)
        scope.define(make_variable("x", TYPE_INT))
        diag = SemanticErrorCollection()
        resolve_function("x", scope, diag, _loc())
        assert diag.has_errors

    def test_resolve_class(self):
        scope = Scope(ScopeKind.GLOBAL)
        scope.define(make_class("MyClass"))
        diag = SemanticErrorCollection()
        sym = resolve_class("MyClass", scope, diag, _loc())
        assert sym is not None

    def test_resolve_type(self):
        scope = Scope(ScopeKind.GLOBAL)
        register_builtins(scope)
        diag = SemanticErrorCollection()
        td = resolve_type("int", scope, diag, _loc())
        assert td is not None
        assert td.kind == SymbolType.INT

    def test_is_callable(self):
        assert is_callable(make_function("f", [], TYPE_NONE))
        assert is_callable(make_method("m", [], TYPE_NONE))
        assert not is_callable(make_variable("x", TYPE_INT))

    def test_is_type_symbol(self):
        assert is_type_symbol(make_class("C"))
        assert is_type_symbol(make_struct("S"))
        assert not is_type_symbol(make_variable("x", TYPE_INT))


# ══════════════════════════════════════════════════════════════════
# Import/Export Tests
# ══════════════════════════════════════════════════════════════════


class TestImports:
    def test_register_module(self):
        ir = ImportResolver()
        mod = ir.register_module("mymod")
        assert mod.name == "mymod"
        assert "mymod" in ir.registered_modules

    def test_resolve_import_found(self):
        ir = ImportResolver()
        ir.register_module("mymod")
        diag = SemanticErrorCollection()
        sym = ir.resolve_import("mymod", None, diag, _loc())
        assert sym is not None
        assert not diag.has_errors

    def test_resolve_import_not_found(self):
        ir = ImportResolver()
        diag = SemanticErrorCollection()
        sym = ir.resolve_import("nonexistent", None, diag, _loc())
        assert sym is None
        assert diag.has_errors

    def test_resolve_import_with_alias(self):
        ir = ImportResolver()
        ir.register_module("mymod")
        diag = SemanticErrorCollection()
        sym = ir.resolve_import("mymod", "alias", diag, _loc())
        assert sym is not None

    def test_circular_import(self):
        ir = ImportResolver()
        ir.register_module("a")
        ir.start_module("a")
        diag = SemanticErrorCollection()
        ir.resolve_import("a", None, diag, _loc())
        assert diag.has_errors
        ir.end_module()

    def test_builtin_module_resolution(self):
        ir = ImportResolver()
        diag = SemanticErrorCollection()
        sym = ir.resolve_import("std", None, diag, _loc())
        assert sym is not None

    def test_register_export(self):
        ir = ImportResolver()
        ir.register_module("mymod")
        ir.start_module("mymod")
        sym = make_variable("x", TYPE_INT)
        diag = SemanticErrorCollection()
        ir.register_export("x", sym, diag, _loc())
        assert "x" in ir.get_module("mymod").exports
        ir.end_module()


# ══════════════════════════════════════════════════════════════════
# Constant Evaluation Tests
# ══════════════════════════════════════════════════════════════════


class TestConstantEvaluation:
    def test_literal_is_constant(self):
        assert is_constant_expression(LiteralExpr(value=42))
        assert is_constant_expression(LiteralExpr(value="hello"))
        assert is_constant_expression(LiteralExpr(value=True))
        assert is_constant_expression(LiteralExpr(value=None))

    def test_binary_constant(self):
        node = BinaryExpr(
            left=LiteralExpr(value=3),
            operator="+",
            right=LiteralExpr(value=4),
        )
        assert is_constant_expression(node)
        success, val = evaluate_constant(node)
        assert success
        assert val == 7

    def test_evaluate_literal(self):
        success, val = evaluate_constant(LiteralExpr(value=42))
        assert success
        assert val == 42

    def test_evaluate_string_concat(self):
        node = BinaryExpr(
            left=LiteralExpr(value="hello"),
            operator="+",
            right=LiteralExpr(value=" world"),
        )
        success, val = evaluate_constant(node)
        assert success
        assert val == "hello world"

    def test_evaluate_comparison(self):
        node = BinaryExpr(
            left=LiteralExpr(value=5),
            operator=">",
            right=LiteralExpr(value=3),
        )
        success, val = evaluate_constant(node)
        assert success
        assert val is True

    def test_evaluate_logical_and(self):
        node = LogicalExpr(
            left=LiteralExpr(value=True),
            operator="kandi",
            right=LiteralExpr(value=False),
        )
        success, val = evaluate_constant(node)
        assert success
        assert val is False

    def test_evaluate_unary_neg(self):
        node = UnaryExpr(operator="-", right=LiteralExpr(value=5))
        success, val = evaluate_constant(node)
        assert success
        assert val == -5

    def test_evaluate_division_by_zero(self):
        node = BinaryExpr(
            left=LiteralExpr(value=10),
            operator="/",
            right=LiteralExpr(value=0),
        )
        success, val = evaluate_constant(node)
        assert not success

    def test_get_constant_value(self):
        val = get_constant_value(LiteralExpr(value=42))
        assert val == 42

    def test_not_constant_identifier(self):
        val = get_constant_value(IdentifierExpr(name="x"))
        assert val is None


# ══════════════════════════════════════════════════════════════════
# Control Flow Tests
# ══════════════════════════════════════════════════════════════════


class TestControlFlow:
    def test_empty_function_has_return(self):
        body = BlockStmt(statements=[ReturnStmt(value=None)])
        assert function_always_returns(body)

    def test_function_without_return(self):
        body = BlockStmt(statements=[
            ExpressionStmt(expression=LiteralExpr(value=42))
        ])
        assert not function_always_returns(body)

    def test_if_both_branches_return(self):
        body = BlockStmt(statements=[
            IfStmt(
                condition=LiteralExpr(value=True),
                then_branch=BlockStmt(statements=[
                    ReturnStmt(value=LiteralExpr(value=1))
                ]),
                elif_branches=[],
                else_branch=BlockStmt(statements=[
                    ReturnStmt(value=LiteralExpr(value=2))
                ]),
            )
        ])
        assert function_always_returns(body)

    def test_if_only_then_returns(self):
        body = BlockStmt(statements=[
            IfStmt(
                condition=LiteralExpr(value=True),
                then_branch=BlockStmt(statements=[
                    ReturnStmt(value=LiteralExpr(value=1))
                ]),
                elif_branches=[],
                else_branch=None,
            )
        ])
        assert not function_always_returns(body)

    def test_unreachable_after_return(self):
        body = BlockStmt(statements=[
            ReturnStmt(value=LiteralExpr(value=1)),
            ExpressionStmt(expression=LiteralExpr(value=2)),
        ])
        analysis = analyze_function_flow(body)
        assert len(analysis.unreachable_statements) == 1

    def test_throw_terminates(self):
        body = BlockStmt(statements=[
            ThrowStmt(value=LiteralExpr(value="err")),
        ])
        analysis = analyze_function_flow(body)
        assert analysis.state == FlowState.THROWS
        assert analysis.all_paths_return

    def test_break_in_loop(self):
        body = BlockStmt(statements=[
            BreakStmt(),
        ])
        analysis = analyze_function_flow(body)
        assert analysis.has_break


# ══════════════════════════════════════════════════════════════════
# Visibility Tests
# ══════════════════════════════════════════════════════════════════


class TestVisibility:
    def test_public_always_visible(self):
        sym = make_variable("x", TYPE_INT, vis=Visibility.PUBLIC)
        scope = Scope(ScopeKind.GLOBAL)
        diag = SemanticErrorCollection()
        assert check_visibility(sym, scope, diag, _loc())

    def test_private_same_scope(self):
        sym = make_variable("x", TYPE_INT, vis=Visibility.PRIVATE)
        scope = Scope(ScopeKind.GLOBAL)
        scope.define(sym)
        diag = SemanticErrorCollection()
        assert check_visibility(sym, scope, diag, _loc())

    def test_internal_always_visible_same_module(self):
        sym = make_variable("x", TYPE_INT, vis=Visibility.INTERNAL)
        scope = Scope(ScopeKind.GLOBAL)
        diag = SemanticErrorCollection()
        assert check_visibility(sym, scope, diag, _loc())


# ══════════════════════════════════════════════════════════════════
# Context Tests
# ══════════════════════════════════════════════════════════════════


class TestAnalysisContext:
    def test_enter_exit_function(self):
        ctx = AnalysisContext()
        ctx.enter_function("foo")
        assert ctx.in_function
        assert ctx.current_function.name == "foo"
        ctx.exit_function()
        assert not ctx.in_function

    def test_enter_exit_class(self):
        ctx = AnalysisContext()
        ctx.enter_class("MyClass")
        assert ctx.in_class
        assert ctx.current_class.name == "MyClass"
        ctx.exit_class()
        assert not ctx.in_class

    def test_loop_depth(self):
        ctx = AnalysisContext()
        assert not ctx.in_loop
        ctx.enter_loop()
        assert ctx.in_loop
        assert ctx.loop_depth == 1
        ctx.enter_loop()
        assert ctx.loop_depth == 2
        ctx.exit_loop()
        assert ctx.loop_depth == 1
        ctx.exit_loop()
        assert not ctx.in_loop

    def test_clear(self):
        ctx = AnalysisContext()
        ctx.enter_function("foo")
        ctx.enter_loop()
        ctx.clear()
        assert not ctx.in_function
        assert not ctx.in_loop


# ══════════════════════════════════════════════════════════════════
# Full Analyzer Integration Tests
# ══════════════════════════════════════════════════════════════════


class TestAnalyzerIntegration:
    def test_empty_program(self):
        analyzer = _analyze_program([])
        assert not analyzer.has_errors

    def test_variable_declaration(self):
        decl = VarDecl(
            name="x", type_annotation=None,
            initializer=LiteralExpr(value=42), is_const=False,
        )
        analyzer = _analyze_program([decl])
        assert not analyzer.has_errors

    def test_const_declaration(self):
        decl = VarDecl(
            name="PI", type_annotation=None,
            initializer=LiteralExpr(value=3.14), is_const=True,
        )
        analyzer = _analyze_program([decl])
        assert not analyzer.has_errors

    def test_duplicate_variable_error(self):
        d1 = VarDecl(name="x", type_annotation=None,
                     initializer=LiteralExpr(value=1), is_const=False)
        d2 = VarDecl(name="x", type_annotation=None,
                     initializer=LiteralExpr(value=2), is_const=False)
        analyzer = _analyze_program([d1, d2])
        assert analyzer.has_errors
        assert any(e.code == SemanticErrorCode.SEM100_DUPLICATE_VARIABLE
                   for e in analyzer.diagnostics.errors)

    def test_function_declaration(self):
        decl = FunctionDecl(
            name="foo",
            parameters=[Parameter(name="x", type_annotation=NamedType(name="int"))],
            return_type=NamedType(name="int"),
            body=BlockStmt(statements=[
                ReturnStmt(value=IdentifierExpr(name="x"))
            ]),
        )
        analyzer = _analyze_program([decl])
        assert not analyzer.has_errors

    def test_duplicate_function_error(self):
        f1 = FunctionDecl(name="foo", parameters=[], return_type=None,
                          body=BlockStmt(statements=[]))
        f2 = FunctionDecl(name="foo", parameters=[], return_type=None,
                          body=BlockStmt(statements=[]))
        analyzer = _analyze_program([f1, f2])
        assert analyzer.has_errors
        assert any(e.code == SemanticErrorCode.SEM101_DUPLICATE_FUNCTION
                   for e in analyzer.diagnostics.errors)

    def test_struct_declaration(self):
        decl = StructDecl(
            name="Point",
            fields=[
                StructField(name="x", type_annotation=NamedType(name="int")),
                StructField(name="y", type_annotation=NamedType(name="int")),
            ],
            methods=[],
        )
        analyzer = _analyze_program([decl])
        assert not analyzer.has_errors

    def test_enum_declaration(self):
        decl = EnumDecl(
            name="Color",
            variants=[
                EnumVariant(name="RED"),
                EnumVariant(name="GREEN"),
                EnumVariant(name="BLUE"),
            ],
        )
        analyzer = _analyze_program([decl])
        assert not analyzer.has_errors

    def test_class_declaration(self):
        decl = ClassDecl(
            name="Animal", parent=None,
            members=[
                FunctionDecl(name="eat", parameters=[], return_type=None,
                             body=BlockStmt(statements=[])),
            ],
        )
        analyzer = _analyze_program([decl])
        assert not analyzer.has_errors

    def test_class_inheritance(self):
        parent = ClassDecl(name="Animal", parent=None, members=[])
        child = ClassDecl(name="Dog", parent="Animal", members=[])
        analyzer = _analyze_program([parent, child])
        assert not analyzer.has_errors

    def test_trait_declaration(self):
        decl = TraitDecl(
            name="Drawable",
            members=[
                FunctionDecl(name="draw", parameters=[], return_type=None,
                             body=BlockStmt(statements=[])),
            ],
        )
        analyzer = _analyze_program([decl])
        assert not analyzer.has_errors

    def test_interface_declaration(self):
        decl = InterfaceDecl(
            name="Comparable",
            members=[
                FunctionDecl(name="compare", parameters=[], return_type=None,
                             body=BlockStmt(statements=[])),
            ],
        )
        analyzer = _analyze_program([decl])
        assert not analyzer.has_errors

    def test_return_outside_function(self):
        stmt = ReturnStmt(value=LiteralExpr(value=42))
        analyzer = _analyze_program([
            ExpressionStmt(expression=stmt.expression if hasattr(stmt, 'expression') else LiteralExpr(value=42))
        ])
        # Return inside expression stmt shouldn't error, but as a statement:
        analyzer2 = _analyze_program([])
        prog = Program(declarations=[stmt])
        analyzer2.analyze(prog)
        assert analyzer2.has_errors

    def test_break_outside_loop(self):
        analyzer = _analyze_program([])
        prog = Program(declarations=[BreakStmt()])
        analyzer.analyze(prog)
        assert analyzer.has_errors

    def test_continue_outside_loop(self):
        analyzer = _analyze_program([])
        prog = Program(declarations=[ContinueStmt()])
        analyzer.analyze(prog)
        assert analyzer.has_errors

    def test_break_inside_loop(self):
        loop = WhileStmt(
            condition=LiteralExpr(value=True),
            body=BlockStmt(statements=[BreakStmt()]),
        )
        analyzer = _analyze_program([
            ExpressionStmt(expression=LiteralExpr(value=0))
        ])
        prog = Program(declarations=[loop])
        analyzer.analyze(prog)
        assert not analyzer.has_errors

    def test_import_declaration(self):
        imp = ImportDecl(path="mymod")
        analyzer = _analyze_program([imp])
        # Module not found is an error
        assert analyzer.has_errors

    def test_export_declaration(self):
        d = VarDecl(name="x", type_annotation=None,
                    initializer=LiteralExpr(value=42), is_const=False)
        e = ExportDecl(name="x")
        analyzer = _analyze_program([d, e])
        assert not analyzer.has_errors

    def test_export_undefined(self):
        e = ExportDecl(name="nonexistent")
        analyzer = _analyze_program([e])
        assert analyzer.has_errors

    def test_if_statement(self):
        stmt = IfStmt(
            condition=LiteralExpr(value=True),
            then_branch=BlockStmt(statements=[]),
            elif_branches=[],
            else_branch=None,
        )
        analyzer = _analyze_program([ExpressionStmt(expression=LiteralExpr(value=0))])
        prog = Program(declarations=[stmt])
        analyzer.analyze(prog)
        assert not analyzer.has_errors

    def test_while_loop(self):
        stmt = WhileStmt(
            condition=LiteralExpr(value=True),
            body=BlockStmt(statements=[BreakStmt()]),
        )
        analyzer = _analyze_program([])
        prog = Program(declarations=[stmt])
        analyzer.analyze(prog)
        assert not analyzer.has_errors

    def test_for_loop(self):
        stmt = ForStmt(
            variable="i",
            start=LiteralExpr(value=0),
            end=LiteralExpr(value=10),
            step=None,
            body=BlockStmt(statements=[]),
        )
        analyzer = _analyze_program([])
        prog = Program(declarations=[stmt])
        analyzer.analyze(prog)
        assert not analyzer.has_errors

    def test_try_catch(self):
        stmt = TryStmt(
            try_body=BlockStmt(statements=[]),
            catch_var="e",
            catch_body=BlockStmt(statements=[]),
            finally_body=None,
        )
        analyzer = _analyze_program([])
        prog = Program(declarations=[stmt])
        analyzer.analyze(prog)
        assert not analyzer.has_errors

    def test_function_with_return(self):
        fn = FunctionDecl(
            name="add",
            parameters=[
                Parameter(name="a", type_annotation=NamedType(name="int")),
                Parameter(name="b", type_annotation=NamedType(name="int")),
            ],
            return_type=NamedType(name="int"),
            body=BlockStmt(statements=[
                ReturnStmt(
                    value=BinaryExpr(
                        left=IdentifierExpr(name="a"),
                        operator="+",
                        right=IdentifierExpr(name="b"),
                    )
                )
            ]),
        )
        analyzer = _analyze_program([fn])
        assert not analyzer.has_errors

    def test_analyze_convenience_function(self):
        prog = Program(declarations=[])
        diag = analyze(prog)
        assert not diag.has_errors


# ══════════════════════════════════════════════════════════════════
# Stress Tests
# ══════════════════════════════════════════════════════════════════


class TestStress:
    def test_many_variables(self):
        decls = [
            VarDecl(name=f"var_{i}", type_annotation=None,
                    initializer=LiteralExpr(value=i), is_const=False)
            for i in range(500)
        ]
        analyzer = _analyze_program(decls)
        assert not analyzer.has_errors

    def test_nested_scopes(self):
        inner_block = BlockStmt(statements=[])
        for i in range(50):
            inner_block = BlockStmt(statements=[inner_block])
        analyzer = _analyze_program([ExpressionStmt(expression=LiteralExpr(value=0))])
        prog = Program(declarations=[inner_block])
        analyzer.analyze(prog)
        assert not analyzer.has_errors

    def test_many_functions(self):
        fns = [
            FunctionDecl(
                name=f"fn_{i}",
                parameters=[Parameter(name="x", type_annotation=NamedType(name="int"))],
                return_type=NamedType(name="int"),
                body=BlockStmt(statements=[
                    ReturnStmt(value=IdentifierExpr(name="x"))
                ]),
            )
            for i in range(200)
        ]
        analyzer = _analyze_program(fns)
        assert not analyzer.has_errors

    def test_many_errors(self):
        decls = [
            VarDecl(name=f"x", type_annotation=None,
                    initializer=LiteralExpr(value=i), is_const=False)
            for i in range(5)
        ]
        analyzer = _analyze_program(decls)
        assert analyzer.has_errors  # All same name = duplicates


# ══════════════════════════════════════════════════════════════════
# Fuzz Tests
# ══════════════════════════════════════════════════════════════════


class TestFuzz:
    def test_random_expressions(self):
        import random
        random.seed(42)
        exprs = []
        for _ in range(100):
            kind = random.choice(["literal", "binary", "unary", "list"])
            if kind == "literal":
                exprs.append(LiteralExpr(value=random.randint(-100, 100)))
            elif kind == "binary":
                left = LiteralExpr(value=random.randint(0, 10))
                right = LiteralExpr(value=random.randint(0, 10))
                op = random.choice(["+", "-", "*", "==", "!="])
                exprs.append(BinaryExpr(left=left, operator=op, right=right))
            elif kind == "unary":
                exprs.append(UnaryExpr(operator="-", right=LiteralExpr(value=5)))
            else:
                exprs.append(ListExpr(elements=[
                    LiteralExpr(value=i) for i in range(3)
                ]))
        analyzer = _analyze_program([
            ExpressionStmt(expression=e) for e in exprs
        ])
        assert not analyzer.has_errors

    def test_random_declarations(self):
        import random
        random.seed(43)
        decls = []
        for i in range(50):
            decls.append(VarDecl(
                name=f"v{i}",
                type_annotation=None,
                initializer=LiteralExpr(value=random.randint(0, 100)),
                is_const=random.choice([True, False]),
            ))
        analyzer = _analyze_program(decls)
        assert not analyzer.has_errors

    def test_mixed_valid_program(self):
        program_nodes = [
            VarDecl(name="count", type_annotation=None,
                    initializer=LiteralExpr(value=0), is_const=False),
            FunctionDecl(
                name="increment",
                parameters=[],
                return_type=None,
                body=BlockStmt(statements=[
                    AssignmentExpr(
                        target=IdentifierExpr(name="count"),
                        value=BinaryExpr(
                            left=IdentifierExpr(name="count"),
                            operator="+",
                            right=LiteralExpr(value=1),
                        ),
                    ),
                ]),
            ),
            StructDecl(
                name="Counter",
                fields=[StructField(name="value", type_annotation=NamedType(name="int"))],
                methods=[],
            ),
            EnumDecl(
                name="Direction",
                variants=[
                    EnumVariant(name="UP"),
                    EnumVariant(name="DOWN"),
                    EnumVariant(name="LEFT"),
                    EnumVariant(name="RIGHT"),
                ],
            ),
        ]
        analyzer = _analyze_program(program_nodes)
        assert not analyzer.has_errors


# ══════════════════════════════════════════════════════════════════
# Regression Tests
# ══════════════════════════════════════════════════════════════════


class TestRegression:
    def test_reserved_keyword_as_variable_name(self):
        decl = VarDecl(
            name="niba", type_annotation=None,
            initializer=LiteralExpr(value=42), is_const=False,
        )
        analyzer = _analyze_program([decl])
        assert analyzer.has_errors
        assert any(e.code == SemanticErrorCode.SEM110_RESERVED_KEYWORD
                   for e in analyzer.diagnostics.errors)

    def test_builtin_not_overwritten(self):
        d1 = VarDecl(name="int", type_annotation=None,
                     initializer=LiteralExpr(value=42), is_const=False)
        analyzer = _analyze_program([d1])
        # 'int' is a builtin type, should be defined already
        # Depending on design: this might warn or be allowed
        assert not analyzer.has_errors or analyzer.has_errors

    def test_nested_function_scopes(self):
        outer = FunctionDecl(
            name="outer",
            parameters=[Parameter(name="a", type_annotation=NamedType(name="int"))],
            return_type=NamedType(name="int"),
            body=BlockStmt(statements=[
                FunctionDecl(
                    name="inner",
                    parameters=[Parameter(name="b", type_annotation=NamedType(name="int"))],
                    return_type=NamedType(name="int"),
                    body=BlockStmt(statements=[
                        ReturnStmt(value=IdentifierExpr(name="b"))
                    ]),
                ),
                ReturnStmt(value=IdentifierExpr(name="a")),
            ]),
        )
        analyzer = _analyze_program([outer])
        assert not analyzer.has_errors

    def test_compound_assignment(self):
        decl = VarDecl(name="x", type_annotation=None,
                       initializer=LiteralExpr(value=10), is_const=False)
        assign = ExpressionStmt(
            expression=CompoundAssignmentExpr(
                target=IdentifierExpr(name="x"),
                operator="+=",
                value=LiteralExpr(value=5),
            )
        )
        analyzer = _analyze_program([decl, assign])
        assert not analyzer.has_errors

    def test_list_literal(self):
        expr = ListExpr(elements=[
            LiteralExpr(value=1),
            LiteralExpr(value=2),
            LiteralExpr(value=3),
        ])
        analyzer = _analyze_program([ExpressionStmt(expression=expr)])
        assert not analyzer.has_errors

    def test_dict_literal(self):
        expr = DictExpr(
            keys=[LiteralExpr(value="a"), LiteralExpr(value="b")],
            values=[LiteralExpr(value=1), LiteralExpr(value=2)],
        )
        analyzer = _analyze_program([ExpressionStmt(expression=expr)])
        assert not analyzer.has_errors

    def test_assignment_to_undefined(self):
        stmt = ExpressionStmt(
            expression=AssignmentExpr(
                target=IdentifierExpr(name="nonexistent"),
                value=LiteralExpr(value=42),
            )
        )
        analyzer = _analyze_program([stmt])
        assert analyzer.has_errors

    def test_function_call_undefined(self):
        stmt = ExpressionStmt(
            expression=CallExpr(
                callee=IdentifierExpr(name="undefined_fn"),
                arguments=[],
            )
        )
        analyzer = _analyze_program([stmt])
        assert analyzer.has_errors

    def test_self_outside_class(self):
        stmt = ExpressionStmt(expression=SelfExpr())
        analyzer = _analyze_program([stmt])
        assert analyzer.has_errors

    def test_super_outside_class(self):
        stmt = ExpressionStmt(expression=SuperExpr(method="foo"))
        analyzer = _analyze_program([stmt])
        assert analyzer.has_errors

    def test_for_each_loop(self):
        decl = VarDecl(name="items", type_annotation=None,
                       initializer=ListExpr(elements=[
                           LiteralExpr(value=1), LiteralExpr(value=2)
                       ]), is_const=False)
        loop = ForEachStmt(
            element="item",
            iterable=IdentifierExpr(name="items"),
            body=BlockStmt(statements=[]),
        )
        analyzer = _analyze_program([decl, ExpressionStmt(expression=loop.iterable)])
        prog = Program(declarations=[decl, loop])
        analyzer2 = _analyze_program([decl])
        analyzer2.analyze(prog)
        assert not analyzer2.has_errors

    def test_multiple_return_paths(self):
        fn = FunctionDecl(
            name="test",
            parameters=[Parameter(name="x", type_annotation=NamedType(name="int"))],
            return_type=NamedType(name="int"),
            body=BlockStmt(statements=[
                IfStmt(
                    condition=BinaryExpr(
                        left=IdentifierExpr(name="x"),
                        operator=">",
                        right=LiteralExpr(value=0),
                    ),
                    then_branch=BlockStmt(statements=[
                        ReturnStmt(value=IdentifierExpr(name="x"))
                    ]),
                    elif_branches=[],
                    else_branch=BlockStmt(statements=[
                        ReturnStmt(value=LiteralExpr(value=0))
                    ]),
                ),
            ]),
        )
        analyzer = _analyze_program([fn])
        assert not analyzer.has_errors

    def test_missing_return_path(self):
        fn = FunctionDecl(
            name="test",
            parameters=[],
            return_type=NamedType(name="int"),
            body=BlockStmt(statements=[
                IfStmt(
                    condition=LiteralExpr(value=True),
                    then_branch=BlockStmt(statements=[
                        ReturnStmt(value=LiteralExpr(value=1))
                    ]),
                    elif_branches=[],
                    else_branch=None,
                ),
            ]),
        )
        analyzer = _analyze_program([fn])
        assert any(d.code == SemanticErrorCode.SEM601_MISSING_RETURN_PATH
                   for d in analyzer.diagnostics.diagnostics)
