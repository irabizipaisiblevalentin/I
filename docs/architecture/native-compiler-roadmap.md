# Native Compiler Roadmap

This document describes how the I Programming Language will eventually compile to native machine code, covering LLVM integration, custom backend options, and trade-offs.

## Table of Contents

- [Overview](#overview)
- [Strategy](#strategy)
- [LLVM Backend](#llvm-backend)
- [Custom Backend](#custom-backend)
- [Hybrid Approach](#hybrid-approach)
- [Phase 1: Bytecode VM](#phase-1-bytecode-vm-current)
- [Phase 2: LLVM Integration](#phase-2-llvm-integration)
- [Phase 3: Custom Backend](#phase-3-custom-backend-optional)
- [Trade-off Analysis](#trade-off-analysis)
- [Target Platforms](#target-platforms)
- [Build System Integration](#build-system-integration)
- [Debugging Native Code](#debugging-native-code)

## Overview

The I compiler currently targets a bytecode VM. The native compilation roadmap describes how I programs will eventually be compiled directly to native machine code for maximum performance.

### Design Goals

1. **Maximize performance**: Native code should be within 10-20% of C/C++ for compute-bound tasks
2. **Minimize binary size**: Produce small, self-contained executables
3. **Preserve safety**: Memory safety, bounds checking, type safety in native code
4. **Enable debugging**: DWARF debug info for native debuggers
5. **Cross-compile**: Support building for different target platforms

## Strategy

### Three-Phase Approach

```
Phase 1 (Current):   Bytecode VM     - Fast compilation, portable execution
Phase 2 (Future):    LLVM Backend    - Good performance, broad platform support
Phase 3 (Optional):  Custom Backend  - Maximum performance, specialized targets
```

### Why Start with LLVM?

1. **Mature infrastructure**: LLVM has 20+ years of optimization research
2. **Broad platform support**: x86, x86_64, ARM, AArch64, RISC-V, WebAssembly
3. **Excellent optimizations**: Register allocation, instruction scheduling, vectorization
4. **Debug info**: DWARF generation for GDB/LLDB
5. **Link-time optimization**: Cross-module optimization
6. **Community**: Large community, well-documented

### Why Consider a Custom Backend Later?

1. **Faster compilation**: LLVM compilation can be slow
2. **Smaller binaries**: LLVM doesn't always produce optimal code size
3. **Specialized optimization**: Custom optimizations for I's type system
4. **Self-hosting**: A custom backend can be written in I itself

## LLVM Backend

### Architecture

```
I Source
    │
    ▼
  Compiler Pipeline (Lexer → Parser → Semantic → TypeCheck → IR)
    │
    ▼
  LLVM IR Generator
    │
    ▼
  LLVM IR
    │
    ▼
  LLVM Optimizer (O0, O1, O2, O3)
    │
    ▼
  LLVM Code Generator
    │
    ▼
  Object File (.o)
    │
    ▼
  Linker (ld, lld)
    │
    ▼
  Native Executable
```

### LLVM IR Generation

The I compiler will generate LLVM IR from the typed AST or optimized IR:

#### Type Mapping

| I Type | LLVM Type |
|--------|-----------|
| int | i64 |
| float | double |
| bool | i1 |
| char | i32 |
| string | %struct.String* |
| List<T> | %struct.List* |
| Dict<K,V> | %struct.Dict* |
| T? | %struct.Optional* |
| Function | function type |
| Struct | %struct.Name* |
| Class | %struct.Name* |

#### Value Representation

```
// Integers: unboxed on stack, boxed on heap
// Floats: unboxed (double) on stack, boxed on heap
// Booleans: i1
// Strings: heap-allocated structs with refcount
// Objects: heap-allocated with vtable pointer
```

#### Memory Management in Native Code

```
// Reference counting for deterministic cleanup
// GC for cycle collection
// Stack scanning for GC roots
// Write barriers for generational GC
```

#### Bounds Checking

```
// Every array access generates:
if (index < 0 || index >= list->length) {
    throw_index_error(index, list->length);
}
return list->elements[index];
```

### LLVM Optimization Pipeline

The I compiler will leverage LLVM's optimization passes:

1. **InstCombine**: Combine instructions
2. **SimplifyCFG**: Simplify control flow
3. **GVN**: Global value numbering
4. **LICM**: Loop-invariant code motion
5. **SROA**: Scalar replacement of aggregates
6. **Inliner**: Function inlining
7. **AutoVectorization**: SIMD vectorization
8. **DeadCodeElimination**: Remove dead code

### Runtime Library

The native compiler will link against a C runtime library:

```
libi_runtime.a {
    // Memory management
    i_alloc(size) -> void*
    i_realloc(ptr, size) -> void*
    i_free(ptr)
    i_gc_collect()

    // String operations
    i_string_new(data, length) -> String*
    i_string_concat(a, b) -> String*
    i_string_compare(a, b) -> bool

    // List operations
    i_list_new(element_size) -> List*
    i_list_append(list, element) -> void
    i_list_get(list, index) -> void*

    // Exception handling
    i_throw(exception)
    i_try_catch(handler)

    // I/O
    i_print(value)
    i_read_file(path) -> String*

    // Type checking
    i_type_check(value, expected_type) -> bool

    // Debug info
    i_debug_breakpoint()
    i_debug_log(message)
}
```

## Custom Backend

### When to Build a Custom Backend

Consider a custom backend when:

1. LLVM compilation speed becomes a bottleneck
2. Binary size needs to be minimized
3. I-specific optimizations are needed
4. Self-hosting is a priority

### Custom Backend Architecture

```
I Optimized IR
    │
    ▼
  Instruction Selection (IR → target instructions)
    │
    ▼
  Register Allocation (graph coloring / linear scan)
    │
    ▼
  Instruction Scheduling
    │
    ▼
  Assembly Generation
    │
    ▼
  Object File Generation (ELF, Mach-O, PE)
    │
    ▼
  Linker
    │
    ▼
  Native Executable
```

### Target Platforms (Custom Backend)

| Platform | Architecture | Priority |
|----------|-------------|----------|
| Linux | x86_64 | High |
| macOS | ARM64 (Apple Silicon) | High |
| Windows | x86_64 | High |
| Linux | ARM64 | Medium |
| Linux | RISC-V | Low |
| WebAssembly | WASM | Medium |

### I-Specific Optimizations

1. **Null check elimination**: Remove redundant null checks after type narrowing
2. **Bounds check elimination**: Remove bounds checks provably within range
3. **Union type specialization**: Generate specialized code for union types
4. **Optional unwrapping**: Optimize optional value access patterns
5. **Generic specialization**: Generate specialized code for concrete generic types

## Phase 1: Bytecode VM (Current)

### Status

The bytecode VM is the current and primary execution target.

### Capabilities

- Fast compilation (< 100ms for typical programs)
- Portable execution (any platform with Python/C runtime)
- Full debugging support
- Garbage collection
- Exception handling
- Module system

### Limitations

- 5-10x slower than native code for compute-bound tasks
- Requires VM runtime
- Larger memory footprint

## Phase 2: LLVM Integration

### Prerequisites

1. Stable AST and type system
2. Complete standard library
3. Working bytecode VM as reference implementation
4. Comprehensive test suite

### Implementation Steps

1. **LLVM IR Generator**: Convert typed AST to LLVM IR
2. **Runtime Library**: Implement C runtime library
3. **Linker Integration**: Support linking against system libraries
4. **Debug Info**: Generate DWARF debug information
5. **Optimization Levels**: Support -O0, -O1, -O2, -O3
6. **Cross-Compilation**: Support building for different targets
7. **Build System**: Integrate with the I build system

### Estimated Timeline

- LLVM IR Generator: 3-6 months
- Runtime Library: 2-4 months
- Debug Info: 1-2 months
- Optimization: 2-3 months
- Cross-compilation: 2-3 months
- **Total**: 12-18 months

## Phase 3: Custom Backend (Optional)

### Prerequisites

- Successful LLVM backend
- Understanding of I-specific optimization opportunities
- Self-hosting compiler
- Sufficient engineering resources

### Implementation Steps

1. **Instruction Selection**: Define target instruction set
2. **Register Allocator**: Implement graph coloring or linear scan
3. **Instruction Scheduler**: Optimize instruction ordering
4. **Object File Writer**: Generate ELF/Mach-O/PE files
5. **Linker**: Support static and dynamic linking
6. **Optimization Passes**: I-specific optimizations

### Estimated Timeline

- Instruction Selection: 3-6 months
- Register Allocator: 2-4 months
- Object File Writer: 2-3 months
- Linker: 2-3 months
- Optimizations: 3-6 months
- **Total**: 12-24 months

## Trade-off Analysis

### LLVM vs Custom Backend

| Aspect | LLVM | Custom Backend |
|--------|------|----------------|
| Compilation Speed | Slow (1-10s) | Fast (100ms-1s) |
| Execution Speed | Excellent | Excellent |
| Binary Size | Moderate | Small |
| Platform Support | Broad | Limited initially |
| Optimization Quality | Excellent | Variable |
| Debug Info | Excellent (DWARF) | Manual implementation |
| Maintenance | Low (upstream) | High (self-maintained) |
| Self-Hosting | No (C++ dependency) | Yes (can be in I) |
| Development Time | 12-18 months | 12-24 months |
| Risk | Low | Medium |

### When to Use Each

**Use LLVM when:**
- Compilation speed is not critical
- Broad platform support is needed
- Maximum optimization quality is needed
- Debug info is important

**Use Custom Backend when:**
- Compilation speed is critical (e.g., hot reload)
- Binary size must be minimized
- I-specific optimizations are needed
- Self-hosting is a priority

### Hybrid Approach

The recommended approach is to maintain both backends:

1. **LLVM backend** for production builds (optimized, debug info)
2. **Custom backend** for development builds (fast compilation, hot reload)

## Target Platforms

### Phase 2 (LLVM)

| Platform | Architecture | Status |
|----------|-------------|--------|
| Linux | x86_64 | Priority 1 |
| macOS | ARM64 | Priority 1 |
| macOS | x86_64 | Priority 2 |
| Windows | x86_64 | Priority 2 |
| Linux | ARM64 | Priority 3 |
| WebAssembly | WASM | Priority 3 |

### Phase 3 (Custom)

| Platform | Architecture | Status |
|----------|-------------|--------|
| Linux | x86_64 | Priority 1 |
| macOS | ARM64 | Priority 2 |
| Windows | x86_64 | Priority 2 |

## Build System Integration

### Compilation Modes

```
i build                    # Default: bytecode
i build --native           # Native compilation (LLVM)
i build --native -O2       # Native with optimizations
i build --native --target  # Cross-compilation
i build --dev              # Development (fast compilation)
i build --release          # Release (maximum optimization)
```

### Build Profiles

```
Development {
    backend: bytecode
    optimization: none
    debug_info: full
    compilation_speed: fast
}

Release {
    backend: llvm
    optimization: O3
    debug_info: minimal
    execution_speed: fast
}

Production {
    backend: llvm
    optimization: O3
    debug_info: none
    execution_speed: fastest
    binary_size: smallest
}
```

## Debugging Native Code

### DWARF Debug Info

The LLVM backend will generate DWARF debug info for use with GDB and LLDB:

- Source file mapping
- Line number information
- Variable locations
- Type descriptions
- Function parameters
- Struct layouts

### Source Mapping

Every native instruction will be mapped back to the I source code:

```
// I source:
shyira x = 42
andika(x)

// Assembly with source mapping:
; main.i:4:4
movl $42, -8(%rbp)    ; x = 42
; main.i:5:4
movl -8(%rbp), %edi   ; load x
call i_print          ; print(x)
```

### Core Dump Analysis

Native crashes will produce useful diagnostics:

```
Signal: SIGSEGV (Segmentation fault)
Location: main.i:12:8
Expression: list[index]
Reason: Index out of bounds (index=10, length=5)
Suggestion: Check the index value before accessing the list.
```

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
