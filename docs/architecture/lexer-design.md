# Lexer Design

This document specifies the complete design of the I Programming Language lexer, including token types, Unicode handling, error recovery, and performance characteristics.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Token Types](#token-types)
- [Keywords](#keywords)
- [Identifiers](#identifiers)
- [Numbers](#numbers)
- [Strings](#strings)
- [Unicode Handling](#unicode-handling)
- [Comments](#comments)
- [Whitespace Rules](#whitespace-rules)
- [Error Recovery](#error-recovery)
- [UTF-8 Support](#utf-8-support)
- [Performance](#performance)
- [Testing Strategy](#testing-strategy)

## Overview

The lexer is the first stage of the I compiler pipeline. It converts raw UTF-8 source text into a stream of tokens. The lexer is designed for:

1. **Full Unicode support** for Kinyarwanda identifiers
2. **Bilingual error messages** (English and Kinyarwanda)
3. **Efficient tokenization** with O(n) time complexity
4. **Graceful error recovery** to report multiple errors per run
5. **Accurate source locations** for every token

## Architecture

```
Source File (.i)
    │
    ▼
┌───────────────┐
│  UTF-8 Reader │  Validate encoding, decode to codepoints
└───────┬───────┘
        │  codepoint stream
        ▼
┌───────────────┐
│  DFA Engine   │  State machine for token recognition
└───────┬───────┘
        │  raw tokens
        ▼
┌───────────────┐
│  Keyword      │  Check identifiers against keyword table
│  Resolver     │
└───────┬───────┘
        │  resolved tokens
        ▼
┌───────────────┐
│  Token Buffer │  Emit tokens with source locations
└───────┬───────┘
        │
        ▼
  Token Stream → Parser
```

### Lexer State Machine

```
States:
  START         → Initial state, no characters consumed
  IDENTIFIER    → Reading an identifier or keyword
  INTEGER       → Reading an integer literal
  FLOAT         → Reading a float literal (after decimal point)
  EXPONENT      → Reading scientific notation exponent
  STRING        → Reading a double-quoted string
  RAW_STRING    → Reading a raw string (r"...")
  CHAR          → Reading a single-quoted character
  LINE_COMMENT  → Reading a single-line comment
  BLOCK_COMMENT → Reading a multi-line comment
  OPERATOR      → Reading an operator
```

### State Transition Diagram

```
                              ┌──────────────────────────────────┐
                              │            START                  │
                              └───────────────┬──────────────────┘
                                              │
          ┌───────────────────────────────────┼───────────────────────────────────┐
          │                │                  │                 │                 │
     letter/_          digit              " or '              #               operator
          │                │                  │                 │                 │
          ▼                ▼                  ▼                 ▼                 ▼
    ┌──────────┐    ┌──────────┐       ┌──────────┐     ┌──────────┐      ┌──────────┐
    │IDENTIFIER│    │ INTEGER  │       │  STRING  │     │  LINE    │      │ OPERATOR │
    └────┬─────┘    └────┬─────┘       └────┬─────┘     │ COMMENT  │      └────┬─────┘
         │               │                  │           └────┬─────┘           │
     letter/         letter/             " or '              │            = or !
     digit/_         digit               end of str      newline           ▼
         │               │                  │              │          ┌──────────┐
         ▼               ▼                  ▼              ▼          │  = or == │
    ┌──────────┐    ┌──────────┐       ┌──────────┐   ┌──────────┐  │  != etc  │
    │IDENTIFIER│    │  FLOAT   │       │  TOKEN   │   │  TOKEN   │  └──────────┘
    └──────────┘    │(if '.')  │       │ COMPLETE │   │ COMPLETE │
                    └──────────┘       └──────────┘   └──────────┘
```

## Token Types

### Complete Token Type Enumeration

```
TokenType enum {
    // Literals
    INTEGER
    FLOAT
    STRING
    CHAR
    BOOLEAN_TRUE       // yego
    BOOLEAN_FALSE      // oya
    NULL               // ubusa

    // Identifiers
    IDENTIFIER

    // Keywords (42 keywords)
    KW_NIBA            // if
    KW_CYANGWA         // else
    KW_CYANGWA_NIBA    // else if
    KW_KUGENDA         // continue
    KW_GUKOMA          // break
    KW_SUBIRA          // return
    KW_TANGA           // yield
    KW_KORA            // do
    KW_WIHUSE          // while
    KW_KUGEZA          // until
    KW_KURI            // for
    KW_MURI            // in
    KW_BURI            // each
    KW_SHYIRA          // let
    KW_SHYIRA_KO       // const
    KW_UMURIMO         // function
    KW_IGICERI         // struct
    KW_IKINDI          // enum
    KW_URWEGO          // class
    KW_AKABUTO         // interface
    KW_URUBINGO        // trait
    KW_KUGIRA          // have (inheritance)
    KW_GUKORA          // make (instantiation)
    KW_SHYIRAMO        // import
    KW_TANGA_EXPORT    // export
    KW_KUGIRA_NGO      // as
    KW_KANDI           // and
    KW_CYANGWA_LOG     // or
    KW_BITEWE          // because
    KW_ARI             // is
    KW_SI              // not
    KW_GUSHYINGURA     // throw
    KW_KUBIKA          // catch
    KW_IKINYOMA        // finally
    KW_IHEREZO         // end
    KW_VOID            // void
    KW_SELF            // self
    KW_SUPER           // super
    KW_TYPE            // type (alias)
    KW_NSHYA           // new (constructor)
    KW_TRUE_EN         // true (English alias)
    KW_FALSE_EN        // false (English alias)
    KW_NULL_EN         // null (English alias)

    // Operators
    PLUS               // +
    MINUS              // -
    STAR               // *
    SLASH              // /
    PERCENT            // %
    STAR_STAR          // **
    SLASH_SLASH        // //
    PLUS_EQ            // +=
    MINUS_EQ           // -=
    STAR_EQ            // *=
    SLASH_EQ           // /=
    PERCENT_EQ         // %=
    STAR_STAR_EQ       // **=

    // Comparison
    EQ_EQ              // ==
    BANG_EQ            // !=
    GT                 // >
    LT                 // <
    GT_EQ              // >=
    LT_EQ              // <=
    IS_EQ              // === (identity)
    BANG_IS_EQ         // !== (not identity)

    // Logical
    AND_AND            // &&
    OR_OR              // ||
    BANG               // !

    // Bitwise
    AMP                // &
    PIPE               // |
    CARET              // ^
    TILDE              // ~
    LT_LT              // <<
    GT_GT              // >>
    GT_GT_GT           // >>>

    // Assignment
    EQ                 // =

    // Delimiters
    LPAREN             // (
    RPAREN             // )
    LBRACE             // {
    RBRACE             // }
    LBRACKET           // [
    RBRACKET           // ]
    COMMA              // ,
    COLON              // :
    SEMICOLON          // ;
    DOT                // .
    DOT_DOT            // ..
    DOT_DOT_DOT        // ...
    ARROW              // ->
    FAT_ARROW          // =>
    QUESTION           // ?
    QUESTION_DOT       // ?.
    AT                 // @
    HASH               // #
    BACKSLASH          // \

    // Special
    EOF
    NEWLINE            // significant newlines (optional)
    ERROR              // error token
}
```

### Token Category Table

| Category | Count | Purpose |
|----------|-------|---------|
| Literals | 7 | Literal values (int, float, string, char, bool, null, bool-false) |
| Identifier | 1 | User-defined names |
| Keywords | 42 | Reserved words |
| Arithmetic | 12 | Math operations |
| Comparison | 8 | Equality and ordering |
| Logical | 3 | Boolean logic |
| Bitwise | 7 | Bit manipulation |
| Assignment | 7 | Variable assignment |
| Delimiters | 22 | Structural punctuation |
| Special | 4 | EOF, newline, error, special |
| **Total** | **113** | |

## Keywords

### Keyword Table

Keywords are recognized by matching an identifier lexeme against a hash table. The hash table is built at lexer initialization time.

| Kinyarwanda | English | Token | Category | Example |
|-------------|---------|-------|----------|---------|
| `niba` | if | `KW_NIBA` | Control Flow | `niba x > 0` |
| `cyangwa` | else | `KW_CYANGWA` | Control Flow | `cyangwa` |
| `cyangwa_niba` | else if | `KW_CYANGWA_NIBA` | Control Flow | `cyangwa_niba x < 0` |
| `kugenda` | continue | `KW_KUGENDA` | Control Flow | `kugenda` |
| `gukoma` | break | `KW_GUKOMA` | Control Flow | `gukoma` |
| `subira` | return | `KW_SUBIRA` | Control Flow | `subira x` |
| `tanga` | yield | `KW_TANGA` | Control Flow | `tanga x` |
| `kora` | do | `KW_KORA` | Block | `kora ... iherezo` |
| `wihuse` | while | `KW_WIHUSE` | Loop | `wihuse condition` |
| `kugeza` | until | `KW_KUGEZA` | Loop | `kugeza condition` |
| `kuri` | for | `KW_KURI` | Loop | `kuri i muri 0 kugeza 10` |
| `muri` | in | `KW_MURI` | Loop | `muri collection` |
| `buri` | each | `KW_BURI` | Loop | `buri item muri list` |
| `shyira` | let | `KW_SHYIRA` | Declaration | `shyira x = 5` |
| `shyira_ko` | const | `KW_SHYIRA_KO` | Declaration | `shyira_ko PI = 3.14` |
| `umurimo` | function | `KW_UMURIMO` | Declaration | `umurimo add(a, b)` |
| `igiceri` | struct | `KW_IGICERI` | Declaration | `igiceri Point` |
| `ikindi` | enum | `KW_IKINDI` | Declaration | `ikindi Color` |
| `urwego` | class | `KW_URWEGO` | Declaration | `urwego Animal` |
| `akabuto` | interface | `KW_AKABUTO` | Declaration | `akabuto Drawable` |
| `urubingo` | trait | `KW_URUBINGO` | Declaration | `urubingo Serializable` |
| `kugira` | have (extends) | `KW_KUGIRA` | Inheritance | `urwego Dog kugira Animal` |
| `gukora` | make (new) | `KW_GUKORA` | Instantiation | `gukora Person("Jean")` |
| `shyiramo` | import | `KW_SHYIRAMO` | Module | `shyiramo "std/io"` |
| `tanga` | export | `KW_TANGA_EXPORT` | Module | `tanga function_name` |
| `kugira_ngo` | as | `KW_KUGIRA_NGO` | Module | `shyiramo mod kugira_ngo m` |
| `kandi` | and | `KW_KANDI` | Logical | `x kandi y` |
| `cyangwa` | or | `KW_CYANGWA_LOG` | Logical | `x cyangwa y` |
| `bitewe` | because | `KW_BITEWE` | Logical | `x kandi y bitewe z` |
| `ari` | is | `KW_ARI` | Comparison | `x ari 5` |
| `si` | not | `KW_SI` | Logical | `si x` |
| `gushyingura` | throw | `KW_GUSHYINGURA` | Exception | `gushyingura err` |
| `kubika` | catch | `KW_KUBIKA` | Exception | `kubika e` |
| `ikinyoma` | finally | `KW_IKINYOMA` | Exception | `ikinyoma` |
| `iherezo` | end | `KW_IHEREZO` | Block End | `iherezo` |
| `void` | void | `KW_VOID` | Type | `-> void` |
| `self` | self | `KW_SELF` | Reference | `self.name` |
| `super` | super | `KW_SUPER` | Reference | `super.method()` |
| `type` | type | `KW_TYPE` | Declaration | `type ID = int` |
| `nshya` | new | `KW_NSHYA` | Instantiation | `Person.nshya()` |
| `true` | true | `KW_TRUE_EN` | Literal | `true` |
| `false` | false | `KW_FALSE_EN` | Literal | `false` |
| `null` | null | `KW_NULL_EN` | Literal | `null` |

### Keyword Resolution Algorithm

```
function resolveKeyword(identifier_lexeme):
    result = keyword_table.lookup(identifier_lexeme)
    if result != null:
        return result  // Return keyword token type
    return IDENTIFIER  // Not a keyword
```

The keyword table uses a perfect hash function for O(1) lookup. The table is case-sensitive: `niba` is a keyword, `Niba` is an identifier.

## Identifiers

### Identifier Rules

An identifier must match this pattern:

```
identifier ::= letter (letter | digit | '_' | UnicodeLetter)*
letter     ::= 'a'..'z' | 'A'..'Z' | '_'
UnicodeLetter ::= any Unicode character with category Lu, Ll, Lt, Lm, Lo, Nl
digit      ::= '0'..'9'
```

### Valid Identifiers

```
umuntu              ✓ (Kinyarwanda word)
my_variable         ✓ (English with underscore)
_underscore         ✓ (leading underscore)
kinyarwanda_word    ✓ (Kinyarwanda with underscore)
ibyiciro            ✓ (Kinyarwanda)
imyitwarire         ✓ (Kinyarwanda)
_PRIVATE            ✓ (convention for private)
x1                  ✓ (letter + digit)
café                ✓ (Unicode letter)
ñand                ✓ (Unicode letter)
```

### Invalid Identifiers

```
123invalid          ✗ (starts with digit)
my-variable         ✗ (contains hyphen)
my@variable         ✗ (contains special character)
niba                ✗ (reserved keyword)
if                  ✗ (reserved keyword)
```

### Unicode Categories for Identifiers

The lexer accepts these Unicode categories as valid identifier characters:

| Category | Name | Examples |
|----------|------|----------|
| Lu | Uppercase Letter | A-Z, À-Ö, Ø-Þ,Ā-Ņ |
| Ll | Lowercase Letter | a-z, à-ö, ø-þ,ā-ņ |
| Lt | Titlecase Letter | ǅ, ǈ, ǋ, ǌ |
| Lm | Modifier Letter | ʹ, ʺ, ˂, ˃ |
| Lo | Other Letter | ʘ, ǀ, ModifiedDate |
| Nl | Number Letter | 0-9 (subscript/superscript) |

### NFC Normalization

All identifiers are normalized to Unicode Normalization Form C (NFC) before being stored in the symbol table. This ensures that the same identifier is always represented the same way, regardless of how it was typed.

```
"café" (e + combining accent) → "café" (precomposed é)
```

## Numbers

### Integer Literals

```
integer ::= decimal_integer
           | hex_integer
           | octal_integer
           | binary_integer

decimal_integer ::= [ '-' ] digit (digit | '_')*
hex_integer     ::= '0' ('x' | 'X') hex_digit (hex_digit | '_')*
octal_integer   ::= '0' ('o' | 'O') octal_digit (octal_digit | '_')*
binary_integer  ::= '0' ('b' | 'B') binary_digit (binary_digit | '_')*
```

### Integer Examples

```
42              ✓ (decimal)
-10             ✓ (negative decimal)
1_000_000       ✓ (underscores for readability)
0xFF            ✓ (hexadecimal)
0o77            ✓ (octal)
0b1010          ✓ (binary)
0               ✓ (zero)
0_0             ✓ (zero with underscore)
```

### Integer Rules

- Underscores may appear between digits but not at the start or end
- Leading zeros are not allowed except for zero itself (`0`)
- The value must fit in a 64-bit signed integer (-2^63 to 2^63-1)
- Underscores are stripped before parsing the value

### Float Literals

```
float ::= [ '-' ] digits '.' digits [ exponent ]
         | [ '-' ] digits exponent

digits   ::= digit (digit | '_')*
exponent ::= ('e' | 'E') [ '+' | '-' ] digits
```

### Float Examples

```
3.14            ✓ (standard float)
-0.001          ✓ (negative float)
1.0e10          ✓ (scientific notation)
1.5e-3          ✓ (scientific with negative exponent)
1_000.5         ✓ (underscore in integer part)
.5              ✓ (no leading zero)
5.              ✓ (no trailing zero)
0.0             ✓ (explicit zero)
```

### Number Parsing Algorithm

```
function parseNumber(start_pos):
    pos = start_pos
    is_float = false
    is_hex = false

    // Handle sign
    if source[pos] == '-':
        pos += 1

    // Handle prefix (0x, 0o, 0b)
    if source[pos] == '0' and source[pos+1] in ('x', 'X'):
        is_hex = true
        pos += 2
    elif source[pos] == '0' and source[pos+1] in ('o', 'O'):
        pos += 2  // octal
    elif source[pos] == '0' and source[pos+1] in ('b', 'B'):
        pos += 2  // binary

    // Parse digits
    while pos < len(source) and (source[pos].isdigit() or source[pos] == '_'):
        pos += 1

    // Check for decimal point
    if not is_hex and source[pos] == '.' and source[pos+1].isdigit():
        is_float = true
        pos += 1
        while pos < len(source) and (source[pos].isdigit() or source[pos] == '_'):
            pos += 1

    // Check for exponent
    if not is_hex and source[pos] in ('e', 'E'):
        is_float = true
        pos += 1
        if source[pos] in ('+', '-'):
            pos += 1
        while pos < len(source) and source[pos].isdigit():
            pos += 1

    lexeme = source[start_pos..pos]
    value = if is_float:
        parseFloat(lexeme)
    else:
        parseInt(lexeme)

    return Token(
        type = FLOAT if is_float else INTEGER,
        lexeme = lexeme,
        value = value,
        location = currentLocation()
    )
```

## Strings

### String Literal Syntax

```
string ::= '"' string_char* '"'
         | 'r"' raw_string_char* '"'       // raw string
         | '"""' triple_string_char* '"""'  // multi-line string

string_char ::= escape_sequence | non_escape_char
escape_sequence ::= '\' ('n' | 't' | 'r' | '\' | '"' | '\''
                        | '0' | 'u' hex_quad | 'U' hex_octet)
non_escape_char ::= any Unicode character except '"' and '\'
```

### String Examples

```
"Muraho"                    ✓ (simple string)
"Hello\nWorld"              ✓ (escape sequences)
"Imyirondoro: \"I\""        ✓ (escaped quotes)
"Path: C:\\Users"           ✓ (escaped backslash)
r"raw\nstring"              ✓ (raw string, no escapes)
"""
Multi
line
string
"""                         ✓ (multi-line string)
```

### Escape Sequences

| Escape | Meaning | Byte Value | Unicode Codepoint |
|--------|---------|------------|-------------------|
| `\n` | Newline | 0x0A | U+000A |
| `\t` | Tab | 0x09 | U+0009 |
| `\r` | Carriage return | 0x0D | U+000D |
| `\\` | Backslash | 0x5C | U+005C |
| `\"` | Double quote | 0x22 | U+0022 |
| `\'` | Single quote | 0x27 | U+0027 |
| `\0` | Null | 0x00 | U+0000 |
| `\uXXXX` | Unicode BMP | varies | U+XXXX |
| `\UXXXXXXXX` | Unicode full | varies | U+XXXXXXXX |

### String Parsing Algorithm

```
function parseString(start_pos):
    pos = start_pos + 1  // skip opening quote
    result = StringBuilder()

    while pos < len(source) and source[pos] != '"':
        if source[pos] == '\\':
            pos += 1
            char = source[pos]
            match char:
                case 'n':  result.append('\n')
                case 't':  result.append('\t')
                case 'r':  result.append('\r')
                case '\\': result.append('\\')
                case '"':  result.append('"')
                case '\'': result.append('\'')
                case '0':  result.append('\0')
                case 'u':  result.append(parseUnicodeEscape(pos, 4)); pos += 4
                case 'U':  result.append(parseUnicodeEscape(pos, 8)); pos += 8
                default:   emitError(LEX005, "Invalid escape sequence"); result.append(char)
        elif source[pos] == '\n':
            emitError(LEX002, "Unterminated string literal")
            break
        else:
            result.append(source[pos])
        pos += 1

    if pos >= len(source):
        emitError(LEX002, "Unterminated string literal")

    pos += 1  // skip closing quote

    return Token(
        type = STRING,
        lexeme = source[start_pos..pos],
        value = result.toString(),
        location = currentLocation()
    )
```

### Raw Strings

Raw strings do not process escape sequences. The content between `r"` and `"` is taken literally. This is useful for:
- Regular expressions
- File paths on Windows
- Text that contains many backslashes

### Multi-Line Strings

Multi-line strings are delimited by `"""`. They:
- Preserve internal newlines
- Strip leading whitespace common to all lines (like Python)
- Do not require escape sequences for internal quotes

## Unicode Handling

### Source File Encoding

All source files must be UTF-8 encoded. The lexer:

1. Validates the UTF-8 byte sequence
2. Handles an optional BOM (byte order mark) at the start of the file
3. Reports errors for invalid UTF-8 sequences

### UTF-8 Decoding

```
function decodeUTF8(bytes):
    codepoints = []
    pos = 0

    while pos < len(bytes):
        byte = bytes[pos]

        if byte <= 0x7F:
            // ASCII (1 byte)
            codepoints.append(Codepoint(byte, pos, 1))
            pos += 1
        elif byte >= 0xC0 and byte <= 0xDF:
            // 2-byte sequence
            if pos + 1 >= len(bytes) or (bytes[pos+1] & 0xC0) != 0x80:
                emitError(LEX004, "Invalid UTF-8 sequence")
                pos += 1
                continue
            cp = ((byte & 0x1F) << 6) | (bytes[pos+1] & 0x3F)
            codepoints.append(Codepoint(cp, pos, 2))
            pos += 2
        elif byte >= 0xE0 and byte <= 0xEF:
            // 3-byte sequence (covers most Kinyarwanda)
            if pos + 2 >= len(bytes) or (bytes[pos+1] & 0xC0) != 0x80 or (bytes[pos+2] & 0xC0) != 0x80:
                emitError(LEX004, "Invalid UTF-8 sequence")
                pos += 1
                continue
            cp = ((byte & 0x0F) << 12) | ((bytes[pos+1] & 0x3F) << 6) | (bytes[pos+2] & 0x3F)
            codepoints.append(Codepoint(cp, pos, 3))
            pos += 3
        elif byte >= 0xF0 and byte <= 0xF7:
            // 4-byte sequence
            if pos + 3 >= len(bytes):
                emitError(LEX004, "Invalid UTF-8 sequence")
                pos += 1
                continue
            cp = ((byte & 0x07) << 18) | ((bytes[pos+1] & 0x3F) << 12) | ((bytes[pos+2] & 0x3F) << 6) | (bytes[pos+3] & 0x3F)
            codepoints.append(Codepoint(cp, pos, 4))
            pos += 4
        else:
            emitError(LEX004, "Invalid UTF-8 start byte")
            pos += 1

    return codepoints
```

### BOM Handling

The lexer accepts an optional UTF-8 BOM (`EF BB BF`) at the start of the file. If present, the BOM is skipped and a note is emitted. The BOM does not appear in the token stream.

### Kinyarwanda Character Support

Kinyarwanda uses Latin-based characters with diacritics. Common characters:

| Character | Unicode | Name | Example |
|-----------|---------|------|---------|
| à | U+00E0 | a-grave | `rwànda` |
| é | U+00E9 | e-acute | `café` |
| è | U+00E8 | e-grave | `è` |
| î | U+00EE | i-circumflex | `î` |
| ô | U+00F4 | o-circumflex | `ô` |
| û | U+00FB | u-circumflex | `û` |
| ñ | U+00F1 | n-tilde | `ñ` |

All of these are valid identifier characters (Unicode category Ll).

## Comments

### Comment Syntax

```
comment ::= single_line_comment | multi_line_comment

single_line_comment ::= '#' [^\n]* newline
multi_line_comment  ::= '#=' comment_body '=#'
comment_body        ::= (any character)*
```

### Comment Examples

```
# This is a single-line comment
shyira x = 10  # inline comment

#=
This is a multi-line comment
that spans multiple lines
=#

#= Nested comments are not supported.
   The first =# closes the comment. =#
```

### Comment Handling

Comments are stripped from the token stream by default. The lexer has an option to preserve comments for:

- **IDE tooling**: Syntax highlighting, hover documentation
- **Documentation extraction**: Auto-generate docs from source
- **Source mapping**: Preserve comments in output code

### Documentation Comments

A special comment form (`///`) is recognized as a documentation comment:

```
/// Adds two numbers together.
/// @param a First number
/// @param b Second number
/// @return The sum
umurimo add(a: int, b: int) -> int
    subira a + b
iherezo
```

Documentation comments are attached to the following declaration in the AST.

## Whitespace Rules

### Whitespace Characters

| Character | Unicode | Name | Significant? |
|-----------|---------|------|-------------|
| Space | U+0020 | Space | No (separator) |
| Tab | U+0009 | Tab | No (separator) |
| Newline | U+000A | Line feed | Sometimes |
| Carriage Return | U+000D | CR | No (converted to LF) |
| CRLF | U+000D U+000A | CR+LF | No (converted to LF) |

### Whitespace Rules

1. **Between tokens**: Whitespace between tokens is insignificant and ignored.
2. **Inside strings**: Whitespace inside string literals is preserved exactly.
3. **Indentation**: The I language does NOT use significant indentation. Blocks are delimited by `kora`/`iherezo` (or `{`/`}`).
4. **Newlines**: Newlines are generally insignificant but are tracked for error reporting.

### Newline Handling

```
function handleNewline():
    line_number += 1
    column_number = 1
    // Newline does not produce a token (unless in raw string)
```

### Indentation Tracking

While I does not use significant indentation, the lexer tracks indentation level for:

- **Error suggestions**: "Did you forget `iherezo`?"
- **IDE features**: Auto-indentation
- **Pretty printing**: Automatic formatting

## Error Recovery

### Error Types

| Code | Name | Description | Recovery |
|------|------|-------------|----------|
| LEX001 | Invalid Character | Unrecognized character in source | Skip character, continue |
| LEX002 | Unterminated String | String literal not closed | Insert closing quote, continue |
| LEX003 | Invalid Number | Number format is invalid | Skip to next valid token |
| LEX004 | Invalid Unicode | Invalid UTF-8 sequence | Skip sequence, continue |
| LEX005 | Invalid Escape | Unknown escape sequence | Skip sequence, continue |
| LEX006 | Unterminated Comment | Multi-line comment not closed | Insert closing `=#`, continue |
| LEX007 | Integer Overflow | Integer literal too large | Clamp to max value, continue |
| LEX008 | Invalid Identifier | Identifier contains invalid characters | Skip invalid characters, continue |

### Error Recovery Algorithm

```
function recoverFromError(error_type):
    emitError(error_type)

    match error_type:
        case LEX001:  // Invalid character
            advance()  // Skip the bad character
            state = START

        case LEX002:  // Unterminated string
            // Try to find closing quote
            while not atEnd() and current() != '"':
                if current() == '\n':
                    line_number += 1
                advance()
            if current() == '"':
                advance()  // Skip closing quote
            emitToken(STRING, "")
            state = START

        case LEX003:  // Invalid number
            // Skip digits until non-digit
            while not atEnd() and (current().isdigit() or current() == '.'):
                advance()
            state = START

        case LEX006:  // Unterminated comment
            // Skip to end of file
            while not atEnd():
                advance()
            state = START
```

### Error Limiting

To prevent overwhelming error output:

1. **Maximum total errors**: 100 errors per file
2. **Consecutive error limit**: If 10 errors occur in a row without any successful token, abort tokenization
3. **Error deduplication**: If the same error occurs at the same location, only report it once

## UTF-8 Support

### Encoding Requirements

- Source files MUST be UTF-8 encoded
- UTF-8 BOM is optional and ignored
- Invalid UTF-8 produces an error but tokenization continues

### Byte Order Mark (BOM)

```
UTF-8 BOM: EF BB BF (3 bytes)

If present at byte offset 0:
    - Skip the BOM
    - Note: "File has UTF-8 BOM, which is unnecessary"
    - Continue tokenization from byte offset 3

If present elsewhere:
    - Treat as regular bytes (likely part of a string or comment)
```

### Validation

```
function validateUTF8(bytes):
    errors = []
    pos = 0

    while pos < len(bytes):
        byte = bytes[pos]

        if byte <= 0x7F:
            pos += 1
        elif byte >= 0x80 and byte <= 0xBF:
            errors.append(LEX004, "Unexpected continuation byte", pos)
            pos += 1
        elif byte >= 0xC0 and byte <= 0xDF:
            if pos + 1 >= len(bytes) or (bytes[pos+1] & 0xC0) != 0x80:
                errors.append(LEX004, "Invalid 2-byte sequence", pos)
            pos += 2
        elif byte >= 0xE0 and byte <= 0xEF:
            if pos + 2 >= len(bytes) or (bytes[pos+1] & 0xC0) != 0x80 or (bytes[pos+2] & 0xC0) != 0x80:
                errors.append(LEX004, "Invalid 3-byte sequence", pos)
            pos += 3
        elif byte >= 0xF0 and byte <= 0xF7:
            if pos + 3 >= len(bytes) or any invalid continuation:
                errors.append(LEX004, "Invalid 4-byte sequence", pos)
            pos += 4
        else:
            errors.append(LEX004, "Invalid UTF-8 start byte", pos)
            pos += 1

    return errors
```

## Performance

### Time Complexity

- **Tokenization**: O(n) where n is the source file size in bytes
- **Keyword lookup**: O(1) with perfect hash table
- **Number parsing**: O(d) where d is the number of digits
- **String parsing**: O(s) where s is the string length

### Space Complexity

- **Token storage**: O(t) where t is the number of tokens
- **Source location**: O(1) per token (line, column, offset)
- **Keyword table**: O(k) where k is the number of keywords (constant)
- **Total**: O(n) in the worst case (all tokens stored at once)

### Optimization Strategies

1. **Buffered I/O**: Read source in 4KB chunks
2. **Keyword trie**: Use a trie for O(m) keyword lookup where m is the keyword length
3. **Digit tables**: Precomputed tables for digit value lookup
4. **String interning**: Intern all identifier strings to save memory
5. **Arena allocation**: Allocate all tokens from a single arena for cache-friendly allocation
6. **Lazy location tracking**: Only compute line/column when needed (for error reporting)

### Memory Layout

```
Token (24 bytes on 64-bit):
  type:     4 bytes  (enum)
  padding:  4 bytes
  lexeme:   8 bytes  (pointer to string)
  value:    8 bytes  (pointer or inline value)
  location: 4 bytes  (packed line + column)
  span:     4 bytes  (start offset + length)
```

## Testing Strategy

### Unit Tests

- **Token type recognition**: Each token type produces the correct `TokenType`
- **Literal values**: Numbers, strings, and booleans are parsed to correct values
- **Source locations**: Line and column tracking is accurate
- **Unicode handling**: Kinyarwanda characters are recognized correctly
- **Error detection**: Each error type is detected correctly
- **Error recovery**: Recovery produces reasonable tokens after errors

### Integration Tests

- **Full source files**: Lex real I programs and verify token streams
- **Edge cases**: Empty files, very long lines, deeply nested comments
- **Performance**: Lex 10,000-line files in under 100ms

### Fuzzing

- **Random bytes**: Feed random byte sequences to the lexer
- **Unicode fuzzing**: Feed random Unicode codepoints
- **Boundary conditions**: Test near token length limits, near integer overflow

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
