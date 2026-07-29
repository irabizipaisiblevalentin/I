"""
Comprehensive AST Tests for the I Programming Language

Tests node creation, visitor pattern, walker, transformer,
pretty printer, debug printer, validator, serializer, and visualizer.
"""

import json
import unittest

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
    NamedType,
    NodeType,
    OptionalType,
    Parameter,
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
from compiler.ast.visitor import ASTWalker, ASTTransformer, PrettyPrinter, DebugPrinter
from compiler.ast.validator import validate_ast, ValidationError, ValidationResult
from compiler.ast.serializer import ASTSerializer, ASTDeserializer
from compiler.ast.visualizer import TextTreeVisualizer, DOTVisualizer


# ══════════════════════════════════════════════════════════════════
# Helper: create a standard test location
# ══════════════════════════════════════════════════════════════════

def loc(line: int = 1, col: int = 1) -> SourceLocation:
    return SourceLocation("test.i", line, col, line, col + 5)


def loc_range(start_line: int = 1, start_col: int = 1,
              end_line: int = 1, end_col: int = 10) -> SourceLocation:
    return SourceLocation("test.i", start_line, start_col, end_line, end_col)


# ══════════════════════════════════════════════════════════════════
# Test: SourceLocation
# ══════════════════════════════════════════════════════════════════


class TestSourceLocation(unittest.TestCase):
    def test_from_token(self):
        class MockToken:
            line = 5
            column = 10
            span = 3
            offset = 42
        t = MockToken()
        sl = SourceLocation.from_token(t, "file.i")
        self.assertEqual(sl.file, "file.i")
        self.assertEqual(sl.start_line, 5)
        self.assertEqual(sl.start_column, 10)
        self.assertEqual(sl.end_line, 5)
        self.assertEqual(sl.end_column, 13)
        self.assertEqual(sl.start_offset, 42)
        self.assertEqual(sl.end_offset, 45)

    def test_merge(self):
        a = SourceLocation("a.i", 1, 1, 1, 5)
        b = SourceLocation("a.i", 3, 2, 5, 10)
        merged = SourceLocation.merge(a, b)
        self.assertEqual(merged.start_line, 1)
        self.assertEqual(merged.start_column, 1)
        self.assertEqual(merged.end_line, 5)
        self.assertEqual(merged.end_column, 10)

    def test_line_count(self):
        sl = SourceLocation("f.i", 1, 1, 3, 10)
        self.assertEqual(sl.line_count, 3)

    def test_str_single_line(self):
        sl = SourceLocation("f.i", 5, 3, 5, 8)
        self.assertEqual(str(sl), "f.i:5:3")

    def test_str_multi_line(self):
        sl = SourceLocation("f.i", 1, 1, 3, 10)
        self.assertEqual(str(sl), "f.i:1:1-3:10")


# ══════════════════════════════════════════════════════════════════
# Test: NodeType enum
# ══════════════════════════════════════════════════════════════════


class TestNodeType(unittest.TestCase):
    def test_program_exists(self):
        self.assertEqual(NodeType.PROGRAM.name, "PROGRAM")

    def test_all_declaration_types(self):
        for name in ["VAR_DECL", "FUNCTION_DECL", "STRUCT_DECL", "ENUM_DECL",
                      "CLASS_DECL", "TRAIT_DECL", "INTERFACE_DECL",
                      "IMPORT_DECL", "EXPORT_DECL"]:
            self.assertEqual(getattr(NodeType, name).name, name)

    def test_all_expression_types(self):
        for name in ["LITERAL_EXPR", "IDENTIFIER_EXPR", "BINARY_EXPR",
                      "UNARY_EXPR", "LOGICAL_EXPR", "ASSIGNMENT_EXPR",
                      "COMPOUND_ASSIGNMENT_EXPR", "CALL_EXPR",
                      "CONSTRUCTOR_EXPR", "GET_EXPR", "SET_EXPR",
                      "INDEX_EXPR", "SLICE_EXPR", "SELF_EXPR", "SUPER_EXPR",
                      "LIST_EXPR", "DICT_EXPR", "TUPLE_EXPR",
                      "LAMBDA_EXPR", "IF_EXPR", "GROUPING_EXPR"]:
            self.assertEqual(getattr(NodeType, name).name, name)

    def test_all_statement_types(self):
        for name in ["BLOCK_STMT", "IF_STMT", "WHILE_STMT", "UNTIL_STMT",
                      "FOR_STMT", "FOR_EACH_STMT", "RETURN_STMT",
                      "BREAK_STMT", "CONTINUE_STMT", "THROW_STMT",
                      "TRY_STMT", "EXPRESSION_STMT", "EMPTY_STMT"]:
            self.assertEqual(getattr(NodeType, name).name, name)

    def test_all_type_nodes(self):
        for name in ["NAMED_TYPE", "GENERIC_TYPE", "FUNCTION_TYPE",
                      "OPTIONAL_TYPE", "TUPLE_TYPE"]:
            self.assertEqual(getattr(NodeType, name).name, name)


