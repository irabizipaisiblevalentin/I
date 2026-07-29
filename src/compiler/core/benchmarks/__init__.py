"""
Benchmark Framework

Performance benchmarking utilities.
"""

from __future__ import annotations

import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""

    name: str
    iterations: int
    times: list[float]

    @property
    def mean(self) -> float:
        """Mean time."""
        return statistics.mean(self.times) if self.times else 0.0

    @property
    def median(self) -> float:
        """Median time."""
        return statistics.median(self.times) if self.times else 0.0

    @property
    def stdev(self) -> float:
        """Standard deviation."""
        return statistics.stdev(self.times) if len(self.times) > 1 else 0.0

    @property
    def min_time(self) -> float:
        """Minimum time."""
        return min(self.times) if self.times else 0.0

    @property
    def max_time(self) -> float:
        """Maximum time."""
        return max(self.times) if self.times else 0.0

    def format(self) -> str:
        """Format result."""
        return (
            f"{self.name}: "
            f"mean={self.mean*1000:.2f}ms "
            f"median={self.median*1000:.2f}ms "
            f"stdev={self.stdev*1000:.2f}ms "
            f"min={self.min_time*1000:.2f}ms "
            f"max={self.max_time*1000:.2f}ms "
            f"({self.iterations} iterations)"
        )


class Benchmark:
    """
    Simple benchmark runner.
    """

    def __init__(
        self,
        name: str,
        func: Callable[[], Any],
        iterations: int = 100,
        warmup: int = 10,
    ) -> None:
        """
        Initialize benchmark.

        Args:
            name: Benchmark name
            func: Function to benchmark
            iterations: Number of iterations
            warmup: Number of warmup iterations
        """
        self._name = name
        self._func = func
        self._iterations = iterations
        self._warmup = warmup

    def run(self) -> BenchmarkResult:
        """
        Run benchmark.

        Returns:
            Benchmark result
        """
        # Warmup
        for _ in range(self._warmup):
            self._func()

        # Benchmark
        times: list[float] = []
        for _ in range(self._iterations):
            start = time.perf_counter()
            self._func()
            elapsed = time.perf_counter() - start
            times.append(elapsed)

        return BenchmarkResult(
            name=self._name,
            iterations=self._iterations,
            times=times,
        )


class BenchmarkSuite:
    """
    Collection of benchmarks.
    """

    def __init__(self) -> None:
        self._benchmarks: list[Benchmark] = []

    def add(
        self,
        name: str,
        func: Callable[[], Any],
        iterations: int = 100,
    ) -> None:
        """Add a benchmark."""
        self._benchmarks.append(
            Benchmark(name, func, iterations)
        )

    def run_all(self) -> list[BenchmarkResult]:
        """Run all benchmarks."""
        return [b.run() for b in self._benchmarks]

    def format_results(self, results: list[BenchmarkResult]) -> str:
        """Format results."""
        lines = ["Benchmark Results:", "=" * 60]
        for result in results:
            lines.append(f"  {result.format()}")
        return "\n".join(lines)
