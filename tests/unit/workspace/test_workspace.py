"""
Tests for workspace configuration.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from src.compiler.core.workspace import (
    Config,
    Dependency,
    DependencySource,
    ValidationError,
    Workspace,
)
from src.compiler.core.workspace.loader import ConfigLoader
from src.compiler.core.workspace.validator import ConfigValidator
from src.compiler.core.workspace.resolver import PathResolver


# ============================================================================
# Config Tests
# ============================================================================


class TestConfig:
    """Tests for Config dataclass."""
    
    def test_from_dict_minimal(self):
        """Test creating config from minimal dictionary."""
        data = {
            "package": {
                "name": "test-package",
                "version": "0.1.0",
            }
        }
        
        config = Config.from_dict(data)
        
        assert config.name == "test-package"
        assert config.version == "0.1.0"
        assert config.edition == "1.0"
        assert config.license == "MIT"
    
    def test_from_dict_full(self):
        """Test creating config from full dictionary."""
        data = {
            "package": {
                "name": "test-package",
                "version": "1.0.0",
                "edition": "2024",
                "authors": ["Developer <dev@example.com>"],
                "description": "A test package",
                "license": "Apache-2.0",
                "repository": "https://github.com/user/repo",
                "keywords": ["test", "example"],
                "categories": ["testing"],
            },
            "dependencies": {
                "ilang-std": "1.0.0",
                "my-lib": {"path": "../my-lib"},
            },
            "dev-dependencies": {
                "ilang-test": "1.0.0",
            },
            "workspace": {
                "members": ["packages/core", "packages/web"],
            },
        }
        
        config = Config.from_dict(data)
        
        assert config.name == "test-package"
        assert config.version == "1.0.0"
        assert config.edition == "2024"
        assert config.authors == ["Developer <dev@example.com>"]
        assert config.description == "A test package"
        assert config.license == "Apache-2.0"
        assert config.repository == "https://github.com/user/repo"
        assert config.keywords == ["test", "example"]
        assert config.categories == ["testing"]
        
        assert len(config.dependencies) == 2
        assert "ilang-std" in config.dependencies
        assert "my-lib" in config.dependencies
        
        assert len(config.dev_dependencies) == 1
        assert "ilang-test" in config.dev_dependencies
        
        assert config.workspace is not None
        assert config.workspace.members == ["packages/core", "packages/web"]
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(
            name="test-package",
            version="0.1.0",
            dependencies={
                "ilang-std": Dependency(name="ilang-std", version="1.0.0"),
            },
        )
        
        data = config.to_dict()
        
        assert data["package"]["name"] == "test-package"
        assert data["package"]["version"] == "0.1.0"
        assert data["dependencies"]["ilang-std"] == "1.0.0"
    
    def test_get_all_dependencies(self):
        """Test getting all dependencies."""
        config = Config(
            name="test",
            version="0.1.0",
            dependencies={
                "dep1": Dependency(name="dep1", version="1.0.0"),
            },
            dev_dependencies={
                "dep2": Dependency(name="dep2", version="2.0.0"),
            },
            build_dependencies={
                "dep3": Dependency(name="dep3", version="3.0.0"),
            },
        )
        
        all_deps = config.get_all_dependencies()
        
        assert len(all_deps) == 3
        assert "dep1" in all_deps
        assert "dep2" in all_deps
        assert "dep3" in all_deps


# ============================================================================
# Dependency Tests
# ============================================================================


class TestDependency:
    """Tests for Dependency dataclass."""
    
    def test_parse_string(self):
        """Test parsing dependency from string."""
        dep = Dependency.parse("ilang-std", "1.0.0")
        
        assert dep.name == "ilang-std"
        assert dep.version == "1.0.0"
        assert dep.source == DependencySource.REGISTRY
    
    def test_parse_dict_version(self):
        """Test parsing dependency from dict with version."""
        dep = Dependency.parse("ilang-std", {"version": "1.0.0"})
        
        assert dep.name == "ilang-std"
        assert dep.version == "1.0.0"
        assert dep.source == DependencySource.REGISTRY
    
    def test_parse_dict_path(self):
        """Test parsing dependency from dict with path."""
        dep = Dependency.parse("my-lib", {"path": "../my-lib"})
        
        assert dep.name == "my-lib"
        assert dep.source == DependencySource.PATH
        assert dep.path == Path("../my-lib")
    
    def test_parse_dict_git(self):
        """Test parsing dependency from dict with git."""
        dep = Dependency.parse(
            "my-lib",
            {"git": "https://github.com/user/repo", "rev": "main"},
        )
        
        assert dep.name == "my-lib"
        assert dep.source == DependencySource.GIT
        assert dep.git_url == "https://github.com/user/repo"
        assert dep.git_rev == "main"
    
    def test_parse_invalid(self):
        """Test parsing invalid dependency."""
        with pytest.raises(ValueError):
            Dependency.parse("dep", 123)


# ============================================================================
# Loader Tests
# ============================================================================


class TestConfigLoader:
    """Tests for ConfigLoader."""
    
    def test_find_config(self):
        """Test finding configuration file."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            
            # Create config file
            config_file = root / "ilang.toml"
            config_file.write_text('[package]\nname = "test"\nversion = "0.1.0"\n')
            
            loader = ConfigLoader()
            found = loader.find_config(root)
            
            assert found == config_file.resolve()
    
    def test_find_config_parent(self):
        """Test finding configuration file in parent directory."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            subdir = root / "src" / "compiler"
            subdir.mkdir(parents=True)
            
            # Create config file in root
            config_file = root / "ilang.toml"
            config_file.write_text('[package]\nname = "test"\nversion = "0.1.0"\n')
            
            loader = ConfigLoader()
            found = loader.find_config(subdir)
            
            assert found == config_file.resolve()
    
    def test_load_toml(self):
        """Test loading TOML configuration."""
        with TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "ilang.toml"
            config_file.write_text('[package]\nname = "test"\nversion = "0.1.0"\n')
            
            loader = ConfigLoader()
            config = loader.load(config_file)
            
            assert config.name == "test"
            assert config.version == "0.1.0"
    
    def test_load_not_found(self):
        """Test loading non-existent configuration."""
        from src.compiler.core.workspace.errors import ConfigNotFoundError
        
        loader = ConfigLoader()
        
        with pytest.raises(ConfigNotFoundError):
            loader.load(Path("/nonexistent/ilang.toml"))


# ============================================================================
# Validator Tests
# ============================================================================


class TestConfigValidator:
    """Tests for ConfigValidator."""
    
    def test_valid_config(self):
        """Test validating valid configuration."""
        config = Config(
            name="valid-package",
            version="1.0.0",
            edition="2024",
        )
        
        validator = ConfigValidator()
        errors = validator.validate(config)
        
        assert len(errors) == 0
    
    def test_invalid_name(self):
        """Test validating invalid package name."""
        config = Config(
            name="123-invalid",
            version="1.0.0",
        )
        
        validator = ConfigValidator()
        errors = validator.validate(config)
        
        assert len(errors) > 0
        assert any(e.code == "W002" for e in errors)
    
    def test_invalid_version(self):
        """Test validating invalid version."""
        config = Config(
            name="test",
            version="not-a-version",
        )
        
        validator = ConfigValidator()
        errors = validator.validate(config)
        
        assert len(errors) > 0
        assert any(e.code == "W004" for e in errors)
    
    def test_invalid_edition(self):
        """Test validating invalid edition."""
        config = Config(
            name="test",
            version="1.0.0",
            edition="invalid",
        )
        
        validator = ConfigValidator()
        errors = validator.validate(config)
        
        assert len(errors) > 0
        assert any(e.code == "W006" for e in errors)
    
    def test_missing_name(self):
        """Test validating missing package name."""
        config = Config(
            name="",
            version="1.0.0",
        )
        
        validator = ConfigValidator()
        errors = validator.validate(config)
        
        assert len(errors) > 0
        assert any(e.code == "W001" for e in errors)


# ============================================================================
# Resolver Tests
# ============================================================================


class TestPathResolver:
    """Tests for PathResolver."""
    
    def test_resolve_relative(self):
        """Test resolving relative path."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            resolver = PathResolver(root)
            
            resolved = resolver.resolve("src/main.i")
            
            assert resolved == (root / "src" / "main.i").resolve()
    
    def test_resolve_absolute(self):
        """Test resolving absolute path."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            resolver = PathResolver(root)
            
            abs_path = Path(tmpdir) / "other"
            resolved = resolver.resolve(str(abs_path))
            
            assert resolved == abs_path.resolve()
    
    def test_relative(self):
        """Test making path relative."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            resolver = PathResolver(root)
            
            abs_path = root / "src" / "main.i"
            relative = resolver.relative(abs_path)
            
            assert str(relative) == "src/main.i"
    
    def test_is_relative_to(self):
        """Test checking if path is relative to root."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            resolver = PathResolver(root)
            
            inside = root / "src" / "main.i"
            outside = Path("/other/path/file.i")
            
            assert resolver.is_relative_to(inside) is True
            assert resolver.is_relative_to(outside) is False


# ============================================================================
# Workspace Tests
# ============================================================================


class TestWorkspace:
    """Tests for Workspace."""
    
    def test_load(self):
        """Test loading workspace."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_file = root / "ilang.toml"
            config_file.write_text('[package]\nname = "test"\nversion = "0.1.0"\n')
            
            workspace = Workspace.load(root)
            
            assert workspace.root == root.resolve()
            assert workspace.config.name == "test"
    
    def test_load_from_config(self):
        """Test loading workspace from config path."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_file = root / "ilang.toml"
            config_file.write_text('[package]\nname = "test"\nversion = "0.1.0"\n')
            
            workspace = Workspace.load_from_config(config_file)
            
            assert workspace.root == root.resolve()
            assert workspace.config.name == "test"
    
    def test_resolve_path(self):
        """Test resolving path."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_file = root / "ilang.toml"
            config_file.write_text('[package]\nname = "test"\nversion = "0.1.0"\n')
            
            workspace = Workspace.load(root)
            resolved = workspace.resolve_path("src/main.i")
            
            assert resolved == (root / "src" / "main.i").resolve()
    
    def test_validate(self):
        """Test validating workspace."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_file = root / "ilang.toml"
            config_file.write_text('[package]\nname = "test"\nversion = "0.1.0"\n')
            
            workspace = Workspace.load(root)
            errors = workspace.validate()
            
            assert len(errors) == 0
    
    def test_is_valid(self):
        """Test checking if workspace is valid."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_file = root / "ilang.toml"
            config_file.write_text('[package]\nname = "test"\nversion = "0.1.0"\n')
            
            workspace = Workspace.load(root)
            
            assert workspace.is_valid() is True
