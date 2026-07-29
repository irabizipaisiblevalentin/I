"""
Lexer Benchmark Suite

Performance benchmarks for the I language lexer.
"""

import time
import statistics
from typing import Callable, List

from src.compiler.lexer import Lexer, tokenize


class BenchmarkResult:
    """Result of a single benchmark."""

    def __init__(
        self,
        name: str,
        times: List[float],
        iterations: int,
        tokens: int,
        chars: int,
    ) -> None:
        self.name = name
        self.times = times
        self.iterations = iterations
        self.tokens = tokens
        self.chars = chars

    @property
    def mean_ms(self) -> float:
        return statistics.mean(self.times) * 1000

    @property
    def median_ms(self) -> float:
        return statistics.median(self.times) * 1000

    @property
    def stdev_ms(self) -> float:
        return statistics.stdev(self.times) * 1000 if len(self.times) > 1 else 0

    @property
    def min_ms(self) -> float:
        return min(self.times) * 1000

    @property
    def max_ms(self) -> float:
        return max(self.times) * 1000

    @property
    def chars_per_sec(self) -> float:
        if self.mean_ms == 0:
            return 0
        return self.chars / (self.mean_ms / 1000)

    @property
    def tokens_per_sec(self) -> float:
        if self.mean_ms == 0:
            return 0
        return self.tokens / (self.mean_ms / 1000)

    def format(self) -> str:
        return (
            f"{self.name}:\n"
            f"  Mean: {self.mean_ms:.3f}ms | "
            f"Median: {self.median_ms:.3f}ms | "
            f"Stdev: {self.stdev_ms:.3f}ms\n"
            f"  Min: {self.min_ms:.3f}ms | "
            f"Max: {self.max_ms:.3f}ms\n"
            f"  Throughput: {self.chars_per_sec:,.0f} chars/s | "
            f"{self.tokens_per_sec:,.0f} tokens/s\n"
            f"  Tokens: {self.tokens:,} | "
            f"Chars: {self.chars:,}"
        )


def run_benchmark(
    name: str,
    source: str,
    iterations: int = 100,
    warmup: int = 10,
) -> BenchmarkResult:
    """Run a single benchmark."""
    # Warmup
    for _ in range(warmup):
        tokens, _ = tokenize(source)

    # Benchmark
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        tokens, _ = tokenize(source)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    final_tokens, _ = tokenize(source)

    return BenchmarkResult(
        name=name,
        times=times,
        iterations=iterations,
        tokens=len(final_tokens),
        chars=len(source),
    )


# ── Test Sources ────────────────────────────────────────────────

SIMPLE_SOURCE = """
shyira x = 42
shyira y = 3.14
shyira msg = "hello world"
"""

KEYWORD_HEAVY_SOURCE = """
niba x > 0 kora
    subira x
cyangwa
    subira 0
iherezo

kuri i = 0 kugeza 10 kora
    # loop body
iherezo

umurimo soma(n) kora
    subira n * 2
iherezo
"""

IDENTIFIER_HEAVY_SOURCE = """
shyira variableAlpha = 1
shyira variableBeta = 2
shyira variableGamma = 3
shyira variableDelta = 4
shyira variableEpsilon = 5
"""

STRING_HEAVY_SOURCE = """
shyira s1 = "hello"
shyira s2 = "world"
shyira s3 = "foo\\nbar\\tbaz"
shyira s4 = "unicode: \\u0041"
"""

NUMBER_HEAVY_SOURCE = """
shyira n1 = 42
shyira n2 = 0xFF
shyira n3 = 0o77
shyira n4 = 0b1010
shyira n5 = 3.14
shyira n6 = 1e10
shyira n7 = 1_000_000
"""

OPERATOR_HEAVY_SOURCE = """
x = a + b - c * d / e % f
y = (a > b) && (c < d) || (e == f)
z = a << 2 >> 3 >>> 1
w = a & b | c ^ ~d
"""

COMMENT_HEAVY_SOURCE = """
# This is a comment
# This is another comment
42 # inline comment
#= This is a
multi-line comment
=#
84 #= nested #= comments =# =#
"""

LARGE_SOURCE = "\n".join(f"shyira x{i} = {i} + {i*2}" for i in range(500))

UNICODE_SOURCE = "\n".join(
    f"shyira igiciro{i} = {i}" for i in range(100)
)


def run_all_benchmarks() -> List[BenchmarkResult]:
    """Run all benchmarks."""
    benchmarks = [
        ("Simple Source", SIMPLE_SOURCE),
        ("Keyword-Heavy", KEYWORD_HEAVY_SOURCE),
        ("Identifier-Heavy", IDENTIFIER_HEAVY_SOURCE),
        ("String-Heavy", STRING_HEAVY_SOURCE),
        ("Number-Heavy", NUMBER_HEAVY_SOURCE),
        ("Operator-Heavy", OPERATOR_HEAVY_SOURCE),
        ("Comment-Heavy", COMMENT_HEAVY_SOURCE),
        ("Large Source (500 lines)", LARGE_SOURCE),
        ("Unicode Source", UNICODE_SOURCE),
    ]

    results = []
    for name, source in benchmarks:
        result = run_benchmark(name, source, iterations=100, warmup=10)
        results.append(result)

    return results


def print_results(results: List[BenchmarkResult]) -> None:
    """Print benchmark results."""
    print("\n" + "=" * 70)
    print("I LANGUAGE LEXER BENCHMARK RESULTS")
    print("=" * 70)

    for result in results:
        print()
        print(result.format())

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_chars = sum(r.chars for r in results)
    total_time = sum(r.mean_ms for r in results)
    avg_throughput = total_chars / (total_time / 1000) if total_time > 0 else 0

    print(f"\nAverage throughput: {avg_throughput:,.0f} chars/second")
    print(f"Total benchmark time: {total_time:.3f}ms")


if __name__ == "__main__":
    results = run_all_benchmarks()
    print_results(results)
