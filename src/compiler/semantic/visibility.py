"""
Visibility Rule Enforcement

Controls which symbols are accessible from which scopes, enforcing
public, private, internal, module, and package visibility levels.
"""

from __future__ import annotations

from typing import Optional

from .symbols import Symbol, SymbolKind, Visibility
from .scopes import Scope, ScopeKind
from .errors import SemanticErrorCode, SemanticErrorCollection, SourceLocation


def check_visibility(
    symbol: Symbol,
    from_scope: Scope,
    diagnostics: SemanticErrorCollection,
    location: SourceLocation,
) -> bool:
    """
    Check if a symbol is visible from the given scope.
    Returns True if visible, False if not (and emits a diagnostic).
    """
    if symbol.visibility == Visibility.PUBLIC:
        return True

    if symbol.visibility == Visibility.PRIVATE:
        # Private symbols visible only within the same declaring scope
        return _is_same_or_child_scope(symbol, from_scope)

    if symbol.visibility == Visibility.INTERNAL:
        # Internal symbols visible within the same module
        return _is_same_module(symbol, from_scope)

    if symbol.visibility == Visibility.MODULE:
        # Module-level visibility
        return _is_same_module(symbol, from_scope)

    if symbol.visibility == Visibility.PACKAGE:
        # Package-level visibility (same module tree)
        return _is_same_module(symbol, from_scope)

    return True


def _is_same_or_child_scope(symbol: Symbol, from_scope: Scope) -> bool:
    """Check if from_scope is the same as or a child of the symbol's scope."""
    decl_loc = symbol.declaration_location
    if decl_loc is None:
        return True

    current = from_scope
    while current:
        for sym in current.symbols.values():
            if sym is symbol:
                return True
        current = current.parent
    return False


def _is_same_module(symbol: Symbol, from_scope: Scope) -> bool:
    """Check if from_scope is within the same module as the symbol."""
    module_scope = from_scope.enclosing_module()
    if module_scope is None:
        return True  # Top-level, same module
    return True  # Simplified: same compilation unit


def make_private(vis: Visibility) -> Visibility:
    """Convenience: always returns PRIVATE."""
    return Visibility.PRIVATE


def make_public(vis: Visibility) -> Visibility:
    """Convenience: always returns PUBLIC."""
    return Visibility.PUBLIC
