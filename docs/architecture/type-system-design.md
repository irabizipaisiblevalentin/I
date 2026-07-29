# Type System Design

This document specifies the complete type system of the I Programming Language, including primitive types, composite types, user-defined types, type inference, and type checking rules.

## Table of Contents

- [Overview](#overview)
- [Type Categories](#type-categories)
- [Primitive Types](#primitive-types)
- [Composite Types](#composite-types)
- [User-Defined Types](#user-defined-types)
- [Type Annotations](#type-annotations)
- [Type Inference](#type-inference)
- [Type Checking Rules](#type-checking-rules)
- [Generic Types](#generic-types)
- [Union Types](#union-types)
- [Optional Types](#optional-types)
- [Function Types](#function-types)
- [Type Compatibility](#type-compatibility)
- [Type Coercion](#type-coercion)
- [Type Errors](#type-errors)
- [Performance](#performance)

## Overview

The I type system is designed for:

1. **Safety**: Catch type errors at compile time
2. **Expressiveness**: Support modern type system features
3. **Inference**: Minimize annotation requirements
4. **Clarity**: Error messages explain what went wrong
5. **Extensibility**: Accommodate future type system features

### Type System Philosophy

The I type system follows the principle of **progressive type safety**:

- Start with simple, well-understood types
- Add complexity only when needed
- Provide clear paths for type system evolution
- Keep inference predictable and understandable

## Type Categories

### Type Hierarchy

```
Type
├── PrimitiveType
│   ├── Int
│   ├── Float
│   ├── Bool
│   ├── String
│   ├── Char
│   └── Null
├── CompositeType
│   ├── List<T>
│   ├── Dict<K, V>
│   ├── Set<T>
│   └── Tuple<T1, T2, ...>
├── UserType
│   ├── Struct
│   ├── Enum
│   ├── Class
│   ├── Trait
│   └── TypeAlias
├── FunctionType
├── GenericType
├── UnionType
├── OptionalType
├── VoidType
└── ErrorType (for error recovery)
```

## Primitive Types

### Int

```
Type: int
Size: 64-bit signed integer
Range: -2^63 to 2^63-1
Default value: 0
Literal syntax: 42, -10, 0xFF, 0o77, 0b1010
```

**Operations:**
```
// Arithmetic
int + int -> int
int - int -> int
int * int -> int
int / int -> int    (integer division)
int % int -> int    (modulo)
int ** int -> int   (power)

// Comparison
int == int -> bool
int != int -> bool
int < int -> bool
int > int -> bool
int <= int -> bool
int >= int -> bool

// Bitwise
int & int -> int
int | int -> int
int ^ int -> int
~int -> int
int << int -> int
int >> int -> int
int >>> int -> int    (unsigned right shift)

// Conversion
int -> float  (implicit)
int -> string (explicit: string(42))
int -> bool   (explicit: bool(42), 0=false, else=true)
```

### Float

```
Type: float
Size: 64-bit IEEE 754 double
Range: ±5.0e-324 to ±1.7976931348623157e+308
Default value: 0.0
Literal syntax: 3.14, -0.001, 1.0e10, .5
```

**Operations:**
```
// Arithmetic
float + float -> float
float - float -> float
float * float -> float
float / float -> float
float % float -> float
float ** float -> float

// Comparison
float == float -> bool
float != float -> bool
float < float -> bool
float > float -> bool
float <= float -> bool
float >= float -> bool

// Conversion
float -> string (explicit: string(3.14))
float -> int   (explicit: int(3.14), truncates)
float -> bool   (explicit: bool(3.14), 0.0=false, else=true)
```

### Bool

```
Type: bool
Size: 1 byte (stored as integer internally)
Values: yego (true), oya (false)
Default value: oya
```

**Operations:**
```
// Logical
bool kandi bool -> bool    (AND)
bool cyangwa bool -> bool  (OR)
si bool -> bool            (NOT)

// Comparison
bool == bool -> bool
bool != bool -> bool

// Conversion
bool -> int   (explicit: int(yego) = 1, int(oya) = 0)
bool -> string (explicit: string(yego) = "yego")
```

### String

```
Type: string
Encoding: UTF-8 (variable length)
Default value: ""
Literal syntax: "Muraho", "Hello\nWorld", r"raw"
```

**Operations:**
```
// Concatenation
string + string -> string

// Repetition
string * int -> string
int * string -> string

// Comparison
string == string -> bool
string != string -> bool

// Indexing
string[int] -> char

// Length
string.length -> int

// Methods (built-in)
string.substring(start: int, end: int) -> string
string.toUpperCase() -> string
string.toLowerCase() -> string
string.trim() -> string
string.startsWith(prefix: string) -> bool
string.endsWith(suffix: string) -> bool
string.contains(substring: string) -> bool
string.split(delimiter: string) -> List<string>
string.indexOf(substring: string) -> int
string.replace(old: string, new: string) -> string

// Conversion
string -> int   (explicit: int("42"), may fail)
string -> float (explicit: float("3.14"), may fail)
string -> char  (explicit: char("a"), must be length 1)
string -> bytes (explicit: bytes("hello"))
```

### Char

```
Type: char
Size: 1 Unicode codepoint (1-4 bytes)
Default value: '\0'
Literal syntax: 'a', 'ñ', '\n', '\u00E9'
```

**Operations:**
```
// Comparison
char == char -> bool
char != char -> bool

// Conversion
char -> int   (explicit: int('a') = 97)
char -> string (explicit: string('a') = "a")
char -> float (explicit: float('a'))
```

### Null

```
Type: null
Values: ubusa (null), null (English alias)
Default value: null
```

**Operations:**
```
// Equality
null == null -> true
null != value -> true
value != null -> true
```

## Composite Types

### List<T>

```
Type: List<T> (generic, parameterized by element type)
Default value: [] (empty list)
Literal syntax: [1, 2, 3], ["a", "b"]
```

**Operations:**
```
// Access
List<T>[int] -> T
List<T>.length -> int

// Modification (mutable)
List<T>.add(element: T) -> void
List<T>.insert(index: int, element: T) -> void
List<T>.remove(index: int) -> T
List<T>.remove(element: T) -> bool

// Search
List<T>.contains(element: T) -> bool
List<T>.indexOf(element: T) -> int
List<T>.find(predicate: (T) -> bool) -> T?

// Transformation
List<T>.map(fn: (T) -> U) -> List<U>
List<T>.filter(fn: (T) -> bool) -> List<T>
List<T>.reduce(fn: (T, U) -> U, initial: U) -> U
List<T>.forEach(fn: (T) -> void) -> void

// Slicing
List<T>.slice(start: int, end: int) -> List<T>
List<T>.sublist(start: int, length: int) -> List<T>

// Sorting
List<T>.sort(comparator: (T, T) -> int) -> List<T>
List<T>.sorted() -> List<T>
```

### Dict<K, V>

```
Type: Dict<K, V> (generic, parameterized by key and value types)
Default value: {} (empty dict)
Literal syntax: {name: "Jean", age: 25}
```

**Operations:**
```
// Access
Dict<K, V>[key: K] -> V?
Dict<K, V>.get(key: K, default: V) -> V
Dict<K, V>.containsKey(key: K) -> bool
Dict<K, V>.length -> int

// Modification
Dict<K, V>.set(key: K, value: V) -> void
Dict<K, V>.remove(key: K) -> bool
Dict<K, V>.clear() -> void

// Iteration
Dict<K, V>.keys() -> List<K>
Dict<K, V>.values() -> List<V>
Dict<K, V>.entries() -> List<(K, V)>
Dict<K, V>.forEach(fn: (K, V) -> void) -> void

// Transformation
Dict<K, V>.map(fn: (K, V) -> (K2, V2)) -> Dict<K2, V2>
Dict<K, V>.filter(fn: (K, V) -> bool) -> Dict<K, V>
```

### Set<T>

```
Type: Set<T> (generic, parameterized by element type)
Default value: {} (empty set)
Literal syntax: {1, 2, 3}
```

**Operations:**
```
// Access
Set<T>.contains(element: T) -> bool
Set<T>.length -> int

// Modification
Set<T>.add(element: T) -> void
Set<T>.remove(element: T) -> bool
Set<T>.clear() -> void

// Set operations
Set<T>.union(other: Set<T>) -> Set<T>
Set<T>.intersection(other: Set<T>) -> Set<T>
Set<T>.difference(other: Set<T>) -> Set<T>
Set<T>.isSubsetOf(other: Set<T>) -> bool
Set<T>.isSupersetOf(other: Set<T>) -> bool

// Iteration
Set<T>.forEach(fn: (T) -> void) -> void
Set<T>.toList() -> List<T>
```

### Tuple<T1, T2, ...>

```
Type: Tuple<T1, T2, ...> (fixed-size, heterogeneous)
Default value: N/A (must be explicitly constructed)
Literal syntax: (1, "hello", yego)
```

**Operations:**
```
// Access (by index, compile-time known)
Tuple<T1, T2>[int] -> T1 or T2

// Length
Tuple<...>.length -> int (compile-time constant)

// Unpacking
(a, b, c) = tuple
```

## User-Defined Types

### Struct Types

```
igiceri Person
    izina: string
    imyaka: int
    email: string = ""
iherezo
```

Creates type `Person` with:
- Fields: `izina` (string), `imyaka` (int), `email` (string, default "")
- Auto-generated constructor: `Person.nshya(izina: string, imyaka: int) -> Person`
- Auto-generated string representation

### Class Types

```
urwego Animal
    izina: string
    
    umurimo speak() -> string
        subira "Sound"
    iherezo
iherezo
```

Creates type `Animal` with:
- Field: `izina` (string)
- Method: `speak()` -> string
- Virtual dispatch support

### Enum Types

```
ikindi Color
    Red
    Green
    Blue
iherezo
```

Creates type `Color` with variants:
- `Color.Red`
- `Color.Green`
- `Color.Blue`

### Trait Types

```
urubingo Drawable
    umurimo draw() -> void
    umurimo bounds() -> (int, int, int, int)
iherezo
```

Creates type `Drawable` with method signatures (no implementation).

### Type Aliases

```
type UserId = int
type Callback = (string) -> void
```

Creates type aliases:
- `UserId` is equivalent to `int`
- `Callback` is equivalent to `(string) -> void`

## Type Annotations

### Syntax

```
// Variable annotation
shyira x: int = 10
shyira name: string = "Jean"
shyira numbers: List<int> = [1, 2, 3]

// Function parameter annotation
umurimo add(a: int, b: int) -> int
    subira a + b
iherezo

// Return type annotation
umurimo get_name() -> string
    subira "Jean"
iherezo

// No return type (void)
umurimo print_name(name: string)
    andika name
iherezo
```

### Annotation Rules

1. **Required when**: Type cannot be inferred from context
2. **Optional when**: Type is clear from initializer or return type
3. **Not allowed on**: Lambda parameters (inferred from context)

## Type Inference

### Inference Rules

The type checker infers types using these rules:

#### Variable Inference

```
shyira x = 10              // x: int (inferred from literal)
shyira name = "Jean"       // name: string (inferred from literal)
shyira list = [1, 2, 3]   // list: List<int> (inferred from elements)
shyira y = x               // y: int (inferred from x)
```

#### Expression Inference

```
// Binary expressions
int + int -> int
float + float -> float
int + float -> float (implicit promotion)
string + string -> string
bool kandi bool -> bool

// Function call
// Return type of called function determines type

// Member access
// Type of member determines type

// Index
// Element type of container determines type
```

#### Return Type Inference

```
// For functions without return type annotation
umurimo add(a: int, b: int)  // No annotation
    subira a + b              // Return type inferred as int
iherezo
```

### Type Inference Algorithm

The type checker uses unification-based type inference:

```
function inferType(expr: Expression, env: TypeEnvironment) -> Type:
    match expr:
        case LiteralExpr:
            return literalType(expr.value)

        case IdentifierExpr:
            symbol = env.lookup(expr.name)
            if symbol.type != null:
                return symbol.type
            return INFERRED_ERROR

        case BinaryExpr:
            left_type = inferType(expr.left, env)
            right_type = inferType(expr.right, env)
            return inferBinaryResult(left_type, expr.operator, right_type)

        case CallExpr:
            callee_type = inferType(expr.callee, env)
            if callee_type is FunctionType:
                // Check argument types against parameter types
                for i, arg in enumerate(expr.arguments):
                    arg_type = inferType(arg, env)
                    unify(arg_type, callee_type.parameters[i])
                return callee_type.return_type

        case IfExpr:
            then_type = inferType(expr.then_expr, env)
            else_type = inferType(expr.else_expr, env)
            return unify(then_type, else_type)
```

### Hindley-Milner Extensions

The I type system extends Hindley-Milner with:

1. **Bounded polymorphism**: Generic type constraints
2. **Row polymorphism**: For struct field access
3. **Subtyping**: For class inheritance
4. **Linear types**: (future) For resource management

## Type Checking Rules

### Binary Expression Rules

| Left | Operator | Right | Result |
|------|----------|-------|--------|
| int | +, -, *, /, % | int | int |
| float | +, -, *, /, % | float | float |
| int | +, -, *, /, % | float | float |
| float | +, -, *, /, % | int | float |
| string | + | string | string |
| string | * | int | string |
| int | * | string | string |
| bool | kandi, cyangwa | bool | bool |
| int | ==, !=, <, >, <=, >= | int | bool |
| float | ==, !=, <, >, <=, >= | float | bool |
| string | ==, != | string | bool |
| T | ==, != | T | bool |

### Unary Expression Rules

| Operator | Operand | Result |
|----------|---------|--------|
| - | int | int |
| - | float | float |
| si | bool | bool |
| ~ | int | int |
| ++ | int | int |
| -- | int | int |

### Assignment Rules

```
// Target must be assignable (lvalue)
x = expr        // x must be a variable
arr[i] = expr   // arr must be a list
obj.field = expr // obj must be a struct/class

// Value type must be compatible with target type
x: int = 10     // OK
x: int = "hi"   // Error: TYP001
```

### Function Call Rules

```
// Number of arguments must match
add(1, 2)       // OK if add has 2 parameters
add(1)          // Error: TYP002 "Expected 2 arguments, got 1"

// Argument types must be compatible
add(1, 2)       // OK if add(a: int, b: int)
add("a", "b")   // Error: TYP003 "Expected int, got string"
```

### Return Type Rules

```
// Return type must match declared type
umurimo add(a: int, b: int) -> int
    subira a + b      // OK: int matches int
    subira "hello"    // Error: TYP004 "Expected int, got string"
iherezo
```

## Generic Types

### Generic Type Declaration

```
igiceri Box<T>
    value: T
    is_empty: bool = yego
iherezo
```

### Generic Type Usage

```
shyira int_box: Box<int> = Box.nshya(42)
shyira string_box: Box<string> = Box.nshya("Hello")
```

### Type Parameter Constraints

```
urubingo Comparable<T>
    umurimo compare_to(other: T) -> int
iherezo

igiceri SortedList<T kugira Comparable<T>>
    items: List<T>
iherezo
```

### Generic Inference

```
// Type parameters can be inferred
shyira box = Box.nshya(42)  // inferred as Box<int>
```

### Multiple Type Parameters

```
igiceri Pair<A, B>
    first: A
    second: B
iherezo

shyira pair = Pair.nshya(1, "hello")  // Pair<int, string>
```

## Union Types

### Union Type Syntax

```
shyira value: int | string = 42
value = "hello"  // OK
value = 3.14     // Error: float not in union
```

### Union Type Checking

When operating on a union type, the operation must be valid for all member types:

```
shyira x: int | string = 42
x + 1           // OK: int + int works
x + "hello"     // Error: int + string doesn't work for all types
```

### Pattern Matching on Unions

```
match value:
    case int => andika("Number: " + string(value))
    case string => andika("String: " + value)
```

## Optional Types

### Optional Type Syntax

```
shyira name: string? = null
name = "Jean"  // OK
name = null     // OK
```

### Null Safety

Accessing an optional type requires null checking:

```
// Error: TYP005 "Cannot access member of optional type"
// name.length

// Required: null check first
niba name != null:
    andika(name.length)
iherezo

// Or use optional chaining (future)
// name?.length
```

### Optional Type Rules

```
// Unwrap with null check
T? -> T (after null check)

// Optional propagation
(T?)? -> T?

// Function parameters
umurimo greet(name: string?) -> string
    niba name == null:
        subira "Hello, World!"
    subira "Hello, " + name!
iherezo
```

## Function Types

### Function Type Syntax

```
type Callback = (int, string) -> bool
type Mapper = (T) -> U
type Predicate = (T) -> bool
```

### Function Type Checking

```
// Function type compatibility
f: (int, string) -> bool

// Compatible functions:
g: (int, string) -> bool      // Exact match
h: (int, string) -> bool      // Exact match

// Incompatible functions:
i: (int) -> bool              // Wrong parameter count
j: (int, string) -> int      // Wrong return type
k: (string, string) -> bool  // Wrong parameter types
```

### Higher-Order Functions

```
// Functions as parameters
umurimo apply(f: (int) -> int, x: int) -> int
    subira f(x)
iherezo

// Functions as return values
umurimo make_adder(n: int) -> (int) -> int
    subira (x: int) -> int => x + n
iherezo
```

## Type Compatibility

### Subtyping Rules

```
// Class inheritance
urwego Animal ...
urwego Dog kugira Animal ...

// Dog is a subtype of Animal
shyira a: Animal = gukora Dog(...)  // OK
shyira d: Dog = gukora Animal(...)  // Error
```

### Covariance and Contravariance

```
// Lists are invariant by default
List<Dog> is NOT a subtype of List<Animal>

// Function parameters are contravariant
(Animal) -> void IS a subtype of (Dog) -> void

// Function return types are covariant
() -> Dog IS a subtype of () -> Animal
```

### Type Compatibility Matrix

| From | To | Compatible? |
|------|----|-------------|
| int | float | Yes (implicit) |
| float | int | No (explicit only) |
| int | string | No (explicit only) |
| string | int | No (explicit only) |
| Dog | Animal | Yes (subtyping) |
| Animal | Dog | No (downcasting) |
| null | T? | Yes |
| T | T? | Yes (lift) |
| T? | T | No (must unwrap) |

## Type Coercion

### Implicit Coercions

| From | To | Rule |
|------|----|------|
| int | float | Widening, always safe |
| int | string | Never implicit |
| bool | int | Never implicit |
| T | T? | Lifting, always safe |
| Dog | Animal | Subtyping |

### Explicit Conversions

| From | To | Syntax |
|------|----|--------|
| int | float | `float(x)` |
| float | int | `int(x)` (truncates) |
| int | string | `string(x)` |
| string | int | `int(x)` (may fail) |
| T | T? | `x` (implicit) |
| T? | T | `x!` (force unwrap, may fail at runtime) |

## Type Errors

### Error Types

| Code | Name | Description |
|------|------|-------------|
| TYP001 | Type Mismatch | Expression type doesn't match expected type |
| TYP002 | Argument Count | Wrong number of arguments to function |
| TYP003 | Argument Type | Argument type doesn't match parameter type |
| TYP004 | Return Type | Return type doesn't match declared type |
| TYP005 | Optional Access | Accessing member of optional type without null check |
| TYP006 | Undefined Member | Member doesn't exist on type |
| TYP007 | Not Callable | Expression is not callable |
| TYP008 | Not Indexable | Expression is not indexable |
| TYP009 | Not Iterable | Expression is not iterable |
| TYP010 | Generic Error | Generic type constraint not satisfied |
| TYP011 | Union Error | Operation not valid for all union members |
| TYP012 | Inference Failed | Type inference failed |
| TYP013 | Circular Type | Circular type definition |
| TYP014 | Abstract Type | Cannot instantiate abstract type |

### Error Messages

Each error includes:

1. **Error code**: TYP001-TYP099
2. **Title**: Short description
3. **Message**: Detailed explanation in English and Kinyarwanda
4. **Location**: Source file, line, column
5. **Snippet**: Source code context
6. **Expected vs. Actual**: What was expected and what was found
7. **Suggestion**: How to fix the error

Example:

```
Error TYP001: Type Mismatch
  | Expected: int
  | Actual: string
  |
  | 4: shyira x: int = "hello"
  |                      ^^^^^^^
  |
  | Suggestion: Remove the quotes to create an integer literal,
  |             or change the type annotation to string.
  |
  | Inyandiko: Ubuhungane bw'ubwoko
  |   Ibisobanuro: int, ariko byabonetse string
```

## Performance

### Type Checking Complexity

- **Type inference**: O(n) for most programs
- **Unification**: O(n * α(n)) with union-find (nearly linear)
- **Generic instantiation**: O(n * g) where g is the number of generic types
- **Overall**: O(n) for typical programs

### Type Representation

```
Type {
    id: int                    // Unique type ID
    kind: TypeKind            // Type category
    data: TypeData            // Type-specific data
    hash: int                 // Cached hash for set/map operations
}
```

### Type Caching

- **Interned types**: Primitive types are interned
- **Canonical forms**: Generic types are canonicalized
- **Memoization**: Type inference results are memoized

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
