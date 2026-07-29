"""
IR Attributes

Function, parameter, and module-level attributes that influence
optimization, calling conventions, and code generation.
"""
from __future__ import annotations

from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Set


# ══════════════════════════════════════════════════════════════════
# Attribute Kinds
# ══════════════════════════════════════════════════════════════════


class AttrKind(Enum):
    """Classification of IR attributes."""
    # Function attributes
    NORETURN = auto()
    NO_UNWIND = auto()
    READNONE = auto()
    READONLY = auto()
    WRITEONLY = auto()
    NOALIAS = auto()
    NOCAPTURE = auto()
    NONNULL = auto()
    NOSYNC = auto()
    WILLRETURN = auto()
    STRICTFP = auto()
    CONVERGENT = auto()
    NODEFAULT = auto()
    OPTNONE = auto()
    OPTSIZE = auto()
    SIZEZERO = auto()
    MINSIZE = auto()
    SSP = auto()
    SSPREQ = auto()
    NORECURSE = auto()
    INLINE_HINT = auto()
    ALWAYS_INLINE = auto()
    NO_INLINE = auto()
    # Parameter attributes
    SIGNEXT = auto()
    ZEROEXT = auto()
    INREG = auto()
    BYVAL = auto()
    STRUCTRET = auto()
    FPRET = auto()
    NOALIAS_ATTR = auto()
    NOCAPTURE_ATTR = auto()
    NONNULL_ATTR = auto()
    DEREFERENCEABLE = auto()
    DEREFERENCEABLE_OR_NULL = auto()
    # Calling conventions
    CCC = auto()
    FASTCC = auto()
    COLDCC = auto()
    # Custom
    CUSTOM = auto()


# ══════════════════════════════════════════════════════════════════
# Attribute
# ══════════════════════════════════════════════════════════════════


class Attribute:
    """An IR attribute with optional value."""
    __slots__ = ("_kind", "_value")

    def __init__(self, kind: AttrKind, value: Optional[str] = None) -> None:
        object.__setattr__(self, "_kind", kind)
        object.__setattr__(self, "_value", value)

    @property
    def kind(self) -> AttrKind:
        return self._kind

    @property
    def value(self) -> Optional[str]:
        return self._value

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, Attribute)
                and self._kind == other._kind
                and self._value == other._value)

    def __hash__(self) -> int:
        return hash(("attr", self._kind, self._value))

    def __repr__(self) -> str:
        if self._value:
            return f"{self._kind.name}({self._value})"
        return self._kind.name


# ══════════════════════════════════════════════════════════════════
# Attribute Sets
# ══════════════════════════════════════════════════════════════════


class AttributeSet:
    """A set of attributes for a function or parameter."""
    __slots__ = ("_attributes",)

    def __init__(self) -> None:
        object.__setattr__(self, "_attributes", set())

    def add(self, attr: Attribute) -> None:
        """Add an attribute."""
        self._attributes.add(attr)

    def add_kind(self, kind: AttrKind, value: Optional[str] = None) -> None:
        """Add an attribute by kind."""
        self._attributes.add(Attribute(kind, value))

    def has(self, kind: AttrKind) -> bool:
        """Check if an attribute of this kind exists."""
        return any(a.kind == kind for a in self._attributes)

    def remove(self, kind: AttrKind) -> None:
        """Remove all attributes of this kind."""
        self._attributes = {a for a in self._attributes if a.kind != kind}

    @property
    def is_empty(self) -> bool:
        return len(self._attributes) == 0

    def __len__(self) -> int:
        return len(self._attributes)

    def __iter__(self):
        return iter(self._attributes)

    def __contains__(self, kind: AttrKind) -> bool:
        return self.has(kind)

    def __repr__(self) -> str:
        attrs = " ".join(repr(a) for a in sorted(self._attributes, key=lambda a: a.kind.name))
        return f"[{attrs}]"


# ══════════════════════════════════════════════════════════════════
# Attribute Factory Functions
# ══════════════════════════════════════════════════════════════════


def attr_noreturn() -> Attribute:
    return Attribute(AttrKind.NORETURN)


def attr_no_unwind() -> Attribute:
    return Attribute(AttrKind.NO_UNWIND)


def attr_readnone() -> Attribute:
    return Attribute(AttrKind.READNONE)


def attr_readonly() -> Attribute:
    return Attribute(AttrKind.READONLY)


def attr_writeonly() -> Attribute:
    return Attribute(AttrKind.WRITEONLY)


def attr_noalias() -> Attribute:
    return Attribute(AttrKind.NOALIAS)


def attr_nocapture() -> Attribute:
    return Attribute(AttrKind.NOCAPTURE)


def attr_nonnull() -> Attribute:
    return Attribute(AttrKind.NONNULL)


def attr_always_inline() -> Attribute:
    return Attribute(AttrKind.ALWAYS_INLINE)


def attr_no_inline() -> Attribute:
    return Attribute(AttrKind.NO_INLINE)


def attr_inline_hint() -> Attribute:
    return Attribute(AttrKind.INLINE_HINT)


def attr_optnone() -> Attribute:
    return Attribute(AttrKind.OPTNONE)


def attr_signext() -> Attribute:
    return Attribute(AttrKind.SIGNEXT)


def attr_zeroext() -> Attribute:
    return Attribute(AttrKind.ZEROEXT)


def attr_dereferenceable(size: int) -> Attribute:
    return Attribute(AttrKind.DEREFERENCEABLE, str(size))


def attr_dereferenceable_or_null(size: int) -> Attribute:
    return Attribute(AttrKind.DEREFERENCEABLE_OR_NULL, str(size))
