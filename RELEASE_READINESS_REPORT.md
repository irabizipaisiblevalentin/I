# Release Readiness Report — I Language v1.0.0 (Vision 1.0.0)

**Prepared:** 2026-08-01
**Scope:** Full public release of the I Programming Language v1.0.0 and the
I Studio IDE desktop application, published from
`https://github.com/irabizipaisiblevalentin/I`.
**Supersedes:** `RELEASE_BLOCKERS.md`, `RELEASE_PROGRESS.md`,
`PACKAGING_REPORT.md`, `PLATFORM_REPORT.md`, and the previous version of this
file (all dated 2026-07-31 and reflecting the earlier RC1 scope).

---

## 1. Definition of Done — Status

| # | DoD Item | Status |
|---|---|---|
| 1 | All tests green | ✅ **4250 passed, 1 skipped** (POSIX-only login-permission test on Windows) |
| 2 | Version + metadata consistent at 1.0.0 | ✅ `pyproject.toml`, all `__version__` packages, stdlib `compiler`/`vm`, istudio, IDE |
| 3 | Repo identity points to the official repo | ✅ README, pyproject URLs, CONTRIBUTING, governance, security, release docs; zero `i-lang.rw` / `github.com/i-lang` references |
| 4 | CI workflows healthy and validated | ✅ `release.yml` (tag-driven, 5 jobs + combined checksums), `ci.yml` (5-OS matrix), `ide-release.yml`, `cd.yml`, `security.yml`; all YAML validated |
| 5 | Windows installer + portable ZIP built and verified | ✅ `release/IStudioIDE-Setup-1.0.0.exe` + `istudio-ide-1.0.0-win-x64.zip`; frozen exe smoke-tested (health, docs, index, project restore) |
| 6 | Linux + macOS packaging in place | ✅ `packaging/linux/` (tarball) + `packaging/macos/` (DMG) specs/scripts wired into `release.yml` (buildable in CI) |
| 7 | Desktop app behaves like a modern IDE | ✅ native window, Open Folder… picker, Explorer "Open with I Studio" context menu, drag-and-drop import, last-workspace restore, command palette, settings, docs view |
| 8 | Security + dependency audit clean | ✅ secret-scan clean, `pip-audit` no known vulns, `npm audit` 0 vulnerabilities |
| 9 | **Stop for approval before publishing** | ⏸ **HERE** — see §6 |

## 2. Test Suite

- **Backend:** `pytest` full run → **4250 passed, 1 skipped, 0 failed**
  (130 s). Includes `tests/istudio` (409), stdlib, compiler, vm, e2e, urubuga.
- **Version test:** `test_stdlib_sprint9.py::TestVM::test_version` updated to
  assert `1.0.0`.
- **Frontend:** `tsc --noEmit` clean; `npm run build` clean (1127 modules).
- **IDE backend tests:** `pytest tests/istudio` green; router now resolves the
  longest prefix so nested `/api/projects/...` routes work.
- **Example programs:** `examples/build/example.py` builds under both dev and
  release profiles.

## 3. Release Artifacts (built locally, Windows)

| Artifact | Size | SHA-256 |
|---|---|---|
| `release/IStudioIDE-Setup-1.0.0.exe` | 16.9 MB | `2930d97667f65ee85b5a21167b1fc9974d1cbf85ea716455ced5a77475ffbf2d` |
| `release/istudio-ide-1.0.0-win-x64.zip` | 19 MB | `fcdd78c11fc69ca7c451247c13714d3847a00ca14c8f45a2c4676c5e3c1ab364` |

- PyPI wheel + sdist built and verified during RC1 (fresh-venv install, `i` CLI,
  example programs, `isoko new`).
- CI (`release.yml`) regenerates checksums across dist/ and release/ artifacts
  when the tag is pushed.

## 4. Desktop App (I Studio IDE, Windows)

Implemented as a pywebview (WebView2) native window over the local IDE server:

- **Workspaces:** any folder is a workspace (no `ilang.toml` required).
- **Open methods:** Welcome → Open Folder… (native picker); File Explorer
  right-click → *Open with I Studio* (registered per-user by the installer for
  both folder context menu and folder-background); `istudio-ide --app <path>`.
- **Drag & drop:** files dropped from Explorer onto the window are imported
  into the active project; last workspace is restored on launch.
- **Editor:** Monaco with I syntax highlighting, breakpoints, run/debug,
  command palette (Ctrl+Shift+P / F1), settings (theme/font size/tab
  size/minimap/word wrap), sidebar docs view, integrated terminal.
- **Docs:** 7 sealed guides bundled and served at `/docs/...`.

## 5. Known v1.0 Gaps (deferred to 1.1)

- Modern compiler pipeline (Sprint 9.x core/build) not fully wired into the
  `i` CLI; the CLI uses the legacy pipeline for run/compile.
- Native compiler targets x86-64 Windows/Linux only; arm64 and macOS native
  builds deferred.
- VM exception unwinding is simplified.
- Coverage: 53% for `compiler` + `vm` (32,101 stmts) — the 90% target is not
  met; measured honestly and tracked for 1.1.

## 6. Launch-Day Uploads (require the release machine)

1. **Logo artwork (blocked on user):** the pasted clipboard image cannot be
   read by this tool. Save it to the repo as `ide/public/logo.svg`/`logo.png`
   (welcome/favicon) and `packaging/windows/app_icon.ico` (window + installer
   icon; a placeholder `app.ico` is wired in now).
2. Commit the working tree (IDE, packaging, CI, docs) and push to
   `https://github.com/irabizipaisiblevalentin/I`.
3. Push tag `v1.0.0` — `release.yml` builds all platform artifacts, runs
   pytest, and creates a **draft** GitHub Release with combined `checksums.txt`
   and `RELEASE_NOTES.md` body.
4. Founder reviews the draft Release and clicks **Publish**.
5. `twine upload` the wheel + sdist to Test PyPI, then PyPI (`pip install
   i-lang`).

## 7. Verdict

**READY for launch-day uploads.** All gates pass locally (tests, typecheck,
builds, installer smoke tests, security audit). Remaining work is external:
founder-supplied logo file, git remote/credentials on the release machine, and
the tag + GitHub Release + PyPI steps in §6.
