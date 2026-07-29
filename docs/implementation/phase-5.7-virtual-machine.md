# Phase 5.7: Virtual Machine Engineering Plan

**Status:** Draft
**Version:** 1.0
**Date:** July 2026
**Author:** I Engineering Team

---

## 1. Objectives

### 1.1 Primary Objectives

Implement the virtual machine for executing I programs:

1. **Stack-Based VM**: Register-free execution model
2. **Bytecode Interpreter**: Efficient execution loop
3. **Memory Management**: Generational GC + reference counting
4. **Call Stack Management**: Function calls and returns
5. **Exception Handling**: Try/catch/finally support
6. **Debug Protocol**: DAP-compatible debugging
7. **Profiling**: Performance data collection

### 1.2 Quality Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| Test Coverage | > 90% | Line coverage |
| Documentation | 100% public API | Doc comments |
| Execution Speed | > 10M ops/s | Throughput |
| Memory Usage | < 2x source size | Memory footprint |

### 1.3 Non-Objectives

- Native code execution (Phase 5.10)
- WebAssembly compilation (Future)
- JIT compilation (Future)

---

## 2. Engineering Design

### 2.1 Architecture Overview

```
Optimized IR
    ↓
Bytecode Generator
    ↓
Bytecode
    ↓
Virtual Machine
    ↓
    ├── Stack Machine
    ├── Memory Manager
    ├── Call Stack
    └── I/O System
    ↓
Program Output
```

### 2.2 Bytecode Format

```rust
// Bytecode structure
pub struct Bytecode {
    pub constants: Vec<Constant>,
    pub functions: Vec<Function>,
    pub entry_point: usize,
    pub debug_info: DebugInfo,
}

pub struct Function {
    pub name: String,
    pub arity: usize,
    pub code: Vec<Instruction>,
    pub locals_count: usize,
}

pub enum Instruction {
    // Constants
    Const(usize),        // Load constant
    
    // Variables
    LocalGet(usize),     // Get local variable
    LocalSet(usize),     // Set local variable
    GlobalGet(String),   // Get global variable
    GlobalSet(String),   // Set global variable
    
    // Arithmetic
    Add,                 // a + b
    Sub,                 // a - b
    Mul,                 // a * b
    Div,                 // a / b
    Mod,                 // a % b
    Neg,                 // -a
    
    // Comparison
    Eq,                  // a == b
    Ne,                  // a != b
    Lt,                  // a < b
    Le,                  // a <= b
    Gt,                  // a > b
    Ge,                  // a >= b
    
    // Logic
    And,                 // a && b
    Or,                  // a || b
    Not,                 // !a
    
    // Stack
    Pop,                 // Pop top
    Dup,                 // Duplicate top
    Swap,                // Swap top two
    
    // Control Flow
    Jump(usize),         // Unconditional jump
    JumpIf(usize),       // Jump if true
    JumpIfNot(usize),    // Jump if false
    Call(usize),         // Call function
    Return,              // Return from function
    TailCall(usize),     // Tail call optimization
    
    // Memory
    Allocate(usize),     // Allocate memory
    Load,                // Load from memory
    Store,               // Store to memory
    
    // I/O
    Print,               // Print to stdout
    Read,                // Read from stdin
    
    // Debug
    DebugLine(usize),    // Debug line info
    Breakpoint,          // Breakpoint
}
```

### 2.3 Stack Machine Design

