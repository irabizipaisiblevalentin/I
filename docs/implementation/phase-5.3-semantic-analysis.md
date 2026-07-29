# Phase 5.3: Semantic Analysis Engineering Plan

**Status:** Draft
**Version:** 1.0
**Date:** July 2026
**Author:** I Engineering Team

---

## 1. Objectives

### 1.1 Primary Objectives

Implement semantic analysis that validates program meaning beyond syntax:

1. **Scopes**: Lexical scope management
2. **Modules**: Module system implementation
3. **Imports**: Import resolution
4. **Namespaces**: Namespace support
5. **Symbol Tables**: Symbol storage and lookup
6. **Name Resolution**: Resolving identifiers to definitions
7. **Constant Evaluation**: Compile-time constant evaluation
8. **Visibility Rules**: Access control enforcement
9. **Generics Preparation**: Foundation for generic types

### 1.2 Quality Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| Test Coverage | > 90% | Line coverage |
| Documentation | 100% public API | Doc comments |
| Error Detection | > 95% | Semantic errors found |
| Performance | < 100ms | Average analysis time |

### 1.3 Non-Objectives

- Type checking (Phase 5.4)
- Code generation (Phase 5.6)
- Optimization (Phase 5.5)

---

## 2. Engineering Design

### 2.1 Architecture Overview

```
Validated AST
    ↓
Scope Analysis
    ↓
Name Resolution
    ↓
Constant Evaluation
    ↓
Visibility Checking
    ↓
Analyzed AST
```

### 2.2 Scope Design

#### 2.2.1 Scope Types

```rust
// Scope types
pub enum ScopeKind {
    Global,
    Module,
    Function,
    Block,
    Loop,
    Closure,
}

// Scope
pub struct Scope {
    pub kind: ScopeKind,
    pub parent: Option<ScopeId>,
    pub symbols: HashMap<Symbol, SymbolId>,
    pub children: Vec<ScopeId>,
    pub span: Span,
}

// Scope ID
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct ScopeId(u32);
```

#### 2.2.2 Scope Chain

```
Global Scope
├── Module Scope
│   ├── Function Scope
│   │   ├── Block Scope
│   │   │   └── Block Scope
│   │   └── Block Scope
│   └── Function Scope
│       └── Block Scope
└── Module Scope
    └── ...
```

### 2.3 Symbol Table Design

#### 2.3.1 Symbol Types

```rust
// Symbol kinds
pub enum SymbolKind {
    Variable(VariableSymbol),
    Function(FunctionSymbol),
    Struct(StructSymbol),
    Class(ClassSymbol),
    Enum(EnumSymbol),
    Trait(TraitSymbol),
    Const(ConstSymbol),
    Module(ModuleSymbol),
    Type(TypeSymbol),
    Label(LabelSymbol),
}

// Symbol
pub struct Symbol {
    pub id: SymbolId,
    pub name: Symbol,
    pub kind: SymbolKind,
    pub scope: ScopeId,
    pub span: Span,
    pub visibility: Visibility,
}

// Symbol ID
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct SymbolId(u32);
```

#### 2.3.2 Symbol Resolution

```rust
// Symbol table
pub struct SymbolTable {
    symbols: Vec<Symbol>,
    scopes: Vec<Scope>,
    current_scope: ScopeId,
}

impl SymbolTable {
    pub fn enter_scope(&mut self, kind: ScopeKind, span: Span) -> ScopeId { ... }
    pub fn exit_scope(&mut self) -> ScopeId { ... }
    pub fn define(&mut self, name: Symbol, kind: SymbolKind) -> Result<SymbolId, Error> { ... }
    pub fn resolve(&self, name: Symbol) -> Option<SymbolId> { ... }
    pub fn resolve_current(&self, name: Symbol) -> Option<SymbolId> { ... }
}
```

### 2.4 Module System Design

#### 2.4.1 Module Representation

```rust
// Module
pub struct Module {
    pub id: ModuleId,
    pub name: Symbol,
    pub path: PathBuf,
    pub declarations: Vec<DeclarationId>,
    pub imports: Vec<ImportId>,
    pub exports: Vec<SymbolId>,
    pub scope: ScopeId,
    pub span: Span,
}

// Module ID
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct ModuleId(u32);

// Import
pub struct Import {
    pub id: ImportId,
    pub path: ImportPath,
    pub alias: Option<Symbol>,
    pub visibility: Visibility,
    pub span: Span,
}

// Import path
pub enum ImportPath {
    Simple(Symbol),
    Nested(Vec<Symbol>),
    Glob,
}
```

