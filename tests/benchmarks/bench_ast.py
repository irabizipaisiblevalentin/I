"""
AST Benchmarks for the I Programming Language

Performance benchmarks for AST construction, traversal, validation,
serialization, and visualization.
"""

import time
import statistics
from typing import Callable, List, Any

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from compiler.ast.nodes import (
    BinaryExpr,
    BlockStmt,
    CallExpr,
    ClassDecl,
    Expr,
    ForStmt,
    FunctionDecl,
    IdentifierExpr,
    IfStmt,
    LiteralExpr,
    NamedType,
    Parameter,
    Program,
    ReturnStmt,
    SourceLocation,
    Stmt,
    VarDecl,
    WhileStmt,
)
from compiler.ast.visitor import ASTWalker, ASTTransformer, PrettyPrinter, DebugPrinter
from compiler.ast.validator import validate_ast
from compiler.ast.serializer import ASTSerializer, ASTDeserializer
from compiler.ast.visualizer import TextTreeVisualizer, DOTVisualizer


# ══════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════


def bench(label: str, func: Callable, iterations: int = 1000) -> None:
    """Run a benchmark and print results."""
    times: List[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append(end - start)

    avg = statistics.mean(times)
    med = statistics.median(times)
    p95 = sorted(times)[int(len(times) * 0.95)]

    print(f"  {label}:")
    print(f"    avg={avg*1000:.3f}ms  median={med*1000:.3f}ms  p95={p95*1000:.3f}ms  (n={iterations})")


def build_small_ast() -> Program:
    """Build a small AST: var x = 1 + 2"""
    return Program(declarations=[
        VarDecl(
            name="x",
            type_annotation=None,
            initializer=BinaryExpr(
                left=LiteralExpr(value=1),
                operator="+",
                right=LiteralExpr(value=2),
            ),
        )
    ])


def build_medium_ast() -> Program:
    """Build a medium AST: function with loop and conditionals."""
    params = [Parameter(name="n", type_annotation=NamedType(name="int"))]
    body_stmts: List[Stmt] = []
    var_sum = VarDecl(name="sum", type_annotation=NamedType(name="int"),
                      initializer=LiteralExpr(value=0))
    body_stmts.append(var_sum)

    loop_body = BlockStmt(statements=[
        VarDecl(name="temp", type_annotation=None,
                initializer=BinaryExpr(IdentifierExpr("sum"), "+", IdentifierExpr("i"))),
    ])
    for_stmt = ForStmt(variable="i", start=LiteralExpr(0),
                       end=IdentifierExpr("n"), step=LiteralExpr(1),
                       body=loop_body)
    body_stmts.append(for_stmt)

    if_stmt = IfStmt(
        condition=BinaryExpr(IdentifierExpr("sum"), ">", LiteralExpr(100)),
        then_branch=BlockStmt(statements=[ReturnStmt(value=IdentifierExpr("sum"))]),
        elif_branches=[],
        else_branch=BlockStmt(statements=[ReturnStmt(value=LiteralExpr(0))]),
    )
    body_stmts.append(if_stmt)

    fn = FunctionDecl(
        name="compute",
        parameters=params,
        return_type=NamedType(name="int"),
        body=BlockStmt(statements=body_stmts),
    )

    decls: list = [fn]
    for i in range(20):
        decls.append(VarDecl(name=f"v{i}", type_annotation=None,
                             initializer=LiteralExpr(value=i)))
    return Program(declarations=decls)


def build_large_ast() -> Program:
    """Build a large AST: multiple functions, structs, classes."""
    decls: list = []
    for i in range(50):
        params = [Parameter(name=f"p{j}", type_annotation=NamedType(name="int"))
                  for j in range(5)]
        body = BlockStmt(statements=[
            VarDecl(name=f"x{i}", type_annotation=None,
                    initializer=LiteralExpr(value=i)),
            ReturnStmt(value=IdentifierExpr(f"x{i}")),
        ])
        decls.append(FunctionDecl(
            name=f"func{i}",
            parameters=params,
            return_type=NamedType(name="int"),
            body=body,
        ))

    for i in range(10):
        fields = [StructField(name=f"f{j}", type_annotation=NamedType(name="int"))
                  for j in range(10)]
        decls.append(ClassDecl(
            name=f"Class{i}",
            parent="Base" if i % 2 == 0 else None,
            members=[VarDecl(name=f"field{j}", type_annotation=NamedType(name="int"),
                             initializer=LiteralExpr(value=j))
                     for j in range(5)],
        ))

    return Program(declarations=decls)


# ══════════════════════════════════════════════════════════════════
# Benchmarks
# ══════════════════════════════════════════════════════════════════


def bench_ast_construction() -> None:
    print("\n=== AST Construction ===")

    bench("Small AST (3 nodes)", build_small_ast, iterations=10000)
    bench("Medium AST (~30 nodes)", build_medium_ast, iterations=1000)
    bench("Large AST (~300 nodes)", build_large_ast, iterations=100)


def bench_ast_walking() -> None:
    print("\n=== AST Walking ===")
    small = build_small_ast()
    medium = build_medium_ast()
    large = build_large_ast()

    walker = ASTWalker()
    count_nodes = lambda: len(walker.walk(small))

    def count_medium():
        return len(walker.walk(medium))

    def count_large():
        return len(walker.walk(large))

    bench("Walk small", count_nodes, iterations=10000)
    bench("Walk medium", count_medium, iterations=1000)
    bench("Walk large", count_large, iterations=100)


def bench_ast_transformation() -> None:
    print("\n=== AST Transformation ===")
    medium = build_medium_ast()
    large = build_large_ast()

    class IdentityTransform(ASTTransformer):
        pass

    transformer = IdentityTransform()

    bench("Transform medium (identity)", lambda: transformer.transform(medium), iterations=1000)
    bench("Transform large (identity)", lambda: transformer.transform(large), iterations=100)


def bench_ast_validation() -> None:
    print("\n=== AST Validation ===")
    small = build_small_ast()
    medium = build_medium_ast()
    large = build_large_ast()

    bench("Validate small", lambda: validate_ast(small), iterations=10000)
    bench("Validate medium", lambda: validate_ast(medium), iterations=1000)
    bench("Validate large", lambda: validate_ast(large), iterations=100)


def bench_ast_serialization() -> None:
    print("\n=== AST Serialization ===")
    small = build_small_ast()
    medium = build_medium_ast()
    large = build_large_ast()

    serializer = ASTSerializer()
    deserializer = ASTDeserializer()

    json_small = serializer.to_json(small)
    json_medium = serializer.to_json(medium)
    json_large = serializer.to_json(large)

    bench("Serialize small", lambda: serializer.to_json(small), iterations=10000)
    bench("Serialize medium", lambda: serializer.to_json(medium), iterations=1000)
    bench("Serialize large", lambda: serializer.to_json(large), iterations=100)

    bench("Deserialize small", lambda: deserializer.from_json(json_small), iterations=10000)
    bench("Deserialize medium", lambda: deserializer.from_json(json_medium), iterations=1000)
    bench("Deserialize large", lambda: deserializer.from_json(json_large), iterations=100)

    bench("Round-trip small", lambda: deserializer.from_json(serializer.to_json(small)),
          iterations=10000)


def bench_ast_visualization() -> None:
    print("\n=== AST Visualization ===")
    small = build_small_ast()
    medium = build_medium_ast()

    text_viz = TextTreeVisualizer()
    dot_viz = DOTVisualizer()
    pretty = PrettyPrinter()
    debug = DebugPrinter()

    bench("TextTree small", lambda: text_viz.render(small), iterations=10000)
    bench("TextTree medium", lambda: text_viz.render(medium), iterations=1000)
    bench("DOT small", lambda: dot_viz.to_dot(small), iterations=10000)
    bench("DOT medium", lambda: dot_viz.to_dot(medium), iterations=1000)
    bench("PrettyPrinter small", lambda: pretty.print(small), iterations=10000)
    bench("PrettyPrinter medium", lambda: pretty.print(medium), iterations=1000)
    bench("DebugPrinter small", lambda: debug.print(small), iterations=10000)
    bench("DebugPrinter medium", lambda: debug.print(medium), iterations=1000)


def bench_node_creation() -> None:
    print("\n=== Individual Node Creation ===")
    loc = SourceLocation("test.i", 1, 1, 1, 10)

    bench("LiteralExpr", lambda: LiteralExpr(value=42, location=loc), iterations=100000)
    bench("IdentifierExpr", lambda: IdentifierExpr(name="x", location=loc), iterations=100000)
    bench("BinaryExpr", lambda: BinaryExpr(LiteralExpr(1), "+", LiteralExpr(2)),
          iterations=100000)
    bench("VarDecl", lambda: VarDecl(name="x", type_annotation=None,
                                     initializer=LiteralExpr(1)),
          iterations=100000)
    bench("FunctionDecl", lambda: FunctionDecl(
        name="f", parameters=[Parameter(name="a")], return_type=None,
        body=BlockStmt(statements=[ReturnStmt(value=LiteralExpr(0))])),
        iterations=50000)


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    print("I Programming Language — AST Benchmarks")
    print("=" * 50)

    bench_node_creation()
    bench_ast_construction()
    bench_ast_walking()
    bench_ast_transformation()
    bench_ast_validation()
    bench_ast_serialization()
    bench_ast_visualization()

    print("\n" + "=" * 50)
    print("Done.")
