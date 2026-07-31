# Test Summary Report — I Language v1.0

**Prepared by:** Release Stabilization Team
**Date:** 2026-07-31
**Command:** `python -m pytest tests/ -q`
**Environment:** Windows, Python 3.14.6, pytest 9.1.1

---

## 1. Result

```
4107 passed, 1 skipped, 2 warnings in 70.43s
```

The single skip is the POSIX-only login-permission test (`tests/unit/isoko/test_login.py`)
on Windows — expected.

## 2. Breakdown by Area

| Area | Result |
|---|---|
| `tests/unit/` (compiler, VM, stdlib, isoko, urubuga, ufa, utilities, workspace, …) | 3236 passed, 1 skipped |
| `tests/e2e/` (CLI subprocess + wheel) | 9 passed |
| Root + other suites (`test_mobile`, `test_lexer`, `test_parser`, istudio, ideveloper, integration, igicu, golden, snapshots, fuzzing, benchmarks) | 862 passed |
| **Total** | **4107 passed, 1 skipped** |

## 3. New Tests Added During Stabilization

| File | Tests | Purpose |
|---|---|---|
| `tests/e2e/test_cli.py` | 6 | 6 examples run with golden stdout; lexical/parse errors exit clean; `-o` bytecode artifact; missing file; `--version` v1.0.0 |
| `tests/e2e/test_stdlib_wheel.py` | 3 | wheel carries stdlib + `urubuga.i`; 11 stdlib modules import from installed wheel; `shyiramo` compiles via wheel CLI |
| `tests/unit/isoko/test_login.py` | 3 (+1 skip) | token persisted; owner-only file/dir modes (POSIX); cancelled login |
| `tests/unit/stdlib/test_archive_security.py` | 7 | zip/tar extraction rejects traversal and links; MD5/SHA-1 digests stable |
| `tests/istudio/test_ugutunganya.py` | +1 | debugger `eval` rejects dunder-escape expressions |

**Total new:** 20 tests (21 cases counting the skipped one).

## 4. Targeted Verification Runs (from `RELEASE_PROGRESS.md` runbook)

```powershell
# parser / codegen / VM hotspots
python -m pytest tests/unit/test_parser.py tests/unit/test_codegen_sprint5.py tests/unit/test_vm_sprint98.py -q
# isoko unit suite
python -m pytest tests/unit/isoko -q          # 220 passed
# stdlib bridge + security
python -m pytest tests/unit/test_stdlib_bridge.py tests/unit/stdlib tests/istudio -q
```

All green.

## 5. Example Programs (end-to-end)

| Example | Output | Exit |
|---|---|---|
| `hello.i` | `Muraho, Isi!` | 0 |
| `variables.i` | `Jean` `25` `Rwanda` `3.14159` | 0 |
| `functions.i` | `8` `30` | 0 |
| `conditionals.i` | `X ni kure` `X si binini` `X ni gitoya` | 0 |
| `loops.i` | 0-4, 0-4, 1-5 | 0 |
| `fibonacci.i` | 0-34 | 0 |
| `structs.i` | **deferred to 1.1** (parse errors on struct syntax) | 1 |

## 6. Known Gaps

- Coverage metric not collected (see RELEASE_READINESS_REPORT.md §3).
- Legacy VM intentionally does not implement structs/methods (`GET_ATTR`/`SET_ATTR`/`NEW_INSTANCE`) — Category C.
