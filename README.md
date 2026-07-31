# I Programming Language

<div align="center">

**A programming language designed around Kinyarwanda**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**v1.0.0** — a stable, documented, tested release of the reference toolchain.

</div>

## Table of Contents

- [Mission](#mission)
- [Installation](#installation)
- [Your First Program](#your-first-program)
- [Language Overview](#language-overview)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Examples](#examples)
- [Architecture](#architecture)
- [Status & Roadmap](#status--roadmap)
- [Contributing](#contributing)
- [License](#license)

## Mission

Create a professional programming language with natural Kinyarwanda syntax that
empowers millions of African developers to build world-class software in their
native language, serving as a foundation for African technological independence.

## Installation

The reference implementation is a Python package. Python 3.10+ is required.

```bash
# Install the I toolchain
pip install i-lang

# Or build from source
git clone https://github.com/i-lang/i-lang.git
cd i-lang
python -m pip install -e .
```

This installs:

- the `i` compiler CLI (`i hello.i -r`, `i --version`)
- the `compiler`, `vm`, and `stdlib` Python packages for host integrations
- the `isoko` project manager (`python -m isoko.cli`)

## Your First Program

Create a file `hello.i`:

```i
# Hello World in I
andika "Muraho, Isi!"
```

Run it:

```bash
i hello.i -r
```

Output:

```
Muraho, Isi!
```

Prefer the module form if the `i` entry point is not on PATH:

```bash
python -m compiler.compiler hello.i -r
```

## Language Overview

Code reads like natural Kinyarwanda. Blocks open with a keyword and close with
`iherezo` (end); keywords are meaningful words rather than punctuation.

### Hello and values

```i
andika "Muraho, Isi!"      # print with newline
shyira izina = "Jean"      # mutable variable
shyira_ko LIMIT = 1000     # constant
```

### Conditionals

```i
shyira umwaka = 2024
niba umwaka irenze 2000
    andika "modern times"
cyangwa_niba umwaka irenze 1000
    andika "medieval"
cyangwa
    andika "ancient"
iherezo
```

### Loops

```i
kuri i muri 0 kugeza 10    # 0..9 (end is exclusive)
    andika i
iherezo

shyira n = 5
wihuse n irenze 0          # while
    andika n
    n = n - 1
iherezo

kugeza found               # do-while: body runs first
    shyira guess = uburengero(soma())
    found = guess == secret
iherezo
```

### Comparison operators

| I form | Meaning |
| --- | --- |
| `a irenze b` | `a > b` |
| `a munsi b` / `a munsi_ya b` | `a < b` |
| `a == b`, `a != b`, `a >= b`, `a <= b` | equality / ordering |
| `si a` | `!a` (boolean negation) |

> **Note (1.0.0):** logical operators `kandi` (and) and `cyangwa` (or) are
> declared keywords but are not yet implemented. Combine conditions with nested
> `niba` blocks.

### Example: Fibonacci

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

## Project Structure

The repository is a monorepo. The reference compiler lives in `src/`; the
framework and platform directories are separate workstreams.

```
src/compiler/     # Compiler pipeline (lexer, parser, semantic, codegen, ...)
src/vm/           # Virtual machine and runtime
src/stdlib/       # 44 Python standard-library modules + urubuga.i
src/isoko/        # isoko project manager (new/init/build/run/test/...)
src/ufa/          # Error diagnostics engine (E-codes)
docs/             # Architecture, specification, user guide, tutorials
examples/         # Single-topic examples + 15 example projects
frameworks/       # Framework workstreams (urubuga, ibiro, ububiko, ...)
tools/            # Tooling workstreams (formatter, linter, lsp, ...)
tests/            # Test suite
```

## Documentation

- **[Getting Started](docs/user-guide/getting-started.md)** — the 15-minute path
- **[Language Guide](docs/user-guide/language-guide.md)** — grammar, operators,
  built-ins, and known 1.0.0 limitations
- **[Tutorials](docs/tutorials/level-1.md)** — a 5-level tutorial series
- **[Standard Library Reference](docs/user-guide/stdlib-reference.md)** — all 44 modules
- **[isoko Guide](docs/user-guide/isoko-package-manager.md)** — project manager
- **[Toolchain Guide](docs/user-guide/toolchain-guide.md)** — CLI, bytecode, embedding
- **[API Reference](docs/user-guide/api-reference.md)** — host APIs
- **[Error Reference](docs/user-guide/error-reference.md)** — PARS/SEM/E-codes
- **[Migration Guide](docs/user-guide/migration-guide.md)** — 0.1.0 → 1.0.0
- **[FAQ](docs/user-guide/faq.md)**

## Examples

- `examples/hello.i`, `variables.i`, `functions.i`, `conditionals.i`,
  `loops.i`, `fibonacci.i` — single-topic basics
- [`examples/projects/`](examples/projects/) — 15 self-contained programs
  (fizzbuzz, primes, fibonacci, factorial, gcd/lcm, sum-of-digits, collatz,
  multiplication table, diamond pattern, binary converter, even-fibonacci sum,
  perfect numbers, palindromic primes, and an interactive guess-the-number
  game). Every example compiles and runs against 1.0.0 with verified output.

```bash
i examples/projects/fizzbuzz.i -r
```

## Architecture

The compiler pipeline is:

```
Source Code → Lexer → Parser → AST → Semantic Analyzer → Code Generator → Bytecode → VM
```

- `src/compiler/lexer` — tokenization, keyword table, E-code diagnostics
- `src/compiler/parser` — recursive-descent parser to AST
- `src/compiler/semantic` — symbol tables, type checking, imports
- `src/compiler/ir` — intermediate representation
- `src/compiler/optimization` — bytecode optimizer
- `src/compiler/codegen` — bytecode emission
- `src/vm` — stack-based virtual machine with a Python-accessible API

See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

## Status & Roadmap

**Current: v1.0.0 (released reference toolchain).** The core language compiles
and runs: keywords, functions, recursion, loops, lists, input, and string
handling are covered by 4,107 passing tests.

Known 1.0.0 limitations are documented in the
[Language Guide](docs/user-guide/language-guide.md#known-limitations) — notably
logical operators, `gukoma` inside `wihuse` loops, module execution, and struct
instantiation are not yet available. See [ROADMAP.md](ROADMAP.md) for the full
roadmap.

## Contributing

We welcome contributions. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and
[STYLE_GUIDE.md](STYLE_GUIDE.md). Run the test suite with:

```bash
python -m pytest tests
```

## License

MIT — see [LICENSE](LICENSE).

---

**I Programming Language** — *Kuvana Imana, Kubaka Icyo Turije* (From God,
Building What We Have)

Founder: **Irabizi Paisible Valentin** | Location: **Rwanda**
