"""
Type Representation for the I Programming Language

Complete, immutable type hierarchy supporting all I types:
primitives, collections, functions, generics, traits, optionals,
results, tuples, ranges, and future async/SIMD types.

Every type is a value object: hashable, comparable, and immutable.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, FrozenSet, List, Optional, Tuple, Sequence
import itertools


# ══════════════════════════════════════════════════════════════════
# Global Type ID Generator
# ══════════════════════════════════════════════════════════════════

_type_id_counter = itertools.count(1)


def _next_type_id() -> int:
    """Generate a unique type ID."""
    return next(_type_id_counter)


def reset_type_ids() -> None:
    """Reset type ID counter (for testing only)."""
    global _type_id_counter
    _type_id_counter = itertools.count(1)


class Variance(Enum):
    """Type variance annotations for generic parameters."""
    INVARIANT = auto()
    COVARIANT = auto()
    CONTRAVARIANT = auto()


# ══════════════════════════════════════════════════════════════════
# Type Kind Enumeration
# ══════════════════════════════════════════════════════════════════


class TypeKind(Enum):
    """Classification of all type kinds in the I language."""

    # Primitive types
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    CHAR = auto()
    STRING = auto()
    NONE_TYPE = auto()

    # Compound types
    LIST = auto()
    MAP = auto()
    SET = auto()
    TUPLE = auto()
    RANGE = auto()

    # Function type
    FUNCTION = auto()

    # User-defined types
    CLASS = auto()
    STRUCT = auto()
    ENUM = auto()
    MODULE = auto()
    PACKAGE = auto()

    # Trait / Interface
    TRAIT = auto()
    INTERFACE = auto()

    # Generic types
    GENERIC = auto()
    TYPE_VAR = auto()

    # Parameterized types (e.g. List<Int>)
    PARAMETERIZED = auto()

    # Optional and Result
    OPTIONAL = auto()
    RESULT = auto()

    # Future types (ready for extension)
    FUTURE = auto()
    COROUTINE = auto()
    SIMD_VECTOR = auto()

    # Special types
    ANY = auto()
    UNKNOWN = auto()
    NEVER = auto()
    BOTTOM = auto()

    # Compile-time types
    CONST_TYPE = auto()


# ══════════════════════════════════════════════════════════════════
# Base Type
# ══════════════════════════════════════════════════════════════════


class Type(ABC):
    """
    Abstract base class for all types in the I language.

    Types are immutable value objects. Two types are equal if and only if
    they have the same structure and parameters.
    """

    __slots__ = ()

    @property
    def type_id(self) -> int:
        """Unique identifier for this type instance (identity-based)."""
        return id(self)

    @property
    @abstractmethod
    def kind(self) -> TypeKind:
        """The kind of this type."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this type."""
        ...

    @abstractmethod
    def is_assignable_to(self, target: Type) -> bool:
        """Can a value of this type be assigned to target?"""
        ...

    @abstractmethod
    def is_subtype_of(self, target: Type) -> bool:
        """Is this type a structural subtype of target?"""
        ...

    @property
    def is_primitive(self) -> bool:
        return self.kind in (
            TypeKind.INT, TypeKind.FLOAT, TypeKind.BOOL,
            TypeKind.CHAR, TypeKind.STRING, TypeKind.NONE_TYPE,
        )

    @property
    def is_numeric(self) -> bool:
        return self.kind in (TypeKind.INT, TypeKind.FLOAT)

    @property
    def is_collection(self) -> bool:
        return self.kind in (TypeKind.LIST, TypeKind.MAP, TypeKind.SET)

    @property
    def is_reference_type(self) -> bool:
        return self.kind in (
            TypeKind.CLASS, TypeKind.STRUCT, TypeKind.TRAIT,
            TypeKind.INTERFACE, TypeKind.LIST, TypeKind.MAP,
            TypeKind.SET, TypeKind.STRING, TypeKind.FUNCTION,
        )

    @property
    def is_value_type(self) -> bool:
        return self.kind in (
            TypeKind.INT, TypeKind.FLOAT, TypeKind.BOOL,
            TypeKind.CHAR, TypeKind.ENUM, TypeKind.TUPLE,
            TypeKind.RANGE,
        )

    @property
    def is_error_like(self) -> bool:
        return self.kind in (TypeKind.NEVER, TypeKind.BOTTOM, TypeKind.UNKNOWN)

    def __hash__(self) -> int:
        return hash((self.kind, self.name))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Type):
            return False
        return self.kind == other.kind and self.name == other.name

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


