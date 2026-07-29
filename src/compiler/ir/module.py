"""
IR Module

The top-level container for an IR program. Contains functions,
global variables, metadata, and type definitions.
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .values import GlobalVariable
from .types import IRType

if TYPE_CHECKING:
    from typing import Dict, Iterator, List
    from .function import IRFunction
    from .metadata import Metadata, MetadataCollection
    from .attributes import AttributeSet


# ══════════════════════════════════════════════════════════════════
# Function Map
# ══════════════════════════════════════════════════════════════════


class FunctionMap:
    """A dual-access collection: supports both dict-like and list-like access.

    Dict access: func_map["name"], func_map.values(), func_map.items()
    List access: for func in func_map, func_map[i], len(func_map)
    """
    __slots__ = ("_by_name", "_ordered")

    def __init__(self, functions: Optional[List] = None) -> None:
        object.__setattr__(self, "_by_name", {})
        object.__setattr__(self, "_ordered", [])
        if functions:
            for f in functions:
                self._add(f)

    def _add(self, func) -> None:
        self._by_name[func.name] = func
        self._ordered.append(func)

    def _remove(self, func) -> None:
        self._by_name.pop(func.name, None)
        if func in self._ordered:
            self._ordered.remove(func)

    # Dict-like access
    def __getitem__(self, key):
        """Support both name-based and index-based access."""
        if isinstance(key, int):
            return self._ordered[key]
        return self._by_name[key]

    def __contains__(self, name: str) -> bool:
        return name in self._by_name

    def get(self, name: str, default=None):
        return self._by_name.get(name, default)

    def values(self):
        return list(self._ordered)

    def keys(self):
        return list(self._by_name.keys())

    def items(self):
        return [(f.name, f) for f in self._ordered]

    # List-like access
    def __iter__(self) -> Iterator:
        return iter(self._ordered)

    def __len__(self) -> int:
        return len(self._ordered)

    def __bool__(self) -> bool:
        return len(self._ordered) > 0

    def __repr__(self) -> str:
        names = [f.name for f in self._ordered]
        return f"FunctionMap({names})"


# ══════════════════════════════════════════════════════════════════
# IR Module
# ══════════════════════════════════════════════════════════════════


class IRModule:
    """Top-level IR module — container for functions and globals."""
    __slots__ = ("_name", "_functions", "_globals", "_named_types",
                 "_metadata", "_target", "_data_layout")

    def __init__(self, name: str = "") -> None:
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_functions", [])
        object.__setattr__(self, "_globals", [])
        object.__setattr__(self, "_named_types", {})
        object.__setattr__(self, "_metadata", {})
        object.__setattr__(self, "_target", "")
        object.__setattr__(self, "_data_layout", "")

    # ── Properties ───────────────────────────────────────────────

    @property
    def name(self) -> str:
        return self._name

    @property
    def functions(self) -> FunctionMap:
        """Functions as a dual-access collection.

        Supports both dict-like access (by name) and list-like access (iteration).
        Examples:
            module.functions["my_func"]   # dict access
            module.functions.values()     # dict-like
            for f in module.functions:    # list iteration
            len(module.functions)         # count
        """
        return FunctionMap(self._functions)

    @property
    def globals(self) -> List[GlobalVariable]:
        return list(self._globals)

    @property
    def named_types(self) -> Dict[str, IRType]:
        return dict(self._named_types)

    @property
    def target(self) -> str:
        return self._target

    @target.setter
    def target(self, value: str) -> None:
        object.__setattr__(self, "_target", value)

    @property
    def data_layout(self) -> str:
        return self._data_layout

    @data_layout.setter
    def data_layout(self, value: str) -> None:
        object.__setattr__(self, "_data_layout", value)

    @property
    def function_count(self) -> int:
        return len(self._functions)

    @property
    def global_count(self) -> int:
        return len(self._globals)

    # ── Function Management ──────────────────────────────────────

    def add_function(self, func: IRFunction) -> None:
        """Add a function to the module."""
        if func not in self._functions:
            self._functions.append(func)
            func.module = self

    def get_function(self, name: str) -> Optional[IRFunction]:
        """Find a function by name."""
        for f in self._functions:
            if f.name == name:
                return f
        return None

    def remove_function(self, func: IRFunction) -> None:
        """Remove a function from the module."""
        if func in self._functions:
            self._functions.remove(func)
            func.module = None

    def has_function(self, name: str) -> bool:
        """Check if a function with the given name exists."""
        return any(f.name == name for f in self._functions)

    # ── Global Management ────────────────────────────────────────

    def add_global(self, global_var: GlobalVariable) -> None:
        """Add a global variable to the module."""
        if global_var not in self._globals:
            self._globals.append(global_var)

    def get_global(self, name: str) -> Optional[GlobalVariable]:
        """Find a global variable by name."""
        for g in self._globals:
            if g.name == name:
                return g
        return None

    def remove_global(self, global_var: GlobalVariable) -> None:
        """Remove a global variable."""
        if global_var in self._globals:
            self._globals.remove(global_var)

    # ── Type Management ──────────────────────────────────────────

    def register_type(self, name: str, typ: IRType) -> None:
        """Register a named type."""
        self._named_types[name] = typ

    def get_type(self, name: str) -> Optional[IRType]:
        """Look up a named type."""
        return self._named_types.get(name)

    # ── Metadata ─────────────────────────────────────────────────

    def set_metadata(self, key: str, value) -> None:
        """Set module-level metadata."""
        self._metadata[key] = value

    def get_metadata(self, key: str):
        """Get module-level metadata."""
        return self._metadata.get(key)

    # ── Queries ──────────────────────────────────────────────────

    @property
    def is_empty(self) -> bool:
        return (len(self._functions) == 0
                and len(self._globals) == 0)

    @property
    def instruction_count(self) -> int:
        return sum(f.instruction_count for f in self._functions)

    @property
    def block_count(self) -> int:
        return sum(f.block_count for f in self._functions)

    def all_instructions(self):
        """Iterate all instructions in the module."""
        for func in self._functions:
            for block in func:
                for inst in block:
                    yield inst

    def __repr__(self) -> str:
        return (f"module \"{self._name}\" "
                f"({self.function_count} funcs, {self.global_count} globals)")