#### 2.4.2 Module Resolution

```
Source File → Module ID → Module → Declarations
     ↓
Import Path → Resolution → Module ID
     ↓
Symbol Lookup → Symbol ID → Definition
```

### 2.5 Name Resolution Design

#### 2.5.1 Resolution Algorithm

1. Start in current scope
2. Look up name in current scope
3. If not found, move to parent scope
4. Repeat until found or reach global scope
5. If not found, report error

#### 2.5.2 Resolution Rules

- Local names shadow outer names
- Module names are accessible via path
- Imported names are accessible in current scope
- Visibility rules are enforced

### 2.6 Constant Evaluation Design

#### 2.6.1 Constant Types

```rust
// Constant value
pub enum ConstValue {
    Integer(i64),
    Float(f64),
    Bool(bool),
    String(String),
    Char(char),
    Array(Vec<ConstValue>),
    Struct(Vec<(Symbol, ConstValue)>),
    Enum(Symbol, Option<Box<ConstValue>>),
    Null,
}

// Constant expression
pub struct ConstExpr {
    pub value: ConstValue,
    pub span: Span,
}
```

#### 2.6.2 Evaluation Rules

- Only compile-time evaluable expressions allowed
- No side effects allowed
- No function calls allowed (except builtins)
- No mutations allowed
- Type checking not required (deferred)

### 2.7 Visibility Rules Design

#### 2.7.1 Visibility Levels

```rust
// Visibility
pub enum Visibility {
    Private,      // Only within current scope
    Public,       // Accessible from anywhere
    Restricted(Vec<Symbol>),  // Accessible from specified modules
}
```

#### 2.7.2 Visibility Rules

- Default visibility is private
- Public items are accessible from outside module
- Restricted items are accessible from specified modules
- Nested items inherit parent visibility
- Imports can change visibility

---

## 3. File Structure

### 3.1 Crate Structure

```
crates/
└── ilang-analyzer/
    ├── Cargo.toml
    ├── src/
    │   ├── lib.rs
    │   ├── scope.rs
    │   ├── symbol.rs
    │   ├── module.rs
    │   ├── import.rs
    │   ├── resolver.rs
    │   ├── constant.rs
    │   ├── visibility.rs
    │   ├── analyzer.rs
    │   └── error.rs
    └── tests/
        ├── scope_tests.rs
        ├── symbol_tests.rs
        ├── module_tests.rs
        ├── import_tests.rs
        ├── resolver_tests.rs
        ├── constant_tests.rs
        └── visibility_tests.rs
```

### 3.2 Key Files

```toml
# crates/ilang-analyzer/Cargo.toml
[package]
name = "ilang-analyzer"
version.workspace = true
edition.workspace = true

[dependencies]
ilang-core = { workspace = true }
ilang-ast = { workspace = true }
ilang-diagnostics = { workspace = true }
ilang-error = { workspace = true }
ilang-utils = { workspace = true }
```

---

## 4. Implementation Plan

### 4.1 Implementation Order

| Step | Component | Dependencies | Estimate |
|------|-----------|--------------|----------|
| 1 | Scope implementation | ilang-core | 3 days |
| 2 | Symbol table | scope | 3 days |
| 3 | Module system | symbol | 3 days |
| 4 | Import resolution | module | 3 days |
| 5 | Name resolver | symbol, scope | 4 days |
| 6 | Constant evaluator | ast | 3 days |
| 7 | Visibility checker | symbol | 2 days |
| 8 | Main analyzer | all above | 4 days |
| 9 | Error reporting | diagnostics | 2 days |
| 10 | Unit tests | all above | 4 days |
| 11 | Integration tests | all above | 3 days |
| 12 | Documentation | all above | 3 days |

**Total Estimated Duration:** 37 days (7 weeks)

### 4.2 Detailed Implementation Steps

#### Step 1: Scope Implementation (3 days)