# ══════════════════════════════════════════════════════════════════
# Primitive Types
# ══════════════════════════════════════════════════════════════════


class PrimitiveType(Type):
    """Base for primitive types."""

    __slots__ = ("_kind", "_name")

    def __init__(self, kind: TypeKind, name: str) -> None:
        object.__setattr__(self, "_kind", kind)
        object.__setattr__(self, "_name", name)

    @property
    def kind(self) -> TypeKind:
        return self._kind

    @property
    def name(self) -> str:
        return self._name

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == self.kind:
            return True
        if self.kind == TypeKind.INT and target.kind == TypeKind.FLOAT:
            return True
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)


class IntType(PrimitiveType):
    def __init__(self) -> None:
        super().__init__(TypeKind.INT, "int")

    def __hash__(self) -> int:
        return hash((TypeKind.INT, "int"))


class FloatType(PrimitiveType):
    def __init__(self) -> None:
        super().__init__(TypeKind.FLOAT, "float")

    def __hash__(self) -> int:
        return hash((TypeKind.FLOAT, "float"))


class BoolType(PrimitiveType):
    def __init__(self) -> None:
        super().__init__(TypeKind.BOOL, "bool")

    def __hash__(self) -> int:
        return hash((TypeKind.BOOL, "bool"))


class CharType(PrimitiveType):
    def __init__(self) -> None:
        super().__init__(TypeKind.CHAR, "char")

    def __hash__(self) -> int:
        return hash((TypeKind.CHAR, "char"))


class StringType(PrimitiveType):
    def __init__(self) -> None:
        super().__init__(TypeKind.STRING, "umuntu")

    def __hash__(self) -> int:
        return hash((TypeKind.STRING, "umuntu"))

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        return target.kind == TypeKind.STRING


class NoneType(PrimitiveType):
    def __init__(self) -> None:
        super().__init__(TypeKind.NONE_TYPE, "none")

    def __hash__(self) -> int:
        return hash((TypeKind.NONE_TYPE, "none"))

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.OPTIONAL:
            return True
        return target.kind == TypeKind.NONE_TYPE


# Singleton instances for primitive types
TYPE_INT = IntType()
TYPE_FLOAT = FloatType()
TYPE_BOOL = BoolType()
TYPE_CHAR = CharType()
TYPE_STRING = StringType()
TYPE_NONE = NoneType()


# ══════════════════════════════════════════════════════════════════
# Special Types
# ══════════════════════════════════════════════════════════════════


class AnyType(Type):
    """Top type - compatible with all types."""

    __slots__ = ()

    @property
    def kind(self) -> TypeKind:
        return TypeKind.ANY

    @property
    def name(self) -> str:
        return "any"

    def is_assignable_to(self, target: Type) -> bool:
        return True

    def is_subtype_of(self, target: Type) -> bool:
        return True

    def __hash__(self) -> int:
        return hash((TypeKind.ANY, "any"))


class UnknownType(Type):
    """Type is not yet known (used during inference)."""

    __slots__ = ()

    @property
    def kind(self) -> TypeKind:
        return TypeKind.UNKNOWN

    @property
    def name(self) -> str:
        return "unknown"

    def is_assignable_to(self, target: Type) -> bool:
        return True

    def is_subtype_of(self, target: Type) -> bool:
        return True

    def __hash__(self) -> int:
        return hash((TypeKind.UNKNOWN, "unknown"))


