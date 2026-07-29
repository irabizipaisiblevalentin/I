# Memory Model Design

This document specifies the memory management model of the I Programming Language, including stack, heap, garbage collection, and ownership.

## Table of Contents

- [Overview](#overview)
- [Memory Architecture](#memory-architecture)
- [Stack Memory](#stack-memory)
- [Heap Memory](#heap-memory)
- [Garbage Collection](#garbage-collection)
- [Reference Counting](#reference-counting)
- [Ownership Model](#ownership-model)
- [Memory Safety](#memory-safety)
- [Resource Cleanup](#resource-cleanup)
- [Future Optimizations](#future-optimizations)

## Overview

The I language uses automatic memory management. The developer does not manually allocate or deallocate memory. The runtime system handles memory through a combination of:

1. **Stack allocation** for local variables and function parameters
2. **Heap allocation** for objects, closures, and dynamic data
3. **Garbage collection** for automatic memory reclamation
4. **Reference counting** for deterministic cleanup of resources

### Design Goals

1. **Safety**: No memory leaks, no dangling pointers, no use-after-free
2. **Predictability**: Deterministic behavior for resource management
3. **Performance**: Low overhead for typical programs
4. **Simplicity**: Developer should not need to think about memory
5. **Extensibility**: Support for future optimizations like ownership

## Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        I Program Memory                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Stack Memory                       │   │
│  │  - Local variables                                   │   │
│  │  - Function parameters                               │   │
│  │  - Return addresses                                  │   │
│  │  - Temporary values                                  │   │
│  │  - Fixed size per frame                              │   │
│  │  - LIFO order                                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Heap Memory                        │   │
│  │  - Objects (structs, classes, enums)                  │   │
│  │  - Closures                                          │   │
│  │  - Lists, Dicts, Sets                                │   │
│  │  - Strings (long)                                    │   │
│  │  - Dynamic allocations                               │   │
│  │  - Managed by Garbage Collector                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    Constant Pool                      │   │
│  │  - String literals                                    │   │
│  │  - Numeric constants                                 │   │
│  │  - Module constants                                  │   │
│  │  - Immutable                                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Stack Memory

### Stack Frame Layout

Each function call creates a stack frame:

```
┌─────────────────────────────┐  High Address
│         Return Address      │
├─────────────────────────────┤
│         Saved Frame Pointer │
├─────────────────────────────┤
│         Local Variable 1    │
├─────────────────────────────┤
│         Local Variable 2    │
├─────────────────────────────┤
│         ...                 │
├─────────────────────────────┤
│         Local Variable n    │
├─────────────────────────────┤
│         Temporary Values    │
├─────────────────────────────┤
│         Operand Stack       │
└─────────────────────────────┘  Low Address (Stack Pointer)
```

### Stack Allocation Rules

1. **Primitive values** (int, float, bool, char) are always stack-allocated
2. **Small structs** (≤ 128 bytes) are stack-allocated when possible
3. **Function parameters** are passed on the stack
4. **Temporary values** during expression evaluation use the operand stack

### Stack Size Limits

```
StackConfig {
    initial_size: 1 MB          // Initial stack size per thread
    max_frame_size: 64 KB       // Maximum size of a single frame
    max_depth: 10,000           // Maximum call depth
    overflow_strategy: ERROR    // What to do on overflow
}
```

### Stack Overflow Detection

```
function checkStackOverflow():
    current_usage = stack_pointer - stack_base
    if current_usage > stack_size * 0.9:
        emitWarning(RUN001, "Stack usage at 90% capacity")

    if stack_pointer < stack_limit:
        throw StackOverflowError("Stack overflow detected")
```

### Value Types vs Reference Types

| Type | Storage | Copy Semantics |
|------|---------|---------------|
| int | Stack | Value copy |
| float | Stack | Value copy |
| bool | Stack | Value copy |
| char | Stack | Value copy |
| null | Stack | Value copy |
| struct | Stack (if small) | Value copy |
| class | Heap | Reference copy |
| list | Heap | Reference copy |
| dict | Heap | Reference copy |
| set | Heap | Reference copy |
| string | Heap (or inline) | Reference copy |
| closure | Heap | Reference copy |
| tuple | Stack (if small) | Value copy |

## Heap Memory

### Object Representation

```
┌─────────────────────────────────────────┐
│            Object Header                 │
├─────────────────────────────────────────┤
│  Type ID        (4 bytes)               │
│  Reference Count (4 bytes)              │
│  GC Mark         (1 byte)               │
│  Padding         (3 bytes)              │
├─────────────────────────────────────────┤
│            Object Data                   │
│  Field 1        (size varies)           │
│  Field 2        (size varies)           │
│  ...                                   │
│  Field n        (size varies)           │
└─────────────────────────────────────────┘
```

### Allocation Strategy

The heap uses a **generational allocator** with multiple spaces:

```
HeapSpaces {
    nursery: NurserySpace     // New objects (< 32KB)
    young: YoungSpace         // Survived one GC cycle
    old: OldSpace             // Survived multiple GC cycles
    large: LargeObjectSpace   // Large objects (> 32KB)
    code: CodeSpace           // Compiled code (future)
}
```

### Nursery Space

- **Size**: 256 KB (configurable)
- **Allocation**: Bump pointer (very fast)
- **Collection**: When full, promote survivors to young space
- **Algorithm**: Copy collector

### Young Space

- **Size**: 4 MB (configurable)
- **Allocation**: After nursery collection
- **Collection**: When full or periodically
- **Algorithm**: Copy collector

### Old Space

- **Size**: 256 MB (configurable, growable)
- **Allocation**: Objects that survive multiple young collections
- **Collection**: Mark-sweep, less frequent
- **Algorithm**: Incremental mark-sweep

### Large Object Space

- **Threshold**: Objects > 32 KB
- **Allocation**: Direct allocation from OS
- **Collection**: Collected with old space
- **Fragmentation**: Managed with free lists

### Allocation Algorithm

```
function allocateObject(type_info: TypeInfo, size: int) -> ObjectRef:
    // Check if large object
    if size > LARGE_OBJECT_THRESHOLD:
        return allocateLargeObject(type_info, size)

    // Try nursery allocation
    if nursery.hasSpace(size):
        return nursery.allocate(type_info, size)

    // Nursery is full - trigger GC
    collectNursery()

    // Retry
    if nursery.hasSpace(size):
        return nursery.allocate(type_info, size)

    // Still no space - allocate in young space
    if young.hasSpace(size):
        return young.allocate(type_info, size)

    // Young space is full - trigger full GC
    collectYoung()

    // Final attempt
    return young.allocate(type_info, size)
```

### String Interning

Short strings are interned (deduplicated) to save memory:

```
StringConfig {
    intern_threshold: 32        // Intern strings shorter than this
    intern_table_size: 10000    // Size of intern table
    intern_max_memory: 1 MB     // Maximum memory for interned strings
}
```

## Garbage Collection

### GC Strategy: Generational

The I runtime uses a **generational garbage collector** based on the generational hypothesis: most objects die young.

### Collection Phases

#### Phase 1: Nursery Collection (Fast)

```
function collectNursery():
    // Stop the world (briefly)
    pauseThreads()

    // Copy live objects from nursery to young space
    for object in nursery:
        if object.isReferenced():
            new_location = young.copy(object)
            updateReferences(object, new_location)

    // Clear nursery
    nursery.clear()

    // Resume threads
    resumeThreads()
```

**Pause time**: < 1ms for typical programs

#### Phase 2: Young Collection (Medium)

```
function collectYoung():
    pauseThreads()

    // Mark phase
    for root in globalRoots:
        markReachable(root)

    for thread in threads:
        for root in thread.stackRoots:
            markReachable(root)

    // Sweep phase
    for object in young:
        if not object.isMarked():
            young.free(object)
        else:
            // Promote to old space if old enough
            if object.age > PROMOTION_THRESHOLD:
                old.copy(object)

    resumeThreads()
```

**Pause time**: < 5ms for typical programs

#### Phase 3: Old Collection (Infrequent)

```
function collectOld():
    // Incremental mark-sweep
    // Runs in background thread
    // Processes work in small increments

    for increment in range(MARK_INCREMENT):
        if marking_queue.isEmpty():
            break
        object = marking_queue.dequeue()
        markReferences(object)

    if marking_queue.isEmpty():
        // Mark phase complete - sweep
        sweepOldSpace()
        gc_phase = SWEEPING
    else:
        // Continue in next increment
        gc_phase = MARKING
```

**Pause time**: < 10ms per increment, spread over multiple increments

### Root Set

The GC tracks roots from:

1. **Global variables**: All module-level variables
2. **Thread stacks**: All local variables in active stack frames
3. **CPU registers**: Values currently in registers
4. **C API roots**: Objects referenced from native code
5. **Weak references**: Tracked separately

### Write Barrier

When an old-space object references a young-space object, a write barrier is installed:

```
function writeBarrier(obj: Object, field: int, value: Object):
    // Store the value
    obj.fields[field] = value

    // If old-space object references young-space object
    if obj.isInOldSpace() and value.isInYoungSpace():
        // Add to remembered set
        rememberedSet.add(obj)
```

### GC Triggers

| Trigger | Action |
|---------|--------|
| Nursery full | Nursery collection |
| Young space > 80% | Young collection |
| Old space > 70% | Full old collection |
| Allocation failure | Emergency collection |
| Manual trigger | GC.collect() |

### GC Metrics

```
GCMetrics {
    nursery_collections: int
    young_collections: int
    old_collections: int
    total_bytes_allocated: long
    total_bytes_freed: long
    current_heap_size: long
    pause_time_total: long
    pause_time_max: long
}
```

## Reference Counting

### Purpose

Reference counting provides **deterministic cleanup** for resources that need immediate release:

- File handles
- Network connections
- Database connections
- Locks/mutexes

### Implementation

Each heap object has a reference count:

```
ObjectHeader {
    type_id: int
    ref_count: int          // Reference count
    gc_mark: byte           // GC mark bit
}
```

### Reference Count Operations

```
function retain(obj: ObjectRef):
    if obj != null:
        obj.header.ref_count += 1

function release(obj: ObjectRef):
    if obj != null:
        obj.header.ref_count -= 1
        if obj.header.ref_count == 0:
            finalize(obj)
            deallocate(obj)
```

### Reference Counting + GC

Reference counting and GC work together:

1. **Reference counts** handle deterministic resource cleanup
2. **GC** handles cycle collection (reference counting can't collect cycles)
3. When ref count reaches 0, the object is finalized and deallocated
4. The GC periodically collects objects that have circular references but non-zero ref counts

### Acyclic Deterministic Destruction

```
// Reference counting ensures timely cleanup
shyira file = open("data.txt")
// ... use file ...
// When file goes out of scope, ref count drops to 0
// File handle is closed immediately
```

## Ownership Model

### Current: Shared Ownership

Currently, I uses shared ownership with reference counting + GC. All references are shared references.

### Future: Optional Ownership

The language may add optional ownership annotations:

```
// Owned reference (unique owner)
shyira owner: own Person = gukora Person("Jean")

// Shared reference (reference counted)
shyira friend: ref Person = owner

// Borrowed reference (no ownership transfer)
umurimo greet(person: &Person) -> string
    subira "Hello, " + person.izina
iherezo
```

### Ownership Rules (Future)

1. **Single owner**: Each value has exactly one owner
2. **Move semantics**: Ownership can be transferred
3. **Borrowing**: References can borrow without taking ownership
4. **Lifetime tracking**: Borrows cannot outlive the owner

### Ownership Benefits

- Deterministic destruction without reference counting overhead
- No garbage collector pauses for owned data
- Compile-time memory safety guarantees
- Better cache locality

## Memory Safety

### Safety Guarantees

The I runtime provides:

1. **No null pointer dereferences**: Optional types with null checking
2. **No use-after-free**: GC prevents freeing live objects
3. **No double-free**: Reference counting + GC
4. **No buffer overflow**: Bounds checking on all array access
5. **No data races**: Thread safety through immutable data + locks
6. **No memory leaks**: GC collects unreachable objects

### Bounds Checking

```
// Every array access is bounds-checked
function listGet(list: List<T>, index: int) -> T:
    if index < 0 or index >= list.length:
        throw IndexError("Index {index} out of bounds (0..{list.length-1})")
    return list.elements[index]
```

### Type Safety

```
// Every type cast is checked
function safeCast(obj: Any, target_type: Type) -> target_type:
    if obj.type == target_type:
        return obj
    throw TypeError("Cannot cast {obj.type} to {target_type}")
```

### Stack Overflow Protection

```
// Every function call checks stack depth
function checkCallDepth():
    if call_stack.depth > MAX_CALL_DEPTH:
        throw StackOverflowError("Maximum call depth exceeded")
```

## Resource Cleanup

### Deterministic Cleanup

For resources that need immediate release:

```
// Using try-finally for deterministic cleanup
kora
    shyira file = open("data.txt")
    // ... use file ...
kubika error
    // handle error
ikinyoma
    file.close()  // Always runs
iherezo
```

### Destructors (Future)

```
igiceri Resource
    handle: Handle
    
    // Destructor - called when ref count reaches 0
    ~Resource()
        close(self.handle)
    iherezo
iherezo
```

### RAII Pattern

Resource Acquisition Is Initialization:

```
// Resource is acquired in constructor
// Resource is released in destructor
// Cleanup is automatic and deterministic
igiceri DatabaseConnection
    connection: Connection
    
    __init__(url: string)
        self.connection = connect(url)
    iherezo
    
    __del__()
        self.connection.close()
    iherezo
    
    umurimo query(sql: string) -> Result
        subira self.connection.execute(sql)
    iherezo
iherezo
```

## Future Optimizations

### Escape Analysis

Determine which objects never escape their creating scope:

```
function process():
    shyira temp = gukora Point(1, 2)  // Never escapes
    // temp can be stack-allocated
    subira temp.x + temp.y
```

### Stack Allocation

For objects that don't escape, allocate on the stack:

```
// Before optimization (heap allocation)
shyira p = gukora Point(1, 2)

// After escape analysis + stack allocation
shyira p = Point(1, 2)  // Stack allocated
```

### Lazy Allocation

Defer allocation until actually needed:

```
// Lazy list - elements computed on demand
shyira lazy_list = LazyList(range(0, 1000000))
// Only allocates as elements are accessed
```

### Memory Pooling

Reuse allocated memory for frequently created objects:

```
// Object pool for small, frequently allocated objects
shyira pool = ObjectPool(Point, initial_size=100)
shyira p = pool.acquire()  // Reuse allocated memory
pool.release(p)
```

### Compaction

Reduce heap fragmentation by compacting live objects:

```
// During GC, move live objects together
// Update all references to new locations
// Result: reduced fragmentation, better cache locality
```

### Generational GC Tuning

Adjust GC parameters based on program behavior:

```
// Adaptive sizing
if nursery_collections_per_second > THRESHOLD:
    increaseNurserySize()
    
if old_space_fragmentation > THRESHOLD:
    triggerCompaction()
```

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
