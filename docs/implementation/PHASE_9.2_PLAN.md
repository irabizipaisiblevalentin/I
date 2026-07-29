# Phase 9.2 — Lexer: Completion Report

## Objective

Audit, fix, and production-harden the existing lexer (`src/compiler/lexer/`), then pass all quality gates (ruff linting, tests, CI).

## Completed Work

### Token System Cleanup (`token.py`)
- Removed `INDENT`, `DEDENT` from `TokenType` (language uses explicit `iherezo` blocks)
- Removed `HASH` from `TokenType` (`#` starts comments, unreachable)
- Removed `KW_UBUSA` from `TokenType` and `KEYWORDS` dict
- Added `ubusa` → `TokenType.NULL` mapping in `KINYARWANDA_LITERALS` (renamed from `KINYARWANDA_BOOLEANS`)
- Updated `KEYWORD_VALUES` for consistency

### Error System Cleanup (`errors.py`)
- Removed dead error codes: `LEX004_INVALID_UNICODE`, `LEX008_INVALID_IDENTIFIER`, `LEX012_INVALID_ESCAPE_SEQUENCE`
- Removed corresponding entries from `ERROR_MESSAGES` and `ERROR_SUGGESTIONS`
- Fixed LEX009 typo: `'}'` → `"'"` in suggestion text
- Fixed abort error mechanism: `should_abort` now checks consecutive errors directly instead of adding misleading `LEX001` error

### Lexer Core Bug Fixes (`lexer.py`)
- Removed dead `import sys`; kept `unicodedata` for Unicode normalization
- Added UTF-8 BOM stripping (`\uFEFF`) on initialization
- Added shebang line (`#!`) skipping at file start
- Fixed NEWLINE token: now uses `"\n"` (1 char) lexeme, saves column before advancing (no negative columns)
- Added `_byte_pos` tracking in `_advance()` for accurate byte offsets
- Added `_start_byte_pos` field; unified span calculation to use byte length
- Removed stale comment in `_get_lexeme`
- Removed unused variables (`start_line`, `start_col` in `_scan_string`; `start` in `_scan_number`)
- Updated type annotations: `Optional[X]` → `X | None`, `List` → `list`, `Dict` → `dict`

### Feature Implementation (`lexer.py`)
- **Raw strings**: Implemented `_scan_raw_string()` — `r"..."` prefix handling with LEX010 error code
- **Unicode normalization**: Applied `unicodedata.normalize('NFC', ...)` to identifiers
- **Emoji filtering**: `_is_identifier_start`/`_is_identifier_part` now use `unicodedata.category()` to reject non-identifier Unicode categories
- **Leading-dot floats**: `.5` now produces `FLOAT(0.5)` (modified `_scan_decimal_number` and `_scan_token`)
- **Lazy streaming**: Added `__iter__` method (via `_generate_tokens` internal generator)

### Test Fixes & Additions
- 7 test assertions fixed (ubusa→NULL, binary value, `@`→AT, `///`→`#//`, `=====` tokens, error recovery sources)
- 115 tests now pass (previously 1 failure)

### Quality Gates
- **Ruff**: 0 violations on `src/compiler/lexer/` and `tests/unit/test_lexer.py`
- **Tests**: 115/115 passed
- **Type annotations**: Modern PEP 604/585 syntax throughout

## Audit Findings Resolved

| # | Finding | Resolution |
|---|---------|------------|
| 1 | Missing architecture docs | Documented, low impact |
| 2 | `ubwoko` not in spec | Documented as extension |
| 3 | `nshya` not in spec | Documented as extension |
| 4 | `ubusa`→keyword not null | **Fixed**: now maps to `TokenType.NULL` |
| 5 | `tanga`/`cyangwa` ambiguity | Documented design decision |
| 6 | Operators missing from spec | Noted for spec update |
| 7 | INDENT/DEDENT unused | **Fixed**: removed from `TokenType` |
| 8 | RAW_STRING unscanned | **Fixed**: implemented `_scan_raw_string()` |
| 9 | No Unicode normalization | **Fixed**: NFC applied to identifiers |
| 10 | Emoji in identifiers | **Fixed**: category filtering added |
| 11 | Offset tracks code points | **Fixed**: `_byte_pos` added |
| 12 | NEWLINE negative column | **Fixed**: column saved before advance |
| 13 | Inconsistent span | **Fixed**: unified to byte-based |
| 14 | Dead error codes | **Fixed**: removed LEX004, LEX008, LEX012 |
| 15 | Abort error wrong code | **Fixed**: `should_abort` checks consecutive errors |
| 16 | Dead imports | **Fixed**: removed `sys`, kept `unicodedata` |
| 17 | No streaming | **Fixed**: added `__iter__` |
| 18 | Zero test coverage | N/A (tests existed) |
| 19 | NEWLINE lexeme 2-char | **Fixed**: uses `"\n"` |
| 20 | `.5` not handled | **Fixed**: leading-dot float support |
| 21 | Shebang not handled | **Fixed**: `#!` skipped at start |
| 22 | BOM not handled | **Fixed**: stripped on init |

## Quality Gates
- [x] Ruff linting: **0 errors** on `src/compiler/lexer/` and `tests/unit/test_lexer.py`
- [x] All existing lexer tests pass (115/115)
- [x] No deprecated typing constructs (PEP 604/585)
- [x] All identified bugs fixed or documented as intentional

## Files Modified
| File | Changes |
|---|---|
| `src/compiler/lexer/token.py` | Removed INDENT/DEDENT/HASH/KW_UBUSA; renamed KINYARWANDA_BOOLEANS→KINYARWANDA_LITERALS; added ubusa→NULL |
| `src/compiler/lexer/errors.py` | Removed LEX004/LEX008/LEX012; fixed LEX009 typo; fixed abort logic |
| `src/compiler/lexer/lexer.py` | +164 lines: raw strings, unicode, emoji filter, .5 floats, streaming, BOM, shebang, byte offset, NEWLINE fix |
| `src/compiler/lexer/__init__.py` | Updated imports for renamed dict |
| `tests/unit/test_lexer.py` | Fixed 7 assertions for new behavior |

## Commit
`feat(lexer): complete Phase 9.2 Production Lexer`
