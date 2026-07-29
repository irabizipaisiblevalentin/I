# I Virtual Machine (IVM) — Implementation Guide

**Sprint 8 | I Programming Language**

The IVM is the official bytecode execution engine and reference runtime for the I Programming Language. It is a stack-based virtual machine with generational garbage collection, cooperative fiber scheduling, a debug/profiling infrastructure, and a custom binary bytecode format.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          VMInstance                                  │
│  (Main entry point — assembles all subsystems)                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Config   │  │  Context  │  │ Executor  │  │ Runtime  │           │
│  │(VMConfig) │  │(VMContext)│  │(VMExecut) │  │(VMRuntm) │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │    GC     │  │  Loader   │  │  Debug   │  │ Profiler │           │
│  │(GarbageC) │  │(VMLoader) │  │(VMDebug) │  │(VMProfil)│           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                         │
│  │  Stats    │  │ Scheduler │  │ Bytecode │                         │
│  │(VMStatist)│  │(VMSchedul)│  │(IVMByte) │                         │
│  └──────────┘  └──────────┘  └──────────┘                         │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │              Memory Subsystem                            │       │
│  │  Stack │ CallFrame │ Heap │ StringPool │ ConstantPool    │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │              Object System                               │       │
│  │  VMObject │ VMString │ VMList │ VMMap │ VMSet │ VMTuple  │       │
│  │  VMStruct │ VMClosure │ VMException │ VMIterator         │       │
│  └─────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```python
from vm import VMConfig, VMInstance

# Create a VM with default settings
vm = VMInstance()

# Execute a chunk
result = vm.execute(chunk)

# Or compile and run source directly
result = vm.run_source("andika(2 + 3)")

# Get a performance report
print(vm.format_report())
```

---

## Module Guide

### 1. VMConfig (`vm_config.py`)

Configuration dataclass with `__slots__` for memory efficiency. All fields accept `**kwargs`.

| Field | Type | Default | Description |
|---|---|---|---|
| `max_stack_depth` | `int` | `1024` | Max values on the operand stack |
| `max_call_depth` | `int` | `256` | Max nested function calls |
| `max_globals` | `int` | `65536` | Max number of global variables |
| `heap_initial_size` | `int` | `1048576` | Initial heap allocation (bytes) |
| `heap_growth_factor` | `float` | `1.5` | Heap growth multiplier |
| `gc_threshold` | `int` | `1024` | Object count that triggers GC |
| `gc_generational` | `bool` | `True` | Enable generational GC |
| `gc_incremental` | `bool` | `False` | Enable incremental GC (future) |
| `gc_stw_limit_ms` | `float` | `10.0` | Stop-the-world pause limit (ms) |
| `enable_debug` | `bool` | `False` | Enable debugger |
| `enable_profiler` | `bool` | `False` | Enable profiler |
| `enable_stats` | `bool` | `True` | Enable statistics tracking |
| `enable_bytecode_verification` | `bool` | `True` | Enable bytecode verifier |
| `resource_limits` | `dict` | `{}` | Arbitrary resource limits |

**Builder methods:** `with_debug()`, `with_profiler()` — return `self` for chaining.

```python
config = VMConfig(max_stack_depth=2048).with_debug().with_profiler()
vm = VMInstance(config)
```

---

### 2. VMContext (`vm_context.py`)

Shared execution context holding all mutable state for a VM session.

**Internal state:**
- `_globals: dict[str, Any]` — user-defined global variables
- `_builtins: dict[str, Any]` — registered builtin functions
- `_modules: dict[str, Any]` — loaded module export tables
- `_string_pool: dict[str, str]` — interned strings by index
- `_ffi_registry: dict[str, Any]` — foreign function interface registry
- `_metadata: dict[str, Any]` — arbitrary metadata

**Key methods:**
```python
ctx.register_builtin("my_fn", lambda x: x + 1)
ctx.get_builtin("my_fn")(10)  # → 11

idx = ctx.intern_string("hello")  # → 0
ctx.get_interned(0)               # → "hello"

ctx.register_ffi("native_add", c_add_fn)
ctx.register_module("mymod", {"exported": 42})
```

String interning uses a monotonically-increasing integer ID scheme. Reverse lookup is available via `_interned_strings`.

