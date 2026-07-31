# Tutorial Level 5 — Building a Program

**Objective:** combine everything into a complete, well-structured program and
prepare a project for distribution.

## What You'll Learn

- Structuring a program: constants, helpers, main flow
- Reading the toolchain's error messages
- Setting up a project with isoko
- Running checks and tests
- Next steps

## 1. Anatomy of a Complete Program

A good program has three parts:

1. **Constants** at the top (`shyira_ko`)
2. **Helper functions** (`umurimo`) in the middle
3. **Main flow** at the bottom

Here is `examples/projects/perfect_numbers.i` (finding perfect numbers) as a
model:

```i
umurimo ni_perfect(n: int) -> int
    shyira total = 0
    kuri d muri 1 kugeza n
        niba n % d == 0
            total = total + d
        iherezo
    iherezo
    niba total == n
        subira 1
    iherezo
    subira 0
iherezo

shyira_ko MAX = 1000

andika "Perfect numbers below " + shobora_umuntu(MAX) + ":"
kuri n muri 2 kugeza MAX
    niba ni_perfect(n) == 1
        andika n
    iherezo
iherezo
```

Run it:

```bash
i perfect_numbers.i -r
```

Output:

```
Perfect numbers below 1000:
6
28
496
```

## 2. Reading Error Messages

Errors follow the pattern:

```
[ERROR] SEM404_UNDEFINED_FUNCTION program.i:5:9: call to undefined function 'ikurikiranyabungubu'
```

| Piece | Meaning |
|-------|---------|
| `SEM404` | Semantic error category |
| `_UNDEFINED_FUNCTION` | Machine-readable name |
| `program.i:5:9` | file, line, column |
| message | What went wrong |

Common errors you will meet:

- `PARS001` — unexpected token (typo, missing `iherezo`)
- `SEM200_UNDEFINED_VARIABLE` — a variable you have not declared
- `SEM301_NOT_CALLABLE` — calling something that is not a function
- `SEM302_ARGUMENT_COUNT` — wrong number of arguments
- `Runtime Error: ...` — the program compiled but failed at runtime

The full catalog is in the [Error Reference](../user-guide/error-reference.md).

## 3. Setting Up a Project with isoko

For anything bigger than a single file, use the isoko project manager:

```bash
python -m isoko.cli new my_project
cd my_project
```

This creates a folder with:

- `ilang.toml` — the project manifest (name, version, description, license)
- `src/main.i` — the entry point
- `lib/` — where reusable `.i` modules live
- `tests/` — test files

Run the project:

```bash
python -m isoko.cli run
```

Test it:

```bash
python -m isoko.cli test
```

Check formatting and lint:

```bash
python -m isoko.cli fmt
python -m isoko.cli lint
```

> **Note:** isoko is invoked with `python -m isoko.cli ...` in this version;
> it is not installed as a standalone `isoko` command.

## 4. The Manifest

`ilang.toml` describes your package:

```toml
[package]
name = "my_project"
version = "0.1.0"
description = "A small I program"

[engines]
i = ">=1.0.0"
```

Key fields:

| Field | Purpose |
|-------|---------|
| `name`, `version` | identity |
| `description`, `authors`, `license` | metadata |
| `dependencies` | packages this project needs |
| `lib` | where modules live (default `lib`) |
| `include` / `exclude` | which files get published |

See the [isoko Guide](../user-guide/isoko-package-manager.md) for the full
manifest reference.

## 5. Project Layout Best Practices

- One concern per `.i` file in `lib/`
- Plan imports with `shyiramo` (bare identifier, no quotes) — see the note on
  module runtime support below
- Keep `main.i` thin — parse input, call functions, print results
- Put a `#` comment at the top of each file explaining its purpose
- Run `python -m isoko.cli lint` before publishing

Example multi-file layout:

```
my_project/
  ilang.toml
  src/
    main.i            # entry point
  lib/
    urutonde.i        # list helpers
    imibare.i         # math helpers
  tests/
    test_main.i
```

## 6. Next Steps

You now know enough to write real programs in I. Where to go from here:

- Browse the other examples in [`examples/projects/`](../../examples/projects/) —
  try to rewrite one from memory.
- Read the [Language Guide](../user-guide/language-guide.md) for the complete
  grammar and the list of 1.0.0 limitations.
- Use the [Standard Library Reference](../user-guide/stdlib-reference.md) —
  44 modules cover text, math, files, HTTP, crypto, and more — available to
  toolchain and host integrations.

### A note on modules

`shyiramo` is an early-access feature in 1.0.0. The compiler accepts
`shyiramo math` and validates that the module name exists, but the reference
VM cannot yet execute module member access (for example `math.pi`), so
imported functions are not usable at runtime in this version. Working
programs should rely on the built-ins (`andika`, `soma`, `uburengero`,
`ubwoko`, `shobora_*`) documented in the Language Guide.

## Practice

1. Turn `sum_digits.i` into a function that works on any number.
2. Create an isoko project, add a `lib` module, and write a `shyiramo`
   statement for it in `main.i`. The compiler will validate the import
   (and report an error if the name does not resolve) even though module
   execution is not available in 1.0.0.
3. Write a program that reads a number, classifies it (prime, perfect,
   or neither), and prints the result.
4. Deliberately break a program (remove an `iherezo`) and read the error —
   then fix it.

## Reference

- [Getting Started](../user-guide/getting-started.md) — the 15-minute intro
- [isoko Package Manager Guide](../user-guide/isoko-package-manager.md)
- [Error Reference](../user-guide/error-reference.md)
- [Toolchain Guide](../user-guide/toolchain-guide.md)

## You're Done!

That completes the tutorial series. You can now read the reference
documentation with confidence, or dive straight into building.
