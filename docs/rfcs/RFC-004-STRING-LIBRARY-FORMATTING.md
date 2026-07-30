# RFC-004: String Library & Formatting

- **RFC ID**: 004
- **Author**: I Programming Language Engineering Council
- **Status**: Draft
- **Created**: 2026-07-30
- **Updated**: 2026-07-30
- **I-Version**: 1.0
- **Category**: Standard Library

## Summary

Define a comprehensive string library providing slicing, searching, transformation, and formatting operations. Introduce string interpolation as syntactic sugar for formatting. These capabilities are essential for code generation, error messages, and general compiler text processing.

## Motivation

### Problem Statement

The LANGUAGE_SPECIFICATION.md defines `string` as a primitive type with literal syntax (`"..."`) and concatenation (`+`), but provides no other operations. A self-hosting compiler requires:

1. **Code generation**: Building output strings from templates
2. **Lexing**: Character-level inspection, Unicode handling
3. **Error messages**: Formatting structured error information
4. **Identifier processing**: Case conversion, validation
5. **File path manipulation**: Joining, splitting paths

Without these, the compiler cannot produce formatted output or process string data.

### Current Workarounds

The Python compiler uses:
- f-strings for code generation: `f"mov {reg}, {value}"`
- `.join()`, `.split()`, `.strip()` for text processing
- `.format()` for complex formatting

In I without string operations, these would require cumbersome character-by-character processing.

### Why a Language Change?

String formatting and interpolation are language-level concerns because:
1. String interpolation requires parser support (`"Hello {name}"`)
2. A string type without operations is incomplete
3. Performance characteristics affect code generation strategies

## Detailed Design

### String Operations (method syntax)

```i
shyira s = "Muraho, Isi!"

# Length
s.uburebure()  # 12

# Access by index (0-based)
s[0]           # 'M'
s[-1]          # '!'

# Slicing
s.ice(0, 6)           # "Muraho"
s.ice(7)              # "Isi!"
s.ice(0, 6, 2)        # "Mrh" (step)
s.ice(-4)             # "Isi!" (negative start)

# Searching
s.shaka("Isi")        # 7 (index)
s.shaka("Hello")      # -1 (not found)
s.shaka_inyuma("i")   # 9 (search from end)
s.ribamo("Isi")       # yego
s.yatanguye("Mu")     # yego
s.yarangiye("!")      # yego
s.ibarizo("Isi", 0)   # 7 (search from offset)

# Transformation
s.hindura("Isi", "Africa")  # "Muraho, Africa!"
s.ntoya()                   # "muraho, isi!"
s.nini()                    # "MURAHO, ISI!"
s.umusingi()                # "Muraho, Isi!" (title case)

# Trimming
s.koma()              # "Muraho, Isi!" (both ends)
s.koma_ibumoso()      # left trim
s.koma_iburyo()       # right trim

# Splitting and joining
s.ma(", ")                # ["Muraho", "Isi!"]
s.ma()                    # ["Muraho,", "Isi!"] (whitespace)

shyira words = ["a", "b", "c"]
words.unga(", ")          # "a, b, c"
words.unga("")            # "abc"

# Padding
"5".uzuza_ibumoso(3, '0')     # "005"
"hi".uzuza_iburyo(5, '-')     # "hi---"
"center".uzuza hagati(10, '*') # "**center**"

# Repetition
"ha".subiramo(3)          # "hahaha"

# Character inspection
"a".ni_inyuguti()         # yego (is alphabetic)
"3".ni_umubare()          # yego (is numeric)
" ".ni_umwanya()          # yego (is whitespace)
"a".ni_ntoya()            # yego (is lowercase)
"A".ni_nini()             # yego (is uppercase)

# UTF-8 / Unicode
s.umubare_wa_bytes()      # byte length (for binary I/O)
s.umubare_wa_char()       # character count (may differ)
s.koresha_normalize("NFC")  # Unicode normalization
```

### String Formatting

#### Positional Formatting

```i
shyira formatted = "{0} ni {1}".forma("Alice", 30)
# "Alice ni 30"

shyira formatted = "{1} ni {0}".forma(30, "Alice")
# "Alice ni 30"
```

#### Named Formatting

```i
shyira formatted = "{izina} ni {imyaka} years old".forma(
    izina="Alice", imyaka=30
)
# "Alice ni 30 years old"
```

