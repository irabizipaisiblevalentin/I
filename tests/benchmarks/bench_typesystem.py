"""
Type System Benchmark Suite

Performance benchmarks for the I language type system components.
"""

import sys
import os
import time
import statistics
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from compiler.typesystem.types import (
    TypeKind, TYPE_INT, TYPE_FLOAT, TYPE_STRING, TYPE_BOOL, TYPE_NONE,
    ClassType, ListType, MapType, FunctionType, GenericType,
    OptionalType, TypeVariable, SetType, RangeType, common_type,
)
from compiler.typesystem.registry import TypeRegistry, TypeDefinition
from compiler.typesystem.constraints import ConstraintSolver, ConstraintKind, Substitution
from compiler.typesystem.generics import GenericEngine, GenericParamDef
from compiler.typesystem.compiletime import CompileTimeEvaluator
from compiler.typesystem.environment import TypeEnvironment
from compiler.typesystem.diagnostics import (
    TypeDiagnostics, TypeErrorCode, TypeSeverity, TypeLocation, TypeDiagnostic,
)
from compiler.typesystem.traits import (
    TraitResolver, TraitDefinition, InterfaceDefinition,
)
from compiler.typesystem.database import TypeDatabase


class BenchmarkResult:
    """Result of a single benchmark."""

    def __init__(self, name: str, times: List[float], ops: int = 1) -> None:
        self.name = name
        self.times = times
        self.ops = ops

    @property
    def mean_ms(self) -> float:
        return statistics.mean(self.times) * 1000

    @property
    def median_ms(self) -> float:
        return statistics.median(self.times) * 1000

    @property
    def min_ms(self) -> float:
        return min(self.times) * 1000

    @property
    def max_ms(self) -> float:
        return max(self.times) * 1000

    @property
    def stdev_ms(self) -> float:
        return statistics.stdev(self.times) * 1000 if len(self.times) > 1 else 0

    @property
    def ops_per_sec(self) -> float:
        return self.ops / (self.mean_ms / 1000) if self.mean_ms > 0 else 0

    def format(self) -> str:
        return (
            f"{self.name}:\n"
            f"  Mean: {self.mean_ms:.3f}ms | "
            f"Median: {self.median_ms:.3f}ms | "
            f"Stdev: {self.stdev_ms:.3f}ms\n"
            f"  Min: {self.min_ms:.3f}ms | "
            f"Max: {self.max_ms:.3f}ms\n"
            f"  Throughput: {self.ops_per_sec:,.0f} ops/s"
        )


# ── Benchmarks ────────────────────────────────────────────────────


