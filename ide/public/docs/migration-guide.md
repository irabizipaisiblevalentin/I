# Migration Guide: 0.1.0 → 1.0.0

This guide helps projects and integrations move from the 0.1.0 milestone to the stable
1.0.0 release. The language syntax did not change; the differences are in packaging,
tooling, and newly supported constructs.

## What Changed in 1.0.0

| Area | 0.1.0 | 1.0.0 |
| --- | --- | --- |
| Version | `0.1.0` | `1.0.0` everywhere (`pyproject`, all 8 package `__version__`, CLI `--version`) |
| Package layout | packages discovered from repository root | `packages.find where = ["src"]` — all 15 packages under `src/` |
| Wheel contents | empty (`where = ["."]`) | all packages + `stdlib/urubuga.i` + `py.typed` |
| Install | — | `pip install -e .` or `pip install i-program` |
| Compiler CLI | `python -m compiler.compiler` | `i` console script (module form still works) |
| Package manager | — | `python -m isoko.cli` |
| Runtime | — | function dispatch, recursion, scope cleanup, for/for-each fixes |
| Language | — | `andika` statement; word operators `irenze`, `munsi`, `munsi_ya` |
| Classifiers | development | `5 - Production/Stable` |

## Updating Install Commands

Replace:

```bash
pip install .
```

with:

```bash
python -m pip install -e .        # development
pip install i-program                # release
```

From the repository root, `python -m pip install -e .` installs the `i` console
script and places all packages on the import path.

## Invoking Tools

Prefer the console script for the compiler:

```bash
i hello.i -r          # new
python -m compiler.compiler hello.i -r   # still works
```

The package manager is always module-invoked:

```bash
python -m isoko.cli --help
```

## Using the New Language Features

### `andika` print statement

Printing is now a first-class statement:

```i
andika "Muraho, Isi!"
```

This compiles to the same call as the `andika` builtin.

### Word comparison operators

Comparisons read naturally and are equivalent to the symbol forms:

```i
shyira x = 5
x irenze 3        # same as x > 3
x munsi 3         # same as x < 3
x munsi_ya 10     # same as x < 10
```

## Running Your Program

Two equivalent ways:

```bash
i hello.i -r
python -m isoko.cli run hello.i
```

Both exit `0` on success and print diagnostics to standard error on failure.

## Common Migration Pitfalls

1. **Quoted import paths no longer (and never did) parse.** The `shyiramo` statement
   takes a bare identifier: `shyiramo text`. Framework sources that used
   `shyiramo "json"` must use the documented import form.
2. **Word operators are comparisons only.** `irenze`, `munsi`, `munsi_ya` are
   comparison operators. Logical `kandi` / `cyangwa` are not implemented; use nested
   `niba` blocks (see the Language Guide's Known Limitations).
3. **`gukoma` (break) in `wihuse` loops** can loop forever on 1.0.0. Use `kuri` loops
   for code that needs to break.
4. **Booleans are `true` / `false`.** The English literals print as `True` / `False`.

## Verifying the Migration

```bash
i --version                    # I Programming Language Compiler v1.0.0
python -m isoko.cli --version  # isoko 1.0.0
python -c "import compiler, vm, stdlib; print(compiler.__version__)"
```

Then run your test suite (`python -m isoko.cli test`) and the golden examples in
`examples/`.