# ══════════════════════════════════════════════════════════════════
# Test: Node creation and properties
# ══════════════════════════════════════════════════════════════════


class TestNodeCreation(unittest.TestCase):
    def test_literal_expr(self):
        e = LiteralExpr(value=42, location=loc())
        self.assertEqual(e.node_type, NodeType.LITERAL_EXPR)
        self.assertEqual(e.value, 42)
        self.assertEqual(e.children(), [])
        self.assertFalse(e.is_lvalue)

    def test_identifier_expr(self):
        e = IdentifierExpr(name="x", location=loc())
        self.assertEqual(e.node_type, NodeType.IDENTIFIER_EXPR)
        self.assertEqual(e.name, "x")
        self.assertTrue(e.is_lvalue)

    def test_binary_expr(self):
        left = LiteralExpr(value=1)
        right = LiteralExpr(value=2)
        e = BinaryExpr(left=left, operator="+", right=right, location=loc())
        self.assertEqual(e.node_type, NodeType.BINARY_EXPR)
        self.assertEqual(len(e.children()), 2)
        self.assertFalse(e.is_lvalue)

    def test_unary_expr(self):
        inner = LiteralExpr(value=5)
        e = UnaryExpr(operator="-", right=inner, location=loc())
        self.assertEqual(e.node_type, NodeType.UNARY_EXPR)
        self.assertEqual(len(e.children()), 1)

    def test_logical_expr(self):
        l = IdentifierExpr(name="a")
        r = IdentifierExpr(name="b")
        e = LogicalExpr(left=l, operator="kandi", right=r, location=loc())
        self.assertEqual(e.node_type, NodeType.LOGICAL_EXPR)
        self.assertEqual(e.operator, "kandi")

    def test_assignment_expr(self):
        t = IdentifierExpr(name="x")
        v = LiteralExpr(value=10)
        e = AssignmentExpr(target=t, value=v, location=loc())
        self.assertEqual(e.node_type, NodeType.ASSIGNMENT_EXPR)
        self.assertTrue(t.is_lvalue)

    def test_compound_assignment_expr(self):
        t = IdentifierExpr(name="x")
        v = LiteralExpr(value=5)
        e = CompoundAssignmentExpr(target=t, operator="+=", value=v, location=loc())
        self.assertEqual(e.node_type, NodeType.COMPOUND_ASSIGNMENT_EXPR)

    def test_call_expr(self):
        callee = IdentifierExpr(name="foo")
        args = [LiteralExpr(value=1), LiteralExpr(value=2)]
        e = CallExpr(callee=callee, arguments=args, location=loc())
        self.assertEqual(e.node_type, NodeType.CALL_EXPR)
        self.assertEqual(len(e.children()), 3)  # callee + 2 args

    def test_constructor_expr(self):
        args = [LiteralExpr(value="hello")]
        e = ConstructorExpr(class_name="MyClass", arguments=args, location=loc())
        self.assertEqual(e.node_type, NodeType.CONSTRUCTOR_EXPR)
        self.assertEqual(len(e.children()), 1)

    def test_get_expr(self):
        obj = IdentifierExpr(name="myObj")
        e = GetExpr(object=obj, property="field", location=loc())
        self.assertEqual(e.node_type, NodeType.GET_EXPR)
        self.assertTrue(e.is_lvalue)

    def test_set_expr(self):
        obj = IdentifierExpr(name="myObj")
        val = LiteralExpr(value=42)
        e = SetExpr(object=obj, property="field", value=val, location=loc())
        self.assertEqual(e.node_type, NodeType.SET_EXPR)
        self.assertEqual(len(e.children()), 2)

    def test_index_expr(self):
        obj = IdentifierExpr(name="arr")
        idx = LiteralExpr(value=0)
        e = IndexExpr(object=obj, index=idx, location=loc())
        self.assertEqual(e.node_type, NodeType.INDEX_EXPR)
        self.assertTrue(e.is_lvalue)

    def test_slice_expr(self):
        obj = IdentifierExpr(name="arr")
        start = LiteralExpr(value=1)
        end = LiteralExpr(value=5)
        e = SliceExpr(object=obj, start=start, end=end, location=loc())
        self.assertEqual(e.node_type, NodeType.SLICE_EXPR)
        self.assertEqual(len(e.children()), 3)

    def test_slice_expr_partial(self):
        obj = IdentifierExpr(name="arr")
        e = SliceExpr(object=obj, start=None, end=LiteralExpr(value=5), location=loc())
        self.assertEqual(len(e.children()), 2)

    def test_self_expr(self):
        e = SelfExpr(location=loc())
        self.assertEqual(e.node_type, NodeType.SELF_EXPR)
        self.assertEqual(e.children(), [])

    def test_super_expr(self):
        e = SuperExpr(method="foo", location=loc())
        self.assertEqual(e.node_type, NodeType.SUPER_EXPR)

    def test_list_expr(self):
        elems = [LiteralExpr(value=1), LiteralExpr(value=2)]
        e = ListExpr(elements=elems, location=loc())
        self.assertEqual(e.node_type, NodeType.LIST_EXPR)
        self.assertEqual(len(e.children()), 2)

    def test_dict_expr(self):
        keys = [LiteralExpr(value="a")]
        vals = [LiteralExpr(value=1)]
        e = DictExpr(keys=keys, values=vals, location=loc())
        self.assertEqual(e.node_type, NodeType.DICT_EXPR)
        self.assertEqual(len(e.children()), 2)

    def test_tuple_expr(self):
        elems = [LiteralExpr(value=1), LiteralExpr(value="two")]
        e = TupleExpr(elements=elems, location=loc())
        self.assertEqual(e.node_type, NodeType.TUPLE_EXPR)

    def test_lambda_expr(self):
        params = [Parameter(name="x")]
        body = IdentifierExpr(name="x")
        e = LambdaExpr(parameters=params, body=body, location=loc())
        self.assertEqual(e.node_type, NodeType.LAMBDA_EXPR)
        self.assertEqual(len(e.children()), 2)

    def test_if_expr(self):
        cond = IdentifierExpr(name="b")
        then = LiteralExpr(value=1)
        e = IfExpr(condition=cond, then_branch=then, else_branch=None, location=loc())
        self.assertEqual(e.node_type, NodeType.IF_EXPR)
        self.assertEqual(len(e.children()), 2)

    def test_if_expr_with_else(self):
        e = IfExpr(condition=IdentifierExpr("b"), then_branch=LiteralExpr(1),
                   else_branch=LiteralExpr(2), location=loc())
        self.assertEqual(len(e.children()), 3)

    def test_grouping_expr(self):
        inner = BinaryExpr(LiteralExpr(1), "+", LiteralExpr(2))
        e = GroupingExpr(expression=inner, location=loc())
        self.assertEqual(e.node_type, NodeType.GROUPING_EXPR)
        self.assertEqual(len(e.children()), 1)