class NeverType(Type):
    """Bottom type - subtype of all types. Represents unreachable code."""

    __slots__ = ()

    @property
    def kind(self) -> TypeKind:
        return TypeKind.NEVER

    @property
    def name(self) -> str:
        return "never"

    def is_assignable_to(self, target: Type) -> bool:
        return True

    def is_subtype_of(self, target: Type) -> bool:
        return True

    def __hash__(self) -> int:
        return hash((TypeKind.NEVER, "never"))


class BottomType(Type):
    """Bottom type alias - subtype of all types."""

    __slots__ = ()

    @property
    def kind(self) -> TypeKind:
        return TypeKind.BOTTOM

    @property
    def name(self) -> str:
        return "bottom"

    def is_assignable_to(self, target: Type) -> bool:
        return True

    def is_subtype_of(self, target: Type) -> bool:
        return True

    def __hash__(self) -> int:
        return hash((TypeKind.BOTTOM, "bottom"))


TYPE_ANY = AnyType()
TYPE_UNKNOWN = UnknownType()
TYPE_NEVER = NeverType()
TYPE_BOTTOM = BottomType()


# ══════════════════════════════════════════════════════════════════
# Collection Types
# ══════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ListType(Type):
    """List type: urutonde<T>."""

    element_type: Type = field(default_factory=lambda: TYPE_ANY)

    @property
    def kind(self) -> TypeKind:
        return TypeKind.LIST

    @property
    def name(self) -> str:
        return f"urutonde<{self.element_type.name}>"

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.LIST:
            return self.element_type.is_assignable_to(target.element_type)
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.LIST, self.element_type))


@dataclass(frozen=True)
class MapType(Type):
    """Map type: ikarita<K, V>."""

    key_type: Type = field(default_factory=lambda: TYPE_ANY)
    value_type: Type = field(default_factory=lambda: TYPE_ANY)

    @property
    def kind(self) -> TypeKind:
        return TypeKind.MAP

    @property
    def name(self) -> str:
        return f"ikarita<{self.key_type.name}, {self.value_type.name}>"

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.MAP:
            return (self.key_type.is_assignable_to(target.key_type) and
                    self.value_type.is_assignable_to(target.value_type))
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.MAP, self.key_type, self.value_type))


@dataclass(frozen=True)
class SetType(Type):
    """Set type: icyobo<T>."""

    element_type: Type = field(default_factory=lambda: TYPE_ANY)

    @property
    def kind(self) -> TypeKind:
        return TypeKind.SET

    @property
    def name(self) -> str:
        return f"icyobo<{self.element_type.name}>"

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.SET:
            return self.element_type.is_assignable_to(target.element_type)
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.SET, self.element_type))


# ══════════════════════════════════════════════════════════════════
# Tuple Type
# ══════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class TupleType(Type):
    """Tuple type: (T1, T2, ...)."""

    element_types: Tuple[Type, ...] = field(default_factory=tuple)

    @property
    def kind(self) -> TypeKind:
        return TypeKind.TUPLE

    @property
    def name(self) -> str:
        inner = ", ".join(t.name for t in self.element_types)
        return f"({inner})"

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.TUPLE:
            if len(self.element_types) != len(target.element_types):
                return False
            return all(s.is_assignable_to(t) for s, t in
                       zip(self.element_types, target.element_types))
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.TUPLE, self.element_types))

    @property
    def arity(self) -> int:
        return len(self.element_types)


# ══════════════════════════════════════════════════════════════════
# Range Type
# ══════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class RangeType(Type):
    """Range type: urutonde_rwibumbiro<T>."""

    element_type: Type = field(default_factory=lambda: TYPE_INT)

    @property
    def kind(self) -> TypeKind:
        return TypeKind.RANGE

    @property
    def name(self) -> str:
        return f"urutonde_rwibumbiro<{self.element_type.name}>"

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.RANGE:
            return self.element_type.is_assignable_to(target.element_type)
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.RANGE, self.element_type))


