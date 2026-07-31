# Design Decision Log — I Programming Language

This file records significant design decisions, trade-offs considered, and rationale.

---

## Sprint 9.5 — Production Type Checker

### D001: Immutable Type Instances with Unique IDs

**Decision:** Each type instance has a unique `type_id` (UUID). Singleton types (`TYPE_INT`, `TYPE_FLOAT`, etc.) ensure canonical primitives while complex types (collections, generics) get unique IDs.

**Rationale:**
- Enables future incremental compilation and caching
- Allows identity-based comparison for debugging
- Clean separation between type identity and value equality

**Trade-off:** Slightly higher memory per type instance vs. pure flyweight pattern.

---

### D002: Constraint-Based Type Inference

**Decision:** Type inference uses a constraint-based approach with a dedicated `InferenceEngine` and `ConstraintSolver`, rather than Hindley-Milner or bi-directional inference.

**Rationale:**
- More explicit and debuggable than HM unification
- Easier to extend with I-specific features (Kinyarwanda keywords, special forms)
- Clean separation between constraint generation and solving
- Supports gradual typing (interaction with `any`/`unknown` types)

**Trade-off:** More verbose than HM for simple cases; requires explicit constraint ordering.

---

### D003: Bilingual Diagnostics (Kinyarwanda + English)

**Decision:** All diagnostic messages provide both Kinyarwanda (primary) and English (secondary) text.

**Rationale:**
- I is the world's first Kinyarwanda-first programming language
- Non-Kinyarwanda speakers can use English fallback
- Error codes (e.g., `TYP100_TYPE_MISMATCH`) are language-agnostic

**Trade-off:** 2x message maintenance; additional complexity in `Diagnostics.format_all()`.

---

### D004: Trait Checking as Deferred Pass

**Decision:** Trait/interface implementation checking is deferred to the end of type checking rather than checked inline during declaration visiting.

**Rationale:**
- Forward references: a type may implement a trait defined later in the file
- Circular reference handling is cleaner
- Summary error reporting (all missing methods at once)

**Trade-off:** Slightly more complex implementation; delayed error feedback.

---

### D005: Numeric Widening (int → float) Allowed

**Decision:** `int` values are assignable to `float` variables (widening), and `common_type(int, float) == float`. No implicit narrowing.

**Rationale:**
- Standard in most modern languages
- Prevents silent precision loss
- Common case: math operations involving mixed int/float

**Trade-off:** Loses strict type safety; can mask logic errors.

---

### D006: `any` Type as Universal Assignable

**Decision:** `any` is both assignable-to and assignable-from every type. `unknown` forces explicit type checks before use.

**Rationale:**
- `any` provides gradual typing escape hatch
- `unknown` provides type-safe dynamic typing
- Mirrors TypeScript's model which is familiar to many developers

**Trade-off:** `any` can subvert type safety if overused.

---

### D007: Generic Variance Tracking

**Decision:** Generic type parameters track variance (`invariant`, `covariant`, `contravariant`) per parameter, defaulting to `invariant`.

**Rationale:**
- Enables sound subtyping for generic containers
- `list<Dog>` is assignable to `list<Animal>` only if covariant
- Prevents runtime type errors from unsound variance

**Trade-off:** Complexity; most I code uses invariant generics by default.

---

### D008: Compile-Time Evaluation for Constants

**Decision:** A `CompileTimeEvaluator` handles constant folding and evaluation for `const` declarations, supporting arithmetic, string ops, comparisons, logical ops, ternary, and `typeof`.

**Rationale:**
- Enables compile-time constant propagation
- Required for `const` correctness checks
- `typeof` enables type-level programming patterns

**Trade-off:** Not a full compile-time function execution system (no macro-style evaluation).

---

### D009: Pipeline Integration as Optional Phase

**Decision:** The type checker runs as a separate pipeline phase after semantic analysis, with its own diagnostics collection.

**Rationale:**
- Clean separation of concerns: semantic analysis handles scope/resolution, type checker handles type validation
- Each phase can be disabled independently for debugging
- Error messages are categorized by phase

**Trade-off:** Two-pass architecture; type errors reported after semantic errors.

---

### D010: Checker Stores No Persistent State

**Decision:** Each `TypeChecker.check()` call creates fresh sub-components (clears context, diagnostics, inference). The `TypeRegistry` is reused for cross-file type definitions.

**Rationale:**
- Re-entrant: checker can be called multiple times safely
- No stale state between compilation units
- Registry persistence enables multi-file compilation

**Trade-off:** Clearing overhead per call.

---

## Earlier Sprints

See [ARCHITECTURE.md](./docs/specification/COMPILER_ARCHITECTURE.md) and individual sprint documentation for earlier decisions.