# ══════════════════════════════════════════════════════════════════
# Test: Type nodes
# ══════════════════════════════════════════════════════════════════


class TestTypeNodes(unittest.TestCase):
    def test_named_type(self):
        t = NamedType(name="int", location=loc())
        self.assertEqual(t.node_type, NodeType.NAMED_TYPE)
        self.assertEqual(t.children(), [])

    def test_generic_type(self):
        arg = NamedType(name="int")
        t = GenericType(name="List", type_args=[arg], location=loc())
        self.assertEqual(t.node_type, NodeType.GENERIC_TYPE)
        self.assertEqual(len(t.children()), 1)

    def test_function_type(self):
        params = [NamedType(name="int"), NamedType(name="string")]
        ret = NamedType(name="bool")
        t = FunctionType(params=params, return_type=ret, location=loc())
        self.assertEqual(t.node_type, NodeType.FUNCTION_TYPE)
        self.assertEqual(len(t.children()), 3)

    def test_optional_type(self):
        inner = NamedType(name="int")
        t = OptionalType(inner=inner, location=loc())
        self.assertEqual(t.node_type, NodeType.OPTIONAL_TYPE)
        self.assertEqual(len(t.children()), 1)

    def test_tuple_type(self):
        elems = [NamedType(name="int"), NamedType(name="string")]
        t = TupleType(elements=elems, location=loc())
        self.assertEqual(t.node_type, NodeType.TUPLE_TYPE)
        self.assertEqual(len(t.children()), 2)


