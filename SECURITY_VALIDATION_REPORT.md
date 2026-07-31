# Security Validation Report — I Language v1.0

**Prepared by:** Release Stabilization Team
**Date:** 2026-07-31
**Scope:** `src/` (all 15 packages), CLI entry points, packaging, and the Category-B2 hardening items.
**Methods:** Manual code review + pattern scan, automated static analysis (bandit 1.9.4), targeted regression tests.

---

## 1. Executive Summary

No published secrets, credentials, or keys were found anywhere in the repository. Three B2
hardening targets from `RELEASE_BLOCKERS.md` (`shell=True` in stdlib `process`, `eval()` in
`istudio`, hardcoded push-token storage in `isoko login`) were addressed, and a static scan of
`src/` (247 findings, mostly informational) surfaced four additional hardening opportunities that
were fixed: unsafe zip/tar extraction, MD5/SHA-1 used without `usedforsecurity=False`,
debugger `eval` sandbox escape, and world-readable registry token storage.

**Status: ready for v1.0.** Remaining static-scan findings are LOW/INFORMATIONAL, documented
intentional APIs, or deferred-to-1.1 items (SQL query builders, XML/`urlopen` library surfaces).

---

## 2. B2 Blocker Dispositions

### 2.1 `shell=True` in stdlib `process`
`src/stdlib/process.py`
- `run()` / `run_checked()` / `run_capture()` / `popen()` execute with `shell=False` by default
  and accept argument lists — **injection-safe** for untrusted input.
- `exec_command()` is the single shell-based entry point. It is an intentional, distinctly named
  shell-execution API. The module and function docstrings now carry an explicit security warning,
  and the safe APIs are called out as the recommended path.
- **Disposition:** hardened by documentation; default-safe APIs remain the only non-explicit path.
  The `run()` call still passes `shell=<param>` (defaults `False`) and is flagged by bandit; this
  is an opt-in keyword argument, not a default-on vulnerability.

### 2.2 `eval()` in `istudio`
`src/istudio/ugutunganya.py:130-140` (debugger `evaluate`)
- The debugger evaluates expressions with `__builtins__` removed. A dunder-access check now rejects
  expressions containing `__` (e.g. `().__class__.__base__`), closing the standard
  object-capability escape path.
- **Disposition:** fixed. Regression test added: `tests/istudio/test_ugutunganya.py`.

### 2.3 Hardcoded push-token path in `isoko login`
`src/isoko/commands/login.py`
- Registry tokens were stored in plaintext at `~/.isoko/config.json` with default (world-readable
  on POSIX) permissions.
- **Disposition:** fixed. The `.isoko` directory is now created with mode `0o700` and the config
  file with mode `0o600` (POSIX). On Windows the file lives under the user profile where ACLs
  already restrict access. Regression tests added: `tests/unit/isoko/test_login.py`.

---

## 3. Automated Scan (bandit 1.9.4) — `bandit -r src`

| Severity | Count |
|---|---|
| HIGH | 6 |
| MEDIUM | 56 |
| LOW | 185 |
| **Total** | **247** |

### 3.1 HIGH findings (6) — all justified or fixed

| Test ID | Location | Disposition |
|---|---|---|
| B324 | `stdlib/crypto.py` `hash_md5`, `hash_sha1` | **Fixed** — now call `hashlib.md5/sha1(..., usedforsecurity=False)`. These are checksum/legacy helpers, not security hashes. |
| B324 | `stdlib/websocket.py:112` SHA-1 | **Justified** — SHA-1 is mandated by RFC 6455 for the `Sec-WebSocket-Accept` handshake. |
| B324 | `ubwenge/gushaka.py:52` MD5 | **Fixed** — `usedforsecurity=False`; MD5 used only for a truncated document-ID digest. |
| B602 | `stdlib/process.py` | **Documented** — see §2.1. |

### 3.2 MEDIUM findings worth noting

| Test ID | Count | Disposition |
|---|---|---|
| B608 (SQL string construction) | 43 | **Deferred to 1.1** — query-builder helpers in `istudio`/`mobile`/`ububiko` interpolate values into SQL strings by design. There is no parameterized-query API yet. Tracked in ROADMAP; recommend parameterized variants before any network-facing use. |
| B314/B405 (XML parsing) | 5 | **Low practical risk** — `xml.etree.ElementTree` does not resolve external entities by default (no XXE exfiltration). Recommend `defusedxml` for 1.1 hardening. |
| B104 (bind `0.0.0.0`) | 5 | **Documented** — framework server defaults; deployers control binding. |
| B310 (`urllib.request.urlopen`) | 3 | **Documented** — generic stdlib fetch API; callers control URLs. |
| B307 (`eval`) | 1 | **Fixed** — the single remaining `eval` is the hardened debugger (see §2.2). |
| B202 (tar/zip extraction) | 1 | **Fixed** — safe extraction now rejects traversal and link members; the single remaining bandit flag is a static false positive on the validated `extractall(members=...)` call. |

### 3.3 LOW findings
185 LOW findings, dominated by `B110 try/except pass` (55), `B311 random module` (47), `B603
subprocess` (23), and `B607 partial path` (14). All are informational code-quality heuristics with
no security impact; no action required for v1.0.

---

## 4. Additional Review Areas

- **Credentials scan:** no hardcoded passwords, API keys, or tokens in `src/` (the one match,
  `igicu/ibikoreshingiro.py:153 API_KEY = "api_key"`, is a constant name, not a secret).
- **`pickle` usage:** two sites, both intentional and documented:
  - `stdlib/serialization.py` — serialization API; docstring warns against untrusted data.
  - `vm/virtual_machine.py` — bytecode artifact loading; equivalent trust level to running a
    program (an `.i` program is arbitrary code by design).
- **Subprocess defaults:** all internal subprocess call sites (`isoko run`, `sisitemu`) use
  argument lists without a shell.
- **Supply chain:** no dependency scan in CI. `bandit` and `safety` jobs run non-blocking in
  `.github/workflows/security.yml`. `pip-audit` is **not** installed locally and remains a
  recommended 1.1 addition (`RELEASE_BLOCKERS.md` Category C).

---

## 5. New Security Tests Added

- `tests/unit/stdlib/test_archive_security.py` — zip/tar extraction rejects `../` traversal and
  symlink/hardlink members; normal archives still extract (7 tests).
- `tests/unit/isoko/test_login.py` — token written to config; POSIX file/dir modes are owner-only;
  cancelled login exits cleanly (3 tests + 1 POSIX-only skip on Windows).
- `tests/istudio/test_ugutunganya.py` — debugger rejects dunder-escape expressions.

---

## 6. Residual Risks / Recommendations (1.1)

1. Add parameterized-query APIs to replace string-interpolated SQL builders (B608).
2. Use `defusedxml` for XML parsing (B314).
3. Add `pip-audit` to CI dependency scan.
4. Consider `trusted-publish`/keyring-backed token storage beyond file permissions.
5. Review any future network-facing bind (`B104`) per deployment.

---

**Conclusion:** The B2 blocker is resolved; no HIGH-severity finding remains open without a
documented justification. v1.0 is cleared for release from a security perspective.
