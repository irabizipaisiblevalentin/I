"""
Type Diagnostics Engine for the I Programming Language

Professional type error diagnostics with bilingual messages
(Kinyarwanda/English), error codes, expected/actual types,
suggested corrections, and related declarations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

from .types import Type


# ══════════════════════════════════════════════════════════════════
# Type Error Codes
# ══════════════════════════════════════════════════════════════════


class TypeErrorCode(Enum):
    """Unique error codes for all type system diagnostics."""

    # ── Type Mismatch (TYP100-TYP199) ────────────────────────────
    TYP100_TYPE_MISMATCH = auto()
    TYP101_ASSIGNMENT_TYPE_MISMATCH = auto()
    TYP102_RETURN_TYPE_MISMATCH = auto()
    TYP103_ARGUMENT_TYPE_MISMATCH = auto()
    TYP104_INCOMPATIBLE_TYPES = auto()
    TYP105_CANNOT_UNIFY = auto()
    TYP106_INCOMPATIBLE_RETURN = auto()

    # ── Not Callable / Indexable (TYP200-TYP249) ─────────────────
    TYP200_NOT_CALLABLE = auto()
    TYP201_WRONG_ARGUMENT_COUNT = auto()
    TYP202_CANNOT_INDEX = auto()
    TYP203_INDEX_MUST_BE_NUMERIC = auto()
    TYP204_CANNOT_SLICE = auto()
    TYP205_CANNOT_SET_PROPERTY = auto()

    # ── Name Resolution (TYP250-TYP299) ──────────────────────────
    TYP250_UNDEFINED_VARIABLE = auto()
    TYP251_UNDEFINED_FUNCTION = auto()
    TYP252_UNDEFINED_TYPE = auto()
    TYP253_UNDEFINED_MEMBER = auto()
    TYP254_UNDEFINED_METHOD = auto()
    TYP255_UNDEFINED_MODULE = auto()
    TYP256_UNDEFINED_TRAIT = auto()

    # ── Generic Errors (TYP300-TYP349) ───────────────────────────
    TYP300_GENERIC_COUNT_MISMATCH = auto()
    TYP301_GENERIC_CONSTRAINT_VIOLATION = auto()
    TYP302_CANNOT_INFER_GENERIC = auto()
    TYP303_MISSING_GENERIC_ARGUMENT = auto()
    TYP304_CYCLIC_GENERIC = auto()

    # ── Trait / Interface Errors (TYP350-TYP399) ─────────────────
    TYP350_MISSING_TRAIT_METHOD = auto()
    TYP351_TRAIT_METHOD_SIGNATURE_MISMATCH = auto()
    TYP352_NOT_IMPLEMENTED = auto()
    TYP353_CANNOT_IMPLEMENT = auto()
    TYP354_DUPLICATE_TRAIT_IMPL = auto()

    # ── Type Compatibility (TYP400-TYP449) ───────────────────────
    TYP400_INCOMPATIBLE_ASSIGNMENT = auto()
    TYP401_INCOMPATIBLE_ARGUMENT = auto()
    TYP402_INCOMPATIBLE_RETURN_VALUE = auto()
    TYP403_INCOMPATIBLE_COLLECTION = auto()
    TYP404_INCOMPATIBLE_INHERITANCE = auto()
    TYP405_INCOMPATIBLE_MODULE = auto()

    # ── Null / Optional Errors (TYP450-TYP499) ───────────────────
    TYP450_NULLABLE_TYPE_ERROR = auto()
    TYP451_NULL_UNSAFE = auto()
    TYP452_OPTIONAL_NOT_UNWRAPPED = auto()

    # ── Const / Immutable Errors (TYP500-TYP549) ─────────────────
    TYP500_CANNOT_ASSIGN_CONST = auto()
    TYP501_CANNOT_MODIFY_IMMUTABLE = auto()
    TYP502_CONST_REQUIRED = auto()

    # ── Visibility Errors (TYP550-TYP599) ────────────────────────
    TYP550_PRIVATE_ACCESS = auto()
    TYP551_MODULE_NOT_EXPORTED = auto()

    # ── Inference Errors (TYP600-TYP649) ─────────────────────────
    TYP600_CANNOT_INFER_TYPE = auto()
    TYP601_AMBIGUOUS_TYPE = auto()
    TYP602_CIRCULAR_INFERENCE = auto()

    # ── Compile-Time Errors (TYP700-TYP749) ──────────────────────
    TYP700_CONST_EVAL_ERROR = auto()
    TYP701_CONST_ASSERT_FAILED = auto()
    TYP702_DIVISION_BY_ZERO = auto()
    TYP703_OVERFLOW = auto()

    # ── Collection Errors (TYP750-TYP799) ────────────────────────
    TYP750_HOMOGENEOUS_COLLECTION = auto()
    TYP751_KEY_TYPE_MISMATCH = auto()
    TYP752_VALUE_TYPE_MISMATCH = auto()
    TYP753_TUPLE_ARITY_MISMATCH = auto()


# ══════════════════════════════════════════════════════════════════
# Diagnostic Severity
# ══════════════════════════════════════════════════════════════════


class TypeSeverity(Enum):
    """Severity level for type diagnostics."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