# ══════════════════════════════════════════════════════════════════
# Test: Declaration nodes
# ══════════════════════════════════════════════════════════════════


class TestDeclarationNodes(unittest.TestCase):
    def test_var_decl(self):
        d = VarDecl(name="x", type_annotation=NamedType(name="int"),
                    initializer=LiteralExpr(value=5), location=loc())
        self.assertEqual(d.node_type, NodeType.VAR_DECL)
        self.assertEqual(len(d.children()), 2)
        self.assertFalse(d.is_const)

    def test_var_decl_const(self):
        d = VarDecl(name="PI", type_annotation=None, initializer=LiteralExpr(3.14),
                    is_const=True, location=loc())
        self.assertTrue(d.is_const)
        self.assertEqual(len(d.children()), 1)

    def test_function_decl(self):
        params = [Parameter(name="a"), Parameter(name="b")]
        ret = NamedType(name="int")
        body = BlockStmt(statements=[])
        d = FunctionDecl(name="add", parameters=params, return_type=ret,
                         body=body, location=loc())
        self.assertEqual(d.node_type, NodeType.FUNCTION_DECL)
        self.assertEqual(len(d.children()), 4)  # 2 params + ret + body

    def test_struct_decl(self):
        fields = [StructField(name="x", type_annotation=NamedType(name="int"))]
        methods = []
        d = StructDecl(name="Point", fields=fields, methods=methods, location=loc())
        self.assertEqual(d.node_type, NodeType.STRUCT_DECL)

    def test_enum_decl(self):
        variants = [EnumVariant(name="Red"), EnumVariant(name="Green")]
        d = EnumDecl(name="Color", variants=variants, location=loc())
        self.assertEqual(d.node_type, NodeType.ENUM_DECL)
        self.assertEqual(len(d.children()), 2)

    def test_class_decl(self):
        d = ClassDecl(name="Dog", parent="Animal", members=[], location=loc())
        self.assertEqual(d.node_type, NodeType.CLASS_DECL)
        self.assertEqual(d.parent, "Animal")

    def test_trait_decl(self):
        d = TraitDecl(name="Comparable", members=[], location=loc())
        self.assertEqual(d.node_type, NodeType.TRAIT_DECL)

    def test_interface_decl(self):
        d = InterfaceDecl(name="Iterable", members=[], location=loc())
        self.assertEqual(d.node_type, NodeType.INTERFACE_DECL)

    def test_import_decl(self):
        d = ImportDecl(path="math", alias="m", location=loc())
        self.assertEqual(d.node_type, NodeType.IMPORT_DECL)
        self.assertEqual(d.alias, "m")

    def test_export_decl(self):
        d = ExportDecl(name="main", location=loc())
        self.assertEqual(d.node_type, NodeType.EXPORT_DECL)


# ══════════════════════════════════════════════════════════════════
# Test: Statement nodes
# ══════════════════════════════════════════════════════════════════


