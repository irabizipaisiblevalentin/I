"""
Build profiles.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class OptimizationLevel(Enum):
    """Optimization levels."""
    
    NONE = 0
    BASIC = 1
    STANDARD = 2
    AGGRESSIVE = 3


class DebugLevel(Enum):
    """Debug information levels."""
    
    NONE = "none"
    LINE_TABLES = "line-tables"
    FULL = "full"


@dataclass(frozen=True)
class BuildProfile:
    """
    Build profile configuration.
    
    Defines optimization and debug settings for builds.
    """
    
    name: str
    optimization: OptimizationLevel = OptimizationLevel.NONE
    debug: DebugLevel = DebugLevel.FULL
    lto: bool = False
    codegen_units: Optional[int] = None
    panic: str = "unwind"
    incremental: bool = True
    
    @classmethod
    def dev(cls) -> BuildProfile:
        """Create development profile."""
        return cls(
            name="dev",
            optimization=OptimizationLevel.NONE,
            debug=DebugLevel.FULL,
            incremental=True,
        )
    
    @classmethod
    def release(cls) -> BuildProfile:
        """Create release profile."""
        return cls(
            name="release",
            optimization=OptimizationLevel.AGGRESSIVE,
            debug=DebugLevel.NONE,
            lto=True,
            codegen_units=1,
            incremental=False,
        )
    
    @classmethod
    def test(cls) -> BuildProfile:
        """Create test profile."""
        return cls(
            name="test",
            optimization=OptimizationLevel.BASIC,
            debug=DebugLevel.LINE_TABLES,
            incremental=True,
        )
    
    @classmethod
    def bench(cls) -> BuildProfile:
        """Create benchmark profile."""
        return cls(
            name="bench",
            optimization=OptimizationLevel.AGGRESSIVE,
            debug=DebugLevel.LINE_TABLES,
            incremental=False,
        )
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> BuildProfile:
        """Create from dictionary."""
        opt_level = data.get("opt-level", 0)
        debug = data.get("debug", True)
        
        # Map debug bool to DebugLevel
        if isinstance(debug, bool):
            debug_level = DebugLevel.FULL if debug else DebugLevel.NONE
        elif isinstance(debug, str):
            debug_level = DebugLevel(debug)
        else:
            debug_level = DebugLevel.FULL
        
        # Map opt-level to OptimizationLevel
        opt_map = {
            0: OptimizationLevel.NONE,
            1: OptimizationLevel.BASIC,
            2: OptimizationLevel.STANDARD,
            3: OptimizationLevel.AGGRESSIVE,
        }
        optimization = opt_map.get(opt_level, OptimizationLevel.NONE)
        
        return cls(
            name=name,
            optimization=optimization,
            debug=debug_level,
            lto=data.get("lto", False),
            codegen_units=data.get("codegen-units"),
            panic=data.get("panic", "unwind"),
            incremental=data.get("incremental", True),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "opt-level": self.optimization.value,
            "debug": self.debug.value,
            "lto": self.lto,
            "codegen-units": self.codegen_units,
            "panic": self.panic,
            "incremental": self.incremental,
        }
    
    @property
    def is_release(self) -> bool:
        """Check if this is a release profile."""
        return self.optimization == OptimizationLevel.AGGRESSIVE and not self.incremental
    
    @property
    def is_dev(self) -> bool:
        """Check if this is a development profile."""
        return self.optimization == OptimizationLevel.NONE and self.incremental