# ══════════════════════════════════════════════════════════════════
# Source Location
# ══════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class TypeLocation:
    """Source location for a type diagnostic."""

    file: str = "<input>"
    line: int = 0
    column: int = 0
    end_line: int = 0
    end_column: int = 0

    def __str__(self) -> str:
        if self.line == 0:
            return self.file
        if self.line == self.end_line:
            return f"{self.file}:{self.line}:{self.column}"
        return f"{self.file}:{self.line}:{self.column}-{self.end_line}:{self.end_column}"

    @classmethod
    def from_node(cls, node: Any, file: str = "<input>") -> TypeLocation:
        """Create from an AST node."""
        if hasattr(node, 'location'):
            loc = node.location
            return cls(
                file=getattr(loc, 'file', file),
                line=getattr(loc, 'start_line', 0),
                column=getattr(loc, 'start_column', 0),
                end_line=getattr(loc, 'end_line', 0),
                end_column=getattr(loc, 'end_column', 0),
            )
        if hasattr(node, 'span'):
            s = node.span
            return cls(
                file=file,
                line=getattr(s, 'start_line', 0),
                column=getattr(s, 'start_column', 0),
                end_line=getattr(s, 'end_line', 0),
                end_column=getattr(s, 'end_column', 0),
            )
        return cls(file=file)


# ══════════════════════════════════════════════════════════════════
# Bilingual Message Database
# ══════════════════════════════════════════════════════════════════


