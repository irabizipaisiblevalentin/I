# Phase 5.8: Standard Library Engineering Plan

**Status:** Draft
**Version:** 1.0
**Date:** July 2026
**Author:** I Engineering Team

---

## 1. Objectives

### 1.1 Primary Objectives

Implement the I standard library with all core modules:

1. **Core Module**: Fundamental types and utilities
2. **Math Module**: Mathematical functions
3. **String Module**: String operations
4. **Array Module**: Array operations
5. **Map Module**: Map/dictionary operations
6. **I/O Module**: File and console I/O
7. **Time Module**: Date and time operations
8. **Error Module**: Error handling utilities
9. **Testing Module**: Test framework
10. **Debug Module**: Debugging utilities

### 1.2 Quality Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| Test Coverage | > 90% | Line coverage |
| Documentation | 100% public API | Doc comments |
| Module Count | 50+ modules | Module count |
| Function Count | 500+ functions | Function count |

### 1.3 Non-Objectives

- Third-party library management (Phase 5.9)
- Package distribution (Phase 5.9)
- Platform-specific implementations (Future)

---

## 2. Engineering Design

### 2.1 Architecture Overview

```
I Standard Library
    ├── Core (ilang-core)
    ├── Math (ilang-math)
    ├── String (ilang-string)
    ├── Array (ilang-array)
    ├── Map (ilang-map)
    ├── I/O (ilang-io)
    ├── Time (ilang-time)
    ├── Error (ilang-error)
    ├── Testing (ilang-testing)
    └── Debug (ilang-debug)
```

### 2.2 Core Module

```rust
// Core module: Fundamental types and utilities
pub mod core {
    // Type conversions
    pub fn to_int(value: Value) -> Result<i64, RuntimeError>;
    pub fn to_float(value: Value) -> Result<f64, RuntimeError>;
    pub fn to_string(value: Value) -> String;
    pub fn to_bool(value: Value) -> bool;
    
    // Type checks
    pub fn is_int(value: &Value) -> bool;
    pub fn is_float(value: &Value) -> bool;
    pub fn is_string(value: &Value) -> bool;
    pub fn is_bool(value: &Value) -> bool;
    pub fn is_null(value: &Value) -> bool;
    pub fn is_array(value: &Value) -> bool;
    pub fn is_map(value: &Value) -> bool;
    pub fn is_function(value: &Value) -> bool;
    
    // Utility functions
    pub fn type_of(value: &Value) -> String;
    pub fn size(value: &Value) -> usize;
    pub fn clone(value: &Value) -> Value;
}
```

### 2.3 Math Module

```rust
// Math module: Mathematical functions
pub mod math {
    // Constants
    pub const PI: f64 = 3.141592653589793;
    pub const E: f64 = 2.718281828459045;
    pub const TAU: f64 = 2.0 * PI;
    
    // Basic operations
    pub fn abs(x: f64) -> f64;
    pub fn ceil(x: f64) -> f64;
    pub fn floor(x: f64) -> f64;
    pub fn round(x: f64) -> f64;
    pub fn min(a: f64, b: f64) -> f64;
    pub fn max(a: f64, b: f64) -> f64;
    
    // Power and roots
    pub fn pow(base: f64, exp: f64) -> f64;
    pub fn sqrt(x: f64) -> f64;
    pub fn cbrt(x: f64) -> f64;
    
    // Trigonometric
    pub fn sin(x: f64) -> f64;
    pub fn cos(x: f64) -> f64;
    pub fn tan(x: f64) -> f64;
    pub fn asin(x: f64) -> f64;
    pub fn acos(x: f64) -> f64;
    pub fn atan(x: f64) -> f64;
    pub fn atan2(y: f64, x: f64) -> f64;
    
    // Logarithmic
    pub fn ln(x: f64) -> f64;
    pub fn log10(x: f64) -> f64;
    pub fn log2(x: f64) -> f64;
    
    // Random
    pub fn random() -> f64;
    pub fn random_range(min: f64, max: f64) -> f64;
    pub fn random_int(min: i64, max: i64) -> i64;
}
```

### 2.4 String Module

