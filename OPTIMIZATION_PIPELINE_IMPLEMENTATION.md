# Optimization Pipeline Implementation (Sprint 7)

## Overview

The I Programming Language compiler includes an industrial-strength optimization pipeline (Phase 7.7) that operates on the IR (Intermediate Representation). It provides a modular framework with 12 analysis passes, 25 optimization passes, seven optimization levels, an analysis cache with BFS cascading invalidation, and comprehensive performance reporting.

## Architecture

### Core Framework

| Module | Purpose |
|--------|---------|
| `base.py` | Abstract base classes: `Pass`, `Analysis`, `PassResult`, `PassImpact`, `AnalysisResult` |
| `manager.py` | `OptimizationManager` — top-level driver, creates registry/pipeline, exposes `optimize()` API |
| `context.py` | `OptimizationContext` — carries module, level, stats, cache, iteration state through a run |
| `pipeline.py` | `OptimizationPipeline` — manages pass execution, fixed-point iteration, single-pass execution |
| `scheduler.py` | `OptimizationScheduler` — topological sort via Kahn's algorithm, cycle detection |
| `registry.py` | `PassRegistry` — stores `PassInfo`/`AnalysisInfo`, lookup by name, level-filtered queries |
| `cache.py` | `AnalysisCache` — LRU-free cache with BFS cascading invalidation via reverse dependencies |
| `stats.py` | `StatisticsEngine` + `OptimizationReport` — timing, instruction/block/byte counts, formatting |

### Data Flow

```
OptimizationManager
  └─ OptimizationPipeline
       ├─ OptimizationScheduler  (topological sort on PassInfo.dependencies)
       ├─ PassRegistry           (PassInfo / AnalysisInfo lookups)
       ├─ AnalysisCache          (get/put/invalidate with BFS cascading)
       └─ StatisticsEngine       (per-pass timing, before/after counts)
            └─ OptimizationReport  (summary, table, to_dict)
```

## Optimization Levels

| Level | Enum Value | Description | Default Passes |
|-------|-----------|-------------|----------------|
| `O0` | 1 | No optimization | (none) |
| `O1` | 2 | Basic folding + DCE | constant_folding, dead_code_elimination |
| `O2` | 3 | Standard optimization | O1 + constant_propagation, copy_propagation, CSE |
| `O3` | 4 | Aggressive optimization | O2 + inlining, LICM, loop_unrolling, strength_reduction, tail_call, instruction_combining, peephole |
| `OS` | 5 | Size optimization | constant_folding, DCE, constant/copy propagation, instruction_combining, peephole, strength_reduction |
| `OZ` | 6 | Minimal size | constant_folding, DCE, peephole, instruction_combining |
| `OFAST` | 7 | Maximum speed | O3 + devirtualization, memory_optimization (placeholder) |

Levels are `IntEnum` with `auto()`: O0=1 through OFAST=7.

## Analysis Passes (12)

All registered via `register_default_analyses()` in `analyses/_register.py`. Each analysis declares `required_analyses`, `produced_analyses`, and `invalidated_analyses` for dependency tracking.

| Analysis | Class | Key Capability |
|----------|-------|----------------|
| `control_flow` | `ControlFlowAnalysis` | CFG construction, predecessor/successor maps |
| `data_flow` | `DataFlowAnalysis` | Dataflow equations (gen/kill, meet operators) |
| `liveness` | `LivenessAnalysis` | Live variable analysis per block |
| `reachability` | `ReachabilityAnalysis` | Forward reachability from entry |
| `escape` | `EscapeAnalysis` | Whether values escape their defining scope |
| `alias` | `AliasAnalysis` | Pointer aliasing relationships |
| `dominance` | `DominanceAnalysis` | Dominator tree, immediate dominators |
| `loop` | `LoopAnalysis` | Loop detection, nesting depth, back-edges |
| `call_graph` | `CallGraphAnalysis` | Inter-procedural call relationships |
| `side_effect` | `SideEffectAnalysis` | Pure vs. side-effecting function classification |
| `memory_access` | `MemoryAccessAnalysis` | Read/write sets for memory operations |
| `constant_propagation` | `ConstantPropagationAnalysis` | Compile-time constant determination |

