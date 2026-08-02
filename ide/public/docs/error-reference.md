# I Error Reference

The compiler reports structured error codes. Each code identifies the stage, the
problem, and the source location. Errors are printed with an English message and a
Kinyarwanda equivalent.

## Example

```text
PARS001 at 1:10 - Unexpected token '"text"', expected 'module path'
  Kinyarwanda: Ikimenyetso '"text"' ntikemewe, byitezwe 'module path'
```

```text
[ERROR] SEM200_UNDEFINED_VARIABLE main.i:5:24: Undefined variable 'x'
```

## Parse Errors — `PARS`

Raised by the lexer/parser stage.

| Code | Meaning |
| --- | --- |
| `PARS001` | Unexpected token — found `X`, expected `Y` |
| `PARS002` | Missing token — expected `Y` |
| `PARS003` | Invalid expression |
| `PARS004` | Unterminated block (expected `iherezo`) |
| `PARS005` | Invalid assignment target |
| `PARS006` | Missing `iherezo` to close block |
| `PARS007` | Invalid statement |
| `PARS008` | Too many errors (parse aborted) |

Common causes:

- `PARS001` on `shyiramo` — the module name must be a bare identifier, **not** a
  quoted string: `shyiramo text` ✓, `shyiramo "text"` ✗
- `PARS003` on a `kuri` loop — check the range form `kuri i muri 0 kugeza 10`
- `PARS004`/`PARS006` — a block is missing its closing `iherezo`

## Semantic Errors — `SEM`

Raised by the semantic analyzer. Grouped by range.

### Declarations — `SEM100`–`SEM199`

| Code | Meaning |
| --- | --- |
| `SEM100` | Duplicate variable |
| `SEM101` | Duplicate function |
| `SEM102` | Duplicate parameter |
| `SEM103` | Duplicate class |
| `SEM104` | Duplicate method |
| `SEM105` | Duplicate module |
| `SEM106` | Duplicate struct |
| `SEM107` | Duplicate enum |
| `SEM108` | Duplicate trait |
| `SEM109` | Duplicate interface |
| `SEM110` | Reserved keyword used as identifier |
| `SEM111` | Illegal identifier |

### Name resolution — `SEM200`–`SEM299`

| Code | Meaning |
| --- | --- |
| `SEM200` | Undefined variable |
| `SEM201` | Undefined function |
| `SEM202` | Undefined class |
| `SEM203` | Undefined module |
| `SEM204` | Undefined type |
| `SEM205` | Undefined struct |
| `SEM206` | Undefined enum |
| `SEM207` | Undefined method |
| `SEM208` | Undefined trait |
| `SEM209` | Undefined interface |

### Types — `SEM300`–`SEM399`

| Code | Meaning |
| --- | --- |
| `SEM300` | Type mismatch |
| `SEM301` | Value is not callable |
| `SEM302` | Argument count mismatch |
| `SEM303` | Missing return value |
| `SEM304` | `subira` (return) outside a function |
| `SEM305` | `gukoma` (break) outside a loop |
| `SEM306` | `kugenda` (continue) outside a loop |
| `SEM307` | Cannot index this value |
| `SEM308` | Index must be numeric |
| `SEM309` | Cannot set this property |
| `SEM310` | No such property |

### Imports — `SEM400`–`SEM499`

| Code | Meaning |
| --- | --- |
| `SEM400` | Module not found |
| `SEM401` | Duplicate import |
| `SEM402` | Circular import |
| `SEM403` | Imported symbol is not public |
| `SEM404` | Export not found |
| `SEM405` | Access to private symbol |

### Constants — `SEM500`–`SEM599`

| Code | Meaning |
| --- | --- |
| `SEM500` | Expression is not a constant |
| `SEM501` | Division by zero |
| `SEM502` | Constant type mismatch |

### Control flow — `SEM600`–`SEM699`

| Code | Meaning |
| --- | --- |
| `SEM600` | Unreachable code |
| `SEM601` | Missing return path |
| `SEM602` | Uninitialized variable |

### Visibility — `SEM700`–`SEM799`

| Code | Meaning |
| --- | --- |
| `SEM700` | Visibility restricted |
| `SEM701` | Module not exported |
| `SEM702` | Symbol not visible |

## Runtime Errors

Runtime failures are reported as `Runtime Error: <message>` with exit code 1.

| Message pattern | Meaning |
| --- | --- |
| `Cannot call non-callable: ...` | calling a value that is not a function |
| `Division by zero` | dividing by zero at runtime |
| `Undefined variable ...` | variable not in scope at runtime |
| `Stack overflow` | call depth exceeded |

## Diagnostics Engine — `E####`

The diagnostics engine (used by editor/studio integrations) uses a separate numeric
taxonomy.

| Range | Category |
| --- | --- |
| `E1001`–`E1005` | Lexer (invalid character, unterminated string/comment, invalid number/unicode) |
| `E2001`–`E2006` | Parser (expected/unexpected token, missing delimiters, invalid expression/statement) |
| `E3001`–`E3007` | Semantic (undefined variable/function/type, duplicate definition, type mismatch, invalid assignment, missing return) |
| `E4001`–`E4005` | Type system (type error/mismatch, not callable, not subscriptable, out of range) |
| `E5001`–`E5003` | IR (invalid instruction/operand, stack overflow) |
| `E6001`–`E6005` | Runtime (error, type error, index error, null error, division by zero) |
| `E7001`–`E7004` | I/O (file not found, permission denied, read/write error) |

## Recovering from Errors

1. Read the code — `PARS*` is syntax, `SEM*` is name/type resolution.
2. Fix the reported location first; downstream errors often cascade.
3. Re-run; the compiler stops reporting parse errors after `PARS008` to avoid noise.