---

### 3. Memory Subsystem (`vm_memory.py`)

#### Stack

Fixed-size value stack with overflow protection. Pre-allocates `_data` list to `max_size`. Popped slots are nullified for GC safety.

```python
stack = Stack(max_size=1024)
stack.push(42)
stack.push("hello")
stack.pop()       # → "hello"
stack.peek()      # → 42
stack.peek_at(0)  # → 42 (top)
stack.dup()       # duplicates top
stack.swap()      # swaps top two
stack.rot_three() # [a, b, c] → [b, c, a]
```

**Operations:**
- `push(value)` — raises `StackOverflowError` if full
- `pop()` — raises `IndexError` if empty; nulls slot for GC
- `peek()` / `peek_at(offset)` — read without popping
- `set_at(offset, value)` — write relative to top
- `truncate(new_size)` — drops elements above new_size
- `to_list()` — snapshot of current elements

#### CallFrame

Single activation record on the call stack. Holds chunk, instruction pointer, base pointer, function name, line number, and optional closure reference.

```python
frame = CallFrame(chunk, ip=0, base_pointer=0, function_name="main")
frame.advance()          # ip += 1
opcode_val = frame.read_byte()  # reads opcode.value, advances IP
```

#### Heap

Simple object heap with allocation tracking. Tracks allocated count, max size, and collection count.

```python
heap = Heap(initial_size=1024*1024, threshold=1024)
heap.allocate(vm_object)
heap.needs_gc       # → True when allocated >= threshold
freed = heap.collect()  # removes None slots
```

#### StringPool

Bidirectional interned string pool. Maps string → ID and ID → string.

#### ConstantPool

Deduplicating constant pool. `add()` returns existing index if same value+type already present.

---

### 4. Object System (`vm_objects.py`)

All heap-allocated VM object types inherit from `VMObject` with built-in GC support (three fields: `_gc_next`, `_gc_marked`, `_gc_gen`). All use `__slots__`.

| Object | Description | Key Methods |
|---|---|---|
| `VMString` | Immutable string wrapper | `value`, `__eq__`, `__hash__`, `__len__` |
| `VMList` | Mutable list | `get(i)`, `set(i, v)`, `append(v)`, `slice(s, e, st)`, `to_list()` |
| `VMMap` | Dictionary (uses `id()` for VMObject keys) | `get(k)`, `set(k, v)` |
| `VMSet` | Set (stores hash/id values) | `add(v)` |
| `VMTuple` | Immutable tuple wrapper | `elements` (read-only) |
| `VMStruct` | Named struct with declared fields | `get_field(n)`, `set_field(n, v)` |
| `VMClosure` | Function chunk + free variables | `capture(values)`, `chunk`, `name`, `arity` |
| `VMException` | Exception with stack trace + cause chain | `with_cause(exc)`, `stack_trace` |
| `VMIterator` | Iterator for `for-in` loops | `has_next()`, `next()` |

**VMIterator** supports: `list`, `VMList`, `tuple`, `VMTuple`, `str`, `VMMap` (iterates keys).

Each object overrides `gc_trace() -> list[Any]` to return its referents for the mark phase.

---

### 5. Garbage Collector (`vm_gc.py`)

Generational mark-sweep garbage collector with two generations.

**Generations:**
- **Young gen (gen 0):** Nursery for newly allocated objects
- **Old gen (gen 1):** Long-lived objects promoted after surviving `_promotion_threshold` (2) minor GCs

**Collection types:**
- **Minor GC** (`collect_young`): Mark-sweep on young gen only. Survivors are promoted to old gen every 2 collections.
- **Major GC** (`collect_all`): Mark-sweep on both generations.
- **Smart dispatch** (`collect`): Minor if generational mode enabled, full otherwise.

**Mark phase:** Iterative DFS using `gc_trace()` on each `VMObject`. Uses an explicit stack (not recursion) to avoid C stack overflow.

**Sweep phase:** Unmarks and untracks unmarked objects from the heap.

```python
gc = GarbageCollector(heap, threshold=1024, generational=True)
gc.allocate(vm_obj)       # allocates in young gen
gc.promote(vm_obj)        # moves to old gen
gc.collect_young()        # minor GC
gc.collect_all()          # major GC
print(gc.format_stats())  # human-readable stats
```