```rust
// crates/ilang-analyzer/src/scope.rs

pub struct ScopeManager {
    scopes: Vec<Scope>,
    current: ScopeId,
}

impl ScopeManager {
    pub fn new() -> Self { ... }
    
    pub fn enter_scope(&mut self, kind: ScopeKind, span: Span) -> ScopeId {
        let scope = Scope {
            kind,
            parent: Some(self.current),
            symbols: HashMap::new(),
            children: Vec::new(),
            span,
        };
        let id = ScopeId(self.scopes.len() as u32);
        self.scopes.push(scope);
        self.current = id;
        id
    }
    
    pub fn exit_scope(&mut self) -> ScopeId {
        let parent = self.scopes[self.current.0 as usize].parent.unwrap();
        self.current = parent;
        parent
    }
    
    pub fn define(&mut self, name: Symbol, symbol_id: SymbolId) -> Result<(), Error> {
        let scope = &mut self.scopes[self.current.0 as usize];
        if scope.symbols.contains_key(&name) {
            return Err(Error::Redefinition(name));
        }
        scope.symbols.insert(name, symbol_id);
        Ok(())
    }
    
    pub fn resolve(&self, name: Symbol) -> Option<SymbolId> {
        let mut current = Some(self.current);
        while let Some(scope_id) = current {
            let scope = &self.scopes[scope_id.0 as usize];
            if let Some(&symbol_id) = scope.symbols.get(&name) {
                return Some(symbol_id);
            }
            current = scope.parent;
        }
        None
    }
}
```

#### Step 2: Symbol Table (3 days)

```rust
// crates/ilang-analyzer/src/symbol.rs

pub struct SymbolTable {
    symbols: Vec<Symbol>,
    scopes: ScopeManager,
}

impl SymbolTable {
    pub fn new() -> Self { ... }
    
    pub fn define_variable(&mut self, name: Symbol, ty: TypeId, span: Span) -> Result<SymbolId, Error> {
        let symbol = Symbol {
            id: SymbolId(self.symbols.len() as u32),
            name,
            kind: SymbolKind::Variable(VariableSymbol { ty }),
            scope: self.scopes.current_scope(),
            span,
            visibility: Visibility::Private,
        };
        let id = symbol.id;
        self.symbols.push(symbol);
        self.scopes.define(name, id)?;
        Ok(id)
    }
    
    pub fn define_function(&mut self, name: Symbol, params: Vec<Param>, return_ty: TypeId, span: Span) -> Result<SymbolId, Error> {
        // Similar to define_variable
    }
    
    pub fn resolve(&self, name: Symbol) -> Option<SymbolId> {
        self.scopes.resolve(name)
    }
    
    pub fn get_symbol(&self, id: SymbolId) -> &Symbol {
        &self.symbols[id.0 as usize]
    }
}
```

#### Step 3-4: Module System (6 days)

```rust
// crates/ilang-analyzer/src/module.rs

pub struct ModuleManager {
    modules: Vec<Module>,
    current: Option<ModuleId>,
    root: ModuleId,
}

impl ModuleManager {
    pub fn new() -> Self { ... }
    
    pub fn create_module(&mut self, name: Symbol, path: PathBuf) -> ModuleId { ... }
    pub fn enter_module(&mut self, id: ModuleId) { ... }
    pub fn exit_module(&mut self) { ... }
    pub fn add_declaration(&mut self, id: DeclarationId) { ... }
    pub fn add_import(&mut self, id: ImportId) { ... }
    pub fn export_symbol(&mut self, symbol_id: SymbolId) { ... }
}
```

#### Step 5: Name Resolver (4 days)

```rust
// crates/ilang-analyzer/src/resolver.rs

pub struct NameResolver<'a> {
    symbols: &'a mut SymbolTable,
    modules: &'a mut ModuleManager,
    diagnostics: &'a mut DiagnosticHandler,
}

impl<'a> NameResolver<'a> {
    pub fn resolve_program(&mut self, program: &Program) -> Result<(), Error> { ... }
    fn resolve_declaration(&mut self, decl: &Declaration) -> Result<(), Error> { ... }
    fn resolve_statement(&mut self, stmt: &Statement) -> Result<(), Error> { ... }
    fn resolve_expression(&mut self, expr: &Expression) -> Result<SymbolId, Error> { ... }
    fn resolve_identifier(&mut self, ident: &Identifier) -> Result<SymbolId, Error> { ... }
}
```

---

## 5. Task Breakdown

### 5.1 Task List