#### Format Specifiers

```i
shyira pi = 3.14159265
shyira formatted = "{0:.2f}".forma(pi)          # "3.14"
shyira formatted = "{0:+d}".forma(42)            # "+42"
shyira formatted = "{0:010d}".forma(255)         # "0000000255"
shyira formatted = "{0:<10}".forma("left")       # "left      "
shyira formatted = "{0:>10}".forma("right")      # "     right"
shyira formatted = "{0:^10}".forma("center")     # "  center  "
```

### String Interpolation

String literals support `{expr}` for inline interpolation:

```i
shyira izina = "Alice"
shyira imyaka = 30

# Interpolated string
shyira message = "{izina} ni {imyaka}"
# "Alice ni 30"

shyira result = "2 + 2 = {2 + 2}"
# "2 + 2 = 4"

shyira computed = "{izina.ntoya()} has {imyaka + 1} next year"
# "alice has 31 next year"
```

### StringBuilder

For efficient string building in loops:

```i
shyira builder = urubuga.StringBuilder.nshya()
builder.ongeza("Line 1")
builder.ongeza_umurongo("Line 2")  # adds newline
builder.ongeza(42)                  # converts to string
shyira result = builder.kubaka()

# With initial capacity
shyira builder = urubuga.StringBuilder.nshya(1024)
```

### Type Signatures

```
string {
    # Access
    uburebure() -> int
    kubona(index: int) -> char
    ice(start: int, end?: int, step?: int) -> string

    # Search
    shaka(needle: string, start?: int) -> int
    shaka_inyuma(needle: string) -> int
    ribamo(needle: string) -> bool
    yatanguye(prefix: string) -> bool
    yarangiye(suffix: string) -> bool

    # Transformation
    hindura(old: string, new: string) -> string
    ntoya() -> string
    nini() -> string
    umusingi() -> string
    koma() -> string
    koma_ibumoso() -> string
    koma_iburyo() -> string

    # Split/Join
    ma(separator?: string) -> list<string>
    unga(elements: list<string>) -> string

    # Formatting
    forma(args...) -> string

    # Padding
    uzuza_ibumoso(width: int, ch: char) -> string
    uzuza_iburyo(width: int, ch: char) -> string
    uzuza_hagati(width: int, ch: char) -> string

    # Repetition
    subiramo(count: int) -> string

    # Inspection
    ni_nyuguti() -> bool
    ni_umubare() -> bool
    ni_umwanya() -> bool
    ni_ntoya() -> bool
    ni_nini() -> bool
}
```

## Alternatives Considered

### Alternative 1: C-style printf

Use `printf`-style format strings: `"%s is %d" % (name, age)`

**Pros:** Familiar to C developers
**Cons:** Not type-safe, limited format specifiers, no named arguments

### Alternative 2: Template literals only

Only support `"Hello {name}"` interpolation, no `.forma()` method.

**Pros:** Simpler, less API surface
**Cons:** Cannot reuse format strings, no format specifiers, less flexible

### Alternative 3: External library

Provide formatting as a third-party package rather than built-in strings.

**Pros:** Keeps language core minimal
**Cons:** Every I program needs string operations; essential for compiler

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

1. Should string interpolation use `{expr}` or a different delimiter (e.g., `${expr}`)?
2. Should escape sequences support `\u{...}` for arbitrary Unicode?
3. Should format specifiers support localization (e.g., decimal separators)?

## Future Possibilities

- Raw string literals: `r"C:\path\to\file"` (already partially supported)
- Byte string literals: `b"..."` for binary data
- Multiline string literals: `"""..."""` with preserved whitespace
- Regular expression literals: `re"\d+\.\d+"`

## References

- LANGUAGE_SPECIFICATION.md (string type, literals section)
- Self-Hosting Feasibility Assessment (gap analysis)
- Python `str` type (design inspiration)
- Rust `std::fmt` module (format specifiers)

## Drawbacks

1. String interpolation adds parser complexity
2. Rich string API increases standard library surface area
3. Format specifier parsing is non-trivial

## Prior Art

- Python: f-strings, `.format()`, `str` methods
- Rust: `format!()`, `format_args!()`, `std::fmt`
- C#: string interpolation `$"{name}"`, `StringBuilder`
- JavaScript: template literals `` `${name}` ``
