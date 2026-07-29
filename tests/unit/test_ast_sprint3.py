"""
Comprehensive AST Sprint 3 Tests for the I Programming Language

Covers: new nodes (Module, MethodDecl, MethodCallExpr, PlaceholderExpr),
ASTRewriter, ASTInspector, source span validation, binary serialization,
versioned serialization, stress tests, Unicode tests, golden snapshots.
"""

import json
import os
import sys
import time
import unittest
from typing import List

from compiler.ast.nodes import (
    AssignmentExpr,
    BinaryExpr,
    BlockStmt,
    BreakStmt,
    CallExpr,
    ClassDecl,
    CompoundAssignmentExpr,
    ConstructorExpr,
    ContinueStmt,
    DictExpr,
    ElifBranch,
    EmptyStmt,
    EnumDecl,
    EnumVariant,
    Expr,
    ExportDecl,
    ExpressionStmt,
    ForEachStmt,
    ForStmt,
    FunctionDecl,
    FunctionType,
    GetExpr,
    GenericType,
    GroupingExpr,
    IfExpr,
    IfStmt,
    IdentifierExpr,
    ImportDecl,
    IndexExpr,
    InterfaceDecl,
    LambdaExpr,
    ListExpr,
    LiteralExpr,
    LogicalExpr,
    MethodCallExpr,
    MethodDecl,
    Module,
    NamedType,
    NodeType,
    OptionalType,
    Parameter,
    PlaceholderExpr,
    Program,
    ReturnStmt,
    SelfExpr,
    SetExpr,
    SliceExpr,
    SourceLocation,
    StructDecl,
    StructField,
    SuperExpr,
    ThrowStmt,
    TraitDecl,
    TryStmt,
    TupleExpr,
    TupleType,
    TypeNode,
    UnaryExpr,
    UntilStmt,
    VarDecl,
    WhileStmt,
)
from compiler.ast.nodes import ASTNode, ASTVisitor, Decl, Stmt
from compiler.ast.visitor import (
    ASTWalker,
    ASTTransformer,
    ASTRewriter,
    ASTInspector,
    PrettyPrinter,
    DebugPrinter,
)
from compiler.ast.validator import validate_ast, ValidationError, ValidationResult
from compiler.ast.serializer import (
    ASTSerializer,
    ASTDeserializer,
    ASTBinarySerializer,
    ASTVersionedSerializer,
)
from compiler.ast.visualizer import TextTreeVisualizer, DOTVisualizer


# ══════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════


def loc(line: int = 1, col: int = 1, file: str = "test.i") -> SourceLocation:
    return SourceLocation(file, line, col, line, col + 5)


def loc_range(sl: int = 1, sc: int = 1, el: int = 1, ec: int = 10,
              file: str = "test.i") -> SourceLocation:
    return SourceLocation(file, sl, sc, el, ec)


def loc_bad(line: int = -1, col: int = -1) -> SourceLocation:
    """Create an invalid source location for testing."""
    return SourceLocation("bad.i", line, col, line, col)


def int_lit(value: int = 42) -> LiteralExpr:
    return LiteralExpr(value=value, location=loc())


def str_lit(value: str = "hello") -> LiteralExpr:
    return LiteralExpr(value=value, location=loc())


def ident(name: str = "x") -> IdentifierExpr:
    return IdentifierExpr(name=name, location=loc())


def block(stmts: List = None) -> BlockStmt:
    return BlockStmt(statements=stmts or [], location=loc())


def empty_block() -> BlockStmt:
    return BlockStmt(statements=[], location=loc())


def param(name: str = "x", type_name: str = None,
          default: Expr = None) -> Parameter:
    type_ann = NamedType(name=type_name) if type_name else None
    return Parameter(name=name, type_annotation=type_ann, default=default,
                     location=loc())


def func_decl(name: str = "f", params=None, ret: str = None,
              stmts: List = None) -> FunctionDecl:
    params = params or []
    ret_type = NamedType(name=ret) if ret else None
    body = BlockStmt(statements=stmts or [], location=loc())
    return FunctionDecl(name=name, parameters=params, return_type=ret_type,
                        body=body, location=loc())


# ══════════════════════════════════════════════════════════════════
# Test: New Node Types in NodeType Enum
# ══════════════════════════════════════════════════════════════════


class TestNewNodeTypes(unittest.TestCase):
    def test_module_exists(self):
        self.assertEqual(NodeType.MODULE.name, "MODULE")

    def test_method_decl_exists(self):
        self.assertEqual(NodeType.METHOD_DECL.name, "METHOD_DECL")

    def test_method_call_expr_exists(self):
        self.assertEqual(NodeType.METHOD_CALL_EXPR.name, "METHOD_CALL_EXPR")

    def test_placeholder_expr_exists(self):
        self.assertEqual(NodeType.PLACEHOLDER_EXPR.name, "PLACEHOLDER_EXPR")


# ══════════════════════════════════════════════════════════════════
# Test: Module Node
# ══════════════════════════════════════════════════════════════════


class TestModuleNode(unittest.TestCase):
    def test_empty_module(self):
        m = Module(name="main", declarations=[], imports=[], location=loc())
        self.assertEqual(m.node_type, NodeType.MODULE)
        self.assertEqual(m.name, "main")
        self.assertEqual(m.children(), [])

    def test_module_with_imports_and_decls(self):
        imp = ImportDecl(path="math", location=loc())
        decl = VarDecl(name="x", type_annotation=None,
                       initializer=LiteralExpr(1))
        m = Module(name="my_mod", declarations=[decl], imports=[imp],
                   location=loc())
        self.assertEqual(len(m.children()), 2)

    def test_module_accepts_visitor(self):
        m = Module(name="m", declarations=[], imports=[], location=loc())
        printer = PrettyPrinter()
        output = printer.print(m)
        self.assertIn("Module(m)", output)


