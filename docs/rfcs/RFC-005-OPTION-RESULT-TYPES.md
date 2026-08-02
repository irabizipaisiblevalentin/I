# RFC-005: Option/Result Types

- **RFC ID**: 005
- **Author**: Irabizi Paisible Valentin
- **Status**: Draft
- **Created**: 2026-07-30
- **Updated**: 2026-07-30
- **I-Version**: 1.0
- **Category**: Language Change

## Summary

Introduce `Option<T>` and `Result<T, E>` types as first-class language features with dedicated syntax (`T | ubusa`), a `?` propagation operator, and safe unwrapping via pattern matching. These types enable safe error handling without exceptions for compiler code, where fallible operations are the norm.

## Motivation

### Problem Statement

The LANGUAGE_SPECIFICATION.md defines exception-based error handling (try/catch/throw). However, exceptions are unsuitable for many compiler operations:

1. **Parsing**: Expected errors (syntax errors) should not use stack unwinding
2. **Symbol resolution**: Missing symbols are common and should be handled locally
3. **Type checking**: Type errors are discovered and reported without crashing
4. **Code generation**: Fallible operations need local error handling

A self-hosting compiler needs a way to represent:
- **Optional values**: A symbol may or may not exist in a scope
- **Fallible results**: An operation may succeed or fail with an error
- **Early propagation**: "If this fails, return the error to my caller"

### Current Workarounds

Without Option/Result types, developers would use:
- Sentinel values: `-1` for "not found" (error-prone, type-incorrect)
- Null/nullable: `ubusa` for "not found" (no type safety)
- Exceptions: Try/catch for expected failures (slow, complex flow)

### Why a Language Change?

Option/Result types require:
1. Generic type definitions (already proposed in RFC-002)
2. Syntax sugar: `T | ubusa` for `Option<T>`
3. `?` operator for early propagation (parser-level change)
4. Integration with pattern matching (RFC-003)

## Detailed Design

### Option Type

```i
# Option represents an optional value: Some(value) or None
ikindi Option<T>
    | Some(value: T)
    | None
iherezo

# Sugar: T | ubusa  means  Option<T>
```

### Result Type

```i
# Result represents success or failure: Ok(value) or Error(info)
ikindi Result<T, E>
    | Ok(value: T)
    | Error(info: E)
iherezo
```

### Usage Patterns

#### Creating Options

```i
# With value
shyira some_value = Option.Some(42)
shyira some_value: int | ubusa = 42  # wrapped automatically

# None
shyira no_value = Option.None
shyira no_value: int | ubusa = ubusa
```

#### Using Options with Pattern Matching

```i
gereranya maybe_value
    Some(value) => urubuga.andika("Got: " + value)
    None => urubuga.andika("Nothing")
iherezo
```

#### Unwrapping Options

```i
# Unwrap with default
shyira value = maybe_value.cya()  # returns value or ubusa (same as bare access)
shyira value = maybe_value.cyangwa(0)  # returns value or 0

# Unwrap with panic
shyira value = maybe_value.fungura()  # panics if None
```

#### Creating Results

```i
# Success
shyira success = Result.Ok(42)

# Failure
shyira failure = Result.Error("Something went wrong")

# Typed
shyira result: Result<int, string> = Result.Ok(42)
```

#### Using Results

```i
gereranya result
    Ok(value) => urubuga.andika("Success: " + value)
    Error(info) => urubuga.andika("Error: " + info)
iherezo
```

### The `?` Propagation Operator

The `?` operator provides early propagation: if a value is `Option.None` or `Result.Error(...)`, return/immediately from the current function with that value.

```i
umurimo soma_dosive_yizewe(path: string) -> Result<string, string>
    shyira content = urubuga.soma_dosive(path) ?  # returns Error if failed
    niba content.uburebure() irenze 0
        subira Result.Ok(content)
    cyangwa
        subira Result.Error("Empty file")
    iherezo
iherezo

# Must be called from a function that returns Option or Result
umurimo process_file(path: string) -> Result<string, string>
    shyira content = soma_dosive_yizewe(path) ?
    shyira lines = content.ma("\n").uburebure()
    subira Result.Ok("Processed " + lines + " lines")
iherezo
```

### Integration with Standard Library

