# Performance Strategy

This document describes the long-term optimization plans for the I Programming Language compiler and runtime.

## Table of Contents

- [Overview](#overview)
- [Compilation Performance](#compilation-performance)
- [Runtime Performance](#runtime-performance)
- [Constant Folding](#constant-folding)
- [Dead Code Elimination](#dead-code-elimination)
- [Inlining](#inlining)
- [Escape Analysis](#escape-analysis)
- [Loop Optimization](#loop-optimization)
- [Incremental Compilation](#incremental-compilation)
- [Parallel Compilation](#parallel-compilation)
- [Caching](#caching)
- [Profiling](#profiling)
- [Optimization Levels](#optimization-levels)

## Overview

Performance optimization is a continuous process. This document describes the optimization strategies across the full stack: compilation speed, runtime speed, and memory usage.

### Performance Goals

| Metric | Target | Timeline |
|--------|--------|----------|
| Compilation speed | 10,000 LOC/sec | Phase 1 |
| Runtime speed | Within 2x of C | Phase 2 |
| Memory usage | Within 2x of C | Phase 2 |
| Binary size | Within 3x of C | Phase 2 |

## Compilation Performance

### Current Targets

- **Lexer**: 100,000 LOC/sec
- **Parser**: 50,000 LOC/sec
- **Semantic analysis**: 30,000 LOC/sec
- **Type checking**: 20,000 LOC/sec
- **IR generation**: 30,000 LOC/sec
- **Bytecode generation**: 50,000 LOC/sec
- **Overall**: 10,000 LOC/sec (bottleneck: type checking)

### Compilation Speed Strategies

1. **Efficient data structures**: Hash maps, arena allocators, interning
2. **Lazy analysis**: Only analyze what's needed
3. **Incremental analysis**: Re-analyze only changed parts
4. **Parallel compilation**: Compile independent modules in parallel
5. **Caching**: Cache intermediate results

## Runtime Performance

### Execution Speed Strategies

1. **Bytecode optimization**: Optimized instruction set
2. **Inline caching**: Cache method lookup results
3. **JIT compilation** (future): Compile hot paths to native code
4. **Escape analysis**: Stack-allocate non-escaping objects
5. **Loop optimization**: Unrolling, vectorization
6. **Tail call optimization**: Convert tail calls to jumps

### Memory Usage Strategies

1. **Value types**: Stack-allocate small structs
2. **String interning**: Deduplicate strings
3. **Memory pooling**: Reuse allocations
4. **Compact representations**: Use smaller types when possible

## Constant Folding

### Description

Evaluate constant expressions at compile time.

### Examples

```
// Before:
shyira x = 2 + 3 * 4

// After constant folding:
shyira x = 14

// Before:
shyira msg = "Hello" + ", " + "World"

// After constant folding:
shyira msg = "Hello, World"
```

### Implementation

1. Walk the AST
2. For each binary/unary expression with constant operands
3. Evaluate the expression
4. Replace with a literal node

### When to Apply

- Optimization level >= 1
- Always for string concatenation in literals
- Never for floating-point (precision concerns) unless -O3

## Dead Code Elimination

### Description

Remove code that can never be executed or whose results are never used.

### Types

1. **Unreachable code**: Code after return/throw/break
2. **Dead assignments**: Variables assigned but never read
3. **Dead functions**: Functions never called
4. **Dead branches**: If conditions that are always true/false

### Examples

```
// Before:
shyira x = 10
subira 42
andika(x)  // Unreachable

// After:
shyira x = 10
subira 42

// Before:
shyira x = 10
// x is never used

// After:
// (x declaration removed)
```

### Implementation

1. Mark all reachable code from entry point
2. Remove unmarked code
3. Remove unused assignments
4. Iterate until no more changes

## Inlining

### Description

Replace function calls with the function body.

### When to Inline

| Criterion | Threshold |
|-----------|-----------|
| Function body size | <= 5 instructions |
| Call frequency | > 10 calls/sec |
| Function depth | <= 3 levels |
| No recursion | Not recursive |
| Small argument count | <= 3 arguments |

### Benefits

1. Eliminates function call overhead
2. Enables further optimizations (constant propagation into inlined body)
3. Reduces branch prediction misses

### Costs

1. Increased code size
2. Longer compilation time
3. Potential instruction cache pressure

### Implementation

1. Profile function call frequency
2. Estimate inlining benefit (saved instructions * call frequency)
3. Apply inlining if benefit exceeds cost
4. Limit inlining depth to prevent code explosion

## Escape Analysis

### Description

Determine which objects never escape their creating scope.

### Applications

1. **Stack allocation**: Allocate non-escaping objects on the stack
2. **Lock elision**: Remove locks for thread-local objects
3. **Scalar replacement**: Decompose objects into individual variables

### Examples

```
// Before (heap allocation):
umurimo process() -> int
    shyira point = gukora Point(1, 2)
    subira point.x + point.y
iherezo

// After escape analysis (stack allocation):
umurimo process() -> int
    shyira point_x = 1  // Stack allocated
    shyira point_y = 2  // Stack allocated
    subira point_x + point_y
iherezo
```

### Implementation

1. Walk the AST, tracking object references
2. Check if any reference escapes the current scope
3. If no escape: mark for stack allocation
4. If escape: mark for heap allocation

## Loop Optimization

### Loop-Invariant Code Motion

Move computations that don't change across loop iterations out of the loop:

```
// Before:
wihuse i < list.length
    shyira temp = expensive_computation()  // Loop-invariant
    andika(list[i] + temp)
    i += 1
iherezo

// After:
shyira temp = expensive_computation()  // Hoisted
wihuse i < list.length
    andika(list[i] + temp)
    i += 1
iherezo
```

### Strength Reduction

Replace expensive operations with cheaper equivalents:

```
// Before:
shyira x = y * 2

// After:
shyira x = y << 1
```

### Loop Unrolling

Duplicate the loop body to reduce branch overhead:

```
// Before:
kuri i muri 0 kugeza 4
    process(array[i])
iherezo

// After:
process(array[0])
process(array[1])
process(array[2])
process(array[3])
```

### Induction Variable Optimization

Optimize loop counter variables:

```
// Before:
shyira i = 0
wihuse i < n
    array[i] = 0
    i = i + 1
iherezo

// After (strength reduction):
shyira ptr = array_base
shyira end = array_base + n * element_size
wihuse ptr < end
    *ptr = 0
    ptr += element_size
iherezo
```

## Incremental Compilation

### Description

Only recompile parts of the program that have changed.

### Strategy

1. **Dependency tracking**: Track which files depend on which
2. **Change detection**: Detect file modifications (timestamps, hashes)
3. **Selective recompilation**: Recompile only changed files and dependents
4. **Incremental type checking**: Re-check only affected types
5. **Incremental code generation**: Re-generate code for changed functions

### Cache Structure

```
IncrementalCache {
    file_hashes: Map<String, Hash>
    ast_cache: Map<String, AST>
    type_cache: Map<String, TypeEnvironment>
    ir_cache: Map<String, IRModule>
    bytecode_cache: Map<String, BytecodeModule>
}
```

### Invalidation Rules

- If a file changes: invalidate its cache entry
- If a file's exports change: invalidate all files that import it
- If a type definition changes: invalidate all files using that type
- If a function signature changes: invalidate all callers

## Parallel Compilation

### Description

Compile independent modules in parallel.

### Parallelism Opportunities

1. **Lexing/Parsing**: Each file can be lexed/parsed independently
2. **Semantic analysis**: Each module can be analyzed independently (after dependency resolution)
3. **Code generation**: Each module can generate code independently
4. **Linking**: Can be parallelized with careful design

### Implementation

1. Build a dependency graph of modules
2. Identify independent modules (no dependency relationship)
3. Compile independent modules in parallel using a thread pool
4. Wait for dependencies before compiling dependent modules

### Thread Pool

```
ThreadPool {
    threads: List<WorkerThread>
    task_queue: Queue<CompilationTask>
    
    submit(task: CompilationTask)
    wait_all()
    shutdown()
}
```

## Caching

### Bytecode Caching

Cache compiled bytecode to avoid recompilation:

```
BytecodeCache {
    cache_dir: Path
    entries: Map<Hash, CacheEntry>
    
    CacheEntry {
        source_hash: Hash
        bytecode: BytecodeModule
        timestamp: int
        size: int
    }
}
```

### Module Caching

Cache loaded modules to avoid re-initialization:

```
ModuleCache {
    modules: Map<String, Module>
    initialized: Set<String>
}
```

### Type Caching

Cache type inference results:

```
TypeCache {
    inferred_types: Map<ASTNodeId, Type>
    constraint_solutions: Map<ConstraintId, Type>
}
```

## Profiling

### Compilation Profiling

Measure compilation time per stage:

```
CompilationProfile {
    lexing_time: Duration
    parsing_time: Duration
    semantic_time: Duration
    type_check_time: Duration
    ir_gen_time: Duration
    optimization_time: Duration
    code_gen_time: Duration
    total_time: Duration
}
```

### Runtime Profiling

Collect runtime statistics for optimization decisions:

```
RuntimeProfile {
    function_call_counts: Map<String, int>
    function_call_times: Map<String, Duration>
    loop_iteration_counts: Map<String, int>
    allocation_sites: Map<String, int>
    gc_pause_times: List<Duration>
}
```

### Profile-Guided Optimization (PGO)

Use runtime profiles to guide compilation:

1. Compile with profiling instrumentation
2. Run the program with representative inputs
3. Collect profile data
4. Recompile using profile data to guide optimization decisions

## Optimization Levels

| Level | Name | Features | Compilation Speed |
|-------|------|----------|-------------------|
| 0 | None | No optimizations | Fastest |
| 1 | Basic | Constant folding, dead code elimination | Fast |
| 2 | Standard | + Inlining, common subexpression elimination | Moderate |
| 3 | Aggressive | + Loop optimization, escape analysis, PGO | Slow |

### Level 0: None

- No optimization passes
- Fastest compilation
- For development and debugging

### Level 1: Basic

- Constant folding
- Dead code elimination
- Peephole optimizations
- Fast compilation, modest speedup

### Level 2: Standard

- Level 1 optimizations
- Function inlining (conservative)
- Common subexpression elimination
- Tail call optimization
- Good balance of compilation speed and execution speed

### Level 3: Aggressive

- Level 2 optimizations
- Function inlining (aggressive)
- Loop unrolling and vectorization
- Escape analysis
- Profile-guided optimization
- Maximum execution speed, slower compilation

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