```rust
// String module: String operations
pub mod string {
    // Creation
    pub fn new() -> String;
    pub fn from(value: Value) -> String;
    pub fn repeat(s: &str, count: usize) -> String;
    
    // Properties
    pub fn length(s: &str) -> usize;
    pub fn is_empty(s: &str) -> bool;
    pub fn bytes(s: &str) -> Vec<u8>;
    
    // Case conversion
    pub fn to_upper(s: &str) -> String;
    pub fn to_lower(s: &str) -> String;
    pub fn capitalize(s: &str) -> String;
    
    // Search
    pub fn contains(s: &str, pattern: &str) -> bool;
    pub fn starts_with(s: &str, prefix: &str) -> bool;
    pub fn ends_with(s: &str, suffix: &str) -> bool;
    pub fn find(s: &str, pattern: &str) -> Option<usize>;
    pub fn rfind(s: &str, pattern: &str) -> Option<usize>;
    
    // Manipulation
    pub fn trim(s: &str) -> String;
    pub fn trim_start(s: &str) -> String;
    pub fn trim_end(s: &str) -> String;
    pub fn replace(s: &str, from: &str, to: &str) -> String;
    pub fn split(s: &str, delimiter: &str) -> Vec<String>;
    pub fn join(parts: &[String], delimiter: &str) -> String;
    pub fn substring(s: &str, start: usize, end: usize) -> String;
    pub fn reverse(s: &str) -> String;
}
```

### 2.5 Array Module

```rust
// Array module: Array operations
pub mod array {
    // Creation
    pub fn new() -> Vec<Value>;
    pub fn from(values: Vec<Value>) -> Vec<Value>;
    pub fn with_capacity(capacity: usize) -> Vec<Value>;
    pub fn fill(value: Value, count: usize) -> Vec<Value>;
    
    // Properties
    pub fn length(arr: &[Value]) -> usize;
    pub fn is_empty(arr: &[Value]) -> bool;
    pub fn capacity(arr: &[Value]) -> usize;
    
    // Access
    pub fn get(arr: &[Value], index: usize) -> Option<&Value>;
    pub fn set(arr: &mut Vec<Value>, index: usize, value: Value) -> Result<(), RuntimeError>;
    pub fn first(arr: &[Value]) -> Option<&Value>;
    pub fn last(arr: &[Value]) -> Option<&Value>;
    
    // Modification
    pub fn push(arr: &mut Vec<Value>, value: Value);
    pub fn pop(arr: &mut Vec<Value>) -> Option<Value>;
    pub fn insert(arr: &mut Vec<Value>, index: usize, value: Value) -> Result<(), RuntimeError>;
    pub fn remove(arr: &mut Vec<Value>, index: usize) -> Result<Value, RuntimeError>;
    pub fn clear(arr: &mut Vec<Value>);
    
    // Search
    pub fn contains(arr: &[Value], value: &Value) -> bool;
    pub fn find(arr: &[Value], predicate: Value) -> Option<usize>;
    pub fn find_index(arr: &[Value], predicate: Value) -> Option<usize>;
    
    // Transformation
    pub fn map(arr: &[Value], f: Value) -> Vec<Value>;
    pub fn filter(arr: &[Value], predicate: Value) -> Vec<Value>;
    pub fn reduce(arr: &[Value], f: Value, initial: Value) -> Value;
    pub fn sort(arr: &mut Vec<Value>) -> Result<(), RuntimeError>;
    pub fn reverse(arr: &mut Vec<Value>);
    pub fn flatten(arr: &[Value]) -> Vec<Value>;
    pub fn zip(arr1: &[Value], arr2: &[Value]) -> Vec<Value>;
    pub fn unzip(arr: &[Value]) -> (Vec<Value>, Vec<Value>);
}
```

### 2.6 I/O Module

```rust
// I/O module: File and console I/O
pub mod io {
    // Console I/O
    pub fn print(value: &Value);
    pub fn println(value: &Value);
    pub fn eprint(value: &Value);
    pub fn eprintln(value: &Value);
    pub fn input(prompt: &str) -> Result<String, RuntimeError>;
    
    // File I/O
    pub fn read_file(path: &str) -> Result<String, RuntimeError>;
    pub fn write_file(path: &str, content: &str) -> Result<(), RuntimeError>;
    pub fn append_file(path: &str, content: &str) -> Result<(), RuntimeError>;
    pub fn file_exists(path: &str) -> bool;
    pub fn delete_file(path: &str) -> Result<(), RuntimeError>;
    
    // Directory I/O
    pub fn create_dir(path: &str) -> Result<(), RuntimeError>;
    pub fn delete_dir(path: &str) -> Result<(), RuntimeError>;
    pub fn list_dir(path: &str) -> Result<Vec<String>, RuntimeError>;
    
    // Path operations
    pub fn join_path(base: &str, path: &str) -> String;
    pub fn parent(path: &str) -> Option<String>;
    pub fn filename(path: &str) -> Option<String>;
    pub fn extension(path: &str) -> Option<String>;
}
```