Standard library functions that can fail return Result types:

```i
# File I/O
urubuga.soma_dosive(path) -> Result<string, Error>

# Parsing
"42".kuba_int() -> Result<int, string>
"3.14".kuba_float() -> Result<float, string>

# Collection access
list.kubona(index) -> Option<T>  # or T | ubusa
map.kubona(key) -> Option<V>     # or V | ubusa
```

### Conversion Between Option and Result

```i
# Option to Result
shyira result = maybe_value.cyangwa("Not found").mbere(Error)

# Result to Option
shyira option = result.nziza()  # Ok(value) -> Some(value), Error -> None
```

### Semantic Changes

1. `?` operator is only valid in functions returning `Option<T>` or `Result<T, E>`
2. The `?` operator type-checks: the returned error type must unify with the function's error type
3. `Option.Some(x)` wraps `x`; `Option.None` represents absence
4. `Result.Ok(x)` represents success; `Result.Error(e)` represents failure

### Type System Impact

1. `T | ubusa` is syntactic sugar for `Option<T>`
2. The `?` operator changes control flow (early return)
3. Type inference can infer Option/Result types from usage

### Implementation Details

1. **Parser**: Parse `?` as a postfix operator on expressions
2. **Parser**: Parse `T | ubusa` as a type (union with null)
3. **Type Checker**: Verify `?` is used in valid contexts
4. **Codegen**: `Option<T>` uses tagged union with discriminant; `None` is a null-like value
5. **Optimizer**: Eliminate redundant None checks after `?` propagation

## Alternatives Considered

### Alternative 1: Exceptions Only

Use try/catch for all error handling, including expected failures.

**Pros:** Simple, consistent model
**Cons:** Slow for expected errors, complex control flow, no type-level documentation

### Alternative 2: Nullable Types Only (`T | ubusa`)

Use nullable types without Result, losing error information.

**Pros:** Simple, familiar
**Cons:** No error context (why did it fail?), no distinction between "not found" and "error"

### Alternative 3: Monadic Error Handling (Haskell)

Use do-notation or monadic composition for error handling.

**Pros:** Purely functional, composable
**Cons:** Unfamiliar syntax, complex for imperative code

## Migration Path

### Automatic Migration

N/A — new feature

### Manual Migration

N/A

### Deprecation Timeline

N/A

## Impact Assessment

### Backward Compatibility

- [x] No breaking changes
- [ ] Breaking changes (with migration path)
- [ ] Breaking changes (without migration path)

### Performance Impact

- [x] No performance impact
- [ ] Positive performance impact
- [ ] Negative performance impact (acceptable)
- [ ] Negative performance impact (unacceptable)

### Tooling Impact

- [x] No tooling changes required
- [ ] Minor tooling changes
- [ ] Major tooling changes

### Documentation Impact

- [x] No documentation changes
- [ ] Minor documentation changes
- [ ] Major documentation changes

### Testing Impact

- [x] No new tests required
- [ ] Minor test additions
- [ ] Major test additions

## Unresolved Questions

1. Should `?` work in non-Option/Result functions (e.g., by panicking)?
2. Should there be an `try` keyword that converts exceptions to Results?
3. Should Option/Result have monadic methods (`map`, `and_then`, `or_else`)?

## Future Possibilities

- `try` block that converts exceptions to Results: `try { code }`
- `niba shyira` (if-let) for single-arm matching on Options
- Combinators: `.map()`, `.and_then()`, `.or_else()`, `.unwrap_or_else()`

## References

- LANGUAGE_SPECIFICATION.md (error handling section)
- RFC-002: Generics System (required for Option<T>)
- RFC-003: Algebraic Data Types (required for pattern matching)
- Self-Hosting Feasibility Assessment (gap analysis)

## Drawbacks

1. Adds complexity: `?` operator, type system changes, standard library integration
2. Two error handling models (exceptions + Option/Result) may confuse beginners
3. `?` propagation obscures control flow for readers

## Prior Art

- Rust: `Option<T>`, `Result<T, E>`, `?` operator
- Haskell: `Maybe`, `Either` types
- Swift: `Optional<T>`, `?` unwrapping
- Kotlin: Nullable types `T?`, `?:` elvis operator