# ══════════════════════════════════════════════════════════════════
# Test: MethodDecl Node
# ══════════════════════════════════════════════════════════════════


class TestMethodDeclNode(unittest.TestCase):
    def test_basic_method(self):
        m = MethodDecl(name="do_thing", parameters=[], return_type=None,
                       body=empty_block(), location=loc())
        self.assertEqual(m.node_type, NodeType.METHOD_DECL)
        self.assertEqual(m.name, "do_thing")
        self.assertFalse(m.is_static)

    def test_static_method(self):
        m = MethodDecl(name="create", parameters=[], return_type=None,
                       body=empty_block(), is_static=True, location=loc())
        self.assertTrue(m.is_static)

    def test_method_with_params(self):
        m = MethodDecl(name="add", parameters=[param("a"), param("b")],
                       return_type=NamedType(name="int"),
                       body=empty_block(), location=loc())
        self.assertEqual(len(m.children()), 4)  # 2 params + ret type + body

    def test_method_printer(self):
        m = MethodDecl(name="foo", parameters=[], return_type=None,
                       body=empty_block(), location=loc())
        printer = PrettyPrinter()
        output = printer.print(m)
        self.assertIn("Method(foo)", output)

    def test_static_method_printer(self):
        m = MethodDecl(name="bar", parameters=[], return_type=None,
                       body=empty_block(), is_static=True, location=loc())
        printer = PrettyPrinter()
        output = printer.print(m)
        self.assertIn("StaticMethod(bar)", output)


# ══════════════════════════════════════════════════════════════════
# Test: MethodCallExpr Node
# ══════════════════════════════════════════════════════════════════


class TestMethodCallExprNode(unittest.TestCase):
    def test_basic_method_call(self):
        obj = ident("self")
        m = MethodCallExpr(object=obj, method="do_thing", arguments=[],
                           location=loc())
        self.assertEqual(m.node_type, NodeType.METHOD_CALL_EXPR)
        self.assertEqual(m.method, "do_thing")
        self.assertEqual(m.children(), [obj])

    def test_method_call_with_args(self):
        obj = ident("self")
        args = [int_lit(1), str_lit("hi")]
        m = MethodCallExpr(object=obj, method="send", arguments=args,
                           location=loc())
        self.assertEqual(len(m.children()), 3)  # obj + 2 args

    def test_method_call_is_not_lvalue(self):
        m = MethodCallExpr(object=ident("x"), method="foo", arguments=[])
        self.assertFalse(m.is_lvalue)

    def test_method_call_printer(self):
        m = MethodCallExpr(object=ident("obj"), method="greet",
                           arguments=[], location=loc())
        printer = PrettyPrinter()
        output = printer.print(m)
        self.assertIn("MethodCall(greet)", output)


# ══════════════════════════════════════════════════════════════════
# Test: PlaceholderExpr Node
# ══════════════════════════════════════════════════════════════════


class TestPlaceholderExprNode(unittest.TestCase):
    def test_empty_placeholder(self):
        p = PlaceholderExpr(location=loc())
        self.assertEqual(p.node_type, NodeType.PLACEHOLDER_EXPR)
        self.assertEqual(p.description, "")
        self.assertEqual(p.children(), [])
        self.assertFalse(p.is_lvalue)

    def test_placeholder_with_desc(self):
        p = PlaceholderExpr(description="TODO: implement await", location=loc())
        self.assertEqual(p.description, "TODO: implement await")

    def test_placeholder_printer(self):
        p = PlaceholderExpr(description="future", location=loc())
        printer = PrettyPrinter()
        output = printer.print(p)
        self.assertIn("Placeholder(future)", output)

    def test_placeholder_debug_printer(self):
        p = PlaceholderExpr(description="test", location=loc())
        printer = DebugPrinter()
        output = printer.print(p)
        self.assertIn("Placeholder(test)", output)


# ══════════════════════════════════════════════════════════════════
# Test: ASTRewriter
# ══════════════════════════════════════════════════════════════════