# ══════════════════════════════════════════════════════════════════
# Function Type
# ══════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class FunctionType(Type):
    """Function type: (P1, P2, ...) -> R."""

    param_types: Tuple[Type, ...] = field(default_factory=tuple)
    return_type: Type = field(default_factory=lambda: TYPE_NONE)

    @property
    def kind(self) -> TypeKind:
        return TypeKind.FUNCTION

    @property
    def name(self) -> str:
        params = ", ".join(t.name for t in self.param_types)
        return f"({params}) -> {self.return_type.name}"

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind != TypeKind.FUNCTION:
            return False
        if len(self.param_types) != len(target.param_types):
            return False
        for s, t in zip(self.param_types, target.param_types):
            if not t.is_assignable_to(s):
                return False
        return self.return_type.is_assignable_to(target.return_type)

    def is_subtype_of(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind != TypeKind.FUNCTION:
            return False
        if len(self.param_types) != len(target.param_types):
            return False
        for s, t in zip(self.param_types, target.param_types):
            if not t.is_assignable_to(s):
                return False
        return self.return_type.is_subtype_of(target.return_type)

    def __hash__(self) -> int:
        return hash((TypeKind.FUNCTION, self.param_types, self.return_type))

    @property
    def arity(self) -> int:
        return len(self.param_types)


# ══════════════════════════════════════════════════════════════════
# User-Defined Types (Class, Struct, Enum, Trait, Interface)
# ══════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class NamedType(Type):
    """
    A named type reference (class, struct, enum, trait, or interface).

    Named types are identified by their fully-qualified name.
    The actual definition is stored in the TypeRegistry.
    """

    _kind: TypeKind
    _name: str

    @property
    def kind(self) -> TypeKind:
        return self._kind

    @property
    def name(self) -> str:
        return self._name

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == self.kind and self.name == target.name:
            return True
        if self.kind == TypeKind.CLASS and target.kind == TypeKind.STRUCT:
            return False
        if self.kind == TypeKind.STRUCT and target.kind == TypeKind.CLASS:
            return False
        return False

    def is_subtype_of(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if self.kind == target.kind and self.name == target.name:
            return True
        return False

    def __hash__(self) -> int:
        return hash((self.kind, self.name))


@dataclass(frozen=True)
class ClassType(Type):
    """Class type with full definition info."""

    _name: str
    parent: Optional[str] = None
    traits: Tuple[str, ...] = field(default_factory=tuple)

    @property
    def kind(self) -> TypeKind:
        return TypeKind.CLASS

    @property
    def name(self) -> str:
        return self._name

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.CLASS and target.name == self._name:
            return True
        if target.kind == TypeKind.CLASS and self.parent:
            return self.parent == target.name
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.CLASS, self._name))


@dataclass(frozen=True)
class StructType(Type):
    """Struct type."""

    _name: str

    @property
    def kind(self) -> TypeKind:
        return TypeKind.STRUCT

    @property
    def name(self) -> str:
        return self._name

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.STRUCT and target.name == self._name:
            return True
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.STRUCT, self._name))


@dataclass(frozen=True)
class EnumType(Type):
    """Enum type."""

    _name: str

    @property
    def kind(self) -> TypeKind:
        return TypeKind.ENUM

    @property
    def name(self) -> str:
        return self._name

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.ENUM and target.name == self._name:
            return True
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.ENUM, self._name))


@dataclass(frozen=True)
class TraitType(Type):
    """Trait type."""

    _name: str

    @property
    def kind(self) -> TypeKind:
        return TypeKind.TRAIT

    @property
    def name(self) -> str:
        return self._name

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.TRAIT and target.name == self._name:
            return True
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.TRAIT, self._name))


@dataclass(frozen=True)
class InterfaceType(Type):
    """Interface type."""

    _name: str

    @property
    def kind(self) -> TypeKind:
        return TypeKind.INTERFACE

    @property
    def name(self) -> str:
        return self._name

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.INTERFACE and target.name == self._name:
            return True
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.INTERFACE, self._name))


