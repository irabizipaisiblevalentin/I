# Self-Hosting Feasibility Assessment

## Sprint 9.10 — Version 1.0 Release Readiness

---

> *"Kuvana Imana, Kubaka Icyo Turije"*
> *From God, Building What We Have*

---

| Document Control | |
|---|---|
| **Version** | 1.0 |
| **Date** | July 30, 2026 |
| **Status** | **Assessment Only — Awaiting Approval** |
| **Sprint** | 9.10 — Production Self-Hosting Compiler |
| **Compiler** | Python bootstrap (13,749 lines across 57 files) |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Self-Hosting Strategy](#2-self-hosting-strategy)
3. [Feature Gap Analysis](#3-feature-gap-analysis)
4. [Critical Gaps Requiring RFC](#4-critical-gaps-requiring-rfc)
5. [Implementation Phases](#5-implementation-phases)
6. [Risk Assessment](#6-risk-assessment)
7. [Recommendation](#7-recommendation)
8. [References](#8-references)

---

## 1. Executive Summary

### 1.1 What We Have

The I compiler is currently a **57-file, 13,749-line Python implementation** that:

- Lexes, parses, and semantically analyses `.i` source files
- Generates bytecode for a virtual machine
- Generates native code via a production native backend (Sprint 9.9)
- Passes 693 tests (252 native + 441 VM)

### 1.2 What Self-Hosting Requires

A self-hosting compiler means the I compiler is written in I itself. This requires:

1. The I language implementation (Python) to be rewritten in I
2. The rewritten I compiler to be compiled by the current Python compiler
3. The resulting binary to compile itself (bootstrapping verification)

### 1.3 Key Finding

**Self-hosting is feasible but requires 5 critical language features that are not currently specified or implemented.** These gaps must be addressed via RFC before implementation can begin.

---

## 2. Self-Hosting Strategy

### 2.1 Roadmap Alignment

Per `docs/evolution/self-hosting-roadmap.md`, self-hosting proceeds in 6 stages:

```
Stage 1: Bootstrap Compiler   ← We are here (Python compiler)
Stage 2: Hybrid Compiler      ← Write frontend components in I
Stage 3: Partial Self-Hosting ← Most components in I
Stage 4: Full Self-Hosting    ← Entire compiler in I
Stage 5: Optimized Self-Hosting
Stage 6: Native Backend
```

### 2.2 Recommended Approach: Hybrid First

Rather than rewriting the entire 57-file Python compiler in I at once, we use a hybrid approach:

1. **Keep Python VM and native backend** as-is (performance-critical)
2. **Rewrite frontend components** (lexer, parser, AST) in I first
3. **Gradually replace** semantic analysis, type checker, and codegen
4. **Finally replace** VM and native backend

This allows incremental verification at each step.

### 2.3 Translation Scope

| Component | Python Files | Python Lines | I Files (est.) | I Lines (est.) | Priority |
|-----------|-------------|-------------|----------------|----------------|----------|
| Lexer | 3 | ~800 | 3 | ~600 | 1 |
| Parser | 3 | ~1,200 | 3 | ~900 | 2 |
| AST | 2 | ~1,500 | 2 | ~1,200 | 3 |
| Semantic | 3 | ~1,800 | 3 | ~1,500 | 4 |
| Type System | 2 | ~1,200 | 2 | ~1,000 | 5 |
| Codegen | 3 | ~1,500 | 3 | ~1,200 | 6 |
| IR | 3 | ~800 | 3 | ~700 | 7 |
| Optimizer | 3 | ~1,000 | 3 | ~800 | 8 |
| VM | 5 | ~2,000 | 5 | ~1,800 | 9 (keep Python) |
| Native Backend | 16 | ~13,749 (total) | — | — | 10 (keep Python) |

---

## 3. Feature Gap Analysis

### 3.1 Language Feature Inventory

Each row assesses whether the I language (as specified) supports a feature needed for self-hosting.

| # | Feature | Required For | Specified? | Implemented? | Gap |
|---|---------|-------------|------------|--------------|-----|
| 1 | File I/O | Reading source files, writing output | ❌ | ❌ | CRITICAL |
| 2 | String library (slice, index, length, concat) | Lexing, parsing, codegen | ⚠️ Partial | ❌ | CRITICAL |
| 3 | String formatting / interpolation | Code generation, error messages | ❌ | ❌ | CRITICAL |
| 4 | Command-line arguments | Accepting input files and flags | ❌ | ❌ | CRITICAL |
| 5 | System/OS interface | File system access, process spawning | ❌ | ❌ | CRITICAL |
| 6 | Generic data structures | Type-safe collections for compiler data | ⚠️ Listed but as "future" | ❌ | CRITICAL |
| 7 | Enums with associated data | AST node types, token types | ⚠️ `ikindi` specified, no data | ❌ | CRITICAL |
| 8 | Pattern matching | AST node traversal, type analysis | ❌ (future extension) | ❌ | CRITICAL |
| 9 | Hash/map library | Symbol tables, keyword lookup | ⚠️ `map<K,V>` specified | ❌ | HIGH |
| 10 | List/array library | Token streams, AST lists | ⚠️ `list<T>` specified | ❌ | HIGH |
| 11 | Set library | Uniqueness checks | ⚠️ `set<T>` specified | ❌ | HIGH |
| 12 | Option/result types | Error handling without exceptions | ❌ | ❌ | HIGH |
| 13 | Iterators / for-each loops | Collection traversal | ✅ (`buri` loop) | ❌ | HIGH |
| 14 | Lambda functions | Callbacks, visitors | ✅ (specified) | ❌ | HIGH |
| 15 | Recursive functions | Recursive descent parsing | ✅ (inferred) | ❌ | MEDIUM |
| 16 | Structs with methods | AST nodes, compiler components | ✅ (`igiceri`) | ❌ | MEDIUM |
| 17 | Enums | Token types, AST node kinds | ✅ (`ikindi`) | ❌ | MEDIUM |
| 18 | Module system | Organizing compiler code | ✅ (`shyiramo`/`tanga`) | ❌ | MEDIUM |
| 19 | Error handling (try/catch) | Robust error recovery | ✅ (specified) | ❌ | MEDIUM |
| 20 | Integer arithmetic | Offset tracking, size calculations | ✅ | ❌ | MEDIUM |
| 21 | Boolean logic | Conditionals | ✅ | ❌ | LOW |
| 22 | Variables and assignment | General programming | ✅ | ❌ | LOW |
| 23 | Functions | General programming | ✅ | ❌ | LOW |
| 24 | If/else conditionals | General programming | ✅ | ❌ | LOW |
| 25 | Loops (while, for, until) | General programming | ✅ | ❌ | LOW |
| 26 | Classes / inheritance | Compiler component hierarchy | ✅ (`urwego`+`kugira`) | ❌ | LOW |
| 27 | Interfaces / traits | Abstract compiler components | ✅ (`akabuto`/`urubingo`) | ❌ | LOW |

### 3.2 Gap Severity Summary

| Severity | Count | Action Required |
|----------|-------|-----------------|
| CRITICAL | 8 | Must be specified, RFC'd, and implemented before self-hosting begins |
| HIGH | 5 | Must be available before hybrid stage is complete |
| MEDIUM | 4 | Must be available before partial self-hosting |
| LOW | 7 | Already specified; implementation needed |

### 3.3 Status Legend

- ✅ = Feature is in the LANGUAGE_SPECIFICATION.md
- ⚠️ = Feature is partially specified or contradictory (e.g., generics listed as "future extension" but generic types `list<T>` are in the spec)
- ❌ = Feature is not in the specification

---

## 4. Critical Gaps Requiring RFC

### 4.1 RFC-001: Standard Library Foundation

**Gap**: No file I/O, string library, or system interface specified.

**Required for**: Reading source files (`shyiramo "file.i"`), writing output, string manipulation for lexing and code generation.

**Proposal**: Define a standard library module `urubuga` (foundation) with:
- `soma_dosive(path) -> string` — Read file
- `andika_dosive(path, content)` — Write file
- `string.slice(start, end) -> string` — String slicing
- `string.find(pattern) -> int` — String search
- `string.length() -> int` — String length
- `string.format(values...) -> string` — String formatting
- `komandi_zemerera()` — Command-line arguments access

### 4.2 RFC-002: Generics System

**Gap**: `list<T>`, `map<K,V>`, `set<T>`, `tuple<T...>` are specified using generic syntax, but generics are listed as a "Future Extension".

**Required for**: Type-safe collections throughout the compiler.

**Proposal**: Implement generics as monomorphization with:
- Generic structs: `igiceri List<T>`
- Generic functions: `umurimo first<T>(items: list<T>) -> T`
- Type constraints: `urubingo Comparable<T>`

### 4.3 RFC-003: Algebraic Data Types & Pattern Matching

**Gap**: `ikindi` (enum) is specified but without associated data. No pattern matching.

**Required for**: AST node types like `Expr.If`, `Expr.Binary` with different payloads per variant.

**Proposal**: 
- Enums with associated data: `ikindi Expr = Binary(left: Expr, op: Operator, right: Expr) | Literal(value: any)`
- Pattern matching: `gereranya expr { ... }` statement for destructuring

### 4.4 RFC-004: String Library & Formatting

**Gap**: No string formatting or interpolation mechanism.

**Required for**: Code generation, error messages, debug output.

**Proposal**:
- String interpolation: `"Muraho {name}"` 
- Format strings: `"Error at line {line}: {message}".format(line, message)`
- StringBuilder pattern for efficient concatenation

### 4.5 RFC-005: Option/Result Types

**Gap**: No safe nullable or result types.

**Required for**: Error handling without exceptions (preferred in compiler code), nullable AST nodes.

**Proposal**:
- `Option<T>` type: `T | ubusa` or explicit `Option<T>` with `Some(value)` / `None` variants
- `Result<T, E>` type for fallible operations without exceptions
- `?` operator for early propagation: `shyira value = fallible() ?`

---

## 5. Implementation Phases

### 5.1 Phase 1: Foundation (Sprint 9.10a)

**Prerequisite**: RFCs 1-5 accepted

**Deliverables**:
- Standard library foundation (`urubuga` module)
- String library with slicing, formatting
- File I/O functions
- Command-line argument support
- Basic `list<T>`, `map<K,V>`, `set<T>` implementations

**Verification**: Write a simple I program that reads a file, processes strings, and writes output.

### 5.2 Phase 2: Lexer in I (Sprint 9.10b)

**Deliverables**:
- `src/compiler/i/lexer.i` — Token definitions, lexer state machine
- `src/compiler/i/token.i` — Token type enum with associated data
- I lexer matches Python lexer output exactly

**Verification**: Golden tests comparing lexer output (Python vs I)

### 5.3 Phase 3: Parser & AST in I (Sprint 9.10c)

**Deliverables**:
- `src/compiler/i/parser.i` — Recursive descent parser
- `src/compiler/i/ast.i` — AST node definitions with algebraic data types

**Verification**: Parse existing `.i` test files and produce matching ASTs

### 5.4 Phase 4: Semantic Analysis & Type Checker in I (Sprint 9.10d)

**Deliverables**:
- `src/compiler/i/semantic.i` — Scope resolution, symbol tables
- `src/compiler/i/type_checker.i` — Type checking

**Verification**: Type-check the I compiler's own source code

### 5.5 Phase 5: Code Generator in I (Sprint 9.10e)

**Deliverables**:
- `src/compiler/i/codegen.i` — Bytecode generation
- `src/compiler/i/ir.i` — IR generation

**Verification**: Generate bytecode for the I compiler itself

### 5.6 Phase 6: Hybrid Integration (Sprint 9.10f)

**Deliverables**:
- Hybrid compiler: I frontend + Python VM/backend
- Bootstrap test: Python compiler compiles I compiler → I compiler compiles I programs

**Verification**: `ilang build --self-check` — compile compiler with bootstrap, then compile compiler with compiled compiler, compare outputs

---

## 6. Risk Assessment

### 6.1 Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Missing language features | HIGH | BLOCKER | RFC process before implementation |
| Bootstrap compiler bugs | MEDIUM | HIGH | Comprehensive golden tests |
| Performance of I-compiled code | HIGH | MEDIUM | Keep VM/native in Python for now |
| Circular translation dependency | MEDIUM | CRITICAL | Python bootstraps first I compiler |
| Feature creep during self-hosting | HIGH | HIGH | Language freeze in effect |
| RFC process delays | MEDIUM | MEDIUM | Prioritize RFCs by dependency order |

### 6.2 Mitigation Strategy

1. **Language freeze** prevents scope creep
2. **Incremental hybrid approach** ensures each step is verifiable
3. **Golden test suite** catches regressions between Python and I implementations
4. **Python compiler stays** as fallback until I compiler is verified
5. Each RFC is self-contained and independently implementable

---

## 7. Recommendation

### 7.1 Proceed Order

1. ✅ **Approve** language specification freeze (completed)
2. 🟡 **Submit** RFC-001 through RFC-005 for approval
3. ⏳ **Await** RFC acceptance before any implementation
4. 📋 **Begin** Phase 1 (Foundation) once RFCs are accepted

### 7.2 Do NOT Start

Per Sprint 9.10 stop conditions:
- Do NOT begin adding new language features until RFCs are approved
- Do NOT implement Version 1.0 Release until self-hosting is complete
- Do NOT skip RFC process for any critical gap

### 7.3 Estimated Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| RFC review & approval | 2-4 weeks | Community + TSC |
| Phase 1: Foundation | 2-4 weeks | RFC approval |
| Phase 2: Lexer in I | 1-2 weeks | Phase 1 |
| Phase 3: Parser & AST | 2-3 weeks | Phase 2 |
| Phase 4: Semantic & Type Checker | 2-3 weeks | Phase 3 |
| Phase 5: Code Generator | 2-3 weeks | Phase 4 |
| Phase 6: Hybrid Integration | 1-2 weeks | Phase 5 |
| **Total** | **12-21 weeks** | |

---

## 8. References

| Document | Location |
|----------|----------|
| Language Specification | `docs/specification/LANGUAGE_SPECIFICATION.md` |
| Compiler Architecture | `docs/architecture/compiler-architecture.md` |
| IPMP | `docs/IPMP.md` |
| Production Implementation Constitution | `docs/governance/PRODUCTION_IMPLEMENTATION_CONSTITUTION.md` |
| Self-Hosting Roadmap | `docs/evolution/self-hosting-roadmap.md` |
| Native Compiler Roadmap | `docs/architecture/native-compiler-roadmap.md` |
| RFC System | `docs/evolution/rfc-system.md` |
| Engineering Execution Manual | `docs/governance/ENGINEERING_EXECUTION_MANUAL.md` |
| VERSIONING | `docs/versioning/VERSIONING.md` |
| Release Process | `docs/release/RELEASE_PROCESS.md` |

---

**I Programming Language** — *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)

*This document is an assessment only. No implementation may begin without explicit approval.*
