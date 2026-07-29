"""
IR Context

The IRContext holds shared state for IR construction and manipulation:
- Type cache (deduplication)
- Name generation
- Module reference
- Source file tracking
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .types import IRType
from .module import IRModule

if TYPE_CHECKING:
    from typing import Dict, Set


# ══════════════════════════════════════════════════════════════════
# IR Context
# ══════════════════════════════════════════════════════════════════


class IRContext:
    """Shared context for IR construction and type deduplication."""
    __slots__ = ("_module", "_type_cache", "_name_counters",
                 "_current_file")

    def __init__(self, module: Optional[IRModule] = None) -> None:
        object.__setattr__(self, "_module", module or IRModule())
        object.__setattr__(self, "_type_cache", {})
        object.__setattr__(self, "_name_counters", {})
        object.__setattr__(self, "_current_file", "")

    # ── Properties ───────────────────────────────────────────────

    @property
    def module(self) -> IRModule:
        return self._module

    @property
    def current_file(self) -> str:
        return self._current_file

    @current_file.setter
    def current_file(self, path: str) -> None:
        object.__setattr__(self, "_current_file", path)

    # ── Type Deduplication ───────────────────────────────────────

    def intern_type(self, typ: IRType) -> IRType:
        """Get a canonical instance of a type (deduplication)."""
        key = repr(typ)
        if key in self._type_cache:
            return self._type_cache[key]
        self._type_cache[key] = typ
        return typ

    # ── Name Generation ─────────────────────────────────────────

    def unique_name(self, prefix: str = "tmp") -> str:
        """Generate a unique name with the given prefix."""
        count = self._name_counters.get(prefix, 0)
        self._name_counters[prefix] = count + 1
        return f"{prefix}{count}"

    def reset_names(self, prefix: str) -> None:
        """Reset the counter for a prefix."""
        self._name_counters[prefix] = 0

    # ── Metadata ─────────────────────────────────────────────────

    def set_source_file(self, filename: str) -> None:
        """Set the current source file for debug info."""
        object.__setattr__(self, "_current_file", filename)

    # ── Cleanup ──────────────────────────────────────────────────

    def clear(self) -> None:
        """Reset all state."""
        self._type_cache.clear()
        self._name_counters.clear()
        object.__setattr__(self, "_current_file", "")

    def __repr__(self) -> str:
        return f"IRContext(module={self._module.name}, types={len(self._type_cache)})"