# ══════════════════════════════════════════════════════════════════
# Optional and Result Types
# ══════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class OptionalType(Type):
    """Optional type: T? - may be T or None."""

    inner: Type = field(default_factory=lambda: TYPE_NONE)

    @property
    def kind(self) -> TypeKind:
        return TypeKind.OPTIONAL

    @property
    def name(self) -> str:
        return f"{self.inner.name}?"

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.NONE_TYPE:
            return True
        if target.kind == TypeKind.OPTIONAL:
            return self.inner.is_assignable_to(target.inner)
        return self.inner.is_assignable_to(target)

    def is_subtype_of(self, target: Type) -> bool:
        if target.kind == TypeKind.OPTIONAL:
            return self.inner.is_subtype_of(target.inner)
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.OPTIONAL, self.inner))

    def unwrap(self) -> Type:
        return self.inner


@dataclass(frozen=True)
class ResultType(Type):
    """Result type: Igitegererezo<T, E> - Ok(T) or Err(E)."""

    ok_type: Type = field(default_factory=lambda: TYPE_ANY)
    err_type: Type = field(default_factory=lambda: TYPE_ANY)

    @property
    def kind(self) -> TypeKind:
        return TypeKind.RESULT

    @property
    def name(self) -> str:
        return f"Igitegererezo<{self.ok_type.name}, {self.err_type.name}>"

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.RESULT:
            return (self.ok_type.is_assignable_to(target.ok_type) and
                    self.err_type.is_assignable_to(target.err_type))
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.RESULT, self.ok_type, self.err_type))


# ══════════════════════════════════════════════════════════════════
# Generic Type Variable
# ══════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class TypeVariable(Type):
    """
    Type variable for generic parameters.

    Each type variable has a unique name and optional bounds (constraints).
    Supports variance annotations for generic type checking.
    """

    _name: str = ""
    upper_bound: Optional[Type] = None
    lower_bound: Optional[Type] = None
    variance: Variance = Variance.INVARIANT

    @property
    def kind(self) -> TypeKind:
        return TypeKind.TYPE_VAR

    @property
    def name(self) -> str:
        return self._name

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.TYPE_VAR and target.name == self._name:
            return True
        if self.upper_bound:
            return self.upper_bound.is_assignable_to(target)
        return True

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.TYPE_VAR, self._name))


# ══════════════════════════════════════════════════════════════════
# Generic Type (Parameterized)
# ══════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class GenericType(Type):
    """
    A parameterized generic type: name<T1, T2, ...>.

    This represents a concrete instantiation of a generic declaration.
    """

    _name: str
    type_args: Tuple[Type, ...] = field(default_factory=tuple)

    @property
    def kind(self) -> TypeKind:
        return TypeKind.PARAMETERIZED

    @property
    def name(self) -> str:
        args = ", ".join(t.name for t in self.type_args)
        return f"{self._name}<{args}>"

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.PARAMETERIZED and target.name == self.name:
            return True
        if target.kind in (TypeKind.CLASS, TypeKind.TRAIT, TypeKind.INTERFACE):
            return target.name == self._name
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.PARAMETERIZED, self._name, self.type_args))

    @property
    def base_name(self) -> str:
        return self._name


# ══════════════════════════════════════════════════════════════════
# Future / Async Types (future-ready)
# ══════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class FutureType(Type):
    """Future/async type: Tegerereza<T>."""

    inner: Type = field(default_factory=lambda: TYPE_ANY)

    @property
    def kind(self) -> TypeKind:
        return TypeKind.FUTURE

    @property
    def name(self) -> str:
        return f"Tegerereza<{self.inner.name}>"

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.FUTURE:
            return self.inner.is_assignable_to(target.inner)
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.FUTURE, self.inner))


@dataclass(frozen=True)
class CoroutineType(Type):
    """Coroutine type: Korohereza<Y, R>."""

    yield_type: Type = field(default_factory=lambda: TYPE_ANY)
    return_type: Type = field(default_factory=lambda: TYPE_ANY)

    @property
    def kind(self) -> TypeKind:
        return TypeKind.COROUTINE

    @property
    def name(self) -> str:
        return f"Korohereza<{self.yield_type.name}, {self.return_type.name}>"

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.COROUTINE:
            return (self.yield_type.is_assignable_to(target.yield_type) and
                    self.return_type.is_assignable_to(target.return_type))
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.COROUTINE, self.yield_type, self.return_type))


