# Implementation Audit — I Language v1.0 Release

**Auditor:** Release Stabilization Team
**Date:** 2026-07-31
**Scope:** Full end-to-end audit of the `i-lang` repository against the v1.0 release definition in `RELEASE_PROCESS.md`.

---

## 1. Executive Summary

The `i-lang` codebase contains a large, well-tested compiler stack — **4088 unit/integration tests pass**
(`pytest tests/`, 31s, Python 3.14.6). However, the product is **not installable and not runnable as
shipped**: the package builds an empty wheel, the `i` CLI entry point is broken, and the flagship
example (`examples/hello.i`) cannot be executed end-to-end. The primary gap is that the shipped CLI
wires only the *legacy* compiler path (lexer -> parser -> semantic -> codegen -> legacy VM), which was
never completed to the point where the language's own example programs run.

## 2. Test Baseline

| Metric | Result |
|---|---|
| Full suite | **4088 passed, 0 failed** |
| Runtime | ~31s |
| Interpreter | Python 3.14.6, pytest 9.1.1 |
| `tests/test_mobile.py` | 154/154 green |
| `tests/unit/test_vm_sprint98.py` | 280/280 green |
| `tests/unit/test_ir_lowering.py` | 27/27 green |
| `tests/isoko/test_cli.py` | 25/25 green |
| `tests/unit/test_optimization_sprint9.py` | 71/71 green |
| `tests/unit/test_stdlib_bridge.py` | 11/11 green |
| `tests/unit/test_semantic_parse_integration.py` | 45/45 green |
| `tests/unit/test_codegen_sprint5.py` | 116/116 green |

Test infrastructure is healthy; the failures are all in **integration surface that is untested**.

## 3. Critical Findings

### 3.1 Packaging: `pip wheel .` produces an EMPTY wheel (6.6 KB)

`pyproject.toml`:
- `[tool.setuptools.packages.find] where = ["."]` — but all code lives under `src/`.
- Result: the wheel contains only `dist-info` metadata, **no package code**.

Verified:
```
> pip wheel . --no-deps -w dist
> unzip -l dist/*.whl   # only dist-info/, no compiler/, vm/, isoko/ packages
> python -m compiler.compiler   # ModuleNotFoundError: No module named 'compiler'
```

The single console script `i = "compiler.compiler:main"` is therefore unusable after installation.

### 3.2 CLI: `i` cannot run any program

The CLI (`src/compiler/compiler.py`) wires only the legacy path:
`Lexer -> Parser -> SemanticAnalyzer -> CodeGenerator -> VirtualMachine (legacy)`.

Two concrete defects:

1. **Crash before real errors:** `compiler.py` `main()` has
   `except LexerError` / `except ParseError`, but `LexerError`
   (`src/compiler/lexer/errors.py:93`) and `ParseError` (`src/compiler/parser/errors.py:66`)
   are **dataclasses, not exceptions** -> `TypeError: catching classes that do not inherit
   from BaseException is not allowed` is raised before any meaningful diagnostic is shown.

2. **Flagship example fails:** `examples/hello.i` (`andika "Muraho, Isi!"`) is tokenized as
   two expression statements; codegen then fails with
   `RuntimeError: Undefined variable: andika`. There is no print-statement syntax in the
   parser, and codegen's `_resolve_variable` cannot fall back to builtin functions.

### 3.3 Language surface vs. shipped examples

All 7 top-level examples use syntax the compiler cannot process end-to-end:

| Example | Constructs required | Status |
|---|---|---|
| `hello.i` | print statement `andika` | FAILS (3.2) |
| `variables.i` | print statement, `shyira`/`shyira_ko` | FAILS (3.2) |
| `conditionals.i` | print statement, word operator `irenze` | FAILS |
| `loops.i` | print statement, word operator `munsi`, while/for/for-each | FAILS |
| `functions.i` | user function calls (`sagura(5,3)`), print | FAILS |
| `fibonacci.i` | recursion, word operator `munsi_ya` | FAILS |
| `structs.i` | struct decl, `.nshya` constructor, field access | FAILS |

Word comparison operators (`irenze`, `munsi`, `munsi_ya`) exist **nowhere** in lexer/parser/codegen.
The legacy VM (`src/vm/virtual_machine.py`) cannot call user-defined functions stored as `Chunk`
constants (`CALL` only handles Python callables and string-keyed builtins, L398-416).

### 3.4 Modern pipeline not wired to the CLI

The mature components — `check_types`, `ASTLowering`, `OptimizationPipeline`, the new VM
(`src/vm/vm_executor.py` with closures/frames/structs) — are **not** reachable from the `i` CLI.
`src/vm/vm_instance.py` `run_source()`/`run_file()` also use the legacy front-end. No end-to-end
driver exists (lexer -> parser -> semantic -> lowering -> IR -> optimizer -> new VM).

### 3.5 Zero CLI / end-to-end tests

No test invokes `compiler.compiler:main`, the installed `i` script, or a full
source->run round trip. This is why 3.1-3.3 went undetected.

## 4. Toolchain / Packaging Observations

- `tools/` directory exists but is **empty** (formatter, linter, LSP, package manager, test runner,
  debugger, doc-gen are placeholders only).
- `i_lang.egg-info/entry_points.txt` confirms the single entry point.
- `requires-python = ">=3.8"` while CI and dev run Python 3.14.
- Classifiers still `Development Status :: 3 - Alpha`.
- No `__main__.py` for `python -m` style invocation of any package.

## 5. CI / Dependencies / Security

- `.github/workflows/*.yml` present with a test matrix (see RELEASE_BLOCKERS.md for the path bugs).
- `requirements.txt`/`requirements-dev.txt` pin exact versions; **no dependency scan is wired into CI**
  (no `pip-audit` job). `pip-audit` is not installed locally.
- Sensitive-pattern scan found flagged locations to harden before release (see
  `SECURITY_VALIDATION_REPORT.md`): `shell=True` usage in stdlib `process`, an `eval()` in
  `istudio`, and a hardcoded push token path. All are **read-only findings to be fixed**, none is a
  published secret.

## 6. What Works Well

- Semantic analyzer: builtins registry (`BUILTIN_FUNCTIONS`, `BUILTIN_TYPES`), imports registry
  (`_STDLIB_EXPORTS`), diagnostics with localized Kinyarwanda messages, type system, 154 semantic
  tests green.
- Codegen: statements (if/while/for/for-each/function decl/var decl), expressions, list/dict literals,
  method-call/constructor codegen pattern, 116 codegen tests green.
- Legacy VM: full arithmetic/comparison/logical opcode set, 280 VM tests green.
- New VM executor: closures, call frames, structs, builtins dispatch — solid foundation for 1.1.
- Optimization pipeline and IR lowering: 71 + 27 tests green.

## 7. Audit Conclusion

v1.0 is blocked on **integration, packaging, and the missing core syntax/runtime surface for the
shipped examples** — not on architecture quality. The fixes in `RELEASE_BLOCKERS.md` are additive and
small (packaging config, parser statement, codegen builtin fallback, legacy-VM call support), keeping
the architecture intact per stabilization rules.