class TestStatementNodes(unittest.TestCase):
    def test_block_stmt(self):
        stmts = [ExpressionStmt(expression=LiteralExpr(1)),
                 EmptyStmt()]
        s = BlockStmt(statements=stmts, location=loc())
        self.assertEqual(s.node_type, NodeType.BLOCK_STMT)
        self.assertEqual(len(s.children()), 2)

    def test_if_stmt(self):
        cond = IdentifierExpr("b")
        then = BlockStmt(statements=[])
        s = IfStmt(condition=cond, then_branch=then, elif_branches=[],
                   else_branch=None, location=loc())
        self.assertEqual(s.node_type, NodeType.IF_STMT)
        self.assertEqual(len(s.children()), 2)

    def test_if_stmt_with_elifs_and_else(self):
        elifs = [ElifBranch(condition=IdentifierExpr("c"),
                            body=BlockStmt(statements=[]))]
        else_b = BlockStmt(statements=[])
        s = IfStmt(condition=IdentifierExpr("a"),
                   then_branch=BlockStmt(statements=[]),
                   elif_branches=elifs, else_branch=else_b, location=loc())
        self.assertEqual(len(s.children()), 4)  # cond + then + elif + else

    def test_while_stmt(self):
        s = WhileStmt(condition=IdentifierExpr("x"),
                      body=BlockStmt(statements=[]), location=loc())
        self.assertEqual(s.node_type, NodeType.WHILE_STMT)

    def test_until_stmt(self):
        s = UntilStmt(condition=IdentifierExpr("done"),
                      body=BlockStmt(statements=[]), location=loc())
        self.assertEqual(s.node_type, NodeType.UNTIL_STMT)

    def test_for_stmt(self):
        body = BlockStmt(statements=[])
        s = ForStmt(variable="i", start=LiteralExpr(0), end=LiteralExpr(10),
                    step=LiteralExpr(2), body=body, location=loc())
        self.assertEqual(s.node_type, NodeType.FOR_STMT)
        self.assertEqual(len(s.children()), 4)  # start + end + step + body

    def test_for_stmt_no_step(self):
        s = ForStmt(variable="i", start=LiteralExpr(0), end=LiteralExpr(10),
                    step=None, body=BlockStmt(statements=[]), location=loc())
        self.assertEqual(len(s.children()), 3)

    def test_for_each_stmt(self):
        iterable = ListExpr(elements=[LiteralExpr(1)])
        body = BlockStmt(statements=[])
        s = ForEachStmt(element="x", iterable=iterable, body=body, location=loc())
        self.assertEqual(s.node_type, NodeType.FOR_EACH_STMT)

    def test_return_stmt(self):
        s = ReturnStmt(value=LiteralExpr(42), location=loc())
        self.assertEqual(s.node_type, NodeType.RETURN_STMT)
        self.assertEqual(len(s.children()), 1)

    def test_return_stmt_void(self):
        s = ReturnStmt(value=None, location=loc())
        self.assertEqual(s.children(), [])

    def test_break_stmt(self):
        s = BreakStmt(location=loc())
        self.assertEqual(s.node_type, NodeType.BREAK_STMT)
        self.assertEqual(s.children(), [])

    def test_continue_stmt(self):
        s = ContinueStmt(location=loc())
        self.assertEqual(s.node_type, NodeType.CONTINUE_STMT)

    def test_throw_stmt(self):
        msg = LiteralExpr(value="error")
        s = ThrowStmt(value=msg, location=loc())
        self.assertEqual(s.node_type, NodeType.THROW_STMT)

    def test_try_stmt(self):
        try_b = BlockStmt(statements=[])
        catch_b = BlockStmt(statements=[])
        finally_b = BlockStmt(statements=[])
        s = TryStmt(try_body=try_b, catch_var="e", catch_body=catch_b,
                    finally_body=finally_b, location=loc())
        self.assertEqual(s.node_type, NodeType.TRY_STMT)
        self.assertEqual(len(s.children()), 3)

    def test_expression_stmt(self):
        expr = LiteralExpr(value=42)
        s = ExpressionStmt(expression=expr, location=loc())
        self.assertEqual(s.node_type, NodeType.EXPRESSION_STMT)
        self.assertEqual(len(s.children()), 1)

    def test_empty_stmt(self):
        s = EmptyStmt(location=loc())
        self.assertEqual(s.node_type, NodeType.EMPTY_STMT)
        self.assertEqual(s.children(), [])


# ══════════════════════════════════════════════════════════════════
# Test: Helper nodes
# ══════════════════════════════════════════════════════════════════


class TestHelperNodes(unittest.TestCase):
    def test_parameter(self):
        p = Parameter(name="x", type_annotation=NamedType(name="int"),
                      default=LiteralExpr(0), location=loc())
        self.assertEqual(p.name, "x")
        self.assertEqual(len(p.children()), 2)

    def test_parameter_no_type_no_default(self):
        p = Parameter(name="y", location=loc())
        self.assertEqual(p.children(), [])

    def test_struct_field(self):
        f = StructField(name="x", type_annotation=NamedType(name="int"),
                        default=LiteralExpr(0), location=loc())
        self.assertEqual(f.name, "x")
        self.assertEqual(len(f.children()), 2)

    def test_enum_variant(self):
        v = EnumVariant(name="Red", value=LiteralExpr(0), location=loc())
        self.assertEqual(v.name, "Red")
        self.assertEqual(len(v.children()), 1)

    def test_enum_variant_no_value(self):
        v = EnumVariant(name="None", location=loc())
        self.assertEqual(v.children(), [])

    def test_elif_branch(self):
        b = ElifBranch(condition=IdentifierExpr("c"),
                       body=BlockStmt(statements=[]), location=loc())
        self.assertEqual(len(b.children()), 2)


