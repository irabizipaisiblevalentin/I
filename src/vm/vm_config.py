"""IVM configuration."""
from __future__ import annotations

from typing import Any


class VMConfig:
    """Configuration for a VM instance."""
    __slots__ = (
        "max_stack_depth", "max_call_depth", "max_globals",
        "heap_initial_size", "heap_growth_factor", "gc_threshold",
        "gc_generational", "gc_incremental", "gc_stw_limit_ms",
        "enable_debug", "enable_profiler", "enable_stats",
        "enable_bytecode_verification", "resource_limits",
    )

    def __init__(self, **kwargs: Any) -> None:
        self.max_stack_depth: int = kwargs.get("max_stack_depth", 1024)
        self.max_call_depth: int = kwargs.get("max_call_depth", 256)
        self.max_globals: int = kwargs.get("max_globals", 65536)
        self.heap_initial_size: int = kwargs.get("heap_initial_size", 1024 * 1024)
        self.heap_growth_factor: float = kwargs.get("heap_growth_factor", 1.5)
        self.gc_threshold: int = kwargs.get("gc_threshold", 1024)
        self.gc_generational: bool = kwargs.get("gc_generational", True)
        self.gc_incremental: bool = kwargs.get("gc_incremental", False)
        self.gc_stw_limit_ms: float = kwargs.get("gc_stw_limit_ms", 10.0)
        self.enable_debug: bool = kwargs.get("enable_debug", False)
        self.enable_profiler: bool = kwargs.get("enable_profiler", False)
        self.enable_stats: bool = kwargs.get("enable_stats", True)
        self.enable_bytecode_verification: bool = kwargs.get("enable_bytecode_verification", True)
        self.resource_limits: dict[str, Any] = kwargs.get("resource_limits", {})

    def with_debug(self) -> VMConfig:
        self.enable_debug = True
        return self

    def with_profiler(self) -> VMConfig:
        self.enable_profiler = True
        return self
