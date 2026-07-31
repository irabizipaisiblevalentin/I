# Lexer Architecture Audit Report

| Metadata | |
|---|---|
| **Phase** | 9.2A — Lexer Architecture Audit |
| **Date** | July 2026 |
| **Auditor** | OpenCode Engineering Agent |
| **Status** | **COMPLETE — 22 findings documented** |

---

## Reference Documents Reviewed

| Document | Path | Status |
|---|---|---|
| LANGUAGE_SPECIFICATION.md | `docs/specification/LANGUAGE_SPECIFICATION.md` | Reviewed |
| ARCHITECTURE.md | `ARCHITECTURE.md` | Reviewed (§ Lexer Architecture) |
| LEXER_IMPLEMENTATION.md | `docs/implementation/LEXER_IMPLEMENTATION.md` | Reviewed |
| PRODUCTION_IMPLEMENTATION_CONSTITUTION.md | `docs/governance/PRODUCTION_IMPLEMENTATION_CONSTITUTION.md` | Reviewed |
| COMPILER_ARCHITECTURE.md | `docs/architecture/COMPILER_ARCHITECTURE.md` | **NOT FOUND** |
| LEXER_DESIGN.md | `docs/architecture/LEXER_DESIGN.md` | **NOT FOUND** |
| ERROR_SYSTEM.md | `docs/architecture/ERROR_SYSTEM.md` | **NOT FOUND** |
| STYLE_GUIDE.md | `docs/STYLE_GUIDE.md` | **NOT FOUND** |
| ENGINEERING_EXECUTION_MANUAL.md | `docs/governance/ENGINEERING_EXECUTION_MANUAL.md` | **NOT FOUND** |

### Finding 1: Missing Architecture Documents

Four referenced documents do not exist: COMPILER_ARCHITECTURE.md, LEXER_DESIGN.md, ERROR_SYSTEM.md, STYLE_GUIDE.md. The lexer design is partially covered by the existing `LEXER_IMPLEMENTATION.md` and `ARCHITECTURE.md`. The Constitution references these by name but they were never created.

**Impact**: Low. The existing `LEXER_IMPLEMENTATION.md` and source code serve as the authoritative design reference.

---

## 1. Token Categories

### 1.1 Complete Token Inventory

The lexer defines **109 token types** (TokenType IntEnum values 1–109):

| Category | Count | Token Types |
|---|---|---|
| **Literals** | 9 | INTEGER, FLOAT, STRING, RAW_STRING, TRIPLE_STRING, CHARACTER, BOOLEAN_TRUE, BOOLEAN_FALSE, NULL |
| **Identifier** | 1 | IDENTIFIER |
| **Keywords** | 43 | KW_NIBA, KW_CYANGWA, KW_CYANGWA_NIBA, KW_KUGENDA, KW_GUKOMA, KW_SUBIRA, KW_TANGA_YIELD, KW_KORA, KW_WIHUSE, KW_KUGEZA, KW_KURI, KW_MURI, KW_BURI, KW_SHYIRA, KW_SHYIRA_KO, KW_UMURIMO, KW_IGICERI, KW_IKINDI, KW_URWEGO, KW_AKABUTO, KW_URUBINGO, KW_UBWOKO, KW_KUGIRA, KW_GUKORA, KW_NSHYA, KW_SHYIRAMO, KW_TANGA_EXPORT, KW_KUGIRA_NGO, KW_KANDI, KW_CYANGWA_LOG, KW_BITEWE, KW_ARI, KW_SI, KW_GUSHYINGURA, KW_KUBIKA, KW_IKINYOMA, KW_IHEREZO, KW_UBUSA, KW_SELF, KW_SUPER, KW_TRUE_EN, KW_FALSE_EN, KW_NULL_EN |
| **Arithmetic** | 7 | PLUS, MINUS, STAR, SLASH, PERCENT, STAR_STAR, SLASH_SLASH |
| **Comparison** | 8 | EQ_EQ, BANG_EQ, GT, LT, GT_EQ, LT_EQ, IS_EQ, BANG_IS_EQ |
| **Logical** | 3 | AND_AND, OR_OR, BANG |
| **Bitwise** | 7 | AMP, PIPE, CARET, TILDE, LT_LT, GT_GT, GT_GT_GT |
| **Assignment** | 7 | EQ, PLUS_EQ, MINUS_EQ, STAR_EQ, SLASH_EQ, PERCENT_EQ, STAR_STAR_EQ |
| **Delimiters** | 19 | LPAREN, RPAREN, LBRACKET, RBRACKET, LBRACE, RBRACE, COMMA, COLON, SEMICOLON, DOT, DOT_DOT, DOT_DOT_DOT, ARROW, FAT_ARROW, QUESTION, QUESTION_DOT, AT, HASH, BACKSLASH |
| **Special** | 5 | EOF, NEWLINE, INDENT, DEDENT, ERROR |
| **Total** | **109** | |

