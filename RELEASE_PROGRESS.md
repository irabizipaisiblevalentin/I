# Release Progress — I Language v1.0

**Owner:** Release Stabilization Team
**Status:** Stabilization complete — **awaiting approval before RC1** (M11)
**Date:** 2026-07-31

> Live tracker. Freeze point reached: **Stop for approval before RC1.**

---

## Sprint Goal

Ship I Programming Language v1.0 this Saturday by eliminating every release blocker in
`RELEASE_BLOCKERS.md`. No architecture redesign, no experimental features, no new keywords beyond
the printed builtins already specified in `LANGUAGE_SPECIFICATION.md`.

## Milestones

| # | Milestone | Status |
|---|---|---|
| M0 | Audit + reports (this set) | ✅ Done |
| M1 | Packaging: wheel contains code, `i` installable | ✅ Done |
| M2 | CLI robust (no crash, clean diagnostics) | ✅ Done |
| M3 | Core syntax: `andika`, word operators, function calls | ✅ Done |
| M4 | Examples run end-to-end (hello, variables, functions, conditionals, loops, fibonacci) | ✅ Done |
| M5 | New e2e CLI tests green | ✅ Done |
| M6 | CI + `isoko run` fixes green | ✅ Done |
| M7 | stdlib in wheel + import tests | ✅ Done |
| M8 | Security hardening + validation report | ✅ Done |
| M9 | Full regression suite green (4107 passed, 1 skipped) | ✅ Done |
| M10 | v1.0 metadata + five release reports + Stabilization Report | ✅ Done |
| M11 | **STOP — await approval before RC1** | 🟡 Awaiting approval |

## Blocker Triage (2026-07-31)

Category A: A1-A8 confirmed, all verified by reproduction, all fixed.
Category B: B1-B3 confirmed, all fixed.
Category C: documented, tracked in ROADMAP for 1.1.

## Blocker Status Detail

| ID | Severity | Status | Notes |
|---|---|---|---|
| A1 | Critical | ✅ Fixed | `where=["src"]`; wheel ships 15 packages + `urubuga.i` + `py.typed` |
| A2 | Critical | ✅ Fixed | `CompilerError` path; clean diagnostics, no traceback |
| A3 | Critical | ✅ Fixed | `andika` parse + codegen + VM builtin |
| A4 | High | ✅ Fixed | Legacy VM `_collect_functions`/`_call`/`_call_function`; recursion works |
| A5 | High | ✅ Fixed | `irenze`/`munsi`/`munsi_ya` → GT/LT |
| A6 | High | ✅ Fixed | 6 CLI e2e tests + 3 wheel e2e tests |
| A7 | Medium | ✅ Fixed | CI workflows re-pointed; wheel-completeness job fixed |
| A8 | Medium | ✅ Fixed | `__main__` guard |
| B1 | Medium | ✅ Fixed | stdlib in wheel + import tests |
| B2 | Medium | ✅ Fixed | login perms, eval dunder-block, safe archives, hash flags; see SECURITY_VALIDATION_REPORT.md |
| B3 | Low | ✅ Fixed | v1.0.0 metadata, `requires-python >=3.10`, classifiers, CHANGELOG |

## Verification Runbook

```powershell
# baseline
python -m pytest tests/ -q
# targeted
python -m pytest tests/unit/test_parser.py tests/unit/test_codegen_sprint5.py tests/unit/test_vm_sprint98.py -q
# wheel
pip wheel . --no-deps -w dist
python -m zipfile -l dist/i_lang-1.0.0-py3-none-any.whl
# install smoke
python -m pip install --target %TEMP%\i_install dist\i_lang-1.0.0-*.whl
# run
python -m compiler.compiler -r examples/hello.i
```

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Example programs expose more parser gaps | Med | High | Test-driven: add e2e case per example; keep Category C honest |
| Legacy VM call frames break existing VM tests | Low | Med | Isolated `_call_function`; run test_vm_sprint98 after change |
| Windows-only path issues | Med | Low | CI runs cross-platform after A7 |

## Freeze Notice

The Stabilization Report must be produced and **approved by the user before RC1 packaging begins**.
