# Semantic Analyzer Design

This document specifies the complete design of the I Programming Language semantic analyzer, including variable resolution, scopes, symbol tables, namespaces, module resolution, and control-flow validation.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Variable Resolution](#variable-resolution)
- [Scopes](#scopes)
- [Symbol Tables](#symbol-tables)
- [Namespaces](#namespaces)
- [Module Resolution](#module-resolution)
- [Control-Flow Validation](#control-flow-validation)
- [Unused Variable Detection](#unused-variable-detection)
- [Warnings](#warnings)
- [Errors](#errors)
- [Performance](#performance)
- [Testing Strategy](#testing-strategy)

## Overview

The semantic analyzer is the third stage of the I compiler pipeline. It walks the AST produced by the parser and validates semantic correctness, building the symbol table infrastructure that the type checker and code generator depend on.

### Responsibilities

1. Build a hierarchy of scopes
2. Resolve every identifier to its declaration
3. Detect duplicate declarations
4. Validate control flow (break/continue/return)
5. Validate mutation rules (const cannot be reassigned)
6. Resolve module imports
7. Detect unused variables and emit warnings
8. Attach symbol information to AST nodes

### Input/Output

```
Input:  Program (AST root) + ModuleRegistry
Output: AnnotatedProgram + SymbolTable + List[CompilerError] + List[CompilerWarning]
```

### Why Separate from Type Checking?

Semantic analysis (scope resolution, name binding) is separated from type checking because:

1. Scope errors are simpler and can be reported independently
2. We can report scope errors without needing the full type system
3. Error messages are clearer when separated
4. It enables gradual typing in the future

## Architecture

```
Program (AST)
    │
    ▼
┌───────────────────┐
│  Scope Builder     │  Walk AST, build scope hierarchy
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│  Name Resolver     │  Resolve identifiers to declarations
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│  Module Resolver   │  Resolve import declarations
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│  Control Flow      │  Validate break/continue/return
│  Validator         │
└───────┬───────────┘
        │
        ▼
┌───────────────────┐
│  Usage Analyzer    │  Detect unused variables
└───────┬───────────┘
        │
        ▼
  AnnotatedProgram + SymbolTable
```

## Variable Resolution

### Resolution Algorithm

For every `IdentifierExpr` in the AST, the analyzer must find its corresponding declaration:

```
function resolveIdentifier(name: string, current_scope: Scope) -> Symbol:
    scope = current_scope

    while scope != null:
        if scope.symbols.contains(name):
            symbol = scope.symbols.get(name)
            symbol.is_used = true
            symbol.use_location = current_location
            return symbol

        scope = scope.parent

    // Not found - emit error SEM001
    emitError(SEM001, "Undefined variable '{name}'")
    return createErrorSymbol(name)
```

### Resolution Order

Identifiers are resolved in the following order:

1. **Local scope**: Variables declared in the current block
2. **Function scope**: Parameters and variables in the enclosing function
3. **Class scope**: Fields and methods of the enclosing class
4. **Module scope**: Top-level declarations in the current module
5. **Import scope**: Imported names from other modules
6. **Global scope**: Built-in names and standard library

### Shadowing Rules

A variable in an inner scope can shadow a variable in an outer scope:

```
shyira x = 10
kora
    shyira x = 20   // Shadows outer x
    andika x         // Uses inner x (20)
iherezo
andika x             // Uses outer x (10)
```

Shadowing is allowed but generates a warning (SEM101).

### Forward References

Functions can reference other functions declared later in the same scope:

```
umurimo a() -> void
    b()    // Forward reference - allowed
iherezo

umurimo b() -> void
    // ...
iherezo
```

Variables cannot be referenced before their declaration:

```
andika x    // Error: SEM002 "Variable 'x' used before declaration"
shyira x = 10
```

## Scopes

### Scope Types

| Scope | Created By | Parent | Lifetime |
|-------|-----------|--------|----------|
| Global | Program start | null | Entire compilation |
| Module | Module file | Global | Module compilation |
| Function | Function declaration | Module/Block | Function body |
| Block | Block statement (kora/iherezo) | Enclosing | Block execution |
| Class | Class declaration | Module | Class definition |
| Trait | Trait declaration | Module | Trait definition |

### Scope Structure

```
Scope {
    parent: Optional<Scope>       // Parent scope (null for global)
    kind: ScopeKind               // GLOBAL, MODULE, FUNCTION, BLOCK, CLASS, TRAIT
    symbols: Map<String, Symbol>  // Symbol bindings
    start_offset: int             // AST offset where scope begins
    end_offset: int               // AST offset where scope ends
    children: List<Scope>         // Child scopes
}
```

### Scope Building Algorithm

```
function buildScopes(ast: Program):
    global_scope = Scope(GLOBAL)

    for declaration in ast.declarations:
        buildScopesForDeclaration(declaration, global_scope)

function buildScopesForDeclaration(decl: Declaration, parent: Scope):
    match decl:
        case FunctionDecl:
            func_scope = Scope(FUNCTION, parent)
            // Add parameters to function scope
            for param in decl.parameters:
                func_scope.add(param.name, Symbol(param))
            // Build scopes for function body
            buildScopesForBlock(decl.body, func_scope)

        case VariableDecl:
            // Add variable to current scope
            parent.add(decl.name, Symbol(decl))

        case StructDecl | ClassDecl | EnumDecl | TraitDecl:
            type_scope = Scope(CLASS, parent)
            // Add type to parent scope
            parent.add(decl.name, Symbol(decl))
            // Build scopes for type members
            for member in decl.methods:
                buildScopesForDeclaration(member, type_scope)
            for field in decl.fields:
                type_scope.add(field.name, Symbol(field))

        case BlockStmt:
            block_scope = Scope(BLOCK, parent)
            buildScopesForBlock(decl, block_scope)

function buildScopesForBlock(block: BlockStmt, scope: Scope):
    for stmt in block.statements:
        buildScopesForStatement(stmt, scope)

function buildScopesForStatement(stmt: Statement, scope: Scope):
    match stmt:
        case IfStmt:
            buildScopesForBlock(stmt.then_branch, scope)
            if stmt.else_branch:
                buildScopesForBlock(stmt.else_branch, scope)

        case WhileStmt | UntilStmt:
            buildScopesForBlock(stmt.body, scope)

        case ForStmt | ForEachStmt:
            loop_scope = Scope(BLOCK, scope)
            loop_scope.add(stmt.variable, Symbol(stmt))
            buildScopesForBlock(stmt.body, loop_scope)

        case TryStmt:
            buildScopesForBlock(stmt.try_block, scope)
            catch_scope = Scope(BLOCK, scope)
            if stmt.catch_var:
                catch_scope.add(stmt.catch_var, Symbol(stmt))
            buildScopesForBlock(stmt.catch_block, catch_scope)
            if stmt.finally_block:
                buildScopesForBlock(stmt.finally_block, scope)

        case BlockStmt:
            buildScopesForBlock(stmt, scope)

        // Other statements don't create new scopes
```

### Scope Lookup Diagram

```
Global Scope
├── Module Scope (std/io)
│   ├── Function: print
│   ├── Function: read
│   └── Struct: File
├── Module Scope (main)
│   ├── Function: main
│   │   ├── Block Scope
│   │   │   ├── Variable: x
│   │   │   └── Variable: y
│   │   └── Block Scope (if branch)
│   │       └── Variable: z
│   ├── Function: helper
│   │   └── Parameter: n
│   ├── Struct: Person
│   │   ├── Field: name
│   │   └── Field: age
│   └── Variable: counter
```

## Symbol Tables

### Symbol Structure

```
Symbol {
    name: string                          // Symbol name
    kind: SymbolKind                      // VARIABLE, FUNCTION, PARAMETER, FIELD, TYPE, MODULE
    declaration: ASTNode                  // The declaration node
    type: Optional<Type>                  // Type annotation (filled by type checker)
    scope: Scope                          // The scope where defined
    visibility: Visibility                // PUBLIC, PRIVATE, PROTECTED
    is_mutable: bool                      // shyira vs shyira_ko
    is_used: bool                         // Whether the symbol is referenced
    use_count: int                        // Number of references
    first_use_location: Optional<Location>  // First reference location
    doc_comments: List<string>            // Documentation
}
```

### SymbolKind Enumeration

```
SymbolKind enum {
    VARIABLE          // shyira / shyira_ko
    FUNCTION          // umurimo
    PARAMETER         // Function parameter
    STRUCT            // igiceri
    ENUM              // ikindi
    CLASS             // urwego
    TRAIT             // urubingo
    INTERFACE         // akabuto
    TYPE_ALIAS        // type
    MODULE            // shyiramo
    FIELD             // Struct/class field
    METHOD            // Struct/class method
    VARIANT           // Enum variant
    BUILTIN           // Built-in function or type
}
```

### Symbol Table Hierarchy

```
SymbolTable {
    scopes: Map<ScopeId, ScopeSymbols>
    global_scope: ScopeSymbols

    lookup(name: string, scope: Scope) -> Optional<Symbol>
    define(name: string, symbol: Symbol, scope: Scope) -> bool
    getScopeSymbols(scope: Scope) -> ScopeSymbols
}

ScopeSymbols {
    symbols: Map<String, Symbol>

    add(name: string, symbol: Symbol) -> bool  // false if duplicate
    get(name: string) -> Optional<Symbol>
    contains(name: string) -> bool
    all() -> List<Symbol>
}
```

### Duplicate Detection

When defining a symbol, check for duplicates:

```
function defineSymbol(name: string, symbol: Symbol, scope: Scope):
    existing = scope.symbols.get(name)

    if existing != null:
        if existing.kind == FUNCTION and symbol.kind == FUNCTION:
            // Function overloading - check parameter types
            // (deferred to type checker)
            return

        // Duplicate error
        emitError(SEM003,
            "Duplicate declaration of '{name}'",
            related=existing.declaration.location)
        return

    scope.symbols.add(name, symbol)
```

## Namespaces

### Module Namespace

Each module has its own namespace. When a module is imported, its exported symbols are brought into the importing module's namespace:

```
// Module: utils.i
tanga add(a: int, b: int) -> int
    subira a + b
iherezo

tanga multiply(a: int, b: int) -> int
    subira a * b
iherezo

// Module: main.i
shyiramo "utils"

shyira result = add(1, 2)     // Uses utils.add
shyira product = multiply(3, 4)  // Uses utils.multiply
```

### Qualified Names

Modules can be accessed using dot notation:

```
shyiramo "math"

shyira result = math.sqrt(25)
```

### Namespace Resolution

```
function resolveQualifiedName(parts: List[string], scope: Scope) -> Symbol:
    // Try to resolve as a module path
    module = moduleRegistry.get(parts[0])
    if module != null:
        symbol = module.lookup(parts[1:])
        if symbol != null:
            return symbol

    // Try to resolve as a local qualified name
    // e.g., struct.field
    current = resolveIdentifier(parts[0], scope)
    for i in range(1, len(parts)):
        member = lookupMember(current.type, parts[i])
        if member == null:
            emitError(SEM005, "No member '{parts[i]}' on type '{current.type}'")
            return createErrorSymbol(parts[i])
        current = member

    return current
```

## Module Resolution

### Module Search Path

When resolving `shyiramo "module_path"`, the compiler searches:

1. **Current directory**: Relative to the importing file
2. **Standard library**: Built-in modules under `stdlib/`
3. **Package directories**: Configured package search paths

### Module Resolution Algorithm

```
function resolveModule(path: string, from_file: string):
    // 1. Try relative path
    dir = dirname(from_file)
    candidates = [
        dir / path / "index.i",
        dir / path + ".i",
        dir / path,
    ]

    // 2. Try standard library
    candidates.append(stdlib_dir / path / "index.i")
    candidates.append(stdlib_dir / path + ".i")

    // 3. Try package paths
    for pkg_dir in package_dirs:
        candidates.append(pkg_dir / path / "index.i")
        candidates.append(pkg_dir / path + ".i")

    // 4. Find first existing candidate
    for candidate in candidates:
        if fileExists(candidate):
            return candidate

    emitError(SEM006, "Module '{path}' not found")
    return null
```

### Module Loading

```
function loadModule(path: string) -> ModuleSymbol:
    if moduleCache.contains(path):
        return moduleCache.get(path)

    // Parse and analyze the module
    source = readFile(path)
    tokens = lexer.tokenize(source)
    ast = parser.parse(tokens)

    // Run semantic analysis on the module
    module_scope = semanticAnalyzer.analyzeModule(ast)

    // Cache the result
    moduleCache.put(path, module_scope)

    return module_scope
```

### Circular Import Detection

The module loader tracks a set of "currently loading" modules. If a module tries to import one that is currently being loaded, a circular import error is detected:

```
function loadModule(path: string):
    if currentlyLoading.contains(path):
        emitError(SEM007, "Circular import detected: '{path}'")
        return createErrorModule(path)

    currentlyLoading.add(path)
    // ... load module ...
    currentlyLoading.remove(path)
```

### Export Validation

When a module exports a symbol, verify that the symbol exists:

```
function processExport(decl: ExportDecl, scope: Scope):
    if decl.name != null:
        symbol = scope.lookup(decl.name)
        if symbol == null:
            emitError(SEM008, "Cannot export undefined '{decl.name}'")
            return
        symbol.visibility = PUBLIC
    else:
        // Export entire declaration
        decl.declaration.visibility = PUBLIC
```

## Control-Flow Validation

### Break Validation

`gukoma` (break) must appear inside a loop (while, until, for, for-each):

```
function validateBreak(stmt: BreakStmt, current_scope: Scope):
    scope = current_scope
    while scope != null:
        if scope.kind == LOOP:
            // Valid break
            return
        if scope.kind == FUNCTION:
            break  // Can't break out of a function
        scope = scope.parent

    emitError(SEM009, "gukoma (break) outside of loop")
```

### Continue Validation

`kugenda` (continue) must appear inside a loop:

```
function validateContinue(stmt: ContinueStmt, current_scope: Scope):
    scope = current_scope
    while scope != null:
        if scope.kind == LOOP:
            return
        if scope.kind == FUNCTION:
            break
        scope = scope.parent

    emitError(SEM010, "kugenda (continue) outside of loop")
```

### Return Validation

`subira` (return) must appear inside a function. The return value (if present) must be consistent with the function's return type:

```
function validateReturn(stmt: ReturnStmt, current_scope: Scope):
    scope = current_scope
    while scope != null:
        if scope.kind == FUNCTION:
            func = scope.function_declaration
            if stmt.value != null and func.return_type == null:
                emitError(SEM011, "Function '{func.name}' has no return type but return has value")
            if stmt.value == null and func.return_type != null:
                emitWarning(SEM102, "Function '{func.name}' expects return value")
            return
        scope = scope.parent

    emitError(SEM012, "subira (return) outside of function")
```

### Unreachable Code Detection

```
function detectUnreachableCode(statements: List<Statement>):
    for i in range(len(statements)):
        if isTerminating(statements[i]):
            if i + 1 < len(statements):
                emitWarning(SEM103, "Unreachable code after '{statements[i].kind}'")
            break

function isTerminating(stmt: Statement) -> bool:
    match stmt:
        case ReturnStmt: return true
        case BreakStmt: return true
        case ContinueStmt: return true
        case ThrowStmt: return true
        case IfStmt:
            // Only if both branches terminate
            return isTerminatingBlock(stmt.then_branch) and
                   stmt.else_branch != null and
                   isTerminatingBlock(stmt.else_branch)
        case BlockStmt:
            return isTerminatingBlock(stmt)
        case ExpressionStmt:
            if stmt.expression is CallExpr and stmt.expression.callee is IdentifierExpr:
                // Check if function always throws (future)
                return false
        default: return false
```

### Exhaustive Return Check

```
function checkExhaustiveReturn(func: FunctionDecl):
    if func.return_type == null:
        return  // void function

    last_stmt = func.body.statements.last()
    if not isTerminating(last_stmt):
        emitError(SEM013, "Function '{func.name}' must return a value on all paths")
```

## Unused Variable Detection

### Detection Algorithm

After all names are resolved and used, check for unused variables:

```
function detectUnusedVariables(scope: Scope):
    for symbol in scope.symbols.all():
        if symbol.kind == VARIABLE and not symbol.is_used:
            emitWarning(SEM104, "Variable '{symbol.name}' is declared but never used",
                       location=symbol.declaration.location)

        if symbol.kind == PARAMETER and not symbol.is_used:
            emitWarning(SEM105, "Parameter '{symbol.name}' is unused",
                       location=symbol.declaration.location)

    for child in scope.children:
        detectUnusedVariables(child)
```

### Exceptions

The following are exempt from unused variable warnings:

1. **Variables prefixed with `_`**: Convention for intentionally unused variables
2. **Parameters starting with `_`**: Convention for unused parameters
3. **Function declarations**: Functions may be unused in the current module but used elsewhere
4. **Type declarations**: Types may be unused in the current module but used elsewhere
5. **Variables in test files**: Test files may have unused setup variables

## Warnings

### Warning Types

| Code | Name | Description | Severity |
|------|------|-------------|----------|
| SEM101 | Shadowed Variable | Inner variable shadows outer variable | Low |
| SEM102 | Missing Return Value | Function expects return but none provided | Medium |
| SEM103 | Unreachable Code | Code after terminating statement | Medium |
| SEM104 | Unused Variable | Variable declared but never used | Low |
| SEM105 | Unused Parameter | Parameter never used in function body | Low |
| SEM106 | Unused Import | Imported module not used | Low |
| SEM107 | Deprecated Usage | Using deprecated feature | Medium |
| SEM108 | Possible Null | Nullable value used without null check | Medium |
| SEM109 | Constant Modified | Attempt to modify const (may be dead code) | Low |

### Warning Configuration

```
WarningConfig {
    enabled: bool = true
    as_errors: bool = false  // Treat warnings as errors
    suppressed_codes: Set<String> = {}
    suppressed_lines: Set<(file, line)> = {}
}
```

## Errors

### Error Types

| Code | Name | Description | Recovery |
|------|------|-------------|----------|
| SEM001 | Undefined Variable | Variable not found in any scope | Insert error symbol |
| SEM002 | Use Before Decl | Variable used before declaration | Insert error symbol |
| SEM003 | Duplicate Declaration | Name already defined in scope | Skip declaration |
| SEM004 | Type Mismatch | (deferred to type checker) | - |
| SEM005 | No Member | Member not found on type | Insert error symbol |
| SEM006 | Module Not Found | Import path cannot be resolved | Skip import |
| SEM007 | Circular Import | Module imports itself directly/indirectly | Skip import |
| SEM008 | Export Not Found | Exported symbol doesn't exist | Skip export |
| SEM009 | Break Outside Loop | break not in a loop | Skip statement |
| SEM010 | Continue Outside Loop | continue not in a loop | Skip statement |
| SEM011 | Return Value Mismatch | Return value type mismatch | Insert error symbol |
| SEM012 | Return Outside Function | return not in a function | Skip statement |
| SEM013 | Missing Return | Function doesn't return on all paths | Insert synthetic return |

### Error Recovery

The semantic analyzer uses error symbols to prevent cascading errors:

```
function createErrorSymbol(name: string) -> Symbol:
    return Symbol(
        name = name,
        kind = ERROR,
        type = ERROR_TYPE
    )
```

When an error symbol is used in subsequent analysis, no further errors are generated for that expression. This prevents a single undefined variable from generating errors at every use site.

## Performance

### Time Complexity

- **Scope building**: O(n) where n is the number of AST nodes
- **Name resolution**: O(n * d) where d is the scope depth (typically small)
- **Symbol table operations**: O(1) with hash maps
- **Overall**: O(n)

### Space Complexity

- **Scope hierarchy**: O(s) where s is the number of scopes
- **Symbol table**: O(n) where n is the number of symbols
- **Total**: O(n)

### Optimization Strategies

1. **Hash maps for symbol lookup**: O(1) average case
2. **Scope chain caching**: Cache scope lookup results
3. **Lazy analysis**: Only analyze modules that are actually used
4. **Incremental analysis**: Re-analyze only changed modules

## Testing Strategy

### Unit Tests

- **Scope building**: Verify correct scope hierarchy
- **Name resolution**: Verify identifiers resolve to correct declarations
- **Duplicate detection**: Verify duplicate declarations are caught
- **Control flow**: Verify break/continue/return validation
- **Unused variables**: Verify warnings for unused variables

### Integration Tests

- **Multi-module programs**: Verify module resolution
- **Complex programs**: Verify analysis of realistic programs
- **Error recovery**: Verify error recovery produces reasonable results

### Regression Tests

- **Past bugs**: Test for known semantic analysis bugs
- **Edge cases**: Test boundary conditions

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
