# I Programming Language - Project Structure

## Overview

This document describes the organized project structure for the I Programming Language.

## Directory Structure

```
ilang/
├── src/                          # Source Code
│   ├── compiler/                 # Compiler Implementation
│   │   ├── lexer/               # Lexer/Tokenizer
│   │   ├── parser/              # Parser/AST Generation
│   │   ├── ast/                 # Abstract Syntax Tree
│   │   ├── semantic/            # Semantic Analysis
│   │   ├── typechecker/         # Type Checking
│   │   ├── ir/                  # Intermediate Representation
│   │   ├── optimizer/           # Code Optimization
│   │   ├── codegen/             # Code Generation
│   │   └── compiler.py          # Main Compiler Entry
│   │
│   ├── vm/                      # Virtual Machine
│   │   ├── core/                # Core VM Implementation
│   │   ├── gc/                  # Garbage Collector
│   │   ├── instructions/        # Instruction Set
│   │   └── vm.py                # Main VM Entry
│   │
│   └── stdlib/                  # Standard Library
│       ├── core/                # Core Module
│       ├── math/                # Math Module
│       ├── string/              # String Module
│       ├── array/               # Array Module
│       ├── io/                  # I/O Module
│       └── time/                # Time Module
│
│   └── compiler/core/          # ✅ SPRINT 0 COMPLETE
│       ├── workspace/           # Workspace Configuration
│       ├── build/               # Build System
│       ├── logging/             # Logging Framework
│       ├── config/              # Configuration Loader
│       ├── source/              # Source File Abstraction
│       ├── unicode/             # Unicode Utilities
│       ├── diagnostics/         # Diagnostic Engine
│       ├── formatting/          # Message Formatting
│       ├── io/                  # File Manager & Paths
│       ├── memory/              # Memory Utilities
│       ├── timing/              # Timing Utilities
│       ├── features/            # Feature Flags
│       ├── context/             # Compiler Context
│       ├── testing/             # Test Framework
│       ├── benchmarks/          # Benchmark Framework
│       └── docs_generator/      # Documentation Generator
│
├── docs/                        # Documentation
│   ├── specification/           # Language Specification
│   │   └── LANGUAGE_SPECIFICATION.md
│   │
│   ├── architecture/            # Architecture Documents
│   │   ├── compiler-architecture.md
│   │   ├── lexer-design.md
│   │   ├── parser-design.md
│   │   ├── ast-design.md
│   │   ├── semantic-analyzer-design.md
│   │   ├── type-system-design.md
│   │   ├── memory-model-design.md
│   │   ├── virtual-machine-design.md
│   │   ├── native-compiler-roadmap.md
│   │   ├── performance-strategy.md
│   │   └── error-system-design.md
│   │
│   ├── ecosystem/               # Ecosystem Architecture
│   │   ├── stdlib-architecture.md
│   │   ├── frameworks-architecture.md
│   │   ├── developer-tools-architecture.md
│   │   ├── package-registry-architecture.md
│   │   ├── website-learning-platform.md
│   │   ├── community-governance.md
│   │   └── ecosystem-architecture-review.md
│   │
│   ├── evolution/               # Language Evolution
│   │   ├── language-philosophy.md
│   │   ├── rfc-system.md
│   │   ├── language-evolution.md
│   │   ├── version-roadmap-30year.md
│   │   ├── self-hosting-roadmap.md
│   │   ├── ecosystem-maturity-model.md
│   │   ├── language-standards.md
│   │   ├── security-strategy.md
│   │   ├── worldwide-adoption-strategy.md
│   │   ├── future-of-i.md
│   │   └── master-plan.md
│   │
│   ├── implementation/          # Implementation Plans
│   │   ├── IPMP.md              # I Programming Language Master Plan
│   │   ├── phase-5.1-core-infrastructure.md
│   │   ├── phase-5.2-compiler-frontend.md
│   │   ├── phase-5.3-semantic-analysis.md
│   │   ├── phase-5.4-type-checker.md
│   │   ├── phase-5.5-intermediate-representation.md
│   │   ├── phase-5.6-optimizer.md
│   │   ├── phase-5.7-virtual-machine.md
│   │   ├── phase-5.8-standard-library.md
│   │   ├── phase-5.9-package-manager.md
│   │   ├── phase-5.10-developer-tools.md
│   │   └── phase-6-eem.md      # Engineering Execution Manual
│   │
│   ├── guides/                  # User Guides
│   │   ├── getting-started.md
│   │   ├── tutorials/
│   │   └── examples/
│   │
│   └── api/                     # API Documentation
│       ├── stdlib-api.md
│       └── compiler-api.md
│
├── tests/                       # Test Suite
│   ├── unit/                    # Unit Tests
│   │   ├── test_lexer.py
│   │   ├── test_parser.py
│   │   ├── test_ast.py
│   │   ├── test_semantic.py
│   │   ├── test_typechecker.py
│   │   ├── test_vm.py
│   │   └── test_stdlib.py
│   │
│   ├── integration/             # Integration Tests
│   │   ├── test_compiler_pipeline.py
│   │   ├── test_vm_execution.py
│   │   └── test_end_to_end.py
│   │
│   ├── fuzzing/                 # Fuzz Tests
│   │   ├── fuzz_lexer.rs
│   │   ├── fuzz_parser.rs
│   │   └── fuzz_compiler.rs
│   │
│   ├── benchmarks/              # Performance Tests
│   │   ├── lexer_benchmark.rs
│   │   ├── parser_benchmark.rs
│   │   └── vm_benchmark.rs
│   │
│   ├── golden/                  # Golden Tests
│   │   ├── valid/
│   │   └── invalid/
│   │
│   └── snapshots/               # Snapshot Tests
│       ├── lexer/
│       └── parser/
│
├── examples/                    # Example Programs
│   ├── hello.i
│   ├── fibonacci.i
│   ├── functions.i
│   ├── conditionals.i
│   ├── loops.i
│   ├── structs.i
│   ├── variables.i
│   └── tutorials/
│
├── tools/                       # Developer Tools
│   ├── lsp/                     # Language Server Protocol
│   ├── formatter/               # Code Formatter (iformat)
│   ├── linter/                  # Linter
│   ├── debugger/                # Debugger (idebug)
│   ├── test-runner/             # Test Runner (itest)
│   ├── doc-gen/                 # Documentation Generator
│   └── package-manager/         # Package Manager (isoko)
│
├── frameworks/                  # Official Frameworks
│   ├── web/                     # urubuga (Web Framework)
│   ├── cli/                     # ibiro (CLI Framework)
│   ├── mobile/                  # Mobile Framework
│   ├── ai/                      # ubwenge (AI/ML Framework)
│   ├── games/                   # imikino (Game Engine)
│   ├── iot/                     # sisitemu (IoT Framework)
│   └── data/                    # igicu (Data Processing)
│
├── stdlib/                      # Standard Library Source
│   ├── core/                    # Core Module
│   ├── math/                    # Math Module
│   ├── string/                  # String Module
│   ├── array/                   # Array Module
│   ├── map/                     # Map Module
│   ├── io/                      # I/O Module
│   ├── time/                    # Time Module
│   ├── testing/                 # Testing Module
│   └── debug/                   # Debug Module
│
├── runtime/                     # Runtime System
│   ├── core/                    # Core Runtime
│   ├── gc/                      # Garbage Collector
│   └── libraries/               # Runtime Libraries
│
├── scripts/                     # Build/Deploy Scripts
│   ├── build/                   # Build Scripts
│   ├── test/                    # Test Scripts
│   ├── release/                 # Release Scripts
│   ├── deploy/                  # Deploy Scripts
│   └── maintenance/             # Maintenance Scripts
│
├── .github/                     # GitHub Configuration
│   ├── workflows/               # CI/CD Pipelines
│   ├── issue-templates/         # Issue Templates
│   ├── pr-templates/            # PR Templates
│   ├── milestones.md
│   └── labels.md
│
├── config/                      # Configuration Files
│   ├── rust/                    # Rust Configuration
│   │   ├── Cargo.toml
│   │   └── rustfmt.toml
│   ├── python/                  # Python Configuration
│   │   ├── pyproject.toml
│   │   └── setup.cfg
│   └── tools/                   # Tool Configuration
│       ├── .pre-commit-config.yaml
│       ├── .editorconfig
│       └── .gitignore
│
├── README.md                    # Project README
├── ARCHITECTURE.md              # Architecture Overview
├── CONTRIBUTING.md              # Contributing Guidelines
├── CODE_OF_CONDUCT.md           # Code of Conduct
├── CHANGELOG.md                 # Changelog
├── LICENSE                      # License
├── GOVERNANCE.md                # Governance
├── SECURITY.md                  # Security Policy
├── TESTING_GUIDE.md             # Testing Guide
├── STYLE_GUIDE.md               # Style Guide
├── API_GUIDELINES.md            # API Guidelines
├── VERSIONING.md                # Versioning Policy
├── RELEASE_PROCESS.md           # Release Process
└── ROADMAP.md                   # Roadmap
```

