# I Programming Language Specification

Version 0.1.0 - Draft

## Table of Contents

1. [Introduction](#introduction)
2. [Lexical Structure](#lexical-structure)
3. [Syntax](#syntax)
4. [Types](#types)
5. [Expressions](#expressions)
6. [Statements](#statements)
7. [Control Flow](#control-flow)
8. [Functions](#functions)
9. [Modules](#modules)
10. [Error Handling](#error-handling)
11. [Concurrency](#concurrency)
12. [Memory Management](#memory-management)

## Introduction

The I Programming Language is designed around Kinyarwanda syntax while maintaining suitability for professional software development. This specification defines the language's syntax, semantics, and type system.

### Design Goals

- **Readable**: Code should read like natural Kinyarwanda
- **Natural**: Syntax should feel intuitive to Kinyarwanda speakers
- **Simple**: Minimal complexity, maximum clarity
- **Consistent**: Uniform patterns throughout
- **Powerful**: Capable of building any software system
- **Fast**: High-performance execution
- **Safe**: Memory safety and type safety by default
- **Modern**: Contemporary features and best practices
- **Professional**: Suitable for enterprise-grade applications
- **Self Hosting**: Eventually written in I itself

### Core Principles

1. **Words over punctuation**: Use Kinyarwanda words instead of symbols
2. **Keyword-driven statements**: Every statement begins with a keyword
3. **Explicit block endings**: Every block ends with `iherezo`
4. **Type safety**: Static typing with type inference
5. **Memory safety**: No null pointer exceptions, no buffer overflows

## Lexical Structure

### Source Code Encoding

Source files are encoded in UTF-8.

### Whitespace

Spaces, tabs, and newlines are used for separation. Indentation is not significant.

### Comments

```i
# Single line comment
# This is a comment

#=
Multi-line comment
Spans multiple lines
=#
```

### Identifiers

Identifiers start with a letter or underscore, followed by letters, digits, or underscores.

```i
umuntu
my_variable
_x
counter123
```

### Keywords

Reserved words in I:

```
niba - if
cyangwa - else
kugenda - continue
gukoma - break
subira - return
tanga - yield
kora - do
wihuse - while
kugeza - until
kuri - for
muri - in
buri - each
shyira - let
shyira_ko - const
umurimo - function
igiceri - struct
ikindi - enum
urwego - class
akabuto - interface
urubingo - trait
kugira - have
gukora - make
shyiramo - import
tanga - export
kugira_ngo - as
kandi - and
cyangwa - or
bitewe - because
ari - is
si - not
kugira - have
gushyingura - throw
kubika - catch
ikinyoma - finally
iherezo - end
```

### Literals

#### Integer Literals

```i
42
-10
1_000_000
0xFF   # hexadecimal
0o77   # octal
0b101  # binary
```

#### Floating-Point Literals

```i
3.14
-0.001
1.0e10
2.5e-3
```

#### String Literals

```i
"Muraho"
"Imyirondoro"
```

#### Character Literals

```i
'A'
'ñ'
'ἀ'
```

#### Boolean Literals

```i
yego   # true
oya    # false
```

#### Null Literal

```i
ubusa  # null
```

### Operators

#### Comparison Operators

```i
irenze      # >
munsi_ya    # <
iringaniye  # ==
nta_iringani # !=
irenze_cyangwa_aringana # >=
munsi_ya_cyangwa_aringana # <=
```

#### Logical Operators

```i
kandi   # and
cyangwa # or
si      # not
```

#### Arithmetic Operators

```i
+      # addition
-      # subtraction
*      # multiplication
/      # division
%      # modulo
**     # exponentiation
```

#### Bitwise Operators

```i
&      # bitwise and
|      # bitwise or
^      # bitwise xor
~      # bitwise not
<<     # left shift
>>     # right shift
```

#### Assignment Operators

```i
=      # assignment
+=     # add and assign
-=     # subtract and assign
*=     # multiply and assign
/=     # divide and assign
%=     # modulo and assign
```

## Syntax

### Program Structure

A program consists of one or more modules:

```i
shyiramo stdlib.io
shyiramo stdlib.math

umurimo kora_ikintu()
    # function body
iherezo

umurimo main()
    kora_ikintu()
iherezo
```

### Variable Declarations

#### Mutable Variables

```i
shyira umuntu = "Jean"
shyira umunyarwanda = 25
```

#### Immutable Variables

```i
shyira_ko PI = 3.14159
shyira_ko IGIHUGU = "Rwanda"
```

#### Type Annotations

```i
shyira umuntu: Umuntu = Umuntu.nshya("Jean")
shyira umunyarwanda: int = 25
```

### Type System

#### Primitive Types

```i
int      # signed integer
float    # floating-point number
bool     # boolean
umuntu   # string (person/character)
bbyte    # byte
```

#### Composite Types

```i
urutonde # list
ikarita  # map/dictionary
tandukanya # tuple
gutoranya # set
```

#### User-Defined Types

```i
igiceri Umuntu
    izina: umuntu
    imyaka: int
iherezo

ikindi Ubwoko
    A
    B
    C(int)
iherezo
```

## Expressions

### Literal Expressions

```i
42
3.14
"Muraho"
yego
```

### Variable Expressions

```i
umuntu
imyaka
```

### Binary Expressions

```i
a + b
a * b
a irenze b
a kandi b
```

### Unary Expressions

```i
-a
si a
```

### Call Expressions

```i
umurimo()
umurimo(arg1, arg2)
```

### Member Access

```i
umuntu.izina
umuntu.imyaka
```

### Index Expressions

```i
urutonde[0]
ikarita["ubutso"]
```

### Slice Expressions

```i
urutonde[0:5]
urutonde[:5]
urutonde[0:]
urutonde[:]
```

## Statements

### Expression Statement

```i
umurimo()
a + b
```

### Declaration Statement

```i
shyira x = 10
shyira_ko y = 20
```

### Assignment Statement

```i
x = 20
umuntu.izina = "Marie"
```

### Block Statement

```i
shyira x = 10
    shyira y = 20
    andika x + y
iherezo
```

## Control Flow

### Conditional Statement

```i
niba a irenze 5
    andika "A ni kure"
iherezo
```

### If-Else Statement

```i
niba a irenze 5
    andika "A ni kure"
cyangwa
    andika "A si kure"
iherezo
```

### If-Elif-Else Statement

```i
niba a irenze 10
    andika "A ni binini"
cyangwa_niba a irenze 5
    andika "A ni hagati"
cyangwa
    andika "A ni gitoya"
iherezo
```

### While Loop

```i
shyira i = 0
wihuse i munsi 10
    andika i
    i = i + 1
iherezo
```

### Until Loop

```i
shyira i = 0
kugeza i aringaniye 10
    andika i
    i = i + 1
iherezo
```

### For Loop

```i
kuri i muri 0 kugeza 10
    andika i
iherezo
```

### For Each Loop

```i
buri element muri urutonde
    andika element
iherezo
```

### Break Statement

```i
wihuse yego
    niba condition
        gukoma
    iherezo
iherezo
```

### Continue Statement

```i
buri x muri urutonde
    niba x aringaniye 5
        kugenda
    iherezo
    andika x
iherezo
```

## Functions

### Function Declaration

```i
umurimo sagura(a: int, b: int) -> int
    subira a + b
iherezo
```

### Function Call

```i
sagura(2, 3)
```

### Anonymous Functions

```i
shyira f = umurimo(x: int) -> int
    subira x * 2
iherezo
```

### Higher-Order Functions

```i
umurimo shira_umurimo(f: umurimo(int) -> int, x: int) -> int
    subira f(x)
iherezo
```

### Closures

```i
umurimo bika_umbuto(x: int) -> umurimo() -> int
    subira umurimo() -> int
        subira x
    iherezo
iherezo
```

## Modules

### Import Statement

```i
shyiramo stdlib.io
shyiramo stdlib.math kugira_ngo math
shyiramo stdlib.collections.urutonde
```

### Export Statement

```i
tanga umurimo sagura
tanga igiceri Umuntu
```

### Module Structure

```i
# module.i
shyiramo stdlib.io

igiceri Umuntu
    izina: umuntu
iherezo

umurimo kora()
    # implementation
iherezo

tanga Umuntu
tanga kora
```

## Error Handling

### Try-Catch Statement

```i
kora
    # code that might throw
    gushyingura Ikosa("ibyago byabaye")
kubika e kugira Ikosa
    andika e.ubutumwa
iherezo
```

### Try-Catch-Finally Statement

```i
kora
    gushyingura Ikosa("ibyago byabaye")
kubika e kugira Ikosa
    andika e.ubutumwa
ikinyoma
    andika "byose byarangiye"
iherezo
```

### Throw Statement

```i
gushyingura Ikosa("ibyago byabaye")
```

### Custom Error Types

```i
igiceri Ikosa
    ubutumwa: umuntu
iherezo
```

## Concurrency

### Goroutines (Lightweight Threads)

```i
umurimo kora()
    andika "akazi"
iherezo

kora kora()
```

### Channels

```i
shyira ch = gutoranya(int)

kora umurimo()
    ch <- 42
iherezo

shyira x = <-ch
```

### Select Statement

```i
shira
x = <-ch1:
    andika "received from ch1"
x = <-ch2:
    andika "received from ch2"
iherezo
```

### Mutex

```i
shyira m = gutoranya()

m.gukora()
# critical section
m.gusohoka()
```

## Memory Management

### Stack Allocation

Local variables are allocated on the stack:

```i
umurimo kora()
    shyira x = 10  # stack allocated
iherezo
```

### Heap Allocation

Objects are allocated on the heap:

```i
shyira umuntu = Umuntu.nshya("Jean")  # heap allocated
```

### Garbage Collection

The language uses automatic garbage collection. No manual memory management is required.

### Ownership and Borrowing

For systems programming, I provides optional ownership semantics:

```i
shyira data = gutoranya([1, 2, 3])
shyira borrowed = &data  # borrow
shyira owned = data      # move
```

## Standard Library

### Core Modules

- `stdlib.io` - Input/output operations
- `stdlib.math` - Mathematical functions
- `stdlib.collections` - Data structures
- `stdlib.strings` - String operations
- `stdlib.files` - File system operations
- `stdlib.network` - Networking
- `stdlib.concurrency` - Concurrency primitives
- `stdlib.time` - Time and date operations

## Examples

### Hello World

```i
umurimo main()
    andika "Muraho, Isi!"
iherezo
```

### Fibonacci

```i
umurimo fibonacci(n: int) -> int
    niba n munsi_ya 2
        subira n
    iherezo
    subira fibonacci(n - 1) + fibonacci(n - 2)
iherezo

umurimo main()
    buri i muri 0 kugeza 10
        andika fibonacci(i)
    iherezo
iherezo
```

### Struct Usage

```i
igiceri Umuntu
    izina: umuntu
    imyaka: int
iherezo

umurimo main()
    shyira umuntu = Umuntu.nshya("Jean", 25)
    andika umuntu.izina
    andika umuntu.imyaka
iherezo
```

### List Operations

```i
umurimo main()
    shyira numbers = gutoranya([1, 2, 3, 4, 5])
    
    buri n muri numbers
        niba n irenze 3
            andika n
        iherezo
    iherezo
iherezo
```

## Grammar (EBNF)

```
program       = { module }
module        = { import_stmt } { decl }
import_stmt   = "shyiramo" identifier [ "kugira_ngo" identifier ]
decl          = var_decl | func_decl | struct_decl | enum_decl
var_decl      = "shyira" identifier [ ":" type ] "=" expr
              | "shyira_ko" identifier [ ":" type ] "=" expr
func_decl     = "umurimo" identifier "(" [ param_list ] ")" [ "->" type ] block
struct_decl   = "igiceri" identifier "{" { field_decl } "}"
enum_decl     = "ikindi" identifier "{" { enum_variant } "}"
block         = { stmt } "iherezo"
stmt          = expr_stmt | if_stmt | while_stmt | for_stmt | return_stmt
if_stmt       = "niba" expr block [ "cyangwa" block ]
while_stmt    = "wihuse" expr block
for_stmt      = "kuri" identifier "muri" expr "kugeza" expr block
return_stmt   = "subira" [ expr ]
expr          = logical_expr
logical_expr  = comparison_expr { ("kandi" | "cyangwa") comparison_expr }
comparison_expr = additive_expr { comparison_op additive_expr }
additive_expr = multiplicative_expr { ("+" | "-") multiplicative_expr }
multiplicative_expr = unary_expr { ("*" | "/" | "%") unary_expr }
unary_expr    = [ "si" | "-" ] primary_expr
primary_expr  = literal | identifier | func_call | "(" expr ")"
```

## Implementation Notes

### Compiler Architecture

The I compiler consists of:

1. **Lexer** - Tokenizes source code
2. **Parser** - Builds abstract syntax tree
3. **Semantic Analyzer** - Type checking and validation
4. **Optimizer** - Code optimization
5. **Code Generator** - Bytecode generation
6. **Native Compiler** - Machine code generation

### Virtual Machine

The I VM executes bytecode with:

- Stack-based execution
- Garbage collection
- JIT compilation (optional)
- Native FFI

### Self-Hosting Goal

The ultimate goal is to rewrite the compiler in I itself, achieving self-hosting capability.

---

This specification is a living document and will evolve as the language develops.
