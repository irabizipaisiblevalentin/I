# I Programming Language Specification

This document specifies the syntax and semantics of the I programming language.

## Table of Contents

- [Introduction](#introduction)
- [Lexical Structure](#lexical-structure)
- [Syntax](#syntax)
- [Types](#types)
- [Expressions](#expressions)
- [Statements](#statements)
- [Functions](#functions)
- [Classes and Structs](#classes-and-structs)
- [Modules](#modules)
- [Error Handling](#error-handling)
- [Concurrency](#concurrency)
- [Memory Management](#memory-management)

## Introduction

The I programming language is designed around Kinyarwanda, prioritizing natural syntax while maintaining professional software development capabilities.

### Design Goals

1. **Natural Syntax**: Use Kinyarwanda words instead of punctuation
2. **Readability**: Code should read like natural language
3. **Consistency**: Uniform patterns throughout the language
4. **Safety**: Type safety and memory safety by default
5. **Performance**: Efficient execution
6. **Expressiveness**: Capable of expressing complex ideas clearly

## Lexical Structure

### Source Code Encoding

Source files are encoded in UTF-8 to support Kinyarwanda characters.

### Whitespace

Whitespace includes spaces, tabs, and newlines. Whitespace is generally insignificant except as a separator.

### Comments

#### Single-line Comments

```i
# This is a single-line comment
```

#### Multi-line Comments

```i
#=
This is a multi-line comment
that spans multiple lines
=#
```

### Identifiers

Identifiers start with a letter or underscore, followed by letters, digits, or underscores. Identifiers can contain Unicode characters to support Kinyarwanda.

```i
umuntu
my_variable
_underscore
kinyarwanda_word
```

### Keywords

Reserved words in the I language:

```i
niba          # if
cyangwa       # else
kugenda       # continue
gukoma        # break
subira        # return
tanga         # yield
kora          # do
wihuse        # while
kugeza        # until
kuri          # for
muri          # in
buri          # each
shyira        # let
shyira_ko     # const
umurimo       # function
igiceri       # struct
ikindi        # enum
urwego        # class
akabuto       # interface
urubingo      # trait
kugira        # have
gukora        # make
shyiramo      # import
tanga         # export
kugira_ngo    # as
kandi         # and
cyangwa       # or
bitewe        # because
ari           # is
si            # not
gushyingura   # throw
kubika        # catch
ikinyoma      # finally
iherezo       # end
```

### Literals

#### Integer Literals

```i
42
-10
1_000_000
```

#### Float Literals

```i
3.14
-0.001
1.0e10
```

#### String Literals

```i
"Muraho"
"Imyirondoro"
```

#### Character Literals

```i
'a'
'ñ'
'c'
```

#### Boolean Literals

```i
yego    # true
oya     # false
```

#### Null Literal

```i
ubusa   # null
```

### Operators

#### Arithmetic Operators

```i
+       # addition
-       # subtraction
*       # multiplication
/       # division
%       # modulo
**      # exponentiation
```

#### Comparison Operators

```i
>           # greater than (irenze)
<           # less than (munsi ya)
==          # equal (iringaniye)
!=          # not equal (nta_iringani)
>=          # greater than or equal (irenze_cyangwa_aringana)
<=          # less than or equal (munsi_ya_cyangwa_aringana)
```

#### Logical Operators

```i
kandi       # and
cyangwa     # or
si          # not
```

#### Assignment Operators

```i
=           # assignment
+=          # add and assign
-=          # subtract and assign
*=          # multiply and assign
/=          # divide and assign
%=          # modulo and assign
```

## Syntax

### Block Structure

Every block ends with `iherezo`:

```i
niba condition
    # block body
iherezo
```

### Statement Structure

Every statement begins with a keyword:

```i
shyira x = 10
andika "Hello"
niba x irenze 5
    andika x
iherezo
```

## Types

### Primitive Types

```i
int         # integer
float       # floating-point
bool        # boolean
string      # string
char        # character
null        # null type
```

### Composite Types

```i
list<T>     # list of type T
map<K, V>   # map from K to V
set<T>      # set of type T
tuple<T...> # tuple of types
```

### User-Defined Types

```i
igiceri Person
    izina: string
    imyaka: int
iherezo
```

### Type Annotations

```i
shyira x: int = 10
shyira name: string = "Jean"

umurimo add(a: int, b: int) -> int
    subira a + b
iherezo
```

## Expressions

### Literal Expressions

```i
42
3.14
"Muraho"
yego
oya
ubusa
```

### Variable Expressions

```i
x
my_variable
```

### Binary Expressions

```i
a + b
a - b
a * b
a / b
a % b
a ** b
```

### Comparison Expressions

```i
a irenze b          # a > b
a munsi ya b        # a < b
a iringaniye b      # a == b
a nta_iringani b    # a != b
```

### Logical Expressions

```i
a kandi b           # a and b
a cyangwa b         # a or b
si a                # not a
```

### Unary Expressions

```i
-a                  # negation
si a                # logical not
```

### Grouping Expressions

```i
(a + b) * c
```

### Call Expressions

```i
function_name(arg1, arg2)
```

### Member Access Expressions

```i
object.field
object.method()
```

### Index Expressions

```i
list[index]
map[key]
```

## Statements

### Variable Declaration

```i
shyira x = 10
shyira_ko PI = 3.14159
```

### Assignment

```i
x = 20
x += 5
```

### Expression Statement

```i
andika "Hello"
function_name()
```

### Block Statement

```i
kora
    shyira x = 10
    shyira y = 20
    andika x + y
iherezo
```

### If Statement

```i
niba condition
    # then block
iherezo

niba condition
    # then block
cyangwa
    # else block
iherezo

niba condition1
    # then block
cyangwa_niba condition2
    # elif block
cyangwa
    # else block
iherezo
```

### While Statement

```i
wihuse condition
    # loop body
iherezo
```

### Until Statement

```i
kugeza condition
    # loop body
iherezo
```

### For Statement

```i
kuri variable muri start kugeza end
    # loop body
iherezo
```

### For Each Statement

```i
buri element muri collection
    # loop body
iherezo
```

### Break Statement

```i
gukoma
```

### Continue Statement

```i
kugenda
```

### Return Statement

```i
subira value
subira
```

### Throw Statement

```i
gushyingura exception
```

### Try Statement

```i
kora
    # try block
kubika exception
    # catch block
ikinyoma
    # finally block
iherezo
```

## Functions

### Function Declaration

```i
umurimo function_name(param1: type1, param2: type2) -> return_type
    # function body
    subira result
iherezo
```

### Function Call

```i
function_name(arg1, arg2)
```

### Lambda Functions

```i
shyira add = (a: int, b: int) -> int => a + b
```

### Default Parameters

```i
umurimo greet(name: string, greeting: string = "Muraho") -> string
    subira greeting + ", " + name
iherezo
```

### Variadic Parameters

```i
umurimo sum(numbers: int...) -> int
    shyira total = 0
    buri n muri numbers
        total += n
    iherezo
    subira total
iherezo
```

## Classes and Structs

### Struct Declaration

```i
igiceri Person
    izina: string
    imyaka: int
iherezo
```

### Struct Instantiation

```i
shyira person = Person.nshya("Jean", 25)
```

### Struct Methods

```i
igiceri Person
    izina: string
    imyaka: int
    
    umurimo introduce() -> string
        subira "Muraho, ndi " + self.izina
    iherezo
iherezo
```

### Class Declaration

```i
urwego Animal
    izina: string
    
    umurimo speak() -> string
        subira "Sound"
    iherezo
iherezo
```

### Inheritance

```i
urwego Dog kugira Animal
    umurimo speak() -> string
        subira "Woof"
    iherezo
iherezo
```

### Interface Declaration

```i
akabuto Drawable
    umurimo draw() -> void
iherezo
```

### Trait Declaration

```i
urubingo Serializable
    umurimo serialize() -> string
    umurimo deserialize(data: string) -> void
iherezo
```

## Modules

### Import Statement

```i
shyiramo module_name
shyiramo module_name kugira_ngo alias
shyiramo module_name.function
shyiramo module_name.struct
```

### Export Statement

```i
tanga function_name
tanga struct_name
tanga *
```

## Error Handling

### Exception Types

```i
ikindi Error
ikindi ValueError
ikindi TypeError
ikindi RuntimeError
```

### Throw Statement

```i
gushyingura ValueError("Invalid value")
```

### Try-Catch Statement

```i
kora
    # code that might throw
kubika error
    # handle error
iherezo
```

### Finally Block

```i
kora
    # code that might throw
kubika error
    # handle error
ikinyoma
    # cleanup code
iherezo
```

## Concurrency

### Goroutines

```i
tanga_gikorwa function_name()
```

### Channels

```i
shyira channel = kora_channel()
kohereza channel, value
shyira value = akira channel
```

### Mutex

```i
shyira mutex = kora_mutex()
mutex.lock()
# critical section
mutex.unlock()
```

## Memory Management

### Automatic Memory Management

The I programming language uses automatic memory management with garbage collection. Developers do not need to manually allocate or deallocate memory.

### Stack vs Heap

- **Stack**: Local variables, function parameters
- **Heap**: Objects, collections, dynamic data

### Garbage Collection

The runtime includes a garbage collector that automatically reclaims memory from objects that are no longer referenced.

## Appendix

### Grammar Summary

```
program ::= statement*

statement ::= variable_decl
            | assignment
            | expression_stmt
            | block_stmt
            | if_stmt
            | while_stmt
            | until_stmt
            | for_stmt
            | for_each_stmt
            | break_stmt
            | continue_stmt
            | return_stmt
            | try_stmt
            | function_decl
            | struct_decl
            | class_decl
            | import_stmt
            | export_stmt

expression ::= literal
              | variable
              | binary_expr
              | unary_expr
              | grouping_expr
              | call_expr
              | member_expr
              | index_expr
```

### Reserved Words

All keywords listed in the Lexical Structure section are reserved and cannot be used as identifiers.

### Future Extensions

The language specification may be extended in future versions to include:
- Pattern matching
- Async/await
- Generics
- Reflection
- Metaprogramming

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