```rust
// Virtual machine
pub struct VirtualMachine {
    stack: Vec<Value>,
    call_stack: Vec<CallFrame>,
    globals: HashMap<String, Value>,
    memory: MemoryManager,
    pc: usize,
    current_frame: usize,
}

// Value representation
pub enum Value {
    Int(i64),
    Float(f64),
    Bool(bool),
    Char(char),
    String(String),
    Null,
    Function(usize),        // Function index
    Object(Object),         // Heap-allocated object
    Array(Vec<Value>),      // Array value
}

impl VirtualMachine {
    pub fn run(&mut self, bytecode: &Bytecode) -> Result<Value, VmError> {
        let mut pc = 0;
        loop {
            let instruction = bytecode.functions[self.current_frame].code[pc];
            match instruction {
                Instruction::Const(idx) => {
                    self.stack.push(bytecode.constants[idx].clone());
                    pc += 1;
                },
                Instruction::Add => {
                    let b = self.stack.pop().unwrap();
                    let a = self.stack.pop().unwrap();
                    self.stack.push(self.add(a, b)?);
                    pc += 1;
                },
                Instruction::Call(arity) => {
                    let func = self.stack.pop().unwrap();
                    self.push_call_frame(pc + 1, self.stack.len() - arity - 1);
                    pc = self.get_function_entry(func)?;
                },
                Instruction::Return => {
                    let result = self.stack.pop().unwrap();
                    let frame = self.pop_call_frame();
                    self.stack.truncate(frame.stack_base);
                    self.stack.push(result);
                    pc = frame.return_pc;
                },
                // ... more instructions
            }
        }
    }
}
```

### 2.4 Memory Manager Design

```rust
// Memory manager with generational GC + RC
pub struct MemoryManager {
    nursery: Vec<Object>,          // Young generation
    tenured: Vec<Object>,          // Old generation
    free_list: Vec<usize>,         // Free memory slots
    gc_threshold: usize,           // GC trigger threshold
    allocation_count: usize,       // Total allocations
    rc_threshold: usize,           // RC to tracing threshold
}

impl MemoryManager {
    pub fn allocate(&mut self, object: Object) -> usize {
        self.allocation_count += 1;
        
        // Try nursery first
        if self.nursery.len() < self.gc_threshold {
            let id = self.nursery.len();
            self.nursery.push(object);
            return id;
        }
        
        // Trigger minor GC
        self.minor_gc();
        
        // If nursery still full, try tenured
        if self.nursery.len() < self.gc_threshold {
            let id = self.nursery.len();
            self.nursery.push(object);
            return id;
        }
        
        // Trigger major GC
        self.major_gc();
        
        // Allocate in tenured
        let id = self.tenured.len();
        self.tenured.push(object);
        id
    }
    
    fn minor_gc(&mut self) {
        // Mark and sweep nursery
        self.mark_nursery();
        self.sweep_nursery();
        
        // Promote surviving objects to tenured
        self.promote_survivors();
    }
    
    fn major_gc(&mut self) {
        // Mark and sweep entire heap
        self.mark_all();
        self.sweep_all();
    }
}
```

### 2.5 Exception Handling

```rust
// Exception handling
pub struct ExceptionHandler {
    pub catch_pc: usize,
    pub finally_pc: usize,
    pub stack_depth: usize,
}

// Exception handling in VM
impl VirtualMachine {
    fn handle_exception(&mut self, exception: Value) -> Result<(), VmError> {
        // Find matching handler
        let handler = self.find_handler(self.pc)?;
        
        if let Some(handler) = handler {
            // Unwind stack to handler's depth
            self.stack.truncate(handler.stack_depth);
            
            // Push exception value
            self.stack.push(exception);
            
            // Jump to handler
            self.pc = handler.catch_pc;
        } else {
            // No handler, propagate exception
            return Err(VmError::UnhandledException(exception));
        }
        
        Ok(())
    }
}
```

---

## 3. File Structure

### 3.1 Crate Structure

```
crates/
└── ilang-vm/
    ├── Cargo.toml
    ├── src/
    │   ├── lib.rs
    │   ├── bytecode.rs
    │   ├── instruction.rs
    │   ├── value.rs
    │   ├── vm.rs
    │   ├── memory.rs
    │   ├── stack.rs
    │   ├── call_frame.rs
    │   ├── exception.rs
    │   ├── io.rs
    │   ├── debug.rs
    │   ├── profiler.rs
    │   └── error.rs
    └── tests/
        ├── instruction_tests.rs
        ├── value_tests.rs
        ├── vm_tests.rs
        ├── memory_tests.rs
        ├── exception_tests.rs
        └── integration_tests.rs
```

### 3.2 Key Files