def bench_type_creation(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: creating type objects."""
    for _ in range(warmup):
        t1 = ClassType("Point")
        t2 = ListType(TYPE_INT)
        t3 = MapType(TYPE_STRING, TYPE_INT)
        t4 = FunctionType((TYPE_INT, TYPE_STRING), TYPE_BOOL)
        t5 = OptionalType(TYPE_INT)
        t6 = TypeVariable("T")

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(100):
            t1 = ClassType("Point")
            t2 = ListType(TYPE_INT)
            t3 = MapType(TYPE_STRING, TYPE_INT)
            t4 = FunctionType((TYPE_INT, TYPE_STRING), TYPE_BOOL)
            t5 = OptionalType(TYPE_INT)
            t6 = TypeVariable("T")
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Type Creation", times, iterations * 100)


def bench_type_equality(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: type equality checks."""
    types_a = [TYPE_INT, TYPE_FLOAT, TYPE_STRING, TYPE_BOOL, ClassType("A"),
               ListType(TYPE_INT), MapType(TYPE_STRING, TYPE_INT)]
    types_b = [TYPE_INT, TYPE_FLOAT, TYPE_STRING, TYPE_BOOL, ClassType("A"),
               ListType(TYPE_INT), MapType(TYPE_STRING, TYPE_INT)]

    for _ in range(warmup):
        for a in types_a:
            for b in types_b:
                _ = a == b

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(1000):
            for a in types_a:
                for b in types_b:
                    _ = a == b
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Type Equality", times, iterations * 1000 * 49)


def bench_subtype_check(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: subtype checks."""
    opt_int = OptionalType(TYPE_INT)
    opt_str = OptionalType(TYPE_STRING)
    list_int = ListType(TYPE_INT)
    list_float = ListType(TYPE_FLOAT)
    func = FunctionType((TYPE_INT,), TYPE_STRING)

    pairs = [
        (TYPE_INT, TYPE_INT),
        (TYPE_INT, TYPE_FLOAT),
        (TYPE_NONE, opt_int),
        (TYPE_INT, opt_int),
        (TYPE_STRING, opt_str),
        (list_int, list_int),
        (list_int, list_float),
        (func, FunctionType((TYPE_INT,), TYPE_STRING)),
    ]

    for _ in range(warmup):
        for a, b in pairs:
            _ = a.is_subtype_of(b)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(1000):
            for a, b in pairs:
                _ = a.is_subtype_of(b)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Subtype Check", times, iterations * 1000 * len(pairs))


def bench_registry_lookup(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: registry type lookup."""
    reg = TypeRegistry()

    for _ in range(warmup):
        for _ in range(100):
            reg.get("int")
            reg.get("string")
            reg.get("list")

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(10000):
            reg.get("int")
            reg.get("string")
            reg.get("list")
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Registry Lookup", times, iterations * 10000 * 3)


def bench_registry_register(iterations: int = 500, warmup: int = 50) -> BenchmarkResult:
    """Benchmark: registering new types."""
    for _ in range(warmup):
        r = TypeRegistry()
        for i in range(100):
            r.register(TypeDefinition(
                f"Type{i}", TypeKind.CLASS, ClassType(f"Type{i}"),
            ))

    times = []
    for _ in range(iterations):
        r = TypeRegistry()
        start = time.perf_counter()
        for i in range(100):
            r.register(TypeDefinition(
                f"Type{i}", TypeKind.CLASS, ClassType(f"Type{i}"),
            ))
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Registry Register (100 types)", times, iterations)


def bench_constraint_solving(iterations: int = 500, warmup: int = 50) -> BenchmarkResult:
    """Benchmark: constraint solver with multiple constraints."""
    for _ in range(warmup):
        solver = ConstraintSolver()
        t1 = TypeVariable("T1")
        t2 = TypeVariable("T2")
        t3 = TypeVariable("T3")
        solver.add_equality(t1, TYPE_INT)
        solver.add_equality(t2, TYPE_STRING)
        solver.add_equality(t3, t1)
        solver.add_assignable(t2, t3)
        solver.solve()

    times = []
    for _ in range(iterations):
        solver = ConstraintSolver()
        t1 = TypeVariable("T1")
        t2 = TypeVariable("T2")
        t3 = TypeVariable("T3")
        solver.add_equality(t1, TYPE_INT)
        solver.add_equality(t2, TYPE_STRING)
        solver.add_equality(t3, t1)
        solver.add_assignable(t2, t3)
        start = time.perf_counter()
        for _ in range(500):
            solver.solve()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Constraint Solving", times, iterations * 500)


def bench_compiletime_eval(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: compile-time expression evaluation."""
    from compiler.typesystem.compiletime import ConstValue
    from compiler.typesystem.diagnostics import TypeLocation

    evaluator = CompileTimeEvaluator(TypeDiagnostics())
    loc = TypeLocation("<bench>", 0, 0, 0, 0)

    def _add(l, r): return evaluator.eval_add(l, r, loc)
    def _mul(l, r): return evaluator.eval_multiply(l, r, loc)
    def _div(l, r): return evaluator.eval_divide(l, r, loc)
    def _pow(l, r): return evaluator.eval_power(l, r, loc)
    def _mod(l, r): return evaluator.eval_modulo(l, r, loc)

    exprs = [
        (ConstValue.int_val(10), _add, ConstValue.int_val(20)),
        (ConstValue.int_val(100), _mul, ConstValue.int_val(5)),
        (ConstValue.int_val(10), _div, ConstValue.int_val(3)),
        (ConstValue.int_val(2), _pow, ConstValue.int_val(10)),
        (ConstValue.int_val(15), _mod, ConstValue.int_val(4)),
    ]

    for _ in range(warmup):
        for left, op_fn, right in exprs:
            op_fn(left, right)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(1000):
            for left, op_fn, right in exprs:
                op_fn(left, right)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Compile-Time Evaluation", times, iterations * 1000 * 5)


def bench_environment_scope(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: environment scope push/pop/lookup."""
    env = TypeEnvironment()
    for i in range(20):
        env.define(f"x{i}", TYPE_INT)

    for _ in range(warmup):
        for _ in range(50):
            env.push("<scope>")
            for i in range(20):
                env.define(f"y{i}", TYPE_STRING)
            for i in range(20):
                env.lookup(f"x{i}")
            env.pop()

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(50):
            env.push("<scope>")
            for i in range(20):
                env.define(f"y{i}", TYPE_STRING)
            for i in range(20):
                env.lookup(f"x{i}")
            env.pop()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Environment Scope Push/Pop/Lookup", times, iterations * 50)


def bench_generic_instantiation(iterations: int = 500, warmup: int = 50) -> BenchmarkResult:
    """Benchmark: generic function instantiation."""
    reg = TypeRegistry()
    engine = GenericEngine(reg)
    t_var = TypeVariable("T")
    u_var = TypeVariable("U")
    swap_type = FunctionType((t_var, u_var), t_var)

    type_pairs = [
        [TYPE_INT, TYPE_STRING],
        [TYPE_FLOAT, TYPE_BOOL],
        [TYPE_STRING, TYPE_INT],
    ]

    for _ in range(warmup):
        for args in type_pairs:
            engine.instantiate_generic_function(swap_type, args, [t_var, u_var])

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(1000):
            for args in type_pairs:
                engine.instantiate_generic_function(swap_type, args, [t_var, u_var])
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Generic Instantiation", times, iterations * 1000 * 3)


# ── Enhanced Type System Benchmarks ───────────────────────────────


def bench_common_type_optimal(iterations: int = 100, warmup: int = 10) -> BenchmarkResult:
    """Benchmark: enhanced common_type with Optional, List, Map combinations."""
    opt_int = OptionalType(TYPE_INT)
    opt_str = OptionalType(TYPE_STRING)
    opt_float = OptionalType(TYPE_FLOAT)
    list_int = ListType(TYPE_INT)
    list_str = ListType(TYPE_STRING)
    list_float = ListType(TYPE_FLOAT)
    map_si = MapType(TYPE_STRING, TYPE_INT)
    map_sf = MapType(TYPE_STRING, TYPE_FLOAT)
    map_ss = MapType(TYPE_STRING, TYPE_STRING)
    map_is = MapType(TYPE_INT, TYPE_STRING)

    pairs = [
        (TYPE_INT, opt_int),
        (TYPE_NONE, opt_str),
        (opt_int, opt_float),
        (TYPE_INT, TYPE_FLOAT),
        (TYPE_INT, TYPE_STRING),
        (list_int, list_str),
        (list_int, list_float),
        (list_str, list_int),
        (map_si, map_sf),
        (map_si, map_ss),
        (map_si, map_is),
        (opt_int, list_int),
        (TYPE_BOOL, TYPE_INT),
    ]

    for _ in range(warmup):
        for a, b in pairs:
            common_type(a, b)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(100):
            for a, b in pairs:
                common_type(a, b)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Common Type (Enhanced)", times, iterations * 100 * len(pairs))


def bench_registry_query_methods(iterations: int = 100, warmup: int = 10) -> BenchmarkResult:
    """Benchmark: get_trait_names, get_interface_names, get_class_names, get_inheritance_chain."""
    reg = TypeRegistry()
    for i in range(30):
        reg.register(TypeDefinition(
            f"Class{i}", TypeKind.CLASS, ClassType(f"Class{i}"),
            parent_name=f"Class{i - 1}" if i > 0 else None,
        ))
    for i in range(15):
        reg.register(TypeDefinition(
            f"Trait{i}", TypeKind.TRAIT, ClassType(f"Trait{i}"),
        ))
    for i in range(10):
        reg.register(TypeDefinition(
            f"Interface{i}", TypeKind.INTERFACE, ClassType(f"Interface{i}"),
        ))

    for _ in range(warmup):
        reg.get_trait_names()
        reg.get_interface_names()
        reg.get_class_names()
        reg.get_inheritance_chain("Class29")

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(100):
            reg.get_trait_names()
            reg.get_interface_names()
            reg.get_class_names()
            reg.get_inheritance_chain("Class29")
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Registry Query Methods", times, iterations * 100 * 4)


def bench_constraint_stats(iterations: int = 100, warmup: int = 10) -> BenchmarkResult:
    """Benchmark: get_constraint_stats, get_all_resolved_types via ConstraintSolver."""
    solver = ConstraintSolver()
    vars_list = [TypeVariable(f"T{i}") for i in range(20)]
    for i, tv in enumerate(vars_list):
        solver.add_equality(tv, [TYPE_INT, TYPE_STRING, TYPE_FLOAT, TYPE_BOOL][i % 4])
    for i in range(len(vars_list) - 1):
        solver.add_equality(vars_list[i], vars_list[i + 1])
    solver.solve()

    for _ in range(warmup):
        solver.get_all_resolved_types()

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(100):
            solver.get_all_resolved_types()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Constraint Stats & Resolved Types", times, iterations * 100)


def bench_environment_snapshots(iterations: int = 100, warmup: int = 10) -> BenchmarkResult:
    """Benchmark: snapshot() and reset_to_global() on TypeEnvironment."""
    env = TypeEnvironment()
    for i in range(50):
        env.define(f"x{i}", TYPE_INT)
    env.push("<scope>")
    for i in range(50):
        env.define(f"y{i}", TYPE_STRING)

    for _ in range(warmup):
        snap = env.snapshot()
        env.reset_to_global()
        for i in range(50):
            env.define(f"x{i}", TYPE_INT)
        env.push("<scope>")
        for i in range(50):
            env.define(f"y{i}", TYPE_STRING)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(50):
            snap = env.snapshot()
            env.reset_to_global()
            for i in range(50):
                env.define(f"x{i}", TYPE_INT)
            env.push("<scope>")
            for i in range(50):
                env.define(f"y{i}", TYPE_STRING)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Environment Snapshots", times, iterations * 50)


def bench_substitution_resolve(iterations: int = 100, warmup: int = 10) -> BenchmarkResult:
    """Benchmark: Substitution.resolve() with Set and Range types."""
    sub = Substitution()
    t_a = TypeVariable("A")
    t_b = TypeVariable("B")
    t_c = TypeVariable("C")
    t_d = TypeVariable("D")
    sub.bind("A", TYPE_INT)
    sub.bind("B", TYPE_STRING)
    sub.bind("C", TYPE_FLOAT)
    sub.bind("D", TYPE_BOOL)

    complex_types = [
        SetType(TYPE_INT),
        SetType(t_a),
        RangeType(TYPE_INT),
        RangeType(t_b),
        OptionalType(SetType(t_c)),
        ListType(RangeType(t_d)),
        MapType(t_a, SetType(t_b)),
        SetType(SetType(t_c)),
        RangeType(RangeType(t_d)),
        FunctionType((SetType(t_a), RangeType(t_b)), SetType(t_c)),
    ]

    for _ in range(warmup):
        for t in complex_types:
            sub.resolve(t)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(100):
            for t in complex_types:
                sub.resolve(t)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Substitution Resolve (Set/Range)", times, iterations * 100 * len(complex_types))


def bench_trait_transitive_closure(iterations: int = 100, warmup: int = 10) -> BenchmarkResult:
    """Benchmark: get_super_traits() with transitive closure."""
    reg = TypeRegistry()
    diags = TypeDiagnostics()
    resolver = TraitResolver(reg, diags)

    resolver.register_trait(TraitDefinition(
        name="Comparable",
        required_methods={"compare": None},
        super_traits=[],
    ))
    resolver.register_trait(TraitDefinition(
        name="Ordered",
        required_methods={"lt": None},
        super_traits=["Comparable"],
    ))
    resolver.register_trait(TraitDefinition(
        name="Serializable",
        required_methods={"serialize": None},
        super_traits=[],
    ))
    resolver.register_trait(TraitDefinition(
        name="Displayable",
        required_methods={"display": None},
        super_traits=["Comparable"],
    ))
    resolver.register_trait(TraitDefinition(
        name="FullComparable",
        required_methods={"full_compare": None},
        super_traits=["Ordered", "Displayable", "Serializable"],
    ))
    resolver.register_trait(TraitDefinition(
        name="UltraComparable",
        required_methods={"ultra": None},
        super_traits=["FullComparable", "Ordered"],
    ))

    for _ in range(warmup):
        resolver.get_super_traits("UltraComparable")
        resolver.get_super_traits("FullComparable")
        resolver.get_super_traits("Ordered")
        resolver.get_super_traits("Comparable")

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(100):
            resolver.get_super_traits("UltraComparable")
            resolver.get_super_traits("FullComparable")
            resolver.get_super_traits("Ordered")
            resolver.get_super_traits("Comparable")
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Trait Transitive Closure", times, iterations * 100 * 4)


def bench_compiletime_string_ops(iterations: int = 100, warmup: int = 10) -> BenchmarkResult:
    """Benchmark: eval_string_equal, eval_string_not_equal, eval_string_concat."""
    from compiler.typesystem.compiletime import ConstValue

    evaluator = CompileTimeEvaluator(TypeDiagnostics())
    pairs = [
        (ConstValue.string_val("hello"), ConstValue.string_val("world")),
        (ConstValue.string_val("abc"), ConstValue.string_val("abc")),
        (ConstValue.string_val("foo"), ConstValue.string_val("bar")),
        (ConstValue.string_val(""), ConstValue.string_val("")),
        (ConstValue.string_val("test"), ConstValue.string_val("value")),
    ]

    for _ in range(warmup):
        for left, right in pairs:
            evaluator.eval_string_equal(left, right)
            evaluator.eval_string_not_equal(left, right)
            evaluator.eval_string_concat(left, right)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(100):
            for left, right in pairs:
                evaluator.eval_string_equal(left, right)
                evaluator.eval_string_not_equal(left, right)
                evaluator.eval_string_concat(left, right)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Compile-Time String Ops", times, iterations * 100 * len(pairs) * 3)


def bench_diagnostics_filtering(iterations: int = 100, warmup: int = 10) -> BenchmarkResult:
    """Benchmark: filter_by_severity, filter_by_code, filter_by_file."""
    diags = TypeDiagnostics()
    severity_cycle = [TypeSeverity.ERROR, TypeSeverity.WARNING, TypeSeverity.INFO, TypeSeverity.HINT]
    code_cycle = [
        TypeErrorCode.TYP100_TYPE_MISMATCH,
        TypeErrorCode.TYP103_ARGUMENT_TYPE_MISMATCH,
        TypeErrorCode.TYP302_CANNOT_INFER_GENERIC,
        TypeErrorCode.TYP350_MISSING_TRAIT_METHOD,
    ]
    files_cycle = ["main.i", "utils.i", "types.i"]

    for i in range(120):
        diags._diagnostics.append(TypeDiagnostic(
            code=code_cycle[i % len(code_cycle)],
            severity=severity_cycle[i % len(severity_cycle)],
            location=TypeLocation(
                file=files_cycle[i % len(files_cycle)],
                line=i + 1, column=1,
                end_line=i + 1, end_column=10,
            ),
            message_rw=f"Umurongo {i}",
            message_en=f"Error line {i}",
            expected_type="int" if i % 2 == 0 else "string",
            actual_type="string" if i % 2 == 0 else "int",
        ))

    for _ in range(warmup):
        diags.filter_by_severity(TypeSeverity.ERROR)
        diags.filter_by_severity(TypeSeverity.WARNING)
        diags.filter_by_code(TypeErrorCode.TYP100_TYPE_MISMATCH)
        diags.filter_by_code(TypeErrorCode.TYP350_MISSING_TRAIT_METHOD)
        diags.filter_by_file("main.i")
        diags.filter_by_file("utils.i")

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(100):
            diags.filter_by_severity(TypeSeverity.ERROR)
            diags.filter_by_severity(TypeSeverity.WARNING)
            diags.filter_by_code(TypeErrorCode.TYP100_TYPE_MISMATCH)
            diags.filter_by_code(TypeErrorCode.TYP350_MISSING_TRAIT_METHOD)
            diags.filter_by_file("main.i")
            diags.filter_by_file("utils.i")
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Diagnostics Filtering", times, iterations * 100 * 6)


# ── Run All ────────────────────────────────────────────────────────


def run_all_benchmarks() -> List[BenchmarkResult]:
    """Run all type system benchmarks."""
    benchmarks = [
        bench_type_creation,
        bench_type_equality,
        bench_subtype_check,
        bench_registry_lookup,
        bench_registry_register,
        bench_constraint_solving,
        bench_compiletime_eval,
        bench_environment_scope,
        bench_generic_instantiation,
        bench_common_type_optimal,
        bench_registry_query_methods,
        bench_constraint_stats,
        bench_environment_snapshots,
        bench_substitution_resolve,
        bench_trait_transitive_closure,
        bench_compiletime_string_ops,
        bench_diagnostics_filtering,
    ]

    results = []
    for bench_fn in benchmarks:
        print(f"  Running {bench_fn.__doc__.strip().split(':')[0]}...")
        result = bench_fn()
        results.append(result)

    return results


def print_results(results: List[BenchmarkResult]) -> None:
    """Print benchmark results."""
    print("\n" + "=" * 70)
    print("I LANGUAGE TYPE SYSTEM BENCHMARK RESULTS")
    print("=" * 70)

    for result in results:
        print()
        print(result.format())

    print("\n" + "=" * 70)


if __name__ == "__main__":
    results = run_all_benchmarks()
    print_results(results)
