"""
Scope System for the I Programming Language

Lexical scoping with support for global, module, function, method, class,
conditional, loop, and nested scopes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

from .symbols import Symbol, SymbolKind, Visibility


class ScopeKind(Enum):
    """Classification of scope types."""
    GLOBAL = auto()
    MODULE = auto()
    FUNCTION = auto()
    METHOD = auto()
    CLASS = auto()
    STRUCT = auto()
    ENUM = auto()
    TRAIT = auto()
    INTERFACE = auto()
    CONDITIONAL = auto()
    LOOP = auto()
    BLOCK = auto()
    CATCH = auto()
    LAMBDA = auto()


@dataclass
class Scope:
    """
    A lexical scope for symbol resolution.

    Scopes form a tree rooted at the global scope. Each scope contains
    locally defined symbols and can look up parent scopes for enclosing names.
    """

    kind: ScopeKind
    parent: Optional[Scope] = None
    name: str = ""
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    children: List[Scope] = field(default_factory=list)
    depth: int = 0

    # Track shadowed symbols for diagnostics
    _shadows: Dict[str, Symbol] = field(default_factory=dict, repr=False)

    def define(self, symbol: Symbol) -> Optional[Symbol]:
        """
        Define a symbol in this scope.
        Returns the previously shadowed symbol if any, or None.
        """
        shadowed = None
        if symbol.name in self.symbols:
            shadowed = self.symbols[symbol.name]
            self._shadows[symbol.name] = shadowed
        self.symbols[symbol.name] = symbol
        return shadowed

    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Resolve a name starting from this scope, walking up to parents.
        """
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Resolve a name only in this exact scope (no parent walk)."""
        return self.symbols.get(name)

    def has(self, name: str) -> bool:
        """Check if name is defined in this scope or any parent."""
        return self.lookup(name) is not None

    def has_local(self, name: str) -> bool:
        """Check if name is defined in this exact scope."""
        return name in self.symbols

    def get_shadowed(self, name: str) -> Optional[Symbol]:
        """Get the symbol that was shadowed when name was defined."""
        return self._shadows.get(name)

    def all_symbols(self) -> Dict[str, Symbol]:
        """Get all symbols in this scope only."""
        return dict(self.symbols)

    def all_visible_symbols(self) -> Dict[str, Symbol]:
        """Get all symbols visible from this scope (including parents)."""
        result = {}
        current = self
        while current:
            for name, sym in current.symbols.items():
                if name not in result:
                    result[name] = sym
            current = current.parent
        return result

    def create_child(self, kind: ScopeKind, name: str = "") -> Scope:
        """Create a child scope."""
        child = Scope(
            kind=kind,
            parent=self,
            name=name,
            depth=self.depth + 1,
        )
        self.children.append(child)
        return child

    @property
    def is_global(self) -> bool:
        return self.kind == ScopeKind.GLOBAL

    @property
    def is_function_scope(self) -> bool:
        return self.kind in (ScopeKind.FUNCTION, ScopeKind.METHOD, ScopeKind.LAMBDA)

    @property
    def is_loop_scope(self) -> bool:
        return self.kind == ScopeKind.LOOP

    def enclosing_function(self) -> Optional[Scope]:
        """Find the nearest enclosing function/method scope."""
        current = self
        while current:
            if current.is_function_scope:
                return current
            current = current.parent
        return None

    def enclosing_loop(self) -> Optional[Scope]:
        """Find the nearest enclosing loop scope."""
        current = self
        while current:
            if current.is_loop_scope:
                return current
            current = current.parent
        return None

    def enclosing_class(self) -> Optional[Scope]:
        """Find the nearest enclosing class scope."""
        current = self
        while current:
            if current.kind == ScopeKind.CLASS:
                return current
            current = current.parent
        return None

    def enclosing_module(self) -> Optional[Scope]:
        """Find the nearest enclosing module scope."""
        current = self
        while current:
            if current.kind == ScopeKind.MODULE:
                return current
            current = current.parent
        return None

    def __repr__(self) -> str:
        return f"Scope({self.kind.name}, depth={self.depth}, name={self.name!r}, symbols={len(self.symbols)})"


class ScopeManager:
    """
    Manages the scope tree during semantic analysis.

    Provides push/pop operations for entering and leaving scopes,
    and convenience methods for common scope operations.
    """

    def __init__(self) -> None:
        self._global = Scope(ScopeKind.GLOBAL, name="<global>")
        self._current = self._global
        self._scope_count = 0

    @property
    def global_scope(self) -> Scope:
        return self._global

    @property
    def current(self) -> Scope:
        return self._current

    @property
    def current_depth(self) -> int:
        return self._current.depth

    def push(self, kind: ScopeKind, name: str = "") -> Scope:
        """Enter a new scope."""
        self._scope_count += 1
        child = self._current.create_child(kind, name)
        self._current = child
        return child

    def pop(self) -> Scope:
        """Leave the current scope, returning to parent."""
        if self._current.parent:
            self._current = self._current.parent
        return self._current

    def define(self, symbol: Symbol) -> Optional[Symbol]:
        """Define a symbol in the current scope."""
        return self._current.define(symbol)

    def lookup(self, name: str) -> Optional[Symbol]:
        """Resolve a name from the current scope."""
        return self._current.lookup(name)

    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Resolve a name only in the current scope."""
        return self._current.lookup_local(name)

    def has(self, name: str) -> bool:
        """Check if name is visible from current scope."""
        return self._current.has(name)

    def has_local(self, name: str) -> bool:
        """Check if name exists in current scope only."""
        return self._current.has_local(name)

    def get_enclosing_function(self) -> Optional[Scope]:
        """Get the nearest enclosing function scope."""
        return self._current.enclosing_function()

    def get_enclosing_loop(self) -> Optional[Scope]:
        """Get the nearest enclosing loop scope."""
        return self._current.enclosing_loop()

    def get_enclosing_class(self) -> Optional[Scope]:
        """Get the nearest enclosing class scope."""
        return self._current.enclosing_class()

    def get_enclosing_module(self) -> Optional[Scope]:
        """Get the nearest enclosing module scope."""
        return self._current.enclosing_module()

    @property
    def scope_count(self) -> int:
        return self._scope_count

    def all_visible_symbols(self) -> Dict[str, Symbol]:
        """Get all symbols visible from current scope."""
        return self._current.all_visible_symbols()
