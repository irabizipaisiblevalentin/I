# Compiler Architecture

This document describes the complete architecture of the I Programming Language compiler, from source code to executable. It serves as the master reference for all compiler-related work.

## Table of Contents

- [Design Philosophy](#design-philosophy)
- [Pipeline Overview](#pipeline-overview)
- [Stage 1: Lexer](#stage-1-lexer)
- [Stage 2: Parser](#stage-2-parser)
- [Stage 3: AST Construction](#stage-3-ast-construction)
- [Stage 4: Semantic Analyzer](#stage-4-semantic-analyzer)
- [Stage 5: Type Checker](#stage-5-type-checker)
- [Stage 6: IR Generator](#stage-6-ir-generator)
- [Stage 7: Optimizer](#stage-7-optimizer)
- [Stage 8: Bytecode Generator](#stage-8-bytecode-generator)
- [Stage 9: Virtual Machine](#stage-9-virtual-machine)
- [Stage 10: Native Compiler](#stage-10-native-compiler-future)
- [Error Flow Architecture](#error-flow-architecture)
- [Data Flow Between Stages](#data-flow-between-stages)
- [Compilation Modes](#compilation-modes)
- [Self-Hosting Strategy](#self-hosting-strategy)
- [Security Architecture](#security-architecture)

## Design Philosophy

The I compiler is designed with the following principles:

1. **Clean Separation of Concerns**: Each stage has exactly one responsibility
2. **Fail-Fast with Maximum Recovery**: Report errors immediately but continue when possible
3. **30-Year Horizon**: Architecture must accommodate features not yet designed
4. **Bilingual by Default**: All errors, diagnostics, and documentation in English and Kinyarwanda
5. **Progressive Enhancement**: Working compiler first, optimizations second, native compilation third

## Pipeline Overview

```
 Source Code (.i)
       │
       ▼
 ┌─────────────┐
 │    Lexer     │  Source text → Token stream
 └──────┬──────┘
        │  Token[]
        ▼
 ┌─────────────┐
 │    Parser    │  Token stream → AST
 └──────┬──────┘
        │  Program (AST root)
        ▼
 ┌─────────────┐
 │   Semantic   │  AST → Annotated AST (scopes, symbols)
 │   Analyzer   │
 └──────┬──────┘
        │  Annotated AST
        ▼
 ┌─────────────┐
 │   Type       │  Annotated AST → Typed AST
 │   Checker    │
 └──────┬──────┘
        │  Typed AST
        ▼
 ┌─────────────┐
 │  IR          │  Typed AST → IR (SSA form)
 │  Generator   │
 └──────┬──────┘
        │  IR
        ▼
 ┌─────────────┐
 │  Optimizer   │  IR → Optimized IR
 └──────┬──────┘
        │  Optimized IR
        ▼
 ┌─────────────┐
 │  Bytecode    │  IR → Bytecode
 │  Generator   │
 └──────┬──────┘
        │  Bytecode + Constant Pool + Debug Info
        ▼
 ┌─────────────┐
 │  Virtual     │  Bytecode → Execution
 │  Machine     │
 └─────────────┘
        │
        ▼
  Program Output
```

### Stage Input/Output Summary

| Stage | Input | Output | Error Code Range |
|-------|-------|--------|------------------|
| Lexer | UTF-8 source text | `Token[]` | LEX001–LEX099 |
| Parser | `Token[]` | `Program` (AST) | PARS001–PARS099 |
| Semantic Analyzer | `Program` | `AnnotatedProgram` | SEM001–SEM099 |
| Type Checker | `AnnotatedProgram` | `TypedProgram` | TYP001–TYP099 |
| IR Generator | `TypedProgram` | `IRModule` | IR001–IR099 |
| Optimizer | `IRModule` | `OptimizedIRModule` | OPT001–OPT099 |
| Bytecode Generator | `OptimizedIRModule` | `BytecodeModule` | BC001–BC099 |
| Virtual Machine | `BytecodeModule` | Program output | RUN001–RUN099 |

## Stage 1: Lexer

### Responsibility

Convert raw UTF-8 source code text into a structured stream of tokens.

### Detailed Behavior

The lexer performs the following operations in sequence:

1. **Encoding Validation**: Verify the source file is valid UTF-8. Handle optional BOM (byte order mark).
2. **Character Streaming**: Read characters one at a time from the source buffer. The lexer operates on a pre-decoded Unicode codepoint stream.
3. **Token Recognition**: Using a deterministic finite automaton (DFA), recognize the longest matching token at each position.
4. **Keyword Resolution**: After recognizing an identifier, check it against the keyword table. If it matches, emit a keyword token instead of an identifier token.
5. **Literal Parsing**: Parse integer, float, string, and character literals into their runtime values during tokenization.
6. **Comment Handling**: Skip single-line comments (`# ...`) and multi-line comments (`#= ... =#`). Optionally preserve documentation comments for IDE tooling.
7. **Source Location Tracking**: Maintain a running count of line number, column number, and byte offset.
8. **Error Recovery**: On encountering an invalid character, emit an error diagnostic and skip the character. On encountering an unterminated string, emit an error and synthesize a closing quote.

### Input Specification

```
Input:
  - source: UTF-8 encoded byte array
  - file_path: string (for error reporting)
  - config: LexerConfig
    - strict_mode: bool (default: true)
    - preserve_comments: bool (default: false)

Output:
  - tokens: List[Token]
  - errors: List[CompilerError]
  - warnings: List[CompilerWarning]
```

### Token Structure

Each token carries:

```
Token {
    type: TokenType          // Category of token
    lexeme: string           // Original text from source
    value: any               // Parsed value (int, float, string, bool, null) or null
    line: int                // 1-indexed line number
    column: int              // 1-indexed column number
    offset: int              // Byte offset from start of file
    span: int                // Length in bytes
}
```

### Error Flow

Lexer errors are collected into an error buffer, not thrown immediately. The lexer continues tokenizing after each error up to a configurable limit (default: 100 errors, or 10 consecutive errors without progress). This enables the user to see multiple problems in one compile run.

### Why This Stage Exists

The lexer is the first line of defense against malformed input. It converts unstructured text into structured tokens, which simplifies the parser's job enormously. By tracking source locations at this stage, every subsequent stage can provide precise error locations. The lexer also handles the complexity of Unicode, which is critical for a language that uses Kinyarwanda identifiers.

---

## Stage 2: Parser

### Responsibility

Transform the token stream into an Abstract Syntax Tree (AST), validating that the token sequence conforms to the I language grammar.

### Detailed Behavior

1. **Grammar Validation**: Using a recursive descent parser with Pratt parsing for expressions, validate that the token stream matches the language grammar.
2. **AST Construction**: Build a tree of AST nodes representing the program structure.
3. **Precedence Handling**: Use a precedence climbing algorithm (Pratt parser) to correctly associate binary and unary operators with their operands.
4. **Block Parsing**: Parse blocks delimited by `kora`/`iherezo` (or `{`/`}` in future syntax).
5. **Error Recovery**: On encountering a syntax error, emit the error and synchronize to the nearest statement boundary (statement-starting keyword, semicolon, or block delimiter) to continue parsing.
6. **Comment Attachment**: Attach documentation comments to the nearest following declaration.

### Input Specification

```
Input:
  - tokens: List[Token] (from Lexer)
  - config: ParserConfig
    - error_recovery: bool (default: true)
    - max_errors: int (default: 100)

Output:
  - ast: Program (root AST node)
  - errors: List[CompilerError]
  - warnings: List[CompilerWarning]
```

### Parsing Strategy

**Type**: Recursive descent with Pratt expression parsing.

**Lookahead**: 2 tokens (LL(2)).

**Why not a parser generator?** Recursive descent gives us:
- Full control over error messages (bilingual)
- Precise error recovery tailored to I's grammar
- No external toolchain dependency
- Easy to extend as the grammar evolves

### Error Flow

Parse errors include the token that was found, the tokens that were expected, and the source location. The parser continues parsing after each error by skipping tokens until a synchronization point is reached (typically a statement boundary).

### Why This Stage Exists

The parser enforces the syntactic rules of the language and creates a structured tree that separates the program's logical structure from its textual representation. This structured representation enables all subsequent analysis stages to operate on well-defined node types rather than raw tokens.

---

## Stage 3: AST Construction

### Responsibility

Define and build the complete hierarchical representation of the program. The AST serves as the universal data structure that all subsequent stages read from and annotate.

### Detailed Behavior

1. **Node Creation**: The parser calls factory methods to create AST nodes, ensuring each node has a unique ID and source location.
2. **Tree Assembly**: Parent nodes reference child nodes. The tree is a directed acyclic graph where each node (except the root) has exactly one parent.
3. **Source Mapping**: Every AST node records its source location (file, line, column, byte offset, span).
4. **Annotation Support**: AST nodes include a flexible annotation map (`Dict[str, Any]`) that subsequent stages use to attach metadata (types, symbols, analysis results).

### Why This Stage Exists

The AST is the contract between the parser and the rest of the compiler. By defining a precise, well-documented AST node hierarchy, we ensure that the parser, semantic analyzer, type checker, and code generator can all operate independently. The annotation map enables each stage to attach its own data without modifying the node definitions.

See `ast-design.md` for the complete AST node specification.

---

## Stage 4: Semantic Analyzer

### Responsibility

Validate the semantic correctness of the program and build the symbol table infrastructure that the type checker and code generator depend on.

### Detailed Behavior

1. **Scope Construction**: Walk the AST and build a hierarchy of scopes (global, module, function, block). Each scope contains bindings from names to symbol records.
2. **Name Resolution**: For every identifier reference, resolve it to its corresponding declaration. Report undefined variables.
3. **Symbol Table Building**: Create `Symbol` records for every declared name, including its type annotation (if present), mutability, visibility, and scope.
4. **Module Resolution**: For every `shyiramo` (import) statement, locate the module file and bring its exports into scope.
5. **Export Validation**: Verify that exported symbols exist and are visible.
6. **Control-Flow Validation**: Verify that `gukoma` (break) and `kugenda` (continue) appear only within loops. Verify that `subira` (return) is used correctly.
7. **Unused Variable Detection**: Mark variables that are declared but never read. Emit warnings (not errors).
8. **Duplicate Detection**: Report duplicate declarations within the same scope.
9. **Mutation Validation**: Ensure `shyira_ko` (const) variables are never reassigned.

### Input Specification

```
Input:
  - ast: Program (from Parser)
  - modules: ModuleRegistry (available modules)
  - config: SemanticConfig

Output:
  - annotated_ast: AnnotatedProgram
  - symbol_table: SymbolTable
  - errors: List[CompilerError]
  - warnings: List[CompilerWarning]
```

### Error Flow

Semantic errors are fatal for the affected scope but do not prevent analysis of the rest of the program. The analyzer continues walking the tree, using a "shadow" symbol for unresolved names to prevent cascading errors.

### Why This Stage Exists

Semantic analysis catches a class of errors that cannot be detected by grammar rules alone: using a variable before it's declared, calling a function with the wrong number of arguments, accessing a field that doesn't exist, etc. By separating this from type checking, we can report scope-related errors without needing the full type system to be operational.

---

## Stage 5: Type Checker

### Responsibility

Validate that the program is type-safe and infer types for unannotated expressions.

### Detailed Behavior

1. **Type Inference**: For expressions without explicit type annotations, infer the type using Hindley-Milner-style type inference with extensions for the I type system.
2. **Type Compatibility**: Verify that every operation receives operands of compatible types.
3. **Generic Instantiation**: Verify that generic type parameters satisfy their constraints.
4. **Union Type Resolution**: Verify that operations on union types are valid for all possible member types.
5. **Optional Type Handling**: Verify that optional values are checked for null before use.
6. **Function Signature Checking**: Verify argument types against parameter types at every call site.
7. **Return Type Checking**: Verify that every function returns a value of the declared return type.
8. **Type Annotation Validation**: Verify that explicit type annotations are consistent with inferred types.

### Input Specification

```
Input:
  - annotated_ast: AnnotatedProgram (from Semantic Analyzer)
  - type_env: TypeEnvironment
  - config: TypeCheckConfig

Output:
  - typed_ast: TypedProgram
  - errors: List[CompilerError]
  - warnings: List[CompilerWarning]
```

### Error Flow

Type errors are collected but do not stop analysis. The type checker uses a "error type" (⊥) for expressions with type errors, preventing cascading type errors. When an expression has type ⊥, all expressions that depend on it are also marked as ⊥ without generating additional errors.

### Why This Stage Exists

Type checking ensures runtime safety by catching type mismatches at compile time. By separating type checking from semantic analysis, we enable:
- Gradual typing in the future
- Better error messages (type errors are different from scope errors)
- Independent optimization of the type inference algorithm

---

## Stage 6: IR Generator

### Responsibility

Lower the typed AST into an Intermediate Representation (IR) that is simpler, more uniform, and easier to optimize.

### Detailed Behavior

1. **Lowering**: Convert high-level constructs (classes, pattern matching, for-each loops) into simpler primitives.
2. **Basic Block Formation**: Split control flow into basic blocks (straight-line sequences of instructions ending with a terminator).
3. **CFG Construction**: Build a control flow graph connecting basic blocks.
4. **SSA Conversion**: Convert the IR to Static Single Assignment form, where every variable is assigned exactly once.
5. **Type Annotation**: Preserve type information in the IR for downstream optimization and code generation.
6. **Metadata Attachment**: Attach source locations, variable names, and other debugging metadata to IR instructions.

### Input Specification

```
Input:
  - typed_ast: TypedProgram (from Type Checker)
  - target: CompilationTarget (bytecode, llvm, wasm)
  - config: IRConfig

Output:
  - ir_module: IRModule
  - errors: List[CompilerError]
```

### IR Design

The IR uses a three-address code format:

```
// Example: a + b * c
%1 = mul %b, %c       // %1 = b * c
%2 = add %a, %1       // %2 = a + %1
```

Each instruction has at most three operands: two inputs and one output (or zero outputs for terminators).

### Error Flow

IR generation errors are rare and typically indicate a compiler bug. They are reported as internal errors.

### Why This Stage Exists

The IR provides a common representation that all backends share. By lowering to IR before optimization, we can apply optimizations uniformly. SSA form makes data flow analysis straightforward and enables many classic optimizations.

---

## Stage 7: Optimizer

### Responsibility

Transform the IR to improve runtime performance and reduce code size, without changing program semantics.

### Detailed Behavior

The optimizer runs multiple passes over the IR:

1. **Constant Folding**: Evaluate constant expressions at compile time (`2 + 3` → `5`).
2. **Dead Code Elimination**: Remove instructions whose results are never used.
3. **Common Subexpression Elimination**: Avoid recomputing expressions that have already been computed.
4. **Function Inlining**: Replace small function calls with the function body.
5. **Loop Optimization**: Hoist loop-invariant code out of loops, perform strength reduction.
6. **Escape Analysis**: Determine which objects never escape their creating scope, enabling stack allocation.
7. **Tail Call Optimization**: Convert tail-recursive calls into loops.

### Input Specification

```
Input:
  - ir_module: IRModule (from IR Generator)
  - config: OptimizerConfig
    - optimization_level: int (0-3)
    - enabled_passes: List[str]

Output:
  - optimized_ir: IRModule
  - report: OptimizationReport
```

### Optimization Levels

| Level | Name | Description |
|-------|------|-------------|
| 0 | None | No optimizations. Fastest compilation. |
| 1 | Basic | Constant folding, dead code elimination. |
| 2 | Standard | + Common subexpression elimination, inlining. |
| 3 | Aggressive | + Loop optimization, escape analysis, tail calls. |

### Error Flow

The optimizer does not produce user-facing errors. If an optimization fails (e.g., due to an unexpected IR shape), it skips that optimization and continues. Internal assertions verify semantic preservation in debug builds.

### Why This Stage Exists

Optimization separates "what the program does" from "how it does it." By operating on IR rather than AST or bytecode, the optimizer can apply powerful transformations that would be difficult or impossible at higher levels.

---

## Stage 8: Bytecode Generator

### Responsibility

Convert the optimized IR into a compact bytecode format that the virtual machine can execute efficiently.

### Detailed Behavior

1. **Instruction Selection**: Map IR instructions to bytecode instructions. Some IR instructions map 1:1; others require multiple bytecode instructions.
2. **Register Allocation**: Assign virtual registers to temporaries and variables. Use a linear scan allocator for speed.
3. **Stack Frame Layout**: Determine the stack frame layout for each function (local variables, temporaries, saved registers).
4. **Constant Pool Construction**: Collect all constants (integers, floats, strings, identifiers) into a shared constant pool referenced by index.
5. **Exception Table Generation**: Record which instruction ranges are covered by which exception handlers.
6. **Debug Info Generation**: Record source-to-bytecode mappings for the debugger. Map each bytecode offset back to a source location.

### Input Specification

```
Input:
  - ir_module: IRModule (from Optimizer)
  - config: BytecodeConfig

Output:
  - bytecode_module: BytecodeModule
    - functions: List[BytecodeFunction]
    - constant_pool: ConstantPool
    - exception_table: ExceptionTable
    - debug_info: DebugInfo
  - errors: List[CompilerError]
```

### Error Flow

Bytecode generation errors indicate unsupported IR constructs or resource limits (too many locals, too many constants). These are reported as compiler internal errors.

### Why This Stage Exists

Bytecode is a compact, portable representation that is fast to generate and fast to execute. It decouples the compiler from the execution engine, enabling the VM to be implemented in any language.

---

## Stage 9: Virtual Machine

### Responsibility

Execute the compiled bytecode and manage the runtime environment.

### Detailed Behavior

1. **Instruction Dispatch**: Execute each bytecode instruction using a threaded dispatch loop.
2. **Stack Management**: Maintain an operand stack for expression evaluation and a call stack for function calls.
3. **Memory Allocation**: Allocate objects on the heap using the configured allocator.
4. **Garbage Collection**: Reclaim unreachable objects using a generational garbage collector.
5. **Exception Handling**: When an exception is thrown, unwind the call stack to the nearest matching handler.
6. **Module Loading**: On encountering a module import, load and execute the module's bytecode.
7. **I/O Operations**: Provide built-in functions for standard I/O, file system access, and networking.

### Input Specification

```
Input:
  - bytecode_module: BytecodeModule (from Bytecode Generator)
  - runtime: RuntimeEnvironment
    - stdlib: StandardLibrary
    - config: VMConfig
      - max_stack_depth: int
      - max_heap_size: int
      - gc_strategy: GCStrategy

Output:
  - exit_code: int
  - stdout: bytes
  - stderr: bytes
  - errors: List[RuntimeError]
```

### Error Flow

Runtime errors are reported with full stack traces, source locations (if debug info is available), and suggestions. The VM catches all runtime errors and reports them gracefully without crashing.

### Why This Stage Exists

The VM provides a safe, portable execution environment. It handles memory management, exception handling, and module loading, which would otherwise need to be reimplemented for every target platform.

---

## Stage 10: Native Compiler (Future)

### Responsibility

Compile I programs directly to native machine code, bypassing the VM.

### Detailed Behavior

1. **LLVM IR Generation**: Convert the optimized IR to LLVM IR.
2. **LLVM Optimization**: Leverage LLVM's optimization passes.
3. **Native Code Generation**: Use LLVM's backend to generate machine code for the target architecture.
4. **Linking**: Link against the I runtime library and system libraries.
5. **Binary Generation**: Produce a standalone executable.

### Trade-offs

| Aspect | Bytecode + VM | Native Compilation |
|--------|---------------|-------------------|
| Compilation speed | Fast | Slow |
| Execution speed | Moderate | Fast |
| Portability | High | Low |
| Debugging | Easy | Moderate |
| Binary size | Requires VM | Standalone |
| Memory safety | Guaranteed by VM | Must be compiled in |

### Why This Stage Exists (Future)

Native compilation provides maximum execution performance and enables deployment in environments where the VM cannot run (embedded systems, operating system kernels, performance-critical applications).

---

## Error Flow Architecture

```
Source Code
    │
    ▼
  Lexer ──────────────────────────┐
    │ (LEX errors)                 │
    ▼                              │
  Parser ─────────────────────────┤
    │ (PARS errors)                │
    ▼                              │
  Semantic Analyzer ──────────────┤
    │ (SEM errors + warnings)      │  All errors flow
    ▼                              │  to a central
  Type Checker ───────────────────┤  Error Collector
    │ (TYP errors + warnings)      │
    ▼                              │
  IR Generator ───────────────────┤
    │ (IR errors - rare)           │
    ▼                              │
  Optimizer ──────────────────────┤
    │ (OPT errors - internal)      │
    ▼                              │
  Bytecode Generator ─────────────┤
    │ (BC errors - rare)           │
    ▼                              │
  Virtual Machine ────────────────┘
    │ (RUN errors)
    ▼
  Error Formatter
    │
    ▼
  stderr (bilingual, with suggestions)
```

### Error Collector Design

The `ErrorCollector` is a shared component used by all stages:

```
ErrorCollector {
    errors: List[CompilerError]
    warnings: List[CompilerWarning]
    max_errors: int (default: 100)
    max_warnings: int (default: 200)

    report(error: CompilerError)
    report(warning: CompilerWarning)
    has_errors() -> bool
    has_warnings() -> bool
    sorted() -> List[Diagnostic]  // sorted by location
}
```

### CompilerError Structure

```
CompilerError {
    code: string          // e.g., "TYP001"
    title: string         // e.g., "Type Mismatch"
    message_en: string    // English description
    message_rw: string    // Kinyarwanda description
    file: string          // Source file path
    line: int             // Line number
    column: int           // Column number
    snippet: string       // Source code snippet
    suggestions: List[string]  // Suggested fixes
    related: List[RelatedLocation>  // Related source locations
    severity: Severity    // Error, Warning, Note
}
```

---

## Data Flow Between Stages

### Stage Interface Contract

Every stage implements this interface:

```
Stage<I, O> {
    name: string
    config: StageConfig

    execute(input: I, collector: ErrorCollector) -> O
    reset()
}
```

### Data Transformations

```
Source Text     → [Lexer]      → Token[]
Token[]         → [Parser]     → Program (AST)
Program         → [Semantic]   → AnnotatedProgram
AnnotatedProgram→ [TypeCheck]  → TypedProgram
TypedProgram    → [IRGen]      → IRModule
IRModule        → [Optimize]   → OptimizedIRModule
OptimizedIRModule→ [BytecodeGen]→ BytecodeModule
BytecodeModule  → [VM]         → Exit Code
```

### Memory Model Between Stages

Each stage allocates its own data structures and frees them when complete. The AST is allocated from an arena allocator and freed after IR generation. The IR is allocated from a separate arena and freed after bytecode generation.

---

## Compilation Modes

### Development Mode

```
Source → Lexer → Parser → Semantic → TypeCheck → IR → BytecodeGen → VM
```
- Fast compilation
- No optimizations (level 0)
- Full debug info
- Runtime bounds checking

### Release Mode

```
Source → Lexer → Parser → Semantic → TypeCheck → IR → Optimize → BytecodeGen → VM
```
- Full optimizations (level 3)
- Reduced debug info
- Inlining and loop optimization

### Native Mode (Future)

```
Source → Lexer → Parser → Semantic → TypeCheck → IR → Optimize → LLVM → Link → Executable
```
- LLVM optimizations
- Native code generation
- Stripped debug info (optional)

---

## Self-Hosting Strategy

### Phase 1: Python Bootstrap (Current)

The compiler is written in Python. This enables rapid development and iteration on the language design.

### Phase 2: I-Implemented Components

Rewrite individual compiler components in I, compiled by the Python bootstrap compiler:

1. Lexer in I
2. Parser in I
3. Semantic Analyzer in I
4. Type Checker in I
5. IR Generator in I
6. Bytecode Generator in I

### Phase 3: Full Self-Hosting

The complete compiler is written in I and compiled by itself.

### Phase 4: Optimization

Optimize the self-hosted compiler for faster compilation and lower memory usage.

### Bootstrapping Requirements

The I language features needed for self-hosting:
- File I/O (for reading source files)
- String manipulation (for tokenization and parsing)
- Hash maps (for symbol tables)
- Lists (for token streams and AST nodes)
- Error handling (for error recovery)
- Pattern matching (for dispatching on token types)

---

## Security Architecture

### Compiler Security

- **Input Validation**: Validate file paths, limit file sizes, verify UTF-8 encoding.
- **Resource Limits**: Limit compilation time, memory usage, recursion depth.
- **Dependency Integrity**: Verify that imported modules haven't been tampered with.

### Runtime Security

- **Memory Safety**: The VM guarantees memory safety through bounds checking and garbage collection.
- **Type Safety**: The type system prevents type confusion attacks.
- **Sandboxing**: The VM can execute untrusted code with restricted I/O and system call access.
- **Stack Overflow Protection**: Detect and prevent stack overflow through depth limits.

---

## Extensibility

### Adding New Syntax

1. Add token types to the Lexer (if new keywords are needed)
2. Add grammar rules to the Parser
3. Add AST node types to the AST
4. Add semantic analysis rules
5. Add type checking rules
6. Add IR generation rules
7. Add bytecode generation rules

### Adding New Backends

1. Implement a new `CodeGenerator` subclass
2. Define the target instruction format
3. Implement instruction selection
4. Implement register/stack allocation
5. Add backend-specific optimizations

### Adding New Optimizations

1. Define the optimization as an IR-to-IR transformation
2. Add it to the optimizer pass pipeline
3. Add it to the appropriate optimization level
4. Add tests and benchmarks

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
