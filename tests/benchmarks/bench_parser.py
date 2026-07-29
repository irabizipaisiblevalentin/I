"""
Parser Benchmark Suite

Performance benchmarks for the I language parser.
"""

import time
import statistics
from typing import List

from src.compiler.parser import parse


class BenchmarkResult:
    """Result of a single benchmark."""

    def __init__(
        self,
        name: str,
        times: List[float],
        stmts: int,
        chars: int,
    ) -> None:
        self.name = name
        self.times = times
        self.stmts = stmts
        self.chars = chars

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
    def stmts_per_sec(self) -> float:
        return self.stmts / (self.mean_ms / 1000) if self.mean_ms > 0 else 0

    def format(self) -> str:
        return (
            f"{self.name}:\n"
            f"  Mean: {self.mean_ms:.3f}ms | "
            f"Median: {self.median_ms:.3f}ms | "
            f"Stdev: {self.stdev_ms:.3f}ms\n"
            f"  Min: {self.min_ms:.3f}ms | "
            f"Max: {self.max_ms:.3f}ms\n"
            f"  Throughput: {self.stmts_per_sec:,.0f} stmts/s\n"
            f"  Statements: {self.stmts} | Chars: {self.chars}"
        )


def run_benchmark(
    name: str,
    source: str,
    iterations: int = 100,
    warmup: int = 10,
) -> BenchmarkResult:
    """Run a single benchmark."""
    for _ in range(warmup):
        ast, _ = parse(source)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        ast, _ = parse(source)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    final_ast, _ = parse(source)
    stmts = sum(len(s.statements) for s in [final_ast] if hasattr(s, 'statements'))

    return BenchmarkResult(
        name=name,
        times=times,
        stmts=stmts,
        chars=len(source),
    )


# ── Test Sources ────────────────────────────────────────────────

SIMPLE_SOURCE = """
shyira x = 42
shyira y = 3.14
shyira msg = "hello"
"""

FUNCTION_SOURCE = """
umurimo add(a, b) -> umubare kora
    subira a + b
iherezo

umurimo subtract(a, b) -> umubare kora
    subira a - b
iherezo

umurimo multiply(a, b) -> umubare kora
    subira a * b
iherezo
"""

IF_ELSE_SOURCE = """
niba x > 0 kora
    subira 1
cyangwa_niba x < 0 kora
    subira -1
cyangwa
    subira 0
iherezo
"""

LOOP_SOURCE = """
kuri i = 0 kugeza 100 kora
    shyira result = i * 2
    niba result > 50 kora
        subira result
    iherezo
iherezo
"""

CLASS_SOURCE = """
urwego Point kora
    kora(x : umubare, y : umubare) kora iherezo

    umurimo distance(other) -> umubare kora
        subira 0
    iherezo
iherezo
"""

EXPRESSION_SOURCE = """
shyira result = (a + b) * (c - d) / e % f
shyira complex = x ** 2 + y ** 2 <= 100 kandi z > 0
"""

LARGE_SOURCE = "\n".join(
    f"""
umurimo func{i}(a{i}, b{i}) -> umubare kora
    shyira result = a{i} + b{i} * {i}
    niba result > {i * 10} kora
        subira result
    cyangwa
        subira 0
    iherezo
    subira result
iherezo
"""
    for i in range(50)
)


def run_all_benchmarks() -> List[BenchmarkResult]:
    """Run all benchmarks."""
    benchmarks = [
        ("Simple Declarations", SIMPLE_SOURCE),
        ("Functions", FUNCTION_SOURCE),
        ("If/Elif/Else", IF_ELSE_SOURCE),
        ("Loops", LOOP_SOURCE),
        ("Class Definition", CLASS_SOURCE),
        ("Complex Expressions", EXPRESSION_SOURCE),
        ("Large Source (50 functions)", LARGE_SOURCE),
    ]

    results = []
    for name, source in benchmarks:
        result = run_benchmark(name, source, iterations=100, warmup=10)
        results.append(result)

    return results


def print_results(results: List[BenchmarkResult]) -> None:
    """Print benchmark results."""
    print("\n" + "=" * 70)
    print("I LANGUAGE PARSER BENCHMARK RESULTS")
    print("=" * 70)

    for result in results:
        print()
        print(result.format())

    print("\n" + "=" * 70)


if __name__ == "__main__":
    results = run_all_benchmarks()
    print_results(results)
