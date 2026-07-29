"""benchmark — Performance benchmarking for the I language.

Provides timing, memory measurement, and comparison tools.
"""

from __future__ import annotations

import sys
import time
from typing import Any, Callable, Dict, List, Optional


class BenchmarkResult:
    """Result of a single benchmark run."""
    __slots__ = ("name", "iterations", "total_ms", "min_ms", "max_ms", "avg_ms")

    def __init__(self, name: str, iterations: int, times_ms: List[float]) -> None:
        self.name = name
        self.iterations = iterations
        self.total_ms = sum(times_ms)
        self.min_ms = min(times_ms) if times_ms else 0
        self.max_ms = max(times_ms) if times_ms else 0
        self.avg_ms = self.total_ms / len(times_ms) if times_ms else 0

    def ops_per_second(self) -> float:
        if self.avg_ms == 0:
            return float("inf")
        return 1000.0 / self.avg_ms

    def __repr__(self) -> str:
        return (f"Benchmark({self.name}: {self.avg_ms:.3f}ms/op, "
                f"{self.ops_per_second():.0f} ops/s)")


def bench(fn: Callable, iterations: int = 1000, warmup: int = 10,
          name: str = "") -> BenchmarkResult:
    """Benchmark a function."""
    label = name or getattr(fn, "__name__", "anonymous")
    # Warmup
    for _ in range(warmup):
        fn()
    # Measure
    times: List[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
    return BenchmarkResult(label, iterations, times)


def bench_time(fn: Callable, *args: Any, **kwargs: Any) -> float:
    """Time a single function call in milliseconds."""
    start = time.perf_counter()
    fn(*args, **kwargs)
    return (time.perf_counter() - start) * 1000


def bench_compare(functions: Dict[str, Callable], iterations: int = 1000) -> List[BenchmarkResult]:
    """Compare multiple functions."""
    results = []
    for name, fn in functions.items():
        result = bench(fn, iterations, name=name)
        results.append(result)
    results.sort(key=lambda r: r.avg_ms)
    return results


def print_results(results: List[BenchmarkResult]) -> None:
    """Print benchmark results as a table."""
    print(f"\n{'Benchmark':<30} {'Avg (ms)':>10} {'Min (ms)':>10} {'Max (ms)':>10} {'Ops/s':>10}")
    print("-" * 75)
    for r in results:
        print(f"{r.name:<30} {r.avg_ms:>10.3f} {r.min_ms:>10.3f} {r.max_ms:>10.3f} {r.ops_per_second():>10.0f}")


class Timer:
    """Context-manager for timing code blocks."""

    def __init__(self, label: str = "") -> None:
        self.label = label
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> Timer:
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        self.elapsed_ms = (time.perf_counter() - self._start) * 1000
        if self.label:
            print(f"{self.label}: {self.elapsed_ms:.3f} ms")
