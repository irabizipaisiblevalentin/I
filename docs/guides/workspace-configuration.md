# Workspace Configuration

## Overview

The Workspace Configuration component manages I project discovery, loading, and configuration. It provides a unified interface for accessing project settings, workspace members, and path resolution.

## Quick Start

### Loading a Workspace

```python
from pathlib import Path
from src.compiler.core.workspace import Workspace

# Load from current directory
workspace = Workspace.load(Path("."))

# Access configuration
print(workspace.config.name)  # "my-app"
print(workspace.config.version)  # "0.1.0"

# Resolve paths
main_file = workspace.resolve_path("src/main.i")
```

### Creating Configuration

Create an `ilang.toml` file in your project root:

```toml
[package]
name = "my-app"
version = "0.1.0"
edition = "2024"
authors = ["Developer <dev@example.com>"]
description = "My I application"
license = "MIT"

[dependencies]
ilang-std = "1.0.0"

[dev-dependencies]
ilang-test = "1.0.0"
```

## API Reference

### Workspace

```python
class Workspace:
    """Main workspace interface."""
    
    @classmethod
    def load(cls, path: Path) -> Workspace:
        """Load workspace from path, searching for ilang.toml."""
        
    @classmethod
    def load_from_config(cls, config_path: Path) -> Workspace:
        """Load workspace from configuration file path."""
        
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
        
    def validate(self) -> List[ValidationError]:
        """Validate workspace configuration."""
        
    def is_valid(self) -> bool:
        """Check if workspace configuration is valid."""
```

### Config

```python
@dataclass(frozen=True)
class Config:
    """Immutable workspace configuration."""
    
    name: str
    version: str
    edition: str = "1.0"
    authors: List[str] = field(default_factory=list)
    description: str = ""
    license: str = "MIT"
    repository: Optional[str] = None
    dependencies: Dict[str, Dependency] = field(default_factory=dict)
    dev_dependencies: Dict[str, Dependency] = field(default_factory=dict)
    build_dependencies: Dict[str, Dependency] = field(default_factory=dict)
    workspace: Optional[WorkspaceConfig] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Config:
        """Create config from dictionary."""
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        
    def get_all_dependencies(self) -> Dict[str, Dependency]:
        """Get all dependencies (main + dev + build)."""
```

### Dependency

```python
@dataclass(frozen=True)
class Dependency:
    """Dependency specification."""
    
    name: str
    version: str
    source: DependencySource = DependencySource.REGISTRY
    path: Optional[Path] = None
    git_url: Optional[str] = None
    git_rev: Optional[str] = None
    
    @classmethod
    def parse(cls, name: str, spec: Union[str, Dict[str, Any]]) -> Dependency:
        """Parse dependency from string or dictionary."""
```

## Configuration File Format

### ilang.toml

```toml
[package]
name = "my-app"
version = "0.1.0"
edition = "2024"
authors = ["Developer <dev@example.com>"]
description = "My I application"
license = "MIT"
repository = "https://github.com/user/my-app"
keywords = ["example", "tutorial"]
categories = ["command-line"]

[dependencies]
ilang-std = "1.0.0"
my-lib = { path = "../my-lib" }
some-lib = { git = "https://github.com/user/some-lib", rev = "main" }

[dev-dependencies]
ilang-test = "1.0.0"

[build-dependencies]
ilang-build = "0.1.0"

[workspace]
members = [
    "packages/core",
    "packages/web",
]

[profile.dev]
opt-level = 0
debug = true

[profile.release]
opt-level = 3
lto = true
```

## Error Codes

| Code | Description | Suggestion |
|------|-------------|------------|
| W001 | Package name is required | Add a name field to the [package] section |
| W002 | Invalid package name | Package names must start with a letter and contain only letters, numbers, hyphens, and underscores |
| W003 | Package version is required | Add a version field to the [package] section |
| W004 | Invalid version format | Version must follow semantic versioning (e.g., 1.0.0) |
| W005 | Edition is required | Add an edition field to the [package] section |
| W006 | Invalid edition | Valid editions are: 1.0, 2024, 2025, 2026 |
| W007 | Invalid dependency specification | Check dependency name and version format |
| W009 | Path dependency not found | Ensure the path exists and is correct |
| W010 | Empty workspace member path | Provide a valid path for workspace member |
| W011 | Uncommon license identifier | Consider using a standard SPDX license identifier |

## Examples

### Basic Project

```toml
[package]
name = "hello-world"
version = "0.1.0"
```

### Full Project

```toml
[package]
name = "my-app"
version = "1.0.0"
edition = "2024"
authors = ["Alice <alice@example.com>", "Bob <bob@example.com>"]
description = "A complete I application"
license = "MIT"
repository = "https://github.com/example/my-app"
keywords = ["example", "tutorial"]
categories = ["command-line", "learning"]

[dependencies]
ilang-std = "1.0.0"
ilang-async = "0.2.0"

[dev-dependencies]
ilang-test = "1.0.0"

[workspace]
members = ["packages/core", "packages/cli"]
```

### Workspace Project

```toml
[package]
name = "my-workspace"
version = "0.1.0"

[workspace]
members = [
    "packages/core",
    "packages/web",
    "packages/cli",
]
```

## Security Considerations

1. **Path traversal**: All paths are resolved and validated
2. **Symlink following**: Symlinks are followed but cycles are detected
3. **File permissions**: Configuration files must be readable
4. **Encoding**: Files must be valid UTF-8

## Performance Considerations

1. **Caching**: Configuration is cached after first load
2. **Lazy loading**: Workspace members are loaded on demand
3. **Minimal I/O**: Only required files are read

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije*
