"""
Built-in Symbols and Standard Library Registration

Registers all built-in types, functions, and compiler intrinsics
available in the I programming language.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .symbols import (
    Symbol, SymbolKind, TypeDescriptor, SymbolType,
    Visibility, make_builtin_type, make_builtin_function,
    TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_STRING, TYPE_NONE,
    TYPE_ANY, TYPE_LIST, TYPE_DICT,
)
from .scopes import Scope, ScopeKind


# ── Built-in Types ──────────────────────────────────────────────

BUILTIN_TYPES: Dict[str, Symbol] = {
    'int': make_builtin_type('int'),
    'float': make_builtin_type('float'),
    'tandukanya': make_builtin_type('tandukanya'),
    'gutoranya': make_builtin_type('gutoranya'),
    'bool': make_builtin_type('bool'),
    'yego': make_builtin_type('bool'),
    'oya': make_builtin_type('bool'),
    'umuntu': make_builtin_type('umuntu'),
    'bbyte': make_builtin_type('bbyte'),
    'urutonde': make_builtin_type('urutonde'),
    'ikarita': make_builtin_type('ikarita'),
    'none': make_builtin_type('none'),
    'any': make_builtin_type('any'),
}

# ── Built-in Functions ──────────────────────────────────────────

BUILTIN_FUNCTIONS: Dict[str, Symbol] = {
    'andika': make_builtin_function(
        'andika', [TYPE_ANY], TYPE_NONE
    ),
    'soma': make_builtin_function(
        'soma', [], TYPE_STRING
    ),
    'uburengero': make_builtin_function(
        'uburengero', [TYPE_ANY], TYPE_INT
    ),
    'ubwoko': make_builtin_function(
        'ubwoko', [TYPE_ANY], TYPE_STRING
    ),
    'shobora_int': make_builtin_function(
        'shobora_int', [TYPE_ANY], TYPE_INT
    ),
    'shobora_float': make_builtin_function(
        'shobora_float', [TYPE_ANY], TYPE_FLOAT
    ),
    'shobora_umuntu': make_builtin_function(
        'shobora_umuntu', [TYPE_ANY], TYPE_STRING
    ),
    'shobora_bool': make_builtin_function(
        'shobora_bool', [TYPE_ANY], TYPE_BOOL
    ),
    'gukoma_func': make_builtin_function(
        'gukoma_func', [], TYPE_NONE
    ),
}

# ── Reserved Keywords ───────────────────────────────────────────

RESERVED_KEYWORDS = frozenset({
    'niba', 'cyangwa', 'cyangwa_niba', 'kugenda', 'gukoma',
    'subira', 'tanga', 'kora', 'wihuse', 'kugeza', 'kuri',
    'muri', 'buri', 'shyira', 'shyira_ko', 'umurimo', 'igiceri',
    'ikindi', 'urwego', 'akabuto', 'urubingo', 'ubwoko', 'kugira',
    'gukora', 'nshya', 'shyiramo', 'kugira_ngo', 'kandi', 'bitewe',
    'ari', 'si', 'gushyingura', 'kubika', 'ikinyoma', 'iherezo',
    'ubusa', 'self', 'super',
})


def register_builtins(scope: Scope) -> None:
    """Register all built-in symbols into a scope."""
    for name, sym in BUILTIN_TYPES.items():
        scope.define(sym)
    for name, sym in BUILTIN_FUNCTIONS.items():
        scope.define(sym)


def is_reserved_keyword(name: str) -> bool:
    """Check if a name is a reserved keyword."""
    return name in RESERVED_KEYWORDS


def is_builtin_type(name: str) -> bool:
    """Check if a name is a built-in type."""
    return name in BUILTIN_TYPES


def is_builtin_function(name: str) -> bool:
    """Check if a name is a built-in function."""
    return name in BUILTIN_FUNCTIONS


def get_builtin_type(name: str) -> Optional[Symbol]:
    """Get a built-in type symbol by name."""
    return BUILTIN_TYPES.get(name)


def get_builtin_function(name: str) -> Optional[Symbol]:
    """Get a built-in function symbol by name."""
    return BUILTIN_FUNCTIONS.get(name)


def resolve_type_name(name: str) -> Optional[TypeDescriptor]:
    """Resolve a type name to its TypeDescriptor."""
    sym = BUILTIN_TYPES.get(name)
    if sym and sym.type_descriptor:
        return sym.type_descriptor
    return None
