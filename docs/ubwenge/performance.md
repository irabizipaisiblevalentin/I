# Performance Guide — Optimization

## Model Caching

```python
from ubwenge.imikorere import ModelCache

cache = ModelCache(max_size_mb=2048, ttl_seconds=3600)
cache.set("model_weights", weights, size_mb=500)
cached = cache.get("model_weights")
print(f"Cache hit rate: {cache.hit_rate:.2f}")
```

## Performance Profiling

```python
from ubwenge.imikorere import PerformanceOptimizer

opt = PerformanceOptimizer()

@opt.measure("inference")
def my_inference():
    pass

stats = opt.profiler.stats("inference")
print(f"p95 latency: {stats['p95']:.1f}ms")
```

## Optimization Levels

```python
from ubwenge.imikorere import OptimizationLevel

opt.set_level(OptimizationLevel.AGGRESSIVE)
# Increases cache to 4GB, TTL to 2h, batch size to 64

opt.set_level(OptimizationLevel.MAXIMUM)
# Increases cache to 8GB, TTL to 4h, batch size to 128
```

## Quantization

```python
from ubwenge.imikorere import Quantizer

q = Quantizer()
reduction = q.estimate_size_reduction(original_mb=1000, precision="int8")
print(f"Estimated size: {reduction:.0f}MB (75% reduction)")
```
