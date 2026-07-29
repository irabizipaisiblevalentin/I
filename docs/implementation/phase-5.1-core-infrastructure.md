# Phase 5.1: Core Infrastructure Engineering Plan

**Status:** Draft
**Version:** 1.0
**Date:** July 2026
**Author:** I Engineering Team

---

## 1. Objectives

### 1.1 Primary Objectives

Establish the foundational infrastructure for the I Programming Language implementation:

1. **Build System**: Cargo-based workspace with clear module boundaries
2. **Workspace Configuration**: Multi-crate workspace for compiler, stdlib, tools
3. **Logging**: Structured logging framework with Kinyarwanda support
4. **Diagnostics**: Error/warning/info reporting with bilingual messages
5. **Configuration**: Project and compiler configuration management
6. **Error Framework**: Typed error handling with source mapping
7. **Utilities**: Common data structures and helper functions
8. **Test Harness**: Comprehensive testing infrastructure
9. **Benchmark Harness**: Performance measurement infrastructure
10. **Documentation Generation**: Automated documentation from source

### 1.2 Quality Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| Test Coverage | > 90% | Line coverage |
| Documentation | 100% public API | Doc comments |
| Build Time | < 30 seconds | Clean build |
| Binary Size | < 50MB | Release build |
| Startup Time | < 100ms | Cold start |

### 1.3 Non-Objectives

- Language implementation (Phase 5.2+)
- IDE integration (Phase 5.10)
- Package management (Phase 5.9)
- Native code generation (Future phase)

---

## 2. Engineering Design

### 2.1 Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Language | Rust | Memory safety, performance, ecosystem |
| Build System | Cargo | Native Rust build system |
| CI/CD | GitHub Actions | Industry standard |
| Testing | built-in + criterion | Native + benchmarking |
| Documentation | rustdoc | Native documentation |
| Logging | tracing | Structured logging |
| Serialization | serde | Fast serialization |
| Error Handling | anyhow + thiserror | Ergonomic error handling |

### 2.2 Workspace Structure

```
ilang/                           # Root workspace
├── Cargo.toml                   # Workspace configuration
├── rust-toolchain.toml          # Rust toolchain version
├── .cargo/config.toml           # Cargo configuration
├── crates/
│   ├── ilang-core/              # Core types and utilities
│   ├── ilang-lexer/             # Lexer implementation
│   ├── ilang-parser/            # Parser implementation
│   ├── ilang-ast/               # AST definitions
│   ├── ilang-analyzer/          # Semantic analyzer
│   ├── ilang-types/             # Type system
│   ├── ilang-ir/                # Intermediate representation
│   ├── ilang-optimizer/         # Optimizer
│   ├── ilang-codegen/           # Code generation
│   ├── ilang-vm/                # Virtual machine
│   ├── ilang-compiler/          # Main compiler binary
│   ├── ilang-stdlib/            # Standard library
│   ├── ilang-cli/               # CLI tools
│   └── ilang-lsp/               # Language server
├── tests/                       # Integration tests
├── benches/                     # Benchmarks
├── docs/                        # Documentation
└── scripts/                     # Build scripts
```

### 2.3 Module Dependency Graph

```
ilang-core
    ↑
ilang-ast ← ilang-lexer
    ↑
ilang-parser
    ↑
ilang-analyzer ← ilang-types
    ↑
ilang-ir
    ↑
ilang-optimizer
    ↑
ilang-codegen
    ↑
ilang-vm
    ↑
ilang-compiler
```

---

## 3. File Structure

### 3.1 Root Configuration

```toml
# Cargo.toml (workspace root)
[workspace]
resolver = "2"
members = [
    "crates/ilang-core",
    "crates/ilang-lexer",
    "crates/ilang-parser",
    "crates/ilang-ast",
    "crates/ilang-analyzer",
    "crates/ilang-types",
    "crates/ilang-ir",
    "crates/ilang-optimizer",
    "crates/ilang-codegen",
    "crates/ilang-vm",
    "crates/ilang-compiler",
    "crates/ilang-stdlib",
    "crates/ilang-cli",
    "crates/ilang-lsp",
]

[workspace.package]
version = "0.1.0"
edition = "2024"
license = "MIT"
repository = "https://github.com/ilang-dev/ilang"
documentation = "https://docs.ilang.dev"
description = "I Programming Language"

[workspace.dependencies]
# Internal crates
ilang-core = { path = "crates/ilang-core" }
ilang-ast = { path = "crates/ilang-ast" }
ilang-lexer = { path = "crates/ilang-lexer" }
ilang-parser = { path = "crates/ilang-parser" }

# External dependencies
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
thiserror = "2.0"
anyhow = "1.0"
tracing = "0.1"
tracing-subscriber = "0.3"
criterion = { version = "0.5", features = ["html_reports"] }
```

