# Error System Design

This document specifies the complete error system for the I Programming Language compiler, including error codes, bilingual messages, source location tracking, and error formatting.

## Table of Contents

- [Overview](#overview)
- [Error Architecture](#error-architecture)
- [Error Structure](#error-structure)
- [Error Code System](#error-code-system)
- [Bilingual Messages](#bilingual-messages)
- [Source Snippets](#source-snippets)
- [Suggestions](#suggestions)
- [Related Locations](#related-locations)
- [Error Formatting](#error-formatting)
- [Error Severity](#error-severity)
- [Error Limiting](#error-limiting)
- [Complete Error Catalog](#complete-error-catalog)

## Overview

The I compiler provides the best error messages possible. Every error includes:

1. **Error code**: Unique identifier (e.g., TYP001)
2. **Title**: Short, descriptive name
3. **Message**: Detailed explanation in English and Kinyarwanda
4. **Source location**: File, line, column
5. **Code snippet**: Visual indication of the problem
6. **Suggestion**: How to fix the error
7. **Related locations**: Other relevant source positions

### Design Philosophy

1. **Helpful, not hostile**: Errors guide the developer to a solution
2. **Bilingual**: Every error in both English and Kinyarwanda
3. **Precise**: Exact location and nature of the problem
4. **Actionable**: Every error includes a suggestion
5. **Contextual**: Related source locations provide context

## Error Architecture

```
Compiler Pipeline
    │
    ├── Lexer ──────────────┐
    ├── Parser ─────────────┤
    ├── Semantic Analyzer ──┤
    ├── Type Checker ───────┤  All errors flow to
    ├── IR Generator ───────┤  ErrorCollector
    ├── Optimizer ──────────┤
    ├── Bytecode Generator ─┤
    └── Virtual Machine ────┘
                               │
                               ▼
                        ErrorCollector
                               │
                               ▼
                        ErrorFormatter
                               │
                    ┌──────────┴──────────┐
                    │                     │
              Terminal Output      IDE Output
              (ANSI colors)       (LSP diagnostics)
```

### ErrorCollector

```
ErrorCollector {
    errors: List[CompilerError>
    warnings: List[CompilerWarning]
    notes: List[CompilerNote]
    max_errors: int = 100
    max_warnings: int = 200

    report(error: CompilerError)
    report(warning: CompilerWarning)
    report(note: CompilerNote)
    has_errors() -> bool
    has_warnings() -> bool
    sorted_diagnostics() -> List[Diagnostic>
    summary() -> ErrorSummary
}
```

## Error Structure

### CompilerError

```
CompilerError {
    code: string               // "TYP001"
    title: string              // "Type Mismatch"
    message_en: string         // English description
    message_rw: string         // Kinyarwanda description
    severity: Severity         // ERROR, WARNING, NOTE

    // Location
    file: string               // Source file path
    line: int                  // 1-indexed line number
    column: int                // 1-indexed column number
    end_line: int              // End line (for multi-line spans)
    end_column: int            // End column

    // Context
    snippet: CodeSnippet       // Source code with highlighting
    suggestions: List[string>  // Suggested fixes
    related: List<RelatedLocation>  // Related source locations
    notes: List[string]        // Additional notes

    // Metadata
    stage: CompilationStage    // Which compiler stage produced this
    timestamp: int             // When the error was produced
}
```

### CompilerWarning

```
CompilerWarning {
    code: string               // "SEM104"
    title: string              // "Unused Variable"
    message_en: string
    message_rw: string
    severity: Severity = WARNING

    file: string
    line: int
    column: int

    snippet: CodeSnippet
    suggestions: List[string]
}
```

### CompilerNote

```
CompilerNote {
    message_en: string
    message_rw: string

    file: string
    line: int
    column: int

    snippet: CodeSnippet
}
```

### CodeSnippet

```
CodeSnippet {
    file: string
    start_line: int
    end_line: int
    lines: List[string]        // Source lines
    highlight_start: int       // Column to start highlighting
    highlight_end: int         // Column to end highlighting
    underline_start: int       // Column to start underline
    underline_end: int         // Column to end underline
}
```

### RelatedLocation

```
RelatedLocation {
    message_en: string         // Why this location is related
    message_rw: string
    file: string
    line: int
    column: int
    snippet: CodeSnippet
}
```

## Error Code System

### Error Code Format

```
[Stage][Number]

Stage: 3-letter prefix
Number: 3-digit number
```

### Error Code Ranges

| Range | Stage | Description |
|-------|-------|-------------|
| LEX001-LEX099 | Lexer | Lexical errors |
| PARS001-PARS099 | Parser | Syntax errors |
| SEM001-SEM099 | Semantic | Semantic errors |
| SEM101-SEM199 | Semantic | Semantic warnings |
| TYP001-TYP099 | Type Checker | Type errors |
| TYP101-TYP199 | Type Checker | Type warnings |
| IR001-IR099 | IR Generator | IR errors |
| OPT001-OPT099 | Optimizer | Optimization errors |
| BC001-BC099 | Bytecode Gen | Bytecode errors |
| RUN001-RUN099 | Runtime | Runtime errors |
| MOD001-MOD099 | Module | Module errors |
| INT001-INT099 | Internal | Internal compiler errors |

## Bilingual Messages

### English Messages

Every error has a clear English message:

```
TYP001: Type Mismatch
  Expected: int
  Actual: string
  |
  4: shyira x: int = "hello"
  |                    ^^^^^^^
  |
  Suggestion: Remove the quotes to use an integer literal,
             or change the type annotation to string.
```

### Kinyarwanda Messages

Every error has an equivalent Kinyarwanda message:

```
TYP001: Ubuhungane bw'ubwoko
  Ibisobanuro: int
  Yabonetse: string
  |
  4: shyira x: int = "hello"
  |                    ^^^^^^^
  |
  Inama: Kubura amabibambo ngo ukoresha inamba,
        cyangwa ushindure urwego rwo kwandika.
```

### Message Quality Guidelines

1. **Start with what went wrong**: "Type mismatch" not "The compiler found..."
2. **Be specific**: "Expected int, got string" not "Incompatible types"
3. **Be helpful**: Include the actual and expected values
4. **Be concise**: Keep messages under 80 characters
5. **Use consistent terminology**: Same terms across all errors

### Kinyarwanda Translation Guidelines

1. **Use natural Kinyarwanda**: Not word-for-word translation
2. **Use technical terms correctly**: Consistent translation of programming terms
3. **Be clear and concise**: Same quality as English
4. **Use proper grammar**: Correct Kinyarwanda grammar

## Source Snippets

### Snippet Generation

Every error includes a source code snippet showing the problem:

```
  --> main.i:4:19
   |
 4 | shyira x: int = "hello"
   |                   ^^^^^^^ expected int, got string
   |
```

### Snippet Rules

1. Show the line(s) where the error occurs
2. Highlight the specific token/expression that caused the error
3. Underline the problematic span
4. Add an arrow or annotation pointing to the issue
5. Include 1-2 lines of context above and below

### Multi-Line Snippets

For errors spanning multiple lines:

```
  --> main.i:8:1-10:5
   |
 8 | niba x > 0
   | ^^^^^^^^^^^ condition starts here
 9 |     andika("positive")
10 | iherezo
   | ^^^^^^^ block ends here
   |
   = note: condition and block must be on the same logical line
```

## Suggestions

### Suggestion Types

1. **Fix-it suggestions**: Exact code to replace the problematic code
2. **Hint suggestions**: General guidance on how to fix
3. **Related suggestions**: Point to related documentation or examples

### Suggestion Format

```
Suggestion {
    message: string           // Human-readable description
    replacement: Optional<CodeReplacement>  // Exact code fix
    applicability: Applicability  // CERTAIN, POSSIBLE, UNKNOWN
}

CodeReplacement {
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    replacement: string       // New code
}
```

### Example Suggestions

```
TYP001: Type Mismatch
  Suggestion: Change the type annotation to string
    shyira x: string = "hello"

TYP002: Argument Count Mismatch
  Suggestion: Add the missing argument
    add(1, 2, 3)

SEM001: Undefined Variable
  Suggestion: Did you mean 'x'?
    shyira x = 10
```

## Related Locations

### When to Include Related Locations

1. **Previous declaration**: When a name is redeclared
2. **Overridden method**: When a method override doesn't match
3. **Type definition**: When using a type incorrectly
4. **Import location**: When an imported name is used incorrectly

### Example

```
TYP001: Type Mismatch
  --> main.i:8:15
   |
 8 |     subira a + b
   |               ^ expected int, got string
   |
   --> main.i:3:12
    |
  3 | umurimo add(a: int, b: string) -> int
    |                     ^^^^^^^^ parameter declared here
```

## Error Formatting

### Terminal Output

ANSI-colored output for terminal:

```
error[TYP001]: Type Mismatch
  --> main.i:4:19
   |
 4 | shyira x: int = "hello"
   |                   ^^^^^^^ expected int, got string
   |
   = note: 'int' was expected because of the type annotation on line 4
   = help: change the type annotation to 'string', or use an integer literal

  Kinyarwanda: Ubuhungane bw'ubwoko
  Ibisobanuro: int, yabonetse string
```

### Color Scheme

| Element | Color |
|---------|-------|
| Error code | Red bold |
| File path | Cyan |
| Line number | Cyan |
| Snippet line | Default |
| Highlight | Red underline |
| Suggestion | Green |
| Note | Yellow |
| Related | Blue |

### IDE Output (LSP)

JSON diagnostics for IDE integration:

```json
{
  "range": {
    "start": {"line": 3, "character": 19},
    "end": {"line": 3, "character": 26}
  },
  "severity": 1,
  "code": "TYP001",
  "source": "I Compiler",
  "message": "Type Mismatch: Expected int, got string",
  "relatedInformation": [
    {
      "location": {
        "uri": "file:///main.i",
        "range": {"start": {"line": 2, "character": 11}, "end": {"line": 2, "character": 14}}
      },
      "message": "parameter declared here"
    }
  ]
}
```

## Error Severity

### Severity Levels

| Level | Icon | Description |
|-------|------|-------------|
| Error | error | Compilation cannot continue |
| Warning | warning | Suspicious but may compile |
| Note | note | Additional information |
| Help | help | Suggestions for fixing |

### Error vs Warning

**Errors** prevent compilation:
- Type mismatches
- Undefined variables
- Syntax errors
- Missing return values

**Warnings** allow compilation:
- Unused variables
- Shadowed variables
- Deprecated usage
- Possible null dereference

### Configuring Severity

```
// In i-project.toml
[compiler.errors]
treat_warnings_as_errors = false
max_errors = 100
max_warnings = 200

[compiler.warnings]
unused_variables = "warning"    # "error", "warning", "ignore"
shadowed_variables = "ignore"
deprecated_usage = "warning"
```

## Error Limiting

### Limits

| Limit | Default | Purpose |
|-------|---------|---------|
| Max errors | 100 | Prevent overwhelming output |
| Max warnings | 200 | Prevent overwhelming output |
| Max consecutive errors | 10 | Detect infinite error loops |
| Max error depth | 10 | Prevent cascading errors |

### Error Summarization

When errors are limited, provide a summary:

```
error: aborting due to 100 previous errors
  23 errors were silenced
  Run with --max-errors=200 to see more
```

## Complete Error Catalog

### Lexer Errors (LEX)

| Code | Title | English | Kinyarwanda |
|------|-------|---------|-------------|
| LEX001 | Invalid Character | Invalid character in source | Inkoresha itashyizwe mu buryo bw'amategeko |
| LEX002 | Unterminated String | Unterminated string literal | Ijambo ritagifungiye |
| LEX003 | Invalid Number | Invalid number format | Ibaneco ry'ubwoko butari busanzwe |
| LEX004 | Invalid Unicode | Invalid UTF-8 sequence | Ikibazo cy'ubwoko bwa UTF-8 |
| LEX005 | Invalid Escape | Unknown escape sequence | Igice kitashyizwe mu buryo |
| LEX006 | Unterminated Comment | Multi-line comment not closed | Ijambo ry'ubusuzuma ryafunguwe |
| LEX007 | Integer Overflow | Integer literal too large | Inameco ryarenze urugero |
| LEX008 | Invalid Identifier | Identifier contains invalid characters | Izina riri mu buryo butari busanzwe |

### Parser Errors (PARS)

| Code | Title | English | Kinyarwanda |
|------|-------|---------|-------------|
| PARS001 | Unexpected Token | Unexpected token found | Ikimenyetso kitari gihari |
| PARS002 | Missing Token | Expected token missing | Ibuze ikimenyetso |
| PARS003 | Extra Token | Extra token found | Ikimenyetso cy'inyongera |
| PARS004 | Invalid Expression | Invalid expression | Imvugo itagira imiterere |
| PARS005 | Unterminated Block | Block not terminated | Buroke butarangiriye |

### Semantic Errors (SEM)

| Code | Title | English | Kinyarwanda |
|------|-------|---------|-------------|
| SEM001 | Undefined Variable | Variable not defined | Impanuka itashyizweho |
| SEM002 | Use Before Declaration | Variable used before declaration | Igihe icyo ari cyo cyose |
| SEM003 | Duplicate Declaration | Name already defined | Izina ryavuzwembere |
| SEM005 | No Member | Member not found on type | Imimerere itabonetse |
| SEM006 | Module Not Found | Module not found | Modile yabonetse |
| SEM007 | Circular Import | Circular import detected | Ubukungurane bw'amakuru |
| SEM008 | Export Not Found | Exported symbol not found | Icyo tubuza cyabonetse |
| SEM009 | Break Outside Loop | Break outside of loop | Gukoma hanze y'umurongo |
| SEM010 | Continue Outside Loop | Continue outside of loop | Kwiga hanze y'umurongo |
| SEM011 | Return Type Mismatch | Return type doesn't match | Ubwoko bw'isubizo ntibuhe |
| SEM012 | Return Outside Function | Return outside of function | Subira hanze y'umurimo |
| SEM013 | Missing Return | Missing return on all paths | Isubiro ritabonetse |

### Semantic Warnings (SEM1xx)

| Code | Title | English | Kinyarwanda |
|------|-------|---------|-------------|
| SEM101 | Shadowed Variable | Variable shadows outer variable | Impenduka y'izina |
| SEM102 | Missing Return Value | Function expects return value | Umurimo usaba isubizo |
| SEM103 | Unreachable Code | Unreachable code detected | Igihe gito |
| SEM104 | Unused Variable | Variable declared but never used | Impenduka itakoreshwa |
| SEM105 | Unused Parameter | Parameter never used | Igice gitakoreshwa |
| SEM106 | Unused Import | Imported module not used | Modile y'inyongera |
| SEM107 | Deprecated | Deprecated feature used | Igihe gito cyarangiye |
| SEM108 | Possible Null | Nullable value used without check | Igihe gito cyane |

### Type Errors (TYP)

| Code | Title | English | Kinyarwanda |
|------|-------|---------|-------------|
| TYP001 | Type Mismatch | Types are not compatible | Ubwoko ntibuhe |
| TYP002 | Argument Count | Wrong number of arguments | Umubare munsi |
| TYP003 | Argument Type | Argument type mismatch | Ubwoko bw'igice |
| TYP004 | Return Type | Return type mismatch | Ubwoko bw'isubizo |
| TYP005 | Optional Access | Accessing optional without null check | Igihe gito cyane |
| TYP006 | No Member | Member not found | Imimerere itabonetse |
| TYP007 | Not Callable | Expression is not callable | Imvugo nta buryo bwo guhamagara |
| TYP008 | Not Indexable | Expression is not indexable | Imvugo nta buryo bwo kubara |
| TYP009 | Not Iterable | Expression is not iterable | Imvugo nta buryo bwo kuzunguruka |
| TYP010 | Generic Constraint | Generic constraint not met | Igice cy'ubwoko |
| TYP011 | Union Error | Operation invalid for union | Ubukungurane bw'amakuru |
| TYP012 | Inference Failed | Type inference failed | Kutabona ubwoko |
| TYP013 | Circular Type | Circular type definition | Ubwoko bwa ringi |
| TYP014 | Abstract Type | Cannot instantiate abstract type | Kutagira ubwoko |

### Runtime Errors (RUN)

| Code | Title | English | Kinyarwanda |
|------|-------|---------|-------------|
| RUN001 | Stack Overflow | Stack overflow | Ubwoko bwa stack |
| RUN002 | Out of Memory | Out of memory | Kutagira ubwoko |
| RUN003 | Index Out of Bounds | Index out of bounds | Igice cyarenze |
| RUN004 | Null Dereference | Null pointer dereference | Ubwoko bw'iburiro |
| RUN005 | Type Error | Runtime type error | Ubwoko bw'ubwoko |
| RUN006 | Division by Zero | Division by zero | Kwakira-zero |
| RUN007 | Unhandled Exception | Unhandled exception | Igice kirimo |

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