class TestASTRewriter(unittest.TestCase):
    def test_identity_rewrite(self):
        rewriter = ASTRewriter()
        expr = BinaryExpr(int_lit(1), "+", int_lit(2))
        result = rewriter.rewrite(expr)
        self.assertIsInstance(result, BinaryExpr)
        self.assertEqual(result.left.value, 1)

    def test_literal_replacement(self):
        rewriter = ASTRewriter()
        rewriter.register(LiteralExpr, lambda e: LiteralExpr(
            value=e.value * 3, location=e.location))
        expr = BinaryExpr(int_lit(2), "+", int_lit(5))
        result = rewriter.rewrite(expr)
        self.assertIsInstance(result, BinaryExpr)
        self.assertEqual(result.left.value, 6)
        self.assertEqual(result.right.value, 15)

    def test_nested_rewrite(self):
        rewriter = ASTRewriter()
        rewriter.register(IdentifierExpr, lambda e: IdentifierExpr(
            name="renamed", location=e.location))
        inner = IdentifierExpr(name="old")
        expr = BinaryExpr(inner, "+", int_lit(1))
        result = rewriter.rewrite(expr)
        self.assertEqual(result.left.name, "renamed")

    def test_rewrite_var_decl(self):
        rewriter = ASTRewriter()
        rewriter.register(LiteralExpr, lambda e: LiteralExpr(
            value=999, location=e.location))
        decl = VarDecl(name="x", type_annotation=None,
                       initializer=LiteralExpr(42))
        result = rewriter.rewrite(decl)
        self.assertIsInstance(result, VarDecl)
        self.assertEqual(result.initializer.value, 999)

    def test_rewrite_program(self):
        rewriter = ASTRewriter()
        rewriter.register(LiteralExpr, lambda e: LiteralExpr(
            value=e.value + 1, location=e.location))
        p = Program(declarations=[
            VarDecl(name="a", type_annotation=None, initializer=LiteralExpr(10)),
            VarDecl(name="b", type_annotation=None, initializer=LiteralExpr(20)),
        ])
        result = rewriter.rewrite(p)
        self.assertIsInstance(result, Program)
        self.assertEqual(result.declarations[0].initializer.value, 11)
        self.assertEqual(result.declarations[1].initializer.value, 21)

    def test_rewrite_method_decl(self):
        rewriter = ASTRewriter()
        rewriter.register(LiteralExpr, lambda e: LiteralExpr(
            value=0, location=e.location))
        md = MethodDecl(name="m", parameters=[], return_type=None,
                        body=BlockStmt(statements=[
                            ExpressionStmt(expression=LiteralExpr(42))
                        ]))
        result = rewriter.rewrite(md)
        self.assertIsInstance(result, MethodDecl)
        self.assertEqual(
            result.body.statements[0].expression.value, 0)

    def test_rewrite_module(self):
        rewriter = ASTRewriter()
        m = Module(name="test", declarations=[], imports=[], location=loc())
        result = rewriter.rewrite(m)
        self.assertIsInstance(result, Module)
        self.assertEqual(result.name, "test")


# ══════════════════════════════════════════════════════════════════
# Test: ASTInspector
# ══════════════════════════════════════════════════════════════════


class TestASTInspector(unittest.TestCase):
    def test_inspect_empty(self):
        inspector = ASTInspector()
        p = Program(declarations=[])
        stats = inspector.inspect(p)
        self.assertEqual(stats["total_nodes"], 1)
        self.assertEqual(stats["max_depth"], 1)

    def test_inspect_literal(self):
        inspector = ASTInspector()
        stats = inspector.inspect(int_lit(42))
        self.assertEqual(stats["total_nodes"], 1)
        self.assertEqual(stats["expressions"], 1)
        self.assertEqual(stats["leaf_nodes"], 1)

    def test_inspect_binary(self):
        inspector = ASTInspector()
        expr = BinaryExpr(int_lit(1), "+", int_lit(2))
        stats = inspector.inspect(expr)
        self.assertEqual(stats["total_nodes"], 3)
        self.assertEqual(stats["max_children"], 2)
        self.assertEqual(stats["leaf_nodes"], 2)

    def test_inspect_function_names(self):
        inspector = ASTInspector()
        p = Program(declarations=[
            func_decl("add"), func_decl("sub"), func_decl("mul")
        ])
        stats = inspector.inspect(p)
        self.assertEqual(stats["function_names"], ["add", "sub", "mul"])

    def test_inspect_method_names(self):
        inspector = ASTInspector()
        md = MethodDecl(name="greet", parameters=[], return_type=None,
                        body=empty_block())
        p = Program(declarations=[md])
        stats = inspector.inspect(p)
        self.assertEqual(stats["method_names"], ["greet"])

    def test_inspect_class_names(self):
        inspector = ASTInspector()
        p = Program(declarations=[
            ClassDecl(name="Dog", parent="Animal", members=[])
        ])
        stats = inspector.inspect(p)
        self.assertEqual(stats["class_names"], ["Dog"])

    def test_inspect_struct_names(self):
        inspector = ASTInspector()
        p = Program(declarations=[
            StructDecl(name="Point", fields=[], methods=[])
        ])
        stats = inspector.inspect(p)
        self.assertEqual(stats["struct_names"], ["Point"])

    def test_inspect_enum_names(self):
        inspector = ASTInspector()
        p = Program(declarations=[
            EnumDecl(name="Color", variants=[])
        ])
        stats = inspector.inspect(p)
        self.assertEqual(stats["enum_names"], ["Color"])

    def test_inspect_trait_names(self):
        inspector = ASTInspector()
        p = Program(declarations=[
            TraitDecl(name="Comparable", members=[])
        ])
        stats = inspector.inspect(p)
        self.assertEqual(stats["trait_names"], ["Comparable"])

    def test_inspect_interface_names(self):
        inspector = ASTInspector()
        p = Program(declarations=[
            InterfaceDecl(name="Iterable", members=[])
        ])
        stats = inspector.inspect(p)
        self.assertEqual(stats["interface_names"], ["Iterable"])

    def test_inspect_identifiers(self):
        inspector = ASTInspector()
        expr = BinaryExpr(ident("a"), "+", ident("b"))
        stats = inspector.inspect(expr)
        self.assertEqual(stats["identifiers"], 2)

    def test_inspect_node_counts(self):
        inspector = ASTInspector()
        expr = BinaryExpr(int_lit(1), "+", int_lit(2))
        stats = inspector.inspect(expr)
        self.assertEqual(stats["node_counts"]["BinaryExpr"], 1)
        self.assertEqual(stats["node_counts"]["LiteralExpr"], 2)

    def test_inspect_module(self):
        inspector = ASTInspector()
        m = Module(name="math", declarations=[], imports=[])
        stats = inspector.inspect(m)
        self.assertEqual(stats["total_nodes"], 1)


# ══════════════════════════════════════════════════════════════════
# Test: Source Span Validation
# ══════════════════════════════════════════════════════════════════


