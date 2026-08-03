# I Programming Language — Vision 1.0.0

**A professional programming language designed around Kinyarwanda.**

This is the official **Vision 1.0.0** release of the I reference toolchain — a
stable, documented, and tested milestone of the world's first professional
programming language built around natural Kinyarwanda syntax. It is the result
of months of design, implementation, and verification toward African
technological independence.

> _Kuvana Imana, Kubaka Icyo Turije_ — From God, Building What We Have.

---

## Highlights

- **Language** — Kinyarwanda-first syntax: blocks open with a keyword and close
  with `iherezo`; word operators like `irenze` (greater than), `munsi_ya` (less
  than), `kandi`, and `cyangwa`.
- **Stable, frozen language specification** — `docs/specification/LANGUAGE_SPECIFICATION.md`
  is under **LANGUAGE FREEZE** for 1.0.0; changes require an RFC for 2.0.
- **Complete toolchain** — compiler (`i`), bytecode VM, 44-module standard
  library, `isoko` project manager, `ufa` diagnostics engine, and the I Studio
  IDE platform.
- **I Studio IDE** — browser-based web IDE (`istudio-ide`, default
  `http://127.0.0.1:8790`) **and** a native Windows desktop app (pywebview) with
  an Inno Setup installer.
- **Verified quality** — 4,285+ passing tests, cross-platform CI
  (Ubuntu/Windows/macOS), ruff/mypy/bandit/safety scans, and a published
  security validation report.

## Installation

```bash
pip install i-program
```

Then run your first program:

```bash
i hello.i -r
```

## Downloads

Prebuilt installers and archives for this release:

- **Windows installer**: `IStudioIDE-Setup-1.0.0.exe`
- **Windows portable**: `istudio-ide-1.0.0-win-x64.zip` (no installation required)
- **Source archive** and **Python wheel/sdist** attached to this release
- **SHA-256 checksums**: `checksums.txt`

## Full Release Notes

- [Changelog](CHANGELOG.md)
- [Migration guide (0.1.0 → 1.0.0)](docs/user-guide/migration-guide.md)
- [Language specification (frozen)](docs/specification/LANGUAGE_SPECIFICATION.md)
- [Getting started](docs/user-guide/getting-started.md)

## Acknowledgments

Built by **Irabizi Paisible Valentin** — Founder, Rwanda.

---

_Made in Rwanda, for Africa, for the world._
