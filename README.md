# I Programming Language

<div align="center">

**The world's first professional programming language designed around Kinyarwanda**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/github/actions/workflow/status/i-lang/i-lang/ci.yml?branch=main)](https://github.com/i-lang/i-lang/actions)
[![codecov](https://codecov.io/gh/i-lang/i-lang/branch/main/graph/badge.svg)](https://codecov.io/gh/i-lang/i-lang)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://docs.i-lang.rw)
[![Gitter](https://badges.gitter.im/i-lang/community.svg)](https://gitter.im/i-lang/community)

[Website](https://i-lang.rw) • [Documentation](https://docs.i-lang.rw) • [Examples](https://github.com/i-lang/examples) • [Community](https://community.i-lang.rw)

</div>

## Table of Contents

- [Mission](#mission)
- [Vision](#vision)
- [Quick Start](#quick-start)
- [Language Overview](#language-overview)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Governance](#governance)
- [Security](#security)
- [License](#license)

## Mission

Create a professional programming language with natural Kinyarwanda syntax that empowers millions of African developers to build world-class software in their native language, serving as a foundation for African technological independence.

## Vision

A language that:
- **Feels like natural Kinyarwanda** while remaining suitable for professional development
- **Serves as a foundation** for African technological independence
- **Enables developers** to express complex ideas with clarity and precision
- **Stands the test of time** for the next 30 years and beyond
- **Supports self-hosting** by eventually being written in I itself

## Quick Start

### Installation

```bash
# Install the I compiler
pip install i-lang

# Or build from source
git clone https://github.com/i-lang/i-lang.git
cd i-lang
python -m pip install -e .
```

### Your First Program

Create a file `hello.i`:

```i
# Hello World in I
andika "Muraho, Isi!"
```

Run it:

```bash
i hello.i -r
```

### Learning Resources

- [Tutorial](https://docs.i-lang.rw/tutorial)
- [Language Specification](https://docs.i-lang.rw/spec)
- [Standard Library](https://docs.i-lang.rw/stdlib)
- [Examples](https://github.com/i-lang/examples)

## Language Overview

### Design Principles

1. **Readable** - Code should read like natural language
2. **Natural** - Syntax should feel intuitive to Kinyarwanda speakers
3. **Simple** - Minimal complexity, maximum clarity
4. **Consistent** - Uniform patterns throughout the language
5. **Powerful** - Capable of building any software system
6. **Fast** - High-performance execution
7. **Safe** - Memory safety and type safety by default
8. **Modern** - Contemporary features and best practices
9. **Professional** - Suitable for enterprise-grade applications
10. **Self Hosting** - Eventually written in I itself

### Natural Syntax

Instead of punctuation, I uses Kinyarwanda words:

```i
# Comparison operators
a irenze 5        # a > 5
a munsi ya 5      # a < 5
a kandi b         # a && b
a cyangwa b       # a || b
si a              # !a
```

### Block Structure

Every block ends with `iherezo` (end):

```i
niba a irenze 5
    andika a
iherezo
```

### Example: Fibonacci

```i
umurimo fibonacci(n: int) -> int
    niba n munsi_ya 2
        subira n
    iherezo
    subira fibonacci(n - 1) + fibonacci(n - 2)
iherezo

buri i muri 0 kugeza 10
    andika fibonacci(i)
iherezo
```

## Project Structure

The repository is organized for million-line scale with clear separation of concerns:

```
i-lang/
├── bootstrap-compiler/          # Initial Python bootstrap compiler
├── self-hosting-compiler/       # Self-hosted I compiler (future)
├── compiler-core/               # Core compiler infrastructure
│   ├── lexer/                   # Lexical analysis
│   ├── parser/                  # Parsing and AST construction
│   ├── ast/                     # Abstract Syntax Tree definitions
│   ├── semantic/                # Semantic analysis
│   ├── optimizer/               # Code optimization
│   ├── codegen/                 # Bytecode generation
│   └── native/                  # Native code generation
├── compiler-frontends/          # Multiple compiler frontends
│   ├── cli/                     # Command-line interface
│   ├── lsp/                     # Language Server Protocol
│   └── repl/                    # Read-Eval-Print Loop
├── compiler-backends/          # Multiple compiler backends
│   ├── bytecode/                # Bytecode backend
│   ├── llvm/                    # LLVM backend (future)
│   ├── wasm/                    # WebAssembly backend (future)
│   └── native/                  # Native code backend (future)
├── runtime-core/               # Core runtime infrastructure
├── runtime-libraries/          # Runtime libraries
├── vm-core/                     # Core virtual machine
├── vm-optimizations/           # VM optimizations
├── stdlib-core/                 # Core standard library
├── stdlib-platform/             # Platform-specific stdlib
├── frameworks-core/             # Core framework infrastructure
├── frameworks-web/              # urubuga - Web framework
├── frameworks-desktop/          # ibiro - Desktop framework
├── frameworks-mobile/           # mobile - Mobile framework
├── frameworks-data/             # ububiko - Database framework
├── frameworks-ai/               # ubwenge - AI framework
├── frameworks-games/            # imikino - Game engine
├── frameworks-systems/          # sisitemu - Systems framework
├── frameworks-cloud/            # igicu - Cloud framework
├── frameworks-robotics/         # robot - Robotics framework
├── frameworks-networking/       # amakuru - Networking framework
├── tools-core/                  # Core tool infrastructure
├── tools-package-manager/      # isoko - Package manager
├── tools-formatter/             # iformat - Code formatter
├── tools-debugger/              # idebug - Debugger
├── tools-linter/                # Linter
├── tools-testing/               # itest - Testing framework
├── tools-documentation/         # idoc - Documentation generator
├── tools-benchmarking/          # Benchmarking tools
├── ide-core/                    # I Studio core
├── ide-editor/                  # Editor component
├── ide-debugger/                # Debugger component
├── ide-intellisense/            # IntelliSense component
├── ide-project-management/      # Project management
├── ide-build-system/            # Build system integration
├── ide-version-control/        # Version control integration
├── ide-terminal/               # Terminal component
├── ide-themes/                  # Theme system
├── ide-plugins/                 # Plugin system
├── docs-specification/          # Language specification docs
├── docs-tutorials/              # Tutorial documentation
├── docs-api/                    # API documentation
├── docs-internals/              # Internal documentation
├── docs-guides/                 # Developer guides
├── docs-faq/                    # FAQ documentation
├── docs-glossary/               # Glossary
├── tests-unit/                  # Unit tests
├── tests-integration/           # Integration tests
├── tests-regression/            # Regression tests
├── tests-performance/           # Performance tests
├── tests-fuzzing/               # Fuzzing tests
├── tests-property/              # Property-based tests
├── examples-tutorials/          # Tutorial examples
├── examples-benchmarks/         # Benchmark examples
├── examples-real-world/         # Real-world examples
├── examples-migration/          # Migration examples
├── benchmarks-compiler/         # Compiler benchmarks
├── benchmarks-runtime/          # Runtime benchmarks
├── benchmarks-stdlib/           # Stdlib benchmarks
├── benchmarks-frameworks/       # Framework benchmarks
├── scripts-build/               # Build scripts
├── scripts-test/                # Test scripts
├── scripts-deploy/              # Deployment scripts
├── scripts-maintenance/         # Maintenance scripts
├── scripts-development/         # Development scripts
├── scripts-release/             # Release scripts
├── .github/workflows/          # GitHub Actions workflows
├── .github/issue-templates/    # Issue templates
├── .github/pr-templates/       # Pull request templates
├── infrastructure-ci/           # CI infrastructure
├── infrastructure-cd/           # CD infrastructure
├── infrastructure-monitoring/  # Monitoring infrastructure
├── infrastructure-security/     # Security infrastructure
├── governance-committees/       # Governance committee docs
├── governance-processes/        # Governance process docs
└── governance-policies/         # Governance policy docs
```

## Architecture

The I programming language follows a clean architecture designed for extensibility and maintainability:

### Compiler Pipeline

```
Source Code → Lexer → Parser → AST → Semantic Analyzer → Optimizer → Code Generator → Bytecode
```

### Multi-Backend Support

The compiler is designed to support multiple backends:
- **Bytecode VM** - Stack-based virtual machine (current)
- **LLVM** - Native code generation (planned)
- **WebAssembly** - Web deployment (planned)
- **Native** - Platform-specific optimization (planned)

### Self-Hosting Strategy

The project follows a bootstrap strategy:
1. **Phase 1**: Python bootstrap compiler (current)
2. **Phase 2**: Incremental self-hosting
3. **Phase 3**: Full self-hosting
4. **Phase 4**: Self-hosting optimization

For details, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Roadmap

### Phase 1: Foundation (Current)
- [x] Repository structure
- [x] Documentation foundation
- [ ] Language specification
- [ ] Lexer implementation
- [ ] Parser implementation
- [ ] AST construction
- [ ] Semantic analysis
- [ ] Bytecode generation
- [ ] Basic VM

### Phase 2: Core Language
- [ ] Complete type system
- [ ] Standard library foundation
- [ ] Error handling
- [ ] Module system
- [ ] Package system

### Phase 3: Ecosystem
- [ ] Package manager (isoko)
- [ ] Testing framework (itest)
- [ ] Documentation generator (idoc)
- [ ] Formatter (iformat)
- [ ] Linter

### Phase 4: Tools
- [ ] Debugger (idebug)
- [ ] Language Server Protocol
- [ ] REPL
- [ ] Build system

### Phase 5: IDE
- [ ] I Studio development
- [ ] Editor integration
- [ ] Debugger integration
- [ ] IntelliSense

### Phase 6: Frameworks
- [ ] urubuga (web framework)
- [ ] ibiro (desktop framework)
- [ ] mobile (mobile framework)
- [ ] Specialized frameworks

### Phase 7: Self-Hosting
- [ ] Incremental self-hosting
- [ ] Full compiler in I
- [ ] Self-hosting optimization

For detailed roadmap, see [ROADMAP.md](ROADMAP.md).

## Contributing

We welcome contributions from developers worldwide. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## Governance

The I programming language is governed by a community-driven process. For details on governance, committees, and decision-making, see [GOVERNANCE.md](GOVERNANCE.md).

## Security

Security is a top priority. For security policies and reporting procedures, see [SECURITY.md](SECURITY.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Inspired by the great programming languages that came before: Python, Rust, Go, Swift, Kotlin, TypeScript, Zig.

Designed with a singular vision: to make programming accessible to millions of African developers in their native language.

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)

Founder: **Irabizi Paisible Valentin** | Location: **Rwanda**
