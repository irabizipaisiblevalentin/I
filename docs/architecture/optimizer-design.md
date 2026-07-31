# Production Optimizer Architecture

## Overview

The I Programming Language compiler includes a production-grade optimization framework (Phase 9.7) that operates on the IR (Intermediate Representation). It provides a modular architecture with 17 analysis passes, 30 optimization passes, 7 optimization levels, IR verification after every pass, comprehensive debugging support, and benchmarking infrastructure.

## Architecture

### Core Framework

| Module | Purpose |
|--------|---------|
| `base.py` | Abstract base classes: `Pass`, `Analysis`, `PassResult`, `PassImpact`, `AnalysisResult` |
| `manager.py` | `OptimizationManager` — top-level driver, creates registry/pipeline, exposes `optimize()` API |
| `context.py` | `OptimizationContext` — carries module, level, stats, cache, iteration, debug state |
| `pipeline.py` | `OptimizationPipeline` — manages pass execution, IR verification, debug dumps |
| `scheduler.py` | `OptimizationScheduler` — topological sort via Kahn's algorithm, cycle detection |
| `registry.py` | `PassRegistry` — stores `PassInfo`/`AnalysisInfo`, lookup by name, level-filtered queries |
| `cache.py` | `AnalysisCache` — LRU-free cache with BFS cascading invalidation via reverse dependencies |
| `stats.py` | `StatisticsEngine` + `OptimizationReport` — timing, instruction/block/byte counts, formatting |
| `benchmark.py` | `BenchmarkRunner` + `BenchmarkReport` — full benchmarking across all optimization levels |

### Data Flow

```
OptimizationManager
  └─ OptimizationPipeline
       ├─ IRValidator (verification after every pass)
       ├─ OptimizationScheduler (topological sort)
       ├─ PassRegistry (PassInfo / AnalysisInfo lookups)
       ├─ AnalysisCache (get/put/invalidate with BFS cascading)
       └─ StatisticsEngine (per-pass timing, before/after counts)
            └─ OptimizationReport (summary, table, to_dict)
```

### IR Verification

After every optimization pass, the pipeline runs `IRValidator.validate_module()` to verify:
- No duplicate function names
- Every block has a terminator
- Terminator is the last instruction in its block
- No use-before-def violations
- Phi node incoming blocks are valid predecessors
- Cast operations have correct operand types
- Load/Store pointers are pointer-typed
- Call targets are function types

If verification fails, a `RuntimeError` is raised immediately, preventing silent IR corruption.

### Debugging Support

The pipeline supports:
- **Pass-by-pass IR dumps**: Dump IR before/after each pass when `enable_debug` is set
- **Transformation logs**: Record each transformation with pass name and description
- **Debug flags**: `debug_enabled`, `verify_ir`, `dump_ir` on `OptimizationContext`
- **Configurable output**: `debug_output_dir` for file-based dumps
- **Changed-only dumps**: Only dump when a pass makes changes

### Benchmarking Infrastructure

The `benchmark.py` module provides:
- **BenchmarkRunner**: Run full benchmarks across all optimization levels
- **BenchmarkReport**: Format and compare results (format_table, format_summary, to_dict)
- **ScalabilityBenchmark**: Measure how optimization scales with program size
- **ScalabilityReport**: Estimate algorithmic complexity from empirical data
- **Pass timing**: Measure individual pass execution times

## Optimization Levels

