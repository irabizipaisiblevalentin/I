"""
Symbol Table System for the I Programming Language

Complete support for all symbol types: variables, constants, functions, methods,
classes, structs, enums, traits, interfaces, parameters, modules, namespaces,
and compiler intrinsics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional


class SymbolKind(Enum):
    """Classification of all symbols."""
    VARIABLE = auto()
    CONSTANT = auto()
    FUNCTION = auto()
    METHOD = auto()
    CLASS = auto()
    STRUCT = auto()
    ENUM = auto()
    TRAIT = auto()
    INTERFACE = auto()
    PARAMETER = auto()
    MODULE = auto()
    ALIAS = auto()
    BUILTIN_TYPE = auto()
    BUILTIN_FUNCTION = auto()
    INTRINSIC = auto()


class Visibility(Enum):
    """Symbol visibility levels."""
    PUBLIC = auto()
    PRIVATE = auto()
    INTERNAL = auto()
    MODULE = auto()
    PACKAGE = auto()


class SymbolType(Enum):
    """Semantic type classification."""
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STRING = "umuntu"
    NONE = "none"
    ANY = "any"
    LIST = "urutonde"
    DICT = "ikarita"
    FUNCTION = "function"
    CLASS = "class"
    STRUCT = "struct"
    ENUM = "enum"
    TRAIT = "trait"
    INTERFACE = "interface"
    MODULE = "module"
    UNKNOWN = "unknown"


@dataclass
class TypeDescriptor:
    """Describes the type of a symbol."""
    kind: SymbolType
    name: str = ""
    param_types: List[TypeDescriptor] = field(default_factory=list)
    return_type: Optional[TypeDescriptor] = None
    element_type: Optional[TypeDescriptor] = None
    key_type: Optional[TypeDescriptor] = None
    value_type: Optional[TypeDescriptor] = None

    def __repr__(self) -> str:
        if self.kind == SymbolType.FUNCTION:
            params = ", ".join(repr(p) for p in self.param_types)
            ret = repr(self.return_type) if self.return_type else "none"
            return f"({params}) -> {ret}"
        if self.kind == SymbolType.LIST and self.element_type:
            return f"urutonde<{self.element_type}>"
        if self.kind == SymbolType.DICT and self.key_type and self.value_type:
            return f"ikarita<{self.key_type}, {self.value_type}>"
        return self.name or self.kind.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeDescriptor):
            return False
        if self.kind != other.kind:
            return False
        if self.kind == SymbolType.FUNCTION:
            return (self.param_types == other.param_types and
                    self.return_type == other.return_type)
        return self.name == other.name

    def is_compatible_with(self, target: TypeDescriptor) -> bool:
        """Check if this type is compatible with target."""
        if target.kind == SymbolType.ANY or self.kind == SymbolType.ANY:
            return True
        if self == target:
            return True
        if self.kind == SymbolType.NONE and target.kind == SymbolType.NONE:
            return True
        return False


# ── Type Descriptors ────────────────────────────────────────────

TYPE_INT = TypeDescriptor(SymbolType.INT, "int")
TYPE_FLOAT = TypeDescriptor(SymbolType.FLOAT, "float")
TYPE_BOOL = TypeDescriptor(SymbolType.BOOL, "bool")
TYPE_STRING = TypeDescriptor(SymbolType.STRING, "umuntu")
TYPE_NONE = TypeDescriptor(SymbolType.NONE, "none")
TYPE_ANY = TypeDescriptor(SymbolType.ANY, "any")
TYPE_LIST = TypeDescriptor(SymbolType.LIST, "urutonde")
TYPE_DICT = TypeDescriptor(SymbolType.DICT, "ikarita")


@dataclass
class Symbol:
    """
    A semantic symbol.

    Every declared identifier in the program creates a Symbol with:
    - name and kind
    - resolved type descriptor
    - visibility level
    - declaration location for diagnostics
    - constness flag
    - metadata for compiler passes
    """

    name: str
    kind: SymbolKind
    type_descriptor: Optional[TypeDescriptor] = None
    visibility: Visibility = Visibility.PUBLIC
    is_const: bool = False
    declaration_location: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    # For class/struct/enum: member symbols
    members: Dict[str, Symbol] = field(default_factory=dict)

    # For functions/methods: parameter symbols
    parameters: List[Symbol] = field(default_factory=list)

    # For modules: exported symbols
    exports: Dict[str, Symbol] = field(default_factory=dict)

    # For classes: parent class name
    parent_name: Optional[str] = None

    def __repr__(self) -> str:
        type_str = f" : {self.type_descriptor}" if self.type_descriptor else ""
        const_str = " const" if self.is_const else ""
        return f"Symbol({self.name}, {self.kind.name}{type_str}{const_str})"

    def set_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)


def make_variable(name: str, type_desc: TypeDescriptor,
                  is_const: bool = False, vis: Visibility = Visibility.PUBLIC,
                  loc: Any = None) -> Symbol:
    """Create a variable symbol."""
    return Symbol(name, SymbolKind.VARIABLE, type_desc, vis, is_const, loc)


def make_constant(name: str, type_desc: TypeDescriptor,
                  vis: Visibility = Visibility.PUBLIC, loc: Any = None) -> Symbol:
    """Create a constant symbol."""
    return Symbol(name, SymbolKind.CONSTANT, type_desc, vis, True, loc)


def make_function(name: str, params: List[TypeDescriptor],
                  return_type: TypeDescriptor, vis: Visibility = Visibility.PUBLIC,
                  loc: Any = None) -> Symbol:
    """Create a function symbol."""
    td = TypeDescriptor(SymbolType.FUNCTION, name, params, return_type)
    sym = Symbol(name, SymbolKind.FUNCTION, td, vis, False, loc)
    return sym


def make_method(name: str, params: List[TypeDescriptor],
                return_type: TypeDescriptor, vis: Visibility = Visibility.PUBLIC,
                is_static: bool = False, loc: Any = None) -> Symbol:
    """Create a method symbol."""
    td = TypeDescriptor(SymbolType.FUNCTION, name, params, return_type)
    sym = Symbol(name, SymbolKind.METHOD, td, vis, False, loc)
    sym.set_metadata('is_static', is_static)
    return sym


def make_class(name: str, parent_name: Optional[str] = None,
               vis: Visibility = Visibility.PUBLIC, loc: Any = None) -> Symbol:
    """Create a class symbol."""
    td = TypeDescriptor(SymbolType.CLASS, name)
    return Symbol(name, SymbolKind.CLASS, td, vis, False, loc,
                  parent_name=parent_name)


def make_struct(name: str, vis: Visibility = Visibility.PUBLIC,
                loc: Any = None) -> Symbol:
    """Create a struct symbol."""
    td = TypeDescriptor(SymbolType.STRUCT, name)
    return Symbol(name, SymbolKind.STRUCT, td, vis, False, loc)


def make_enum(name: str, vis: Visibility = Visibility.PUBLIC,
              loc: Any = None) -> Symbol:
    """Create an enum symbol."""
    td = TypeDescriptor(SymbolType.ENUM, name)
    return Symbol(name, SymbolKind.ENUM, td, vis, False, loc)


def make_trait(name: str, vis: Visibility = Visibility.PUBLIC,
               loc: Any = None) -> Symbol:
    """Create a trait symbol."""
    td = TypeDescriptor(SymbolType.TRAIT, name)
    return Symbol(name, SymbolKind.TRAIT, td, vis, False, loc)


def make_interface(name: str, vis: Visibility = Visibility.PUBLIC,
                   loc: Any = None) -> Symbol:
    """Create an interface symbol."""
    td = TypeDescriptor(SymbolType.INTERFACE, name)
    return Symbol(name, SymbolKind.INTERFACE, td, vis, False, loc)


def make_parameter(name: str, type_desc: Optional[TypeDescriptor] = None,
                   loc: Any = None) -> Symbol:
    """Create a parameter symbol."""
    return Symbol(name, SymbolKind.PARAMETER, type_desc or TYPE_ANY,
                  Visibility.PUBLIC, False, loc)


def make_module(name: str, vis: Visibility = Visibility.PUBLIC,
                loc: Any = None) -> Symbol:
    """Create a module symbol."""
    td = TypeDescriptor(SymbolType.MODULE, name)
    return Symbol(name, SymbolKind.MODULE, td, vis, False, loc)


def make_builtin_type(name: str) -> Symbol:
    """Create a built-in type symbol."""
    kind_map = {
        'int': SymbolType.INT, 'float': SymbolType.FLOAT,
        'bool': SymbolType.BOOL, 'umuntu': SymbolType.STRING,
        'urutonde': SymbolType.LIST, 'ikarita': SymbolType.DICT,
        'none': SymbolType.NONE, 'any': SymbolType.ANY,
        'tandukanya': SymbolType.FLOAT, 'gutoranya': SymbolType.FLOAT,
        'bbyte': SymbolType.STRING,
    }
    td = TypeDescriptor(kind_map.get(name, SymbolType.UNKNOWN), name)
    return Symbol(name, SymbolKind.BUILTIN_TYPE, td, Visibility.PUBLIC, True)


def make_builtin_function(name: str, params: List[TypeDescriptor],
                          return_type: TypeDescriptor) -> Symbol:
    """Create a built-in function symbol."""
    td = TypeDescriptor(SymbolType.FUNCTION, name, params, return_type)
    return Symbol(name, SymbolKind.BUILTIN_FUNCTION, td, Visibility.PUBLIC, True)