# ══════════════════════════════════════════════════════════════════
# Test: Program root
# ══════════════════════════════════════════════════════════════════


class TestProgram(unittest.TestCase):
    def test_empty_program(self):
        p = Program(declarations=[], location=loc())
        self.assertEqual(p.node_type, NodeType.PROGRAM)
        self.assertEqual(p.children(), [])

    def test_program_with_decls(self):
        d1 = VarDecl(name="x", type_annotation=None, initializer=LiteralExpr(1))
        d2 = FunctionDecl(name="f", parameters=[], return_type=None,
                          body=BlockStmt(statements=[]))
        p = Program(declarations=[d1, d2], location=loc())
        self.assertEqual(len(p.children()), 2)


# ══════════════════════════════════════════════════════════════════
# Test: Metadata
# ══════════════════════════════════════════════════════════════════


class TestMetadata(unittest.TestCase):
    def test_set_and_get(self):
        e = LiteralExpr(value=1)
        e.set_metadata("type", "int")
        self.assertEqual(e.get_metadata("type"), "int")
        self.assertIsNone(e.get_metadata("missing"))
        self.assertEqual(e.get_metadata("missing", "default"), "default")


# ══════════════════════════════════════════════════════════════════
# Test: ASTWalker
# ══════════════════════════════════════════════════════════════════


class TestASTWalker(unittest.TestCase):
    def test_walk_literal(self):
        walker = ASTWalker()
        visited = []
        walker.on_enter(lambda n: visited.append(("enter", n.__class__.__name__)))
        walker.on_exit(lambda n: visited.append(("exit", n.__class__.__name__)))
        walker.walk(LiteralExpr(value=42))
        self.assertEqual(visited, [("enter", "LiteralExpr"), ("exit", "LiteralExpr")])

    def test_walk_binary(self):
        walker = ASTWalker()
        types = []
        walker.on_enter(lambda n: types.append(n.__class__.__name__))
        expr = BinaryExpr(LiteralExpr(1), "+", LiteralExpr(2))
        walker.walk(expr)
        self.assertEqual(types, ["BinaryExpr", "LiteralExpr", "LiteralExpr"])

    def test_walk_program(self):
        walker = ASTWalker()
        types = []
        walker.on_enter(lambda n: types.append(n.__class__.__name__))
        p = Program(declarations=[
            VarDecl(name="x", type_annotation=None, initializer=LiteralExpr(1))
        ])
        walker.walk(p)
        self.assertIn("Program", types)
        self.assertIn("VarDecl", types)
        self.assertIn("LiteralExpr", types)


# ══════════════════════════════════════════════════════════════════
# Test: ASTTransformer
# ══════════════════════════════════════════════════════════════════


class TestASTTransformer(unittest.TestCase):
    def test_identity_transform(self):
        class IdTransform(ASTTransformer):
            pass
        expr = BinaryExpr(LiteralExpr(1), "+", LiteralExpr(2))
        result = IdTransform().transform(expr)
        self.assertIsInstance(result, BinaryExpr)

    def test_literal_replacement(self):
        class DoubleLiteral(ASTTransformer):
            def visit_literal_expr(self, expr):
                if isinstance(expr.value, (int, float)):
                    return LiteralExpr(value=expr.value * 2, location=expr.location)
                return expr
        expr = BinaryExpr(LiteralExpr(3), "+", LiteralExpr(4))
        result = DoubleLiteral().transform(expr)
        self.assertIsInstance(result, BinaryExpr)
        self.assertEqual(result.left.value, 6)
        self.assertEqual(result.right.value, 8)


# ══════════════════════════════════════════════════════════════════
# Test: PrettyPrinter
# ══════════════════════════════════════════════════════════════════


