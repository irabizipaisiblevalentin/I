# Performance Report — I Language v1.0

**Prepared by:** Release Stabilization Team
**Date:** 2026-07-31
**Method:** `python -m compiler.compiler -r examples/<name>` × 5 runs, median wall time (includes
Python interpreter startup, lexing, parsing, semantic analysis, codegen, and legacy-VM execution).
Environment: Windows, Python 3.14.6.

---

## 1. Example Program End-to-End Times

| Example | Median (ms) | Min (ms) | Max (ms) |
|---|---|---|---|
| `hello.i` | 291 | 286 | 319 |
| `variables.i` | 296 | 286 | 309 |
| `functions.i` | 296 | 290 | 300 |
| `conditionals.i` | 297 | 290 | 309 |
| `loops.i` | 298 | 283 | 305 |
| `fibonacci.i` (recursive) | 302 | 297 | 314 |

All examples complete in roughly **290-300 ms** regardless of program complexity (hello vs.
recursive fibonacci differ by ~10 ms). Execution is dominated by fixed interpreter/compiler
startup overhead, not by program work. The compiler stack is more than fast enough for v1.0
interactive use.

## 2. Full Test Suite

| Measurement | Time |
|---|---|
| Direct `pytest tests/ -q` | ~70 s |
| (includes ~40-60 s for the 3 e2e wheel-build/install tests) | — |
| Unit + other suites (excl. wheel builds) | ~30-35 s |

## 3. Wheel / Install

- Wheel size: **1,119,802 bytes** (~1.07 MB), pure-Python `py3-none-any`.
- `pip install --target` + imports of all 45 stdlib modules: < 1 s.
- No platform-specific binaries; performance is interpreter-bound.

## 4. Notes

- Timing includes the benign `RuntimeWarning` on stderr (see PACKAGING_REPORT.md §5); it does not
  affect runtime.
- The legacy VM (v1.0 runtime) is unoptimized by design; the modern `vm_executor.py` (frames,
  closures, structs) plus the optimization pipeline are the intended 1.1 performance path.
- No performance regressions observed relative to the pre-stabilization baseline (no benchmark
  suite exists; the only comparable metric is that all six examples now run at all, exit 0).

## 5. Recommendation

Add a lightweight CI benchmark gate in 1.1 (e.g., assert each shipped example completes in
< 1 s) to guard against startup regressions.