### Finding 2: Keyword `ubwoko` (type) not in Language Specification

**Status**: IMPLEMENTATION EXTENSION
- `ubwoko` → KW_UBWOKO exists in KEYWORDS dict (line 287) and LEXER_IMPLEMENTATION.md
- Language specification does not list `ubwoko` as a keyword
- **Recommendation**: Add to LANGUAGE_SPECIFICATION.md or remove from implementation

### Finding 3: Keyword `nshya` (new) not in Language Specification

**Status**: IMPLEMENTATION EXTENSION
- `nshya` → KW_NSHYA exists in KEYWORDS dict (line 292) and LEXER_IMPLEMENTATION.md
- Language specification does not list `nshya` as a keyword
- **Recommendation**: Add to LANGUAGE_SPECIFICATION.md or remove from implementation

### Finding 4: `ubusa` mapped as keyword, should be null literal

**Status**: INCONSISTENCY
- Language specification (line 155): `ubusa # null`
- Implementation: `ubusa` → KW_UBUSA (keyword type), value=None (via KEYWORD_VALUES)
- Should produce: `TokenType.NULL` with value=None (consistent with `yego`/`oya` which map to BOOLEAN_TRUE/BOOLEAN_FALSE literals)
- **Recommendation**: Move `ubusa` from KEYWORDS dict to KINYARWANDA_BOOLEANS-like handling, producing TokenType.NULL with value=None

### Finding 5: `tanga` and `cyangwa` ambiguity

**Status**: ACKNOWLEDGED DESIGN
- `tanga` maps to KW_TANGA_YIELD by default, with KW_TANGA_EXPORT for context-based reclassification
- `cyangwa` maps to KW_CYANGWA (else) and KW_CYANGWA_LOG (or) contextually
- Current implementation maps all occurrences to a single token type; parser must reclassify
- **Recommendation**: Document this as a design decision in LEXER_IMPLEMENTATION.md

### Finding 6: `//`, `**=`, `===`, `!==`, `<<`, `>>`, `>>>`, `^`, `~`, `..`, `...`, `->`, `=>`, `?`, `?.`, `@`, `#`, `\` tokens not in Language Specification

