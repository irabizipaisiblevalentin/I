# Standard Library Architecture

This document specifies the complete standard library of the I Programming Language, organized into modules with full API specifications.

## Table of Contents

- [Design Philosophy](#design-philosophy)
- [Module Organization](#module-organization)
- [Core Modules](#core-modules)
- [Text & String Modules](#text--string-modules)
- [Number Modules](#number-modules)
- [Collection Modules](#collection-modules)
- [Time & Date Modules](#time--date-modules)
- [File System Modules](#file-system-modules)
- [Network Modules](#network-modules)
- [Data Format Modules](#data-format-modules)
- [Database Modules](#database-modules)
- [System Modules](#system-modules)
- [Security Modules](#security-modules)
- [Compression Modules](#compression-modules)
- [Media Modules](#media-modules)
- [Concurrency Modules](#concurrency-modules)
- [FFI Modules](#ffi-modules)
- [Testing Modules](#testing-modules)
- [Debug Modules](#debug-modules)
- [Internationalization Modules](#internationalization-modules)

## Design Philosophy

1. **Small language, powerful stdlib**: The language core is minimal; the stdlib does the heavy lifting
2. **Consistent API**: All modules follow the same naming conventions and patterns
3. **Bilingual naming**: Functions use Kinyarwanda names; English aliases available
4. **Zero-cost abstractions**: High-level APIs compile to efficient code
5. **Composability**: Modules compose naturally through standard types
6. **Progressive complexity**: Simple operations are simple; complex operations are possible

## Module Organization

```
stdlib/
├── core/           # Core types and builtins
├── text/           # String and text processing
├── math/           # Mathematical functions
├── numbers/        # Numeric types and operations
├── collections/    # Data structures
├── time/           # Date and time
├── fs/             # File system
├── path/           # Path manipulation
├── process/        # Process management
├── system/         # System information
├── network/        # Networking
├── http/           # HTTP client/server
├── websocket/      # WebSocket support
├── json/           # JSON parsing/serialization
├── xml/            # XML parsing
├── yaml/           # YAML parsing
├── csv/            # CSV parsing
├── database/       # Database abstractions
├── sqlite/         # SQLite driver
├── postgres/       # PostgreSQL driver
├── mysql/          # MySQL driver
├── mongodb/        # MongoDB driver
├── compression/    # Compression algorithms
├── archive/        # Archive formats
├── image/          # Image processing
├── audio/          # Audio processing
├── video/          # Video processing
├── graphics/       # 2D/3D graphics
├── window/         # Window management
├── ui/             # UI widgets
├── terminal/       # Terminal I/O
├── logging/        # Logging
├── config/         # Configuration
├── env/            # Environment
├── crypto/         # Cryptography
├── security/       # Security utilities
├── random/         # Random number generation
├── testing/        # Testing framework
├── benchmark/      # Benchmarking
├── reflect/        # Reflection
├── serialization/  # Serialization
├── concurrency/    # Concurrency primitives
├── threading/      # Threading
├── async/          # Async/await
├── parallel/       # Parallel processing
├── ffi/            # Foreign function interface
├── memory/         # Memory management
├── unicode/        # Unicode utilities
├── i18n/           # Internationalization
├── locale/         # Locale support
├── package/        # Package management
├── compiler/       # Compiler APIs
├── vm/             # VM APIs
├── debug/          # Debug utilities
└── meta/           # Metaprogramming
```

## Core Modules

### Module: `core`

Purpose: Core types, builtins, and fundamental operations.

```
core/
├── builtin.i       # Built-in functions (print, input, etc.)
├── types.i         # Core type definitions
├── errors.i        # Error types
├── option.i        # Option<T> type
├── result.i        # Result<T, E> type
├── either.i        # Either<L, R> type
├── range.i         # Range types
├── slice.i         # Slice operations
├── ptr.i           # Pointer operations
└── markers.i       # Marker traits (Send, Sync, etc.)
```

#### API: `core.builtin`

```
# Print to stdout
andika(values: Any..., sep: string = " ", end: string = "\n") -> void

# Print to stderr
andika_inkeri(values: Any..., sep: string = " ", end: string = "\n") -> void

# Read line from stdin
soma_umurongo(prompt: string? = null) -> string?

# Read all from stdin
soma() -> string

# Type of value
ubwoko(value: Any) -> Type

# String representation
imiterere(value: Any) -> string

# Length of collection/string
uburebure(value: Any) -> int

# Absolute value
igiceri(x: int | float) -> int | float

# Minimum of values
nto(x: Any, y: Any) -> Any

# Maximum of values
nke(x: Any, y: Any) -> Any

# Enumerate collection
pera(iterable: Iterable<T>) -> List<(int, T)>

# Zip two iterables
zippe(iterable1: Iterable<A>, iterable2: Iterable<B>) -> List<(A, B)>

# Sorted collection
shyijwe(iterable: Iterable<T>, comparator: (T, T) -> int? = null) -> List<T>

# Reversed collection
subiyembi(iterable: Iterable<T>) -> List<T>

# Flatten nested collections
gukemura(iterable: Iterable<Iterable<T>>) -> List<T>

# Apply function to each element
shira_ukuri(iterable: Iterable<T>, f: (T) -> U) -> List<U>

# Filter elements
gushungura(iterable: Iterable<T>, predicate: (T) -> bool) -> List<T>

# Reduce collection
guhindura(iterable: Iterable<T>, f: (T, U) -> U, initial: U) -> U

# Check if any element satisfies predicate
hitamwo(iterable: Iterable<T>, predicate: (T) -> bool) -> bool

# Check if all elements satisfy predicate
vyose(iterable: Iterable<T>, predicate: (T) -> bool) -> bool

# Find first element satisfying predicate
shaka(iterable: Iterable<T>, predicate: (T) -> bool) -> T?

# Count elements satisfying predicate
ibara(iterable: Iterable<T>, predicate: (T) -> bool) -> int

# Check if element exists
iri_muri(iterable: Iterable<T>, element: T) -> bool
```

#### API: `core.option`

```
igiceri Option<T>
    # Unwrap the value (panics if None)
    gusohoka(self) -> T
    
    # Unwrap with default
    cyangwa_ibikurwa(self, default: T) -> T
    
    # Unwrap or compute
    cyangwa_kora(self, f: () -> T) -> T
    
    # Map over value
    guhindura(self, f: (T) -> U) -> Option<U>
    
    # Flat map
    guhindura_kubiri(self, f: (T) -> Option<U>) -> Option<U>
    
    # Filter
    gushungura(self, predicate: (T) -> bool) -> Option<T>
    
    # Is Some
    iri_ho(self) -> bool
    
    # Is None
    ntiri_ho(self) -> bool
    
    # Unwrap or null
    cyangwa_null(self) -> T?
iherezo
```

#### API: `core.result`

```
igiceri Result<T, E>
    # Unwrap the value (panics if Err)
    gusohoka(self) -> T
    
    # Unwrap with default
    cyangwa_ibikurwa(self, default: T) -> T
    
    # Unwrap error (panics if Ok)
    gusohoka_ikosa(self) -> E
    
    # Map over value
    guhindura(self, f: (T) -> U) -> Result<U, E>
    
    # Map over error
    guhindura_ikosa(self, f: (E) -> F) -> Result<T, F>
    
    # Flat map
    guhindura_kubiri(self, f: (T) -> Result<U, E>) -> Result<U, E>
    
    # Is Ok
    biri_neho(self) -> bool
    
    # Is Err
    ntibiri_neho(self) -> bool
    
    # Unwrap or null
    cyangwa_null(self) -> T?
iherezo
```

## Text & String Modules

### Module: `text`

Purpose: String manipulation, pattern matching, and text processing.

```
text/
├── string.i        # String operations
├── builder.i       # String builder
├── format.i        # String formatting
├── pattern.i       # Pattern matching
├── regex.i         # Regular expressions
├── parse.i         # String parsing
├── encode.i        # Encoding (base64, hex, etc.)
└── template.i      # String templates
```

#### API: `text.string`

```
# String length (UTF-8 codepoints)
uburebure(s: string) -> int

# Byte length
uburebure_bwa_byte(s: string) -> int

# Character at index
ikaratare(s: string, index: int) -> char

# Substring
igice(s: string, start: int, end: int? = null) -> string

# Contains
irimo(s: string, substring: string) -> bool

# Starts with
itangiriro(s: string, prefix: string) -> bool

# Ends with
irangira(s: string, suffix: string) -> bool

# Index of
umurongo(s: string, substring: string) -> int?

# Last index of
umurongo_ibikurwa(s: string, substring: string) -> int?

# Replace
gusimbura(s: string, old: string, new: string) -> string

# Split
tandukanya(s: string, delimiter: string) -> List<string>

# Join
ungurira(parts: List<string>, separator: string) -> string

# Trim
gukera(s: string) -> string

# Trim start
gutangira(s: string) -> string

# Trim end
gukomeza(s: string) -> string

# Lowercase
hasi(s: string) -> string

# Uppercase
hejuru(s: string) -> string

# Capitalize
igiciro(s: string) -> string

# Title case
umutwe(s: string) -> string

# Reverse
subiyembi(s: string) -> string

# Repeat
kubira(s: string, count: int) -> string

# Pad left
gufata_ibumoso(s: string, length: int, char: char = ' ') -> string

# Pad right
gufata_iburyo(s: string, length: int, char: char = ' ') -> string

# Center
gufata_abagatati(s: string, length: int, char: char = ' ') -> string

# Is empty
ntirafungura(s: string) -> bool

# Is whitespace only
ni_umwanya(s: string) -> bool

# Is numeric
ni_inamba(s: string) -> bool

# Is alphabetic
ni_inyandiko(s: string) -> bool

# Is alphanumeric
ni_inamba_cyangwa_inyandiko(s: string) -> bool

# Count occurrences
ibara(s: string, substring: string) -> int

# Lines
imirongo(s: string) -> List<string>

# Words
amagambo(s: string) -> List<string>

# Truncate
gufunga(s: string, max_length: int, suffix: string = "...") -> string
```

#### API: `text.builder`

```
igiceri StringBuilder
    __init__(capacity: int = 16)
    
    # Append value
    ongera(self, value: Any) -> Self
    
    # Append line
    ongera_umurongo(self, value: Any) -> Self
    
    # Append format
    ongera_gufungura(self, format: string, args: Any...) -> Self
    
    # Clear
    hesha(self) -> Self
    
    # Convert to string
    kuba_string(self) -> string
    
    # Length
    uburebure(self) -> int
    
    # Is empty
    ntirafungura(self) -> bool
iherezo
```

#### API: `text.format`

```
# Format string with values
gufungura(template: string, values: Map<string, Any>) -> string

# Format with positional args
gufungura_ibintu(template: string, args: Any...) -> string

# Number formatting
gufungura_inamba(n: int | float, format: string) -> string

# Date formatting
gufungura_igeno(date: DateTime, format: string) -> string

# Format specifiers:
# {name} - named argument
# {0}, {1} - positional argument
# {value:.2f} - format specifier
# {value:>10} - right-aligned
# {value:<10} - left-aligned
# {value:^10} - centered
```

#### API: `text.regex`

```
igiceri Regex
    # Compile pattern
    __init__(pattern: string, flags: int = 0)
    
    # Match at position
    girikana(self, text: string, position: int = 0) -> Match?
    
    # Match entire string
    girikana_vyose(self, text: string) -> Match?
    
    # Find all matches
    shaka_vyose(self, text: string) -> List<Match>
    
    # Replace all
    gusimbura_vyose(self, text: string, replacement: string) -> string
    
    # Split
    tandukanya(self, text: string) -> List<string>
    
    # Is match
    irimo(self, text: string) -> bool
iherezo

igiceri Match
    value: string           # Full match
    start: int              # Start position
    end: int                # End position
    groups: List<string>    # Capture groups
    
    # Get named group
    igice(self, name: string) -> string?
iherezo
```

## Number Modules

### Module: `math`

Purpose: Mathematical functions and constants.

```
math/
├── basic.i         # Basic math operations
├── trigonometry.i  # Trigonometric functions
├── statistics.i    # Statistical functions
├── linear.i        # Linear algebra
├── complex.i       # Complex numbers
├── bigdecimal.i    # Arbitrary precision decimals
└── bigint.i        # Arbitrary precision integers
```

#### API: `math.basic`

```
# Constants
igiceri PI: float = 3.141592653589793
igiceri E: float = 2.718281828459045
igiceri TAU: float = 6.283185307179586
igiceri LN2: float = 0.6931471805599453
igiceri LN10: float = 2.302585092994046
igiceri SQRT2: float = 1.4142135623730951

# Absolute value
igiceri(x: int) -> int
igiceri(x: float) -> float

# Power
kuba(base: float, exponent: float) -> float

# Square root
imisusire(x: float) -> float

# Cube root
imisusire_ya_gatatu(x: float) -> float

# Natural logarithm
logib自然(x: float) -> float

# Log base 2
logib_2(x: float) -> float

# Log base 10
logib_10(x: float) -> float

# Exponential
exibonentiali(x: float) -> float

# Ceiling
hejuru(x: float) -> int

# Floor
hasi(x: float) -> int

# Round
igice_cyose(x: float) -> int

# Min/Max
nto(values: List<int | float>) -> int | float
nke(values: List<int | float>) -> int | float

# Clamp
gufunga(value: int | float, min: int | float, max: int | float) -> int | float

# GCD (Greatest Common Divisor)
igiciro_cyose(x: int, y: int) -> int

# LCM (Least Common Multiple)
igiciro_gito(x: int, y: int) -> int

# Factorial
ifactoriyeli(n: int) -> int

# Is even
ni_pera(x: int) -> bool

# Is odd
ni_bitari_pera(x: int) -> bool

# Is prime
ni_icyiciro(x: int) -> bool

# Next prime
icyiciro_gikurikira(x: int) -> int
```

#### API: `math.trigonometry`

```
# Trigonometric functions
sinusi(x: float) -> float
kosinusi(x: float) -> float
tanjeniti(x: float) -> float

# Inverse trigonometric
asinusi(x: float) -> float
akosinusi(x: float) -> float
atanjeniti(x: float) -> float
atan2(y: float, x: float) -> float

# Hyperbolic
sinusi_hyperboliki(x: float) -> float
kosinusi_hyperboliki(x: float) -> float
tanjeniti_hyperboliki(x: float) -> float

# Convert degrees to radians
degree_ku_radiani(degrees: float) -> float

# Convert radians to degrees
radiani_ku_degree(radians: float) -> float
```

#### API: `math.statistics`

```
# Mean
igitsindaho(values: List<float>) -> float

# Median
igitsindaho_ya_hagati(values: List<float>) -> float

# Mode
igitsindaho_cyane(values: List<float>) -> float

# Standard deviation
uburambe_bwa_standardi(values: List<float>) -> float

# Variance
uburambe(values: List<float>) -> float

# Sum
ibara(values: List<int | float>) -> int | float

# Product
igiciro(values: List<int | float>) -> int | float

# Percentile
ibya_kumi(values: List<float>, p: float) -> float

# Correlation
ubukungurane(values1: List<float>, values2: List<float>) -> float

# Linear regression
isobanuririre_ya_linear(values1: List<float>, values2: List<float>) -> (float, float)
```

## Collection Modules

### Module: `collections`

Purpose: Data structures and collection operations.

```
collections/
├── list.i          # List<T> operations
├── dict.i          # Dict<K, V> operations
├── set.i           # Set<T> operations
├── stack.i         # Stack<T> data structure
├── queue.i         # Queue<T> data structure
├── deque.i         # Deque<T> data structure
├── priority.i      # Priority queue
├── linked_list.i   # Linked list
├── tree.i          # Tree data structure
├── graph.i         # Graph data structure
├── cache.i         # Cache data structures
└── iter.i          # Iterator utilities
```

#### API: `collections.list`

```
# Create list
gutoranya(elements: T...) -> List<T>
gutoranya_uburebure(length: int, default: T) -> List<T>
gutoranya_inzero(length: int) -> List<int>

# Access
igice(list: List<T>, start: int, end: int? = null) -> List<T>

# Search
iri_muri(list: List<T>, element: T) -> bool
umurongo(list: List<T>, element: T) -> int?
shaka(list: List<T>, predicate: (T) -> bool) -> T?

# Transform
gushira_ukuri(list: List<T>, f: (T) -> U) -> List<U>
gushungura(list: List<T>, predicate: (T) -> bool) -> List<T>
guhindura(list: List<T>, f: (T, U) -> U, initial: U) -> U

# Sort
shyijwe(list: List<T>, comparator: (T, T) -> int? = null) -> List<T>
shyijwe_na_kintu(list: List<T>, key: (T) -> K) -> List<T>

# Manipulation
ongera(list: List<T>, element: T) -> void
ongera_vyose(list: List<T>, elements: List<T>) -> void
siba(list: List<T>, index: int) -> T
siba_element(list: List<T>, element: T) -> bool

# Statistics
nto(list: List<T>) -> T?
nke(list: List<T>) -> T?
ibara(list: List<T>) -> int

# Conversion
kuba_mappe(list: List<T>, key: (T) -> K) -> Map<K, T>
kuba_mappe_ibibitsa(list: List<T>, key: (T) -> K) -> Map<K, List<T>>
```

#### API: `collections.dict`

```
# Create dict
ikarita(pairs: List<(K, V)>) -> Map<K, V>
ikarita_ibikurwa() -> Map<K, V>

# Access
gushaka(map: Map<K, V>, key: K) -> V?
gushaka_cyangwa(map: Map<K, V>, key: K, default: V) -> V

# Modify
shyiramo(map: Map<K, V>, key: K, value: V) -> void
siba_ikintu(map: Map<K, V>, key: K) -> bool

# Query
iriho_ikintu(map: Map<K, V>, key: K) -> bool
amakoresha(map: Map<K, V>) -> List<K>
ibintu(map: Map<K, V>) -> List<V>
ibintu_vyose(map: Map<K, V>) -> List<(K, V)>

# Transform
gushira_ukuri(map: Map<K, V>, f: (K, V) -> (K2, V2)) -> Map<K2, V2>
gushungura(map: Map<K, V>, predicate: (K, V) -> bool) -> Map<K, V>
```

#### API: `collections.stack`

```
igiceri Stack<T>
    __init__()
    
    # Push element
    ongera(self, element: T) -> void
    
    # Pop element
    gukura(self) -> T?
    
    # Peek
    reba(self) -> T?
    
    # Is empty
    ntirafungura(self) -> bool
    
    # Size
    uburebure(self) -> int
    
    # Clear
    hesha(self) -> void
iherezo
```

#### API: `collections.queue`

```
igiceri Queue<T>
    __init__(capacity: int = 0)
    
    # Enqueue
    ongera(self, element: T) -> void
    
    # Dequeue
    gukura(self) -> T?
    
    # Peek
    reba(self) -> T?
    
    # Is empty
    ntirafungura(self) -> bool
    
    # Size
    uburebure(self) -> int
iherezo
```

## Time & Date Modules

### Module: `time`

Purpose: Date, time, duration, and timezone operations.

```
time/
├── datetime.i      # DateTime type
├── duration.i      # Duration type
├── timezone.i      # Timezone support
├── instant.i       # Instant in time
├── timer.i         # Timer utilities
└── cron.i          # Cron expression parsing
```

#### API: `time.datetime`

```
igiceri DateTime
    # Components
    year: int
    month: int         # 1-12
    day: int           # 1-31
    hour: int          # 0-23
    minute: int        # 0-59
    second: int        # 0-59
    millisecond: int   # 0-999
    
    # Create
    __init__(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0, millisecond: int = 0)
    
    # Current time
    @staticmethod
    noneho() -> DateTime
    
    # Parse from string
    @staticmethod
    girikana(format: string, text: string) -> DateTime?
    
    # Format
    gufungura(self, format: string) -> string
    
    # Add duration
   ongera(self, duration: Duration) -> DateTime
    
    # Subtract
    gukura(self, other: DateTime | Duration) -> DateTime | Duration
    
    # Comparison
    compare(self, other: DateTime) -> int
    
    # Unix timestamp
    timestamp(self) -> int
    
    # Day of week
    umunsi_wa_sinduku(self) -> int  # 0=Sunday, 6=Saturday
    
    # Is leap year
    ni_ukwira(self) -> bool
    
    # Days in month
    iminsi_ya_monthi(self) -> int
iherezo

# Format specifiers:
# YYYY - 4-digit year
# MM - 2-digit month
# DD - 2-digit day
# HH - 2-digit hour (24h)
# hh - 2-digit hour (12h)
# mm - 2-digit minute
# ss - 2-digit second
# SSS - 3-digit millisecond
# AM/PM - AM/PM marker
```

#### API: `time.duration`

```
igiceri Duration
    # Create
    @staticmethod
    milisecondi(ms: int) -> Duration
    
    @staticmethod
    amaseconda(s: int) -> Duration
    
    @staticmethod
    miniti(m: int) -> Duration
    
    @staticmethod
    amasaha(h: int) -> Duration
    
    @staticmethod
    iminsi(d: int) -> Duration
    
    @staticmethod
    ibyumweru(w: int) -> Duration
    
    @staticmethod
    amezi(m: int) -> Duration
    
    @staticmethod
    imyaka(y: int) -> Duration
    
    # Components
    milisecondi(self) -> int
    amaseconda(self) -> float
    miniti(self) -> float
    amasaha(self) -> float
    iminsi(self) -> float
    
    # Arithmetic
    ongera(self, other: Duration) -> Duration
    gukura(self, other: Duration) -> Duration
    kuba(self, factor: float) -> Duration
    
    # Comparison
    compare(self, other: Duration) -> int
    
    # Is zero
    ni_zero(self) -> bool
iherezo
```

## File System Modules

### Module: `fs`

Purpose: File system operations.

```
fs/
├── file.i          # File operations
├── directory.i     # Directory operations
├── path.i          # Path manipulation
├── watch.i         # File watching
├── temp.i          # Temporary files
└── permissions.i   # File permissions
```

#### API: `fs.file`

```
igiceri File
    # Open
    @staticmethod
    fungura(path: string, mode: string = "r") -> File
    
    # Read
    soma(self) -> string
    soma_bytes(self) -> bytes
    soma_umurongo(self) -> string?
    soma_umurongo_vyose(self) -> List<string>
    
    # Write
    andika(self, content: string) -> void
    andika_bytes(self, content: bytes) -> void
    andika_umurongo(self, line: string) -> void
    
    # Seek
    gushaka(self, offset: int, whence: int = 0) -> int
    
    # Tell
    igiciro(self) -> int
    
    # Close
    fungura(self) -> void
    
    # Is open
    iri_ho(self) -> bool
    
    # Size
    ingano(self) -> int
    
    # Flush
    guhindura(self) -> void
iherezo

# File modes:
# "r" - read
# "w" - write (truncate)
# "a" - append
# "r+" - read/write
# "w+" - read/write (truncate)
# "a+" - read/append
# "rb" - read binary
# "wb" - write binary
```

#### API: `fs.directory`

```
# Create directory
gukora(path: string, recursive: bool = true) -> void

# List directory
soma_imyanya(path: string) -> List<string>

# List directory with info
soma_imyanya_n_amakuru(path: string) -> List<DirEntry>

# Remove directory
gusiba(path: string, recursive: bool = false) -> void

# Copy directory
gukoporora(source: string, destination: string) -> void

# Move directory
guhindura(source: string, destination: string) -> void

# Check if directory exists
iriho(path: string) -> bool

# Current working directory
ubwo uhariho() -> string

# Change working directory
guhindura_ubwo(path: string) -> void

igiceri DirEntry
    name: string
    path: string
    is_file: bool
    is_dir: bool
    is_symlink: bool
    size: int
    modified: DateTime
    created: DateTime
iherezo
```

## Network Modules

### Module: `http`

Purpose: HTTP client and server.

```
http/
├── client.i        # HTTP client
├── server.i        # HTTP server
├── request.i       # Request type
├── response.i      # Response type
├── headers.i       # Headers type
├── router.i        # URL router
├── middleware.i     # Middleware
├── cookie.i        # Cookie handling
└── session.i       # Session management
```

#### API: `http.client`

```
# GET request
igiriho(url: string, headers: Map<string, string> = {}) -> Response

# POST request
shyiramo(url: string, body: string | bytes, headers: Map<string, string> = {}) -> Response

# PUT request
gushyiraho(url: string, body: string | bytes, headers: Map<string, string> = {}) -> Response

# PATCH
guhindura(url: string, body: string | bytes, headers: Map<string, string> = {}) -> Response

# DELETE
siba(url: string, headers: Map<string, string> = {}) -> Response

# HEAD
umutwe(url: string, headers: Map<string, string> = {}) -> Response

# OPTIONS
uburyo(url: string, headers: Map<string, string> = {}) -> Response

igiceri Request
    method: string
    url: string
    headers: Headers
    body: bytes?
    query: Map<string, string>
    
    # Build request
    @staticmethod
    builder() -> RequestBuilder
iherezo

igiceri Response
    status: int
    headers: Headers
    body: bytes
    
    # Get body as string
    text(self) -> string
    
    # Get body as JSON
    json(self) -> Any
    
    # Check status
    iri_neho(self) -> bool  # 200-299
    ntago_iri_neho(self) -> bool
    
    # Stream body
    stream(self) -> Stream<bytes>
iherezo
```

#### API: `http.server`

```
igiceri Server
    __init__(host: string = "0.0.0.0", port: int = 8080)
    
    # Add route
    route(self, method: string, path: string, handler: Handler) -> Self
    
    # Add middleware
    middleware(self, mw: Middleware) -> Self
    
    # Start serving
    gutangira(self) -> void
    
    # Stop serving
    guhagarika(self) -> void
    
    # Static files
    files(self, path: string, directory: string) -> Self
iherezo

# Route handlers
type Handler = (Request) -> Response
type AsyncHandler = (Request) -> Future<Response>
type Middleware = (Request, Handler) -> Response
```

## Data Format Modules

### Module: `json`

Purpose: JSON parsing and serialization.

```
json/
├── parser.i        # JSON parser
├── serializer.i    # JSON serializer
├── value.i         # JSON value type
└── path.i          # JSON path queries
```

#### API: `json`

```
# Parse JSON string
gukemura(text: string) -> Any

# Serialize to JSON
gufungura_json(value: Any, pretty: bool = false) -> string

# Parse with type
gukemura_na_ubwoko<T>(text: string) -> T?

# Validate
iriho(text: string) -> bool

igiceri JsonValue
    kind: JsonKind
    
    # Access
    igice(self, index: int) -> JsonValue?
    igice(self, key: string) -> JsonValue?
    
    # Convert
    kuba_string(self) -> string?
    kuba_int(self) -> int?
    kuba_float(self) -> float?
    kuba_bool(self) -> bool?
    kuba_list(self) -> List<JsonValue>?
    kuba_dict(self) -> Map<string, JsonValue>?
iherezo

JsonKind enum {
    STRING
    NUMBER
    BOOLEAN
    NULL
    ARRAY
    OBJECT
}
```

## Database Modules

### Module: `database`

Purpose: Database abstraction layer.

```
database/
├── connection.i    # Connection interface
├── query.i         # Query builder
├── result.i        # Result set
├── pool.i          # Connection pool
├── migration.i     # Schema migration
└── model.i         # ORM model
```

#### API: `database`

```
igiceri Connection
    # Execute query
    gutangira(self, query: string, params: List<Any> = {}) -> Result
    
    # Prepared statement
    itegura(self, query: string) -> Statement
    
    # Transaction
    ikigo(self) -> Transaction
    
    # Close
    gufungura(self) -> void
iherezo

igiceri Statement
    gutangira(self, params: List<Any> = {}) -> Result
    gutangira_ikindi(self, params: List<Any> = {}) -> Result
iherezo

igiceri Transaction
    gutangira(self, query: string, params: List<Any> = {}) -> Result
    gukomeza(self) -> void
    gusubiza(self) -> void
iherezo

igiceri Result
    affected_rows: int
    last_insert_id: int
    
    # Fetch rows
    somera(self) -> List<Map<string, Any>>
    somera_imwe(self) -> Map<string, Any>?
    
    # Iterate
    iterate(self) -> Iterator<Map<string, Any>>
iherezo

# Query builder
igiceri Query
    @staticmethod
    guhitamwo(table: string) -> Query
    @staticmethod
    shyiramo(table: string, data: Map<string, Any>) -> Query
    @staticmethod
    guhindura(table: string, data: Map<string, Any>) -> Query
    @staticmethod
    siba(table: string) -> Query
    
    where(self, condition: string, params: Any...) -> Query
    igice(self, offset: int, limit: int) -> Query
    shyijwe(self, column: string, direction: string = "ASC") -> Query
    kuba_string(self) -> (string, List<Any>)
iherezo
```

## Security Modules

### Module: `crypto`

Purpose: Cryptographic operations.

```
crypto/
├── hash.i          # Hashing
├── hmac.i          # HMAC
├── cipher.i        # Symmetric encryption
├── asymmetric.i    # Asymmetric encryption
├── sign.i          # Digital signatures
├── certificate.i   # Certificate handling
├── random.i        # Cryptographic random
└── password.i      # Password hashing
```

#### API: `crypto.hash`

```
# Hash algorithms
igiceri Hasher
    @staticmethod
    md5() -> Hasher
    @staticmethod
    sha1() -> Hasher
    @staticmethod
    sha256() -> Hasher
    @staticmethod
    sha384() -> Hasher
    @staticmethod
    sha512() -> Hasher
    
    # Update with data
    update(self, data: string | bytes) -> Self
    
    # Finalize and get hash
    gusohoka(self) -> bytes
    
    # Get hex string
    hex(self) -> string
iherezo

# Convenience functions
hash_md5(data: string | bytes) -> string
hash_sha1(data: string | bytes) -> string
hash_sha256(data: string | bytes) -> string
```

#### API: `crypto.cipher`

```
igiceri Cipher
    @staticmethod
    aes_256_gcm(key: bytes) -> Cipher
    
    # Encrypt
    burya(self, plaintext: bytes, aad: bytes = empty_bytes) -> (bytes, bytes)
    
    # Decrypt
    subiza(self, ciphertext: bytes, nonce: bytes, aad: bytes = empty_bytes) -> bytes
iherezo
```

## Concurrency Modules

### Module: `concurrency`

Purpose: Concurrency primitives.

```
concurrency/
├── channel.i       # Channels
├── mutex.i         # Mutex
├── waitgroup.i     # Wait groups
├── atomics.i       # Atomic operations
├── once.i          # Execute once
└── semaphore.i     # Semaphore
```

#### API: `concurrency.channel`

```
igiceri Channel<T>
    # Create bounded channel
    @staticmethod
    gukora(uburebure: int) -> Channel<T>
    
    # Create unbounded channel
    @staticmethod
    ntibufungura() -> Channel<T>
    
    # Send value
    kohereza(self, value: T) -> void
    
    # Receive value
    akira(self) -> T
    
    # Try receive (non-blocking)
    gerageza_akira(self) -> T?
    
    # Close channel
    gufungura(self) -> void
    
    # Is closed
    irifunguye(self) -> bool
iherezo
```

#### API: `concurrency.mutex`

```
igiceri Mutex<T>
    __init__(value: T)
    
    # Lock and access
    fungura(self) -> MutexGuard<T>
    
    # Try lock
    gerageza_fungura(self) -> MutexGuard<T>?
iherezo

igiceri MutexGuard<T>
    # Dereference
    reba(self) -> &T
    reba_yanditswe(self) -> &mut T
iherezo
```

## FFI Modules

### Module: `ffi`

Purpose: Foreign function interface.

```
ffi/
├── lib.i           # Dynamic library loading
├── call.i          # Function calling
├── types.i         # FFI type mapping
├── struct.i        # C struct mapping
└── callback.i      # Callback functions
```

#### API: `ffi`

```
# Load dynamic library
igiceri Library
    @staticmethod
    fungura(path: string) -> Library
    
    # Get function
    umurimo(self, name: string, return_type: Type, param_types: List<Type>) -> Function
    
    # Get global variable
    igiciro(self, name: string, type: Type) -> Ref<Any>
    
    # Close
    gufungura(self) -> void
iherezo

igiceri Function
    # Call function
    gutangira(self, args: Any...) -> Any
iherezo
```

## Testing Modules

### Module: `testing`

Purpose: Testing framework.

```
testing/
├── test.i          # Test runner
├── assert.i        # Assertions
├── mock.i          # Mocking
├── fixture.i       # Test fixtures
├── property.i      # Property-based testing
├── snapshot.i      # Snapshot testing
└── coverage.i      # Code coverage
```

#### API: `testing`

```
# Test function
igiceri TestSuite
    igiciro(name: string) -> Self
    
    gutangira(self, name: string, test_fn: () -> void) -> Self
    gusunika(self, name: string, test_fn: () -> void) -> Self
    
    # Before/after each
    mbere_yo_buri(self, setup: () -> void) -> Self
    nyuma_yo_buri(self, teardown: () -> void) -> Self
    
    # Before/after all
    mbere_yo_vyose(self, setup: () -> void) -> Self
    nyuma_yo_vyose(self, teardown: () -> void) -> Self
    
    # Run tests
    gutangira(self) -> TestResult
iherezo

# Assertions
gereranya(actual: Any, expected: Any) -> void
ntigereranya(actual: Any, expected: Any) -> void
iri_ho(condition: bool, message: string = "") -> void
ntiri_ho(condition: bool, message: string = "") -> void
panics(fn: () -> void) -> void
ntipanics(fn: () -> void) -> void

# Time assertion
igice_cyose(fn: () -> void, max_duration: Duration) -> void
```

## Debug Modules

### Module: `debug`

Purpose: Debugging utilities.

```
debug/
├── stacktrace.i    # Stack trace
├── memory.i        # Memory inspection
├── profile.i       # Profiling
├── trace.i         # Execution tracing
└── breakpoint.i    # Breakpoints
```

#### API: `debug`

```
# Stack trace
stacktrace() -> string

# Breakpoint
gukata() -> void

# Memory info
amakuru_ya_memory() -> MemoryInfo

# Execution trace
gukurikirana(message: string) -> void

# Debug print
andika_ikosa(values: Any...) -> void

igiceri MemoryInfo
    heap_used: int
    heap_total: int
    stack_used: int
    stack_total: int
    gc_count: int
iherezo
```

## Implementation Strategy

### Phase 1: Core (Months 1-3)
- `core` - Builtins, Option, Result
- `text` - String operations
- `math` - Basic math
- `collections` - List, Dict, Set
- `fs` - File operations
- `time` - DateTime, Duration

### Phase 2: Data (Months 3-6)
- `json` - JSON parsing
- `csv` - CSV parsing
- `xml` - XML parsing
- `yaml` - YAML parsing
- `database` - Database abstraction
- `config` - Configuration

### Phase 3: Network (Months 6-9)
- `http` - HTTP client/server
- `network` - TCP/UDP
- `websocket` - WebSocket
- `crypto` - Cryptography

### Phase 4: System (Months 9-12)
- `process` - Process management
- `system` - System info
- `concurrency` - Channels, mutexes
- `threading` - Thread management
- `async` - Async/await
- `ffi` - Foreign function interface

### Phase 5: Advanced (Months 12+)
- `image` - Image processing
- `graphics` - Graphics
- `terminal` - Terminal UI
- `compression` - Compression
- `i18n` - Internationalization

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
