# Phase 9.3 — Parser: Implementation Plan

## Objective

Audit, fix, and production-harden the existing parser (`src/compiler/parser/`) to produce a fully validated AST from the Lexer's token stream, passing all quality gates (ruff, tests, CI).

## Current State

The parser is a **complete recursive-descent + Pratt parser** (1065 lines) with:
- 15-level precedence table (Pratt expression parsing)
- 20+ statement types (declarations, control flow, blocks, expressions)
- Bilingual (English/Kinyarwanda) error diagnostics with 8 error codes
- Error collector with configurable abort conditions
- Comprehensive AST (1439 lines, 30+ node types, visitor/validation/serialization)
- Test suite: `tests/unit/test_parser.py` (790 lines, 92 tests)
- Architecture doc: `docs/implementation/PARSER_IMPLEMENTATION.md`

## Blocking Bugs

### 1. Span → Location field name mismatch
- AST uses `location: SourceLocation` (inherited from `ASTNode`)
- Parser passes `span=SourceSpan.from_token(tok)` everywhere
- `SourceSpan = SourceLocation` (alias in nodes.py:1423) — same type, different kwarg name
- **Fix**: Replace every `span=` with `location=` in `parser.py`

### 2. LiteralExpr token → token_type field name
- AST defines `LiteralExpr.value: Any` + `token_type: TokenType`
- Parser passes `token=tok` (should be `token_type=tok.type`)
- **Fix**: Change `token=tok` → `token_type=tok.type` in `_prefix()`

### 3. ExportStmt not imported
- `_export_declaration()` returns `ExportStmt` but it's missing from `from ..ast.nodes import (...)`
- **Fix**: Add `ExportStmt` to imports

### 4. Any not imported
- `GroupingExprWrapper` uses `expression: Any` annotation but `Any` is not imported
- **Fix**: Add `from typing import Any`

## Ruff Violations (45 fixes)

| Category | Count | Action |
|----------|-------|--------|
| UP035/UP006/UP045 deprecated typing | 8 | Replace `List`→`list`, `Optional`→`X|None`, `Dict`→`dict`, `Callable`→`collections.abc.Callable` |
| F401 unused imports | 10 | Remove `ASTNode`, `SetExpr`, `TupleExpr`, `ParseError`, `Callable`, `Dict`, test unused imports |
| F841 unused variables | 2 | Remove `eq` in `_assignment_expr`, `dot` in `_get_expr` |
| I001 import sorting | 3 | Organize import blocks |
| W293 trailing whitespace | 3 | Clean blank lines |
| F821 undefined names | 2 | Fix `ExportStmt`, `Any` |

## Missing Grammar Productions

### Lambda Expressions (`(params) => expr`)
- **Spec**: `shyira add = (a: int, b: int) -> int => a + b`
- **Current**: `_lambda_expr()` defined at line 931 but **not wired** into `_prefix()`
- **Fix**: In `_prefix()`, when `LPAREN` is found, peek for `RPAREN` then `FAT_ARROW`; if so, route to `_lambda_expr()` instead of grouping

### Tuple Expressions (`(1, 2, 3)`)
- **Spec**: Not explicitly in grammar summary but `TupleExpr` node exists
- **Current**: `(1, 2)` produces `GroupingExprWrapper` (single expr), commas cause errors
- **Fix**: In `_prefix()`, after `LPAREN`, parse `_expression()` then check for `COMMA`; if found, build `TupleExpr`

## Error Recovery Enhancements
- Current: basic recovery at statement boundaries, synchronise on NEWLINE/keywords
- Add: source snippets in error messages
- Add: synchronisation at statement-starting keyword boundaries
- Ensure: `PARS004` (unterminated block) recovery doesn't consume too many tokens

## Source Mapping
- Phase 9.2 added `_byte_pos` tracking to Lexer; `Token.offset` and `Token.span` are byte-based
- Parser uses `SourceSpan.from_token(token)` → fields `start_offset`, `end_offset` already populated
- No changes needed — Phase 9.2 byte offsets flow through automatically

## Test Plan

| Phase | Action | Expected |
|-------|--------|----------|
| Baseline | Fix bugs → run 92 existing tests | 92/92 pass |
| Coverage | Add tests for lambda, tuple, exports | 10+ new tests |
| Edge cases | Empty source, deeply nested, unicode, recovery | 5+ new tests |
| Fuzz | Malformed source sequences | 5+ new tests |
| Ruff | Lint all files | 0 violations |

## Quality Gates

- [ ] All 92+ parser tests pass
- [ ] 0 ruff violations on `src/compiler/parser/` and `tests/unit/test_parser.py`
- [ ] No unused imports or variables
- [ ] Modern Python typing (PEP 604/585)
- [ ] Lambda expressions parse correctly
- [ ] Tuple expressions parse correctly
- [ ] Error recovery handles malformed input without infinite loops
- [ ] Source locations (byte offsets) propagate correctly from lexer

## Files to Modify

| File | Changes |
|------|---------|
| `src/compiler/parser/parser.py` | span→location, token→token_type, lambda wiring, tuple parsing, ExportStmt import, ruff fixes |
| `src/compiler/parser/errors.py` | Remove unused imports, typing modernization |
| `src/compiler/parser/__init__.py` | Import sort fix |
| `tests/unit/test_parser.py` | Remove unused imports, add lambda/tuple/export tests |
| `docs/implementation/PARSER_IMPLEMENTATION.md` | Verify accuracy after changes |
| `docs/implementation/PHASE_9.3_PLAN.md` | This file — status updates |

## Out of Scope (Phase 9.3)

- Semantic analysis (Phase 9.4)
- Type checking (Phase 9.5)
- Match expressions, async/await, pattern matching (future phases)
- Full IDE integration (I Studio phase)

## Post-Completion: Phase 9.4 Preparation

After commit, prepare SPRINT 9.4 plan including:
- Semantic analysis objectives
- Scope management strategy
- Symbol table architecture
- Namespace handling
- Import resolution
- Diagnostics strategy
- Testing plan
- Benchmark plan
- Implementation milestones

## Deliverables

- Committed code with `feat(parser): implement production-grade recursive descent parser`
- Architecture compliance report (this doc)
- Grammar coverage report
- AST node implementation summary
- Test statistics
- Security review notes
- Remaining risks
- Phase 9.4 readiness plan