@dataclass(frozen=True)
class SimdVectorType(Type):
    """SIMD/vector type: Imbonedvwa<T, N>."""

    element_type: Type = field(default_factory=lambda: TYPE_FLOAT)
    size: int = 4

    @property
    def kind(self) -> TypeKind:
        return TypeKind.SIMD_VECTOR

    @property
    def name(self) -> str:
        return f"Imbonedvwa<{self.element_type.name}, {self.size}>"

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        if target.kind == TypeKind.SIMD_VECTOR:
            return (self.element_type.is_assignable_to(target.element_type) and
                    self.size == target.size)
        return False

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.SIMD_VECTOR, self.element_type, self.size))


# ══════════════════════════════════════════════════════════════════
# Module / Package Types
# ══════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ModuleType(Type):
    """Module type."""

    _name: str

    @property
    def kind(self) -> TypeKind:
        return TypeKind.MODULE

    @property
    def name(self) -> str:
        return self._name

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        return target.kind == TypeKind.MODULE and target.name == self._name

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.MODULE, self._name))


@dataclass(frozen=True)
class PackageType(Type):
    """Package type."""

    _name: str

    @property
    def kind(self) -> TypeKind:
        return TypeKind.PACKAGE

    @property
    def name(self) -> str:
        return self._name

    def is_assignable_to(self, target: Type) -> bool:
        if target.kind == TypeKind.ANY:
            return True
        return target.kind == TypeKind.PACKAGE and target.name == self._name

    def is_subtype_of(self, target: Type) -> bool:
        return self.is_assignable_to(target)

    def __hash__(self) -> int:
        return hash((TypeKind.PACKAGE, self._name))

    def __hash__(self) -> int:
        return hash((TypeKind.PACKAGE, self._name))


# ══════════════════════════════════════════════════════════════════
# Type Construction Helpers
# ══════════════════════════════════════════════════════════════════


def make_list(element: Type) -> ListType:
    """Create a list type."""
    return ListType(element)


def make_map(key: Type, value: Type) -> MapType:
    """Create a map type."""
    return MapType(key, value)


def make_set(element: Type) -> SetType:
    """Create a set type."""
    return SetType(element)


def make_tuple(*elements: Type) -> TupleType:
    """Create a tuple type."""
    return TupleType(tuple(elements))


def make_optional(inner: Type) -> OptionalType:
    """Create an optional type."""
    return OptionalType(inner)


def make_result(ok_type: Type, err_type: Type) -> ResultType:
    """Create a result type."""
    return ResultType(ok_type, err_type)


def make_function(params: Sequence[Type], ret: Type) -> FunctionType:
    """Create a function type."""
    return FunctionType(tuple(params), ret)


def make_class_type(name: str, parent: Optional[str] = None) -> ClassType:
    """Create a class type."""
    return ClassType(name, parent)


def make_struct_type(name: str) -> StructType:
    """Create a struct type."""
    return StructType(name)


def make_enum_type(name: str) -> EnumType:
    """Create an enum type."""
    return EnumType(name)


def make_trait_type(name: str) -> TraitType:
    """Create a trait type."""
    return TraitType(name)


def make_interface_type(name: str) -> InterfaceType:
    """Create an interface type."""
    return InterfaceType(name)


def make_type_var(name: str, bound: Optional[Type] = None) -> TypeVariable:
    """Create a type variable."""
    return TypeVariable(name, bound)


def make_generic(name: str, *args: Type) -> GenericType:
    """Create a parameterized generic type."""
    return GenericType(name, tuple(args))


def make_range(element: Type) -> RangeType:
    """Create a range type."""
    return RangeType(element)


def make_future(inner: Type) -> FutureType:
    """Create a future type."""
    return FutureType(inner)