| Level | Enum Value | Description | Default Passes |
|-------|-----------|-------------|----------------|
| `O0` | 1 | No optimization | (none) |
| `O1` | 2 | Basic folding + DCE + branch elimination | constant_folding, dead_code_elimination, redundant_branch_elimination |
| `O2` | 3 | Standard optimization | O1 + constant_propagation, copy_propagation, CSE, basic_block_merging, control_flow_simplification |
| `O3` | 4 | Aggressive optimization | O2 + inlining, LICM, loop_unrolling, strength_reduction, tail_call, instruction_combining, peephole, jump_threading, branch_simplification, switch_optimization, sparse_ccp, ssa_cleanup |
| `OS` | 5 | Size optimization | O1 + constant/copy propagation, instruction_combining, peephole, strength_reduction, basic_block_merging |
| `OZ` | 6 | Minimal size | constant_folding, DCE, peephole, instruction_combining, redundant_branch_elimination |
| `OFAST` | 7 | Maximum speed | O3 + devirtualization, memory_optimization, object_lifetime, allocation_hoisting, register_allocation |

## Analysis Passes (17)

All registered via `register_default_analyses()`. Each analysis declares `required_analyses`, `produced_analyses`, and `invalidated_analyses`.

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

## Optimization Passes (30)

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
| `basic_block_merging` | `BasicBlockMergingPass` | Merge single-predecessor blocks |
| `redundant_branch_elimination` | `RedundantBranchEliminationPass` | Eliminate unnecessary branches |

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
| `devirtualization` | `DevirtualizationPass` | Replace indirect calls with direct calls |

### Memory Optimizations
| Pass | Class | Description |
|------|-------|-------------|
| `memory_coalescing` | `MemoryCoalescingPass` | Combine adjacent memory operations |
| `memory_optimization` | `MemoryOptimizationPass` | Reduce allocations, improve locality |
| `object_lifetime_optimization` | `ObjectLifetimeOptimizationPass` | Remove dead allocas (≥30% dead ratio) |
| `allocation_hoisting` | `AllocationHoistingPass` | Hoist loop-invariant allocations |

### Peephole
| Pass | Class | Description |
|------|-------|-------------|
| `peephole_optimization` | `PeepholeOptimizationPass` | Pattern-based local rewrites |

### SSA Cleanup
| Pass | Class | Description |
|------|-------|-------------|
| `ssa_cleanup` | `SSACleanupPass` | Clean up redundant phis, normalize SSA form |

### Code Generation Preparation
| Pass | Class | Description |
|------|-------|-------------|
| `register_allocation` | `RegisterAllocationPass` | Virtual register estimation |

## Quality Gates

The optimizer is considered production-ready when:
1. All 30 optimization passes pass correctness tests
2. IR verification succeeds after every pass
3. Benchmarks meet performance targets
4. Documentation is complete
5. No compiler warnings
6. No lint errors
7. Security review passes
8. Cross-platform validation passes

## Usage

```python
from compiler.optimization.manager import OptimizationManager
from compiler.optimization.context import OptimizationLevel
from compiler.optimization.benchmark import BenchmarkRunner

# Basic optimization
manager = OptimizationManager()
report = manager.optimize(module, level=OptimizationLevel.O2)
print(report.format_summary())
print(report.format_table())

# With debugging
from compiler.optimization.pipeline import PipelineConfig
config = PipelineConfig()
config.enable_debug = True
config.enable_verification = True
config.debug_output_dir = "./opt_debug"
manager = OptimizationManager(config=config)
report = manager.optimize(module, level=OptimizationLevel.O2)

# Benchmarking across all levels
runner = BenchmarkRunner()
bench_report = runner.benchmark(module)
print(bench_report.format_table())

# Scalability analysis
from compiler.optimization.benchmark import ScalabilityBenchmark
scal = ScalabilityBenchmark()
scale_report = scal.benchmark(lambda size: make_module_of_size(size), [10, 100, 1000])
print(scale_report.format_summary())
```

## Security Considerations

1. **Integer overflow**: Constant folding handles large integer values safely
2. **Resource exhaustion**: Fixed-point iteration limits prevent infinite loops
3. **IR corruption**: Verification after every pass detects invalid transformations
4. **Undefined behaviour**: No optimisation introduces undefined behaviour
5. **Timeouts**: Configurable timeout prevents hangs on pathological input
