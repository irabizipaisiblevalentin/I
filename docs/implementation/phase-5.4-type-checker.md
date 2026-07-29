# Phase 5.4: Type Checker Engineering Plan

**Status:** Draft
**Version:** 1.0
**Date:** July 2026
**Author:** I Engineering Team

---

## 1. Objectives

### 1.1 Primary Objectives

Implement the type checker that validates type correctness:

1. **Type Inference**: Infer types from context
2. **Constraint Solving**: Solve type constraints
3. **Generic Types**: Support for generic type parameters
4. **Trait Checking**: Validate trait implementations
5. **Type Diagnostics**: Clear type error messages
6. **Compile-time Evaluation**: Evaluate compile-time expressions

### 1.2 Quality Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| Test Coverage | > 90% | Line coverage |
| Documentation | 100% public API | Doc comments |
| Error Detection | > 95% | Type errors found |
| Performance | < 200ms | Average check time |

### 1.3 Non-Objectives

- Code generation (Phase 5.6)
- Optimization (Phase 5.5)
- Runtime type checking (VM phase)

---

## 2. Engineering Design

### 2.1 Architecture Overview

```
Analyzed AST
    ↓
Type Collection
    ↓
Constraint Generation
    ↓
Constraint Solving
    ↓
Trait Checking
    ↓
Type-Checked AST
```

### 2.2 Type System Design

#### 2.2.1 Type Representation

```rust
// Type ID
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct TypeId(u32);

// Type kinds
pub enum TypeKind {
    // Primitive types
    Int,
    Float,
    Bool,
    String,
    Char,
    Null,
    Void,
    
    // Composite types
    Array(TypeId),
    Map(TypeId, TypeId),
    Tuple(Vec<TypeId>),
    Struct(StructId),
    Enum(EnumId),
    
    // Function type
    Function {
        params: Vec<TypeId>,
        return_ty: TypeId,
    },
    
    // Reference types
    Reference(TypeId),
    MutableReference(TypeId),
    
    // Generic types
    Generic(GenericId, Vec<TypeId>),
    
    // Type variables (for inference)
    Variable(TypeVarId),
    
    // Type parameters
    Parameter(TypeParamId),
    
    // Error type (for recovery)
    Error,
}

// Type
pub struct Type {
    pub id: TypeId,
    pub kind: TypeKind,
    pub span: Option<Span>,
}
```

#### 2.2.2 Type Variables

```rust
// Type variable ID
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct TypeVarId(u32);

// Type variable
pub struct TypeVar {
    pub id: TypeVarId,
    pub bound: Option<TypeId>,
    pub constraints: Vec<TypeConstraint>,
    pub span: Span,
}

// Type constraint
pub enum TypeConstraint {
    Implements(TraitId),
    SubtypeOf(TypeId),
    Equal(TypeId),
    OneOf(Vec<TypeId>),
}
```

#### 2.2.3 Generic Types

```rust
// Generic ID
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct GenericId(u32);

// Generic type parameter
pub struct GenericParam {
    pub id: GenericId,
    pub name: Symbol,
    pub bounds: Vec<TraitId>,
    pub default: Option<TypeId>,
    pub span: Span,
}

// Generic instantiation
pub struct GenericInstance {
    pub generic_id: GenericId,
    pub type_args: Vec<TypeId>,
    pub span: Span,
}
```

### 2.3 Type Inference Design

#### 2.3.1 Inference Algorithm

I uses bidirectional type inference:

1. **Checking Mode**: Expected type is known
2. **Inference Mode**: Expected type is unknown

```rust
// Type inference context
pub struct InferContext {
    type_vars: Vec<TypeVar>,
    constraints: Vec<TypeConstraint>,
    substitutions: HashMap<TypeVarId, TypeId>,
}

impl InferContext {
    pub fn new_type_var(&mut self, span: Span) -> TypeVarId { ... }
    pub fn add_constraint(&mut self, constraint: TypeConstraint) { ... }
    pub fn solve(&mut self) -> Result<HashMap<TypeVarId, TypeId>, TypeError> { ... }
}
```

#### 2.3.2 Constraint Solving

