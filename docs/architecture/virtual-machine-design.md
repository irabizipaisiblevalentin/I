# Virtual Machine Design

This document specifies the I virtual machine architecture, instruction set, and execution model.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Instruction Format](#instruction-format)
- [Stack Machine Design](#stack-machine-design)
- [Opcode Reference](#opcode-reference)
- [Function Calls](#function-calls)
- [Modules](#modules)
- [Exception Handling](#exception-handling)
- [Debug Information](#debug-information)
- [Bytecode Format](#bytecode-format)
- [Execution Model](#execution-model)

## Overview

The I virtual machine (IVM) executes compiled bytecode. It is a stack-based VM designed for:

1. **Portability**: Runs on any platform with a Python/C runtime
2. **Performance**: Threaded dispatch, inline caching, future JIT
3. **Safety**: Bounds checking, type checking, stack overflow detection
4. **Debuggability**: Step-through debugging, breakpoints, variable inspection

## Architecture

```
VM Architecture:
  Execution Engine  - Instruction pointer, dispatch loop, decoding
  Operand Stack     - Per-thread, LIFO, configurable max size
  Call Stack        - Call frames, return addresses, local variables
  Memory Manager    - Heap (GC), Stack (per-thread), Constant pool
  Runtime Services  - Module loader, I/O, native bridge, debug interface
```

### VM Components

```
VirtualMachine {
    threads: List[Thread]
    current_thread: Thread
    heap: Heap
    constant_pool: ConstantPool
    module_loader: ModuleLoader
    stdlib: StandardLibrary
    native_registry: NativeRegistry
    debug_info: DebugInfo
    breakpoints: List[Breakpoint]
    config: VMConfig
}
```

### Thread Structure

```
Thread {
    id: int
    name: string
    instruction_pointer: int
    call_stack: CallStack
    operand_stack: OperandStack
    current_frame: Frame
    state: ThreadState  // RUNNING, WAITING, BLOCKED, TERMINATED
    stack_roots: List<ObjectRef>
}
```

## Instruction Format

Each instruction is variable-length: 1-byte opcode followed by 0-8 bytes of operands.

### Opcode Encoding

- 0x00-0x7F: Single-byte opcodes (128 available)
- 0x80-0xFF: Extended opcodes (via prefix byte 0xFF)

### Opcode Categories

| Range | Category | Description |
|-------|----------|-------------|
| 0x00-0x0F | Stack | Push/pop/dup/swap |
| 0x10-0x1F | Local | Load/store local variables |
| 0x20-0x2F | Constant | Load constants from pool |
| 0x30-0x3F | Arithmetic | Integer and float operations |
| 0x40-0x4F | Comparison | Comparison operations |
| 0x50-0x5F | Logical | Boolean operations |
| 0x60-0x6F | Control | Jumps, calls, returns |
| 0x70-0x7F | Object | Object field access, method calls |
| 0x80-0x8F | Collection | List/dict/set operations |
| 0x90-0x9F | String | String operations |
| 0xA0-0xAF | Type | Type checking and casting |
| 0xB0-0xBF | Module | Import/export operations |
| 0xC0-0xCF | Exception | Try/catch/throw |
| 0xD0-0xDF | Debug | Breakpoints, single-step |

## Stack Machine Design

All operations work on an operand stack. Operations pop their inputs and push their results.

```
// a + b
PUSH 10        // Stack: [10]
PUSH 20        // Stack: [10, 20]
ADD_INT        // Stack: [30]
STORE_LOCAL 0  // Stack: []  (local_0 = 30)
```

### Advantages

1. Simple code generation (no register allocation)
2. Compact bytecode (operands are implicit)
3. Portable (no dependency on CPU register count)
4. Easy to debug (stack state is explicit)

### Future: Register Machine

For performance, a register machine mode may be added:

```
LOAD r0, 10
LOAD r1, 20
ADD r2, r0, r1
STORE 0, r2
```

## Opcode Reference

### Stack Operations (0x00-0x0F)

| Opcode | Name | Operands | Description |
|--------|------|----------|-------------|
| 0x00 | NOP | none | No operation |
| 0x01 | PUSH | value | Push constant onto stack |
| 0x02 | POP | none | Pop top of stack |
| 0x03 | DUP | none | Duplicate top of stack |
| 0x04 | SWAP | none | Swap top two values |
| 0x05 | PUSH_NULL | none | Push null |

### Local Variable Operations (0x10-0x1F)

| Opcode | Name | Operands | Description |
|--------|------|----------|-------------|
| 0x10 | LOAD_LOCAL | index (1B) | Push local variable |
| 0x11 | STORE_LOCAL | index (1B) | Store to local variable |
| 0x12 | LOAD_ARG | index (1B) | Push function argument |
| 0x13 | STORE_ARG | index (1B) | Store to function argument |

### Constant Operations (0x20-0x2F)

| Opcode | Name | Operands | Description |
|--------|------|----------|-------------|
| 0x20 | LOAD_CONST | index (2B) | Push constant from pool |
| 0x21 | LOAD_INT_0 | none | Push integer 0 |
| 0x22 | LOAD_INT_1 | none | Push integer 1 |
| 0x23 | LOAD_INT_2 | none | Push integer 2 |
| 0x24 | LOAD_TRUE | none | Push boolean true |
| 0x25 | LOAD_FALSE | none | Push boolean false |

### Arithmetic Operations (0x30-0x3F)

| Opcode | Name | Operands | Description |
|--------|------|----------|-------------|
| 0x30 | ADD_INT | none | a + b (integers) |
| 0x31 | SUB_INT | none | a - b (integers) |
| 0x32 | MUL_INT | none | a * b (integers) |
| 0x33 | DIV_INT | none | a / b (integers) |
| 0x34 | MOD_INT | none | a % b (integers) |
| 0x35 | POW_INT | none | a ** b (integers) |
| 0x36 | NEG_INT | none | -a (integer) |
| 0x37 | ADD_FLOAT | none | a + b (floats) |
| 0x38 | SUB_FLOAT | none | a - b (floats) |
| 0x39 | MUL_FLOAT | none | a * b (floats) |
| 0x3A | DIV_FLOAT | none | a / b (floats) |
| 0x3B | MOD_FLOAT | none | a % b (floats) |
| 0x3C | POW_FLOAT | none | a ** b (floats) |
| 0x3D | NEG_FLOAT | none | -a (float) |
| 0x3E | INT_TO_FLOAT | none | Convert int to float |
| 0x3F | FLOAT_TO_INT | none | Convert float to int |

### Comparison Operations (0x40-0x4F)

| Opcode | Name | Operands | Description |
|--------|------|----------|-------------|
| 0x40 | EQ | none | a == b |
| 0x41 | NE | none | a != b |
| 0x42 | LT | none | a < b |
| 0x43 | LE | none | a <= b |
| 0x44 | GT | none | a > b |
| 0x45 | GE | none | a >= b |
| 0x46 | EQ_INT | none | int a == int b |
| 0x47 | NE_INT | none | int a != int b |
| 0x48 | LT_INT | none | int a < int b |
| 0x49 | LE_INT | none | int a <= int b |
| 0x4A | GT_INT | none | int a > int b |
| 0x4B | GE_INT | none | int a >= int b |

### Logical Operations (0x50-0x5F)

| Opcode | Name | Operands | Description |
|--------|------|----------|-------------|
| 0x50 | AND | none | a AND b |
| 0x51 | OR | none | a OR b |
| 0x52 | NOT | none | NOT a |
| 0x53 | IS_NULL | none | a IS NULL |

### Control Flow (0x60-0x6F)

| Opcode | Name | Operands | Description |
|--------|------|----------|-------------|
| 0x60 | JUMP | offset (2B) | Unconditional jump |
| 0x61 | JUMP_IF | offset (2B) | Jump if true |
| 0x62 | JUMP_IF_NOT | offset (2B) | Jump if false |
| 0x63 | CALL | index (2B) | Call function |
| 0x64 | CALL_METHOD | index (2B) | Call method |
| 0x65 | RETURN | none | Return from function |
| 0x66 | RETURN_NULL | none | Return null |
| 0x67 | TAIL_CALL | index (2B) | Tail call |

### Object Operations (0x70-0x7F)

| Opcode | Name | Operands | Description |
|--------|------|----------|-------------|
| 0x70 | NEW_OBJECT | index (2B) | Create new object |
| 0x71 | GET_FIELD | index (1B) | Get object field |
| 0x72 | SET_FIELD | index (1B) | Set object field |
| 0x73 | NEW_LIST | count (2B) | Create new list |
| 0x74 | NEW_DICT | count (2B) | Create new dict |
| 0x75 | LIST_GET | none | Get list element |
| 0x76 | LIST_SET | none | Set list element |
| 0x77 | LIST_LEN | none | Get list length |
| 0x78 | DICT_GET | none | Get dict value |
| 0x79 | DICT_SET | none | Set dict value |

### Exception Handling (0xC0-0xCF)

| Opcode | Name | Operands | Description |
|--------|------|----------|-------------|
| 0xC0 | TRY | handler (2B) | Start try block |
| 0xC1 | END_TRY | none | End try block |
| 0xC2 | THROW | none | Throw exception |
| 0xC3 | CATCH | local (1B) | Store caught exception |

## Function Calls

### Call Frame Structure

```
Frame {
    function: FunctionEntry
    return_address: int
    previous_frame: Frame
    locals: List[Value]
    operand_stack: List<Value>
    module: Module
    closure: Optional<Closure>
}
```

### Call Sequence

1. Create new frame with return address and previous frame
2. Copy arguments to locals
3. Push frame onto call stack
4. Set instruction pointer to function start
5. Check call depth limit

### Return Sequence

1. Pop frame from call stack
2. Restore caller frame
3. Restore instruction pointer
4. Push return value onto caller's operand stack

### Tail Call Optimization

When the last operation in a function is a call to another function and the result is returned directly, reuse the current frame instead of creating a new one.

## Modules

### Module Loading

1. Check module cache
2. Load bytecode file (.ibc)
3. Validate magic number and version
4. Initialize module constants
5. Execute module-level initialization code
6. Cache the module

### Module Resolution

1. Check if already loaded (cache)
2. Resolve relative to importing file
3. Check standard library path
4. Check package directories
5. Load and cache

## Exception Handling

### Exception Table

Each function has an exception table mapping instruction ranges to handlers:

```
ExceptionEntry {
    start_ip: int           // Start of try block
    end_ip: int             // End of try block
    handler_ip: int         // Start of catch block
    catch_type: int         // Exception type (-1 = catch all)
    local: int              // Local variable for exception
}
```

### Throw Sequence

1. Search exception table for matching handler
2. If found: unwind stack to matching frame, store exception, jump to handler
3. If not found: continue unwinding to parent frame
4. If no handler anywhere: unhandled exception error

## Debug Information

### Source Map

```
SourceMapEntry {
    bytecode_offset: int
    source_file: string
    line: int
    column: int
}
```

### Debug Protocol

The VM supports a debug protocol for IDE integration:

- CONTINUE: Resume execution
- STEP_IN: Step into function
- STEP_OVER: Step over function call
- STEP_OUT: Step out of function
- SET_BREAKPOINT: Set breakpoint
- REMOVE_BREAKPOINT: Remove breakpoint
- GET_VARIABLES: Get local variables
- GET_STACK_TRACE: Get call stack
- EVALUATE: Evaluate expression

## Bytecode Format

### File Structure

```
BytecodeFile {
    header: {
        magic: uint32 = 0x494C4E47  // "ILNG"
        version: uint16
        flags: uint16
        timestamp: uint64
    }
    constant_pool: Section
    function_table: Section
    class_table: Section
    module_table: Section
    debug_info: Section
    source_map: Section
    exception_table: Section
    checksum: uint32
}
```

### Section Format

```
Section {
    type: uint8
    size: uint32
    data: bytes
}
```

## Execution Model

### Dispatch

The VM uses threaded dispatch for fast instruction execution:

```
dispatch_table = [op_nop, op_push, op_pop, op_add_int, ...]

loop:
    opcode = readByte()
    goto dispatch_table[opcode]

op_add_int:
    b = pop()
    a = pop()
    push(a + b)
    goto loop
```

### Safepoints

The VM checks for GC safepoints at:

- Function call boundaries
- Backward jumps (loop iterations)
- Allocation sites
- Every N instructions (configurable)

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
