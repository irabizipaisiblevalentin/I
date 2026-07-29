# LEXER_IMPLEMENTATION.md — I Language Lexer

## Overview

The I language lexer is a production-quality lexical analyzer that transforms I source code (`.i` files) into a validated token stream. It is the first stage of the I compiler pipeline.

## Architecture

```
Source Code (.i)
    ↓
UTF-8 Reader (handles BOM, encoding)
    ↓
DFA Engine (state machine)
    ↓
Keyword Resolver (hash table lookup)
    ↓
Token Buffer (immutable Token objects)
    ↓
Token Stream (List[Token])
```

## Token System

### Token Structure

```python
@dataclass(frozen=True)
class Token:
    type: TokenType        # Token category
    lexeme: str            # Original text from source
    location: TokenLocation  # Line, column, offset, span
    value: Any             # Parsed value (int, float, string, bool, None)
```

### Token Types (113 total)

| Category | Count | Examples |
|----------|-------|----------|
| Literals | 9 | INTEGER, FLOAT, STRING, RAW_STRING, TRIPLE_STRING, CHARACTER, BOOLEAN_TRUE, BOOLEAN_FALSE, NULL |
| Identifier | 1 | IDENTIFIER |
| Keywords | 42 | KW_NIBA, KW_CYANGWA, KW_UMURIMO, KW_IHEREZO, etc. |
| Arithmetic | 7 | PLUS, MINUS, STAR, SLASH, PERCENT, STAR_STAR, SLASH_SLASH |
| Comparison | 8 | EQ_EQ, BANG_EQ, GT, LT, GT_EQ, LT_EQ, IS_EQ, BANG_IS_EQ |
| Logical | 3 | AND_AND, OR_OR, BANG |
| Bitwise | 7 | AMP, PIPE, CARET, TILDE, LT_LT, GT_GT, GT_GT_GT |
| Assignment | 7 | EQ, PLUS_EQ, MINUS_EQ, STAR_EQ, SLASH_EQ, PERCENT_EQ, STAR_STAR_EQ |
| Delimiters | 22 | LPAREN, RPAREN, LBRACKET, RBRACKET, LBRACE, RBRACE, COMMA, COLON, SEMICOLON, DOT, DOT_DOT, DOT_DOT_DOT, ARROW, FAT_ARROW, QUESTION, QUESTION_DOT, AT, HASH, BACKSLASH |
| Special | 4 | EOF, NEWLINE, INDENT, DEDENT, ERROR |

### Keyword Mapping

All 42 Kinyarwanda keywords are recognized:

| Kinyarwanda | English | Token Type |
|-------------|---------|-----------|
| `niba` | if | KW_NIBA |
| `cyangwa` | else | KW_CYANGWA |
| `cyangwa_niba` | else if | KW_CYANGWA_NIBA |
| `kugenda` | continue | KW_KUGENDA |
| `gukoma` | break | KW_GUKOMA |
| `subira` | return | KW_SUBIRA |
| `tanga` | yield | KW_TANGA_YIELD |
| `kora` | do | KW_KORA |
| `wihuse` | while | KW_WIHUSE |
| `kugeza` | until | KW_KUGEZA |
| `kuri` | for | KW_KURI |
| `muri` | in | KW_MURI |
| `buri` | each | KW_BURI |
| `shyira` | let | KW_SHYIRA |
| `shyira_ko` | const | KW_SHYIRA_KO |
| `umurimo` | function | KW_UMURIMO |
| `igiceri` | struct | KW_IGICERI |
| `ikindi` | enum | KW_IKINDI |
| `urwego` | class | KW_URWEGO |
| `akabuto` | interface | KW_AKABUTO |
| `urubingo` | trait | KW_URUBINGO |
| `ubwoko` | type | KW_UBWOKO |
| `kugira` | have/extends | KW_KUGIRA |
| `gukora` | make/new | KW_GUKORA |
| `nshya` | new | KW_NSHYA |
| `shyiramo` | import | KW_SHYIRAMO |
| `kugira_ngo` | as | KW_KUGIRA_NGO |
| `kandi` | and | KW_KANDI |
| `bitewe` | because | KW_BITEWE |
| `ari` | is | KW_ARI |
| `si` | not | KW_SI |
| `gushyingura` | throw | KW_GUSHYINGURA |
| `kubika` | catch | KW_KUBIKA |
| `ikinyoma` | finally | KW_IKINYOMA |
| `iherezo` | end | KW_IHEREZO |
| `ubusa` | void | KW_UBUSA |
| `self` | self | KW_SELF |
| `super` | super | KW_SUPER |
| `true` | true | KW_TRUE_EN |
| `false` | false | KW_FALSE_EN |
| `null` | null | KW_NULL_EN |