```rust
// Constraint solver
pub struct ConstraintSolver {
    substitutions: HashMap<TypeVarId, TypeId>,
    constraints: Vec<TypeConstraint>,
}

impl ConstraintSolver {
    pub fn solve(&mut self) -> Result<(), TypeError> {
        // 1. Unify equal types
        // 2. Check trait implementations
        // 3. Check subtype relationships
        // 4. Propagate substitutions
    }
    
    fn unify(&mut self, left: TypeId, right: TypeId) -> Result<(), TypeError> { ... }
    fn apply_substitution(&self, ty: TypeId) -> TypeId { ... }
}
```

### 2.4 Trait Checking Design

#### 2.4.1 Trait Representation

```rust
// Trait ID
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct TraitId(u32);

// Trait definition
pub struct TraitDef {
    pub id: TraitId,
    pub name: Symbol,
    pub type_params: Vec<GenericParam>,
    pub methods: Vec<TraitMethod>,
    pub span: Span,
}

// Trait method
pub struct TraitMethod {
    pub name: Symbol,
    pub params: Vec<TypeId>,
    pub return_ty: TypeId,
    pub span: Span,
}

// Trait implementation
pub struct TraitImpl {
    pub trait_id: TraitId,
    pub type_id: TypeId,
    pub methods: Vec<MethodImpl>,
    pub span: Span,
}
```

#### 2.4.2 Trait Checking Algorithm

1. Collect all trait implementations
2. For each trait bound, verify implementation exists
3. Check method signatures match
4. Report missing implementations

### 2.5 Type Diagnostics Design

#### 2.5.1 Error Types

```rust
pub enum TypeError {
    TypeMismatch {
        expected: TypeId,
        found: TypeId,
        span: Span,
    },
    UndefinedVariable {
        name: Symbol,
        span: Span,
    },
    UndefinedFunction {
        name: Symbol,
        span: Span,
    },
    ArgumentCountMismatch {
        expected: usize,
        found: usize,
        span: Span,
    },
    MissingTraitImplementation {
        trait_id: TraitId,
        type_id: TypeId,
        span: Span,
    },
    InfiniteType {
        type_var: TypeVarId,
        span: Span,
    },
    // ... more error types
}
```

#### 2.5.2 Error Messages

```rust
// Error message format
pub struct TypeErrorMsg {
    pub primary: String,
    pub primary_rw: String,  // Kinyarwanda
    pub notes: Vec<String>,
    pub notes_rw: Vec<String>,
    pub suggestions: Vec<Suggestion>,
}
```

---

## 3. File Structure

### 3.1 Crate Structure

```
crates/
└── ilang-types/
    ├── Cargo.toml
    ├── src/
    │   ├── lib.rs
    │   ├── types.rs
    │   ├── type_var.rs
    │   ├── generic.rs
    │   ├── trait_def.rs
    │   ├── inference.rs
    │   ├── solver.rs
    │   ├── checker.rs
    │   ├── context.rs
    │   └── error.rs
    └── tests/
        ├── type_tests.rs
        ├── inference_tests.rs
        ├── solver_tests.rs
        ├── trait_tests.rs
        └── checker_tests.rs
```

### 3.2 Key Files

```toml
# crates/ilang-types/Cargo.toml
[package]
name = "ilang-types"
version.workspace = true
edition.workspace = true

[dependencies]
ilang-core = { workspace = true }
ilang-ast = { workspace = true }
ilang-analyzer = { workspace = true }
ilang-diagnostics = { workspace = true }
ilang-error = { workspace = true }
```

---

## 4. Implementation Plan

### 4.1 Implementation Order

| Step | Component | Dependencies | Estimate |
|------|-----------|--------------|----------|
| 1 | Type definitions | ilang-core | 3 days |
| 2 | Type variables | types | 2 days |
| 3 | Generic types | types | 3 days |
| 4 | Trait definitions | types | 3 days |
| 5 | Type inference | all above | 5 days |
| 6 | Constraint solver | inference | 4 days |
| 7 | Trait checker | traits, solver | 3 days |
| 8 | Main checker | all above | 4 days |
| 9 | Error reporting | diagnostics | 2 days |
| 10 | Unit tests | all above | 4 days |
| 11 | Integration tests | all above | 3 days |
| 12 | Documentation | all above | 3 days |

