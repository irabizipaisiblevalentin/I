# Platform Report — I Language v1.0

**Prepared by:** Release Stabilization Team
**Date:** 2026-07-31

---

## 1. Verified Environments

| Platform | Python | Result |
|---|---|---|
| Windows (win32, PowerShell 5.1) — local | 3.14.6 | Full suite green (4107 passed, 1 skipped); wheel built, installed, and all smoke tests passed |
| Linux (GitHub Actions `ubuntu-latest`) | 3.10 / 3.11 / 3.12 | CI test matrix configured (`python-version: ['3.10', '3.11', '3.12']`) |
| Linux (GitHub Actions `ubuntu-latest`) | 3.12 | lint, build/wheel-completeness, integration (e2e), security jobs |

> **Note:** CI results for the *current* workflows have not been observed since the workflow
> rewrite (no push/PR since the edits). The configuration was reviewed line-by-line; the wheel
> build/check steps were reproduced locally on Windows. First CI run after merge should be
> watched. Known historical issue (fixed): the wheel-completeness job expected an `ideveloper`
> package that does not exist in `src/` — removed from the expected set.

## 2. Platform Dependencies

- **Runtime:** pure-Python standard library only (no external runtime deps).
- **Interpreter compatibility:** `requires-python = ">=3.10"` (aligned to the tested CI range
  3.10-3.12; locally 3.14). Classifiers updated to 3.10/3.11/3.12.
- `usedforsecurity=False` hash calls carry a `TypeError` fallback so they remain correct across
  the supported range.

## 3. Windows-Specific Items Found & Handled During the Sprint

1. `pip wheel` builds can fail with `WinError 183` (cannot create `build\...\dist-info`) when a
   stale `build/` exists in the repo root. Mitigation: e2e wheel test builds from a clean copy of
   the source; the stale `build/` directory was removed from the working tree.
2. PowerShell `Set-Content -Encoding UTF8` corrupts UTF-8 sources (adds BOM, mojibakes em-dashes).
   All version bumps were redone with the encoding-safe edit tool.
3. POSIX file-permission bits are not enforced on Windows; the login-permission test skips there
   (user-profile ACLs provide equivalent protection).

## 4. Wheel Portability

- `py3-none-any` wheel: single artifact for all platforms; no platform-specific binaries.

## 5. Recommendation

After this change set is committed and pushed, confirm the first CI run (test matrix + build +
integration + security) before proceeding to RC1 packaging.
