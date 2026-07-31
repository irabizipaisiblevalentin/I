# Stabilization Report — I Language v1.0

**Owner:** Release Stabilization Team
**Date:** 2026-07-31
**Status:** **STOP — awaiting approval before RC1 packaging (M11)**

---

## 1. Sprint Goal

Eliminate every release blocker in `RELEASE_BLOCKERS.md` for I Programming Language v1.0 —
**no architecture redesign, no experimental features, no new keywords beyond the printed
builtins** — verify with tests, produce the required reports, and stop for approval before RC1.

## 2. Outcome

**Goal met.** All Category A blockers (A1-A8) and all Category B blockers (B1-B3) are fixed and
verified. The full test suite is green, the wheel is installable and runnable, and all six shipped
example programs run end-to-end with correct output.

### 2.1 Blockers resolved

| Area | Fix |
|---|---|
| A1 Packaging | `packages.find where = ["src"]`; wheel ships 15 packages + `stdlib/urubuga.i` + `py.typed` |
| A2 CLI errors | `CompilerError` path; lexical/parse errors exit 1 with clean diagnostics (no traceback) |
| A3 `andika` | print statement parsed, codegen'd, run on legacy VM |
| A4 Function calls | legacy VM `_collect_functions`/`_call`/`_call_function`; recursion verified via `fibonacci.i` |
| A5 Word operators | `irenze`/`munsi`/`munsi_ya` → GT/LT |
| A6 No e2e tests | `tests/e2e/` CLI suite (6) + wheel suite (3) |
| A7 CI drift | workflows re-pointed; wheel-completeness job fixed (incl. phantom `ideveloper` removal); Python 3.10/3.11/3.12 matrix |
| A8 `__main__` guard | `vm.virtual_machine` guard added |
| B1 stdlib in wheel | package-data for `*.i`; import tests against installed wheel |
| B2 Security | login token perms, debugger eval dunder-block, safe archive extraction, `usedforsecurity=False`, process shell documented (see SECURITY_VALIDATION_REPORT.md) |
| B3 Metadata | v1.0.0 everywhere; `requires-python >=3.10` aligned to CI; classifiers Production/Stable; CHANGELOG `[1.0.0]` |

### 2.2 Notable runtime fixes (found during verification)

- `examples/loops.i`: step-expression NEWLINE guard in the parser; legacy-VM scope-exit slot reuse
  and for-each iterator slot isolation.
- `isoko run`: subprocess now receives `os.path.abspath(file_path)` so it works from any cwd.

## 3. Verification Evidence

| Check | Result |
|---|---|
| `python -m pytest tests/ -q` | **4107 passed, 1 skipped** (POSIX-only login test on Windows) |
| New tests added this sprint | **21** (6 CLI e2e + 3 wheel e2e + 3 login + 7 archive + 1 debugger + 1 parser/loop coverage elsewhere) |
| `pip wheel . --no-deps` | valid `i_lang-1.0.0-py3-none-any.whl` (~1.07 MB), all packages present |
| Wheel install smoke | `i`/`isoko`/`compiler` all run from the installed wheel; `isoko run hello.i`/`fibonacci.i` exit 0 |
| Examples | hello, variables, functions, conditionals, loops, fibonacci — golden output, exit 0 |
| Security scan | bandit 1.9.4; no HIGH finding without justification; fixes + tests added (see SECURITY_VALIDATION_REPORT.md) |

## 4. Reports Delivered

1. `RELEASE_READINESS_REPORT.md`
2. `TEST_SUMMARY_REPORT.md`
3. `PACKAGING_REPORT.md`
4. `PLATFORM_REPORT.md`
5. `PERFORMANCE_REPORT.md`
6. `SECURITY_VALIDATION_REPORT.md`
7. `STABILIZATION_REPORT.md` (this document)

Plus trackers updated: `RELEASE_PROGRESS.md`, `IMPLEMENTATION_AUDIT.md` (as source of truth),
`RELEASE_BLOCKERS.md`, `CHANGELOG.md`.

## 5. Open Items Before RC1 (action required, not code)

1. **`git add src/stdlib/urubuga.i`** — the file is untracked; a fresh CI checkout would omit it.
2. **Commit this stabilization work** — no commits were made during the sprint; the working tree
   contains all changes.
3. **Watch the first CI run** after push (workflows rewritten this sprint; reproduced locally only).
4. Optional: run `pytest --cov` for the 90% coverage metric called for in RELEASE_PROCESS.md.

## 6. Deferred to 1.1 (Category C, documented — unchanged)

- Structs/methods/constructors on the legacy VM (`structs.i` fails to parse — expected).
- Modern pipeline (lexer→parser→semantic→lowering→IR→optimizer→new VM) not wired to the CLI.
- `tools/` subcommands, `isoko urubuga` bridge, LSP/IDE integration, dependency scan
  (`pip-audit`), parameterized SQL builders, `defusedxml`.

## 7. Stabilization Rules Compliance

- No architecture redesign. ✅
- No experimental features. ✅
- No new keywords beyond the printed builtins (`andika`, `irenze`, `munsi`, `munsi_ya` are
  specified/printed builtins per the language spec). ✅
- No public API changes except the additions required to run the shipped examples (legacy-VM
  function dispatch, `andika`, word operators). ✅
- RC1 packaging **not started**. ✅

---

## 8. STOP FOR APPROVAL

Per `RELEASE_PROGRESS.md` (M11) and `RELEASE_BLOCKERS.md` DoD item 5:

> The Stabilization Report must be produced and **approved by the user before RC1 packaging begins.**

**Awaiting user approval to proceed to RC1 packaging** (build sdist/wheel, sign artifacts, upload
to Test PyPI per RELEASE_PROCESS.md steps 6-7). No RC1 work will begin until approval is given.
