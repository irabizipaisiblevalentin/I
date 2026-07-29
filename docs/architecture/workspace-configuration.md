# Workspace Configuration Architecture

## Overview

The Workspace Configuration component manages I project discovery, loading, and configuration. It provides a unified interface for accessing project settings, workspace members, and path resolution.

## Design Principles

1. **Immutable after loading**: Configuration cannot be modified after initialization
2. **Fail-fast**: Invalid configuration causes immediate error
3. **Backward compatible**: Supports older configuration formats
4. **Platform agnostic**: Works on Windows, macOS, and Linux

## Directory Structure

```
src/compiler/core/workspace/
├── __init__.py          # Public API
├── config.py            # Configuration data structures
├── loader.py            # Configuration file loading
├── resolver.py          # Path resolution
├── validator.py         # Configuration validation
├── workspace.py         # Workspace management
└── errors.py            # Workspace-specific errors
```

## Public Interfaces

### Workspace Class

```python
class Workspace:
    """Main workspace interface."""
    
    def __init__(self, root_path: Path):
        """Initialize workspace from root path."""
        
    @classmethod
    def load(cls, path: Path) -> 'Workspace':
        """Load workspace from path, searching for ilang.toml."""
        
    @property
    def root(self) -> Path:
        """Root directory of the workspace."""
        
    @property
    def config(self) -> Config:
        """Workspace configuration."""
        
    @property
    def members(self) -> List[Path]:
        """List of workspace member paths."""
        
    def resolve_path(self, path: str) -> Path:
        """Resolve path relative to workspace root."""
        
    def get_member(self, name: str) -> Optional[Path]:
        """Get workspace member by name."""
```

### Config Class

```python
@dataclass(frozen=True)
class Config:
    """Immutable workspace configuration."""
    
    name: str
    version: str
    edition: str
    authors: List[str]
    description: str
    license: str
    repository: Optional[str]
    dependencies: Dict[str, Dependency]
    dev_dependencies: Dict[str, Dependency]
    build_dependencies: Dict[str, Dependency]
    workspace: Optional[WorkspaceConfig]
    profile: ProfileConfig
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create config from dictionary."""
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
```

### Dependency Class

```python
@dataclass(frozen=True)
class Dependency:
    """Dependency specification."""
    
    name: str
    version: str
    source: DependencySource
    
    @classmethod
    def parse(cls, name: str, spec: Union[str, Dict[str, Any]]) -> 'Dependency':
        """Parse dependency from string or dictionary."""
```

## Internal Interfaces

### Loader

```python
class ConfigLoader:
    """Loads configuration from files."""
    
    def load(self, path: Path) -> Config:
        """Load configuration from path."""
        
    def _load_toml(self, path: Path) -> Dict[str, Any]:
        """Load TOML file."""
        
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file."""
        
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load JSON file."""
```

### Validator

```python
class ConfigValidator:
    """Validates configuration."""
    
    def validate(self, config: Config) -> List[ValidationError]:
        """Validate configuration, returning list of errors."""
        
    def _validate_name(self, name: str) -> Optional[ValidationError]:
        """Validate package name."""
        
    def _validate_version(self, version: str) -> Optional[ValidationError]:
        """Validate version string."""
        
    def _validate_dependencies(self, deps: Dict[str, Dependency]) -> List[ValidationError]:
        """Validate dependencies."""
```

### Resolver

```python
class PathResolver:
    """Resolves paths relative to workspace."""
    
    def __init__(self, root: Path):
        """Initialize with workspace root."""
        
    def resolve(self, path: str) -> Path:
        """Resolve path relative to workspace root."""
        
    def relative(self, path: Path) -> Path:
        """Make path relative to workspace root."""
        
    def canonical(self, path: Path) -> Path:
        """Get canonical path."""
```

## Configuration File Format

### ilang.toml

```toml
[package]
name = "my-app"
version = "0.1.0"
edition = "1.0"
authors = ["Developer <dev@example.com>"]
description = "My I application"
license = "MIT"
repository = "https://github.com/user/my-app"

[dependencies]
ilang-std = "1.0.0"
my-lib = { path = "../my-lib" }

[dev-dependencies]
ilang-test = "1.0.0"

[build-dependencies]
ilang-build = "1.0.0"

[workspace]
members = [
    "packages/core",
    "packages/web",
]

[profile.release]
opt-level = 3
lto = true

[profile.dev]
opt-level = 0
debug = true
```

## Error Codes

| Code | Description |
|------|-------------|
| W001 | Missing package name |
| W002 | Invalid package name |
| W003 | Missing package version |
| W004 | Invalid version format |
| W005 | Missing edition |
| W006 | Invalid edition |
| W007 | Invalid dependency specification |
| W008 | Circular dependency detected |
| W009 | Missing workspace member |
| W010 | Invalid workspace member path |

## Security Considerations

1. **Path traversal**: All paths are resolved and validated
2. **Symlink following**: Symlinks are followed but cycles are detected
3. **File permissions**: Configuration files must be readable
4. **Encoding**: Files must be valid UTF-8

## Performance Considerations

1. **Caching**: Configuration is cached after first load
2. **Lazy loading**: Workspace members are loaded on demand
3. **Minimal I/O**: Only required files are read

## Testing Strategy

1. **Unit tests**: Test each component in isolation
2. **Integration tests**: Test workspace loading end-to-end
3. **Edge cases**: Test invalid configurations
4. **Platform tests**: Test on Windows, macOS, Linux

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije*