### 3.2 Toolchain Configuration

```toml
# rust-toolchain.toml
[toolchain]
channel = "stable"
components = ["rustfmt", "clippy", "rust-docs"]
targets = ["x86_64-unknown-linux-gnu", "x86_64-pc-windows-msvc", "aarch64-apple-darwin"]
```

### 3.3 Cargo Configuration

```toml
# .cargo/config.toml
[build]
target = "x86_64-unknown-linux-gnu"

[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "target-cpu=native"]

[target.x86_64-pc-windows-msvc]
linker = "lld-link"
rustflags = ["-C", "target-cpu=native"]

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true

[profile.bench]
opt-level = 3
lto = true
```

---

## 4. Implementation Plan

### 4.1 Core Infrastructure Components

#### 4.1.1 ilang-core

**Purpose:** Foundational types, traits, and utilities used by all other crates.

**Modules:**

```rust
// crates/ilang-core/src/lib.rs

pub mod span;      // Source location tracking
pub mod source;    // Source file management
pub mod symbol;    // Symbol/interned string management
pub mod arena;     // Arena allocation
pub mod hash;      // Consistent hashing
pub mod id;        // Generic ID types
pub mod index;     // Index types for collections
pub mod bitset;    // Bit set implementation
pub mod arena_pool; // Arena pool for reuse
```

**Key Types:**

```rust
// Source position
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Span {
    pub start: u32,
    pub end: u32,
    pub file_id: FileId,
}

// Source file identifier
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct FileId(u32);

// Interned string
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Symbol(u32);

// Generic ID type
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Id<T> {
    pub index: u32,
    pub _marker: PhantomData<T>,
}
```

#### 4.1.2 ilang-diagnostics

**Purpose:** Error/warning/info reporting with bilingual support.

**Modules:**

```rust
// crates/ilang-diagnostics/src/lib.rs

pub mod diagnostic;    // Diagnostic types
pub mod emitter;       // Diagnostic emission
pub mod handler;       // Diagnostic handler
pub mod snippet;       // Source snippet rendering
pub mod suggestion;    // Code suggestions
pub mod bilingual;     // Bilingual message support
```

**Key Types:**

```rust
// Severity levels
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Severity {
    Bug,
    Error,
    Warning,
    Note,
    Help,
}

// Diagnostic message
#[derive(Debug, Clone)]
pub struct Diagnostic {
    pub severity: Severity,
    pub code: DiagnosticCode,
    pub message: Message,
    pub spans: Vec<Span>,
    pub children: Vec<Diagnostic>,
    pub suggestions: Vec<Suggestion>,
}

// Bilingual message
#[derive(Debug, Clone)]
pub struct Message {
    pub primary: String,
    pub primary_rw: Option<String>,  // Kinyarwanda translation
    pub secondary: Option<String>,
    pub secondary_rw: Option<String>,
}

// Diagnostic code
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct DiagnosticCode {
    pub category: Category,  // LEX, PARS, SEM, TYP, RUN
    pub number: u32,
}

// Category
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Category {
    Lexer,
    Parser,
    Semantic,
    Type,
    Runtime,
}
```

#### 4.1.3 ilang-logging

**Purpose:** Structured logging with Kinyarwanda support.

**Modules:**

```rust
// crates/ilang-logging/src/lib.rs

pub mod logger;      // Logger implementation
pub mod level;       // Log levels
pub mod span;        // Log spans
pub mod event;       // Log events
pub mod subscriber;  // Subscriber implementation
pub mod format;      // Log formatting
```

**Key Types:**

```rust
// Log level
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum Level {
    Trace,
    Debug,
    Info,
    Warn,
    Error,
}

// Log event
#[derive(Debug)]
pub struct LogEvent {
    pub level: Level,
    pub target: &'static str,
    pub message: String,
    pub fields: HashMap<String, Value>,
    pub timestamp: SystemTime,
}
```

#### 4.1.4 ilang-config

**Purpose:** Project and compiler configuration management.

**Modules:**

```rust
// crates/ilang-config/src/lib.rs

pub mod project;     // Project configuration
pub mod compiler;    // Compiler configuration
pub mod format;      // Formatter configuration
pub mod lint;        // Linter configuration
pub mod test;        // Test configuration
pub mod toml;        // TOML parsing
```