## Optimization Passes (25)

All registered via `register_default_passes()` in `passes/_register.py`. Each pass declares dependencies, required/produced/invalidated analyses, and returns `PassResult(changed=..., impact=..., details=...)`.

### Scalar Optimizations
| Pass | Class | Description |
|------|-------|-------------|
| `constant_folding` | `ConstantFoldingPass` | Evaluate constant expressions at compile time |
| `constant_propagation` | `ConstantPropagationPass` | Propagate known constants through SSA edges |
| `copy_propagation` | `CopyPropagationPass` | Replace copies with source values |
| `common_subexpression_elimination` | `CommonSubexpressionEliminationPass` | Remove redundant computations |
| `sparse_conditional_constant_propagation` | `SparseConditionalConstantPropagationPass` | SCCP — lattice-based constant propagation |
| `strength_reduction` | `StrengthReductionPass` | Replace expensive ops (mul→shift, div→shift) |
| `instruction_combining` | `InstructionCombiningPass` | Combine redundant instruction patterns |

### Dead Code Elimination
| Pass | Class | Description |
|------|-------|-------------|
| `dead_code_elimination` | `DeadCodeEliminationPass` | Remove instructions with no uses |
| `dead_store_elimination` | `DeadStoreEliminationPass` | Remove stores to dead locations |
| `redundant_load_elimination` | `RedundantLoadEliminationPass` | Remove loads when value already known |
| `redundant_store_elimination` | `RedundantStoreEliminationPass` | Remove consecutive stores to same location |

### Control Flow Optimizations
| Pass | Class | Description |
|------|-------|-------------|
| `control_flow_simplification` | `ControlFlowSimplificationPass` | Merge blocks, remove empty blocks |
| `branch_simplification` | `BranchSimplificationPass` | Simplify constant branches, dead edges |
| `jump_threading` | `JumpThreadingPass` | Thread jumps through blocks with single target |
| `switch_optimization` | `SwitchOptimizationPass` | Optimize switch: dense→lookup table, 0-case→branch |

### Loop Optimizations
| Pass | Class | Description |
|------|-------|-------------|
| `loop_invariant_code_motion` | `LoopInvariantCodeMotionPass` | Hoist loop-invariant computations to preheader |
| `loop_unrolling` | `LoopUnrollingPass` | Unroll small loops to reduce branch overhead |
| `loop_simplification` | `LoopSimplificationPass` | Ensure single entry (preheader), merge multiple entries |

### Function Optimizations
| Pass | Class | Description |
|------|-------|-------------|
| `function_inlining` | `FunctionInliningPass` | Inline small functions (≤5 instructions, ≤2 blocks) |
| `tail_call_optimization` | `TailCallOptimizationPass` | Convert tail calls to jumps |

### Memory Optimizations
| Pass | Class | Description |
|------|-------|-------------|
| `memory_coalescing` | `MemoryCoalescingPass` | Combine adjacent memory operations |
| `object_lifetime_optimization` | `ObjectLifetimeOptimizationPass` | Remove dead allocas (≥30% dead ratio) |
| `allocation_hoisting` | `AllocationHoistingPass` | Hoist loop-invariant allocations |

### Peephole
| Pass | Class | Description |
|------|-------|-------------|
| `peephole_optimization` | `PeepholeOptimizationPass` | Pattern-based local rewrites (algebraic identities, strength) |

### SSA Cleanup
| Pass | Class | Description |
|------|-------|-------------|
| `ssa_cleanup` | `SSACleanupPass` | Clean up redundant phis, normalize SSA form |

## Key Design Decisions

### IR Mutation Pattern

`BasicBlock.instructions` is a **property that returns a copy**. All optimization passes must mutate via:
- `bb._instructions` — direct list access
- `bb.append(inst)` — add to end
- `bb.insert_before(ref, inst)` / `bb.insert_after(ref, inst)` — positional insert
- `bb.remove(inst)` — remove by reference
- `bb.replace(old, new)` — swap instructions

