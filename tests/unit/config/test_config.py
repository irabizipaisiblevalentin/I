"""
Tests for Config Loader.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from src.compiler.core.config import (
    ConfigLoader,
    load_config,
    CompilerConfig,
    BuildConfig,
    FeatureFlags,
)
from src.compiler.core.config.schema import ConfigError, ConfigSchema


# ============================================================================
# Type Tests
# ============================================================================


class TestCompilerConfig:
    """Tests for CompilerConfig."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = CompilerConfig()
        
        assert config.name == "ilang"
        assert config.version == "0.1.0"
    
    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "name": "my_project",
            "version": "1.0.0",
            "build": {"optimization": "aggressive"},
        }
        
        config = CompilerConfig.from_dict(data)
        
        assert config.name == "my_project"
        assert config.version == "1.0.0"
        assert config.build.optimization.value == "aggressive"


class TestFeatureFlags:
    """Tests for FeatureFlags."""
    
    def test_default_flags(self):
        """Test default feature flags."""
        flags = FeatureFlags()
        
        assert flags.experimental_generics is False
        assert flags.experimental_pattern_matching is True
    
    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "experimental_generics": True,
            "unsafe_mode": True,
        }
        
        flags = FeatureFlags.from_dict(data)
        
        assert flags.experimental_generics is True
        assert flags.unsafe_mode is True


# ============================================================================
# Schema Tests
# ============================================================================


class TestConfigSchema:
    """Tests for ConfigSchema."""
    
    def test_valid_config(self):
        """Test validating valid config."""
        data = {"name": "test", "version": "1.0.0"}
        errors = ConfigSchema.validate(data)
        
        assert len(errors) == 0
    
    def test_invalid_type(self):
        """Test invalid field type."""
        data = {"name": 123}
        errors = ConfigSchema.validate(data)
        
        assert len(errors) > 0
    
    def test_valid_build(self):
        """Test valid build config."""
        data = {"optimization": "aggressive"}
        errors = ConfigSchema.validate_build(data)
        
        assert len(errors) == 0
    
    def test_invalid_optimization(self):
        """Test invalid optimization level."""
        data = {"optimization": "super_fast"}
        errors = ConfigSchema.validate_build(data)
        
        assert len(errors) > 0
    
    def test_valid_features(self):
        """Test valid feature flags."""
        data = {"experimental_generics": True}
        errors = ConfigSchema.validate_features(data)
        
        assert len(errors) == 0
    
    def test_unknown_feature(self):
        """Test unknown feature flag."""
        data = {"unknown_feature": True}
        errors = ConfigSchema.validate_features(data)
        
        assert len(errors) > 0
    
    def test_invalid_feature_type(self):
        """Test invalid feature flag type."""
        data = {"experimental_generics": "yes"}
        errors = ConfigSchema.validate_features(data)
        
        assert len(errors) > 0


# ============================================================================
# Loader Tests
# ============================================================================


class TestConfigLoader:
    """Tests for ConfigLoader."""
    
    def test_load_default(self):
        """Test loading default config."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            loader = ConfigLoader(root)
            
            config = loader.load()
            
            assert isinstance(config, CompilerConfig)
            assert config.root == root
    
    def test_load_toml(self):
        """Test loading TOML config."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_file = root / "ilang.toml"
            config_file.write_text('name = "test_project"\nversion = "1.0.0"')
            
            loader = ConfigLoader(root)
            config = loader.load()
            
            assert config.name == "test_project"
            assert config.version == "1.0.0"
    
    def test_load_json(self):
        """Test loading JSON config."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_file = root / "ilang.json"
            config_file.write_text('{"name": "test_project", "version": "1.0.0"}')
            
            loader = ConfigLoader(root)
            config = loader.load()
            
            assert config.name == "test_project"
            assert config.version == "1.0.0"
    
    def test_invalid_format(self):
        """Test invalid config format."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_file = root / "ilang.yaml"
            config_file.write_text("name: test")
            
            loader = ConfigLoader(root)
            
            with pytest.raises(ConfigError):
                loader.load_file(config_file)
