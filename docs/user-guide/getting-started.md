# Getting Started with I

Welcome to **I** — the world's first professional programming language designed around
Kinyarwanda. This guide gets you from zero to your first running programs in about 15
minutes.

## What is I?

I is a compiled programming language with natural Kinyarwanda keywords and a small,
readable standard library. Code reads like instructions:

```i
andika "Muraho, Isi!"
```

`andika` means *write* — it prints a value to the terminal.

I compiles source code to bytecode and runs it on a built-in virtual machine. The
toolchain is written in Python and installs cleanly with `pip`.

## Prerequisites

- **Python 3.10 or newer** (the 1.0.0 release is tested on Python 3.14)
- A terminal (PowerShell on Windows, `bash` on Linux/macOS)
- `pip` available on your PATH

Check your Python version:

```bash
python --version
```

## Installation

### Option A — Install from source (recommended for development)

```bash
git clone https://github.com/i-lang/i-lang.git
cd i-lang
python -m pip install -e .
```

### Option B — Install the release wheel

```bash
pip install i-lang
```

### Verify the installation

```bash
i --version
```

You should see:

```
I Programming Language Compiler v1.0.0
```

The package manager is invoked through Python:

```bash
python -m isoko.cli --version
```

You should see:

```
isoko 1.0.0
```

## Your First Program

Create a file named `hello.i`:

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

The `-r` (or `--run`) flag compiles the file and runs it. Without `-r`, `i` only
compiles the program to bytecode.

## A Closer Look

### Variables

Use `shyira` (*place*) for mutable variables and `shyira_ko` (*place firmly*) for
constants:

```i
shyira izina = "Jean"     # a string
shyira imyaka = 25        # an integer
shyira ipima = 3.5        # a float

shyira_ko IGIHUGU = "Rwanda"
```

### Functions

Use `umurimo` (*work*) to define a function and `subira` (*return*) to return a value.
Every block ends with `iherezo` (*end*):

```i
umurimo komeza(x: int) -> int
    subira x + 1
iherezo

andika komeza(41)   # prints 42
```

### Conditionals

`niba` (*if*), `cyangwa_niba` (*else if*), and `cyangwa` (*else*):

```i
shyira a = 10

niba a irenze 15
    andika "large"
cyangwa_niba a irenze 5
    andika "medium"
cyangwa
    andika "small"
iherezo
```

`irenze` means *is greater than*. The other comparison words are `munsi` / `munsi_ya`
(*less than*). Symbol comparison operators (`>`, `<`, `>=`, `<=`, `==`, `!=`) work too.

### Loops

`wihuse` (*hurry*) is a while loop:

```i
shyira i = 0
wihuse i munsi 5
    andika i
    i = i + 1
iherezo
```

`kuri ... muri ... kugeza ...` is a numeric for loop. The end value is exclusive:

```i
kuri i muri 0 kugeza 5
    andika i
iherezo
```

`buri ... muri ...` iterates over a list:

```i
buri izina muri ["Jean", "Aline", "Eric"]
    andika izina
iherezo
```

## Project Structure

A simple project looks like this:

```
my-project/
├── ilang.toml          # project manifest (created by `isoko init`)
├── src/
│   └── main.i          # entry point
└── tests/
    └── test_main.i     # tests
```

Create a project scaffold with the package manager:

```bash
python -m isoko.cli new my-project
python -m isoko.cli run my-project
```

## Standard Library

I ships with 44 standard-library modules covering text, math, collections, JSON, CSV,
HTTP, filesystem, cryptography, and more. The modules are Python-backed and import
from the `stdlib` package.

## What's Next?

- [Language Guide](language-guide.md) — the complete, verified syntax reference
- [Standard Library Reference](stdlib-reference.md) — the 44 modules and their functions
- [isoko Package Manager Guide](isoko-package-manager.md) — projects, builds, publishing
- [Toolchain Guide](toolchain-guide.md) — compiler flags, bytecode, debugging
- [Tutorials](../tutorials/level-1.md) — five guided levels with runnable examples
- [Examples](../../examples/) — a growing collection of `.i` programs

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `i` is not recognized as a command | The console script is not on PATH. Run `python -m compiler.compiler ...` instead, or reinstall with `python -m pip install -e .` |
| `Runtime Warning: 'compiler.compiler' found in sys.modules` | Cosmetic warning from `python -m compiler.compiler`; use the `i` entry point to avoid it |
| UTF-8 output looks wrong on Windows | Ensure the terminal uses UTF-8 (`chcp 65001`) |