**Key Types:**

```rust
// Project configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectConfig {
    pub name: String,
    pub version: String,
    pub description: Option<String>,
    pub authors: Vec<String>,
    pub license: Option<String>,
    pub repository: Option<String>,
    pub edition: Edition,
}

// Compiler configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompilerConfig {
    pub target: Target,
    pub optimization: OptimizationLevel,
    pub debug: bool,
    pub emit: EmitOption,
    pub warnings: WarningsConfig,
}

// Edition
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub enum Edition {
    #[serde(rename = "2027")]
    Edition2027,
}

// Target
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Target {
    pub triple: String,
    pub features: Vec<String>,
}
```

#### 4.1.5 ilang-error

**Purpose:** Typed error handling framework.

**Modules:**

```rust
// crates/ilang-error/src/lib.rs

pub mod error;       // Error types
pub mod result;      // Result extensions
pub mod context;     // Error context
pub mod report;      // Error reporting
pub mod suggestion;  // Error suggestions
```

**Key Types:**

```rust
// Error trait
pub trait IlangError: std::error::Error {
    fn code(&self) -> DiagnosticCode;
    fn severity(&self) -> Severity;
    fn message(&self) -> &Message;
    fn spans(&self) -> &[Span];
    fn suggestions(&self) -> &[Suggestion];
}

// Error result extension
pub trait ResultExt<T> {
    fn with_context(self, context: &str) -> Result<T, IlError>;
    fn with_span(self, span: Span) -> Result<T, IlError>;
}

// Ilang error
#[derive(Debug, thiserror::Error)]
pub enum IlError {
    #[error("{0}")]
    Lexer(#[from] LexerError),
    
    #[error("{0}")]
    Parser(#[from] ParserError),
    
    #[error("{0}")]
    Semantic(#[from] SemanticError),
    
    #[error("{0}")]
    Type(#[from] TypeError),
    
    #[error("{0}")]
    Runtime(#[from] RuntimeError),
    
    #[error("{0}")]
    Io(#[from] std::io::Error),
    
    #[error("{0}")]
    Config(#[from] ConfigError),
}
```

#### 4.1.6 ilang-utils

**Purpose:** Common utilities and data structures.

**Modules:**

```rust
// crates/ilang-utils/src/lib.rs

pub mod collections;   // Specialized collections
pub mod interner;      // String interner
pub mod builder;       // Builder pattern utilities
pub mod cache;         // Caching utilities
pub mod path;          // Path utilities
pub mod hash;          // Hashing utilities
pub mod bit;           // Bit manipulation
pub mod utf8;          // UTF-8 utilities
```

**Key Types:**

```rust
// String interner
pub struct Interner<T: Hash + Eq> {
    strings: Vec<String>,
    map: HashMap<String, T>,
}

// Arena allocator
pub struct Arena<T> {
    chunks: Vec<Box<[MaybeUninit<T>]>>,
    current: usize,
}

// Builder trait
pub trait Builder {
    type Target;
    
    fn build(self) -> Result<Self::Target, BuildError>;
}
```

#### 4.1.7 ilang-test

**Purpose:** Test harness and utilities.

**Modules:**

```rust
// crates/ilang-test/src/lib.rs

pub mod harness;      // Test harness
pub mod fixture;      // Test fixtures
pub mod snapshot;     // Snapshot testing
pub mod fuzz;         // Fuzz testing
pub mod property;     // Property-based testing
pub mod coverage;     // Coverage reporting
```

**Key Types:**

```rust
// Test harness
pub struct TestHarness {
    fixtures: PathBuf,
    snapshots: PathBuf,
    temp_dir: PathBuf,
}

// Snapshot test
pub fn assert_snapshot(name: &str, actual: &str) {
    // Compare with stored snapshot
}

// Fuzz target
pub fn fuzz_target(data: &[u8]) {
    // Fuzz test implementation
}
```

#### 4.1.8 ilang-bench

**Purpose:** Benchmark harness.

**Modules:**

```rust
// crates/ilang-bench/src/lib.rs

pub mod harness;      // Benchmark harness
pub mod measure;      // Measurement utilities
pub mod report;       // Report generation
pub mod compare;      // Comparison utilities
```

**Key Types:**