class TestSourceSpanValidation(unittest.TestCase):
    def test_valid_source_span(self):
        loc_valid = loc_range(1, 1, 5, 10)
        e = LiteralExpr(value=42, location=loc_valid)
        p = Program(declarations=[
            ExpressionStmt(expression=e, location=loc_valid)
        ])
        result = validate_ast(p)
        self.assertTrue(result.is_valid)

    def test_negative_start_line(self):
        bad_loc = SourceLocation("test.i", -1, 1, 1, 10)
        e = LiteralExpr(value=42, location=bad_loc)
        p = Program(declarations=[ExpressionStmt(expression=e)])
        result = validate_ast(p)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("start_line" in e.message for e in result.errors))

    def test_negative_start_column(self):
        bad_loc = SourceLocation("test.i", 1, -5, 1, 10)
        e = LiteralExpr(value=42, location=bad_loc)
        p = Program(declarations=[ExpressionStmt(expression=e)])
        result = validate_ast(p)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("start_column" in e.message for e in result.errors))

    def test_end_before_start_line(self):
        bad_loc = SourceLocation("test.i", 5, 1, 2, 10)
        e = LiteralExpr(value=42, location=bad_loc)
        p = Program(declarations=[ExpressionStmt(expression=e)])
        result = validate_ast(p)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("end_line" in e.message for e in result.errors))

    def test_end_before_start_column_same_line(self):
        bad_loc = SourceLocation("test.i", 3, 10, 3, 2)
        e = LiteralExpr(value=42, location=bad_loc)
        p = Program(declarations=[ExpressionStmt(expression=e)])
        result = validate_ast(p)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("end_column" in e.message for e in result.errors))

    def test_end_offset_before_start_offset(self):
        bad_loc = SourceLocation("test.i", 1, 1, 1, 10, start_offset=100,
                                end_offset=50)
        e = LiteralExpr(value=42, location=bad_loc)
        p = Program(declarations=[ExpressionStmt(expression=e)])
        result = validate_ast(p)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("end_offset" in e.message for e in result.errors))


# ══════════════════════════════════════════════════════════════════
# Test: Validation with New Nodes
# ══════════════════════════════════════════════════════════════════


class TestValidationNewNodes(unittest.TestCase):
    def test_valid_method_decl(self):
        md = MethodDecl(name="foo", parameters=[], return_type=None,
                        body=empty_block())
        p = Program(declarations=[md])
        result = validate_ast(p)
        self.assertTrue(result.is_valid)

    def test_method_return_outside_function(self):
        md = MethodDecl(name="m", parameters=[], return_type=None,
                        body=BlockStmt(statements=[ReturnStmt(value=int_lit(1))]))
        p = Program(declarations=[md])
        result = validate_ast(p)
        self.assertTrue(result.is_valid)  # method counts as function context

    def test_valid_module(self):
        m = Module(name="test", declarations=[
            VarDecl(name="x", type_annotation=None, initializer=int_lit(1))
        ], imports=[])
        result = validate_ast(m)
        self.assertTrue(result.is_valid)

    def test_placeholder_is_valid(self):
        p = PlaceholderExpr(description="todo")
        prog = Program(declarations=[
            ExpressionStmt(expression=p)
        ])
        result = validate_ast(prog)
        self.assertTrue(result.is_valid)

    def test_method_call_expr_valid(self):
        mce = MethodCallExpr(object=ident("obj"), method="foo",
                             arguments=[int_lit(1)])
        p = Program(declarations=[
            ExpressionStmt(expression=mce)
        ])
        result = validate_ast(p)
        self.assertTrue(result.is_valid)


# ══════════════════════════════════════════════════════════════════
# Test: Serialization of New Nodes
# ══════════════════════════════════════════════════════════════════


class TestSerializationNewNodes(unittest.TestCase):
    def test_round_trip_module(self):
        m = Module(name="my_mod",
                   declarations=[VarDecl(name="x", type_annotation=None,
                                         initializer=int_lit(1))],
                   imports=[ImportDecl(path="math")])
        serializer = ASTSerializer()
        json_str = serializer.to_json(m)
        self.assertIn("Module", json_str)
        deserializer = ASTDeserializer()
        m2 = deserializer.from_json(json_str)
        self.assertIsInstance(m2, Module)
        self.assertEqual(m2.name, "my_mod")
        self.assertEqual(len(m2.declarations), 1)
        self.assertEqual(len(m2.imports), 1)

    def test_round_trip_method_decl(self):
        md = MethodDecl(name="do_thing", parameters=[param("x")],
                        return_type=NamedType(name="int"),
                        body=BlockStmt(statements=[
                            ReturnStmt(value=int_lit(42))
                        ]), is_static=True)
        serializer = ASTSerializer()
        json_str = serializer.to_json(md)
        self.assertIn("MethodDecl", json_str)
        deserializer = ASTDeserializer()
        md2 = deserializer.from_json(json_str)
        self.assertIsInstance(md2, MethodDecl)
        self.assertEqual(md2.name, "do_thing")
        self.assertTrue(md2.is_static)
        self.assertEqual(len(md2.parameters), 1)

    def test_round_trip_method_call_expr(self):
        mce = MethodCallExpr(object=ident("self"), method="send",
                             arguments=[int_lit(1), str_lit("msg")])
        serializer = ASTSerializer()
        json_str = serializer.to_json(mce)
        self.assertIn("MethodCallExpr", json_str)
        deserializer = ASTDeserializer()
        mce2 = deserializer.from_json(json_str)
        self.assertIsInstance(mce2, MethodCallExpr)
        self.assertEqual(mce2.method, "send")
        self.assertEqual(len(mce2.arguments), 2)

    def test_round_trip_placeholder(self):
        p = PlaceholderExpr(description="await support")
        serializer = ASTSerializer()
        json_str = serializer.to_json(p)
        self.assertIn("PlaceholderExpr", json_str)
        deserializer = ASTDeserializer()
        p2 = deserializer.from_json(json_str)
        self.assertIsInstance(p2, PlaceholderExpr)
        self.assertEqual(p2.description, "await support")

    def test_full_program_round_trip(self):
        p = Program(declarations=[
            ImportDecl(path="math"),
            Module(name="sub", declarations=[
                VarDecl(name="x", type_annotation=NamedType(name="int"),
                        initializer=int_lit(10)),
            ], imports=[]),
            MethodDecl(name="calc", parameters=[param("a")],
                       return_type=NamedType(name="int"),
                       body=BlockStmt(statements=[
                           ReturnStmt(value=MethodCallExpr(
                               object=ident("self"),
                               method="helper",
                               arguments=[ident("a")]
                           ))
                       ])),
            ExpressionStmt(expression=MethodCallExpr(
                object=ident("obj"), method="run", arguments=[]
            )),
            ExpressionStmt(expression=PlaceholderExpr(description="future")),
        ])
        serializer = ASTSerializer()
        json_str = serializer.to_json(p)
        deserializer = ASTDeserializer()
        p2 = deserializer.from_json(json_str)
        self.assertEqual(len(p2.declarations), 5)
        self.assertIsInstance(p2.declarations[0], ImportDecl)
        self.assertIsInstance(p2.declarations[1], Module)
        self.assertIsInstance(p2.declarations[2], MethodDecl)
        self.assertIsInstance(p2.declarations[3], ExpressionStmt)
        self.assertIsInstance(p2.declarations[4], ExpressionStmt)
        self.assertIsInstance(p2.declarations[4].expression, PlaceholderExpr)


