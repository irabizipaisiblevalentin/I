# Phase 5.5: Intermediate Representation Engineering Plan

**Status:** Draft
**Version:** 1.0
**Date:** July 2026
**Author:** I Engineering Team

---

## 1. Objectives

### 1.1 Primary Objectives

Design and implement the intermediate representation for code generation:

1. **IR Specification**: Define IR format and semantics
2. **IR Validator**: Validate IR structure
3. **Optimization-Friendly IR**: Design for easy optimization
4. **Serialization**: IR serialization/deserialization
5. **Visualization Tools**: IR visualization for debugging
6. **IR Debugging**: Debugging support for IR

### 1.2 Quality Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| Test Coverage | > 90% | Line coverage |
| Documentation | 100% public API | Doc comments |
| Validation | 100% | Invalid IR rejected |
| Performance | < 50ms | Generation time |

### 1.3 Non-Objectives

- Optimization (Phase 5.6)
- Code generation (Phase 5.7)
- Runtime execution (VM phase)

---

## 2. Engineering Design

### 2.1 Architecture Overview

```
Type-Checked AST
    ↓
IR Generation
    ↓
Raw IR
    ↓
IR Validation
    ↓
Validated IR
    ↓
IR Optimization (Phase 5.6)
    ↓
Optimized IR
    ↓
Code Generation (Phase 5.7)
```

### 2.2 IR Design

#### 2.2.1 IR Format

I uses a three-address code (TAC) based IR:

```
// Example IR
fn main() -> int {
    %0 = const 42
    %1 = const 10
    %2 = add %0, %1
    ret %2
}
```

#### 2.2.2 IR Types

```rust
// IR Module
pub struct IrModule {
    pub functions: Vec<IrFunction>,
    pub globals: Vec<IrGlobal>,
    pub types: Vec<IrType>,
}

// IR Function
pub struct IrFunction {
    pub name: Symbol,
    pub params: Vec<IrParam>,
    pub return_ty: IrTypeId,
    pub basic_blocks: Vec<BasicBlock>,
    pub locals: Vec<IrLocal>,
}

// Basic Block
pub struct BasicBlock {
    pub label: IrLabel,
    pub instructions: Vec<Instruction>,
    pub terminator: Terminator,
}

// Instruction
pub enum Instruction {
    // Arithmetic
    Add(IrValue, IrValue, IrValue),
    Sub(IrValue, IrValue, IrValue),
    Mul(IrValue, IrValue, IrValue),
    Div(IrValue, IrValue, IrValue),
    Mod(IrValue, IrValue, IrValue),
    
    // Comparison
    Eq(IrValue, IrValue, IrValue),
    Ne(IrValue, IrValue, IrValue),
    Lt(IrValue, IrValue, IrValue),
    Le(IrValue, IrValue, IrValue),
    Gt(IrValue, IrValue, IrValue),
    Ge(IrValue, IrValue, IrValue),
    
    // Logical
    And(IrValue, IrValue, IrValue),
    Or(IrValue, IrValue, IrValue),
    Not(IrValue, IrValue),
    
    // Memory
    Load(IrValue, IrValue),
    Store(IrValue, IrValue),
    Alloca(IrValue, IrTypeId),
    
    // Control
    Call(IrValue, IrValue, Vec<IrValue>),
    
    // Constants
    Const(IrValue, IrConst),
    
    // Cast
    Cast(IrValue, IrValue, IrTypeId),
}

// Terminator
pub enum Terminator {
    Ret(IrValue),
    Br(IrLabel),
    CondBr(IrValue, IrLabel, IrLabel),
    Switch(IrValue, Vec<(IrConst, IrLabel)>, IrLabel),
    Unreachable,
}
```

#### 2.2.3 IR Values

