# Performance Guide

## Overview

The `imikorere_sisitemu` module provides benchmarking, latency measurement,
memory tracking, throughput metering, and performance optimization for systems
programming.

## Benchmarking

```python
from sisitemu.imikorere_sisitemu import Benchmark

bench = Benchmark()
result = bench.run("memcpy", lambda n: bytearray(n).copy(), iterations=10000)
print(f"Mean: {result.mean_ms:.3f}ms, P95: {result.p95_ms:.3f}ms")
```

## Latency Measurement

```python
from sisitemu.imikorere_sisitemu import LatencyMeter

meter = LatencyMeter()
with meter.sample():
    do_operation()
report = meter.report()
print(f"p50={report.p50_us}us p95={report.p95_us}us p99={report.p99_us}us")
```

## Memory Tracking

```python
from sisitemu.imikorere_sisitemu import MemoryUsageTracker

tracker = MemoryUsageTracker()
tracker.snapshot("before")
large_list = [0] * 1_000_000
tracker.snapshot("after")
diff = tracker.diff("before", "after")
print(f"Delta: {diff.peak_mb:.2f} MB")
```

## Throughput

```python
from sisitemu.imikorere_sisitemu import ThroughputMeter

meter = ThroughputMeter(unit="MB/s")
for i in range(1000):
    process_data(data[i])
    meter.record(len(data[i]))
print(f"Throughput: {meter.throughput():.2f} MB/s")
```

## Profiling

```bash
isoko sisitemu benchmark --module all --iterations 5000 --output results.json
```
