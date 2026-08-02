# RFC-003: Algebraic Data Types & Pattern Matching

- **RFC ID**: 003
- **Author**: Irabizi Paisible Valentin
- **Status**: Draft
- **Created**: 2026-07-30
- **Updated**: 2026-07-30
- **I-Version**: 1.0
- **Category**: Language Change

## Summary

Extend the `ikindi` (enum) type to support associated data per variant (algebraic data types), and introduce a `gereranya` (match) expression for safe, exhaustive pattern matching. This is required for compiler AST representation and traversal.

## Motivation

### Problem Statement

The LANGUAGE_SPECIFICATION.md defines `ikindi` (enum) as a simple name-only enum:

```i
ikindi Error
ikindi ValueError
ikindi TypeError
ikindi RuntimeError
```

A self-hosting compiler requires AST nodes where each variant carries different data:

```i
# Binary expression needs: left, operator, right
# Literal expression needs: value
# Call expression needs: callee, arguments
```

Without algebraic data types, the compiler must use:
- Class inheritance hierarchies (verbose, unsafe downcasting)
- Single struct with nullable fields for all variants (wasteful, error-prone)
- Separate structs per node type (no common interface)

### Current Workarounds

The Python compiler uses Python's class hierarchy with `@dataclass`:

```python
class Expr(ABC): pass
@dataclass class Binary(Expr): left: Expr; op: Operator; right: Expr
@dataclass class Literal(Expr): value: Any
@dataclass class Call(Expr): callee: Expr; args: list[Expr]
```

In I without ADTs, developers would need to emulate this with inheritance, interfaces, and manual dispatching, which is non-idiomatic and error-prone.

### Why a Language Change?

Algebraic data types and pattern matching are core language features that:
1. Require new syntax for variant declarations with payloads
2. Require a `gereranya` (match) expression with exhaustiveness checking
3. Fundamentally change how the type system handles enums

## Detailed Design

### Syntax

#### Enum with Associated Data

```i
# Expression types
ikindi Expr
    | Binary(left: Expr, op: Operator, right: Expr)
    | Literal(value: any)
    | Call(callee: Expr, args: list<Expr>)
    | Variable(name: string)
    | Unary(op: Operator, operand: Expr)
    | Grouping(expression: Expr)
iherezo

# Token types
ikindi TokenType
    | INTEGER(value: int)
    | FLOAT(value: float)
    | STRING(value: string)
    | IDENTIFIER(name: string)
    | KEYWORD(kw: Keyword)
    | OPERATOR(op: OpType)
    | LPAREN
    | RPAREN
    | NEWLINE
    | EOF
iherezo

# Option type
ikindi Option<T>
    | Some(value: T)
    | None
iherezo

# Result type
ikindi Result<T, E>
    | Ok(value: T)
    | Error(info: E)
iherezo
```

#### Pattern Matching (gereranya)

```i
umurimo evaluate(expr: Expr) -> int
    gereranya expr
        Binary(left, op, right) => {
            shyira left_val = evaluate(left)
            shyira right_val = evaluate(right)
            gereranya op
                PLUS => left_val + right_val
                MINUS => left_val - right_val
                TIMES => left_val * right_val
                DIVIDE => left_val / right_val
            iherezo
        }
        Literal(value) => value
        Variable(name) => environment.kubona(name)
        Unary(op, operand) => {
            shyira val = evaluate(operand)
            gereranya op
                NEGATE => -val
                NOT => si val
            iherezo
        }
        Grouping(expr) => evaluate(expr)
        Call(callee, args) => {
            shyira callee_val = evaluate(callee)
            shyira arg_vals = args.kari(kuri evaluate)
            subira callee_val(arg_vals)
        }
    iherezo
iherezo
```

#### Exhaustiveness Checking

The compiler must verify that all variants are handled:

```i
gereranya expr
    Binary(left, op, right) => evaluate_binary(left, op, right)
    Literal(value) => value
    Variable(name) => environment.kubona(name)
    # ERROR: missing Call, Unary, Grouping variants
iherezo
```

