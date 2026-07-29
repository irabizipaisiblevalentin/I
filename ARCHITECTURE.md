# Architecture

This document describes the architecture of the I Programming Language compiler and runtime system.

## Table of Contents

- [Architecture Philosophy](#architecture-philosophy)
- [High-Level Architecture](#high-level-architecture)
- [Compiler Pipeline](#compiler-pipeline)
- [Component Architecture](#component-architecture)
- [Multi-Backend Support](#multi-backend-support)
- [Self-Hosting Strategy](#self-hosting-strategy)
- [Performance Considerations](#performance-considerations)
- [Security Architecture](#security-architecture)
- [Extensibility](#extensibility)

## Architecture Philosophy

The I Programming Language architecture is guided by:

- **Clean Architecture**: Clear separation of concerns
- **Modularity**: Independent, interchangeable components
- **Extensibility**: Easy to add new features and backends
- **Performance**: Optimized for speed and memory
- **Maintainability**: Clear code structure and documentation
- **Testability**: Every component is testable
- **Portability**: Runs on multiple platforms

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Code                            │
│                      (.i source files)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Compiler Frontends                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   CLI    │  │   LSP    │  │   REPL   │  │   IDE    │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Compiler Core                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Lexer   │  │  Parser  │  │   AST    │  │ Semantic │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ Optimizer│  │ Code Gen │  │  IR      │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Compiler Backends                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Bytecode  │  │   LLVM   │  │   WASM   │  │  Native  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Runtime System                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │    VM    │  │   GC     │  │  Memory  │  │  Thread  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Standard Library                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   Core   │  │    I/O   │  │  Math    │  │  String  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Compiler Pipeline

### Phase 1: Lexical Analysis

**Component**: `compiler-core/lexer/`

**Purpose**: Convert source code into tokens

**Input**: I source code (text)
**Output**: Token stream

**Key Functions**:
- Token recognition
- Keyword identification
- Operator parsing
- Literal parsing
- Comment handling
- Error reporting

**Design Considerations**:
- Unicode support for Kinyarwanda
- Efficient token streaming
- Clear error messages
- Position tracking for error reporting

### Phase 2: Parsing

**Component**: `compiler-core/parser/`

**Purpose**: Build Abstract Syntax Tree from tokens

**Input**: Token stream
**Output**: AST

**Key Functions**:
- Grammar parsing
- AST construction
- Syntax validation
- Error recovery
- Operator precedence handling

**Design Considerations**:
- Recursive descent parsing
- Clear error messages
- Good error recovery
- Extensible grammar

### Phase 3: Semantic Analysis

**Component**: `compiler-core/semantic/`

**Purpose**: Validate semantics and build symbol table

**Input**: AST
**Output**: Validated AST with type information

**Key Functions**:
- Type checking
- Name resolution
- Scope management
- Type inference
- Semantic validation

**Design Considerations**:
- Strong static typing
- Clear type errors
- Efficient type checking
- Support for generics

### Phase 4: Optimization

**Component**: `compiler-core/optimizer/`

**Purpose**: Optimize the AST for better performance

**Input**: Validated AST
**Output**: Optimized AST

**Key Functions**:
- Constant folding
- Dead code elimination
- Loop optimization
- Function inlining
- Memory optimization

**Design Considerations**:
- Multiple optimization passes
- Measurable performance improvements
- Preserve semantics
- Configurable optimization levels

### Phase 5: Code Generation

**Component**: `compiler-core/codegen/`

**Purpose**: Generate intermediate representation

**Input**: Optimized AST
**Output**: Intermediate Representation (IR)

**Key Functions**:
- IR generation
- Register allocation
- Instruction selection
- Basic block formation
- Control flow graph construction

**Design Considerations**:
- Clear IR format
- Optimizable IR
- Backend-independent
- Well-documented IR

### Phase 6: Backend Compilation

**Component**: `compiler-backends/`

**Purpose**: Convert IR to target format

**Input**: IR
**Output**: Target code (bytecode, native, WASM, etc.)

**Key Functions**:
- Backend-specific optimization
- Target code generation
- Linking
- Binary generation

**Design Considerations**:
- Multiple backend support
- Backend-specific optimizations
- Clear backend interface
- Easy to add new backends

## Component Architecture

### Lexer Architecture

```
Lexer
├── Token definitions
├── Character stream
├── Token recognition
├── Keyword table
└── Error handling
```

**Key Classes**:
- `Lexer`: Main lexer class
- `Token`: Token representation
- `TokenType`: Token type enumeration
- `LexerError`: Lexer error handling

### Parser Architecture

```
Parser
├── Grammar rules
├── AST node definitions
├── Parsing functions
├── Error recovery
└── AST construction
```

**Key Classes**:
- `Parser`: Main parser class
- `ASTNode`: Base AST node class
- `Expr`: Expression node base class
- `Stmt`: Statement node base class
- `ParseError`: Parser error handling

### Semantic Analyzer Architecture

```
SemanticAnalyzer
├── Type system
├── Symbol table
├── Scope management
├── Type checking
└── Type inference
```

**Key Classes**:
- `SemanticAnalyzer`: Main analyzer class
- `Type`: Type system base class
- `Symbol`: Symbol representation
- `Scope`: Scope management
- `SemanticError`: Semantic error handling

### Virtual Machine Architecture

```
VirtualMachine
├── Stack
├── Instruction pointer
├── Constant pool
├── Call stack
├── Garbage collector
└── Native functions
```

**Key Classes**:
- `VirtualMachine`: Main VM class
- `Frame`: Execution frame
- `Value`: Value representation
- `GC`: Garbage collector
- `RuntimeError`: Runtime error handling

## Multi-Backend Support

### Backend Interface

All backends implement a common interface:

```python
class Backend:
    def compile(self, ir: IR) -> CompiledCode:
        """Compile IR to target code"""
        pass
    
    def optimize(self, code: CompiledCode) -> CompiledCode:
        """Optimize target code"""
        pass
    
    def link(self, code: CompiledCode) -> Executable:
        """Link to executable"""
        pass
```

### Bytecode Backend

**Status**: Current implementation
**Target**: Stack-based virtual machine
**Advantages**:
- Simple implementation
- Fast compilation
- Portable
- Easy to debug

**Disadvantages**:
- Slower execution
- Limited optimization

### LLVM Backend

**Status**: Planned
**Target**: LLVM IR
**Advantages**:
- Excellent optimization
- Native performance
- Multiple target platforms
- Industry-standard

**Disadvantages**:
- Complex implementation
- Larger binary size
- Slower compilation

### WebAssembly Backend

**Status**: Planned
**Target**: WebAssembly
**Advantages**:
- Web deployment
- Near-native performance
- Small binary size
- Browser support

**Disadvantages**:
- Limited platform support
- Limited runtime features

### Native Backend

**Status**: Planned
**Target**: Platform-specific machine code
**Advantages**:
- Maximum performance
- Platform-specific optimization
- Small binary size

**Disadvantages**:
- Platform-specific
- Complex implementation
- Maintenance burden

## Self-Hosting Strategy

### Bootstrap Strategy

The project follows a phased self-hosting approach:

#### Phase 1: Python Bootstrap (Current)
- Compiler written in Python
- VM written in Python
- Foundation for self-hosting

#### Phase 2: Incremental Self-Hosting
- Rewrite lexer in I
- Rewrite parser in I
- Rewrite semantic analyzer in I
- Rewrite code generator in I
- Rewrite VM in I

#### Phase 3: Full Self-Hosting
- Complete compiler in I
- Complete toolchain in I
- Drop Python dependency

#### Phase 4: Self-Hosting Optimization
- Optimize self-hosted compiler
- Improve performance
- Reduce memory usage

### Self-Hosting Architecture

```
Bootstrap Compiler (Python)
        │
        ▼
Self-Hosted Compiler (I)
        │
        ▼
Optimized Self-Hosted Compiler (I)
```

### Challenges

- **Bootstrapping**: Need working compiler to compile compiler
- **Performance**: Self-hosted compiler must be performant
- **Features**: Must support all features needed for compilation
- **Testing**: Comprehensive testing required

### Solutions

- **Incremental Approach**: Rewrite components incrementally
- **Performance Profiling**: Profile and optimize continuously
- **Feature Parity**: Ensure feature parity with bootstrap
- **Testing**: Extensive testing at each stage

## Performance Considerations

### Compilation Performance

**Goals**:
- Fast compilation for development
- Optimized compilation for production
- Incremental compilation support
- Parallel compilation where possible

**Strategies**:
- Efficient data structures
- Lazy evaluation where appropriate
- Caching of intermediate results
- Parallel processing of independent units

### Runtime Performance

**Goals**:
- Fast execution
- Low memory usage
- Efficient garbage collection
- Good cache locality

**Strategies**:
- JIT compilation
- Escape analysis
- Inline caching
- Efficient data structures
- Memory pooling

### Memory Usage

**Goals**:
- Low memory footprint
- Efficient memory allocation
- Minimal memory fragmentation
- Predictable memory usage

**Strategies**:
- Memory pooling
- Efficient data structures
- Garbage collection tuning
- Memory profiling

## Security Architecture

### Compiler Security

**Features**:
- Input validation
- Safe defaults
- Sandboxing support
- Secure standard library

**Considerations**:
- Trust boundaries
- Supply chain security
- Dependency security
- Code signing

### Runtime Security

**Features**:
- Memory safety
- Type safety
- Bounds checking
- Resource limits

**Considerations**:
- Privilege separation
- Secure defaults
- Audit logging
- Vulnerability response

## Extensibility

### Plugin Architecture

The compiler supports plugins for:

- Custom lexers
- Custom parsers
- Custom analyzers
- Custom optimizers
- Custom backends
- Custom tools

### Extension Points

- Lexer extensions
- Grammar extensions
- Type system extensions
- Standard library extensions
- Backend extensions

### API Design

All extension points:
- Well-documented
- Versioned
- Stable
- Tested
- Backward compatible

## Documentation Architecture

### Internal Documentation

- Architecture documentation
- API documentation
- Algorithm documentation
- Design documentation
- Implementation notes

### External Documentation

- Language specification
- User documentation
- Tutorial documentation
- Example documentation
- API documentation

### Documentation Generation

- Automated documentation generation
- Consistent formatting
- Cross-referencing
- Search functionality
- Multiple formats

## Testing Architecture

### Test Organization

```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── regression/        # Regression tests
├── performance/       # Performance tests
├── fuzzing/          # Fuzzing tests
└── property/         # Property-based tests
```

### Test Strategy

- Unit tests for individual components
- Integration tests for component interactions
- Regression tests for known bugs
- Performance tests for performance validation
- Fuzzing tests for robustness
- Property-based tests for correctness

### Test Infrastructure

- Test framework
- Test runners
- Coverage tools
- Benchmarking tools
- Fuzzing tools

## Deployment Architecture

### Distribution

- Source distribution
- Binary distribution
- Package manager distribution
- Platform-specific packages

### Installation

- Pip installation
- Package manager installation
- Binary installation
- Source installation

### Updates

- Automatic updates
- Security updates
- Feature updates
- Migration guides

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
