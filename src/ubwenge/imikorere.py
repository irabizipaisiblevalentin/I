"""Performance — GPU utilization, memory usage, inference speed, model loading, caching, quantization, edge deployment."""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import OrderedDict


class OptimizationLevel(str, Enum):
    NONE = "none"
    BASIC = "basic"
    AGGRESSIVE = "aggressive"
    MAXIMUM = "maximum"


@dataclass
class PerformanceMetrics:
    inference_latency_ms: float = 0.0
    tokens_per_second: float = 0.0
    memory_usage_mb: float = 0.0
    gpu_utilization_pct: float = 0.0
    cpu_utilization_pct: float = 0.0
    disk_io_mb_s: float = 0.0
    model_load_time_ms: float = 0.0
    cache_hit_rate: float = 0.0
    throughput_per_second: float = 0.0
    batch_efficiency: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "inference_latency_ms": self.inference_latency_ms,
            "tokens_per_second": self.tokens_per_second,
            "memory_usage_mb": self.memory_usage_mb,
            "gpu_utilization_pct": self.gpu_utilization_pct,
            "cache_hit_rate": self.cache_hit_rate,
            "throughput_per_second": self.throughput_per_second,
        }


class ModelCache:
    def __init__(self, max_size_mb: int = 2048, ttl_seconds: int = 3600):
        self.max_size_mb = max_size_mb
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Tuple[Any, float, int]] = OrderedDict()
        self._current_size_mb = 0
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            data, timestamp, size = self._cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                self._cache.move_to_end(key)
                self._hits += 1
                return data
            else:
                del self._cache[key]
                self._current_size_mb -= size
        self._misses += 1
        return None

    def set(self, key: str, value: Any, size_mb: int = 1) -> None:
        while self._current_size_mb + size_mb > self.max_size_mb and self._cache:
            oldest_key, (_, _, oldest_size) = next(iter(self._cache.items()))
            del self._cache[oldest_key]
            self._current_size_mb -= oldest_size
        self._cache[key] = (value, time.time(), size_mb)
        self._current_size_mb += size_mb

    def clear(self) -> None:
        self._cache.clear()
        self._current_size_mb = 0
        self._hits = 0
        self._misses = 0

    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def size_mb(self) -> int:
        return self._current_size_mb


class Quantizer:
    @staticmethod
    def quantize_int8(model_path: str, output_path: str) -> str:
        return output_path or model_path.replace(".bin", "_int8.bin")

    @staticmethod
    def quantize_int4(model_path: str, output_path: str) -> str:
        return output_path or model_path.replace(".bin", "_int4.bin")

    def estimate_size_reduction(self, original_mb: float,
                                 precision: str = "int8") -> float:
        ratios = {"int8": 0.25, "int4": 0.125, "fp16": 0.5, "bf16": 0.5}
        return original_mb * ratios.get(precision, 1.0)


class Batcher:
    def __init__(self, max_batch_size: int = 32, max_wait_ms: int = 10):
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        self._queue: List[Tuple[Any, Callable]] = []

    def add(self, item: Any, callback: Callable) -> None:
        self._queue.append((item, callback))

    def flush(self) -> List[Any]:
        batch = self._queue[:self.max_batch_size]
        self._queue = self._queue[self.max_batch_size:]
        return [item for item, _ in batch]


class Profiler:
    def __init__(self):
        self._measurements: Dict[str, List[float]] = {}

    def start(self, label: str) -> None:
        if label not in self._measurements:
            self._measurements[label] = []

    def record(self, label: str, duration_ms: float) -> None:
        if label not in self._measurements:
            self._measurements[label] = []
        self._measurements[label].append(duration_ms)

    def stats(self, label: str) -> Dict[str, float]:
        values = self._measurements.get(label, [])
        if not values:
            return {"count": 0, "mean": 0, "min": 0, "max": 0, "p50": 0, "p95": 0, "p99": 0}
        sorted_v = sorted(values)
        n = len(sorted_v)
        return {
            "count": n,
            "mean": sum(sorted_v) / n,
            "min": sorted_v[0],
            "max": sorted_v[-1],
            "p50": sorted_v[int(n * 0.50)],
            "p95": sorted_v[int(n * 0.95)],
            "p99": sorted_v[int(n * 0.99)],
        }

    def report(self) -> Dict[str, Dict[str, float]]:
        return {label: self.stats(label) for label in self._measurements}


class PerformanceOptimizer:
    def __init__(self):
        self.cache = ModelCache()
        self.quantizer = Quantizer()
        self.batcher = Batcher()
        self.profiler = Profiler()
        self.level = OptimizationLevel.BASIC

    def set_level(self, level: OptimizationLevel) -> None:
        self.level = level
        if level == OptimizationLevel.AGGRESSIVE:
            self.cache.max_size_mb = 4096
            self.cache.ttl_seconds = 7200
            self.batcher.max_batch_size = 64
        elif level == OptimizationLevel.MAXIMUM:
            self.cache.max_size_mb = 8192
            self.cache.ttl_seconds = 14400
            self.batcher.max_batch_size = 128
        else:
            self.cache.max_size_mb = 2048
            self.cache.ttl_seconds = 3600
            self.batcher.max_batch_size = 32

    def measure(self, label: str) -> Callable:
        def decorator(fn: Callable) -> Callable:
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start = time.time()
                result = fn(*args, **kwargs)
                duration = (time.time() - start) * 1000
                self.profiler.record(label, duration)
                return result
            return wrapper
        return decorator


_perf_optimizer = PerformanceOptimizer()


def get_optimizer() -> PerformanceOptimizer:
    return _perf_optimizer
