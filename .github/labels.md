# GitHub Labels

This document describes the GitHub labels used in the I Programming Language repository.

## Issue Labels

### Type Labels

| Label | Color | Description |
|-------|-------|-------------|
| `bug` | `d73a4a` | Reports of bugs or unexpected behavior |
| `enhancement` | `a2eeef` | Feature requests or enhancements |
| `documentation` | `0075ca` | Documentation improvements or issues |
| `question` | `cc317c` | Questions about the project |
| `performance` | `fbca04` | Performance-related issues |
| `security` | `e11d21` | Security vulnerabilities or concerns |

### Priority Labels

| Label | Color | Description |
|-------|-------|-------------|
| `critical` | `b60205` | Critical priority issues |
| `high` | `d93f0b` | High priority issues |
| `medium` | `fbca04` | Medium priority issues |
| `low` | `fef2c0` | Low priority issues |

### Component Labels

| Label | Color | Description |
|-------|-------|-------------|
| `compiler` | `0052cc` | Compiler-related issues |
| `runtime` | `0066cc` | Runtime-related issues |
| `vm` | `0077cc` | Virtual Machine-related issues |
| `stdlib` | `0088cc` | Standard Library-related issues |
| `tools` | `0099cc` | Tools-related issues |
| `ide` | `00aacc` | IDE-related issues |
| `frameworks` | `00bbcc` | Frameworks-related issues |
| `documentation` | `0075ca` | Documentation-related issues |

### Status Labels

| Label | Color | Description |
|-------|-------|-------------|
| `in-progress` | `84b6eb` | Currently being worked on |
| `review` | `5319e7` | Under review |
| `blocked` | `e11d21` | Blocked by another issue |
| `duplicate` | `cfd3d7` | Duplicate of another issue |
| `wontfix` | `ffffff` | Will not be fixed |
| `help wanted` | `008672` | Help wanted from community |
| `good first issue` | `7057ff` | Good for first-time contributors |

## Pull Request Labels

### Type Labels

| Label | Color | Description |
|-------|-------|-------------|
| `bug` | `d73a4a` | Bug fix |
| `feature` | `a2eeef` | New feature |
| `refactor` | `fbca04` | Code refactoring |
| `documentation` | `0075ca` | Documentation update |
| `test` | `bfd4f2` | Test addition or update |
| `performance` | `fbca04` | Performance improvement |
| `breaking` | `e11d21` | Breaking change |

### Review Labels

| Label | Color | Description |
|-------|-------|-------------|
| `needs-review` | `d93f0b` | Needs review |
| `approved` | `0e8a16` | Approved for merge |
| `changes-requested` | `e11d21` | Changes requested |
| `merged` | `6f42c1` | Merged |

## Label Usage Guidelines

### When to Use Labels

- **Always** label issues and pull requests
- Use **at least one** type label
- Use **at most one** priority label
- Use **relevant** component labels
- Use **status** labels as appropriate

### Label Combinations

**Bug Report Example**:
- `bug` + `compiler` + `high` + `in-progress`

**Feature Request Example**:
- `enhancement` + `stdlib` + `medium` + `help wanted`

**Pull Request Example**:
- `feature` + `frameworks` + `needs-review`

### Label Management

- **Add labels** when creating issues or PRs
- **Update labels** as status changes
- **Remove labels** when no longer applicable
- **Create new labels** only when necessary

## Automated Labels

Some labels are applied automatically by GitHub Actions:

- `size/XS` - Very small changes (< 10 lines)
- `size/S` - Small changes (10-50 lines)
- `size/M` - Medium changes (50-200 lines)
- `size/L` - Large changes (200-500 lines)
- `size/XL` - Very large changes (> 500 lines)

## Label Creation Process

To create a new label:

1. **Discuss** with the team
2. **Choose** an appropriate color
3. **Document** the label in this file
4. **Create** the label in GitHub
5. **Announce** the new label to contributors

## Label Cleanup

Periodic label cleanup:

- **Review** unused labels
- **Remove** obsolete labels
- **Merge** duplicate labels
- **Update** label descriptions

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