---

## 3. File Structure

### 3.1 Crate Structure

```
crates/
├── ilang-stdlib/
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── core.rs
│       ├── math.rs
│       ├── string.rs
│       ├── array.rs
│       ├── map.rs
│       ├── io.rs
│       ├── time.rs
│       ├── error.rs
│       ├── testing.rs
│       └── debug.rs
└── ilang-vm/
    └── src/
        └── builtins.rs (wraps stdlib for VM)
```

### 3.2 Key Files

```toml
# crates/ilang-stdlib/Cargo.toml
[package]
name = "ilang-stdlib"
version.workspace = true
edition.workspace = true

[dependencies]
ilang-core = { workspace = true }
ilang-error = { workspace = true }
```

---

## 4. Implementation Plan

### 4.1 Implementation Order

| Step | Module | Dependencies | Estimate |
|------|--------|--------------|----------|
| 1 | Core module | ilang-core | 3 days |
| 2 | Math module | - | 2 days |
| 3 | String module | - | 3 days |
| 4 | Array module | - | 3 days |
| 5 | Map module | - | 3 days |
| 6 | I/O module | - | 3 days |
| 7 | Time module | - | 2 days |
| 8 | Error module | - | 2 days |
| 9 | Testing module | - | 3 days |
| 10 | Debug module | - | 2 days |
| 11 | VM integration | all above | 3 days |
| 12 | Unit tests | all above | 5 days |
| 13 | Integration tests | all above | 3 days |
| 14 | Documentation | all above | 5 days |

**Total Estimated Duration:** 42 days (8 weeks)

### 4.2 Detailed Implementation Steps

#### Step 1: Core Module (3 days)

```rust
// crates/ilang-stdlib/src/core.rs

pub struct CoreModule;

impl CoreModule {
    pub fn register(registry: &mut ModuleRegistry) {
        registry.register_module("core", Self::new());
    }
    
    pub fn new() -> Self {
        Self
    }
}

impl Module for CoreModule {
    fn name(&self) -> &str {
        "core"
    }
    
    fn functions(&self) -> Vec<(&str, Function)> {
        vec![
            ("to_int", Self::to_int),
            ("to_float", Self::to_float),
            ("to_string", Self::to_string),
            ("to_bool", Self::to_bool),
            ("is_int", Self::is_int),
            ("is_float", Self::is_float),
            ("is_string", Self::is_string),
            ("is_bool", Self::is_bool),
            ("is_null", Self::is_null),
            ("is_array", Self::is_array),
            ("is_map", Self::is_map),
            ("is_function", Self::is_function),
            ("type_of", Self::type_of),
            ("size", Self::size),
            ("clone", Self::clone),
        ]
    }
}
```

#### Step 2: Math Module (2 days)

```rust
// crates/ilang-stdlib/src/math.rs

pub struct MathModule;

impl MathModule {
    pub fn register(registry: &mut ModuleRegistry) {
        registry.register_module("math", Self::new());
    }
    
    pub fn new() -> Self {
        Self
    }
}

impl Module for MathModule {
    fn name(&self) -> &str {
        "math"
    }
    
    fn functions(&self) -> Vec<(&str, Function)> {
        vec![
            ("abs", Self::abs),
            ("ceil", Self::ceil),
            ("floor", Self::floor),
            ("round", Self::round),
            ("min", Self::min),
            ("max", Self::max),
            ("pow", Self::pow),
            ("sqrt", Self::sqrt),
            ("cbrt", Self::cbrt),
            ("sin", Self::sin),
            ("cos", Self::cos),
            ("tan", Self::tan),
            ("asin", Self::asin),
            ("acos", Self::acos),
            ("atan", Self::atan),
            ("atan2", Self::atan2),
            ("ln", Self::ln),
            ("log10", Self::log10),
            ("log2", Self::log2),
            ("random", Self::random),
            ("random_range", Self::random_range),
            ("random_int", Self::random_int),
        ]
    }
    
    fn constants(&self) -> Vec<(&str, Value)> {
        vec![
            ("PI", Value::Float(std::f64::consts::PI)),
            ("E", Value::Float(std::f64::consts::E)),
            ("TAU", Value::Float(2.0 * std::f64::consts::PI)),
        ]
    }
}
```