def make_coroutine(yield_type: Type, ret_type: Type) -> CoroutineType:
    """Create a coroutine type."""
    return CoroutineType(yield_type, ret_type)


def make_simd(element: Type, size: int = 4) -> SimdVectorType:
    """Create a SIMD vector type."""
    return SimdVectorType(element, size)


# ══════════════════════════════════════════════════════════════════
# Type Unification Helpers
# ══════════════════════════════════════════════════════════════════


def is_compatible(source: Type, target: Type) -> bool:
    """Check if source type is compatible with target type."""
    return source.is_assignable_to(target)


def is_strict_subtype(source: Type, target: Type) -> bool:
    """Check if source is a strict subtype of target (not equal)."""
    return source.is_subtype_of(target) and source != target


def common_type(a: Type, b: Type) -> Optional[Type]:
    """Find the least upper bound (common type) of two types."""
    if a == b:
        return a
    if a.kind == TypeKind.ANY:
        return b
    if b.kind == TypeKind.ANY:
        return a
    if a.kind == TypeKind.NEVER:
        return b
    if b.kind == TypeKind.NEVER:
        return a
    if a.kind == TypeKind.NONE_TYPE and b.kind == TypeKind.OPTIONAL:
        return b
    if b.kind == TypeKind.NONE_TYPE and a.kind == TypeKind.OPTIONAL:
        return a
    if a.kind == TypeKind.NONE_TYPE and b.kind == TypeKind.NONE_TYPE:
        return TYPE_NONE
    if a.is_numeric and b.is_numeric:
        if a.kind == TypeKind.FLOAT or b.kind == TypeKind.FLOAT:
            return TYPE_FLOAT
        return TYPE_INT
    # Optional wrapping: T and U -> Optional<T> | Optional<U> if either is optional
    if a.kind == TypeKind.OPTIONAL or b.kind == TypeKind.OPTIONAL:
        inner_a = a.inner if a.kind == TypeKind.OPTIONAL else a
        inner_b = b.inner if b.kind == TypeKind.OPTIONAL else b
        if inner_a.kind == TypeKind.NONE_TYPE:
            return OptionalType(inner_b)
        if inner_b.kind == TypeKind.NONE_TYPE:
            return OptionalType(inner_a)
        inner_common = common_type(inner_a, inner_b)
        if inner_common:
            return OptionalType(inner_common)
    # List covariance: List<T> and List<U> -> List<T|U>
    if a.kind == TypeKind.LIST and b.kind == TypeKind.LIST:
        elem_common = common_type(a.element_type, b.element_type)
        if elem_common:
            return ListType(elem_common)
    # Map covariance: Map<K1,V1> and Map<K2,V2> -> Map<K1|K2, V1|V2>
    if a.kind == TypeKind.MAP and b.kind == TypeKind.MAP:
        key_common = common_type(a.key_type, b.key_type)
        val_common = common_type(a.value_type, b.value_type)
        if key_common and val_common:
            return MapType(key_common, val_common)
    # Set covariance: Set<T> and Set<U> -> Set<T|U>
    if a.kind == TypeKind.SET and b.kind == TypeKind.SET:
        elem_common = common_type(a.element_type, b.element_type)
        if elem_common:
            return SetType(elem_common)
    # Function contravariance: (P1) -> R1 and (P2) -> R2
    if a.kind == TypeKind.FUNCTION and b.kind == TypeKind.FUNCTION:
        if len(a.param_types) == len(b.param_types):
            ret_common = common_type(a.return_type, b.return_type)
            if ret_common is None:
                return None
            param_commons = []
            for pa, pb in zip(a.param_types, b.param_types):
                pc = common_type(pa, pb)
                if pc is None:
                    return None
                param_commons.append(pc)
            return FunctionType(tuple(param_commons), ret_common)
    # Range covariance
    if a.kind == TypeKind.RANGE and b.kind == TypeKind.RANGE:
        elem_common = common_type(a.element_type, b.element_type)
        if elem_common:
            return RangeType(elem_common)
    return None