**GCStats** tracks: collections (young/major), bytes collected, pause time, objects alive, heap size.

---

### 6. Executor (`vm_executor.py`)

The core execution engine — a dispatch loop that executes bytecode instructions.

**Entry point:** `run(chunk) -> Any` — pushes a `<module>` frame, runs the dispatch loop, returns the top of the stack.

**Frame management:**
- `_push_frame(chunk, name, closure)` — checks `max_call_depth`, creates `CallFrame`
- `_pop_frame()` — pops frame, truncates stack to base pointer
- `call_function(closure, arg_count)` — validates arity, pushes new frame
- `call_native(func, arg_count)` — pops args, calls Python function, pushes result

**Hook system:** Fires events on every instruction for stats/profiling:
- `"instruction"` → `(opcode_value, ip, chunk_name)`
- `"call"` → `(name, base_pointer)`
- `"return"` → `(name)`

#### Opcode Reference

All 62 opcodes are handled in the dispatch loop. Jump instructions use **absolute positions** (matching the compiler's `_patch_jump` convention).

| Category | Opcodes |
|---|---|
| **Control** | `HALT`, `NOP` |
| **Loads** | `LOAD_CONST`, `LOAD_NULL`, `LOAD_TRUE`, `LOAD_FALSE`, `LOAD_LOCAL`, `LOAD_GLOBAL` |
| **Stores** | `STORE_LOCAL`, `STORE_GLOBAL` |
| **Stack** | `POP`, `DUP`, `SWAP`, `ROT_THREE` |
| **Arithmetic** | `ADD`, `SUB`, `MUL`, `DIV` (÷0 check), `MOD` (%0 check), `NEG` |
| **Bitwise** | `BIT_AND`, `BIT_OR`, `BIT_XOR`, `BIT_NOT`, `LEFT_SHIFT`, `RIGHT_SHIFT` |
| **Comparison** | `EQ`, `NEQ`, `LT`, `LTE`, `GT`, `GTE` |
| **Logical** | `AND`, `OR`, `NOT` |
| **Control flow** | `JUMP`, `JUMP_IF_FALSE`, `JUMP_IF_TRUE`, `JUMP_IF_FALSE_POP`, `LOOP` |
| **Functions** | `CALL` (VMClosure / callable / builtin), `RETURN`, `MAKE_FUNCTION` |
| **Collections** | `BUILD_LIST`, `BUILD_MAP`, `BUILD_SET`, `BUILD_TUPLE`, `GET_ITEM`, `SET_ITEM`, `SLICE` |
| **Attributes** | `GET_ATTR`, `SET_ATTR` |
| **Structs** | `NEW_STRUCT`, `NEW_INSTANCE` (stubs) |
| **Closures** | `MAKE_CLOSURE` (stub) |
| **Iteration** | `GET_ITER`, `FOR_ITER` |
| **Exceptions** | `RAISE`, `SETUP_TRY`, `POP_BLOCK` |

**CALL opcode dispatch:** Three paths:
1. `VMClosure` → pushes a new call frame
2. Python `callable` → calls directly via Python
3. String matching `context.builtins` → looks up and calls

**Error handling:** `VMRuntimeError` carries the call stack for traceback formatting via `format_trace()`.

---

### 7. Debugger (`vm_debug.py`)

Full-featured debug interface with breakpoints, stepping, and watch expressions.

**Breakpoints:**
```python
vm.debugger.add_breakpoint("main.i", 10)
vm.debugger.add_breakpoint("main.i", 20, condition="x > 5")  # conditional
vm.debugger.hit_breakpoint("main.i", 10)  # → True/False
```

**Stepping modes:**
- `step_into()` — breaks on every function call
- `step_over()` — breaks at same or shallower call depth
- `step_out()` — breaks when call depth decreases
- `continue_execution()` — runs until next breakpoint

**Watch expressions:**
```python
vm.debugger.add_watch("x", current_x_value)
vm.debugger.get_watches()  # → [{"name": "x", "value": 42}]
```

**Introspection:**
```python
vm.debugger.get_stack_trace(call_stack)  # → [{"function": "main", "line": 10, "ip": 5}]
vm.debugger.inspect_variable("x", 42)    # → {"name": "x", "type": "int", "repr": "42"}
```

**Events:** Fires `"pause"` and `"resume"` callbacks for UI integration.

---

### 8. Profiler (`vm_profiler.py`)

Function-level performance profiler with hot-spot detection.

```python
vm.profiler.start()
# ... execute code ...
vm.profiler.stop()

print(vm.profiler.format_profile())
# ┌──────────────┬───────┬───────────┬───────────┬──────────┐
# │ Function     │ Calls │ Total (ms)│ Self (ms) │ Avg (ms) │
# ├──────────────┼───────┼───────────┼───────────┼──────────┤
# │ main         │     1 │    12.340 │    12.340 │   12.340 │
# │ helper       │    10 │     5.670 │     5.670 │    0.567 │
# └──────────────┴───────┴───────────┴───────────┴──────────┘

vm.profiler.top_functions(n=5)
vm.profiler.get_hot_spots(threshold=10.0)
```

**ProfileEntry** tracks: name, calls, total_time_ms, self_time_ms, max_time_ms, min_time_ms, instruction_count.

---

### 9. Statistics (`vm_stats.py`)

Runtime statistics engine tracking all execution metrics.

**Tracked metrics:**
- Instructions executed (total + per-opcode histogram)
- Function calls and max call depth
- Stack max depth
- Exceptions raised and caught
- Execution time (live — uses `time.monotonic()`)
- Instructions per second
- GC stats and bytecode size

```python
vm.stats.record_instruction(opcode_value)
vm.stats.record_call()
vm.stats.record_return()
vm.stats.get_top_opcodes(n=10)  # → [(opcode_val, count), ...]
print(vm.stats.format_summary())
```

---

### 10. Loader & Verifier (`vm_loader.py`)

Binary bytecode serialization/deserialization with verification.

#### Binary Format

```
┌──────────────────────────────────────────────────────┐
│ Header (16 bytes)                                     │
│   Magic: "IBCM" (4 bytes)                             │
│   Version: 1 (2 bytes)                                │
│   Padding: 2 bytes                                    │
│   Reserved: 2 × 4 bytes                              │
├──────────────────────────────────────────────────────┤
│ Constants Section                                      │
│   Count: 4 bytes (big-endian uint32)                  │
│   Per constant:                                        │
│     Type tag: 1 byte                                  │
│       0 = null     1 = int       2 = float            │
│       3 = bool     4 = string                         │
│     Payload: (varies by type)                         │
│       int:  8 bytes (big-endian int64)                │
│       float: 8 bytes (big-endian float64)             │
│       bool: 1 byte (0x00/0x01)                        │
│       string: 2-byte length + UTF-8 bytes             │
├──────────────────────────────────────────────────────┤
│ Code Section                                           │
│   Count: 4 bytes (big-endian uint32)                  │
│   Per instruction:                                     │
│     Opcode: 1 byte (high bit = has-arg flag)          │
│     If has-arg: arg as 2-byte big-endian uint16       │
├──────────────────────────────────────────────────────┤
│ Name Section                                           │
│   Length: 2 bytes + UTF-8 name bytes                  │
└──────────────────────────────────────────────────────┘
```

**Instruction encoding:** The high bit (`0x80`) of the opcode byte indicates whether a 2-byte argument follows. When set, the opcode value is `byte & 0x7F`.

**VMVerifier** checks:
1. Each instruction is an `Instruction` instance
2. Opcode value is in valid range (0–61)
3. Required opcodes have non-None arguments

```python
loader = VMLoader(enable_verification=True)
loader.save_file(chunk, "output.ibcm")
loaded = loader.load_file("output.ibcm")
```

---

### 11. Runtime (`vm_runtime.py`)

Builtin functions and module management. Builtins have both English and Kinyarwanda names.

#### Core Builtins

| English | Kinyarwanda | Signature | Description |
|---|---|---|---|
| `print` | `andika` | `*args` | Print to stdout |
| `len` | `ishobora` | `collection` | Length of collection |
| `type` | `tangura` | `value` | Type code: 0=None, 1=bool, 2=int, 3=float, 4=str, 5=list, 6=map, 7=tuple, 8=struct, 9=closure |
| `int` | — | `value` | Convert to int |
| `float` | — | `value` | Convert to float |
| `str` | — | `value` | Convert to string |
| `bool` | — | `value` | Convert to bool |
| `abs` | — | `value` | Absolute value |
| `min` | — | `*values` | Minimum (multi-arg or single list) |
| `max` | — | `*values` | Maximum (multi-arg or single list) |
| `sum` | `soma` | `*values` | Sum (multi-arg or single list) |
| `repr` | `uburyo` | `value` | String representation |
| `range_check` | `igenzura` | `val, low, high` | `low <= val <= high` |
| `time` | `igihe` | — | Current time (seconds) |
| `random` | `izuburamwaka` | `low?, high?` | Random int (0–100 or range) |
| `error` | `kubura` | `message` | Raise exception |
| `assert` | `gukora` | `condition` | Assert (raises on falsy) |

#### Math Builtins

| Name | Function |
|---|---|
| `math_abs` | `abs()` |
| `math_sqrt` | Square root |
| `math_sin` / `math_cos` / `math_tan` | Trigonometry |
| `math_log` | Natural logarithm |
| `math_exp` | Exponential |
| `math_pow` | Power (2 args) |

---

### 12. Scheduler (`vm_scheduler.py`)

Cooperative fiber/coroutine scheduler (future-ready).

**Fiber states:** `CREATED → READY → RUNNING → FINISHED` (or `SUSPENDED`)

```python
scheduler = VMScheduler()
fiber1 = scheduler.spawn(lambda: compute_a())
fiber2 = scheduler.spawn(lambda: compute_b())
scheduler.run_all()  # runs all fibers sequentially
```

**Current behavior:** Fibers run to completion (no preemption). Time slicing is tracked but not enforced. The `SUSPENDED` state is defined for future async/await support.

---

### 13. Extended Bytecode (`vm_bytecode.py`)

IVM-specific opcode definitions extending the base compiler's `OpCode`.

**89 opcodes total:**

**Core (0–61):** Matches the base compiler `OpCode` enum — all standard operations.

**Extended (64–88):** Future instruction set for advanced features:

| Category | Opcodes |
|---|---|
| **OOP** | `INVOKE`, `INVOKE_VIRTUAL`, `INVOKE_INTERFACE`, `CHECK_CAST`, `INSTANCE_OF` |
| **Memory** | `NEW_ARRAY`, `NEW_OBJECT`, `GET_FIELD`, `PUT_FIELD`, `GET_STATIC`, `PUT_STATIC` |
| **Registers** | `LOAD_FAST`, `STORE_FAST`, `LOAD_ARG`, `STORE_ARG` |
| **Frames** | `ENTER_FRAME`, `EXIT_FRAME` |
| **Async** | `YIELD`, `AWAIT`, `SEND`, `THROW`, `FINALLY` |
| **Concurrency** | `LOCK`, `UNLOCK` |

**IVMInstruction** extends the base `Instruction` with: `arg2` (second operand), `source_file` (source mapping).

**IVMChunk** adds: nested function chunks, line table, source file tracking, and version metadata.

---

### 14. VMInstance (`vm_instance.py`)

The main entry point that assembles all subsystems into a complete execution environment.

**Initialization:**
1. Creates all subsystems from `VMConfig`
2. Wires GC to executor
3. Starts profiler if enabled
4. Sets up call/return/instruction hooks for stats and profiling

**Execution methods:**
```python
vm = VMInstance()

# Execute a pre-compiled chunk
result = vm.execute(chunk)

# Compile and run source code
result = vm.run_source("andika(2 + 3)")

# Load and run a bytecode file
result = vm.run_file("program.ibcm")
```

**Introspection:**
```python
vm.set_global("x", 42)
vm.get_global("x")  # → 42

print(vm.format_report())
# ╔══════════════════════════════════════════╗
# ║         IVM Execution Report             ║
# ╠══════════════════════════════════════════╣
# ║ Instructions:    1234                    ║
# ║ Function calls:  56                      ║
# ║ Execution time:  12.34 ms                ║
# ║ IPC:             100.0                   ║
# ╚══════════════════════════════════════════╝
```

**Reset:** Clears stack, call stack, globals; recreates stats and GC.

---

## Test Suite

**161 tests** across 20 test classes, covering every module.

| Test Class | Tests | Coverage |
|---|---|---|
| `TestStack` | 13 | push/pop, peek, dup, swap, rot_three, overflow/underflow, clear, truncate |
| `TestCallFrame` | 4 | properties, advance, read_byte, repr |
| `TestHeap` | 3 | allocate, collect, stats |
| `TestStringPool` | 3 | intern dedup, lookup, resolve |
| `TestConstantPool` | 3 | add/get, dedup, len |
| `TestVMObjects` | 19 | all 10 object types, GC marking |
| `TestGarbageCollector` | 6 | minor/major GC, stats, promotion |
| `TestVMDebugger` | 14 | breakpoints, stepping, watches, introspection |
| `TestVMProfiler` | 7 | start/stop, calls, hot spots, format |
| `TestVMStatistics` | 8 | all metrics, format, to_dict |
| `TestVMVerifier` | 2 | valid/invalid chunks |
| `TestVMLoader` | 6 | serialize/deserialize, file I/O, error detection |
| `TestVMRuntime` | 5 | builtins, modules, exceptions |
| `TestVMScheduler` | 4 | spawn, run_all, step, stats |
| `TestVMContext` | 5 | globals, builtins, modules, interning, metadata |
| `TestVMExecutor` | 3 | push/pop, stack, hooks |
| `TestVMInstance` | 16 | create, config, execute, introspection, reset |
| `TestIVMBytecode` | 8 | opcodes, instructions, chunks, line tables |
| `TestVMConfig` | 3 | defaults, builder methods |
| `TestVMIntegration` | 29 | end-to-end: arithmetic, jumps, collections, globals, profiling, debugging |

**Run tests:**
```bash
python -m pytest tests/unit/test_vm_sprint8.py -v
```

---

## Design Decisions

### Absolute Jump Positions

Jump instructions (`JUMP`, `JUMP_IF_FALSE`, etc.) use **absolute target positions**, not relative offsets. This matches the compiler's `_patch_jump` convention where the argument is set to `len(chunk.code)` at the target position.

### Opcode Enum with auto()

The `OpCode` enum uses Python's `auto()` starting from 1. The executor dispatches on `instruction.opcode` (the enum value), not raw integers. The `Instruction` dataclass stores `opcode: OpCode`, so `code[frame.ip]` returns an `Instruction` object — the executor accesses `.opcode` and `.arg` from it.

### Memory Efficiency

All major classes use `__slots__` to minimize per-instance memory overhead. The stack nulls popped slots to avoid dangling references for the GC.

### GC Safety

Stack slots are explicitly nulled on pop. The mark-sweep collector uses iterative DFS (not recursion) to avoid C stack overflow on deeply linked object graphs.

---

## File Index

| File | Purpose |
|---|---|
| `src/vm/__init__.py` | Package exports: VMConfig, VMContext, VMInstance |
| `src/vm/vm_config.py` | VM configuration dataclass |
| `src/vm/vm_context.py` | Shared execution context |
| `src/vm/vm_memory.py` | Stack, CallFrame, Heap, StringPool, ConstantPool |
| `src/vm/vm_objects.py` | All VM object types (10 classes) |
| `src/vm/vm_gc.py` | Generational mark-sweep garbage collector |
| `src/vm/vm_executor.py` | Instruction dispatch loop (62 opcodes) |
| `src/vm/vm_debug.py` | Debugger: breakpoints, stepping, watches |
| `src/vm/vm_profiler.py` | Function-level performance profiler |
| `src/vm/vm_stats.py` | Runtime statistics engine |
| `src/vm/vm_loader.py` | Binary bytecode loader, verifier, serializer |
| `src/vm/vm_runtime.py` | Builtins, modules, exception formatting |
| `src/vm/vm_scheduler.py` | Cooperative fiber scheduler |
| `src/vm/vm_bytecode.py` | Extended IVM opcodes (89 total) and chunks |
| `src/vm/vm_instance.py` | Main VM entry point |
| `tests/unit/test_vm_sprint8.py` | Test suite (161 tests) |