---

## 5. Task Breakdown

### 5.1 Task List

| ID | Task | Priority | Estimate | Dependencies |
|----|------|----------|----------|--------------|
| 5.8.1 | Implement core module | Critical | 3 days | - |
| 5.8.2 | Implement math module | Critical | 2 days | - |
| 5.8.3 | Implement string module | Critical | 3 days | - |
| 5.8.4 | Implement array module | Critical | 3 days | - |
| 5.8.5 | Implement map module | Critical | 3 days | - |
| 5.8.6 | Implement I/O module | High | 3 days | - |
| 5.8.7 | Implement time module | Medium | 2 days | - |
| 5.8.8 | Implement error module | High | 2 days | - |
| 5.8.9 | Implement testing module | High | 3 days | - |
| 5.8.10 | Implement debug module | Medium | 2 days | - |
| 5.8.11 | Implement VM integration | Critical | 3 days | All above |
| 5.8.12 | Write unit tests | Critical | 5 days | All above |
| 5.8.13 | Write integration tests | Critical | 3 days | All above |
| 5.8.14 | Write documentation | High | 5 days | All above |

**Total Estimated Duration:** 42 days (8 weeks)

### 5.2 Milestone Schedule

| Milestone | Date | Tasks |
|-----------|------|-------|
| M5.8.1 | Week 1-2 | 5.8.1, 5.8.2, 5.8.3 |
| M5.8.2 | Week 3-4 | 5.8.4, 5.8.5, 5.8.6 |
| M5.8.3 | Week 5-6 | 5.8.7, 5.8.8, 5.8.9, 5.8.10 |
| M5.8.4 | Week 7-8 | 5.8.11, 5.8.12, 5.8.13, 5.8.14 |

---

## 6. Testing Strategy

### 6.1 Test Types

| Type | Coverage Target | Description |
|------|-----------------|-------------|
| Unit Tests | 90% | Individual function tests |
| Integration Tests | 85% | Module interaction tests |
| Performance Tests | 80% | Benchmark tests |
| Documentation Tests | 100% | Doc example tests |

### 6.2 Test Examples

```rust
// Math module test
#[test]
fn test_sqrt() {
    assert_eq!(MathModule::sqrt(4.0), 2.0);
    assert_eq!(MathModule::sqrt(9.0), 3.0);
    assert!(MathModule::sqrt(-1.0).is_nan());
}

// Array module test
#[test]
fn test_map() {
    let arr = vec![Value::Int(1), Value::Int(2), Value::Int(3)];
    let f = Value::Function(/* double function */);
    let result = ArrayModule::map(&arr, f);
    assert_eq!(result, vec![Value::Int(2), Value::Int(4), Value::Int(6)]);
}
```

---

## 7. Security Considerations

### 7.1 Security Requirements

| Requirement | Description | Verification |
|-------------|-------------|--------------|
| Input Validation | Validate all inputs | Bounds checking |
| Path Traversal | Prevent path attacks | Sanitize paths |
| Memory Limits | Prevent memory exhaustion | Resource limits |

---

## 8. Documentation Requirements

### 8.1 Documentation Types

| Type | Location | Audience |
|------|----------|----------|
| API Documentation | Source code | Developers |
| Module Reference | docs/modules.md | Users |
| Examples | examples/ | Users |
| Benchmarks | benches/ | Contributors |

---

## 9. Definition of Done

### 9.1 Phase 5.8 is complete when:

- [ ] All modules implemented and compiling
- [ ] Unit tests passing (> 90% coverage)
- [ ] Integration tests passing
- [ ] All 50+ modules available
- [ ] All 500+ functions implemented
- [ ] VM integration working
- [ ] Documentation complete
- [ ] Examples working
- [ ] Benchmarks passing
- [ ] Cross-platform testing passing
- [ ] Code review complete
- [ ] Changelog updated

### 9.2 Quality Gates

| Gate | Requirement | Status |
|------|-------------|--------|
| Build | Clean build passes | - |
| Tests | All tests pass | - |
| Coverage | > 90% | - |
| Lint | No warnings | - |
| Format | Formatted | - |
| Docs | All public API documented | - |
| Benchmarks | No regressions | - |
| Review | Code reviewed | - |

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
