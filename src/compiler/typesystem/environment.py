"""
Type Environment for the I Programming Language

Maps variable names to their types in the current lexical scope.
Supports nested scopes, shadowing, and efficient lookup.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .types import Type, TypeKind, TYPE_ANY, TYPE_UNKNOWN, TypeVariable


# ══════════════════════════════════════════════════════════════════
# Environment Entry
# ══════════════════════════════════════════════════════════════════


@dataclass
class TypeEntry:
    """A single entry in the type environment."""

    name: str
    type: Type
    is_mutable: bool = True
    is_const: bool = False
    is_initialized: bool = True
    declaration_file: str = ""
    declaration_line: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ══════════════════════════════════════════════════════════════════
# Type Scope
# ══════════════════════════════════════════════════════════════════


@dataclass
class TypeScope:
    """
    A single lexical scope for type bindings.

    Each scope holds bindings for one block (function, class, loop, etc.)
    and has a pointer to its parent scope for name resolution.
    """

    name: str = ""
    parent: Optional[TypeScope] = None
    bindings: Dict[str, TypeEntry] = field(default_factory=dict)
    depth: int = 0

    def define(self, entry: TypeEntry) -> Optional[TypeEntry]:
        """
        Define a binding in this scope.
        Returns the previously shadowed entry, if any.
        """
        old = self.bindings.get(entry.name)
        self.bindings[entry.name] = entry
        return old

    def lookup(self, name: str) -> Optional[TypeEntry]:
        """
        Resolve a name starting from this scope, walking up to parents.
        """
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def lookup_local(self, name: str) -> Optional[TypeEntry]:
        """Resolve a name in this scope only (no parent walk)."""
        return self.bindings.get(name)

    def has(self, name: str) -> bool:
        """Check if name is defined in this scope or any parent."""
        return self.lookup(name) is not None

    def has_local(self, name: str) -> bool:
        """Check if name is defined in this scope only."""
        return name in self.bindings

    def get_type(self, name: str) -> Optional[Type]:
        """Get the type of a name."""
        entry = self.lookup(name)
        return entry.type if entry else None

    def create_child(self, name: str = "") -> TypeScope:
        """Create a child scope."""
        return TypeScope(
            name=name,
            parent=self,
            depth=self.depth + 1,
        )

    def all_names(self) -> Dict[str, Type]:
        """Get all names visible from this scope."""
        result: Dict[str, Type] = {}
        current: Optional[TypeScope] = self
        while current:
            for name, entry in current.bindings.items():
                if name not in result:
                    result[name] = entry.type
            current = current.parent
        return result

    def local_names(self) -> Dict[str, Type]:
        """Get names defined in this scope only."""
        return {name: entry.type for name, entry in self.bindings.items()}

    @property
    def is_global(self) -> bool:
        return self.depth == 0

    @property
    def is_function_scope(self) -> bool:
        return self.name.startswith("<fn:") or self.name.startswith("<method:")

    @property
    def is_class_scope(self) -> bool:
        return self.name.startswith("<class:")


# ══════════════════════════════════════════════════════════════════
# Type Environment
# ══════════════════════════════════════════════════════════════════


class TypeEnvironment:
    """
    Manages the type environment during type checking.

    Provides push/pop for entering/leaving scopes, and convenience
    methods for defining and looking up typed names.
    """

    def __init__(self) -> None:
        self._global = TypeScope(name="<global>", depth=0)
        self._current = self._global
        self._scope_count = 1
        self._history: List[TypeScope] = []

    @property
    def global_scope(self) -> TypeScope:
        return self._global

    @property
    def current_scope(self) -> TypeScope:
        return self._current

    @property
    def current_depth(self) -> int:
        return self._current.depth

    def push(self, name: str = "") -> TypeScope:
        """Enter a new scope."""
        self._scope_count += 1
        child = self._current.create_child(name)
        self._current = child
        return child

    def pop(self) -> TypeScope:
        """Leave the current scope."""
        if self._current.parent:
            self._current = self._current.parent
        return self._current

    def define(
        self,
        name: str,
        typ: Type,
        *,
        is_mutable: bool = True,
        is_const: bool = False,
        is_initialized: bool = True,
        file: str = "",
        line: int = 0,
    ) -> Optional[TypeEntry]:
        """
        Define a name with its type in the current scope.
        Returns the previously shadowed entry, if any.
        """
        entry = TypeEntry(
            name=name,
            type=typ,
            is_mutable=is_mutable,
            is_const=is_const,
            is_initialized=is_initialized,
            declaration_file=file,
            declaration_line=line,
        )
        return self._current.define(entry)

    def lookup(self, name: str) -> Optional[Type]:
        """Look up a name's type."""
        entry = self._current.lookup(name)
        return entry.type if entry else None

    def lookup_entry(self, name: str) -> Optional[TypeEntry]:
        """Look up the full entry for a name."""
        return self._current.lookup(name)

    def lookup_local(self, name: str) -> Optional[Type]:
        """Look up a name in the current scope only."""
        entry = self._current.lookup_local(name)
        return entry.type if entry else None

    def has(self, name: str) -> bool:
        """Check if a name is visible."""
        return self._current.has(name)

    def has_local(self, name: str) -> bool:
        """Check if a name is in the current scope only."""
        return self._current.has_local(name)

    def is_mutable(self, name: str) -> bool:
        """Check if a name refers to a mutable binding."""
        entry = self._current.lookup(name)
        return entry.is_mutable if entry else True

    def is_const(self, name: str) -> bool:
        """Check if a name is a constant."""
        entry = self._current.lookup(name)
        return entry.is_const if entry else False

    def update_type(self, name: str, new_type: Type) -> bool:
        """
        Update the type of an existing binding (for inference refinement).
        Returns True if the update succeeded.
        """
        entry = self._current.lookup(name)
        if entry is None:
            return False
        if entry.type.kind == TypeKind.UNKNOWN:
            entry.type = new_type
            return True
        if entry.type.kind == TypeKind.ANY:
            entry.type = new_type
            return True
        return False

    def get_all_bindings(self) -> Dict[str, Type]:
        """Get all bindings visible from the current scope."""
        return self._current.all_names()

    def get_local_bindings(self) -> Dict[str, Type]:
        """Get bindings in the current scope only."""
        return self._current.local_names()

    @property
    def binding_count(self) -> int:
        """Count all bindings visible from the current scope."""
        return len(self._current.all_names())

    @property
    def local_binding_count(self) -> int:
        """Count bindings in the current scope only."""
        return len(self._current.bindings)

    def get_all_names(self) -> List[str]:
        """Get all visible names as a list."""
        return list(self._current.all_names().keys())

    def has_name(self, name: str) -> bool:
        """Alias for has() - checks if a name is visible."""
        return self.has(name)

    def reset_to_global(self) -> None:
        """Reset to global scope only (for re-checking)."""
        self._global = TypeScope(name="<global>", depth=0)
        self._current = self._global
        self._scope_count = 1
        self._history.clear()

    def snapshot(self) -> Dict[str, Type]:
        """Take a snapshot of all current bindings (for diff-based checks)."""
        return self._current.all_names()

    def enter_function(self, name: str) -> TypeScope:
        """Enter a function scope."""
        return self.push(f"<fn:{name}>")

    def exit_function(self) -> TypeScope:
        """Exit a function scope."""
        return self.pop()

    def enter_class(self, name: str) -> TypeScope:
        """Enter a class scope."""
        return self.push(f"<class:{name}>")

    def exit_class(self) -> TypeScope:
        """Exit a class scope."""
        return self.pop()

    def enter_loop(self) -> TypeScope:
        """Enter a loop scope."""
        return self.push("<loop>")

    def exit_loop(self) -> TypeScope:
        """Exit a loop scope."""
        return self.pop()

    def enter_block(self, name: str = "") -> TypeScope:
        """Enter a block scope."""
        return self.push(f"<block:{name}>" if name else "<block>")

    def exit_block(self) -> TypeScope:
        """Exit a block scope."""
        return self.pop()

    @property
    def scope_count(self) -> int:
        """Total number of scopes created."""
        return self._scope_count

    def clear(self) -> None:
        """Reset the environment."""
        self._global = TypeScope(name="<global>", depth=0)
        self._current = self._global
        self._scope_count = 1
        self._history.clear()
