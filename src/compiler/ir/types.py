"""
IR Type System

Lightweight type system for the I language Intermediate Representation.
Separate from the source-level type system — represents machine-level types
needed for code generation, optimization, and serialization.

Design principles:
- Immutable value objects
- Structural equality (two types with same structure are equal)
- Minimal set of types sufficient for all backends
- No source-level type information leaks here
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List


# ══════════════════════════════════════════════════════════════════
# IR Type Kind
# ══════════════════════════════════════════════════════════════════


class IRTypeKind(Enum):
    """Classification of all IR type kinds."""
    VOID = auto()
    LABEL = auto()
    METADATA = auto()
    TOKEN = auto()
    INTEGER = auto()
    FLOAT = auto()
    POINTER = auto()
    ARRAY = auto()
    STRUCT = auto()
    FUNCTION = auto()
    VECTOR = auto()


# ══════════════════════════════════════════════════════════════════
# IR Type (Abstract Base)
# ══════════════════════════════════════════════════════════════════


class IRType(ABC):
    """Base class for all IR types."""
    __slots__ = ()

    @property
    @abstractmethod
    def kind(self) -> IRTypeKind:
        """Type kind classification."""
        ...

    @property
    @abstractmethod
    def is_first_class(self) -> bool:
        """Whether this type can be a value (not void/label/metadata)."""
        ...

    @property
    @abstractmethod
    def is_zero_sized(self) -> bool:
        """Whether this type has zero size."""
        ...

    @property
    def is_integer(self) -> bool:
        return self.kind == IRTypeKind.INTEGER

    @property
    def is_float(self) -> bool:
        return self.kind == IRTypeKind.FLOAT

    @property
    def is_pointer(self) -> bool:
        return self.kind == IRTypeKind.POINTER

    @property
    def is_array(self) -> bool:
        return self.kind == IRTypeKind.ARRAY

    @property
    def is_struct(self) -> bool:
        return self.kind == IRTypeKind.STRUCT

    @property
    def is_function(self) -> bool:
        return self.kind == IRTypeKind.FUNCTION

    @property
    def is_void(self) -> bool:
        return self.kind == IRTypeKind.VOID

    @property
    def is_vector(self) -> bool:
        return self.kind == IRTypeKind.VECTOR

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        ...

    @abstractmethod
    def __hash__(self) -> int:
        ...

    @abstractmethod
    def __repr__(self) -> str:
        ...


# ══════════════════════════════════════════════════════════════════
# Concrete IR Types
# ══════════════════════════════════════════════════════════════════


class VoidType(IRType):
    """The void type — used for functions with no return value."""
    __slots__ = ()

    @property
    def kind(self) -> IRTypeKind:
        return IRTypeKind.VOID

    @property
    def is_first_class(self) -> bool:
        return False

    @property
    def is_zero_sized(self) -> bool:
        return True

    def __eq__(self, other: object) -> bool:
        return isinstance(other, VoidType)

    def __hash__(self) -> int:
        return hash(("void",))

    def __repr__(self) -> str:
        return "void"


class LabelType(IRType):
    """The label type — used for basic block references."""
    __slots__ = ()

    @property
    def kind(self) -> IRTypeKind:
        return IRTypeKind.LABEL

    @property
    def is_first_class(self) -> bool:
        return False

    @property
    def is_zero_sized(self) -> bool:
        return True

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LabelType)

    def __hash__(self) -> int:
        return hash(("label",))

    def __repr__(self) -> str:
        return "label"


class MetadataType(IRType):
    """The metadata type — used for debug info and metadata nodes."""
    __slots__ = ()

    @property
    def kind(self) -> IRTypeKind:
        return IRTypeKind.METADATA

    @property
    def is_first_class(self) -> bool:
        return False

    @property
    def is_zero_sized(self) -> bool:
        return True

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MetadataType)

    def __hash__(self) -> int:
        return hash(("metadata",))

    def __repr__(self) -> str:
        return "metadata"


class TokenType(IRType):
    """The token type — used for inline assembly and special values."""
    __slots__ = ()

    @property
    def kind(self) -> IRTypeKind:
        return IRTypeKind.TOKEN

    @property
    def is_first_class(self) -> bool:
        return False

    @property
    def is_zero_sized(self) -> bool:
        return True

    def __eq__(self, other: object) -> bool:
        return isinstance(other, TokenType)

    def __hash__(self) -> int:
        return hash(("token",))

    def __repr__(self) -> str:
        return "token"


class IntegerType(IRType):
    """An integer type with a specific bit width."""
    __slots__ = ("_bit_width",)

    def __init__(self, bit_width: int) -> None:
        object.__setattr__(self, "_bit_width", bit_width)

    @property
    def bit_width(self) -> int:
        return self._bit_width

    @property
    def kind(self) -> IRTypeKind:
        return IRTypeKind.INTEGER

    @property
    def is_first_class(self) -> bool:
        return True

    @property
    def is_zero_sized(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, IntegerType) and self._bit_width == other._bit_width

    def __hash__(self) -> int:
        return hash(("int", self._bit_width))

    def __repr__(self) -> str:
        return f"i{self._bit_width}"


class FloatType(IRType):
    """A floating-point type with a specific bit width."""
    __slots__ = ("_bit_width",)

    def __init__(self, bit_width: int) -> None:
        object.__setattr__(self, "_bit_width", bit_width)

    @property
    def bit_width(self) -> int:
        return self._bit_width

    @property
    def kind(self) -> IRTypeKind:
        return IRTypeKind.FLOAT

    @property
    def is_first_class(self) -> bool:
        return True

    @property
    def is_zero_sized(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FloatType) and self._bit_width == other._bit_width

    def __hash__(self) -> int:
        return hash(("float", self._bit_width))

    def __repr__(self) -> str:
        return f"f{self._bit_width}"


class PointerType(IRType):
    """A pointer to another type."""
    __slots__ = ("_element_type", "_address_space")

    def __init__(self, element_type: IRType, address_space: int = 0) -> None:
        object.__setattr__(self, "_element_type", element_type)
        object.__setattr__(self, "_address_space", address_space)

    @property
    def element_type(self) -> IRType:
        return self._element_type

    @property
    def address_space(self) -> int:
        return self._address_space

    @property
    def kind(self) -> IRTypeKind:
        return IRTypeKind.POINTER

    @property
    def is_first_class(self) -> bool:
        return True

    @property
    def is_zero_sized(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, PointerType)
                and self._element_type == other._element_type
                and self._address_space == other._address_space)

    def __hash__(self) -> int:
        return hash(("ptr", self._element_type, self._address_space))

    def __repr__(self) -> str:
        if self._address_space == 0:
            return f"{self._element_type}*"
        return f"{self._element_type} addrspace({self._address_space})*"


class ArrayType(IRType):
    """A fixed-length array of elements."""
    __slots__ = ("_length", "_element_type")

    def __init__(self, length: int, element_type: IRType) -> None:
        object.__setattr__(self, "_length", length)
        object.__setattr__(self, "_element_type", element_type)

    @property
    def length(self) -> int:
        return self._length

    @property
    def element_type(self) -> IRType:
        return self._element_type

    @property
    def kind(self) -> IRTypeKind:
        return IRTypeKind.ARRAY

    @property
    def is_first_class(self) -> bool:
        return True

    @property
    def is_zero_sized(self) -> bool:
        return self._length == 0 or self._element_type.is_zero_sized

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, ArrayType)
                and self._length == other._length
                and self._element_type == other._element_type)

    def __hash__(self) -> int:
        return hash(("array", self._length, self._element_type))

    def __repr__(self) -> str:
        return f"[{self._length} x {self._element_type}]"


class StructType(IRType):
    """A struct with named or anonymous fields."""
    __slots__ = ("_field_types", "_is_packed", "_name", "_name_frozen")

    def __init__(
        self,
        field_types: Tuple[IRType, ...],
        is_packed: bool = False,
        name: str = "",
    ) -> None:
        object.__setattr__(self, "_field_types", field_types)
        object.__setattr__(self, "_is_packed", is_packed)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_name_frozen", name)

    @property
    def field_types(self) -> Tuple[IRType, ...]:
        return self._field_types

    @property
    def is_packed(self) -> bool:
        return self._is_packed

    @property
    def name(self) -> str:
        return self._name

    @property
    def kind(self) -> IRTypeKind:
        return IRTypeKind.STRUCT

    @property
    def is_first_class(self) -> bool:
        return True

    @property
    def is_zero_sized(self) -> bool:
        return len(self._field_types) == 0

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, StructType)
                and self._field_types == other._field_types
                and self._is_packed == other._is_packed
                and self._name == other._name)

    def __hash__(self) -> int:
        return hash(("struct", self._field_types, self._is_packed, self._name))

    def __repr__(self) -> str:
        fields = ", ".join(str(f) for f in self._field_types)
        prefix = "packed " if self._is_packed else ""
        if self._name:
            return f"{prefix}%\"{self._name}\" = {{ {fields} }}"
        return f"{prefix}{{ {fields} }}"


class IRFunctionType(IRType):
    """A function type: parameter types + return type."""
    __slots__ = ("_param_types", "_return_type", "_is_variadic")

    def __init__(
        self,
        param_types: Tuple[IRType, ...],
        return_type: IRType,
        is_variadic: bool = False,
    ) -> None:
        object.__setattr__(self, "_param_types", param_types)
        object.__setattr__(self, "_return_type", return_type)
        object.__setattr__(self, "_is_variadic", is_variadic)

    @property
    def param_types(self) -> Tuple[IRType, ...]:
        return self._param_types

    @property
    def return_type(self) -> IRType:
        return self._return_type

    @property
    def is_variadic(self) -> bool:
        return self._is_variadic

    @property
    def kind(self) -> IRTypeKind:
        return IRTypeKind.FUNCTION

    @property
    def is_first_class(self) -> bool:
        return False

    @property
    def is_zero_sized(self) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, IRFunctionType)
                and self._param_types == other._param_types
                and self._return_type == other._return_type
                and self._is_variadic == other._is_variadic)

    def __hash__(self) -> int:
        return hash(("func", self._param_types, self._return_type, self._is_variadic))

    def __repr__(self) -> str:
        params = ", ".join(str(p) for p in self._param_types)
        if self._is_variadic:
            params += ", ..."
        return f"{self._return_type} ({params})"


class VectorType(IRType):
    """A fixed-length SIMD vector type."""
    __slots__ = ("_element_count", "_element_type")

    def __init__(self, element_count: int, element_type: IRType) -> None:
        object.__setattr__(self, "_element_count", element_count)
        object.__setattr__(self, "_element_type", element_type)

    @property
    def element_count(self) -> int:
        return self._element_count

    @property
    def element_type(self) -> IRType:
        return self._element_type

    @property
    def kind(self) -> IRTypeKind:
        return IRTypeKind.VECTOR

    @property
    def is_first_class(self) -> bool:
        return True

    @property
    def is_zero_sized(self) -> bool:
        return self._element_count == 0

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, VectorType)
                and self._element_count == other._element_count
                and self._element_type == other._element_type)

    def __hash__(self) -> int:
        return hash(("vec", self._element_count, self._element_type))

    def __repr__(self) -> str:
        return f"<{self._element_count} x {self._element_type}>"


# ══════════════════════════════════════════════════════════════════
# Common Type Singletons
# ══════════════════════════════════════════════════════════════════

IR_VOID = VoidType()
IR_LABEL = LabelType()
IR_METADATA = MetadataType()
IR_TOKEN = TokenType()

IR_I1 = IntegerType(1)
IR_I8 = IntegerType(8)
IR_I16 = IntegerType(16)
IR_I32 = IntegerType(32)
IR_I64 = IntegerType(64)
IR_I128 = IntegerType(128)

IR_F16 = FloatType(16)
IR_F32 = FloatType(32)
IR_F64 = FloatType(64)
IR_F128 = FloatType(128)

IR_PTR = PointerType(IR_I8)

IRVoid = VoidType
IRLabel = LabelType


# ══════════════════════════════════════════════════════════════════
# Type Utilities
# ══════════════════════════════════════════════════════════════════


def int_type(bit_width: int) -> IntegerType:
    """Create an integer type with the given bit width."""
    return IntegerType(bit_width)


def float_type(bit_width: int) -> FloatType:
    """Create a float type with the given bit width."""
    return FloatType(bit_width)


def ptr_type(element_type: IRType) -> PointerType:
    """Create a pointer type pointing to the given element type."""
    return PointerType(element_type)


def array_type(length: int, element_type: IRType) -> ArrayType:
    """Create an array type."""
    return ArrayType(length, element_type)


def struct_type(
    field_types: Tuple[IRType, ...],
    is_packed: bool = False,
    name: str = "",
) -> StructType:
    """Create a struct type."""
    return StructType(field_types, is_packed, name)


def func_type(
    param_types: Tuple[IRType, ...],
    return_type: IRType,
    is_variadic: bool = False,
) -> IRFunctionType:
    """Create a function type."""
    return IRFunctionType(param_types, return_type, is_variadic)


def vec_type(element_count: int, element_type: IRType) -> VectorType:
    """Create a vector type."""
    return VectorType(element_count, element_type)


def get_element_type(ptr_or_array: IRType) -> Optional[IRType]:
    """Get the element type of a pointer or array type."""
    if isinstance(ptr_or_array, PointerType):
        return ptr_or_array.element_type
    if isinstance(ptr_or_array, ArrayType):
        return ptr_or_array.element_type
    return None


def get_pointer_depth(typ: IRType) -> int:
    """Count the nesting depth of pointer types."""
    depth = 0
    current = typ
    while isinstance(current, PointerType):
        depth += 1
        current = current.element_type
    return depth


def is_numeric_type(typ: IRType) -> bool:
    """Check if a type is numeric (integer or float)."""
    return typ.kind in (IRTypeKind.INTEGER, IRTypeKind.FLOAT)


def is_integer_type(typ: IRType) -> bool:
    """Check if a type is an integer type."""
    return typ.kind == IRTypeKind.INTEGER