class TestPrettyPrinter(unittest.TestCase):
    def test_literal(self):
        printer = PrettyPrinter()
        output = printer.print(LiteralExpr(value=42))
        self.assertIn("Literal(42)", output)

    def test_binary(self):
        printer = PrettyPrinter()
        expr = BinaryExpr(LiteralExpr(1), "+", LiteralExpr(2))
        output = printer.print(expr)
        self.assertIn("Binary(+)", output)
        self.assertIn("Literal(1)", output)
        self.assertIn("Literal(2)", output)

    def test_program(self):
        printer = PrettyPrinter()
        p = Program(declarations=[
            VarDecl(name="x", type_annotation=None, initializer=LiteralExpr(1))
        ])
        output = printer.print(p)
        self.assertIn("Program", output)
        self.assertIn("Var(x)", output)

    def test_indented_output(self):
        printer = PrettyPrinter(indent=">>> ")
        expr = BinaryExpr(LiteralExpr(1), "+", LiteralExpr(2))
        output = printer.print(expr)
        self.assertIn(">>> Literal(1)", output)
        self.assertIn(">>> Literal(2)", output)


# ══════════════════════════════════════════════════════════════════
# Test: DebugPrinter
# ══════════════════════════════════════════════════════════════════


class TestDebugPrinter(unittest.TestCase):
    def test_shows_node_id(self):
        printer = DebugPrinter()
        e = LiteralExpr(value=42, location=loc(5, 3))
        output = printer.print(e)
        self.assertIn(f"[{e.node_id}]", output)
        self.assertIn("Literal(42)", output)

    def test_shows_location(self):
        printer = DebugPrinter()
        e = LiteralExpr(value=1, location=loc(10, 5))
        output = printer.print(e)
        self.assertIn("test.i", output)
        self.assertIn("10", output)


# ══════════════════════════════════════════════════════════════════
# Test: Validator
# ══════════════════════════════════════════════════════════════════


class TestValidator(unittest.TestCase):
    def test_valid_program(self):
        p = Program(declarations=[
            VarDecl(name="x", type_annotation=None, initializer=LiteralExpr(1))
        ])
        result = validate_ast(p)
        self.assertTrue(result.is_valid)

    def test_break_outside_loop(self):
        p = Program(declarations=[
            FunctionDecl(name="f", parameters=[], return_type=None,
                         body=BlockStmt(statements=[BreakStmt()]))
        ])
        result = validate_ast(p)
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Break" in e.message for e in result.errors))

    def test_continue_outside_loop(self):
        p = Program(declarations=[
            FunctionDecl(name="f", parameters=[], return_type=None,
                         body=BlockStmt(statements=[ContinueStmt()]))
        ])
        result = validate_ast(p)
        self.assertFalse(result.is_valid)

    def test_return_outside_function(self):
        p = Program(declarations=[
            ReturnStmt(value=LiteralExpr(1))
        ])
        result = validate_ast(p)
        self.assertFalse(result.is_valid)

    def test_valid_break_in_loop(self):
        p = Program(declarations=[
            WhileStmt(condition=IdentifierExpr("true"),
                      body=BlockStmt(statements=[BreakStmt()]))
        ])
        result = validate_ast(p)
        self.assertTrue(result.is_valid)

    def test_assignment_to_rvalue(self):
        p = Program(declarations=[
            FunctionDecl(name="f", parameters=[], return_type=None,
                         body=BlockStmt(statements=[
                             AssignmentExpr(target=LiteralExpr(42),
                                            value=LiteralExpr(1))
                         ]))
        ])
        result = validate_ast(p)
        self.assertFalse(result.is_valid)

    def test_duplicate_var_in_scope(self):
        p = Program(declarations=[
            BlockStmt(statements=[
                VarDecl(name="x", type_annotation=None, initializer=LiteralExpr(1)),
                VarDecl(name="x", type_annotation=None, initializer=LiteralExpr(2)),
            ])
        ])
        result = validate_ast(p)
        self.assertTrue(result.is_valid)  # warning, not error
        self.assertTrue(any("Duplicate" in e.message for e in result.errors))


# ══════════════════════════════════════════════════════════════════
# Test: Serializer / Deserializer
# ══════════════════════════════════════════════════════════════════