```toml
# crates/ilang-vm/Cargo.toml
[package]
name = "ilang-vm"
version.workspace = true
edition.workspace = true

[dependencies]
ilang-core = { workspace = true }
ilang-ir = { workspace = true }
ilang-optimizer = { workspace = true }
ilang-diagnostics = { workspace = true }
ilang-error = { workspace = true }
```

---

## 4. Implementation Plan

### 4.1 Implementation Order

| Step | Component | Dependencies | Estimate |
|------|-----------|--------------|----------|
| 1 | Bytecode format | ilang-ir | 2 days |
| 2 | Value representation | - | 2 days |
| 3 | Basic VM loop | bytecode, value | 3 days |
| 4 | Stack machine | VM loop | 2 days |
| 5 | Call frames | stack, VM loop | 2 days |
| 6 | Memory manager | value | 4 days |
| 7 | Exception handling | call frames | 3 days |
| 8 | I/O system | VM loop | 2 days |
| 9 | Debug protocol | VM loop | 3 days |
| 10 | Profiler | VM loop | 3 days |
| 11 | Unit tests | all above | 4 days |
| 12 | Integration tests | all above | 3 days |
| 13 | Documentation | all above | 3 days |

**Total Estimated Duration:** 36 days (7 weeks)

### 4.2 Detailed Implementation Steps

#### Step 1: Bytecode Format (2 days)

```rust
// crates/ilang-vm/src/bytecode.rs

pub struct Bytecode {
    pub constants: Vec<Constant>,
    pub functions: Vec<Function>,
    pub entry_point: usize,
    pub debug_info: DebugInfo,
}

impl Bytecode {
    pub fn from_ir(ir: &IrModule) -> Result<Self, VmError> {
        let mut builder = BytecodeBuilder::new();
        
        // Convert IR to bytecode
        for function in &ir.functions {
            builder.add_function(function)?;
        }
        
        // Find entry point
        let entry_point = builder.find_entry_point()?;
        
        Ok(Self {
            constants: builder.constants,
            functions: builder.functions,
            entry_point,
            debug_info: builder.debug_info,
        })
    }
}
```

#### Step 2: Value Representation (2 days)

```rust
// crates/ilang-vm/src/value.rs

#[derive(Clone, Debug)]
pub enum Value {
    Int(i64),
    Float(f64),
    Bool(bool),
    Char(char),
    String(String),
    Null,
    Function(usize),
    Object(Gc<Object>),
}

impl Value {
    pub fn is_truthy(&self) -> bool {
        match self {
            Value::Int(0) => false,
            Value::Float(0.0) => false,
            Value::Bool(false) => false,
            Value::Char('\0') => false,
            Value::String(s) => !s.is_empty(),
            Value::Null => false,
            _ => true,
        }
    }
    
    pub fn to_string(&self) -> String {
        match self {
            Value::Int(n) => n.to_string(),
            Value::Float(f) => f.to_string(),
            Value::Bool(b) => b.to_string(),
            Value::Char(c) => c.to_string(),
            Value::String(s) => s.clone(),
            Value::Null => "null".to_string(),
            Value::Function(f) => format!("<function {}>", f),
            Value::Object(o) => format!("<object {}>", o.id),
        }
    }
}
```

---

## 5. Task Breakdown

### 5.1 Task List

| ID | Task | Priority | Estimate | Dependencies |
|----|------|----------|----------|--------------|
| 5.7.1 | Implement bytecode format | Critical | 2 days | - |
| 5.7.2 | Implement value representation | Critical | 2 days | - |
| 5.7.3 | Implement basic VM loop | Critical | 3 days | 5.7.1, 5.7.2 |
| 5.7.4 | Implement stack machine | Critical | 2 days | 5.7.3 |
| 5.7.5 | Implement call frames | Critical | 2 days | 5.7.4 |
| 5.7.6 | Implement memory manager | High | 4 days | 5.7.2 |
| 5.7.7 | Implement exception handling | High | 3 days | 5.7.5 |
| 5.7.8 | Implement I/O system | Medium | 2 days | 5.7.3 |
| 5.7.9 | Implement debug protocol | High | 3 days | 5.7.3 |
| 5.7.10 | Implement profiler | Medium | 3 days | 5.7.3 |
| 5.7.11 | Write unit tests | Critical | 4 days | All above |
| 5.7.12 | Write integration tests | Critical | 3 days | All above |
| 5.7.13 | Write documentation | High | 3 days | All above |