_MESSAGES: Dict[TypeErrorCode, Tuple[str, str]] = {
    # Type Mismatch
    TypeErrorCode.TYP100_TYPE_MISMATCH: (
        "Ubwoko butemewe: ndabona '%s' ariko nabonye '%s'",
        "Type mismatch: expected '%s' but got '%s'",
    ),
    TypeErrorCode.TYP101_ASSIGNMENT_TYPE_MISMATCH: (
        "Ubwoko butemewe mu kwiyunga: '%s' ntushobora kwakira '%s'",
        "Assignment type mismatch: '%s' cannot accept '%s'",
    ),
    TypeErrorCode.TYP102_RETURN_TYPE_MISMATCH: (
        "Ubwoko bw'isubiramo butemewe: ndabona '%s' ariko nabonye '%s'",
        "Return type mismatch: expected '%s' but got '%s'",
    ),
    TypeErrorCode.TYP103_ARGUMENT_TYPE_MISMATCH: (
        "Igiparamita %d: ndabona '%s' ariko nabonye '%s'",
        "Argument %d: expected '%s' but got '%s'",
    ),
    TypeErrorCode.TYP104_INCOMPATIBLE_TYPES: (
        "Ubwoko '%s' ntabwo bushobora guhurira na '%s'",
        "Types '%s' and '%s' are not compatible",
    ),
    TypeErrorCode.TYP105_CANNOT_UNIFY: (
        "Ntishobora guhuza ubwoko '%s' na '%s'",
        "Cannot unify types '%s' and '%s'",
    ),
    TypeErrorCode.TYP106_INCOMPATIBLE_RETURN: (
        "Isubiramo ry'umurimo '%s' ntabwo rihuriira",
        "Return value of function '%s' is incompatible",
    ),

    # Not Callable
    TypeErrorCode.TYP200_NOT_CALLABLE: (
        "Ibiri mu '%s' ntabwo bishobora gukoreshwa nka umurimo",
        "Value of type '%s' is not callable",
    ),
    TypeErrorCode.TYP201_WRONG_ARGUMENT_COUNT: (
        "Ibihanya byatanzwe: %d ariko nabonye %d",
        "Argument count: expected %d but got %d",
    ),
    TypeErrorCode.TYP202_CANNOT_INDEX: (
        "Ubwoko '%s' ntabwo bushobora kwibitswa",
        "Type '%s' does not support indexing",
    ),
    TypeErrorCode.TYP203_INDEX_MUST_BE_NUMERIC: (
        "Igice cy'ububiko bugenewe kuba numeric",
        "Index must be numeric",
    ),
    TypeErrorCode.TYP204_CANNOT_SLICE: (
        "Ubwoko '%s' ntabwo bushobora gukarata",
        "Type '%s' does not support slicing",
    ),
    TypeErrorCode.TYP205_CANNOT_SET_PROPERTY: (
        "Ubwoko '%s' ntabwo bushobora guhindura ibintu",
        "Type '%s' does not support property assignment",
    ),

    # Name Resolution
    TypeErrorCode.TYP250_UNDEFINED_VARIABLE: (
        "Ikibeto '%s' ntabwo kibonetse",
        "Undefined variable '%s'",
    ),
    TypeErrorCode.TYP251_UNDEFINED_FUNCTION: (
        "Umurimo '%s' ntabwo ubonetse",
        "Undefined function '%s'",
    ),
    TypeErrorCode.TYP252_UNDEFINED_TYPE: (
        "Ubwoko '%s' ntabwo bwabonetse",
        "Undefined type '%s'",
    ),
    TypeErrorCode.TYP253_UNDEFINED_MEMBER: (
        "Urwego '%s' ntabwo rwafite ubwoko '%s'",
        "Type '%s' has no member '%s'",
    ),
    TypeErrorCode.TYP254_UNDEFINED_METHOD: (
        "Ububiko '%s' ntabwo bwabonetse mu urwego '%s'",
        "Method '%s' not found in type '%s'",
    ),
    TypeErrorCode.TYP255_UNDEFINED_MODULE: (
        "Modile '%s' ntabwo yabonetse",
        "Module '%s' not found",
    ),
    TypeErrorCode.TYP256_UNDEFINED_TRAIT: (
        "Urubingo '%s' ntabwo rwabonetse",
        "Trait '%s' not found",
    ),

    # Generic Errors
    TypeErrorCode.TYP300_GENERIC_COUNT_MISMATCH: (
        "Urwego '%s' rufite ingano y'ubwoko %d ariko nabonye %d",
        "Type '%s' expects %d type argument(s) but got %d",
    ),
    TypeErrorCode.TYP301_GENERIC_CONSTRAINT_VIOLATION: (
        "Ubwoko '%s' ntabwo buhuriira na '%s'",
        "Type '%s' does not satisfy constraint '%s'",
    ),
    TypeErrorCode.TYP302_CANNOT_INFER_GENERIC: (
        "Ntishobora kumenya ubwoko bw'ingano bw'urwego '%s'",
        "Cannot infer generic type parameter for '%s'",
    ),
    TypeErrorCode.TYP303_MISSING_GENERIC_ARGUMENT: (
        "Igice cy'ubwoko '%s' kirabaye",
        "Missing type argument(s) for '%s'",
    ),
    TypeErrorCode.TYP304_CYCLIC_GENERIC: (
        "Ikibazo cy'ubwoko bw'ingano gikomeje",
        "Cyclic generic type constraint",
    ),

    # Trait / Interface Errors
    TypeErrorCode.TYP350_MISSING_TRAIT_METHOD: (
        "Urwego '%s' ntabwo ruhagaze ububiko '%s' bw'urubingo '%s'",
        "Type '%s' does not implement required method '%s' of trait '%s'",
    ),
    TypeErrorCode.TYP351_TRAIT_METHOD_SIGNATURE_MISMATCH: (
        "Ubwoko bw'ububiko '%s' bw'urubingo '%s' ntabwo buhuriira",
        "Method signature '%s' of trait '%s' does not match",
    ),
    TypeErrorCode.TYP352_NOT_IMPLEMENTED: (
        "Urwego '%s' ntabwo ruhagaze urubingo '%s'",
        "Type '%s' does not implement trait '%s'",
    ),
    TypeErrorCode.TYP353_CANNOT_IMPLEMENT: (
        "Ntishobora guhurira urubingo '%s' na urwego '%s'",
        "Cannot implement trait '%s' for type '%s'",
    ),
    TypeErrorCode.TYP354_DUPLICATE_TRAIT_IMPL: (
        "Urubingo '%s' rwahereye kabiri mu urwego '%s'",
        "Trait '%s' is implemented twice for type '%s'",
    ),

    # Type Compatibility
    TypeErrorCode.TYP400_INCOMPATIBLE_ASSIGNMENT: (
        "Ubwoko '%s' ntabwo bushobora kwemererwa mu bwoko '%s'",
        "Type '%s' is not compatible with target type '%s'",
    ),
    TypeErrorCode.TYP401_INCOMPATIBLE_ARGUMENT: (
        "Igiparamita '%s' kirindwa '%s' ariko cyatanzwe '%s'",
        "Parameter '%s' expects '%s' but received '%s'",
    ),
    TypeErrorCode.TYP402_INCOMPATIBLE_RETURN_VALUE: (
        "Agaciro k'isubiramo '%s' ntabwo kahurira",
        "Return value type '%s' is not compatible",
    ),
    TypeErrorCode.TYP403_INCOMPATIBLE_COLLECTION: (
        "Ibintu biri mu urutonde ntabwo birihurira: '%s' na '%s'",
        "Collection elements are incompatible: '%s' and '%s'",
    ),
    TypeErrorCode.TYP404_INCOMPATIBLE_INHERITANCE: (
        "Urwego '%s' ntabwo rushobora kugira '%s' nka data",
        "Type '%s' cannot inherit from '%s'",
    ),
    TypeErrorCode.TYP405_INCOMPATIBLE_MODULE: (
        "Modile '%s' ntabwo ihurira na '%s'",
        "Module '%s' is not compatible with '%s'",
    ),

    # Null / Optional Errors
    TypeErrorCode.TYP450_NULLABLE_TYPE_ERROR: (
        "Ubwoko '%s' bushobora kuba null ariko ntabwo buhagaze",
        "Type '%s' may be null but is not checked",
    ),
    TypeErrorCode.TYP451_NULL_UNSAFE: (
        "Kugereranya na null nta bwemezo bw'amahitamo",
        "Null access is not safe without null check",
    ),
    TypeErrorCode.TYP452_OPTIONAL_NOT_UNWRAPPED: (
        "Ubwoko '%s' ni optional ariko ntabwo bwafunguwe",
        "Type '%s' is optional but not unwrapped",
    ),

    # Const / Immutable Errors
    TypeErrorCode.TYP500_CANNOT_ASSIGN_CONST: (
        "Ikibeto '%s' ni constant — ntabwo cyahinduka",
        "Variable '%s' is constant and cannot be reassigned",
    ),
    TypeErrorCode.TYP501_CANNOT_MODIFY_IMMUTABLE: (
        "Ibiri mu '%s' ntabwo birashobora guhinduka",
        "Contents of '%s' cannot be modified",
    ),
    TypeErrorCode.TYP502_CONST_REQUIRED: (
        "Agaciro ka constant karabaye ariko '%s' ntagwo",
        "Constant value required but got '%s'",
    ),

    # Visibility Errors
    TypeErrorCode.TYP550_PRIVATE_ACCESS: (
        "Ikibeto '%s' ni iri mu buryo bwihariye",
        "Symbol '%s' is private and cannot be accessed here",
    ),
    TypeErrorCode.TYP551_MODULE_NOT_EXPORTED: (
        "Ikibeto '%s' ntabwo kitangwa mu modile '%s'",
        "Symbol '%s' is not exported from module '%s'",
    ),

    # Inference Errors
    TypeErrorCode.TYP600_CANNOT_INFER_TYPE: (
        "Ntishobora kumenya ubwoko bw'ikibeto '%s'",
        "Cannot infer type of '%s'",
    ),
    TypeErrorCode.TYP601_AMBIGUOUS_TYPE: (
        "Ubwoko '%s' burashidisha",
        "Type '%s' is ambiguous",
    ),
    TypeErrorCode.TYP602_CIRCULAR_INFERENCE: (
        "Ikibazo cy'ubwoko gikomeje mu '%s'",
        "Circular type inference in '%s'",
    ),

    # Compile-Time Errors
    TypeErrorCode.TYP700_CONST_EVAL_ERROR: (
        "Ntishobora kubara agaciro ka constant: %s",
        "Cannot evaluate compile-time constant: %s",
    ),
    TypeErrorCode.TYP701_CONST_ASSERT_FAILED: (
        "Ikibazo cy'ubwoko ka constant gitumye",
        "Compile-time assertion failed",
    ),
    TypeErrorCode.TYP702_DIVISION_BY_ZERO: (
        "Kugabanya kuri zero mu gihe c'ubwoko",
        "Division by zero in compile-time evaluation",
    ),
    TypeErrorCode.TYP703_OVERFLOW: (
        "Ibika ry'agaciro ka constant irereye",
        "Compile-time constant overflow",
    ),

    # Collection Errors
    TypeErrorCode.TYP750_HOMOGENEOUS_COLLECTION: (
        "Ubwoko bw'ibintu biri mu urutonde ntabwo buhurira: '%s' na '%s'",
        "Collection elements must have the same type: got '%s' and '%s'",
    ),
    TypeErrorCode.TYP751_KEY_TYPE_MISMATCH: (
        "Ubwoko bw'inkono '%s' ntabwo buhurira na '%s'",
        "Key type '%s' does not match expected '%s'",
    ),
    TypeErrorCode.TYP752_VALUE_TYPE_MISMATCH: (
        "Ubwoko bw'agaciro '%s' ntabwo buhurira na '%s'",
        "Value type '%s' does not match expected '%s'",
    ),
    TypeErrorCode.TYP753_TUPLE_ARITY_MISMATCH: (
        "Ikigereranyo cy'ubwoko: ndabona %d ariko nabonye %d",
        "Tuple arity mismatch: expected %d but got %d",
    ),
}