## Key Principles

1. **Logical Grouping**: Related files are grouped together
2. **Clear Hierarchy**: Maximum 3 levels of nesting
3. **Consistent Naming**: Snake_case for directories, consistent file naming
4. **Separation of Concerns**: Source, tests, docs, tools are separate
5. **Easy Navigation**: Clear paths to find any file

## Migration Notes

### From Old Structure

| Old Location | New Location |
|--------------|--------------|
| `compiler/` | `src/compiler/` |
| `vm/` | `src/vm/` |
| `tests/` | `tests/unit/` |
| `docs/` | `docs/guides/` |
| `docs-internals/` | `docs/` (merged) |
| `docs-specification/` | `docs/specification/` |
| `frameworks-*` | `frameworks/` |
| `ide-*` | `tools/` |
| `stdlib-*` | `stdlib/` |
| `runtime-*` | `runtime/` |
| `scripts-*` | `scripts/` |

### Files to Move

1. Move `compiler/` → `src/compiler/`
2. Move `vm/` → `src/vm/`
3. Move `tests/unit/*` → `tests/unit/`
4. Move `examples/*` → `examples/`
5. Merge `docs-internals/*` → `docs/`
6. Merge `docs-specification/*` → `docs/specification/`
7. Merge `frameworks-*` → `frameworks/`
8. Merge `ide-*` → `tools/`
9. Merge `stdlib-*` → `stdlib/`
10. Merge `runtime-*` → `runtime/`
11. Merge `scripts-*` → `scripts/`