**Total Estimated Duration:** 36 days (7 weeks)

### 5.2 Milestone Schedule

| Milestone | Date | Tasks |
|-----------|------|-------|
| M5.7.1 | Week 1 | 5.7.1, 5.7.2 |
| M5.7.2 | Week 2-3 | 5.7.3, 5.7.4, 5.7.5 |
| M5.7.3 | Week 4-5 | 5.7.6, 5.7.7, 5.7.8, 5.7.9, 5.7.10 |
| M5.7.4 | Week 6-7 | 5.7.11, 5.7.12, 5.7.13 |

---

## 6. Testing Strategy

### 6.1 Test Types

| Type | Coverage Target | Description |
|------|-----------------|-------------|
| Unit Tests | 90% | Individual instruction tests |
| Integration Tests | 85% | Full program execution tests |
| Memory Tests | 90% | GC correctness tests |
| Exception Tests | 95% | Exception handling tests |

### 6.2 Test Examples

```rust
// Instruction test
#[test]
fn test_add_instruction() {
    let bytecode = create_bytecode_with_add();
    let mut vm = VirtualMachine::new();
    let result = vm.run(&bytecode).unwrap();
    assert_eq!(result, Value::Int(5));
}

// Memory test
#[test]
fn test_gc_collects_unreachable() {
    let mut vm = VirtualMachine::new();
    // Allocate many objects
    for _ in 0..1000 {
        vm.allocate_object();
    }
    // Drop references
    vm.clear_stack();
    // Trigger GC
    vm.collect_garbage();
    // Verify memory freed
    assert!(vm.memory_usage() < 100);
}

// Exception test
#[test]
fn test_exception_handling() {
    let bytecode = create_bytecode_with_exception();
    let mut vm = VirtualMachine::new();
    let result = vm.run(&bytecode);
    assert!(result.is_ok());
}
```

---

## 7. Security Considerations

### 7.1 Security Requirements

| Requirement | Description | Verification |
|-------------|-------------|--------------|
| Memory Safety | No buffer overflows | Bounds checking |
| Stack Safety | No stack overflows | Depth limits |
| Resource Limits | Prevent DoS | Resource quotas |
| Input Validation | Validate all inputs | Check all sources |

---

## 8. Performance Considerations

### 8.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Execution Speed | > 10M ops/s | Throughput |
| Memory Usage | < 2x source size | Memory footprint |
| Startup Time | < 100ms | Time to first instruction |

### 8.2 Optimization Strategies

1. **Computed Goto**: Use computed goto for dispatch
2. **Inline Caching**: Cache dynamic lookups
3. **Threaded Code**: Threaded interpreter
4. **Register Allocation**: Optimize register usage

---

## 9. Documentation Requirements

### 9.1 Documentation Types

| Type | Location | Audience |
|------|----------|----------|
| API Documentation | Source code | Developers |
| VM Internals | docs/vm-internals.md | Contributors |
| Bytecode Reference | docs/bytecode.md | Contributors |

---

## 10. Definition of Done

### 10.1 Phase 5.7 is complete when:

- [ ] All components implemented and compiling
- [ ] Unit tests passing (> 90% coverage)
- [ ] Integration tests passing
- [ ] Bytecode interpreter working
- [ ] Memory manager working
- [ ] Exception handling working
- [ ] Debug protocol working
- [ ] Documentation complete
- [ ] Examples working
- [ ] Cross-platform testing passing
- [ ] Security review complete
- [ ] Performance review complete
- [ ] Code review complete
- [ ] Changelog updated

### 10.2 Quality Gates

| Gate | Requirement | Status |
|------|-------------|--------|
| Build | Clean build passes | - |
| Tests | All tests pass | - |
| Coverage | > 90% | - |
| Lint | No warnings | - |
| Format | Formatted | - |
| Docs | All public API documented | - |
| Security | No vulnerabilities | - |
| Review | Code reviewed | - |

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