| ID | Task | Priority | Estimate | Dependencies |
|----|------|----------|----------|--------------|
| 5.3.1 | Implement scope management | Critical | 3 days | - |
| 5.3.2 | Implement symbol table | Critical | 3 days | 5.3.1 |
| 5.3.3 | Implement module system | Critical | 3 days | 5.3.2 |
| 5.3.4 | Implement import resolution | Critical | 3 days | 5.3.3 |
| 5.3.5 | Implement name resolver | Critical | 4 days | 5.3.2, 5.3.1 |
| 5.3.6 | Implement constant evaluator | High | 3 days | 5.3.2 |
| 5.3.7 | Implement visibility checker | High | 2 days | 5.3.2 |
| 5.3.8 | Implement main analyzer | Critical | 4 days | All above |
| 5.3.9 | Implement error reporting | High | 2 days | 5.3.8 |
| 5.3.10 | Write unit tests | Critical | 4 days | All above |
| 5.3.11 | Write integration tests | Critical | 3 days | All above |
| 5.3.12 | Write documentation | High | 3 days | All above |

**Total Estimated Duration:** 37 days (7 weeks)

### 5.2 Milestone Schedule

| Milestone | Date | Tasks |
|-----------|------|-------|
| M5.3.1 | Week 1-2 | 5.3.1, 5.3.2 |
| M5.3.2 | Week 3-4 | 5.3.3, 5.3.4 |
| M5.3.3 | Week 5-6 | 5.3.5, 5.3.6, 5.3.7 |
| M5.3.4 | Week 7 | 5.3.8, 5.3.9, 5.3.10, 5.3.11, 5.3.12 |

---

## 6. Testing Strategy

### 6.1 Test Types

| Type | Coverage Target | Description |
|------|-----------------|-------------|
| Unit Tests | 90% | Individual function tests |
| Integration Tests | 85% | Module interaction tests |
| Error Tests | 90% | Error detection tests |
| Edge Case Tests | 80% | Boundary condition tests |

### 6.2 Test Examples

```rust
// Scope test
#[test]
fn test_scope_lookup() {
    let mut symbols = SymbolTable::new();
    symbols.enter_scope(ScopeKind::Block, Span::dummy());
    let id = symbols.define_variable(Symbol::new("x"), TypeId(0), Span::dummy()).unwrap();
    assert_eq!(symbols.resolve(Symbol::new("x")), Some(id));
    symbols.exit_scope();
    assert_eq!(symbols.resolve(Symbol::new("x")), None);
}

// Shadowing test
#[test]
fn test_shadowing() {
    let mut symbols = SymbolTable::new();
    let id1 = symbols.define_variable(Symbol::new("x"), TypeId(0), Span::dummy()).unwrap();
    symbols.enter_scope(ScopeKind::Block, Span::dummy());
    let id2 = symbols.define_variable(Symbol::new("x"), TypeId(0), Span::dummy()).unwrap();
    assert_eq!(symbols.resolve(Symbol::new("x")), Some(id2));
    symbols.exit_scope();
    assert_eq!(symbols.resolve(Symbol::new("x")), Some(id1));
}

// Redefinition error test
#[test]
fn test_redefinition_error() {
    let mut symbols = SymbolTable::new();
    let _ = symbols.define_variable(Symbol::new("x"), TypeId(0), Span::dummy()).unwrap();
    let result = symbols.define_variable(Symbol::new("x"), TypeId(0), Span::dummy());
    assert!(result.is_err());
}
```

---

## 7. Security Considerations

### 7.1 Security Requirements

| Requirement | Description | Verification |
|-------------|-------------|--------------|
| Input Validation | All AST nodes validated | Unit tests |
| Memory Safety | No unsafe code | Clippy audit |
| Error Messages | No code injection | Static analysis |
| DoS Prevention | No exponential blowup | Timeouts |

---

## 8. Performance Considerations

### 8.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Analysis Speed | > 100K LOC/s | Throughput |
| Memory Usage | < 200 MB | Peak memory |
| Symbol Lookup | < 100ns | Average time |

### 8.2 Optimization Strategies

1. **Hash Maps**: Use efficient hash maps for symbol lookup
2. **Arena Allocation**: Use arena allocators for symbols
3. **Incremental Analysis**: Analyze only changed regions
4. **Parallel Analysis**: Analyze independent modules in parallel

---

## 9. Documentation Requirements

### 9.1 Documentation Types

| Type | Location | Audience |
|------|----------|----------|
| API Documentation | Source code | Developers |
| Architecture Guide | docs/analyzer.md | Contributors |
| Name Resolution | docs/resolution.md | Contributors |
| Module System | docs/modules.md | Contributors |

---

## 10. Definition of Done

### 10.1 Phase 5.3 is complete when:

- [ ] All components implemented and compiling
- [ ] Unit tests passing (> 90% coverage)
- [ ] Integration tests passing
- [ ] Error detection working
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
