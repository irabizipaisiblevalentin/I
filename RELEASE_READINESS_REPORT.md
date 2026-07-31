# Release Readiness Report — I Language v1.0

**Prepared by:** Release Stabilization Team
**Date:** 2026-07-31
**Reference:** `RELEASE_BLOCKERS.md` (Definition of Done), `RELEASE_PROCESS.md` (Pre-Release Checklist).

---

## 1. Definition of Done — Status

| # | DoD Item | Status |
|---|---|---|
| 1 | A1-A8 fixed, all tests green | ✅ Done — 4107 passed, 1 skipped |
| 2 | `pip wheel .` installs; `i run examples/hello.i` prints `Muraho, Isi!`; variables/functions/conditionals/loops/fibonacci compile and run (structs deferred) | ✅ Done — verified below |
| 3 | New e2e CLI tests green | ✅ Done — `tests/e2e/` 9 tests |
| 4 | `SECURITY_VALIDATION_REPORT.md` + five release reports + Stabilization Report delivered | ✅ Done — see this report set |
| 5 | **Stop for approval before RC1** | ⏸ **HERE** |

## 2. Blocker Matrix

| ID | Severity | Status | Evidence |
|---|---|---|---|
| A1 | Critical | ✅ Fixed | Wheel carries 15 packages + `stdlib/urubuga.i` + `py.typed` (see PACKAGING_REPORT.md) |
| A2 | Critical | ✅ Fixed | Lexical/parse errors exit 1 with clean stderr, no traceback (`tests/e2e/test_cli.py`) |
| A3 | Critical | ✅ Fixed | `andika` prints; golden outputs verified for all 6 examples |
| A4 | High | ✅ Fixed | Legacy VM function dispatch; recursion works (`fibonacci.i`) |
| A5 | High | ✅ Fixed | `irenze`/`munsi`/`munsi_ya` GT/LT (examples run) |
| A6 | High | ✅ Fixed | 6 CLI e2e tests + 3 wheel e2e tests |
| A7 | Medium | ✅ Fixed | CI workflows re-pointed; wheel-completeness job added |
| A8 | Medium | ✅ Fixed | `__main__` guard in `virtual_machine.py` |
| B1 | Medium | ✅ Fixed | stdlib in wheel + import tests (`tests/e2e/test_stdlib_wheel.py`) |
| B2 | Medium | ✅ Fixed | See SECURITY_VALIDATION_REPORT.md |
| B3 | Low | ✅ Fixed | v1.0.0 metadata everywhere + CHANGELOG entry |

## 3. Pre-Release Checklist (RELEASE_PROCESS.md)

- [x] All tests pass — 4107 passed, 1 skipped (POSIX-only login-permission test on Windows).
- [x] CHANGELOG.md updated with `[1.0.0]` section.
- [x] Version number updated — `pyproject.toml` + all 8 `__version__` packages + `--version`.
- [x] Security review completed — SECURITY_VALIDATION_REPORT.md.
- [ ] Coverage target 90%+ — **not measured**; suite is functional, coverage report pending (see note below).
- [ ] Migration guide — N/A (first release; no prior users).
- [ ] Release notes — embedded in this report set / CHANGELOG.

> **Coverage note:** `RELEASE_PROCESS.md` calls for 90%+ coverage. Coverage was not run in this
> stabilization sprint. Recommend running `pytest --cov` as part of the RC1 packaging step.

## 4. Remaining Action Items Before RC1

1. **Track `src/stdlib/urubuga.i` in git.** The file exists and is shipped in the wheel, but is
   currently **untracked** (`git status` shows `?? src/stdlib/urubuga.i`). A fresh CI checkout will
   not include it unless `git add`ed. Must be staged before RC1.
2. **Decide on committing this stabilization work.** No commits were made during the sprint
   (staging/committing deferred per policy); the working tree contains all fixes.
3. **Optional:** run `pytest --cov` for the 90% coverage metric; publish RC artifacts per
   RELEASE_PROCESS.md steps 6-7 (build sdist/wheel, sign, upload to Test PyPI).

## 5. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `urubuga.i` missing from CI checkout | High (certain without action) | Medium | `git add src/stdlib/urubuga.i` before RC1 |
| Legacy-VM structs unsupported | Certain | Medium | Documented; deferred to 1.1 (Category C) |
| Modern pipeline not wired to CLI | Certain | Medium | Documented; deferred to 1.1 (Category C) |

## 6. Verdict

**READY to proceed to Stabilization Report and the STOP-for-approval gate**, subject to the two
git/commit actions above being completed at RC1 time.
