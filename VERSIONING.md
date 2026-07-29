# Versioning

This document describes the versioning policy for the I Programming Language.

## Table of Contents

- [Semantic Versioning](#semantic-versioning)
- [Version Format](#version-format)
- [Release Types](#release-types)
- [Version Lifecycle](#version-lifecycle)
- [Compatibility](#compatibility)
- [Deprecation Policy](#deprecation-policy)
- [Version Numbers in Code](#version-numbers-in-code)

## Semantic Versioning

The I Programming Language follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

### Format

```
MAJOR.MINOR.PATCH
```

### Version Components

- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible functionality additions
- **PATCH**: Backwards-compatible bug fixes

### Examples

- `1.0.0` - Initial stable release
- `1.1.0` - Added new features (backwards-compatible)
- `1.1.1` - Bug fix (backwards-compatible)
- `2.0.0` - Breaking changes

## Version Format

### Standard Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

### Components

- **MAJOR**: Major version (non-negative integer)
- **MINOR**: Minor version (non-negative integer)
- **PATCH**: Patch version (non-negative integer)
- **PRERELEASE**: Pre-release identifier (optional)
- **BUILD**: Build metadata (optional)

### Pre-release Identifiers

Pre-release versions use dot-separated identifiers:

- `alpha.1` - Alpha release
- `alpha.2` - Second alpha release
- `beta.1` - Beta release
- `rc.1` - Release candidate

### Examples

```
1.0.0-alpha.1
1.0.0-beta.1
1.0.0-rc.1
1.0.0
1.0.0+build.123
```

## Release Types

### Major Release

**When to use**:
- Breaking API changes
- Removal of deprecated features
- Major architectural changes

**Impact**:
- Requires migration
- May require code changes
- Significant new features

**Example**: `1.0.0` → `2.0.0`

### Minor Release

**When to use**:
- New backwards-compatible features
- New APIs
- New functionality

**Impact**:
- No breaking changes
- Optional to upgrade
- New features available

**Example**: `1.0.0` → `1.1.0`

### Patch Release

**When to use**:
- Bug fixes
- Security fixes
- Performance improvements

**Impact**:
- No breaking changes
- Recommended to upgrade
- Fixes issues

**Example**: `1.0.0` → `1.0.1`

### Pre-release

**When to use**:
- Alpha releases
- Beta releases
- Release candidates

**Impact**:
- Not production-ready
- May have bugs
- For testing only

**Example**: `1.0.0-alpha.1`

## Version Lifecycle

### Development Phase

**Version**: `0.x.x`

**Characteristics**:
- No stability guarantees
- Frequent breaking changes
- Rapid iteration
- Not production-ready

**Example**: `0.1.0`, `0.2.0`, `0.3.0`

### Stable Phase

**Version**: `1.x.x` and above

**Characteristics**:
- Stability guarantees
- Backwards compatibility
- Regular releases
- Production-ready

**Example**: `1.0.0`, `1.1.0`, `1.2.0`

### Long-term Support (LTS)

**Version**: Selected major versions

**Characteristics**:
- Extended support period
- Security updates only
- Critical bug fixes
- 3-year support

**Example**: `1.0.0` (LTS), `2.0.0` (LTS)

## Compatibility

### Backwards Compatibility

**Maintained for**:
- Minor versions (1.x → 1.y)
- Patch versions (1.x.y → 1.x.z)

**Broken by**:
- Major versions (1.x → 2.x)

### API Compatibility

**Breaking changes include**:
- Removed APIs
- Changed API signatures
- Changed behavior
- Changed semantics

### ABI Compatibility

**Breaking changes include**:
- Changed data structures
- Changed calling conventions
- Changed binary format

## Deprecation Policy

### Deprecation Process

1. **Announce**: Announce deprecation in release notes
2. **Document**: Document deprecation in API docs
3. **Warn**: Emit warnings when deprecated API is used
4. **Maintain**: Keep deprecated API for 2 major versions
5. **Remove**: Remove deprecated API

### Deprecation Timeline

```
Version 1.0.0: API introduced
Version 1.1.0: API deprecated (warning)
Version 2.0.0: API removed
```

### Deprecation Warning

```python
@deprecated("Use new_function instead (will be removed in v2.0)")
def old_function():
    """Deprecated: Use new_function instead."""
    emit_warning("old_function is deprecated")
    return new_function()
```

## Version Numbers in Code

### Version Constant

```python
# compiler/__init__.py
__version__ = "1.0.0"
__author__ = "Irabizi Paisible Valentin"
```

### Version Check

```python
def check_version(required: str) -> bool:
    """Check if current version meets requirement."""
    from packaging import version
    current = __version__
    return version.parse(current) >= version.parse(required)
```

### Version in CLI

```bash
$ i --version
I Programming Language Compiler v1.0.0
```

## Release Schedule

### Regular Releases

- **Minor releases**: Every 3 months
- **Patch releases**: As needed
- **Major releases**: Every 12-18 months

### Security Releases

- **Critical**: Within 48 hours
- **High**: Within 1 week
- **Medium**: Within 1 month
- **Low**: Next regular release

## Version Bumping

### Automated Bumping

Use tools to automate version bumping:

```bash
# Bump patch version
bumpversion patch

# Bump minor version
bumpversion minor

# Bump major version
bumpversion major
```

### Manual Bumping

Update version in:
- `compiler/__init__.py`
- `pyproject.toml`
- `README.md`
- `CHANGELOG.md`

## Version Tags

### Git Tags

Tag each release:

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Tag Format

```
vMAJOR.MINOR.PATCH
```

### Pre-release Tags

```
v1.0.0-alpha.1
v1.0.0-beta.1
v1.0.0-rc.1
```

## Version Verification

### Verification Steps

1. **Check version**: Verify version number
2. **Check changelog**: Verify changelog updated
3. **Check compatibility**: Verify compatibility
4. **Check tests**: Verify all tests pass
5. **Check documentation**: Verify documentation updated

### Verification Script

```python
def verify_release(version: str):
    """Verify release is ready."""
    # Check version format
    assert re.match(r'^\d+\.\d+\.\d+', version)
    
    # Check changelog
    assert version in changelog
    
    # Check tests
    assert all_tests_pass()
    
    # Check documentation
    assert version_in_docs(version)
```

## Version Communication

### Release Notes

Include in release notes:
- Version number
- Release date
- New features
- Bug fixes
- Breaking changes
- Migration guide

### Announcement Channels

- GitHub releases
- Mailing list
- Blog post
- Social media
- Community forums

## Version History

### Current Version

**Version**: 0.1.0
**Status**: Development
**Release Date**: 2026-07-22

### Previous Versions

None (initial release)

### Future Versions

See [ROADMAP.md](ROADMAP.md) for planned releases.

## Version Support

### Supported Versions

| Version | Support Until | Status |
|---------|---------------|--------|
| 0.1.x   | TBD           | Development |
| 1.0.x   | TBD           | Planned   |

### Unsupported Versions

None (initial release)

## Version Policy

### Principles

1. **Stability**: Maintain stability for stable versions
2. **Predictability**: Follow predictable release schedule
3. **Communication**: Communicate changes clearly
4. **Migration**: Provide migration guides
5. **Support**: Support versions for reasonable period

### Exceptions

Exceptions may be made for:
- Security vulnerabilities
- Critical bugs
- Legal requirements

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
