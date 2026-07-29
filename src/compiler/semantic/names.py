"""
Name Resolution Engine

Resolves variable names, function names, method names, class names,
import names, namespace names, framework modules, and built-in identifiers.
"""

from __future__ import annotations

from typing import Optional

from .symbols import Symbol, SymbolKind, TypeDescriptor, SymbolType
from .scopes import Scope, ScopeKind
from .errors import SemanticErrorCode, SemanticErrorCollection, SourceLocation


def resolve_name(
    name: str,
    scope: Scope,
    diagnostics: SemanticErrorCollection,
    location: SourceLocation,
    expected_kind: Optional[SymbolKind] = None,
) -> Optional[Symbol]:
    """
    Resolve a name from the given scope, walking up the scope chain.
    Emits a diagnostic if the name is not found.
    """
    symbol = scope.lookup(name)
    if symbol is None:
        diagnostics.error(
            SemanticErrorCode.SEM200_UNDEFINED_VARIABLE,
            location, name,
        )
        return None
    return symbol


def resolve_function(
    name: str,
    scope: Scope,
    diagnostics: SemanticErrorCollection,
    location: SourceLocation,
) -> Optional[Symbol]:
    """Resolve a function name."""
    symbol = scope.lookup(name)
    if symbol is None:
        diagnostics.error(
            SemanticErrorCode.SEM201_UNDEFINED_FUNCTION,
            location, name,
        )
        return None
    if symbol.kind not in (SymbolKind.FUNCTION, SymbolKind.BUILTIN_FUNCTION, SymbolKind.METHOD):
        diagnostics.error(
            SemanticErrorCode.SEM301_NOT_CALLABLE,
            location, name,
        )
        return None
    return symbol


def resolve_class(
    name: str,
    scope: Scope,
    diagnostics: SemanticErrorCollection,
    location: SourceLocation,
) -> Optional[Symbol]:
    """Resolve a class name."""
    symbol = scope.lookup(name)
    if symbol is None:
        diagnostics.error(
            SemanticErrorCode.SEM202_UNDEFINED_CLASS,
            location, name,
        )
        return None
    return symbol


def resolve_type(
    name: str,
    scope: Scope,
    diagnostics: SemanticErrorCollection,
    location: SourceLocation,
) -> Optional[TypeDescriptor]:
    """Resolve a type name to its TypeDescriptor."""
    symbol = scope.lookup(name)
    if symbol is None:
        diagnostics.error(
            SemanticErrorCode.SEM204_UNDEFINED_TYPE,
            location, name,
        )
        return None
    if symbol.type_descriptor:
        return symbol.type_descriptor
    return TypeDescriptor(SymbolType.UNKNOWN, name)


def resolve_method(
    class_name: str,
    method_name: str,
    scope: Scope,
    diagnostics: SemanticErrorCollection,
    location: SourceLocation,
) -> Optional[Symbol]:
    """Resolve a method on a class."""
    class_sym = scope.lookup(class_name)
    if class_sym is None:
        diagnostics.error(
            SemanticErrorCode.SEM202_UNDEFINED_CLASS,
            location, class_name,
        )
        return None

    method = class_sym.members.get(method_name)
    if method is None:
        diagnostics.error(
            SemanticErrorCode.SEM207_UNDEFINED_METHOD,
            location, method_name, class_name,
            related_symbols=[class_name],
        )
        return None
    return method


def is_callable(symbol: Symbol) -> bool:
    """Check if a symbol represents a callable entity."""
    return symbol.kind in (
        SymbolKind.FUNCTION, SymbolKind.BUILTIN_FUNCTION,
        SymbolKind.METHOD,
    )


def is_type_symbol(symbol: Symbol) -> bool:
    """Check if a symbol represents a type."""
    return symbol.kind in (
        SymbolKind.CLASS, SymbolKind.STRUCT, SymbolKind.ENUM,
        SymbolKind.TRAIT, SymbolKind.INTERFACE, SymbolKind.BUILTIN_TYPE,
    )
