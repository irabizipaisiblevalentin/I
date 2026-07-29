"""
Configuration types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path


class OptimizationLevel(Enum):
    """Optimization levels."""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"


class DebugLevel(Enum):
    """Debug information levels."""
    NONE = "none"
    LINE_NUMBERS = "line_numbers"
    FULL = "full"


class OutputFormat(Enum):
    """Output formats."""
    BYTECODE = "bytecode"
    WASM = "wasm"
    NATIVE = "native"


@dataclass
class FeatureFlags:
    """Feature flags."""
    experimental_generics: bool = False
    experimental_coroutines: bool = False
    experimental_pattern_matching: bool = True
    unsafe_mode: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FeatureFlags:
        """Create from dictionary."""
        return cls(
            experimental_generics=data.get("experimental_generics", False),
            experimental_coroutines=data.get("experimental_coroutines", False),
            experimental_pattern_matching=data.get("experimental_pattern_matching", True),
            unsafe_mode=data.get("unsafe_mode", False),
        )


@dataclass
class BuildConfig:
    """Build configuration."""
    optimization: OptimizationLevel = OptimizationLevel.STANDARD
    debug_info: DebugLevel = DebugLevel.LINE_NUMBERS
    output_format: OutputFormat = OutputFormat.BYTECODE
    target: str = "default"
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BuildConfig:
        """Create from dictionary."""
        return cls(
            optimization=OptimizationLevel(data.get("optimization", "standard")),
            debug_info=DebugLevel(data.get("debug_info", "line_numbers")),
            output_format=OutputFormat(data.get("output_format", "bytecode")),
            target=data.get("target", "default"),
        )


@dataclass
class CompilerConfig:
    """Complete compiler configuration."""
    name: str = "ilang"
    version: str = "0.1.0"
    root: Optional[Path] = None
    source_dirs: List[str] = field(default_factory=lambda: ["src"])
    output_dir: str = "build"
    stdlib_path: Optional[str] = None
    build: BuildConfig = field(default_factory=BuildConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    extra: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CompilerConfig:
        """Create from dictionary."""
        return cls(
            name=data.get("name", "ilang"),
            version=data.get("version", "0.1.0"),
            source_dirs=data.get("source_dirs", ["src"]),
            output_dir=data.get("output_dir", "build"),
            stdlib_path=data.get("stdlib_path"),
            build=BuildConfig.from_dict(data.get("build", {})),
            features=FeatureFlags.from_dict(data.get("features", {})),
            extra={k: v for k, v in data.items() if k not in {
                "name", "version", "source_dirs", "output_dir",
                "stdlib_path", "build", "features"
            }},
        )