```rust
// Benchmark harness
pub struct BenchHarness {
    warmup: Duration,
    iterations: usize,
    sample_size: usize,
}

// Benchmark result
pub struct BenchResult {
    pub name: String,
    pub mean: Duration,
    pub std_dev: Duration,
    pub samples: Vec<Duration>,
}
```

#### 4.1.9 ilang-doc

**Purpose:** Documentation generation.

**Modules:**

```rust
// crates/ilang-doc/src/lib.rs

pub mod generator;    // Documentation generator
pub mod extractor;    // Documentation extractor
pub mod template;     // Documentation templates
pub mod search;       // Search index generation
```

**Key Types:**

```rust
// Documentation generator
pub struct DocGenerator {
    input: PathBuf,
    output: PathBuf,
    format: DocFormat,
    theme: DocTheme,
}

// Documentation item
pub struct DocItem {
    pub name: String,
    pub kind: DocKind,
    pub documentation: Option<String>,
    pub source: Option<Span>,
    pub children: Vec<DocItem>,
}
```

---

## 5. Task Breakdown

### 5.1 Task List

| ID | Task | Priority | Estimate | Dependencies |
|----|------|----------|----------|--------------|
| 5.1.1 | Create workspace structure | Critical | 1 day | - |
| 5.1.2 | Implement ilang-core | Critical | 5 days | 5.1.1 |
| 5.1.3 | Implement ilang-diagnostics | Critical | 5 days | 5.1.2 |
| 5.1.4 | Implement ilang-logging | High | 3 days | 5.1.2 |
| 5.1.5 | Implement ilang-config | High | 3 days | 5.1.2 |
| 5.1.6 | Implement ilang-error | Critical | 4 days | 5.1.3 |
| 5.1.7 | Implement ilang-utils | High | 5 days | 5.1.2 |
| 5.1.8 | Implement ilang-test | High | 4 days | 5.1.2 |
| 5.1.9 | Implement ilang-bench | Medium | 3 days | 5.1.2 |
| 5.1.10 | Implement ilang-doc | Medium | 3 days | 5.1.2 |
| 5.1.11 | Write documentation | High | 5 days | All above |
| 5.1.12 | Write examples | High | 3 days | All above |
| 5.1.13 | Performance benchmarks | Medium | 2 days | All above |
| 5.1.14 | Security review | High | 2 days | All above |
| 5.1.15 | Cross-platform testing | High | 3 days | All above |

**Total Estimated Duration:** 45 days (9 weeks)

### 5.2 Milestone Schedule

| Milestone | Date | Tasks |
|-----------|------|-------|
| M5.1.1 | Week 1 | 5.1.1, 5.1.2 |
| M5.1.2 | Week 2 | 5.1.3, 5.1.4 |
| M5.1.3 | Week 3 | 5.1.5, 5.1.6 |
| M5.1.4 | Week 4 | 5.1.7, 5.1.8 |
| M5.1.5 | Week 5 | 5.1.9, 5.1.10 |
| M5.1.6 | Week 6-7 | 5.1.11, 5.1.12 |
| M5.1.7 | Week 8 | 5.1.13, 5.1.14 |
| M5.1.8 | Week 9 | 5.1.15, Final review |

---

## 6. Testing Strategy

### 6.1 Test Types

| Type | Coverage Target | Description |
|------|-----------------|-------------|
| Unit Tests | 95% | Individual function tests |
| Integration Tests | 90% | Module interaction tests |
| Property Tests | 80% | Property-based testing |
| Fuzz Tests | N/A | Random input testing |
| Snapshot Tests | 100% | Output comparison tests |
| Performance Tests | N/A | Benchmark regression tests |

### 6.2 Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── core/
│   ├── diagnostics/
│   ├── logging/
│   ├── config/
│   ├── error/
│   └── utils/
├── integration/             # Integration tests
│   ├── core_diagnostics.rs
│   ├── config_error.rs
│   └── ...
├── property/                # Property tests
│   ├── core_properties.rs
│   └── ...
├── fuzz/                    # Fuzz tests
│   ├── fuzz_target.rs
│   └── ...
├── snapshot/                # Snapshot tests
│   ├── diagnostics/
│   └── ...
└── bench/                   # Benchmarks
    ├── core_bench.rs
    └── ...
```

### 6.3 Test Conventions

```rust
// Unit test convention
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_function_name() {
        // Arrange
        let input = "test";
        
        // Act
        let result = function(input);
        
        // Assert
        assert_eq!(result, expected);
    }
    
    #[test]
    fn test_error_case() {
        // Test error conditions
        let result = function("");
        assert!(result.is_err());
    }
}