```rust
// IR Value
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum IrValue {
    Local(IrLocalId),
    Param(IrParamId),
    Constant(IrConstId),
    Global(IrGlobalId),
}

// IR Local
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct IrLocalId(u32);

// IR Parameter
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct IrParamId(u32);

// IR Constant
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct IrConstId(u32);

// IR Label
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct IrLabel(u32);

// IR Type ID
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct IrTypeId(u32);
```

#### 2.2.4 IR Types

```rust
// IR Type
pub enum IrType {
    Void,
    Bool,
    Int8,
    Int16,
    Int32,
    Int64,
    Float32,
    Float64,
    Pointer(Box<IrType>),
    Array(Box<IrType>, usize),
    Struct(Vec<IrType>),
    Function {
        params: Vec<IrType>,
        return_ty: Box<IrType>,
    },
}
```

### 2.3 IR Generation Design

#### 2.3.1 Generation Algorithm

1. Create function preamble
2. Allocate local variables
3. Generate basic blocks for statements
4. Generate instructions for expressions
5. Handle control flow
6. Generate function epilogue

#### 2.3.2 Control Flow Graph

```
Entry Block
    ↓
Block 1
    ↓ (condition)
    ├──→ Block 2 (true)
    │       ↓
    │       ↓
    └──→ Block 3 (false)
            ↓
            ↓
Merge Block
    ↓
Exit Block
```

### 2.4 IR Validation Design

#### 2.4.1 Validation Rules

1. All referenced values are defined
2. Types match in instructions
3. Basic blocks have terminators
4. No dead code (unreachable blocks)
5. Valid control flow structure

#### 2.4.2 Validation Algorithm

```rust
pub fn validate_module(module: &IrModule) -> Result<(), IrError> {
    for function in &module.functions {
        validate_function(function)?;
    }
    Ok(())
}

pub fn validate_function(function: &IrFunction) -> Result<(), IrError> {
    // Validate basic blocks
    // Validate instructions
    // Validate terminators
    // Validate types
    Ok(())
}
```

### 2.5 Serialization Design

#### 2.5.1 Serialization Format

```rust
// Binary format
pub struct IrBinary {
    pub magic: [u8; 4],  // "ILNG"
    pub version: u32,
    pub module: IrModule,
}

// Text format (for debugging)
pub struct IrText {
    pub functions: Vec<String>,
    pub globals: Vec<String>,
}
```

#### 2.5.2 Serialization API

```rust
impl IrModule {
    pub fn serialize_binary(&self) -> Vec<u8> { ... }
    pub fn deserialize_binary(data: &[u8]) -> Result<Self, IrError> { ... }
    pub fn to_text(&self) -> String { ... }
    pub fn from_text(text: &str) -> Result<Self, IrError> { ... }
}
```

### 2.6 Visualization Design

#### 2.6.1 Visualization Formats

1. **Text**: Human-readable IR
2. **Graphviz**: Control flow graph
3. **JSON**: Machine-readable IR

#### 2.6.2 Visualization API

```rust
impl IrModule {
    pub fn visualize_text(&self) -> String { ... }
    pub fn visualize_graphviz(&self) -> String { ... }
    pub fn visualize_json(&self) -> String { ... }
}
```

---

## 3. File Structure

### 3.1 Crate Structure

```
crates/
└── ilang-ir/
    ├── Cargo.toml
    ├── src/
    │   ├── lib.rs
    │   ├── types.rs
    │   ├── function.rs
    │   ├── instruction.rs
    │   ├── basic_block.rs
    │   ├── value.rs
    │   ├── generator.rs
    │   ├── validator.rs
    │   ├── serializer.rs
    │   ├── visualizer.rs
    │   └── error.rs
    └── tests/
        ├── types_tests.rs
        ├── function_tests.rs
        ├── instruction_tests.rs
        ├── generator_tests.rs
        ├── validator_tests.rs
        ├── serializer_tests.rs
        └── visualizer_tests.rs
```

### 3.2 Key Files