### Files to Remove

1. Empty directories
2. Duplicate files
3. Temporary files
4. Build artifacts

## Configuration Files

### Root Level
- `README.md` - Project overview
- `LICENSE` - License file
- `CONTRIBUTING.md` - Contribution guidelines
- `CODE_OF_CONDUCT.md` - Code of conduct
- `CHANGELOG.md` - Version history
- `GOVERNANCE.md` - Governance model
- `SECURITY.md` - Security policy
- `ARCHITECTURE.md` - Architecture overview
- `TESTING_GUIDE.md` - Testing guide
- `STYLE_GUIDE.md` - Style guide
- `API_GUIDELINES.md` - API guidelines
- `VERSIONING.md` - Versioning policy
- `RELEASE_PROCESS.md` - Release process
- `ROADMAP.md` - Project roadmap

### Config Directory
- `config/rust/Cargo.toml` - Rust project config
- `config/python/pyproject.toml` - Python project config
- `config/tools/.pre-commit-config.yaml` - Pre-commit hooks

## Documentation Structure

### Specification
- `docs/specification/LANGUAGE_SPECIFICATION.md` - Official language spec

### Architecture
- `docs/architecture/` - System architecture documents

### Ecosystem
- `docs/ecosystem/` - Ecosystem architecture

### Evolution
- `docs/evolution/` - Language evolution plans

### Implementation
- `docs/implementation/` - Implementation plans and phases

### Guides
- `docs/guides/` - User guides and tutorials

### API
- `docs/api/` - API documentation

## Testing Structure

### Unit Tests
- `tests/unit/` - Individual component tests

### Integration Tests
- `tests/integration/` - Component interaction tests

### Fuzz Tests
- `tests/fuzzing/` - Random input testing

### Benchmarks
- `tests/benchmarks/` - Performance tests

### Golden Tests
- `tests/golden/` - Output comparison tests

### Snapshot Tests
- `tests/snapshots/` - Snapshot testing

## Tools Structure

### Language Server
- `tools/lsp/` - LSP implementation

### Formatter
- `tools/formatter/` - Code formatter

### Linter
- `tools/linter/` - Code linter

### Debugger
- `tools/debugger/` - Debugger implementation

### Test Runner
- `tools/test-runner/` - Test runner

### Documentation Generator
- `tools/doc-gen/` - Doc generator

### Package Manager
- `tools/package-manager/` - isoko package manager

## Frameworks Structure

### Web Framework
- `frameworks/web/` - urubuga web framework

### CLI Framework
- `frameworks/cli/` - ibiro CLI framework

### Mobile Framework
- `frameworks/mobile/` - Mobile development

### AI/ML Framework
- `frameworks/ai/` - ubwenge AI framework

### Game Engine
- `frameworks/games/` - imikino game engine

### IoT Framework
- `frameworks/iot/` - sisitemu IoT framework

### Data Processing
- `frameworks/data/` - igicu data processing

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
