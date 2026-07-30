# RFC-002: Generics System

- **RFC ID**: 002
- **Author**: I Programming Language Engineering Council
- **Status**: Draft
- **Created**: 2026-07-30
- **Updated**: 2026-07-30
- **I-Version**: 1.0
- **Category**: Language Change

## Summary

Implement a generics system using monomorphization, enabling type-safe generic structs, functions, and type constraints. This resolves the contradiction in LANGUAGE_SPECIFICATION.md where `list<T>`, `map<K,V>`, `set<T>`, and `tuple<T...>` are specified using generic syntax but generics are listed as a "Future Extension."

## Motivation

### Problem Statement

The LANGUAGE_SPECIFICATION.md defines composite types using generic syntax:

```
list<T>     # list of type T
map<K, V>   # map from K to V
set<T>      # set of type T
tuple<T...> # tuple of types
```

However, generics are listed under "Future Extensions" with pattern matching, async/await, reflection, and metaprogramming. This is a contradiction — the types cannot be implemented without generics.

A self-hosting compiler requires type-safe collections for:
- Symbol tables: `map<string, SymbolInfo>`
- Token streams: `list<Token>`
- AST node children: `list<Stmt>`, `list<Expr>`
- Type parameters: `list<Type>`

Without generics, the compiler must either use untyped collections (defeating type safety) or duplicate data structures for each type.

### Current Workarounds

The Python bootstrap compiler uses Python's built-in generic types (`list[Token]`, `dict[str, Symbol]`). Without generics in I, compiler authors would need to:
1. Use `any`-typed collections and cast (unsafe)
2. Write separate structs for each collection type (verbose, error-prone)

### Why a Language Change?

Generics fundamentally affect the type system and require new syntax for:
- Generic struct declarations: `igiceri List<T>`
- Generic function declarations: `umurimo first<T>(items: list<T>) -> T`
- Type constraint syntax: `urubingo Comparable<T>`

## Detailed Design

### Syntax

#### Generic Structs

```i
igiceri List<T>
    elements: list<T>
    uburebure: int
    
    umurimo nshya() -> List<T>
        subira List(elements: [], uburebure: 0)
    iherezo
    
    umurimo ongeza(element: T) -> void
        self.elements = self.elements + [element]
        self.uburebure += 1
    iherezo
    
    umurimo kubona(index: int) -> T
        subira self.elements[index]
    iherezo
iherezo
```

#### Generic Functions

```i
# Generic function
umurimo first<T>(items: list<T>) -> T
    niba items.uburebure() irenze 0
        subira items[0]
    cyangwa
        gushyingura "List is empty"
    iherezo
iherezo

# Usage
shyira numbers = [1, 2, 3]
shyira first_num = first<int>(numbers)

shyira names = ["Alice", "Bob"]
shyira first_name = first<string>(names)
```

#### Multiple Type Parameters

```i
igiceri Map<K, V>
    keys: list<K>
    values: list<V>
    
    umurimo nshya() -> Map<K, V>
        subira Map(keys: [], values: [])
    iherezo
    
    umurimo shyira(key: K, value: V) -> void
        self.keys.ongeza(key)
        self.values.ongeza(value)
    iherezo
    
    umurimo kubona(key: K) -> V | ubusa
        buri i muri 0..self.keys.uburebure()
            niba self.keys[i] == key
                subira self.values[i]
            iherezo
        iherezo
        subira ubusa
    iherezo
iherezo
```

#### Type Constraints

```i
# Define a constraint trait
urubingo Comparable<T>
    umurimo igereranya(other: T) -> int
iherezo

# Constrain a generic parameter
umurimo max<T>(a: T, b: T) -> T niba T kugira Comparable<T>
    niba a.igereranya(b) irenze 0
        subira a
    cyangwa
        subira b
    iherezo
iherezo
```

#### Generic Type Aliases

```i
# Type alias for complex generic types
shyira_ko StringMap<V> = Map<string, V>
shyira_ko IntList = List<int>
```

### Semantic Changes

1. **Monomorphization**: Each concrete instantiation of a generic function/struct generates a specialized copy
2. **Type inference**: Generic type parameters may be inferred from usage when unambiguous
3. **Constraint checking**: Type arguments must satisfy declared constraints at instantiation time

### Type System Impact

1. Type parameters introduce a new kind of type variable
2. Constraint checking uses the trait/interface system
3. Monomorphization happens after type checking (during code generation)

### Implementation Details

1. **Parser**: Add `<T>` syntax to struct, function, and type alias declarations
2. **AST**: Add `GenericParam` node, `GenericArgs` to type references
3. **Type Checker**: Track type parameters, verify constraints
4. **Codegen**: Monomorphize — for each unique set of type arguments, generate a copy of the generic code

## Alternatives Considered

### Alternative 1: Type Erasure (Java-style)

Generic types are erased at runtime; all generic code operates on `any`.

**Pros:** Simpler implementation, smaller binaries
**Cons:** No runtime type safety, boxing overhead, no specialization

### Alternative 2: Dynamic Typing Only

Remove generic syntax entirely; use `any` for collections.

**Pros:** Simpler language
**Cons:** No type safety for collections, defeats purpose of static typing

### Alternative 3: No Generics (Duplicated Structs)

Require users to manually create `IntList`, `StringList`, etc.

**Pros:** No compiler complexity
**Cons:** Extremely verbose, error-prone, impractical for compiler self-hosting

## Migration Path

### Automatic Migration

N/A — this is a net-new feature

### Manual Migration

Existing code that uses untyped collections should add type parameters:
```i
# Before
shyira list = []
shyira list.ongeza(42)

# After
shyira list: list<int> = []
shyira list.ongeza(42)
```

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

1. Should type inference be bidirectional (Hindley-Milner) or unidirectional?
2. Should generic functions support specialization for performance?
3. Should `niba T kugira Comparable<T>` use trait syntax or a new `aho` (where) clause?

## Future Possibilities

- Higher-kinded types (generics over generics)
- Associated type defaults
- Generic constant parameters: `List<T, N: int>`
- Variance annotations (covariant, contravariant)

## References

- LANGUAGE_SPECIFICATION.md (composite types section)
- Self-Hosting Feasibility Assessment (gap analysis)
- Rust generics system (design inspiration)
- C++ templates (monomorphization model)

## Drawbacks

1. Monomorphization increases compilation time and binary size
2. Generic code is harder to write and debug than concrete code
3. Complex type constraints can lead to confusing error messages

## Prior Art

- Rust: Generic structs `struct Foo<T>`, trait bounds `T: Display`
- C++: Templates (monomorphization)
- Java: Generics with type erasure
- C#: Generics with reification