class TestSerializer(unittest.TestCase):
    def test_round_trip_literal(self):
        e = LiteralExpr(value=42, location=loc(1, 2))
        serializer = ASTSerializer()
        data = serializer.to_dict(e)
        self.assertEqual(data["kind"], "LiteralExpr")
        self.assertEqual(data["value"], 42)

    def test_round_trip_binary(self):
        e = BinaryExpr(LiteralExpr(1), "+", LiteralExpr(2))
        serializer = ASTSerializer()
        data = serializer.to_dict(e)
        self.assertEqual(data["kind"], "BinaryExpr")
        self.assertEqual(data["left"]["kind"], "LiteralExpr")
        self.assertEqual(data["right"]["kind"], "LiteralExpr")

    def test_round_trip_program(self):
        p = Program(declarations=[
            VarDecl(name="x", type_annotation=NamedType(name="int"),
                    initializer=LiteralExpr(5))
        ])
        serializer = ASTSerializer()
        json_str = serializer.to_json(p)
        self.assertIn("Program", json_str)
        self.assertIn("VarDecl", json_str)

        deserializer = ASTDeserializer()
        p2 = deserializer.from_json(json_str)
        self.assertIsInstance(p2, Program)
        self.assertEqual(len(p2.declarations), 1)
        self.assertIsInstance(p2.declarations[0], VarDecl)

    def test_deserialize_literal(self):
        data = {"kind": "LiteralExpr", "node_id": 1,
                "location": {"file": "<input>", "start_line": 0, "start_column": 0,
                             "end_line": 0, "end_column": 0, "start_offset": 0, "end_offset": 0},
                "value": "hello", "token_type": None}
        d = ASTDeserializer()
        node = d.from_dict(data)
        self.assertIsInstance(node, LiteralExpr)
        self.assertEqual(node.value, "hello")

    def test_full_round_trip(self):
        p = Program(declarations=[
            VarDecl(name="a", type_annotation=NamedType(name="int"),
                    initializer=LiteralExpr(1)),
            VarDecl(name="b", type_annotation=NamedType(name="string"),
                    initializer=LiteralExpr("hello")),
            FunctionDecl(name="add", parameters=[
                Parameter(name="x", type_annotation=NamedType(name="int")),
                Parameter(name="y", type_annotation=NamedType(name="int")),
            ], return_type=NamedType(name="int"),
                body=BlockStmt(statements=[
                    ReturnStmt(value=BinaryExpr(
                        IdentifierExpr("x"), "+", IdentifierExpr("y")))
                ])),
        ])
        serializer = ASTSerializer()
        json_str = serializer.to_json(p)
        deserializer = ASTDeserializer()
        p2 = deserializer.from_json(json_str)
        self.assertEqual(len(p2.declarations), 3)
        self.assertEqual(p2.declarations[0].name, "a")
        self.assertEqual(p2.declarations[2].name, "add")


# ══════════════════════════════════════════════════════════════════
# Test: TextTreeVisualizer
# ══════════════════════════════════════════════════════════════════


class TestTextTreeVisualizer(unittest.TestCase):
    def test_simple_tree(self):
        viz = TextTreeVisualizer()
        expr = BinaryExpr(LiteralExpr(1), "+", LiteralExpr(2))
        output = viz.render(expr)
        self.assertIn("BinaryExpr", output)
        self.assertIn("LiteralExpr", output)
        self.assertIn("└──", output)

    def test_program_tree(self):
        viz = TextTreeVisualizer()
        p = Program(declarations=[
            VarDecl(name="x", type_annotation=None, initializer=LiteralExpr(1))
        ])
        output = viz.render(p)
        self.assertIn("Program", output)
        self.assertIn("VarDecl", output)

    def test_show_ids(self):
        viz = TextTreeVisualizer(show_ids=True)
        e = LiteralExpr(value=42)
        output = viz.render(e)
        self.assertIn(f"#{e.node_id}", output)


# ══════════════════════════════════════════════════════════════════
# Test: DOTVisualizer
# ══════════════════════════════════════════════════════════════════


class TestDOTVisualizer(unittest.TestCase):
    def test_dot_output(self):
        viz = DOTVisualizer()
        expr = BinaryExpr(LiteralExpr(1), "+", LiteralExpr(2))
        dot = viz.to_dot(expr)
        self.assertIn("digraph AST", dot)
        self.assertIn("BinaryExpr", dot)
        self.assertIn("LiteralExpr", dot)

    def test_dot_edges(self):
        viz = DOTVisualizer()
        expr = BinaryExpr(LiteralExpr(1), "+", LiteralExpr(2))
        dot = viz.to_dot(expr)
        self.assertIn("->", dot)


if __name__ == "__main__":
    unittest.main()