// Integration test convention
#[test]
fn integration_test_name() {
    // Test component interaction
}

// Property test convention
#[test]
fn property_test_name() {
    // Property-based testing
}
```

### 6.4 CI Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --workspace
      - run: cargo test --workspace --release
      - run: cargo clippy --workspace -- -D warnings
      - run: cargo fmt --all -- --check
```

---

## 7. Security Considerations

### 7.1 Security Requirements

| Requirement | Description | Verification |
|-------------|-------------|--------------|
| Input Validation | All inputs validated | Unit tests |
| Memory Safety | No unsafe code | Clippy audit |
| Dependency Audit | All dependencies audited | cargo-audit |
| Secret Handling | No hardcoded secrets | Static analysis |
| Supply Chain | Dependencies pinned | Cargo.lock |

### 7.2 Security Review Checklist

- [ ] No `unsafe` code blocks
- [ ] All public APIs documented
- [ ] Input validation on all external data
- [ ] Error messages don't leak secrets
- [ ] Dependencies are audited
- [ ] No unsafe deserialization
- [ ] Memory safety verified

### 7.3 Dependency Management

```toml
# Cargo.toml dependencies
[dependencies]
# Pin all dependencies
serde = "=1.0.193"
serde_json = "=1.0.108"
# ...

[dev-dependencies]
# Test dependencies
criterion = "=0.5.1"
```

---

## 8. Performance Considerations

### 8.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Compile Time | < 30s | Clean build |
| Link Time | < 10s | Release build |
| Binary Size | < 50MB | Stripped release |
| Memory Usage | < 100MB | Idle |
| Startup Time | < 100ms | Cold start |

### 8.2 Performance Optimization Strategies

1. **Arena Allocation**: Use arena allocators for temporary data
2. **String Interning**: Intern strings for faster comparison
3. **Incremental Compilation**: Cache intermediate results
4. **Parallel Processing**: Use rayon for parallel work
5. **Memory Pooling**: Pool frequently allocated objects

### 8.3 Benchmarking

```rust
// benches/core_bench.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_interner(c: &mut Criterion) {
    let mut interner = Interner::new();
    
    c.bench_function("intern_string", |b| {
        b.iter(|| interner.intern(black_box("test_string")))
    });
}

criterion_group!(benches, bench_interner);
criterion_main!(benches);
```

---

## 9. Documentation Requirements

### 9.1 Documentation Types

| Type | Location | Audience |
|------|----------|----------|
| API Documentation | Source code | Developers |
| Architecture Guide | docs/ | Contributors |
| User Guide | docs/ | Users |
| Examples | examples/ | Learners |
| Changelog | CHANGELOG.md | All |

### 9.2 Documentation Standards

```rust
/// Brief description of the function.
///
/// Longer description with more details.
///
/// # Arguments
///
/// * `input` - The input string to process
/// * `config` - Configuration options
///
/// # Returns
///
/// The processed string.
///
/// # Errors
///
/// Returns `Err` if the input is invalid.
///
/// # Examples
///
/// ```
/// let result = process("hello", &config)?;
/// assert_eq!(result, "HELLO");
/// ```
///
/// # Panics
///
/// This function does not panic.
pub fn process(input: &str, config: &Config) -> Result<String, Error> {
    // Implementation
}
```

### 9.3 Documentation Generation

```bash
# Generate documentation
cargo doc --workspace --no-deps

# Open documentation
cargo doc --workspace --no-deps --open

# Check documentation
cargo doc --workspace --no-deps 2>&1 | grep "warning"
```

---

## 10. Definition of Done

### 10.1 Phase 5.1 is complete when:

- [ ] All crates implemented and compiling
- [ ] Unit tests passing (> 90% coverage)
- [ ] Integration tests passing
- [ ] Documentation complete
- [ ] Examples working
- [ ] Benchmarks established
- [ ] CI/CD pipeline working
- [ ] Cross-platform testing passing
- [ ] Security review complete
- [ ] Performance review complete
- [ ] Code review complete
- [ ] Changelog updated
- [ ] Release notes drafted

### 10.2 Quality Gates

| Gate | Requirement | Status |
|------|-------------|--------|
| Build | Clean build passes | - |
| Tests | All tests pass | - |
| Coverage | > 90% | - |
| Lint | No warnings | - |
| Format | Formatted | - |
| Docs | All public API documented | - |
| Bench | Benchmarks pass | - |
| Security | No vulnerabilities | - |
| Review | Code reviewed | - |

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