**Status**: IMPLEMENTATION EXTENSION
- These operators/tokens exist in the implementation but are not mentioned in LANGUAGE_SPECIFICATION.md
- Some are standard (// floor div, bitwise ops for systems programming)
- `===`/`!==` are common in JS-like languages for strict equality
- `->`/`=>` are used for function return types and lambda syntax
- `?.` is null-conditional access
- **Recommendation**: Add to LANGUAGE_SPECIFICATION.md or remove. Document rationale.

### Finding 7: INDENT/DEDENT tokens defined but never emitted

**Status**: UNUSED IMPLEMENTATION
- `TokenType.INDENT` (107) and `TokenType.DEDENT` (108) are defined
- **Zero scanning logic** exists — the lexer has no indentation tracking code
- The language uses `iherezo` as explicit block terminator (not significant whitespace)
- **Recommendation**: Remove INDENT/DEDENT from TokenType if not needed, or implement if the language intends significant indentation

### Finding 8: RAW_STRING token type defined but never scanned

**Status**: UNUSED TOKEN TYPE
- `TokenType.RAW_STRING` (4) exists but `_scan_string` has no `r"..."` prefix handling
- LEXER_IMPLEMENTATION.md lists raw strings as "planned"
- `_scan_string` only checks for `"` → triple distinguish, no prefix checks
- **Recommendation**: Either implement raw string scanning or remove the token type

---

## 2. Unicode Strategy

### 2.1 Current Implementation

| Aspect | Implementation | Assessment |
|---|---|---|
| **UTF-8 handling** | Source loaded as Python `str` (implicitly decoded as UTF-8 by `open()` or passed as-is) | Correct |
| **Identifier characters** | Uses `char.isalpha()` / `char.isalnum()` which handles Unicode via Python's Unicode database | Correct for XID_Start/XID_Continue |
| **Normalisation** | No NFC/NFD normalisation applied to identifiers | **GAP** — `é` (U+00E9) and `e\u0301` (U+0065 U+0301) treated as different identifiers |
| **Invalid UTF-8 recovery** | Handled by Python's str decoder at file-read time, not by lexer | Acceptable |
| **Emoji policy** | Emoji characters pass `isalpha()` in some cases, may be accepted as identifiers | **GAP** — Should explicitly reject emoji in identifiers |
| **Mixed-language support** | Unicode identifiers allowed, bilingual error messages (EN/RW) | Correct |

### Finding 9: No Unicode normalisation for identifiers

**Status**: INCONSISTENCY
- `nība` (composed) and `ni\u0304ba` (decomposed) would be treated as different identifiers
- Python strings are compared by code point, not by canonical equivalence
- **Recommendation**: Apply `unicodedata.normalize('NFC', ...)` to identifiers (note: `unicodedata` is already imported but unused)

### Finding 10: Emoji in identifiers not rejected

**Status**: POTENTIAL BUG
- `char.isalpha()` returns `True` for some emoji modifiers
- `_is_identifier_start` and `_is_identifier_part` may accept characters that aren't valid identifiers
- **Recommendation**: Add explicit category filtering using `unicodedata.category()` — accept only L (letter), Nl (letter number), Mn (nonspacing mark), Mc (spacing mark), Pc (connector punctuation) categories

### 2.2 Recommended Unicode Strategy

```
1. Load source as UTF-8 (Python str, already done)
2. Skip UTF-8 BOM (\uFEFF at start of file) — NOT IMPLEMENTED
3. Normalise identifiers to NFC before storing as lexeme — NOT IMPLEMENTED
4. Reject identifiers containing emoji or non-identifier Unicode categories — NOT IMPLEMENTED
5. Continue using unicodedata (already imported but unused)
```

---

## 3. Source Location Tracking

### 3.1 TokenLocation Fields

| Field | Type | Description | Current Implementation |
|---|---|---|---|
| `line` | int | 1-indexed line number | ✓ Correct |
| `column` | int | 1-indexed column number | ✓ Correct for ASCII, **BUG** for NEWLINE |
| `offset` | int | Byte offset from start of file | **BUG** — tracks code point offset, not byte offset |
| `span` | int | Token length in bytes | **INCONSISTENT** — `_make_token` uses byte length, `_emit` uses code point count |

### Finding 11: `offset` tracks code points, not bytes

**Status**: BUG
- `_pos` is incremented by 1 per Python character (code point)
- TokenLocation docstring says "Byte offset from start of file"
- For multi-byte UTF-8 characters (like `ñ` = U+00F1 = 2 bytes), `_pos` gives code point index, not byte offset
- **Impact**: Error messages can't accurately point to byte position in file
- **Fix options**:
  - (a) Track byte offset separately via `len(char.encode('utf-8'))` in `_advance`
  - (b) Change docstring to "code point offset" and accept the inconsistency
  - **Recommendation**: Option (a) — add `_byte_pos` field to Lexer

### Finding 12: NEWLINE token has negative column

**Status**: BUG
- In `_scan_token`: `self._advance()` consumes `\n` → `_line` incremented, `_column = 1`
- Then `_make_token(TokenType.NEWLINE, "\\n")` computes:
  - `column = self._column - len("\\n") = 1 - 2 = -1`
- **Impact**: Negative column in NEWLINE token location
- **Root cause**: `_make_token` calculates starting position by subtracting lexeme length from current position, but position is already past the token AND lexeme is `"\\n"` (2 chars representing `\n`) instead of `"\n"` (1 char)
- **Recommendation**: Fix `_scan_token` to save column before advancing, or use `_emit`-style calculation

### Finding 13: `_make_token` and `_emit` use different span calculations

**Status**: INCONSISTENCY
- `_make_token`: `span = len(lexeme.encode("utf-8"))` → bytes
- `_emit`: `span = self._pos - self._start_pos` → code points
- **Recommendation**: Unify to use byte length consistently (requires fixing Finding 11 first)

---

## 4. Error Recovery

### 4.1 Error Code Inventory

| Code | Name | Status | Recovery |
|---|---|---|---|
| LEX001 | Invalid Character | ✓ Implemented | Consume char, continue |
| LEX002 | Unterminated String | ✓ Implemented | Return partial token |
| LEX003 | Invalid Number | ✓ Implemented | Skip to next delimiter |
| LEX004 | Invalid Unicode | ❌ **UNUSED** | N/A — no UTF-8 validation code |
| LEX005 | Invalid Escape | ✓ Implemented | Return literal `\x` |
| LEX006 | Unterminated Comment | ✓ Implemented | End of file terminates |
| LEX007 | Integer Overflow | ✓ Implemented | Clamp to MAX_I64, continue |
| LEX008 | Invalid Identifier | ❌ **UNUSED** | N/A — never emitted |
| LEX009 | Unterminated Char | ✓ Implemented | Return partial token |
| LEX010 | Unterminated Raw String | ❌ **UNIMPLEMENTED** | No raw string scanner exists |
| LEX011 | Unterminated Triple String | ✓ Implemented | Return partial token |
| LEX012 | Invalid Escape Sequence | ❌ **UNUSED** | LEX005 is used instead |

### Finding 14: Error codes LEX004, LEX008, LEX010, LEX012 are dead code

**Status**: DEAD CODE
- **LEX004** (Invalid Unicode): No UTF-8 validation code exists in the lexer
- **LEX008** (Invalid Identifier): Never emitted — lexer emits LEX001 for bad start chars
- **LEX010** (Unterminated Raw String): No raw string scanner exists
- **LEX012** (Invalid Escape Sequence): LEX005 is used for all escape errors
- **Recommendation**: Remove dead error codes or implement their intended handlers

### Finding 15: LexerErrorCollector abort error uses wrong code

**Status**: MINOR BUG
- Line 229: `abort = LexerError(code=LexerErrorCode.LEX001_INVALID_CHAR, ...)`
- The abort error should signal "too many errors" not "invalid character"
- **Recommendation**: Add a dedicated abort error code or use `LEX008_INVALID_IDENTIFIER` (which is dead)

### 4.2 Recovery Strategy Summary

| Situation | Strategy | Assessment |
|---|---|---|
| Invalid character | Consume, add error, continue | ✓ Correct |
| Unterminated string | Return partial, continue | ✓ Correct |
| Invalid number | Skip, add error, continue | ✓ Correct |
| Integer overflow | Clamp to MAX_I64, emit token, continue | ✓ Pragmatic |
| Unterminated comment (multi-line) | Reached EOF, add error, continue | ✓ Correct |
| Escape error | Return literal, continue | ✓ Correct |
| Max errors | 100 errors → stop | ✓ Correct |
| Consecutive errors | 10 sequential → abort | ✓ Correct |

---

## 5. Performance Strategy

### 5.1 Current Architecture

| Aspect | Current Implementation | Assessment |
|---|---|---|
| **Memory allocation** | Allocates `List[Token]` — one object per token | Acceptable for bootstrap |
| **Zero-copy** | Lexeme is `source[start:end]` — creates new string | **GAP** — could use slices/views |
| **Buffered reading** | Entire source loaded as `str` upfront | Acceptable for bootstrap |
| **Incremental lexing** | Not supported — tokenize() processes entire file | **GAP** — needed for IDE/LSP |
| **Token streaming** | Returns `List[Token]`, not generator | **GAP** — prevents streaming |
| **`sys` import** | Imported but never used | Dead import |
| **`unicodedata` import** | Imported but never used | Dead import |

### Finding 16: `sys` and `unicodedata` are dead imports

**Status**: TRIVIAL
- Both imported at top of `lexer.py` but never referenced in method bodies
- **Recommendation**: Remove unused imports

### Finding 17: No incremental/streaming lexing support

**Status**: FUNCTIONAL GAP
- `Lexer.tokenize()` returns `List[Token]` — must complete before any token is usable
- No `__iter__` or generator-based API for streaming
- **Impact**: Large files consume O(n) memory; IDE can't provide partial results
- **Recommendation**: Add `__iter__` method yielding tokens lazily for Phase 9.2+; keep `tokenize()` for compatibility

### 5.2 Expected Throughput Targets

| Metric | Target | Current Estimate (bootstrap) |
|---|---|---|
| Tokens/second | ≥500K | ~200K (untested) |
| Peak memory (100K LOC) | ≤50MB | ~100MB (allocates all tokens) |
| Startup to first token | ≤1ms | 100% before first token (full file) |

---

## 6. Testing Matrix

### 6.1 Required Test Coverage

| Test Category | Count (est.) | Coverage Target | Current Status |
|---|---|---|---|
| **Unit: TokenType** | 120+ | Every token type exists, every keyword maps correctly | ❌ 0 tests |
| **Unit: Token** | 30+ | Creation, properties, is_keyword/is_operator/is_literal, repr | ❌ 0 tests |
| **Unit: TokenLocation** | 15+ | Line/column/offset/span/str | ❌ 0 tests |
| **Unit: Lexer — single char** | 10+ | All 10 single-char delimiters | ❌ 0 tests |
| **Unit: Lexer — operators** | 30+ | All multi-char operators, precedence edge cases | ❌ 0 tests |
| **Unit: Lexer — comments** | 15+ | Single-line, multi-line, nested, doc comments, unterminated | ❌ 0 tests |
| **Unit: Lexer — integers** | 20+ | Decimal, hex, octal, binary, underscores, overflow, edge cases | ❌ 0 tests |
| **Unit: Lexer — floats** | 15+ | Standard, scientific, fractional-only, edge cases | ❌ 0 tests |
| **Unit: Lexer — strings** | 25+ | Regular, triple-quoted, escape sequences, unterminated | ❌ 0 tests |
| **Unit: Lexer — chars** | 10+ | ASCII, Unicode, escape sequences, unterminated | ❌ 0 tests |
| **Unit: Lexer — identifiers** | 15+ | ASCII, Unicode, Kinyarwanda, with digits, underscore-only | ❌ 0 tests |
| **Unit: Lexer — keywords** | 45+ | Every keyword maps correctly, case sensitivity, partial match | ❌ 0 tests |
| **Unit: Lexer — edges** | 20+ | Empty source, whitespace-only, BOM, shebang, very large input | ❌ 0 tests |
| **Unit: ErrorSystem** | 25+ | Error codes, bilingual messages, suggestions, collector limits | ❌ 0 tests |
| **Unit: Lexer — error recovery** | 15+ | Error collector limits, consecutive error abort, recovery after error | ❌ 0 tests |
| **Snapshot tests** | 10+ | Full token output for representative `.i` files | ❌ 0 tests |
| **Fuzz tests** | 1000+ | Random byte sequences, partial UTF-8, edge characters | ❌ 0 tests |
| **Property tests** | 10+ | Idempotency, keyword set completeness, number round-trip | ❌ 0 tests |
| **Unicode tests** | 20+ | Kinyarwanda identifiers, combined chars, RTL, BOM | ❌ 0 tests |
| **Regression tests** | TBD | Tests for each fixed bug | ❌ 0 tests |
| **Performance tests** | 5+ | Tokens/sec, peak memory, large file | ❌ 0 tests |

### Finding 18: Zero test coverage for entire lexer module

**Status**: CRITICAL GAP
- No test files exist for any lexer component
- Violates Constitution §7: "Every exported symbol requires tests"
- **Recommendation**: Priority for Phase 9.2 implementation

---

## 7. Public API Review

### 7.1 Current Exports (`__init__.py`)

| Export | Source | Purpose | Assessment |
|---|---|---|---|
| `TokenType` | `token.py` | Enum of all 109 token types | Correct — essential for all downstream consumers |
| `Token` | `token.py` | Immutable token dataclass | Correct — fundamental data type |
| `TokenLocation` | `token.py` | Source location for tokens | Correct — needed for error reporting |
| `KEYWORDS` | `token.py` | Kinyarwanda → TokenType dict | Correct — useful for parser/IDE |
| `KEYWORD_VALUES` | `token.py` | TokenType → semantic value map | Correct — needed for keyword values |
| `KINYARWANDA_BOOLEANS` | `token.py` | yego/oya → BOOLEAN_TRUE/FALSE | Correct — specific Kinyarwanda literal handling |
| `Lexer` | `lexer.py` | Main lexer class with full API | Correct — primary tokenization interface |
| `tokenize` | `lexer.py` | Convenience function (tokens, errors) | Correct — simple one-shot API |
| `LexerError` | `errors.py` | Single error with bilingual messages | Correct — error information |
| `LexerErrorCode` | `errors.py` | Enum of 12 error codes | Correct — error identification |
| `LexerErrorCollector` | `errors.py` | Error collection with limits | Correct — error aggregation |
| `ERROR_MESSAGES` | `errors.py` | Error code → bilingual message map | Correct — message lookup |
| `ERROR_SUGGESTIONS` | `errors.py` | Error code → suggestion map | Correct — user guidance |

### 7.2 Recommendations

- Add `Lexer.__iter__()` for streaming token access
- Add `LexerError.message_en` and `LexerError.message_rw` as public properties (already exist)
- Ensure all public methods have docstrings (✓ mostly done)
- Add type hints to all public methods (✓ done)

---

## 8. Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | **Ubusa→KW_UBUSA mapping confuses parser** — parser expects NULL for null literal, gets keyword | High | Medium | Fix mapping: ubusa → TokenType.NULL (Finding 4) |
| R2 | **Negative column in NEWLINE tokens** — tooling/IDE breaks on negative column numbers | High | Low | Fix `_make_token` column calculation (Finding 12) |
| R3 | **Code point vs byte offset mismatch** — error messages point to wrong file positions for files with multi-byte UTF-8 | Medium | Medium | Track byte offset separately (Finding 11) |
| R4 | **Unicode identifier confusion** — composed vs decomposed forms treated as different identifiers | Medium | Medium | Apply NFC normalisation (Finding 9) |
| R5 | **Dead error codes create false expectations** — LEX004, LEX008, LEX010, LEX012 look implemented but never fire | Medium | Low | Remove or implement unused error codes (Finding 14) |
| R6 | **No streaming support** — IDE/LSP integration blocked | Medium | High | Add `__iter__` or generator API (Finding 17) |
| R7 | **Empty imports waste init time** — sys/unicodedata imported but unused | Low | Low | Remove dead imports (Finding 16) |
| R8 | **Spec deviation** — ubwoko, nshya, and multiple operators exist in lexer but not in spec | Low | Medium | Update spec or remove tokens (Findings 2, 3, 6) |
| R9 | **INDENT/DEDENT expected by parser** — if parser expects indentation tokens, they're missing | Unknown | High | Clarify: does language use significant whitespace or explicit `iherezo` blocks? (Finding 7) |
| R10 | **Raw string token type exists but scanning is missing** — consumer may expect RAW_STRING tokens | Low | Low | Implement or remove (Finding 8) |

---

## Summary of Findings

| # | Severity | Finding | File(s) | Action |
|---|---|---|---|---|
| 1 | Low | Missing architecture documents | N/A | Create or link existing docs |
| 2 | Medium | `ubwoko` not in spec | `token.py:287` | Document extension or update spec |
| 3 | Medium | `nshya` not in spec | `token.py:292` | Document extension or update spec |
| 4 | **High** | `ubusa`→keyword not null literal | `token.py:313` | Fix mapping to TokenType.NULL |
| 5 | Low | `tanga`/`cyangwa` ambiguity | `token.py:261,268` | Document design decision |
| 6 | Medium | Operators missing from spec | `token.py:105-167` | Update LANGUAGE_SPECIFICATION.md |
| 7 | Medium | INDENT/DEDENT defined but unused | `token.py:162-163` | Clarify: remove or implement |
| 8 | Medium | RAW_STRING defined but unscanned | `token.py:26` | Implement or remove |
| 9 | Medium | No Unicode NFC normalisation | `lexer.py:766-790` | Apply normalisation |
| 10 | Low | Emoji in identifiers | `lexer.py:892-910` | Add category filtering |
| 11 | **High** | Offset tracks code points not bytes | `lexer.py:852-860` | Track byte offset separately |
| 12 | **High** | NEWLINE token has negative column | `lexer.py:107-112` | Fix column calculation |
| 13 | Low | Inconsistent span calculation | `lexer.py:852-876` | Unify span logic |
| 14 | Medium | 4 dead error codes | `errors.py:19-30` | Implement or remove |
| 15 | Low | Abort error uses wrong code | `errors.py:229-235` | Fix abort error code |
| 16 | Trivial | Dead imports (sys, unicodedata) | `lexer.py:10-11` | Remove unused imports |
| 17 | Medium | No incremental/streaming lexing | `lexer.py:77-90` | Add generator API |
| 18 | **Critical** | Zero test coverage | All files | Implement per Phase 9.2 plan |
| 19 | Low | `_make_token` uses `"\\n"` lexeme (2 chars) for newline | `lexer.py:110` | Use `"\n"` (1 char) for correct calc |
| 20 | Low | `_scan_decimal_number` doesn't handle leading `.5` | `lexer.py:700-762` | Verify spec requires this (spec shows 0.5 not .5) |
| 21 | Low | Shebang line `#!` not handled | `lexer.py:126-128` | Skip `#!` at start of file |
| 22 | Low | UTF-8 BOM not handled | `lexer.py:43-61` | Strip BOM on init |

---

## Phase 9.2 Plan Updates Required

Based on audit findings, the following updates to `PHASE_9.2_PLAN.md` are recommended:

1. **Add Fix Tasks before Testing** — Finding 11 (byte offset), Finding 12 (NEWLINE column), Finding 4 (ubusa) are bugs that must be fixed before tests can be written (tests would fail)
2. **Add BOM/Shebang handling** — Finding 21, 22 — simple edge-case implementations
3. **Add Unicode normalisation** — Finding 9 — apply NFC to identifiers
4. **Add emoji filtering** — Finding 10 — reject emoji in identifiers
5. **Add `__iter__` to Lexer** — Finding 17 — streaming support
6. **Remove dead code** — Findings 14, 15, 16 — clean up before testing
7. **Decision needed on INDENT/DEDENT** — Finding 7 — confirm block structure strategy
8. **Decision needed on RAW_STRING** — Finding 8 — implement or remove

---

*Prepared according to the Production Implementation Constitution v1.0, Section 8 (Documentation Standard).*