**Total Estimated Duration:** 39 days (8 weeks)

### 4.2 Detailed Implementation Steps

#### Step 1: Type Definitions (3 days)

```rust
// crates/ilang-types/src/types.rs

pub struct TypeStore {
    types: Vec<Type>,
    type_vars: Vec<TypeVar>,
    generic_params: Vec<GenericParam>,
    trait_defs: Vec<TraitDef>,
    trait_impls: Vec<TraitImpl>,
}

impl TypeStore {
    pub fn new() -> Self { ... }
    
    pub fn intern_type(&mut self, kind: TypeKind) -> TypeId { ... }
    pub fn get_type(&self, id: TypeId) -> &Type { ... }
    pub fn get_type_kind(&self, id: TypeId) -> &TypeKind { ... }
    
    pub fn int_type(&mut self) -> TypeId { ... }
    pub fn float_type(&mut self) -> TypeId { ... }
    pub fn bool_type(&mut self) -> TypeId { ... }
    pub fn string_type(&mut self) -> TypeId { ... }
    pub fn void_type(&mut self) -> TypeId { ... }
    
    pub fn array_type(&mut self, element: TypeId) -> TypeId { ... }
    pub fn function_type(&mut self, params: Vec<TypeId>, return_ty: TypeId) -> TypeId { ... }
    pub fn reference_type(&mut self, inner: TypeId) -> TypeId { ... }
}
```

#### Step 5: Type Inference (5 days)

```rust
// crates/ilang-types/src/inference.rs

pub struct TypeInferencer<'a> {
    type_store: &'a mut TypeStore,
    symbol_table: &'a SymbolTable,
    context: InferContext,
    diagnostics: &'a mut DiagnosticHandler,
}

impl<'a> TypeInferencer<'a> {
    pub fn infer_program(&mut self, program: &Program) -> Result<(), TypeError> { ... }
    
    fn infer_declaration(&mut self, decl: &Declaration) -> Result<TypeId, TypeError> { ... }
    fn infer_statement(&mut self, stmt: &Statement) -> Result<TypeId, TypeError> { ... }
    fn infer_expression(&mut self, expr: &Expression) -> Result<TypeId, TypeError> { ... }
    
    fn infer_binary(&mut self, left: &Expression, op: BinaryOp, right: &Expression) -> Result<TypeId, TypeError> { ... }
    fn infer_unary(&mut self, op: UnaryOp, operand: &Expression) -> Result<TypeId, TypeError> { ... }
    fn infer_call(&mut self, callee: &Expression, args: &[Expression]) -> Result<TypeId, TypeError> { ... }
}
```

#### Step 6: Constraint Solver (4 days)

```rust
// crates/ilang-types/src/solver.rs

pub struct ConstraintSolver {
    type_store: TypeStore,
    substitutions: HashMap<TypeVarId, TypeId>,
    constraints: Vec<TypeConstraint>,
}

impl ConstraintSolver {
    pub fn new(type_store: TypeStore) -> Self { ... }
    
    pub fn add_constraint(&mut self, constraint: TypeConstraint) { ... }
    
    pub fn solve(&mut self) -> Result<(), TypeError> {
        // 1. Process equality constraints
        // 2. Process trait constraints
        // 3. Process subtype constraints
        // 4. Check for cycles
        // 5. Apply substitutions
    }
    
    fn unify(&mut self, left: TypeId, right: TypeId) -> Result<(), TypeError> { ... }
    fn occurs_check(&self, var: TypeVarId, ty: TypeId) -> bool { ... }
    fn apply_substitution(&self, ty: TypeId) -> TypeId { ... }
}
```

---

## 5. Task Breakdown

### 5.1 Task List