# ══════════════════════════════════════════════════════════════════
# Test: Binary Serialization
# ══════════════════════════════════════════════════════════════════


class TestBinarySerialization(unittest.TestCase):
    def test_round_trip(self):
        p = Program(declarations=[
            VarDecl(name="x", type_annotation=NamedType(name="int"),
                    initializer=int_lit(42))
        ])
        serializer = ASTBinarySerializer()
        data = serializer.to_bytes(p)
        self.assertIsInstance(data, bytes)
        self.assertTrue(data.startswith(b"I-AST-v1\n"))
        p2 = serializer.from_bytes(data)
        self.assertIsInstance(p2, Program)
        self.assertEqual(len(p2.declarations), 1)

    def test_compressed_is_smaller(self):
        # Build a moderately large AST
        decls = [VarDecl(name=f"v{i}", type_annotation=None,
                         initializer=int_lit(i)) for i in range(50)]
        p = Program(declarations=decls)
        serializer = ASTBinarySerializer()
        data = serializer.to_bytes(p)
        json_data = json.dumps(ASTSerializer().to_dict(p)).encode("utf-8")
        # Binary should be smaller (compressed)
        self.assertLess(len(data), len(json_data))

    def test_invalid_header(self):
        serializer = ASTBinarySerializer()
        with self.assertRaises(ValueError):
            serializer.from_bytes(b"INVALID DATA")

    def test_file_round_trip(self):
        import tempfile
        p = Program(declarations=[VarDecl(name="f", type_annotation=None,
                                          initializer=int_lit(7))])
        serializer = ASTBinarySerializer()
        with tempfile.NamedTemporaryFile(suffix=".iast", delete=False) as f:
            path = f.name
        try:
            serializer.to_file(p, path)
            p2 = serializer.from_file(path)
            self.assertIsInstance(p2, Program)
            self.assertEqual(len(p2.declarations), 1)
        finally:
            os.unlink(path)


# ══════════════════════════════════════════════════════════════════
# Test: Versioned Serialization
# ══════════════════════════════════════════════════════════════════


class TestVersionedSerialization(unittest.TestCase):
    def test_round_trip(self):
        p = Program(declarations=[
            VarDecl(name="v", type_annotation=None, initializer=int_lit(5))
        ])
        serializer = ASTVersionedSerializer()
        json_str = serializer.to_json(p)
        data = json.loads(json_str)
        self.assertIn("format_version", data)
        self.assertIn("ast_version", data)
        self.assertIn("ast", data)
        self.assertEqual(data["ast_version"], 1)

    def test_deserialize(self):
        p = Program(declarations=[
            VarDecl(name="x", type_annotation=None, initializer=int_lit(10))
        ])
        serializer = ASTVersionedSerializer()
        json_str = serializer.to_json(p)
        p2 = serializer.from_json(json_str)
        self.assertIsInstance(p2, Program)
        self.assertEqual(len(p2.declarations), 1)

    def test_wrong_version_rejected(self):
        data = {
            "format_version": "1.0",
            "ast_version": 9999,
            "ast": {"kind": "Program", "node_id": 1,
                    "location": {"file": "<input>", "start_line": 0,
                                 "start_column": 0, "end_line": 0,
                                 "end_column": 0, "start_offset": 0,
                                 "end_offset": 0},
                    "declarations": []},
        }
        serializer = ASTVersionedSerializer()
        with self.assertRaises(ValueError):
            serializer.from_dict(data)


# ══════════════════════════════════════════════════════════════════
# Test: Visualization of New Nodes
# ══════════════════════════════════════════════════════════════════


