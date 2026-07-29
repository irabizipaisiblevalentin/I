# Language Evolution

This document defines how the I Programming Language evolves over time while maintaining stability, backward compatibility, and cultural identity.

## Table of Contents

- [Evolution Principles](#evolution-principles)
- [Introducing New Syntax](#introducing-new-syntax)
- [Reserving Keywords](#reserving-keywords)
- [Stabilizing Features](#stabilizing-features)
- [Removing Obsolete Features](#removing-obsolete-features)
- [Preserving Compatibility](#preserving-compatibility)
- [Edition System](#edition-system)
- [Evolution Governance](#evolution-governance)

---

## Evolution Principles

### The Three Laws of Language Evolution

1. **Evolution Without Destruction**
   New versions must not break existing programs without explicit migration. The language grows forward, never backward.

2. **Complexity Budget**
   Every new feature must justify its complexity. The language has a limited budget for complexity. Spend it wisely.

3. **Cultural Continuity**
   The Kinyarwanda soul of the language must be preserved through all changes. Evolution enhances identity, never erodes it.

### Evolution Rules

| Rule | Description | Rationale |
|------|-------------|-----------|
| Add, don't remove | New versions add features | Backward compatibility |
| Deprecate before removing | 2-version deprecation | Migration time |
| Editions for major changes | Allow old code to compile | Smooth transitions |
| Keywords are sacred | Very high bar for new keywords | Language identity |
| Tooling must keep up | IDEs, formatters updated | Developer experience |

---

## Introducing New Syntax

### Syntax Addition Process

```
1. RFC Proposed
   ↓
2. Community Discussion (4-8 weeks)
   ↓
3. Core Team Review
   ↓
4. Accepted → Implementation
   ↓
5. Experimental (behind flag)
   ↓
6. Stabilized (next minor version)
```

### Syntax Categories

| Category | Example | Process | Timeline |
|----------|---------|---------|----------|
| Expression | New operators | RFC | 3-6 months |
| Statement | New control flow | RFC | 6-12 months |
| Declaration | New declaration forms | RFC + TSC | 6-18 months |
| Type | New type syntax | RFC + TSC | 12-24 months |
| Keyword | New keywords | RFC + supermajority | 12-36 months |

### Syntax Guidelines

1. **Consistency**
   New syntax must be consistent with existing syntax patterns.

```
# Good: Consistent pattern
shyiramo urubuga

# Variables
shyira x: int = 5
shyira y: string = "hello"

# Functions
umurimo add(a: int, b: int) -> int:
    subira a + b
iherezo

# New syntax should follow similar patterns
igiceri Person:
    umurimo greet(self) -> string:
        subira "Muraho"
    iherezo
iherezo
```

2. **Readability**
   New syntax should improve readability, not just reduce typing.

```
# Good: Improves readability
niba x > 5:
    print("big")
cyangwa niba x > 0:
    print("positive")
cyangwa:
    print("non-positive")

# Bad: Reduces readability but not typing
match x:
    > 5: print("big")
    > 0: print("positive")
    _: print("non-positive")
```

3. **Learnability**
   New syntax should be easy to learn for beginners.

```
# Good: Intuitive
async umurimo fetch_data() -> Result<Data>:
    shyira response = await http.get(url)
    subira json.decode(response.body)
iherezo

# Bad: Unintuitive
async fn fetch_data() -> Result<Data> {
    let response = http.get(url).await;
    return json.decode(response.body);
}
```

### Syntax Evolution Examples

#### Adding a New Operator

```
# v1.0: No pipe operator
shyiramo urubuga

shyira result = double(add_one(x))

# v2.0: Pipe operator added (RFC-0042)
shyiramo urubuga

shyira result = x |> add_one() |> double()
```

#### Adding New Control Flow

```
# v1.0: No unless statement
niba !condition:
    print("not condition")

# v2.0: unless statement added (RFC-0056)
niba !condition:
    print("not condition")
# or
tabetsa condition:
    print("not condition")
```

---

## Reserving Keywords

### Keyword Reservation Process

Keywords are the most sacred part of the language. Reserving a new keyword requires:

1. **Supermajority Vote** (3/4 TSC)
2. **Demonstrated Necessity** (cannot be a library)
3. **Cultural Sensitivity** (Kinyarwanda appropriateness)
4. **Long-term Commitment** (permanent reservation)

### Keyword Categories

| Category | Examples | Priority | Process |
|----------|----------|----------|---------|
| Control Flow | `niba`, `cyangwa`, `kora` | Critical | Never change |
| Declarations | `shyira`, `umurimo`, `igiceri` | Critical | Never change |
| Types | `int`, `string`, `bool` | High | Very rare changes |
| Operators | `na`, `cyangwa`, `si` | High | Very rare changes |
| Modifiers | `pub`, `priv`, `statik` | Medium | Rare changes |
| Future | (reserved) | Low | As needed |

### Keyword Reservation Rules

1. **Kinyarwanda Keywords**
   Must be actual Kinyarwanda words with clear meaning.
   Must be approved by Kinyarwanda language experts.

2. **English Aliases**
   Must be standard English programming terms.
   Must have clear Kinyarwanda equivalents.

3. **Reserved Words**
   Cannot be used as identifiers.
   Compiler provides clear error messages.

### Current Keyword Inventory

```
# Control Flow (sacred)
niba       # if
cyangwa    # else
kora       # do / begin
iherezo    # end
gukemura  # switch
hitamo    # case
subira    # return
gukomeza  # continue
guhagarika # break

# Declarations (sacred)
shyira     # let
umurimo   # function
igiceri   # struct
urwego    # class
ubwoko    # enum
uburumbarizo # trait / interface
ubukoro   # module
gusangiza # const
isoko     # import
gufata    # from
nuko      # as

# Types (high priority)
int        # integer
igice      # float
ibooli     # boolean
inyandiko  # string
ibibendo   # array
imapfa     # map
ubutumwa   # message (result)
amakosa    # error

# English Aliases
if         # alias for niba
else       # alias for cyangwa
do         # alias for kora
end        # alias for iherezo
return     # alias for subira
let        # alias for shyira
function   # alias for umurimo
struct     # alias for igiceri
class      # alias for urwego
enum       # alias for ubwoko
const      # alias for gusangiza
import     # alias for isoko
from       # alias for gufata
as         # alias for nuko
```

### Adding New Keywords

#### Kinyarwanda Keywords

1. **Language Expert Review**
   - Verify word is proper Kinyarwanda
   - Verify meaning is clear
   - Verify pronunciation is accessible

2. **RFC Process**
   - Demonstrate necessity
   - Show alternatives considered
   - Prove no library solution exists

3. **TSC Vote**
   - 3/4 supermajority required
   - Public vote with reasoning
   - 2-week voting period

4. **Implementation**
   - Add as experimental feature
   - Test with community
   - Stabilize after feedback

#### English Aliases

1. **Demonstrate Need**
   - Show international use case
   - Prove Kinyarwanda keyword is insufficient

2. **RFC Process**
   - Same as Kinyarwanda keywords
   - Must have Kinyarwanda equivalent

3. **TSC Vote**
   - 2/3 majority required
   - Less stringent than Kinyarwanda keywords

---

## Stabilizing Features

### Feature Stabilization Lifecycle

```
1. RFC Accepted
   ↓
2. Implementation (behind feature flag)
   ↓
3. Experimental (ilang --experimental)
   ↓
4. Beta (ilang --beta)
   ↓
5. Stable (default in next version)
```

### Stabilization Criteria

| Criterion | Experimental | Beta | Stable |
|-----------|--------------|------|--------|
| Implementation | Partial | Complete | Complete |
| Tests | Minimal | Comprehensive | Comprehensive |
| Documentation | Draft | Complete | Complete |
| Tooling | None | Basic | Full |
| Community Testing | Internal | Beta program | Public |
| Performance | Unknown | Benchmarked | Optimized |
| Migration Path | N/A | Documented | Documented |

### Stabilization Process

1. **Experimental Phase** (3-6 months)
   - Feature behind `--experimental` flag
   - Limited testing
   - API may change
   - Not for production

2. **Beta Phase** (3-6 months)
   - Feature behind `--beta` flag
   - Comprehensive testing
   - API is stable
   - For testing only

3. **Stable Phase**
   - Feature enabled by default
   - Full tooling support
   - Production ready
   - Backward compatibility guaranteed

### Stabilization Example

```
# v1.0: Pattern matching accepted (RFC-0035)
# Implementation begins

# v1.1: Pattern matching experimental
ilang build --experimental main.i
# Pattern matching available with --experimental flag

# v1.2: Pattern matching beta
ilang build --beta main.i
# Pattern matching available with --beta flag

# v2.0: Pattern matching stable
ilang build main.i
# Pattern matching available by default
```

---

## Removing Obsolete Features

### Removal Lifecycle

```
1. Feature Deprecated (v1.0)
   ↓
2. Deprecation Warning (v1.0-v1.9)
   ↓
3. Feature Removed (v2.0)
   ↓
4. Migration Guide Published (v2.0)
```

### Removal Criteria

A feature is removed if:

1. **Better Alternative Exists**
   The new feature is strictly better.

2. **Security Risk**
   The feature poses security risks.

3. **Maintenance Burden**
   The feature is too costly to maintain.

4. **Community Consensus**
   The community agrees to remove it.

### Removal Process

1. **Deprecation RFC**
   - Document why feature should be removed
   - Provide replacement/migration path
   - Set timeline (minimum 1 major version)

2. **Deprecation Warning**
   - Compiler warns when deprecated feature is used
   - Clear message about replacement
   - Documentation updated

3. **Removal**
   - Feature removed in next major version
   - Breaking change noted in changelog
   - Migration guide published

### Removal Timeline

| Version | Action |
|---------|--------|
| v1.0 | Feature deprecated |
| v1.1-v1.9 | Deprecation warnings |
| v2.0 | Feature removed |

### Migration Support

1. **Automatic Migration**
   - Compiler can automatically fix simple cases
   - `ilang migrate` command
   - Safe, reversible changes

2. **Manual Migration**
   - Complex cases require manual changes
   - Clear documentation
   - Example code provided

3. **Migration Tools**
   - `ilang migrate` for automatic fixes
   - IDE support for manual fixes
   - Community support for questions

---

## Preserving Compatibility

### Compatibility Guarantees

| Guarantee | Scope | Duration |
|-----------|-------|----------|
| Source compatibility | Same code compiles | 2 major versions |
| Binary compatibility | Same ABI | 3 major versions |
| API compatibility | Same APIs work | 2 major versions |
| Behavioral compatibility | Same semantics | 2 major versions |

### Compatibility Modes

```
# Compile with specific edition
ilang build --edition 2027 main.i
ilang build --edition 2029 main.i

# Or in ilang.toml
[compiler]
edition = "2027"
```

### Breaking Changes Policy

1. **Never Break Without Notice**
   - Minimum 1 major version warning
   - Clear migration guide
   - Tooling support

2. **Minimize Breaking Changes**
   - Prefer additions over changes
   - Deprecate before removing
   - Provide compatibility shims

3. **Document Breaking Changes**
   - Clear changelog entries
   - Migration guide for each change
   - Example code for before/after

### Example Compatibility Timeline

```
v1.0 (2027): Feature A introduced
v1.1 (2027): Feature A stable
v1.2 (2028): Feature A deprecated
v2.0 (2029): Feature A removed
v2.1 (2029): Feature A completely gone
```

---

## Edition System

### What are Editions?

Editions allow major language changes while maintaining backward compatibility. Each edition:
- Introduces new features
- May change default behaviors
- Can break compatibility
- Has a clear migration path

### Edition Timeline

| Edition | Version | Year | Major Changes |
|---------|---------|------|---------------|
| 2027 | v1.0 | 2027 | Initial release |
| 2029 | v3.0 | 2029 | Performance edition |
| 2031 | v5.0 | 2031 | AI edition |
| 2033 | v7.0 | 2033 | Systems edition |
| 2035 | v9.0 | 2035 | Scientific edition |
| 2037 | v11.0 | 2037 | Enterprise edition |

### Edition Features

#### Edition 2027 (v1.0)

- Core language features
- Standard library
- Basic tooling
- Kinyarwanda keywords

#### Edition 2029 (v3.0)

- Performance optimizations
- Advanced type system features
- Improved concurrency
- Memory management improvements

#### Edition 2031 (v5.0)

- AI framework integration
- Machine learning primitives
- Neural network support
- GPU acceleration

### Edition Migration

```
# Migrate to new edition
ilang migrate --edition 2029

# Check compatibility
ilang check --edition 2029 main.i

# Build with specific edition
ilang build --edition 2027 main.i
```

### Edition Compatibility

| From → To | Compatibility | Migration |
|-----------|---------------|-----------|
| 2027 → 2029 | Mostly compatible | Minor changes |
| 2027 → 2031 | Some incompatibilities | Moderate changes |
| 2027 → 2033 | Significant changes | Major migration |

---

## Evolution Governance

### Evolution Roles

| Role | Responsibility | Term |
|------|----------------|------|
| Language Designer | Overall vision | Permanent |
| TSC | Strategic decisions | 1 year |
| Core Team | Technical decisions | Ongoing |
| RFC Champions | Drive RFCs | Per RFC |

### Evolution Decisions

| Decision | Who Decides | Process |
|----------|-------------|---------|
| New features | TSC + Core | RFC |
| Breaking changes | TSC | RFC + supermajority |
| Keyword changes | TSC | RFC + 3/4 vote |
| Deprecation | Core | RFC |
| Emergency fixes | Core | Fast-track |

### Evolution Calendar

| Month | Activity |
|-------|----------|
| January | Feature freeze for next version |
| February | Stabilization period |
| March | Release candidate |
| April | Release |
| May-June | Community testing |
| July | RFC deadline for next version |
| August-September | Implementation |
| October-November | Testing |
| December | Release candidate |

### Evolution Transparency

All evolution decisions are public:
- RFCs on GitHub
- TSC meetings recorded
- Voting results public
- Changelogs comprehensive
- Migration guides clear

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
