"""imikorere_sisitemu — Performance: benchmarks, optimisation, startup time, memory usage, binary size, latency, throughput."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from statistics import mean, median, stdev
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class BenchmarkResult:
    name: str = ""
    iterations: int = 0
    total_time: float = 0.0
    min_time: float = 0.0
    max_time: float = 0.0
    avg_time: float = 0.0
    median_time: float = 0.0
    std_dev: float = 0.0
    throughput: float = 0.0
    ops_per_second: float = 0.0
    samples: List[float] = field(default_factory=list)

    @property
    def p50(self) -> float:
        return self.percentile(50)

    @property
    def p95(self) -> float:
        return self.percentile(95)

    @property
    def p99(self) -> float:
        return self.percentile(99)

    def percentile(self, p: float) -> float:
        if not self.samples:
            return 0.0
        sorted_s = sorted(self.samples)
        idx = max(0, min(len(sorted_s) - 1, int(len(sorted_s) * p / 100)))
        return sorted_s[idx]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "iterations": self.iterations,
            "total_time": round(self.total_time, 4),
            "avg_time": round(self.avg_time, 6),
            "min_time": round(self.min_time, 6),
            "max_time": round(self.max_time, 6),
            "median": round(self.median_time, 6),
            "p50": round(self.p50, 6),
            "p95": round(self.p95, 6),
            "p99": round(self.p99, 6),
            "stddev": round(self.std_dev, 6),
            "throughput": round(self.throughput, 2),
            "ops_per_second": round(self.ops_per_second, 2),
        }


class Benchmark:
    def __init__(self, name: str = "benchmark"):
        self.name = name
        self.results: Dict[str, BenchmarkResult] = {}
        self._warmup_iterations: int = 10

    def set_warmup(self, count: int) -> None:
        self._warmup_iterations = count

    def measure(self, name: str, fn: Callable,
                iterations: int = 1000, warmup: Optional[int] = None) -> BenchmarkResult:
        warmup = warmup if warmup is not None else self._warmup_iterations
        for _ in range(warmup):
            fn()
        samples = []
        for _ in range(iterations):
            start = time.perf_counter()
            fn()
            elapsed = time.perf_counter() - start
            samples.append(elapsed)
        total = sum(samples)
        result = BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=total,
            min_time=min(samples),
            max_time=max(samples),
            avg_time=mean(samples),
            median_time=median(samples),
            std_dev=stdev(samples) if len(samples) > 1 else 0.0,
            throughput=iterations / total if total > 0 else 0,
            ops_per_second=iterations / total if total > 0 else 0,
            samples=samples,
        )
        self.results[name] = result
        return result

    def measure_overhead(self, name: str, setup_fn: Callable[[], Any],
                         teardown_fn: Optional[Callable] = None,
                         iterations: int = 1000) -> BenchmarkResult:
        def run():
            obj = setup_fn()
            if teardown_fn:
                teardown_fn()
        return self.measure(name, run, iterations)

    def compare(self, name: str, implementations: Dict[str, Callable],
                iterations: int = 1000) -> Dict[str, BenchmarkResult]:
        results = {}
        for impl_name, fn in implementations.items():
            results[impl_name] = self.measure(f"{name}/{impl_name}", fn, iterations)
        return results

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "benchmarks": {k: v.to_dict() for k, v in self.results.items()},
        }


class LatencyMeter:
    def __init__(self):
        self.samples: List[float] = []

    def record(self, latency: float) -> None:
        self.samples.append(latency)

    @property
    def avg(self) -> float:
        return mean(self.samples) if self.samples else 0.0

    @property
    def p50(self) -> float:
        return self._percentile(50)

    @property
    def p95(self) -> float:
        return self._percentile(95)

    @property
    def p99(self) -> float:
        return self._percentile(99)

    def _percentile(self, p: float) -> float:
        if not self.samples:
            return 0.0
        sorted_s = sorted(self.samples)
        idx = max(0, min(len(sorted_s) - 1, int(len(sorted_s) * p / 100)))
        return sorted_s[idx]

    def summary(self) -> Dict[str, Any]:
        return {
            "samples": len(self.samples),
            "avg": round(self.avg, 6),
            "p50": round(self.p50, 6),
            "p95": round(self.p95, 6),
            "p99": round(self.p99, 6),
        }


class MemoryUsageTracker:
    def __init__(self):
        self.snapshots: List[Dict[str, int]] = []

    def snapshot(self, tag: str = "") -> None:
        import os
        import psutil
        process = psutil.Process(os.getpid())
        self.snapshots.append({
            "tag": tag,
            "rss": process.memory_info().rss,
            "vms": process.memory_info().vms,
            "timestamp": time.time(),
        })

    def diff(self, start_tag: str, end_tag: str) -> Dict[str, Any]:
        start = next((s for s in self.snapshots if s["tag"] == start_tag), None)
        end = next((s for s in self.snapshots if s["tag"] == end_tag), None)
        if not start or not end:
            return {}
        return {
            "rss_diff": end["rss"] - start["rss"],
            "vms_diff": end["vms"] - start["vms"],
            "time_diff": end["timestamp"] - start["timestamp"],
        }

    def peak_usage(self) -> int:
        return max((s["rss"] for s in self.snapshots), default=0)

    def summary(self) -> Dict[str, Any]:
        return {
            "snapshots": len(self.snapshots),
            "peak_rss": self.peak_usage(),
        }


class ThroughputMeter:
    def __init__(self, name: str = ""):
        self.name = name
        self._start: float = 0.0
        self._count: int = 0
        self._running: bool = False

    def start(self) -> None:
        self._start = time.perf_counter()
        self._count = 0
        self._running = True

    def increment(self, n: int = 1) -> None:
        self._count += n

    def stop(self) -> Dict[str, Any]:
        self._running = False
        elapsed = time.perf_counter() - self._start
        return {
            "name": self.name,
            "count": self._count,
            "elapsed": round(elapsed, 3),
            "throughput": round(self._count / elapsed, 2) if elapsed > 0 else 0,
        }


class PerformanceOptimizer:
    def __init__(self):
        self.benchmark = Benchmark()
        self.latency = LatencyMeter()
        self.memory = MemoryUsageTracker()
        self.throughput_meters: Dict[str, ThroughputMeter] = {}
        self._recommendations: List[str] = []

    def create_throughput_meter(self, name: str) -> ThroughputMeter:
        meter = ThroughputMeter(name)
        self.throughput_meters[name] = meter
        return meter

    def recommend(self, suggestion: str) -> None:
        self._recommendations.append(suggestion)

    def get_recommendations(self) -> List[str]:
        return self._recommendations

    def measure_startup(self, init_fn: Callable) -> BenchmarkResult:
        return self.benchmark.measure("startup", init_fn, iterations=1, warmup=0)

    def measure_interrupt_latency(self, simulated_irq_fn: Callable,
                                  iterations: int = 100) -> BenchmarkResult:
        return self.benchmark.measure("interrupt_latency", simulated_irq_fn, iterations)

    def measure_context_switch(self, switch_fn: Callable,
                               iterations: int = 100) -> BenchmarkResult:
        return self.benchmark.measure("context_switch", switch_fn, iterations)

    def summary(self) -> Dict[str, Any]:
        return {
            "benchmarks": self.benchmark.summary(),
            "latency": self.latency.summary(),
            "memory": self.memory.summary(),
            "throughput": {k: v.stop() if v._running else {} for k, v in self.throughput_meters.items()},
            "recommendations": self._recommendations,
        }


_performance = PerformanceOptimizer()


def get_performance() -> PerformanceOptimizer:
    return _performance
