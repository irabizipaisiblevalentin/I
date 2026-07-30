# Engineering Execution Manual

## The I Programming Language — Engineering Process & Workflows

---

> *"Kuvana Imana, Kubaka Icyo Turije"*
> *From God, Building What We Have*

---

| Document Control | |
|---|---|
| **Document Title** | Engineering Execution Manual |
| **Version** | 1.0 |
| **Date** | July 2026 |
| **Status** | **Official** |
| **Classification** | Governing Document |
| **Author** | I Programming Language Engineering Council |
| **Review Schedule** | Semi-Annual (January, July) |
| **Next Review** | January 2027 |

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Engineering Principles](#2-engineering-principles)
3. [Development Workflow](#3-development-workflow)
4. [Branching Strategy](#4-branching-strategy)
5. [Code Review Standards](#5-code-review-standards)
6. [Testing Standards](#6-testing-standards)
7. [CI/CD Pipeline](#7-cicd-pipeline)
8. [Issue & Sprint Management](#8-issue--sprint-management)
9. [Documentation Requirements](#9-documentation-requirements)
10. [Quality Gates](#10-quality-gates)
11. [Release Process](#11-release-process)
12. [Incident Response](#12-incident-response)
13. [References](#13-references)

---

## 1. Introduction

### 1.1 Purpose

This manual defines the engineering execution processes for the I Programming Language project. All contributors must follow these processes when implementing, testing, reviewing, and releasing code.

### 1.2 Scope

This manual covers all engineering activities:
- Compiler development (frontend, backend, VM)
- Runtime and standard library
- Tooling (package manager, IDE, build system)
- Documentation and testing infrastructure
- Release engineering

### 1.3 Relationship to Other Documents

| Document | Relationship |
|----------|-------------|
| PRODUCTION_IMPLEMENTATION_CONSTITUTION.md | Supreme governing authority; this manual implements its principles |
| LANGUAGE_SPECIFICATION.md | Formal language definition; all code must conform |
| IPMP.md | Strategic roadmap; this manual defines tactical execution |
| VERSIONING.md | Version numbering policy |
| RELEASE_PROCESS.md | Release-specific workflows |

---

## 2. Engineering Principles

### 2.1 Core Tenets

1. **Correctness before optimisation** — Make it work, then make it fast
2. **Readable code before clever code** — Code is written once, read many times
3. **Security by design** — Threat model every component
4. **Performance through architecture** — Choose the right algorithm first
5. **Testing before release** — No untested code reaches production
6. **Documentation before completion** — A feature is not done until it is documented
7. **Backwards compatibility** — Never break users without a migration path
8. **Stable public APIs** — Public API = contract with users
9. **Cross-platform behaviour** — Write once, run everywhere
10. **Predictable developer experience** — Consistent tooling and processes

### 2.2 Decision-Making Framework

When faced with an engineering decision, evaluate in this order:

1. **Safety** — Does this preserve memory safety, type safety, and security?
2. **Correctness** — Does this produce the right answer in all cases?
3. **Maintainability** — Will future engineers understand this code?
4. **Performance** — Does this meet performance requirements?
5. **Elegance** — Is this the simplest solution that works?

### 2.3 Technical Debt Policy

- Technical debt must be documented in the issue tracker with a `tech-debt` label
- Critical debt must be addressed within 1 sprint
- Non-critical debt must be addressed within 3 sprints
- No new debt may be introduced without a corresponding issue

---

## 3. Development Workflow

### 3.1 Feature Lifecycle

```
Idea → RFC (if required) → Design → Implementation → Review → Merge → Release

Each stage has clear exit criteria.
```

### 3.2 Stage 1: Idea

- Anyone may propose an idea via GitHub Discussions
- Ideas are informally discussed before formalisation
- No code is written at this stage

### 3.3 Stage 2: RFC (if required)

- Required for language changes, new APIs, breaking changes
- Follow the RFC process defined in `docs/evolution/rfc-system.md`
- RFC must be accepted before implementation begins

### 3.4 Stage 3: Design

- Produce a design document for non-trivial changes
- Design must be reviewed before implementation
- Design must include:
  - API surface (public interfaces)
  - Data structures
  - Algorithm choices
  - Testing strategy
  - Performance considerations
  - Security considerations

### 3.5 Stage 4: Implementation

- Implement against the approved design
- All code must have tests
- All code must pass linting before commit
- Commit messages follow conventional commits format

### 3.6 Stage 5: Review

- Every PR requires at least one approved review
- No self-merging (author cannot merge own PR)
- Review must verify:
  - Correctness
  - Test coverage
  - Documentation
  - Security
  - Performance
  - Style consistency

### 3.7 Stage 6: Merge

- Merges to `main` only after CI passes
- Use squash-merge for feature branches
- Use merge-commit for release branches

### 3.8 Stage 7: Release

- Follow the Release Process
- Release notes must be generated
- Breaking changes documented

---

## 4. Branching Strategy

### 4.1 Branch Model

```
main          ─── Production-ready code
  │
  ├── release/*  ─── Release candidates
  │
  └── feat/*     ─── Feature branches (branch from main, merge to main)
  └── fix/*      ─── Bug fixes (branch from main, merge to main)
  └── docs/*     ─── Documentation-only changes
  └── perf/*     ─── Performance improvements
  └── chore/*    ─── Maintenance tasks
```

### 4.2 Branch Naming

- `feat/<brief-description>` — New features
- `fix/<issue-id>-<brief-description>` — Bug fixes
- `docs/<brief-description>` — Documentation
- `perf/<brief-description>` — Performance
- `chore/<brief-description>` — Maintenance
- `release/<version>` — Release preparation

### 4.3 Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `perf`, `chore`, `refactor`, `test`
Scopes: `lexer`, `parser`, `semantic`, `codegen`, `vm`, `native`, `core`, `stdlib`, `cli`, `docs`, `build`

### 4.4 Protected Branches

The following branches are protected and require PR review:
- `main` — requires 1 approval, passing CI
- `release/*` — requires 2 approvals, passing CI

---

## 5. Code Review Standards

### 5.1 Review Requirements

| Change Type | Reviewers | Minimum Approvals |
|-------------|-----------|-------------------|
| Bug fix | 1 | 1 |
| Minor feature | 1 | 1 |
| Major feature | 2 | 1 |
| Breaking change | 3 | 2 |
| Compiler core | 2 | 2 |
| Security-sensitive | 3 | 2 |

### 5.2 Review Checklist

Every review must verify:

- [ ] Code is correct and handles edge cases
- [ ] Tests cover happy path, error cases, and edge cases
- [ ] No dead code, unused imports, or TODO comments
- [ ] Public APIs are documented
- [ ] No security vulnerabilities introduced
- [ ] Performance impact is acceptable
- [ ] Follows existing code style
- [ ] No regressions introduced

### 5.3 Review Etiquette

- Be constructive and specific
- Distinguish between blocking and non-blocking comments
- Explain the "why" behind suggestions
- Approve only when all blocking comments are resolved

---

## 6. Testing Standards

### 6.1 Test Types

| Type | Purpose | Required | Location |
|------|---------|----------|----------|
| Unit tests | Test single components | Always | `tests/unit/` |
| Integration tests | Test component interaction | Always | `tests/integration/` |
| Golden tests | Compiler output snapshots | For compiler changes | `tests/golden/` |
| Fuzz tests | Malformed input handling | For parsers/lexers | `tests/fuzzing/` |
| Benchmark tests | Performance regression | For perf-sensitive changes | `tests/benchmarks/` |
| Stress tests | Long-running stability | For VM/runtime | `tests/stress/` |

### 6.2 Coverage Requirements

- Unit tests must cover ≥ 90% of new code
- Integration tests must cover all public APIs
- No regressions allowed in existing tests
- Edge cases must be explicitly tested

### 6.3 Test Naming Convention

```
test_<module>_<function>_<scenario>
```

### 6.4 Running Tests

```
# All tests
ilang test

# Specific category
ilang test --unit
ilang test --integration
ilang test --golden

# With coverage
ilang test --coverage
```

---

## 7. CI/CD Pipeline

### 7.1 Pipeline Stages

```
1. Lint        ─── Ruff check + Ruff format check
2. Type Check  ─── mypy / pyright
3. Unit Tests  ─── pytest (unit)
4. Integration ─── pytest (integration)
5. Benchmarks  ─── pytest-benchmark
6. Security    ─── Bandit / safety
```

### 7.2 Required Checks

Every PR must pass:
- All lint checks (0 violations)
- All unit tests
- All integration tests
- No regression in benchmark performance

### 7.3 CI Infrastructure

- GitHub Actions for CI/CD
- Windows, macOS, Linux runners
- Python 3.14+ runtime

---

## 8. Issue & Sprint Management

### 8.1 Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Defect in existing functionality |
| `feature` | New capability |
| `enhancement` | Improvement to existing feature |
| `tech-debt` | Technical debt |
| `security` | Security vulnerability |
| `documentation` | Documentation gap |
| `RFC` | Requires RFC process |
| `blocker` | Blocks release |
| `good-first-issue` | Suitable for new contributors |

### 8.2 Sprint Cadence

- Sprint duration: 2 weeks
- Sprint planning: First day of sprint
- Sprint review: Last day of sprint
- Sprint retrospective: Last day of sprint

### 8.3 Sprint Backlog

- Sprint backlog is selected from the top of the product backlog
- Capacity is based on historical velocity
- Unfinished work returns to the product backlog
- No mid-sprint additions without team approval

---

## 9. Documentation Requirements

### 9.1 Mandatory Documentation

Every feature must include:

1. **Architecture** — How the feature works internally
2. **Tutorial** — Getting started guide
3. **Reference** — Complete API documentation
4. **Examples** — Runnable code examples
5. **Migration Notes** — How to migrate from previous versions (if applicable)

### 9.2 Documentation Location

| Type | Location |
|------|----------|
| Architecture | `docs/architecture/` |
| Tutorial | `docs/guides/` |
| Reference | `docs/reference/` |
| Examples | `examples/` |
| API Docs | Generated from source |

### 9.3 Documentation Review

- Documentation is reviewed as part of the PR
- Incomplete documentation blocks merge
- Documentation must be kept in sync with code

---

## 10. Quality Gates

### 10.1 Pre-Merge Gates

- [ ] Code compiles without errors
- [ ] Linting passes (0 violations)
- [ ] All tests pass
- [ ] Code review approved
- [ ] Documentation is complete
- [ ] Public APIs are documented

### 10.2 Pre-Release Gates

- [ ] Full test suite passes on all platforms
- [ ] Security audit completed
- [ ] Performance benchmarks pass
- [ ] Fuzz testing completed
- [ ] Documentation audit completed
- [ ] API compatibility verified

### 10.3 Enforcement

- CI enforces pre-merge gates
- Release manager enforces pre-release gates
- No exceptions without engineering council approval

---

## 11. Release Process

### 11.1 Release Types

| Type | Frequency | Approval |
|------|-----------|----------|
| Patch | As needed | Engineering lead |
| Minor | Quarterly | Engineering council |
| Major | Annual | TSC + engineering council |

### 11.2 Release Steps

1. Create `release/<version>` branch from `main`
2. Run full test suite and quality gates
3. Generate release notes
4. Tag release candidate: `v<version>-rc.<n>`
5. Testing period (2 weeks for major/minor)
6. Tag final release: `v<version>`
7. Merge release branch to `main`

---

## 12. Incident Response

### 12.1 Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| SEV1 | Complete system failure | 1 hour |
| SEV2 | Major functionality broken | 4 hours |
| SEV3 | Minor functionality broken | 24 hours |
| SEV4 | Cosmetic issue | Next sprint |

### 12.2 Incident Process

1. **Detect** — Automated monitoring or user report
2. **Triage** — Assign severity and owner
3. **Fix** — Develop and test fix
4. **Review** — Emergency review process
5. **Deploy** — Emergency release if needed
6. **Post-mortem** — Document root cause and prevent recurrence

---

## 13. References

| Document | Location |
|----------|----------|
| Production Implementation Constitution | `docs/governance/PRODUCTION_IMPLEMENTATION_CONSTITUTION.md` |
| Language Specification | `docs/specification/LANGUAGE_SPECIFICATION.md` |
| IPMP (I Programming Maturity Process) | `docs/IPMP.md` |
| RFC System | `docs/evolution/rfc-system.md` |
| VERSIONING | `docs/versioning/VERSIONING.md` |
| Release Process | `docs/release/RELEASE_PROCESS.md` |
| Self-Hosting Roadmap | `docs/evolution/self-hosting-roadmap.md` |
| Compiler Architecture | `docs/architecture/compiler-architecture.md` |
| Native Compiler Roadmap | `docs/architecture/native-compiler-roadmap.md` |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | July 2026 | I Programming Language Engineering Council | Initial official release |

---

## Copyright and Licence

Copyright © 2026 Irabizi Paisible Valentin. All rights reserved.

The I Programming Language is released under the terms specified in the project licence.

---

**I Programming Language** — *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
