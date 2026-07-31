# Release Blockers — I Language v1.0

**Owner:** Release Stabilization Team
**Date:** 2026-07-31
**Category legend:**
- **A = Must fix for v1.0** (release-blocking, verified defect)
- **B = Should fix** (if time permits, meaningful quality gain)
- **C = Defer to 1.1** (documented limitation, needs RFC / architectural change)

---

## Category A — Release-Blocking

### A1. Empty wheel / package discovery broken
`pyproject.toml` uses `[tool.setuptools.packages.find] where = ["."]` while code lives in `src/`.
`pip wheel .` ships **no package code**; the installed `i` command and `python -m compiler.compiler`
cannot import. → `pyproject.toml` fix: `where = ["src"]`, include `stdlib*`, keep entry point.

### A2. `i` CLI crashes before reporting errors
`compiler.py` `main()` catches `LexerError`/`ParseError` which are **dataclasses, not exceptions**
(TypeError). → Catch the real exception classes (`CompilerError` base if present) or wrap
collector-based diagnostics; print clean diagnostics to stderr.

### A3. No print statement (`andika`) in parser
`examples/hello.i` (`andika "Muraho, Isi!"`) cannot be parsed as a single statement; codegen then
fails with `Undefined variable: andika`. → Parser: `andika <expr>` statement -> `CallExpr`.
Codegen: builtin callee fallback (`LOAD_CONST` name, matching the method-call pattern).
Legacy VM: register semantic builtins (`andika`, `soma`, `uburengero`, `ubwoko`, `shobora_*`,
`gukoma_func`).

### A4. User-defined function calls don't run on the legacy VM
Codegen stores functions as `Chunk` constants (LOAD_CONST + STORE_LOCAL); the legacy VM `CALL`
handles only Python callables / string-keyed builtins (virtual_machine.py:398-416).
Function-to-function / recursive calls also fail at codegen (`_resolve_variable` has no global
function fallback). → Codegen: identifier fallback to builtin/function name constant.
VM: `_call_function` for `Chunk` callees (fresh local stack, shared globals, recursion via
call-stack save/restore) + name->chunk registry scan.

### A5. Word comparison operators missing (`irenze`, `munsi`, `munsi_ya`)
`conditionals.i`, `loops.i`, `fibonacci.i` use `irenze` (>), `munsi` (<), `munsi_ya` (<) as infix
operators; no lexer/parser/codegen support. → Infix handling keyed on identifier lexemes +
opcode mapping (`irenze`->GT, `munsi`/`munsi_ya`->LT).

### A6. Zero CLI / end-to-end tests
No test exercises `compiler.compiler:main`, the `i` console script, or a source->run round trip.
→ New `tests/e2e/` suite (subprocess `i run`, compile-only golden checks) + parser/codegen unit tests
for `andika`.

### A7. CI workflow references broken paths
`.github/workflows/*.yml` reference files/layouts that no longer match the repo (see inline fixes).
→ Correct paths; keep matrix green; add a wheel-build smoke job.

### A8. `isoko run` broken: `virtual_machine.py` executed directly has no `__main__` guard
`python src/vm/virtual_machine.py` runs the whole module top-to-bottom. → `if __name__ == '__main__':`
guard.

---

## Category B — Should Fix

### B1. stdlib packaging + import tests
`stdlib*` packages are excluded from the wheel; several modules (yaml, process, http, httpserver,
websocket, compiler) have no import smoke tests. → include in wheel, add `tests/unit/test_stdlib_imports.py`.

### B2. Security hardening
`shell=True` in stdlib `process`, `eval()` in `istudio`, hardcoded push token path. → fix, then
produce `SECURITY_VALIDATION_REPORT.md`.

### B3. Version metadata for v1.0
Version 0.1.0 -> 1.0.0, `--version` string, classifiers to `5 - Production/Stable`,
`requires-python` aligned to tested range (>=3.9 or >=3.10, matching CI), CHANGELOG entry.

---

## Category C — Deferred to 1.1 (documented limitations)

- **Structs / method calls / constructors on the legacy VM**: `GET_ATTR`/`SET_ATTR`/`NEW_INSTANCE`
  are unimplemented in `virtual_machine.py`; `structs.i` requires VM struct runtime. New VM executor
  already supports structs — wire it via the modern pipeline.
- **Modern pipeline end-to-end driver**: lexer->parser->semantic->check_types->ASTLowering->
  OptimizationPipeline->new VM (`vm_executor.py`). `src/compiler/native/compiler.py`
  `_ensure_ir_module` is the closest; stops at IR.
- **`tools/` empty subdirs**: formatter, linter, LSP, package manager, test runner, debugger, doc-gen.
- **`isoko urubuga` bridge**, **LSP/IDE integration**, **golden/snapshot/fuzz shells**.
- **Dependency scan in CI** (`pip-audit`) — see B2; recommended before 1.1.

---

## Definition of Done for v1.0

1. A1-A8 fixed, all tests green.
2. `pip wheel .` installs; `i run examples/hello.i` prints `Muraho, Isi!`;
   `variables.i`, `functions.i`, `conditionals.i`, `loops.i`, `fibonacci.i` compile and run
   (structs deferred, documented).
3. New e2e CLI tests green.
4. `SECURITY_VALIDATION_REPORT.md` + five release reports delivered; Stabilization Report produced.
5. **Stop for approval before RC1.**