class TestVisualizationNewNodes(unittest.TestCase):
    def test_text_tree_module(self):
        viz = TextTreeVisualizer()
        m = Module(name="test_mod",
                   declarations=[VarDecl(name="x", type_annotation=None,
                                         initializer=int_lit(1))],
                   imports=[])
        output = viz.render(m)
        self.assertIn("test_mod", output)
        self.assertIn("VarDecl", output)

    def test_text_tree_method_decl(self):
        viz = TextTreeVisualizer()
        md = MethodDecl(name="greet", parameters=[], return_type=None,
                        body=empty_block())
        output = viz.render(md)
        self.assertIn("MethodDecl", output)

    def test_text_tree_method_call(self):
        viz = TextTreeVisualizer()
        mce = MethodCallExpr(object=ident("obj"), method="run", arguments=[])
        output = viz.render(mce)
        self.assertIn("MethodCallExpr", output)

    def test_text_tree_placeholder(self):
        viz = TextTreeVisualizer()
        p = PlaceholderExpr(description="TBD")
        output = viz.render(p)
        self.assertIn("PlaceholderExpr", output)

    def test_dot_module(self):
        viz = DOTVisualizer()
        m = Module(name="m", declarations=[], imports=[])
        dot = viz.to_dot(m)
        self.assertIn("Module", dot)
        self.assertIn("digraph AST", dot)

    def test_dot_method_call(self):
        viz = DOTVisualizer()
        mce = MethodCallExpr(object=ident("x"), method="foo",
                             arguments=[int_lit(1)])
        dot = viz.to_dot(mce)
        self.assertIn("MethodCallExpr", dot)


# ══════════════════════════════════════════════════════════════════
# Test: Debug Printer with New Nodes
# ══════════════════════════════════════════════════════════════════


class TestDebugPrinterNewNodes(unittest.TestCase):
    def test_method_decl_debug(self):
        md = MethodDecl(name="foo", parameters=[], return_type=None,
                        body=empty_block(), location=loc(3, 2))
        printer = DebugPrinter()
        output = printer.print(md)
        self.assertIn("Method(foo)", output)
        self.assertIn("3:2", output)

    def test_static_method_decl_debug(self):
        md = MethodDecl(name="bar", parameters=[], return_type=None,
                        body=empty_block(), is_static=True)
        printer = DebugPrinter()
        output = printer.print(md)
        self.assertIn("StaticMethod(bar)", output)

    def test_module_debug(self):
        m = Module(name="mod", declarations=[], imports=[], location=loc(1, 1))
        printer = DebugPrinter()
        output = printer.print(m)
        self.assertIn("Module(mod)", output)


# ══════════════════════════════════════════════════════════════════
# Test: Stress Tests
# ══════════════════════════════════════════════════════════════════


class TestStress(unittest.TestCase):
    def test_large_ast_creation(self):
        """Create a large AST with 1000 declarations."""
        decls = []
        for i in range(1000):
            decls.append(VarDecl(
                name=f"var_{i}",
                type_annotation=NamedType(name="int"),
                initializer=LiteralExpr(value=i)
            ))
        p = Program(declarations=decls)
        self.assertEqual(len(p.declarations), 1000)

    def test_deep_ast(self):
        """Create a deeply nested expression (100 levels)."""
        expr = int_lit(0)
        for i in range(100):
            expr = BinaryExpr(expr, "+", int_lit(i))
        self.assertIsNotNone(expr)
        inspector = ASTInspector()
        stats = inspector.inspect(expr)
        self.assertGreater(stats["max_depth"], 100)

    def test_wide_ast(self):
        """Create a program with many statements per block."""
        stmts = [ExpressionStmt(expression=int_lit(i)) for i in range(500)]
        p = Program(declarations=[
            FunctionDecl(name="big", parameters=[], return_type=None,
                         body=BlockStmt(statements=stmts))
        ])
        inspector = ASTInspector()
        stats = inspector.inspect(p)
        self.assertGreater(stats["max_children"], 100)

    def test_deep_ast_validation(self):
        """Validate a deeply nested AST without stack overflow."""
        expr = int_lit(0)
        for i in range(200):
            expr = BinaryExpr(expr, "+", int_lit(i))
        p = Program(declarations=[
            ExpressionStmt(expression=expr)
        ])
        result = validate_ast(p)
        self.assertTrue(result.is_valid)

    def test_large_ast_serialization(self):
        """Serialize and deserialize a large AST."""
        decls = [VarDecl(name=f"x{i}", type_annotation=None,
                         initializer=int_lit(i)) for i in range(100)]
        p = Program(declarations=decls)
        serializer = ASTSerializer()
        json_str = serializer.to_json(p)
        deserializer = ASTDeserializer()
        p2 = deserializer.from_json(json_str)
        self.assertEqual(len(p2.declarations), 100)

    def test_large_ast_binary_serialization(self):
        """Binary serialize a large AST."""
        decls = [VarDecl(name=f"v{i}", type_annotation=None,
                         initializer=int_lit(i)) for i in range(200)]
        p = Program(declarations=decls)
        serializer = ASTBinarySerializer()
        data = serializer.to_bytes(p)
        p2 = serializer.from_bytes(data)
        self.assertEqual(len(p2.declarations), 200)

    def test_many_visitors_performance(self):
        """Walk a large AST many times."""
        decls = [VarDecl(name=f"v{i}", type_annotation=None,
                         initializer=int_lit(i)) for i in range(500)]
        p = Program(declarations=decls)
        for _ in range(10):
            walker = ASTWalker()
            visited = []
            walker.on_enter(lambda n: visited.append(n))
            walker.walk(p)
            self.assertGreater(len(visited), 500)


# ══════════════════════════════════════════════════════════════════
# Test: Unicode Tests
# ══════════════════════════════════════════════════════════════════


