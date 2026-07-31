# Packaging & Installation Report — I Language v1.0

**Prepared by:** Release Stabilization Team
**Date:** 2026-07-31
**Artifact:** `dist/i_lang-1.0.0-py3-none-any.whl` (1,119,802 bytes, ~1.07 MB)

---

## 1. Wheel Contents

| Package | In wheel |
|---|---|
| `compiler` (+ `py.typed`) | ✅ |
| `vm` (+ `py.typed`) | ✅ |
| `isoko` | ✅ |
| `ufa`, `urubuga`, `ibiro`, `mobile`, `uam` | ✅ |
| `ububiko`, `ubwenge`, `imikino`, `sisitemu`, `igicu`, `istudio` | ✅ |
| `stdlib` (45 Python modules + `urubuga.i`) | ✅ |
| `i_lang-1.0.0.dist-info` | ✅ |

`pyproject.toml` packaging changes that made this possible:
- `[tool.setuptools.packages.find] where = ["src"]` with the full package include list.
- `[tool.setuptools.package-data]` `"stdlib" = ["*.i"]` (ships `stdlib/urubuga.i`).
- `py.typed` marker files created for `compiler` and `vm` (declared, previously absent).

## 2. Build

```powershell
python -m pip wheel . --no-deps -w dist
# → Successfully built i-lang; sha256 b601f8bcddaf4a90c06ebf37fcf6746a2e82ab945a8b70d9e085a91ff09cd251
```

> Note: `pip wheel --no-build-isolation` fails in this environment ("Cannot import
> setuptools.build_meta"); the default (isolated) build works. CI uses the default build.

## 3. Install + Smoke Tests (from the built wheel)

Installed into an isolated target with `pip install --no-deps --target <tmp>` and run with
`PYTHONPATH=<tmp>`:

| Command | Result |
|---|---|
| `python -m compiler.compiler --version` | `I Programming Language Compiler v1.0.0`, exit 0 |
| `python -m compiler.compiler -r examples/hello.i` | `Muraho, Isi!`, exit 0 |
| `python -m isoko.cli run examples/hello.i` | `Muraho, Isi!`, exit 0 |
| `python -m isoko.cli run examples/fibonacci.i` | 0…34, exit 0 |
| `python -m isoko.cli --version` | `isoko 1.0.0`, exit 0 |
| All 45 stdlib modules import from installed wheel | 0 failures |

Console script (installed in the global environment via `pip install -e .`):

| Command | Result |
|---|---|
| `i.exe --version` | `I Programming Language Compiler v1.0.0`, exit 0 |
| `i.exe -r examples/hello.i` | `Muraho, Isi!`, exit 0 |

## 4. Editable Install

`pip install -e .` succeeds; the `i` console script resolves to `C:\Python314\Scripts\i.exe`.

## 5. Known Cosmetic Item

`python -m compiler.compiler` and `python -m vm.virtual_machine` print a benign
`RuntimeWarning: '<pkg>' found in sys.modules after import of package '<pkg>'` on stderr.
It does not affect exit codes or stdout and does not fail CI. Optional cleanup for 1.1:
use `python -m compiler` style entry points with proper `__main__.py` files.

## 6. Gating Issue (must be done before RC1)

`src/stdlib/urubuga.i` is **not tracked by git** (`?? src/stdlib/urubuga.i`). It ships in a wheel
built from this working tree, but a fresh CI checkout would omit it. **Action:** `git add
src/stdlib/urubuga.i` before RC1 packaging.
