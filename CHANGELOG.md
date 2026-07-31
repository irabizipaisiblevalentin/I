# Changelog

All notable changes to the I Programming Language will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-31

### Added
- Packaging: wheel now ships all 15 packages from `src/` plus the `stdlib/urubuga.i` framework source and `py.typed` markers; `i` console script installs and runs.
- CLI: `i --version`, clean diagnostics for lexical/parse errors, `-o` bytecode artifact output, and a `__main__` guard for `vm.virtual_machine`.
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
- Empty wheel (packages excluded by `where = ["."]`).
- CLI crash on `LexerError`/`ParseError` (non-exception dataclasses caught as exceptions).
- `examples/loops.i` step-expression parse guard and legacy-VM local-slot reuse.
- `isoko run` failing when invoked from a directory other than the target file's directory.

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
