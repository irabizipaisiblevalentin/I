# RFC-001: Standard Library Foundation

- **RFC ID**: 001
- **Author**: Irabizi Paisible Valentin
- **Status**: Draft
- **Created**: 2026-07-30
- **Updated**: 2026-07-30
- **I-Version**: 1.0
- **Category**: Standard Library

## Summary

Define a standard library module `urubuga` (foundation) providing file I/O, string manipulation, command-line argument access, and system interface capabilities required for compiler self-hosting.

## Motivation

### Problem Statement

The I language currently has no specified standard library. The LANGUAGE_SPECIFICATION.md defines types (`string`, `int`, `list<T>`, `map<K,V>`, etc.) but provides no operations on these types. A self-hosting compiler requires:

1. Reading and writing source files
2. String manipulation (slicing, searching, formatting)
3. Accessing command-line arguments
4. System-level operations (file system queries, process management)

Without these capabilities, the compiler cannot read its own source code or produce output.

### Current Workarounds

The Python-based bootstrap compiler handles all I/O and system interaction in Python. When rewriting compiler components in I, these capabilities must exist in the I standard library.

### Why a Language Change?

This is not a language syntax change — it is a standard library addition. Per the RFC threshold, new standard library modules require an RFC.

## Detailed Design

### Module: `urubuga` (Foundation)

#### File I/O

```i
shyiramo urubuga

# Read entire file as string
shyira source = urubuga.soma_dosive("main.i")

# Write string to file
urubuga.andika_dosive("output.i", source)

# Check if file exists
niba urubuga.dosive_ribaho("main.i")
    # file exists
iherezo

# List directory contents
shyira files = urubuga.uruti("src/")

# Get file metadata
shyira info = urubuga.umwirondoro("main.i")
urubuga.andika("File size: " + info.ubunini)
```

#### Console I/O

```i
# Print to stdout (with newline)
urubuga.andika("Muraho, Isi!")

# Print without newline
urubuga.andika_nta_umurongo("Enter name: ")

# Read line from stdin
shyira izina = urubuga.soma_umurongo()

# Read all from stdin
shyira contents = urubuga.soma_byose()
```

#### String Operations

```i
shyira message = "Muraho, Isi!"

# Length
shyira uburebure = message.uburebure()  # 12

# Slicing
shyira greeting = message.ice(0, 6)      # "Muraho"
shyira rest = message.ice(7)             # "Isi!"

# Search
shyira index = message.shaka("Isi")      # 7
shyira exists = message.ribamo("Hello")  # oya

# Replace
shyira updated = message.hindura("Isi", "Africa")

# Split
shyira parts = message.ma(" ")           # ["Muraho,", "Isi!"]

# Join
shyira joined = parts.unga(", ")         # "Muraho, Isi!"

# Case conversion
shyira lower = message.ntoya()           # "muraho, isi!"
shyira upper = message.nini()            # "MURAHO, ISI!"

# Trim
shyira trimmed = "  hello  ".koma()      # "hello"
shyira left = "  hello".koma_ibumoso()   # "hello"
shyira right = "hello  ".koma_iburyo()   # "hello"

# Check prefix/suffix
niba message.yatanguye("Muraho")
    # true
iherezo
niba message.yarangiye("!")
    # true
iherezo
```

#### String Formatting

```i
# Format with positional arguments
shyira name = "Alice"
shyira age = 30
shyira formatted = "{0} is {1} years old".forma(name, age)
# Result: "Alice is 30 years old"

# Named format
shyira formatted = "{izina} ni {imyaka}".forma(izina=name, imyaka=age)
```

#### Command-Line Arguments

```i
# Get all arguments
shyira args = urubuga.komandi_zemerera()
# args[0] = program name
# args[1..] = command-line arguments

# Get argument count
shyira count = args.uburebure()

# Check flag
niba urubuga.ibendera_ribaho("--verbose")
    # verbose mode
iherezo
```

#### Error Handling

```i
kora
    shyira source = urubuga.soma_dosive("main.i")
kubika error
    urubuga.andika("Error: " + error.ubutumwa)
    urubuga.guma(1)  # Exit with error code
iherezo
```

### Type Signatures

```
urubuga {
    # File I/O
    soma_dosive(path: string) -> string | gushyingura
    andika_dosive(path: string, content: string) -> void | gushyingura
    dosive_ribaho(path: string) -> bool
    uruti(path: string) -> list<string> | gushyingura
    umwirondoro(path: string) -> DosiveInfo | gushyingura

    # Console I/O
    andika(value: any) -> void
    andika_nta_umurongo(value: any) -> void
    soma_umurongo() -> string
    soma_byose() -> string

    # System
    guma(code: int) -> void
    komandi_zemerera() -> list<string>
    ibendera_ribaho(flag: string) -> bool
    igihe() -> int  # Unix timestamp

    # Environment
    ibidukikije() -> map<string, string>
    ibidukikije(izina: string) -> string | ubusa
}

igiceri DosiveInfo {
    izina: string
    nzira: string
    ubunini: int  # bytes
    guhindurwa: int  # timestamp
    dosive: bool
    ububiko: bool
}
```

### Standard Library Location

Modules will live in `src/stdlib/` with one file per module:

```
src/stdlib/
├── urubuga.i       # Foundation module
├── urutonde.i      # Collections (list, map, set)
└── ...
```

The compiler must resolve `shyiramo urubuga` to `src/stdlib/urubuga.i` by default.

### Implementation

The standard library will be implemented initially in Python (alongside the bootstrap compiler), then ported to I during Phase 1 of self-hosting.

- For file I/O: delegate to Python's `open()`, `os.path`, etc.
- For strings: delegate to Python's string methods
- For console: delegate to Python's `print()`, `input()`

## Alternatives Considered

### Alternative 1: Built-in Functions

Instead of a module, provide all I/O as built-in functions (like Go's `print`/`println`).

**Pros:** Simpler for beginners
**Cons:** Pollutes namespace, less organized, harder to document

### Alternative 2: Foreign Function Interface (FFI)

Define a C FFI and let users call libc directly.

**Pros:** Maximum flexibility
**Cons:** Unsafe, non-portable, complex for compiler self-hosting

### Alternative 3: No Standard Library (Keep in Python)

Keep all I/O in the Python bootstrap and only expose language features.

**Pros:** Simplest short-term
**Cons:** I programs cannot do anything useful independently; self-hosting impossible

## Migration Path

### Automatic Migration

No migration needed — this is a net-new addition.

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

1. Should `urubuga` be auto-imported or explicitly imported?
2. Should error handling use exceptions or result types?

## Future Possibilities

- Async I/O (`urubuga.soma_dosive_izindi()`)
- File system watcher
- Network I/O
- Process management

## References

- LANGUAGE_SPECIFICATION.md (string type definition)
- Self-Hosting Feasibility Assessment (gap analysis)
- Python `io` module, `os` module (implementation reference)

## Drawbacks

1. Increases compiler complexity (must resolve standard library imports)
2. Standard library must be maintained alongside language evolution
3. Initial implementation in Python may differ from eventual I implementation

## Prior Art

- Python: `open()`, `print()`, `sys.argv`
- Go: `os`, `fmt`, `strings` packages
- Rust: `std::fs`, `std::io`, `std::env` modules
