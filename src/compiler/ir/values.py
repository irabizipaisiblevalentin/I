"""
IR Values and Constants

All SSA values in the IR: constants, function arguments, basic block references,
instruction results, global variables, and function references.
Every value has a type and a unique name.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Optional, TYPE_CHECKING

from .types import IRType, IR_I1, IR_I8, IR_I32, IR_I64, IR_F32, IR_F64

if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from .instructions import Instruction
    from .basic_block import BasicBlock
    from .function import IRFunction
    from .metadata import Metadata


# ══════════════════════════════════════════════════════════════════
# Value Kinds
# ══════════════════════════════════════════════════════════════════


class ValueKind(Enum):
    """Classification of IR values."""
    CONSTANT = auto()
    ARGUMENT = auto()
    INSTRUCTION = auto()
    BASIC_BLOCK = auto()
    FUNCTION = auto()
    GLOBAL_VARIABLE = auto()
    UNDEFINED = auto()
    POISON = auto()
    METADATA = auto()


# ══════════════════════════════════════════════════════════════════
# Value (Abstract Base)
# ══════════════════════════════════════════════════════════════════


class Value(ABC):
    """Base class for all SSA values in the IR."""
    __slots__ = ("_name", "_type", "_uses")

    def __init__(self, name: str, typ: IRType) -> None:
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_type", typ)
        object.__setattr__(self, "_uses", [])

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        object.__setattr__(self, "_name", value)

    @property
    def type(self) -> IRType:
        return self._type

    @property
    def kind(self) -> ValueKind:
        return self._value_kind()

    @abstractmethod
    def _value_kind(self) -> ValueKind:
        ...

    @property
    def uses(self) -> List[Instruction]:
        """Instructions that use this value."""
        return self._uses

    def add_use(self, instruction: Instruction) -> None:
        """Record that an instruction uses this value."""
        self._uses.append(instruction)

    def remove_use(self, instruction: Instruction) -> None:
        """Remove a use record."""
        if instruction in self._uses:
            self._uses.remove(instruction)

    @property
    def use_count(self) -> int:
        return len(self._uses)

    @property
    def has_uses(self) -> bool:
        return len(self._uses) > 0

    def __repr__(self) -> str:
        return f"{self._name}: {self._type}"


# ══════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════


class Constant(Value):
    """A compile-time constant value."""
    __slots__ = ()

    def _value_kind(self) -> ValueKind:
        return ValueKind.CONSTANT


class IntConstant(Constant):
    """An integer constant."""
    __slots__ = ("_value",)

    def __init__(self, value: int, typ: Optional[IRType] = None) -> None:
        if typ is None:
            typ = IR_I64
        super().__init__(str(value), typ)
        object.__setattr__(self, "_value", value)

    @property
    def value(self) -> int:
        return self._value

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, IntConstant)
                and self._value == other._value
                and self._type == other._type)

    def __hash__(self) -> int:
        return hash(("int_const", self._value, self._type))

    def __repr__(self) -> str:
        return str(self._value)


class FloatConstant(Constant):
    """A floating-point constant."""
    __slots__ = ("_value",)

    def __init__(self, value: float, typ: Optional[IRType] = None) -> None:
        if typ is None:
            typ = IR_F64
        super().__init__(str(value), typ)
        object.__setattr__(self, "_value", value)

    @property
    def value(self) -> float:
        return self._value

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, FloatConstant)
                and self._value == other._value
                and self._type == other._type)

    def __hash__(self) -> int:
        return hash(("float_const", self._value, self._type))

    def __repr__(self) -> str:
        return str(self._value)


class BoolConstant(Constant):
    """A boolean constant (i1)."""
    __slots__ = ("_value",)

    def __init__(self, value: bool) -> None:
        super().__init__(str(value).lower(), IR_I1)
        object.__setattr__(self, "_value", value)

    @property
    def value(self) -> bool:
        return self._value

    def __eq__(self, other: object) -> bool:
        return isinstance(other, BoolConstant) and self._value == other._value

    def __hash__(self) -> int:
        return hash(("bool_const", self._value))

    def __repr__(self) -> str:
        return "true" if self._value else "false"


class StringConstant(Constant):
    """A string constant (array of i8)."""
    __slots__ = ("_value", "_bytes_val")

    def __init__(self, value: str) -> None:
        from .types import ArrayType
        self._bytes_val = value.encode("utf-8")
        byte_arr = ArrayType(len(self._bytes_val), IR_I8)
        super().__init__(f'"{value}"', byte_arr)
        object.__setattr__(self, "_value", value)

    @property
    def value(self) -> str:
        return self._value

    @property
    def byte_data(self) -> bytes:
        return self._bytes_val

    def __eq__(self, other: object) -> bool:
        return isinstance(other, StringConstant) and self._value == other._value

    def __hash__(self) -> int:
        return hash(("str_const", self._value))

    def __repr__(self) -> str:
        return f'"{self._value}"'


class NullConstant(Constant):
    """A null pointer constant."""
    __slots__ = ()

    def __init__(self, ptr_type: Optional[IRType] = None) -> None:
        from .types import PointerType, IR_I8
        if ptr_type is None:
            ptr_type = PointerType(IR_I8)
        super().__init__("null", ptr_type)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NullConstant) and self._type == other._type

    def __hash__(self) -> int:
        return hash(("null", self._type))

    def __repr__(self) -> str:
        return "null"


class UndefinedConstant(Constant):
    """An undef constant — value is unspecified."""
    __slots__ = ()

    def __init__(self, typ: IRType) -> None:
        super().__init__("undef", typ)

    def _value_kind(self) -> ValueKind:
        return ValueKind.UNDEFINED

    def __eq__(self, other: object) -> bool:
        return isinstance(other, UndefinedConstant) and self._type == other._type

    def __hash__(self) -> int:
        return hash(("undef", self._type))

    def __repr__(self) -> str:
        return f"undef {self._type}"


class PoisonConstant(Constant):
    """A poison constant — using it is undefined behavior."""
    __slots__ = ()

    def __init__(self, typ: IRType) -> None:
        super().__init__("poison", typ)

    def _value_kind(self) -> ValueKind:
        return ValueKind.POISON

    def __eq__(self, other: object) -> bool:
        return isinstance(other, PoisonConstant) and self._type == other._type

    def __hash__(self) -> int:
        return hash(("poison", self._type))

    def __repr__(self) -> str:
        return f"poison {self._type}"


class ZeroConstant(Constant):
    """A zero-initialized aggregate constant."""
    __slots__ = ()

    def __init__(self, typ: IRType) -> None:
        super().__init__("zeroinitializer", typ)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ZeroConstant) and self._type == other._type

    def __hash__(self) -> int:
        return hash(("zero_init", self._type))

    def __repr__(self) -> str:
        return "zeroinitializer"


class AggregateConstant(Constant):
    """An aggregate constant (struct/array)."""
    __slots__ = ("_elements",)

    def __init__(self, typ: IRType, elements: Tuple[Constant, ...]) -> None:
        super().__init__("aggregate", typ)
        object.__setattr__(self, "_elements", elements)

    @property
    def elements(self) -> Tuple[Constant, ...]:
        return self._elements

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, AggregateConstant)
                and self._elements == other._elements
                and self._type == other._type)

    def __hash__(self) -> int:
        return hash(("agg_const", self._elements, self._type))

    def __repr__(self) -> str:
        elems = ", ".join(repr(e) for e in self._elements)
        return f"[{elems}]"


# ══════════════════════════════════════════════════════════════════
# Argument
# ══════════════════════════════════════════════════════════════════


class Argument(Value):
    """A function argument."""
    __slots__ = ("_index", "_attributes", "_parent")

    def __init__(self, name: str, typ: IRType, index: int = 0) -> None:
        super().__init__(name, typ)
        object.__setattr__(self, "_index", index)
        object.__setattr__(self, "_attributes", [])
        object.__setattr__(self, "_parent", None)

    @property
    def index(self) -> int:
        return self._index

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, func) -> None:
        object.__setattr__(self, "_parent", func)

    def _value_kind(self) -> ValueKind:
        return ValueKind.ARGUMENT


# ══════════════════════════════════════════════════════════════════
# Global Variable
# ══════════════════════════════════════════════════════════════════


class GlobalVariable(Value):
    """A global variable."""
    __slots__ = ("_value_type", "_is_constant", "_initializer", "_linkage")

    def __init__(
        self,
        name: str,
        value_type: IRType,
        is_constant: bool = False,
        initializer: Optional[Constant] = None,
        linkage: str = "internal",
    ) -> None:
        from .types import PointerType
        super().__init__(name, PointerType(value_type))
        object.__setattr__(self, "_value_type", value_type)
        object.__setattr__(self, "_is_constant", is_constant)
        object.__setattr__(self, "_initializer", initializer)
        object.__setattr__(self, "_linkage", linkage)

    @property
    def value_type(self) -> IRType:
        return self._value_type

    @property
    def is_constant(self) -> bool:
        return self._is_constant

    @property
    def initializer(self) -> Optional[Constant]:
        return self._initializer

    @property
    def linkage(self) -> str:
        return self._linkage

    def _value_kind(self) -> ValueKind:
        return ValueKind.GLOBAL_VARIABLE


# ══════════════════════════════════════════════════════════════════
# Value Utilities
# ══════════════════════════════════════════════════════════════════

from typing import Tuple


def make_int_constant(value: int, bit_width: int = 64) -> IntConstant:
    """Create an integer constant with the specified bit width."""
    from .types import IntegerType
    return IntConstant(value, IntegerType(bit_width))


def make_float_constant(value: float, bit_width: int = 64) -> FloatConstant:
    """Create a float constant with the specified bit width."""
    from .types import FloatType
    return FloatConstant(value, FloatType(bit_width))


def make_bool_constant(value: bool) -> BoolConstant:
    """Create a boolean constant."""
    return BoolConstant(value)


def make_string_constant(value: str) -> StringConstant:
    """Create a string constant."""
    return StringConstant(value)


def make_null_constant(ptr_type: Optional[IRType] = None) -> NullConstant:
    """Create a null pointer constant."""
    return NullConstant(ptr_type)


def is_constant(value: Value) -> bool:
    """Check if a value is a compile-time constant."""
    return isinstance(value, Constant)


def is_terminator(value: Value) -> bool:
    """Check if a value is a terminator instruction."""
    from .instructions import TerminatorInst
    return isinstance(value, TerminatorInst)