| ID | Task | Priority | Estimate | Dependencies |
|----|------|----------|----------|--------------|
| 5.4.1 | Implement type definitions | Critical | 3 days | - |
| 5.4.2 | Implement type variables | Critical | 2 days | 5.4.1 |
| 5.4.3 | Implement generic types | High | 3 days | 5.4.1 |
| 5.4.4 | Implement trait definitions | High | 3 days | 5.4.1 |
| 5.4.5 | Implement type inference | Critical | 5 days | 5.4.1-5.4.4 |
| 5.4.6 | Implement constraint solver | Critical | 4 days | 5.4.5 |
| 5.4.7 | Implement trait checker | High | 3 days | 5.4.4, 5.4.6 |
| 5.4.8 | Implement main checker | Critical | 4 days | All above |
| 5.4.9 | Implement error reporting | High | 2 days | 5.4.8 |
| 5.4.10 | Write unit tests | Critical | 4 days | All above |
| 5.4.11 | Write integration tests | Critical | 3 days | All above |
| 5.4.12 | Write documentation | High | 3 days | All above |

**Total Estimated Duration:** 39 days (8 weeks)

### 5.2 Milestone Schedule

| Milestone | Date | Tasks |
|-----------|------|-------|
| M5.4.1 | Week 1-2 | 5.4.1, 5.4.2, 5.4.3, 5.4.4 |
| M5.4.2 | Week 3-5 | 5.4.5, 5.4.6 |
| M5.4.3 | Week 6-7 | 5.4.7, 5.4.8, 5.4.9 |
| M5.4.4 | Week 8 | 5.4.10, 5.4.11, 5.4.12 |

---

## 6. Testing Strategy

### 6.1 Test Types

| Type | Coverage Target | Description |
|------|-----------------|-------------|
| Unit Tests | 90% | Individual function tests |
| Integration Tests | 85% | Module interaction tests |
| Type Error Tests | 90% | Error detection tests |
| Inference Tests | 85% | Type inference tests |
| Trait Tests | 85% | Trait checking tests |

### 6.2 Test Examples

```rust
// Type inference test
#[test]
fn test_infer_literal() {
    let mut checker = create_checker();
    let expr = Expression::literal(Literal::integer(42));
    let ty = checker.infer_expression(&expr).unwrap();
    assert_eq!(checker.get_type(ty), &TypeKind::Int);
}

// Type mismatch test
#[test]
fn test_type_mismatch() {
    let mut checker = create_checker();
    let expr = Expression::binary(
        Expression::literal(Literal::integer(42)),
        BinaryOp::Plus,
        Expression::literal(Literal::string("hello")),
    );
    let result = checker.infer_expression(&expr);
    assert!(result.is_err());
}

// Generic test
#[test]
fn test_generic_function() {
    let source = "umurimo identity<T>(x: T) -> T { subira x; }";
    let mut checker = create_checker(source);
    let result = checker.check_program();
    assert!(result.is_ok());
}
```

---

## 7. Security Considerations

### 7.1 Security Requirements

| Requirement | Description | Verification |
|-------------|-------------|--------------|
| Input Validation | All type expressions validated | Unit tests |
| Memory Safety | No unsafe code | Clippy audit |
| Error Messages | No code injection | Static analysis |
| DoS Prevention | No exponential blowup | Timeouts |

---

## 8. Performance Considerations

### 8.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Check Speed | > 50K LOC/s | Throughput |
| Memory Usage | < 500 MB | Peak memory |
| Constraint Solving | < 100ms | Average time |

### 8.2 Optimization Strategies

1. **Type Interning**: Intern types for deduplication
2. **Incremental Checking**: Check only changed regions
3. **Parallel Checking**: Check independent functions in parallel
4. **Caching**: Cache type information

---

## 9. Documentation Requirements

### 9.1 Documentation Types

| Type | Location | Audience |
|------|----------|----------|
| API Documentation | Source code | Developers |
| Type System Guide | docs/types.md | Contributors |
| Inference Guide | docs/inference.md | Contributors |
| Trait Guide | docs/traits.md | Contributors |

---

## 10. Definition of Done

### 10.1 Phase 5.4 is complete when:

- [ ] All components implemented and compiling
- [ ] Unit tests passing (> 90% coverage)
- [ ] Integration tests passing
- [ ] Type inference working
- [ ] Generic types working
- [ ] Trait checking working
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