Similarly, `func.basic_blocks` returns a copy; use `func._blocks` for mutation, `func.insert_block(idx, block)` for insertion.

### Analysis Cache

The `AnalysisCache` uses BFS cascading invalidation. When an analysis result is invalidated, all analyses that transitively depend on it are also invalidated via reverse-dependency traversal.

### Pass Scheduling

`OptimizationScheduler` uses Kahn's algorithm (topological sort) on `PassInfo.dependencies`. Cycles are detected and raise `ValueError`. Custom pass order is supported via `PipelineConfig.custom_pass_order`.

### Fixed-Point Iteration

`OptimizationPipeline.run_fixed_point()` runs all passes at the given level repeatedly until no instruction count changes or `max_fixed_point_iterations` (default 4) is reached. Each iteration tracks `ctx.iteration` for passes that need to know which round they're in.

## Usage

```python
from compiler.optimization.manager import OptimizationManager
from compiler.optimization.context import OptimizationLevel

manager = OptimizationManager()
report = manager.optimize(module, level=OptimizationLevel.O2)
print(report.format_summary())
print(report.format_table())

# Or via integer level:
report = manager.optimize_module(module, level=3)

# Single pass:
manager.run_pass(module, "constant_folding", level=OptimizationLevel.O1)
```

## File Structure

```
src/compiler/optimization/
├── __init__.py
├── base.py              # Pass, Analysis, PassResult, PassImpact, AnalysisResult
├── manager.py           # OptimizationManager (top-level driver)
├── context.py           # OptimizationContext, OptimizationLevel enum
├── pipeline.py          # OptimizationPipeline, PipelineConfig
├── scheduler.py         # OptimizationScheduler (topological sort)
├── registry.py          # PassRegistry, PassInfo, AnalysisInfo
├── cache.py             # AnalysisCache (BFS invalidation)
├── stats.py             # StatisticsEngine, PassStats, OptimizationReport
├── analyses/
│   ├── __init__.py
│   ├── _register.py     # register_default_analyses()
│   ├── alias.py
│   ├── call_graph.py
│   ├── constant_propagation.py
│   ├── control_flow.py
│   ├── data_flow.py
│   ├── dominance.py
│   ├── escape.py
│   ├── liveness.py
│   ├── loop.py
│   ├── memory_access.py
│   ├── reachability.py
│   └── side_effect.py
└── passes/
    ├── __init__.py
    ├── _register.py     # register_default_passes()
    ├── allocation_hoisting.py
    ├── branch_simplification.py
    ├── common_subexpression.py
    ├── constant_folding.py
    ├── constant_propagation.py
    ├── control_flow_simplification.py
    ├── copy_propagation.py
    ├── dead_code_elimination.py
    ├── dead_store_elimination.py
    ├── function_inlining.py
    ├── instruction_combining.py
    ├── jump_threading.py
    ├── loop_invariant_code_motion.py
    ├── loop_simplification.py
    ├── loop_unrolling.py
    ├── memory_coalescing.py
    ├── object_lifetime.py
    ├── peephole.py
    ├── redundant_load_elimination.py
    ├── redundant_store_elimination.py
    ├── sparse_ccp.py
    ├── ssa_cleanup.py
    ├── strength_reduction.py
    ├── switch_optimization.py
    └── tail_call.py
```

## Tests

188 tests in `tests/unit/test_optimization_sprint7.py` covering:
- Base classes (Pass, Analysis, PassResult, PassImpact, AnalysisResult)
- Context (OptimizationLevel enum, state management)
- Registry (pass/analysis registration, lookup, level filtering)
- Cache (get/put, BFS cascading invalidation, dependency tracking)
- Scheduler (topological sort, cycle detection, custom order)
- Statistics (timing, counters, report generation, formatting)
- Pipeline (single-pass, fixed-point, default pipeline)
- Manager (optimize, optimize_module, run_pass)
- All 25 optimization passes (smoke tests + effect verification)
- All 12 analyses (basic functionality)

**Test command:**
```bash
python -m pytest tests/unit/test_optimization_sprint7.py -v --tb=short
```

**All 188 tests pass.**