```toml
# crates/ilang-ir/Cargo.toml
[package]
name = "ilang-ir"
version.workspace = true
edition.workspace = true

[dependencies]
ilang-core = { workspace = true }
ilang-ast = { workspace = true }
ilang-types = { workspace = true }
ilang-diagnostics = { workspace = true }
ilang-error = { workspace = true }
serde = { workspace = true }
```

---

## 4. Implementation Plan

### 4.1 Implementation Order

| Step | Component | Dependencies | Estimate |
|------|-----------|--------------|----------|
| 1 | IR type definitions | ilang-core | 2 days |
| 2 | IR value definitions | types | 2 days |
| 3 | IR instruction definitions | values | 3 days |
| 4 | IR function definitions | instructions | 2 days |
| 5 | IR generator | all above | 5 days |
| 6 | IR validator | all above | 3 days |
| 7 | IR serializer | all above | 3 days |
| 8 | IR visualizer | all above | 3 days |
| 9 | Error reporting | diagnostics | 2 days |
| 10 | Unit tests | all above | 4 days |
| 11 | Integration tests | all above | 3 days |
| 12 | Documentation | all above | 3 days |

**Total Estimated Duration:** 35 days (7 weeks)

### 4.2 Detailed Implementation Steps

#### Step 1-4: IR Definitions (9 days)

```rust
// crates/ilang-ir/src/types.rs

pub struct IrTypeStore {
    types: Vec<IrType>,
}

impl IrTypeStore {
    pub fn new() -> Self { ... }
    pub fn void_type(&mut self) -> IrTypeId { ... }
    pub fn int32_type(&mut self) -> IrTypeId { ... }
    pub fn int64_type(&mut self) -> IrTypeId { ... }
    pub fn float64_type(&mut self) -> IrTypeId { ... }
    pub fn pointer_type(&mut self, inner: IrTypeId) -> IrTypeId { ... }
    pub fn array_type(&mut self, element: IrTypeId, size: usize) -> IrTypeId { ... }
}
```

#### Step 5: IR Generator (5 days)

```rust
// crates/ilang-ir/src/generator.rs

pub struct IrGenerator<'a> {
    type_store: &'a mut IrTypeStore,
    module: IrModule,
    current_function: Option<IrFunctionId>,
    current_block: Option<IrLabel>,
    diagnostics: &'a mut DiagnosticHandler,
}

impl<'a> IrGenerator<'a> {
    pub fn generate_program(&mut self, program: &Program) -> Result<IrModule, IrError> { ... }
    
    fn generate_function(&mut self, decl: &FunctionDecl) -> Result<IrFunction, IrError> { ... }
    fn generate_statement(&mut self, stmt: &Statement) -> Result<(), IrError> { ... }
    fn generate_expression(&mut self, expr: &Expression) -> Result<IrValue, IrError> { ... }
    
    fn emit(&mut self, instruction: Instruction) { ... }
    fn emit_terminator(&mut self, terminator: Terminator) { ... }
    fn create_block(&mut self) -> IrLabel { ... }
    fn switch_to_block(&mut self, label: IrLabel) { ... }
}
```

---

## 5. Task Breakdown

### 5.1 Task List

| ID | Task | Priority | Estimate | Dependencies |
|----|------|----------|----------|--------------|
| 5.5.1 | Implement IR type definitions | Critical | 2 days | - |
| 5.5.2 | Implement IR value definitions | Critical | 2 days | 5.5.1 |
| 5.5.3 | Implement IR instruction definitions | Critical | 3 days | 5.5.2 |
| 5.5.4 | Implement IR function definitions | Critical | 2 days | 5.5.3 |
| 5.5.5 | Implement IR generator | Critical | 5 days | 5.5.1-5.5.4 |
| 5.5.6 | Implement IR validator | Critical | 3 days | 5.5.1-5.5.4 |
| 5.5.7 | Implement IR serializer | High | 3 days | 5.5.1-5.5.4 |
| 5.5.8 | Implement IR visualizer | High | 3 days | 5.5.1-5.5.4 |
| 5.5.9 | Implement error reporting | High | 2 days | 5.5.5 |
| 5.5.10 | Write unit tests | Critical | 4 days | All above |
| 5.5.11 | Write integration tests | Critical | 3 days | All above |
| 5.5.12 | Write documentation | High | 3 days | All above |

