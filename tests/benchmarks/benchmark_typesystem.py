"""
Benchmark suite for the type system.

Measures throughput of core type operations:
- Type creation
- Type compatibility checks
- Type inference
- Constraint solving
- Full program type checking
"""

import statistics
import time

from compiler.ast.nodes import (
    BinaryExpr,
    BlockStmt,
    FunctionDecl,
    IdentifierExpr,
    LiteralExpr,
    NamedType,
    Parameter,
    Program,
    ReturnStmt,
    StructDecl,
    StructField,
    VarDecl,
)
from compiler.typesystem.checker import TypeChecker
from compiler.typesystem.constraints import ConstraintSolver, TypeVariable
from compiler.typesystem.context import TypeContext
from compiler.typesystem.diagnostics import TypeDiagnostics, TypeLocation
from compiler.typesystem.inference import InferenceEngine
from compiler.typesystem.types import (
    TYPE_BOOL,
    TYPE_FLOAT,
    TYPE_INT,
    TYPE_STRING,
    FloatType,
    IntType,
    common_type,
    is_compatible,
    is_strict_subtype,
    make_class_type,
    make_function,
    make_list,
    make_map,
    make_optional,
    make_tuple,
)


def bench(name, fn, iterations=1000):
    """Run a benchmark and print results."""
    # Warmup
    for _ in range(100):
        fn()

    # Timed runs
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        end = time.perf_counter()
        times.append((end - start) * 1_000_000)  # microseconds

    avg = statistics.mean(times)
    med = statistics.median(times)
    best = min(times)
    total = sum(times) / 1000  # ms

    print(f"  {name:40s} avg={avg:8.2f}us  median={med:8.2f}us  best={best:8.2f}us  total={total:8.2f}ms")


def bench_type_creation():
    print("\n--- Type Creation ---")
    bench("IntType()", lambda: IntType())
    bench("FloatType()", lambda: FloatType())
    bench("make_list(TYPE_INT)", lambda: make_list(TYPE_INT))
    bench("make_map(TYPE_STR,TYPE_INT)", lambda: make_map(TYPE_STRING, TYPE_INT))
    bench("make_tuple(3 types)", lambda: make_tuple(TYPE_INT, TYPE_FLOAT, TYPE_STRING))
    bench("make_optional(TYPE_INT)", lambda: make_optional(TYPE_INT))
    bench("make_function(2 params)", lambda: make_function([TYPE_INT, TYPE_STRING], TYPE_BOOL))
    bench("make_class_type('X')", lambda: make_class_type("X"))


def bench_type_operations():
    print("\n--- Type Operations ---")
    list_int = make_list(TYPE_INT)
    list_float = make_list(TYPE_FLOAT)
    make_list(TYPE_STRING)
    make_map(TYPE_STRING, TYPE_INT)

    bench("common_type(int,float)", lambda: common_type(TYPE_INT, TYPE_FLOAT))
    bench("common_type(list<int>,list<float>)", lambda: common_type(list_int, list_float))
    bench("is_compatible(int,float)", lambda: is_compatible(TYPE_INT, TYPE_FLOAT))
    bench("is_compatible(int,string)", lambda: is_compatible(TYPE_INT, TYPE_STRING))
    bench("is_strict_subtype(int,float)", lambda: is_strict_subtype(TYPE_INT, TYPE_FLOAT))


def bench_constraint_solving():
    print("\n--- Constraint Solving ---")
    solver = ConstraintSolver()
    t = TypeVariable("T")
    u = TypeVariable("U")
    solver.add_equality(t, TYPE_INT)
    solver.add_equality(u, TYPE_STRING)
    solver.solve()

    bench("equality constraint", lambda: (
        ConstraintSolver().add_equality(TypeVariable("T"), TYPE_INT).solve()
    ))

    chain_solver = ConstraintSolver()
    a = TypeVariable("A")
    b = TypeVariable("B")
    c = TypeVariable("C")
    chain_solver.add_equality(a, b)
    chain_solver.add_equality(b, c)
    chain_solver.add_equality(c, TYPE_FLOAT)
    chain_solver.solve()

    bench("chain resolution",
          lambda: chain_solver.resolve_type(a))


def bench_inference():
    print("\n--- Inference ---")
    ctx = TypeContext()
    diag = TypeDiagnostics()
    engine = InferenceEngine(ctx, diag)
    loc = TypeLocation("<bench>", 1, 1)

    bench("infer_literal(int)", lambda: engine.infer_literal(42))
    bench("infer_binary(int+int)", lambda: engine.infer_binary(TYPE_INT, "+", TYPE_INT, loc))
    bench("infer_binary(int+float)", lambda: engine.infer_binary(TYPE_INT, "+", TYPE_FLOAT, loc))


def bench_full_check():
    print("\n--- Full Type Checking ---")

    def _check_small_program():
        checker = TypeChecker()
        prog = Program(declarations=[
            VarDecl("x", NamedType("int"), LiteralExpr(42)),
            FunctionDecl(
                "add",
                [Parameter("a", NamedType("int")), Parameter("b", NamedType("int"))],
                NamedType("int"),
                BlockStmt([ReturnStmt(BinaryExpr(IdentifierExpr("a"), "+", IdentifierExpr("b")))]),
            ),
        ])
        checker.check(prog)
        return checker

    bench("small program (var + func)", _check_small_program)

    def _check_medium_program():
        checker = TypeChecker()
        decls = [
            StructDecl("Point", [StructField("x", NamedType("int")),
                                 StructField("y", NamedType("int"))], []),
            VarDecl("p", None, LiteralExpr(42)),
        ]
        for i in range(10):
            decls.append(VarDecl(f"x{i}", NamedType("int"), LiteralExpr(i)))
        prog = Program(declarations=decls)
        checker.check(prog)
        return checker

    bench("medium program (struct + 10 vars)", _check_medium_program)


if __name__ == "__main__":
    print("=" * 60)
    print("Type System Benchmarks")
    print("=" * 60)
    bench_type_creation()
    bench_type_operations()
    bench_constraint_solving()
    bench_inference()
    bench_full_check()
    print("\nDone.")