class TestUnicode(unittest.TestCase):
    def test_unicode_identifiers(self):
        """Test Unicode in identifier names."""
        e = IdentifierExpr(name="ibara_yumurerwa")
        self.assertEqual(e.name, "ibara_yumurerwa")

    def test_unicode_literal(self):
        """Test Unicode string literals."""
        e = LiteralExpr(value="Muraho Dunia")
        self.assertEqual(e.value, "Muraho Dunia")

    def test_unicode_module_name(self):
        m = Module(name="ibisobanuro", declarations=[], imports=[])
        self.assertEqual(m.name, "ibisobanuro")

    def test_unicode_in_printer(self):
        p = Program(declarations=[
            VarDecl(name="ibara", type_annotation=None,
                    initializer=LiteralExpr(value="icyumweru"))
        ])
        printer = PrettyPrinter()
        output = printer.print(p)
        self.assertIn("ibara", output)
        self.assertIn("icyumweru", output)

    def test_unicode_in_visualizer(self):
        viz = TextTreeVisualizer()
        p = Program(declarations=[
            VarDecl(name="umurimo", type_annotation=None,
                    initializer=LiteralExpr(value="kora"))
        ])
        output = viz.render(p)
        self.assertIn("umurimo", output)

    def test_unicode_serialization_round_trip(self):
        p = Program(declarations=[
            VarDecl(name="igice", type_annotation=None,
                    initializer=LiteralExpr(value="Igihe"))
        ])
        serializer = ASTSerializer()
        json_str = serializer.to_json(p)
        self.assertIn("igice", json_str)
        self.assertIn("Igihe", json_str)
        deserializer = ASTDeserializer()
        p2 = deserializer.from_json(json_str)
        self.assertEqual(p2.declarations[0].name, "igice")
        self.assertEqual(p2.declarations[0].initializer.value, "Igihe")

    def test_unicode_binary_serialization(self):
        p = Program(declarations=[
            VarDecl(name="amategeko", type_annotation=None,
                    initializer=LiteralExpr(value="Kinyarwanda"))
        ])
        serializer = ASTBinarySerializer()
        data = serializer.to_bytes(p)
        p2 = serializer.from_bytes(data)
        self.assertEqual(p2.declarations[0].name, "amategeko")

    def test_emoji_in_string(self):
        e = LiteralExpr(value="\U0001f600")
        self.assertEqual(e.value, "\U0001f600")


# ══════════════════════════════════════════════════════════════════
# Test: Golden Snapshots
# ══════════════════════════════════════════════════════════════════


class TestGoldenSnapshots(unittest.TestCase):
    def test_snapshot_simple_program(self):
        p = Program(declarations=[
            VarDecl(name="x", type_annotation=NamedType(name="int"),
                    initializer=int_lit(42)),
        ])
        printer = PrettyPrinter()
        output = printer.print(p)
        expected = (
            "Program\n"
            "  Var(x)\n"
            "    Type(int)\n"
            "    Literal(42)"
        )
        self.assertEqual(output, expected)

    def test_snapshot_function(self):
        p = Program(declarations=[
            func_decl("add", params=[param("a"), param("b")], ret="int",
                      stmts=[ReturnStmt(value=BinaryExpr(
                          ident("a"), "+", ident("b")))]),
        ])
        printer = PrettyPrinter()
        output = printer.print(p)
        self.assertIn("Program", output)
        self.assertIn("Function(add)", output)
        self.assertIn("Param(a)", output)
        self.assertIn("Param(b)", output)
        self.assertIn("Type(int)", output)
        self.assertIn("Return", output)
        self.assertIn("Binary(+)", output)

    def test_snapshot_method_call(self):
        p = Program(declarations=[
            ExpressionStmt(expression=MethodCallExpr(
                object=ident("self"), method="send",
                arguments=[int_lit(1), str_lit("hi")]
            ))
        ])
        printer = PrettyPrinter()
        output = printer.print(p)
        self.assertIn("MethodCall(send)", output)
        self.assertIn("Identifier(self)", output)

    def test_snapshot_module(self):
        m = Module(name="utils",
                   imports=[ImportDecl(path="math", alias="m")],
                   declarations=[
                       VarDecl(name="pi", type_annotation=None,
                               initializer=LiteralExpr(value=3.14))
                   ])
        printer = PrettyPrinter()
        output = printer.print(m)
        self.assertIn("Module(utils)", output)
        self.assertIn("Import(math as m)", output)
        self.assertIn("Var(pi)", output)


# ══════════════════════════════════════════════════════════════════
# Test: ASTWalker with New Nodes
# ══════════════════════════════════════════════════════════════════


class TestWalkerNewNodes(unittest.TestCase):
    def test_walk_method_call(self):
        walker = ASTWalker()
        types = []
        walker.on_enter(lambda n: types.append(n.__class__.__name__))
        mce = MethodCallExpr(object=ident("x"), method="f",
                             arguments=[int_lit(1)])
        walker.walk(mce)
        self.assertIn("MethodCallExpr", types)
        self.assertIn("IdentifierExpr", types)
        self.assertIn("LiteralExpr", types)

    def test_walk_placeholder(self):
        walker = ASTWalker()
        types = []
        walker.on_enter(lambda n: types.append(n.__class__.__name__))
        walker.walk(PlaceholderExpr(description="todo"))
        self.assertEqual(types, ["PlaceholderExpr"])

    def test_walk_module(self):
        walker = ASTWalker()
        types = []
        walker.on_enter(lambda n: types.append(n.__class__.__name__))
        m = Module(name="m", declarations=[
            VarDecl(name="x", type_annotation=None, initializer=int_lit(1))
        ], imports=[])
        walker.walk(m)
        self.assertIn("Module", types)
        self.assertIn("VarDecl", types)

    def test_walk_method_decl(self):
        walker = ASTWalker()
        types = []
        walker.on_enter(lambda n: types.append(n.__class__.__name__))
        md = MethodDecl(name="m", parameters=[], return_type=None,
                        body=empty_block())
        walker.walk(md)
        self.assertIn("MethodDecl", types)
        self.assertIn("BlockStmt", types)