Kinyarwanda boolean/null literals:
| Kinyarwanda | Token Type | Value |
|-------------|-----------|-------|
| `yego` | BOOLEAN_TRUE | True |
| `oya` | BOOLEAN_FALSE | False |

## Number Formats

### Integers
- Decimal: `42`, `1_000_000`
- Hexadecimal: `0xFF`, `0XAB_CD`
- Octal: `0o77`, `0o1_234`
- Binary: `0b1010`, `0b1_000_000`

### Floats
- Standard: `3.14`
- No integer part: `.5`
- With exponent: `1e10`, `1.5e-3`, `1E+5`

## String Formats

### Regular Strings
```python
"hello"          # Basic string
"hello\nworld"   # Escape sequences
"hello \"world\"" # Escaped quotes
```

### Escape Sequences
| Sequence | Character |
|----------|-----------|
| `\n` | Newline |
| `\t` | Tab |
| `\r` | Carriage return |
| `\\` | Backslash |
| `\"` | Double quote |
| `\'` | Single quote |
| `\0` | Null |
| `\uXXXX` | Unicode (4 hex) |
| `\UXXXXXXXX` | Unicode (8 hex) |

### Triple-Quoted Strings
```python
"""
This is a multi-line
string that spans
multiple lines.
"""
```

## Comment Formats

### Single-Line Comments
```
# This is a comment
42 # This is an inline comment
```

### Multi-Line Comments
```
#= This is a
multi-line comment
=#
```

Multi-line comments support nesting:
```
#= Outer #= inner =# still outer =#
```

### Documentation Comments
```
/// This is a documentation comment
/// It will be attached to the following declaration
umurimo soma() kora
    subira 42
iherezo
```

## Error System

### Error Codes
| Code | Name | Description |
|------|------|-------------|
| LEX001 | Invalid Character | Invalid character in source |
| LEX002 | Unterminated String | String literal not closed |
| LEX003 | Invalid Number | Invalid number format |
| LEX004 | Invalid Unicode | Invalid UTF-8 sequence |
| LEX005 | Invalid Escape | Unknown escape sequence |
| LEX006 | Unterminated Comment | Multi-line comment not closed |
| LEX007 | Integer Overflow | Integer literal too large |
| LEX008 | Invalid Identifier | Invalid identifier format |
| LEX009 | Unterminated Char | Character literal not closed |
| LEX010 | Unterminated Raw String | Raw string not closed |
| LEX011 | Unterminated Triple String | Triple-quoted string not closed |
| LEX012 | Invalid Escape Sequence | Invalid escape in string |

### Bilingual Messages
Every error includes:
- English message
- Kinyarwanda message
- Suggested fix

### Error Recovery
- Maximum 100 errors per file
- Aborts after 10 consecutive errors
- Continues tokenizing after individual errors

## API Usage

### Basic Tokenization
```python
from src.compiler.lexer import tokenize

tokens, errors = tokenize("shyira x = 42")
for token in tokens:
    print(token)
```

### Using the Lexer Class
```python
from src.compiler.lexer import Lexer

lexer = Lexer(source, filename="main.i")
tokens = lexer.tokenize()

if lexer.has_errors:
    print(lexer.errors.format_all())
```

### Accessing Token Information
```python
for token in tokens:
    print(f"{token.type.name}: {token.lexeme!r} at {token.line}:{token.column}")
    if token.value is not None:
        print(f"  value: {token.value!r}")
```

## Design Decisions

1. **IntEnum for TokenType**: Efficient comparison and memory usage
2. **Frozen dataclass for Token**: Immutable, hashable, memory-efficient
3. **Error collection vs exceptions**: Collects all errors instead of failing on first
4. **DFA-based scanning**: Clean state transitions, easy to extend
5. **Unicode support**: Full Unicode identifier support for Kinyarwanda
6. **Bilingual errors**: Every error has English and Kinyarwanda messages

## Testing Strategy

- **Unit tests**: 150+ tests covering all token types and edge cases
- **Performance tests**: Large file handling, throughput measurement
- **Unicode tests**: Kinyarwanda identifiers and strings
- **Error tests**: All error codes, recovery, bilingual messages

## Future Improvements

1. **Raw strings**: `r"..."` syntax (planned)
2. **Byte literals**: `b'x'` syntax (planned)
3. **Improve Unicode NFC normalization** for identifiers
4. **Add token interning** for better memory efficiency
5. **Implement INDENT/DEDENT tracking** for significant whitespace