def get_bilingual_message(code: TypeErrorCode, *args: Any) -> Tuple[str, str]:
    """Get bilingual message for an error code with optional format args."""
    template = _MESSAGES.get(code, ("Ikosa ryateye akere", "Unknown type error"))
    if args:
        try:
            return (template[0] % args, template[1] % args)
        except (TypeError, ValueError):
            return template
    return template


# ══════════════════════════════════════════════════════════════════
# Type Diagnostic
# ══════════════════════════════════════════════════════════════════


@dataclass
class TypeDiagnostic:
    """A single type system diagnostic."""

    code: TypeErrorCode
    severity: TypeSeverity
    location: TypeLocation
    message_rw: str
    message_en: str
    expected_type: Optional[str] = None
    actual_type: Optional[str] = None
    related_symbols: List[str] = field(default_factory=list)
    suggested_fix: Optional[str] = None
    reference_doc: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        loc = str(self.location) if self.location.line > 0 else ""
        prefix = f"[{self.severity.value.upper()}]"
        location_part = f" {loc}" if loc else ""
        types_part = ""
        if self.expected_type and self.actual_type:
            types_part = f" ({self.expected_type} vs {self.actual_type})"
        return f"{prefix} {self.code.name}{location_part}: {self.message_en}{types_part}"

    def bilingual_str(self) -> str:
        """Full bilingual representation."""
        loc = str(self.location) if self.location.line > 0 else ""
        location_part = f"\n  Location: {loc}" if loc else ""
        expected = ""
        if self.expected_type:
            expected = f"\n  Expected: {self.expected_type}"
        actual = ""
        if self.actual_type:
            actual = f"\n  Actual:   {self.actual_type}"
        related = ""
        if self.related_symbols:
            related = f"\n  Related: {', '.join(self.related_symbols)}"
        fix = ""
        if self.suggested_fix:
            fix = f"\n  Fix: {self.suggested_fix}"
        ref = ""
        if self.reference_doc:
            ref = f"\n  Reference: {self.reference_doc}"
        return (
            f"[{self.severity.value.upper()}] {self.code.name}\n"
            f"  Kinyarwanda: {self.message_rw}\n"
            f"  English:     {self.message_en}"
            f"{location_part}{expected}{actual}{related}{fix}{ref}"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        d: Dict[str, Any] = {
            'code': self.code.name,
            'severity': self.severity.value,
            'message_en': self.message_en,
            'message_rw': self.message_rw,
        }
        if self.location.line > 0:
            d['location'] = {
                'file': self.location.file,
                'line': self.location.line,
                'column': self.location.column,
            }
        if self.expected_type:
            d['expected_type'] = self.expected_type
        if self.actual_type:
            d['actual_type'] = self.actual_type
        if self.related_symbols:
            d['related_symbols'] = self.related_symbols
        if self.suggested_fix:
            d['suggested_fix'] = self.suggested_fix
        return d


# ══════════════════════════════════════════════════════════════════
# Type Diagnostics Collection
# ══════════════════════════════════════════════════════════════════


class TypeDiagnostics:
    """
    Collects type diagnostics during type checking.

    Provides methods for emitting errors, warnings, info, and hints
    with full support for bilingual messages, suggested fixes,
    and related declarations.
    """

    def __init__(self) -> None:
        self._diagnostics: List[TypeDiagnostic] = []
        self._max_errors: int = 100

    @property
    def diagnostics(self) -> List[TypeDiagnostic]:
        return list(self._diagnostics)

    @property
    def errors(self) -> List[TypeDiagnostic]:
        return [d for d in self._diagnostics if d.severity == TypeSeverity.ERROR]

    @property
    def warnings(self) -> List[TypeDiagnostic]:
        return [d for d in self._diagnostics if d.severity == TypeSeverity.WARNING]

    @property
    def infos(self) -> List[TypeDiagnostic]:
        return [d for d in self._diagnostics if d.severity == TypeSeverity.INFO]

    @property
    def has_errors(self) -> bool:
        return any(d.severity == TypeSeverity.ERROR for d in self._diagnostics)

    @property
    def has_warnings(self) -> bool:
        return any(d.severity == TypeSeverity.WARNING for d in self._diagnostics)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    @property
    def should_abort(self) -> bool:
        return self.error_count >= self._max_errors

    def _make_diagnostic(
        self,
        code: TypeErrorCode,
        severity: TypeSeverity,
        location: TypeLocation,
        args: Tuple[Any, ...] = (),
        expected_type: Optional[Type] = None,
        actual_type: Optional[Type] = None,
        related_symbols: Optional[List[str]] = None,
        suggested_fix: Optional[str] = None,
        reference_doc: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> TypeDiagnostic:
        msg_rw, msg_en = get_bilingual_message(code, *args)
        return TypeDiagnostic(
            code=code,
            severity=severity,
            location=location,
            message_rw=msg_rw,
            message_en=msg_en,
            expected_type=str(expected_type) if expected_type else None,
            actual_type=str(actual_type) if actual_type else None,
            related_symbols=related_symbols or [],
            suggested_fix=suggested_fix,
            reference_doc=reference_doc,
            context=context or {},
        )

    def error(
        self,
        code: TypeErrorCode,
        location: TypeLocation,
        *args: Any,
        expected_type: Optional[Type] = None,
        actual_type: Optional[Type] = None,
        **kwargs: Any,
    ) -> TypeDiagnostic:
        """Emit an error diagnostic."""
        diag = self._make_diagnostic(
            code, TypeSeverity.ERROR, location, args,
            expected_type=expected_type,
            actual_type=actual_type,
            **kwargs,
        )
        self._diagnostics.append(diag)
        return diag

    def warning(
        self,
        code: TypeErrorCode,
        location: TypeLocation,
        *args: Any,
        expected_type: Optional[Type] = None,
        actual_type: Optional[Type] = None,
        **kwargs: Any,
    ) -> TypeDiagnostic:
        """Emit a warning diagnostic."""
        diag = self._make_diagnostic(
            code, TypeSeverity.WARNING, location, args,
            expected_type=expected_type,
            actual_type=actual_type,
            **kwargs,
        )
        self._diagnostics.append(diag)
        return diag

    def info(
        self,
        code: TypeErrorCode,
        location: TypeLocation,
        *args: Any,
        **kwargs: Any,
    ) -> TypeDiagnostic:
        """Emit an info diagnostic."""
        diag = self._make_diagnostic(
            code, TypeSeverity.INFO, location, args, **kwargs,
        )
        self._diagnostics.append(diag)
        return diag

    def hint(
        self,
        code: TypeErrorCode,
        location: TypeLocation,
        *args: Any,
        **kwargs: Any,
    ) -> TypeDiagnostic:
        """Emit a hint diagnostic."""
        diag = self._make_diagnostic(
            code, TypeSeverity.HINT, location, args, **kwargs,
        )
        self._diagnostics.append(diag)
        return diag

    def type_mismatch(
        self,
        location: TypeLocation,
        expected: Type,
        actual: Type,
        related: Optional[List[str]] = None,
        fix: Optional[str] = None,
    ) -> TypeDiagnostic:
        """Convenience: emit a type mismatch error."""
        return self.error(
            TypeErrorCode.TYP100_TYPE_MISMATCH,
            location,
            str(expected), str(actual),
            expected_type=expected,
            actual_type=actual,
            related_symbols=related,
            suggested_fix=fix,
        )

    def not_callable(
        self,
        location: TypeLocation,
        typ: Type,
    ) -> TypeDiagnostic:
        """Convenience: emit a not-callable error."""
        return self.error(
            TypeErrorCode.TYP200_NOT_CALLABLE,
            location,
            str(typ),
            actual_type=typ,
        )

    def wrong_arg_count(
        self,
        location: TypeLocation,
        expected: int,
        actual: int,
    ) -> TypeDiagnostic:
        """Convenience: emit wrong argument count error."""
        return self.error(
            TypeErrorCode.TYP201_WRONG_ARGUMENT_COUNT,
            location,
            expected, actual,
        )

    def undefined_variable(
        self,
        location: TypeLocation,
        name: str,
    ) -> TypeDiagnostic:
        """Convenience: emit undefined variable error."""
        return self.error(
            TypeErrorCode.TYP250_UNDEFINED_VARIABLE,
            location,
            name,
        )

    def undefined_member(
        self,
        location: TypeLocation,
        type_name: str,
        member: str,
    ) -> TypeDiagnostic:
        """Convenience: emit undefined member error."""
        return self.error(
            TypeErrorCode.TYP253_UNDEFINED_MEMBER,
            location,
            type_name, member,
            related_symbols=[type_name],
        )

    def clear(self) -> None:
        """Clear all diagnostics."""
        self._diagnostics.clear()

    def filter_by_severity(self, severity: TypeSeverity) -> List[TypeDiagnostic]:
        """Filter diagnostics by severity level."""
        return [d for d in self._diagnostics if d.severity == severity]

    def filter_by_code(self, code: TypeErrorCode) -> List[TypeDiagnostic]:
        """Filter diagnostics by error code."""
        return [d for d in self._diagnostics if d.code == code]

    def filter_by_file(self, file: str) -> List[TypeDiagnostic]:
        """Filter diagnostics by source file."""
        return [d for d in self._diagnostics if d.location.file == file]

    def format_all(self, bilingual: bool = False) -> str:
        """Format all diagnostics."""
        lines = []
        for d in self._diagnostics:
            if bilingual:
                lines.append(d.bilingual_str())
            else:
                lines.append(str(d))
        return "\n\n".join(lines)

    def format_summary(self) -> str:
        """Format a summary of all diagnostics."""
        parts = []
        if self.error_count:
            parts.append(f"{self.error_count} error(s)")
        if self.warning_count:
            parts.append(f"{self.warning_count} warning(s)")
        info_count = len(self.infos)
        if info_count:
            parts.append(f"{info_count} info(s)")
        if not parts:
            return "No diagnostics"
        return ", ".join(parts)

    def to_json(self) -> List[Dict[str, Any]]:
        """Serialize all diagnostics to JSON-compatible dicts."""
        return [d.to_dict() for d in self._diagnostics]

    def generate_suggestion(self, diag: TypeDiagnostic) -> Optional[str]:
        """Generate a suggested fix for a diagnostic."""
        if diag.suggested_fix:
            return diag.suggested_fix
        if diag.code == TypeErrorCode.TYP101_ASSIGNMENT_TYPE_MISMATCH:
            if diag.expected_type and diag.actual_type:
                return f"Cast '{diag.actual_type}' to '{diag.expected_type}'"
        if diag.code == TypeErrorCode.TYP200_NOT_CALLABLE:
            return "Add parentheses to call this function"
        if diag.code == TypeErrorCode.TYP250_UNDEFINED_VARIABLE:
            return "Check spelling or add a declaration"
        if diag.code == TypeErrorCode.TYP500_CANNOT_ASSIGN_CONST:
            return "Use 'nibyo' (var) instead of 'ni' (val/let)"
        return None

    @property
    def diagnostic_count(self) -> int:
        """Total number of diagnostics."""
        return len(self._diagnostics)