**Total Estimated Duration:** 35 days (7 weeks)

### 5.2 Milestone Schedule

| Milestone | Date | Tasks |
|-----------|------|-------|
| M5.5.1 | Week 1-2 | 5.5.1, 5.5.2, 5.5.3, 5.5.4 |
| M5.5.2 | Week 3-4 | 5.5.5, 5.5.6 |
| M5.5.3 | Week 5-6 | 5.5.7, 5.5.8, 5.5.9 |
| M5.5.4 | Week 7 | 5.5.10, 5.5.11, 5.5.12 |

---

## 6. Testing Strategy

### 6.1 Test Types

| Type | Coverage Target | Description |
|------|-----------------|-------------|
| Unit Tests | 90% | Individual function tests |
| Integration Tests | 85% | Module interaction tests |
| Validation Tests | 90% | IR validation tests |
| Serialization Tests | 90% | Round-trip tests |
| Visualization Tests | 80% | Output format tests |

### 6.2 Test Examples

```rust
// IR generation test
#[test]
fn test_generate_function() {
    let source = "umurimo add(a: int, b: int) -> int { subira a + b; }";
    let mut generator = create_generator(source);
    let ir = generator.generate_program().unwrap();
    assert_eq!(ir.functions.len(), 1);
    assert_eq!(ir.functions[0].basic_blocks.len(), 1);
}

// IR validation test
#[test]
fn test_validate_valid_ir() {
    let ir = create_valid_ir();
    assert!(validate_module(&ir).is_ok());
}

// IR validation test (invalid)
#[test]
fn test_validate_invalid_ir() {
    let ir = create_invalid_ir();
    assert!(validate_module(&ir).is_err());
}

// Serialization round-trip test
#[test]
fn test_serialization_roundtrip() {
    let ir = create_valid_ir();
    let serialized = ir.serialize_binary();
    let deserialized = IrModule::deserialize_binary(&serialized).unwrap();
    assert_eq!(ir, deserialized);
}
```

---

## 7. Security Considerations

### 7.1 Security Requirements

| Requirement | Description | Verification |
|-------------|-------------|--------------|
| Input Validation | All IR validated | Unit tests |
| Memory Safety | No unsafe code | Clippy audit |
| Serialization Safety | No deserialization exploits | Fuzz testing |
| DoS Prevention | No exponential blowup | Timeouts |

---

## 8. Performance Considerations

### 8.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Generation Speed | > 100K LOC/s | Throughput |
| Validation Speed | > 1M LOC/s | Throughput |
| Serialization Speed | > 50 MB/s | Throughput |
| Memory Usage | < 500 MB | Peak memory |

### 8.2 Optimization Strategies

1. **Arena Allocation**: Use arena allocators for IR nodes
2. **Incremental Generation**: Generate only changed regions
3. **Parallel Generation**: Generate independent functions in parallel
4. **Caching**: Cache IR for unchanged code

---

## 9. Documentation Requirements

### 9.1 Documentation Types

| Type | Location | Audience |
|------|----------|----------|
| API Documentation | Source code | Developers |
| IR Specification | docs/ir-spec.md | Contributors |
| IR Guide | docs/ir-guide.md | Contributors |
| IR Reference | docs/ir-reference.md | Contributors |

---

## 10. Definition of Done

### 10.1 Phase 5.5 is complete when:

- [ ] All components implemented and compiling
- [ ] Unit tests passing (> 90% coverage)
- [ ] Integration tests passing
- [ ] IR generation working
- [ ] IR validation working
- [ ] Serialization working
- [ ] Visualization working
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