Wildcard patterns:

```i
gereranya expr
    Binary(left, op, right) => evaluate_binary(left, op, right)
    _ => gushyingura "Unsupported expression"
iherezo
```

#### Nested Patterns

```i
gereranya expr
    # Match literal with specific value
    Literal(0) => "zero"
    Literal(value) => "non-zero: " + value
    # Match binary with any operator
    Binary(left, PLUS, right) => evaluate(left) + evaluate(right)
    # Catch all
    _ => "unknown"
iherezo
```

#### Guard Clauses

```i
gereranya value
    Literal(n) niba n irenze 0 => "positive"
    Literal(n) niba n munsi ya 0 => "negative"
    Literal(0) => "zero"
    _ => "not a number"
iherezo
```

#### Pattern Matching with Option/Result

```i
# Safe unwrapping
gereranya maybe_value
    Some(value) => value
    None => 0
iherezo

# Error handling
gereranya result
    Ok(value) => value
    Error(err) => {
        urubuga.andika("Error: " + err)
        guma(1)
    }
iherezo
```

### Semantic Changes

1. Enum variants with data are constructors (function-like)
2. Pattern matching introduces variable binding in each arm
3. Exhaustiveness checking is mandatory at compile time
4. Patterns are matched top-to-bottom, first match wins
5. Wildcard `_` matches any value without binding

### Type System Impact

1. Enums become sum types (tagged unions)
2. Pattern matching arms must all return the same type
3. Exhaustiveness checking ensures type safety
4. Destructuring binds variables with types inferred from variant fields

### Implementation Details

1. **Parser**: Parse variant syntax with optional `(...)` payloads
2. **Parser**: Parse `gereranya` expression with arm list
3. **AST**: Add fields to enum variants
4. **Type Checker**: Verify exhaustiveness, type consistency across arms
5. **Codegen**: Tagged union representation (discriminant + payload union)

## Alternatives Considered

### Alternative 1: Visitor Pattern with Interfaces

Use the visitor design pattern with interfaces for dispatching.

**Pros:** Works with existing class/interface system
**Cons:** Boilerplate-heavy, not exhaustive at compile time, verbose

### Alternative 2: Type Checking + Casts

Use `ari` (is) type checking with manual casting.

**Pros:** Simple to implement
**Cons:** Unsafe (forgot a cast), not exhaustive, runtime overhead

### Alternative 3: Separate Struct Hierarchy

Define a base struct and sub-structs for each variant.

**Pros:** Familiar OOP pattern
**Cons:** No compile-time exhaustiveness, nullable fields, downcasting

## Migration Path

### Automatic Migration

N/A — new feature

### Manual Migration

Existing enums without data continue to work as before. Only enums that add `(...)` payloads are affected.

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

1. Should `gereranya` be an expression (returning a value) or a statement?
2. Should mutable bindings in patterns be allowed?
3. Should `..` (rest pattern) be supported for matching remaining fields?
4. Should or-patterns be supported: `Binary(left, PLUS | MINUS, right)`?

## Future Possibilities

- `niba shyira` (if-let) for single-arm pattern matching
- Pattern matching in function parameters: `umurimo len(List(head, tail)) -> int`
- Match ergonomics (auto-deref patterns)

## References

- LANGUAGE_SPECIFICATION.md (ikindi section)
- Self-Hosting Feasibility Assessment (gap analysis)
- Rust enums and match (design inspiration)
- OCaml algebraic data types (original concept)

## Drawbacks

1. Pattern matching adds significant compiler complexity
2. Exhaustiveness checking may reject valid code in edge cases
3. ADTs with many variants can be verbose to match exhaustively

## Prior Art

- Rust: `enum Option<T> { Some(T), None }`, `match` with exhaustiveness
- OCaml/Haskell: Algebraic data types with pattern matching
- Swift: `enum` with associated values, `switch` with pattern matching
- TypeScript: Discriminated unions, `switch` with exhaustiveness checking
