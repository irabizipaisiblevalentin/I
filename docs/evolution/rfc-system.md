# RFC System

This document defines the Request for Comments (RFC) process for the I Programming Language. The RFC process is the primary mechanism for proposing, discussing, and deciding significant changes to the language.

## Table of Contents

- [Overview](#overview)
- [RFC Lifecycle](#rfc-lifecycle)
- [RFC Template](#rfc-template)
- [Discussion Stages](#discussion-stages)
- [Review Stages](#review-stages)
- [Acceptance Criteria](#acceptance-criteria)
- [Deprecation Policy](#deprecation-policy)
- [Experimental Features](#experimental-features)
- [Nightly Features](#nightly-features)
- [Stable Releases](#stable-releases)
- [LTS Releases](#lts-releases)
- [Emergency Releases](#emergency-releases)

---

## Overview

### What is an RFC?

An RFC (Request for Comments) is a formal proposal for changing the I Programming Language or its ecosystem. RFCs are used for:

1. **Language changes**: New syntax, keywords, types, or semantics
2. **Standard library additions**: New modules or significant changes
3. **Tooling changes**: Compiler, package manager, or other tools
4. **Process changes**: Governance, contribution, or release processes
5. **Ecosystem changes**: Package registry, documentation, or community

### When is an RFC Required?

| Change Type | RFC Required? | Rationale |
|-------------|---------------|-----------|
| Bug fix | No | Already agreed-upon behavior |
| Minor feature | No | Below threshold |
| Major feature | Yes | Significant impact |
| Language change | Yes | Permanent change |
| Breaking change | Yes + TSC approval | Requires extra scrutiny |
| New keyword | Yes + supermajority | Reserved permanently |
| Deprecation | Yes | Removes functionality |
| Security fix | Emergency process | Time-critical |

### RFC Threshold

A change requires an RFC if it meets ANY of these criteria:
- Adds a new keyword
- Changes language semantics
- Adds a new type or type system feature
- Adds a new standard library module
- Changes the compiler pipeline
- Affects backward compatibility
- Has significant implementation complexity
- Affects multiple ecosystem components

---

## RFC Lifecycle

### Lifecycle Diagram

```
+----------+     +----------+     +----------+     +----------+
|  Draft   | --> |  Active  | --> |  Review  | --> | Accepted |
+----------+     +----------+     +----------+     +----------+
      |               |               |               |
      v               v               v               v
+----------+     +----------+     +----------+     +----------+
|  Closed  |     |  Postponed|    | Rejected |     | Implemented|
+----------+     +----------+     +----------+     +----------+
```

### Stage Descriptions

| Stage | Description | Duration |
|-------|-------------|----------|
| Draft | Initial proposal, author working | No limit |
| Active | Under community discussion | 4-8 weeks |
| Review | Core team review | 2-4 weeks |
| Accepted | Approved for implementation | - |
| Rejected | Not accepted (with reasons) | - |
| Postponed | Deferred to future version | - |
| Implemented | Feature shipped | - |
| Closed | Withdrawn by author | - |

---

## RFC Template

### Official Template

```markdown
# RFC-XXXX: [Title]

- **RFC ID**: XXXX
- **Author**: [Name]
- **Status**: Draft
- **Created**: YYYY-MM-DD
- **Updated**: YYYY-MM-DD
- **I-Version**: Target version
- **Category**: Language | Standard Library | Tooling | Process | Ecosystem

## Summary

One paragraph summary of the proposal.

## Motivation

### Problem Statement

What problem does this RFC solve?

### Current Workarounds

How do developers currently solve this problem?

### Why a Language Change?

Why can't this be solved with a library or tool?

## Detailed Design

### Syntax Changes

```i
# New syntax examples
shyiramo urubuga
# ...
```

### Semantic Changes

How does this change language behavior?

### Type System Impact

Does this affect the type system?

### Standard Library Changes

What new APIs are introduced?

### Implementation Details

How should this be implemented?

## Alternatives Considered

### Alternative 1: [Name]

Description of alternative.

**Pros:**
- Pro 1
- Pro 2

**Cons:**
- Con 1
- Con 2

### Alternative 2: [Name]

Description of alternative.

**Pros:**
- Pro 1
- Pro 2

**Cons:**
- Con 1
- Con 2

## Migration Path

How do existing programs migrate to the new feature?

### Automatic Migration

Can the compiler automatically migrate code?

### Manual Migration

What manual steps are required?

### Deprecation Timeline

When will the old behavior be deprecated?

## Impact Assessment

### Backward Compatibility

- [ ] No breaking changes
- [ ] Breaking changes (with migration path)
- [ ] Breaking changes (without migration path)

### Performance Impact

- [ ] No performance impact
- [ ] Positive performance impact
- [ ] Negative performance impact (acceptable)
- [ ] Negative performance impact (unacceptable)

### Tooling Impact

- [ ] No tooling changes required
- [ ] Minor tooling changes
- [ ] Major tooling changes

### Documentation Impact

- [ ] No documentation changes
- [ ] Minor documentation changes
- [ ] Major documentation changes

### Testing Impact

- [ ] No new tests required
- [ ] Minor test additions
- [ ] Major test additions

## Unresolved Questions

What questions need further discussion?

## Future Possibilities

What related features might be proposed in the future?

## References

Links to related RFCs, issues, or discussions.

## Drawbacks

What are the drawbacks of this proposal?

## Prior Art

How have other languages solved this problem?

## Learning Resources

What resources would help developers understand this feature?
```

---

## Discussion Stages

### Stage 1: Draft

**Duration:** No limit

**Activities:**
1. Author writes RFC using template
2. Author discusses informally (Discord, forums)
3. Author gathers initial feedback
4. Author iterates on the proposal

**Exit Criteria:**
- RFC follows template
- Core problem is clearly stated
- Design is reasonably complete
- Author is ready for public discussion

### Stage 2: Active

**Duration:** 4-8 weeks

**Activities:**
1. RFC submitted to GitHub
2. Community discusses on RFC issue
3. Author responds to feedback
4. Author iterates on the proposal
5. Regular discussion summaries posted

**Discussion Norms:**
- Be respectful and constructive
- Focus on technical merits
- Provide concrete examples
- Acknowledge trade-offs
- Avoid personal attacks

**Exit Criteria:**
- Discussion period complete (4-8 weeks)
- Major concerns addressed
- Community sentiment is clear
- Author is ready for review

### Stage 3: Review

**Duration:** 2-4 weeks

**Activities:**
1. Core team reviews RFC
2. Core team discusses internally
3. Core team requests clarifications if needed
4. Core team votes on acceptance

**Review Criteria:**
1. Does it align with language philosophy?
2. Does it pass the Seven Tests?
3. Is the design sound?
4. Is the migration path clear?
5. Is the implementation feasible?
6. Is there community support?

**Exit Criteria:**
- Core team vote complete
- Decision documented with reasoning
- Feedback provided to author

### Stage 4: Decision

**Decision Options:**

| Decision | Description | Next Steps |
|----------|-------------|------------|
| Accepted | Approved for implementation | Begin implementation |
| Rejected | Not accepted | Document reasons, close RFC |
| Postponed | Deferred to future | Add to roadmap for future version |
| Revision | Needs more work | Return to Draft/Active |

---

## Review Stages

### Core Team Review Process

1. **Initial Triage** (1 week)
   - RFC assigned to reviewer
   - Preliminary assessment
   - Identify major concerns

2. **Deep Review** (1-2 weeks)
   - Detailed technical review
   - Implementation feasibility
   - Impact assessment

3. **Discussion** (1 week)
   - Core team discussion
   - Address remaining concerns
   - Vote preparation

4. **Vote** (1 week)
   - Core team vote
   - Decision documented
   - Author notified

### Voting Rules

| RFC Type | Quorum | Threshold | Duration |
|----------|--------|-----------|----------|
| Minor feature | 5/10 core | Simple majority | 1 week |
| Major feature | 7/10 core | 2/3 majority | 1 week |
| Language change | 3/5 TSC | Simple majority | 2 weeks |
| Breaking change | 4/5 TSC | 2/3 majority | 2 weeks |
| New keyword | 4/5 TSC | 3/4 supermajority | 2 weeks |

### Review Checklist

- [ ] RFC follows template
- [ ] Problem is clearly stated
- [ ] Design is complete
- [ ] Alternatives are considered
- [ ] Migration path is clear
- [ ] Impact assessment is accurate
- [ ] Implementation plan exists
- [ ] Tests will be comprehensive
- [ ] Documentation will be updated
- [ ] Community support exists
- [ ] No unresolved critical questions

---

## Acceptance Criteria

### Must Have

1. **Clear Problem Statement**
   - What problem does this solve?
   - Why is this problem important?
   - Who benefits from this solution?

2. **Sound Design**
   - Design is consistent with language philosophy
   - Design passes the Seven Tests
   - Design is complete and unambiguous

3. **Migration Path**
   - Clear migration strategy for existing code
   - Automatic migration where possible
   - Deprecation timeline if removing existing feature

4. **Implementation Plan**
   - Clear implementation steps
   - Feasible within timeline
   - Resources identified

5. **Community Support**
   - Positive community sentiment
   - No major unresolved objections
   - Maintainer support

### Should Have

1. **Reference Implementation**
   - Working prototype
   - Performance benchmarks
   - Integration tests

2. **Documentation Plan**
   - Language specification changes
   - Tutorial updates
   - API documentation

3. **Tooling Plan**
   - IDE support
   - Formatter support
   - Linter support

### Nice to Have

1. **Real-World Examples**
   - Usage examples from real projects
   - Performance comparisons
   - Case studies

2. **Educational Materials**
   - Blog posts
   - Video tutorials
   - Workshop materials

---

## Deprecation Policy

### Deprecation Lifecycle

```
+----------+     +----------+     +----------+     +----------+
|  Active  | --> | Deprecated| --> |  Removed | --> |  Retired |
+----------+     +----------+     +----------+     +----------+
                  (1 major)        (2 major)        (3+ major)
```

### Deprecation Process

1. **Deprecation RFC**
   - Why feature should be deprecated
   - What replaces the feature
   - Migration path
   - Timeline

2. **Deprecation Warning**
   - Compiler warning when deprecated feature is used
   - Clear message about replacement
   - Documentation updated

3. **Removal**
   - Feature removed after deprecation period
   - Breaking change (requires major version)
   - Migration guide published

### Deprecation Timeline

| Version | Deprecation | Removal |
|---------|-------------|---------|
| v1.0 | Feature active | - |
| v1.1 | Feature deprecated | - |
| v2.0 | Feature deprecated | Feature removed |
| v2.1 | - | Feature removed |

### Deprecation Warnings

```
# Deprecation warning message
Warning: 'shyira' keyword is deprecated.
  Use 'shyira' instead of 'shyira'.
  This will be an error in v2.0.
  
  Example:
    Old: shyira x = 5
    New: shyira x = 5
```

### Breaking Changes Policy

1. **Minor Version (x.Y.0)**
   - No breaking changes
   - New features only
   - Bug fixes only

2. **Major Version (X.0.0)**
   - Breaking changes allowed
   - Deprecated features removed
   - Migration path required

3. **Epoch Version (X.0.0)**
   - Major language changes
   - Edition system support
   - Long-term migration support

---

## Experimental Features

### What are Experimental Features?

Experimental features are features that are:
- Not yet stable
- Under active development
- Subject to change
- Not recommended for production

### Enabling Experimental Features

```
# Enable experimental features
ilang build --experimental

# Or in ilang.toml
[compiler]
experimental = true
```

### Experimental Feature Categories

| Category | Description | Risk |
|----------|-------------|------|
| Syntax | New syntax | High |
| Type System | New type features | Medium |
| Standard Library | New APIs | Low |
| Compiler | Compiler optimizations | Low |
| Runtime | Runtime changes | Medium |

### Experimental Feature Lifecycle

```
1. RFC Accepted as Experimental
   ↓
2. Implemented behind feature flag
   ↓
3. Community testing and feedback
   ↓
4. RFC to stabilize
   ↓
5. Stabilized in next version
```

### Current Experimental Features

| Feature | Since | Stabilized In |
|---------|-------|---------------|
| (none yet) | - | - |

---

## Nightly Features

### What are Nightly Features?

Nightly features are features that are:
- Even more experimental than experimental
- Built from the latest development branch
- May break at any time
- For testing and development only

### Using Nightly

```
# Install nightly
ilang-install nightly

# Use nightly
ilang +nightly build
```

### Nightly vs Experimental

| Aspect | Experimental | Nightly |
|--------|--------------|---------|
| Stability | Moderate | Low |
| Feature flags | Yes | No |
| Breaking changes | Unlikely | Likely |
| Recommended use | Testing | Development only |

### Nightly to Stable

```
Nightly → Experimental → Stable
```

---

## Stable Releases

### Release Cadence

| Release Type | Frequency | Purpose |
|--------------|-----------|---------|
| Patch | As needed | Bug fixes, security |
| Minor | Every 3 months | New features |
| Major | Every 2 years | Breaking changes |

### Version Numbering

```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes
MINOR: New features (backward compatible)
PATCH: Bug fixes (backward compatible)
```

### Example

```
v1.0.0 → v1.0.1 (bug fix)
v1.0.1 → v1.1.0 (new feature)
v1.1.0 → v1.1.1 (bug fix)
v1.1.1 → v2.0.0 (breaking change)
```

### Release Process

1. **Release Candidate**
   - 2-week testing period
   - Community testing
   - Bug fixes only

2. **Release**
   - Final testing
   - Documentation updates
   - Announcement

3. **Post-Release**
   - Monitor for issues
   - Quick patches if needed
   - Community feedback

---

## LTS Releases

### What are LTS Releases?

LTS (Long-Term Support) releases receive:
- Security updates for 5 years
- Bug fixes for 3 years
- No new features (after initial release)

### LTS Schedule

| Version | Release | LTS Start | LTS End |
|---------|---------|-----------|---------|
| v1.0 | 2027 | 2027 | 2032 |
| v3.0 | 2029 | 2029 | 2034 |
| v5.0 | 2031 | 2031 | 2036 |

### LTS Policy

1. **LTS Designation**
   - Every odd major version becomes LTS
   - Designated at release
   - 5-year support commitment

2. **LTS Updates**
   - Security patches
   - Critical bug fixes
   - No new features
   - No breaking changes

3. **LTS Migration**
   - Migration guides for next LTS
   - Tooling support
   - Community support

### LTS vs Regular

| Aspect | Regular | LTS |
|--------|---------|-----|
| Feature updates | Yes | No |
| Security patches | Yes | Yes |
| Bug fixes | Yes | Yes (critical only) |
| Support duration | 6 months | 5 years |

---

## Emergency Releases

### What are Emergency Releases?

Emergency releases address:
- Critical security vulnerabilities
- Data loss bugs
- Corruption bugs
- Complete functionality loss

### Emergency Release Process

1. **Vulnerability Report** (0-24 hours)
   - Report received
   - Triage and assessment
   - Core team notified

2. **Fix Development** (24-72 hours)
   - Fix developed
   - Tests written
   - Review completed

3. **Release** (72-96 hours)
   - Release candidate
   - Testing
   - Release

4. **Announcement** (96+ hours)
   - Public disclosure
   - Advisory published
   - Users notified

### Emergency Release Versioning

```
v1.0.0 → v1.0.1 (emergency)
v1.0.1 → v1.0.2 (emergency)
```

### Security Advisory Format

```markdown
# Security Advisory: I-XXXX

## Summary
Brief description of the vulnerability.

## Affected Versions
- I 1.0.0
- I 1.0.1

## Not Affected
- I 1.1.0
- I 2.0.0

## Impact
Description of potential impact.

## Solution
Upgrade to I 1.0.2 or later.

## Workaround
Temporary workaround if available.

## References
- CVE: CVE-XXXX-XXXX
- Issue: #XXXX
- Commit: XXXXXXXX
```

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