# ══════════════════════════════════════════════════════════════════
# Test: ASTTransformer with New Nodes
# ══════════════════════════════════════════════════════════════════


class TestTransformerNewNodes(unittest.TestCase):
    def test_transform_method_call(self):
        class RenameMethod(ASTTransformer):
            def visit_method_call_expr(self, expr):
                return MethodCallExpr(
                    object=expr.object, method="renamed",
                    arguments=expr.arguments, node_id=expr.node_id,
                    location=expr.location)
        mce = MethodCallExpr(object=ident("x"), method="old", arguments=[])
        result = RenameMethod().transform(mce)
        self.assertEqual(result.method, "renamed")

    def test_transform_method_decl(self):
        class RenameMethod(ASTTransformer):
            def visit_method_decl(self, decl):
                return MethodDecl(
                    name=decl.name + "_renamed",
                    parameters=decl.parameters,
                    return_type=decl.return_type,
                    body=decl.body,
                    is_static=decl.is_static,
                    node_id=decl.node_id,
                    location=decl.location)
        md = MethodDecl(name="foo", parameters=[], return_type=None,
                        body=empty_block())
        result = RenameMethod().transform(md)
        self.assertEqual(result.name, "foo_renamed")

    def test_identity_transform_module(self):
        class IdTransform(ASTTransformer):
            pass
        m = Module(name="m", declarations=[], imports=[])
        result = IdTransform().transform(m)
        self.assertIsInstance(result, Module)
        self.assertEqual(result.name, "m")


# ══════════════════════════════════════════════════════════════════
# Test: Regression Tests
# ══════════════════════════════════════════════════════════════════


class TestRegression(unittest.TestCase):
    def test_program_preserves_node_id(self):
        """Node IDs should be preserved through serialization."""
        p = Program(declarations=[
            VarDecl(name="x", type_annotation=None, initializer=int_lit(1))
        ])
        original_id = p.declarations[0].node_id
        serializer = ASTSerializer()
        data = serializer.to_dict(p)
        deserializer = ASTDeserializer()
        p2 = deserializer.from_dict(data)
        self.assertEqual(p2.declarations[0].node_id, original_id)

    def test_location_preserved_through_transform(self):
        """Locations should be preserved through transformation."""
        loc_test = loc_range(5, 3, 5, 20)
        expr = BinaryExpr(int_lit(1, ), "+", int_lit(2), location=loc_test)
        transformer = ASTTransformer()
        result = transformer.transform(expr)
        self.assertEqual(result.location, loc_test)

    def test_metadata_preserved_through_transform(self):
        """Metadata should be preserved through transformation."""
        expr = int_lit(42)
        expr.set_metadata("inferred_type", "int")
        transformer = ASTTransformer()
        result = transformer.transform(expr)
        self.assertEqual(result.get_metadata("inferred_type"), "int")

    def test_empty_try_stmt_valid(self):
        s = TryStmt(try_body=empty_block(), catch_var=None,
                    catch_body=None, finally_body=None)
        p = Program(declarations=[s])
        result = validate_ast(p)
        self.assertTrue(result.is_valid)

    def test_nested_try_catch_valid(self):
        inner = TryStmt(
            try_body=BlockStmt(statements=[
                ThrowStmt(value=str_lit("inner"))
            ]),
            catch_var="e", catch_body=empty_block())
        outer = TryStmt(
            try_body=BlockStmt(statements=[ExpressionStmt(expression=inner)]),
            catch_var="e2", catch_body=empty_block())
        p = Program(declarations=[outer])
        result = validate_ast(p)
        self.assertTrue(result.is_valid)


# ══════════════════════════════════════════════════════════════════
# Test: Fuzz Tests
# ══════════════════════════════════════════════════════════════════


class TestFuzz(unittest.TestCase):
    def test_random_ast_nodes(self):
        """Create random-ish AST structures and verify they work."""
        import random
        random.seed(42)
        for _ in range(50):
            n_literals = random.randint(1, 20)
            decls = []
            for i in range(n_literals):
                v = random.choice([int_lit(i), str_lit(f"s{i}"),
                                   LiteralExpr(value=float(i))])
                decls.append(VarDecl(name=f"v{i}", type_annotation=None,
                                     initializer=v))
            p = Program(declarations=decls)
            # Verify serialization round-trip
            serializer = ASTSerializer()
            json_str = serializer.to_json(p)
            deserializer = ASTDeserializer()
            p2 = deserializer.from_json(json_str)
            self.assertEqual(len(p2.declarations), n_literals)

    def test_random_tree_shapes(self):
        """Create trees of varying shapes and verify walkers."""
        import random
        random.seed(123)
        for _ in range(30):
            depth = random.randint(1, 15)
            expr = int_lit(0)
            for _ in range(depth):
                op = random.choice(["+", "-", "*", "/"])
                expr = BinaryExpr(expr, op, int_lit(random.randint(0, 100)))
            p = Program(declarations=[
                ExpressionStmt(expression=expr)
            ])
            walker = ASTWalker()
            count = [0]
            walker.on_enter(lambda n: count.__setitem__(0, count[0] + 1))
            walker.walk(p)
            self.assertGreater(count[0], depth + 2)


if __name__ == "__main__":
    unittest.main()
