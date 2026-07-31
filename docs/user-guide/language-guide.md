# I Language Guide

This guide documents the **I** programming language as implemented in version **1.0.0**.
Every construct shown here compiles and runs with the released toolchain. Constructs
that appear in design documents but are not yet implemented are listed in
[Known Limitations](#known-limitations) at the end.

## Syntax at a Glance

I uses Kinyarwanda words instead of punctuation for structure. A block is opened by an
indented body and closed with `iherezo` (*end*).

```i
# a comment
shyira izina = "Jean"              # variable
shyira_ko IMIYAKA = 25             # constant

umurimo komeza(x: int) -> int      # function
    subira x + 1
iherezo

niba izina == "Jean"               # conditional
    andika komeza(IMIYAKA)
cyangwa
    andika "Other"
iherezo
```

## Comments

Comments start with `#` and run to the end of the line.

```i
# this is a comment
shyira x = 1  # trailing comments are fine too
```

## Values and Types

| Type | Example literals | `ubwoko(...)` returns |
| --- | --- | --- |
| Integer | `42`, `-7`, `0` | `int` |
| Float | `3.14`, `-0.5`, `2.0` | `float` |
| String | `"Muraho"`, `"a" + "b"` | `str` |
| Boolean | `true`, `false` | `bool` |
| Null | `null` | `null` |
| List | `[1, 2, 3]`, `["a", "b"]` | `urutonde` |

Strings use double quotes. String concatenation uses `+`:

```i
andika "Rwanda" + "!"        # Rwanda!
```

Booleans are the English words `true` and `false` (they print as `True` / `False`).

## Variables

### Mutable variables — `shyira`

```i
shyira izina = "Jean"
izina = "Aline"     # reassignment
```

### Constants — `shyira_ko`

```i
shyira_ko PI = 3.14159
shyira_ko IGIHUGU = "Rwanda"
```

Constants are conventionally written in UPPERCASE. Reassigning a constant is a
semantic error.

### Type annotations

Function parameters and return types are annotated with `: type` and `-> type`.
Variables may carry type annotations as well:

```i
umurimo sagura(a: int, b: int) -> int
    subira a + b
iherezo
```

The basic types are `int`, `float`, `string`, `bool`, and `null`.

## Operators

### Arithmetic

```i
+   -   *   /   %
```

```i
shyira a = 10
shyira b = 3
andika a / b    # 3.333... (floating division)
andika a % b    # 1
```

### Comparison

Symbol operators and Kinyarwanda words are both supported:

```i
==  !=  >  <  >=  <=
```

```i
irenze    # greater than  (>)
munsi     # less than     (<)
munsi_ya  # less than     (<)
```

```i
shyira x = 5
andika x irenze 3     # True
andika x munsi 3      # False
andika x munsi_ya 10  # True
andika x >= 5         # True
```

`===` and `!==` are accepted as aliases for `==` and `!=`.

### Bitwise

```i
&   |   ^   <<   >>
```

```i
andika 5 & 3     # 1
andika 5 | 3     # 7
andika 1 << 4    # 16
```

### Unary

```i
-    !    si
```

```i
shyira a = 5
andika -a        # -5
andika !true     # False
andika si true   # False
```

> **Note:** `si` is the Kinyarwanda word for *not*.

### Compound conditions

To combine conditions, nest `niba` blocks. The logical operators `kandi`, `cyangwa`,
`&&`, `||`, `and`, and `or` are **not** available in 1.0.0 (see
[Known Limitations](#known-limitations)).

```i
niba x irenze 0
    niba x munsi_ya 100
        andika "between 0 and 100"
    iherezo
iherezo
```

## Control Flow

### If / else if / else

```i
niba x irenze 20
    andika "large"
cyangwa_niba x irenze 10
    andika "medium"
cyangwa
    andika "small"
iherezo
```

The closing `iherezo` is optional on each branch but required for the statement as a
whole in practice — always write it.

### While — `wihuse`

```i
shyira i = 0
wihuse i munsi 5
    andika i
    i = i + 1
iherezo
```

> **Note:** `gukoma` (*break*) does **not** work reliably inside `wihuse` loops in
> 1.0.0 and can cause an infinite loop. Prefer `kuri` loops when you need to break.

### Until (do-while) — `kugeza`

`kugeza` runs the body first and then checks the condition:

```i
shyira n = 0
kugeza n >= 5
    n = n + 1
iherezo
andika n    # 5 — the body always runs at least once
```

### For — `kuri ... muri ... kugeza ...`

```i
kuri i muri 0 kugeza 5
    andika i
iherezo
```

Prints `0 1 2 3 4`. The end value is **exclusive**. The loop variable is scoped to the
loop body.

Break out of a `kuri` loop with `gukoma`:

```i
kuri i muri 0 kugeza 10
    niba i == 3
        gukoma
    iherezo
    andika i
iherezo
# prints 0 1 2
```

> **Note:** `kugenda` (*continue*) is not reliable in 1.0.0 (it jumps before the loop
> variable is updated). Use `niba` guards instead.

### For each — `buri ... muri ...`

```i
shyira totals = [10, 20, 30]
buri n muri totals
    andika n
iherezo
```

## Functions

### Definition

```i
umurimo name(param: type, ...) -> type
    ...
iherezo
```

### Return — `subira`

```i
umurimo sagura(a: int, b: int) -> int
    subira a + b
iherezo

andika sagura(5, 3)    # 8
```

### Recursion

Functions may call themselves:

```i
umurimo fibonacci(n: int) -> int
    niba n munsi_ya 2
        subira n
    iherezo
    subira fibonacci(n - 1) + fibonacci(n - 2)
iherezo

kuri i muri 0 kugeza 10
    andika fibonacci(i)
iherezo
```

### Multiple statements

```i
umurimo kora_ikintu(x: int, y: int) -> int
    shyira result = x * y
    subira result + 10
iherezo
```

## Collections

### Lists

```i
shyira numbers = [1, 2, 3, 4, 5]
```

Indexing uses `[n]` with zero-based indices:

```i
andika numbers[0]     # 1
andika numbers[2]     # 3
```

Iterate with `buri`:

```i
shyira total = 0
buri n muri numbers
    total = total + n
iherezo
andika total          # 15
```

## Modules

Import a module with `shyiramo` (*include*). The module name is written **without
quotes**:

```i
shyiramo text
```

In 1.0.0 the importable standard-library modules and their exported function names are
declared in the semantic layer (`urubuga`, `text`, `math`, `string`, `list`, `io`,
`std`). Note that the runtime does not yet bind all exported names, so treat imports as
an early-access feature and rely on the builtins below for working programs.

## Built-in Functions

The runtime provides these built-in functions in every program:

| Function | Meaning | Example |
| --- | --- | --- |
| `andika(...)` | print (with newline) | `andika "Muraho"` |
| `soma()` | read a line from stdin | `shyira izina = soma()` |
| `ubwoko(...)` | type name of a value | `andika ubwoko(5)` → `int` |
| `uburengero(...)` | convert to integer | `andika uburengero("42")` → `42` |
| `shobora_int(...)` | convert to integer | `shobora_int(3.9)` |
| `shobora_float(...)` | convert to float | `shobora_float("2.5")` |
| `shobora_umuntu(...)` | convert to string | `shobora_umuntu(42)` |
| `shobora_bool(...)` | convert to boolean | `shobora_bool(0)` |

## Known Limitations (1.0.0)

These are documented so you do not hit them unexpectedly. They are tracked for the
next minor release.

- **Logical operators** `kandi`, `cyangwa`, `&&`, `||`, `and`, `or` are not yet
  implemented. Combine conditions with nested `niba` blocks.
- **`gukoma` (break)** works inside `kuri` / `buri` loops but not inside `wihuse`
  loops (can cause an infinite loop).
- **`kugenda` (continue)** is unreliable in all loops.
- **Structs, classes, enums, traits, interfaces** parse but cannot yet be
  instantiated at runtime (`Igiceri()` raises "not callable").
- **For-loop step** is parsed but ignored; the loop always increments by 1.
- **String / list methods** (`.upper()`, `.slice()`, `.push()`) are not yet
  implemented; use the `stdlib` Python modules from host code when needed.

## Grammar Summary

```
program       := statement*
statement     := comment | variable | constant | function | if | while
               | until | for | foreach | return | print | expression

variable      := "shyira" IDENTIFIER "=" expression
constant      := "shyira_ko" IDENTIFIER "=" expression
function      := "umurimo" IDENTIFIER "(" params? ")" ("->" type)? block
params        := IDENTIFIER ":" type ("," IDENTIFIER ":" type)*
if            := "niba" expression block
               ("cyangwa_niba" expression block)* ("cyangwa" block)?
while         := "wihuse" expression block
until         := "kugeza" expression block
for           := "kuri" IDENTIFIER "muri" expression "kugeza" expression block
foreach       := "buri" IDENTIFIER "muri" expression block
return        := "subira" expression?
print         := "andika" expression
block         := NEWLINE INDENT statement+ DEDENT "iherezo"
type          := "int" | "float" | "string" | "bool" | "null" | IDENTIFIER
```
