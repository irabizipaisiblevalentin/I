# Changelog

All notable changes to the I Programming Language will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-08-01

### Added
- I Studio web IDE (`istudio-ide` console script / `istudio ide` subcommand): browser-based IDE with a React/TypeScript/Monaco frontend (`ide/`) and a stdlib-only Python backend (`src/istudio/ide/`). Edit, run, debug, built-in terminal, project templates, Git panel, and package-manager integration over a local HTTP server (`--host`/`--port`, default `127.0.0.1:8790`).
- I Studio IDE Windows desktop app: `--app` mode runs the IDE in a native window via pywebview (WebView2). Any folder is a workspace; the installer registers an **Open with I Studio** File Explorer context-menu entry (folder + background), the Welcome screen offers a native **Open Folder…** picker, files dragged from Explorer are imported into the active project, and the last workspace is restored on launch.
- I Studio IDE features: command palette (Ctrl/Cmd+Shift+P, F1), settings modal + status-bar theme dropdown (theme, font/tab size, minimap, word wrap), sidebar docs view with 7 bundled guides, and keyboard shortcuts (Ctrl/Cmd+S, Ctrl+`, F5 run, F9 breakpoint).
- I Studio IDE Extensions: Activity Bar → Extensions panel backed by `GET /api/extensions{,/browse}` and `POST /api/extensions/install|uninstall`; extensions install under `ISTUDIO_HOME/extensions` (path-traversal guarded) from the isoko package registry.
- I Studio IDE Monaco formatting: `formatICode` formatting provider (block indent for `kora`/`iherezo`/`cyangwa`, 4-space units) wired into the editor; `npx tsc --noEmit` clean.
- `isoko` console script (`isoko = isoko.cli:main`) plus `python -m isoko` / `python -m compiler` entry points.
- Packaging: `packaging/windows/` (PyInstaller spec + Inno Setup script + `build_windows.ps1`) produces `release/IStudioIDE-Setup-<version>.exe` and a portable `istudio-ide-<version>-win-x64.zip`; `packaging/linux/` and `packaging/macos/` produce portable tarball / DMG builds in CI.
- CI: tag-driven `release.yml` builds platform installers, runs pytest, and creates a draft GitHub Release with combined SHA-256 `checksums.txt` and `RELEASE_NOTES.md` body; `ide-release.yml` builds the Windows app on PRs and manual dispatch.
- Packaging: wheel now ships all 15 packages from `src/` plus the `stdlib/urubuga.i` framework source and `py.typed` markers; `i` console script installs and runs.
- CLI: `i --version`, clean diagnostics for lexical/parse errors, `-o` bytecode artifact output, and a `__main__` guard for `vm.virtual_machine`.
- I Studio: `istudio` console script (standalone CLI for the IDE platform, equivalent to `isoko istudio`); `--format json` for `istudio lint`; user guide at `docs/istudio/`.
- I Studio Desktop: `istudio-desktop` console script and `istudio desktop [path]` CLI subcommand launching a tkinter GUI IDE (`istudio.desktop`) — tabbed code editor with syntax highlighting, gutter breakpoints, bracket matching; live diagnostics, autocomplete, hover, go-to-definition, formatting, symbols outline; F5 run against the real compiler/VM; file explorer, Problems/Output/Run panels, four themes, autosave. Headless-testable controller/runner/highlight/theme modules.
- I Studio engine: `EditorEngine.create_tab` (untitled tabs) and `EditorEngine.save_file_as`.
- Language: `andika` print statement; word comparison operators `irenze` (`>`), `munsi` / `munsi_ya` (`<`).
- Runtime: legacy VM function dispatch (`_collect_functions`, `_call`, `_call_function`) with recursion and scope cleanup; for/for-each iteration on legacy stack semantics.
- `isoko`: `isoko run` resolves files via absolute path; registry tokens stored with owner-only permissions.
- Tests: `tests/e2e/` CLI suite (6 subprocess tests) and stdlib wheel suite (3 tests); archive safe-extraction and login-permission security tests.
- Security: safe zip/tar extraction (path-traversal and link rejection), debugger `eval` dunder-escape blocking, MD5/SHA-1 marked `usedforsecurity=False`.

### Changed
- Version metadata `0.1.0` -> `1.0.0` across all packages; classifiers to `5 - Production/Stable`.
- CI workflows updated for current layout (Python 3.12, wheel-completeness job, e2e job, bandit/safety job).
- `pyproject.toml`: `packages.find where = ["src"]`, package-data for `stdlib/*.i`.

### Fixed
- IDE server router now resolves the longest matching route prefix, so nested `/api/projects/...` endpoints (current/recent/create/open) are no longer shadowed by `/api/projects`.
- Empty wheel (packages excluded by `where = ["."]`).
- CLI crash on `LexerError`/`ParseError` (non-exception dataclasses caught as exceptions).
- `isoko istudio lint` crashed on the bridge parser (`Namespace` missing `format`); profile/extension bridge subcommands now parse `--name` / `--path` for parity with the standalone CLI.
- `examples/loops.i` step-expression parse guard and legacy-VM local-slot reuse.
- `isoko run` failing when invoked from a directory other than the target file's directory.
- Call-argument expressions are now analyzed before callee-kind dispatch, so `andika y` / `andika a + b` and user-function calls with undefined arguments raise `SEM200_UNDEFINED_VARIABLE` instead of silently passing.
- `isoko build` rewritten as a per-file `python -m compiler.compiler <file> -o <out>/<rel>.ipyc` build with `--target bytecode` validation and per-file failure reporting.
- isoko manifest parsing now tolerates a UTF-8 BOM (`utf-8-sig` read + `\ufeff` strip).
- isoko registry `search` normalizes bare-list, `{"results"|"objects"|"packages"}`, and nested `package` response shapes to `{name, latest_version, description}`.
- stdlib `compile_source` called a nonexistent `get_chunk()`; it now uses `Compiler().compile_source(source, filename)` and round-trips via pickle.
- isoko developer-platform registry (`src/isoko/ideveloper/ububiko.py`) is now persistent (atomic JSON store under `ISOKO_HOME`, default `~/.isoko/registry.json`) with enum/`_to_dict` conversion on load/save.

### Removed
- N/A

### Security
- See `SECURITY_VALIDATION_REPORT.md` for the full validation and dispositions.

## [0.1.0] - 2026-07-22

### Added
- Project initialization
- MIT License
- Basic project documentation
- Repository structure

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [Unreleased] - Future Versions

### Phase 1: Foundation
- Language specification
- Lexer implementation
- Parser implementation
- AST construction
- Semantic analysis
- Bytecode generation
- Basic VM

### Phase 2: Core Language
- Complete type system
- Standard library foundation
- Error handling
- Module system
- Package system

### Phase 3: Ecosystem
- Package manager (isoko)
- Testing framework (itest)
- Documentation generator (idoc)
- Formatter (iformat)
- Linter

### Phase 4: Tools
- Debugger (idebug)
- Language Server Protocol
- REPL
- Build system

### Phase 5: IDE
- I Studio development
- Editor integration
- Debugger integration
- IntelliSense

### Phase 6: Frameworks
- urubuga (web framework)
- ibiro (desktop framework)
- mobile (mobile framework)
- Specialized frameworks

### Phase 7: Self-Hosting
- Incremental self-hosting
- Full compiler in I
- Self-hosting optimization

## Versioning Scheme

We follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

## Release Categories

### Added
New features, functionality, or capabilities

### Changed
Changes to existing functionality

### Deprecated
Features that will be removed in future versions

### Removed
Features removed from this version

### Fixed
Bug fixes

### Security
Security-related changes or vulnerabilities

## Changelog Maintenance

- Update this file for every release
- Include all notable changes
- Follow the format above
- Reference related issues and pull requests
- Keep entries concise and clear

## Release Process

For detailed release procedures, see [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
