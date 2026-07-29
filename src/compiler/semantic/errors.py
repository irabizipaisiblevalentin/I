"""
Semantic Analysis Error System

Professional diagnostics with bilingual (Kinyarwanda/English) messages,
unique error codes, source locations, suggested fixes, and related symbols.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple


class SemanticErrorCode(Enum):
    """Unique error codes for all semantic diagnostics."""

    # ── Declaration Errors (SEM100-SEM199) ──────────────────────
    SEM100_DUPLICATE_VARIABLE = auto()
    SEM101_DUPLICATE_FUNCTION = auto()
    SEM102_DUPLICATE_PARAMETER = auto()
    SEM103_DUPLICATE_CLASS = auto()
    SEM104_DUPLICATE_METHOD = auto()
    SEM105_DUPLICATE_MODULE = auto()
    SEM106_DUPLICATE_STRUCT = auto()
    SEM107_DUPLICATE_ENUM = auto()
    SEM108_DUPLICATE_TRAIT = auto()
    SEM109_DUPLICATE_INTERFACE = auto()
    SEM110_RESERVED_KEYWORD = auto()
    SEM111_ILLEGAL_IDENTIFIER = auto()

    # ── Name Resolution Errors (SEM200-SEM299) ─────────────────
    SEM200_UNDEFINED_VARIABLE = auto()
    SEM201_UNDEFINED_FUNCTION = auto()
    SEM202_UNDEFINED_CLASS = auto()
    SEM203_UNDEFINED_MODULE = auto()
    SEM204_UNDEFINED_TYPE = auto()
    SEM205_UNDEFINED_STRUCT = auto()
    SEM206_UNDEFINED_ENUM = auto()
    SEM207_UNDEFINED_METHOD = auto()
    SEM208_UNDEFINED_TRAIT = auto()
    SEM209_UNDEFINED_INTERFACE = auto()

    # ── Type Errors (SEM300-SEM399) ─────────────────────────────
    SEM300_TYPE_MISMATCH = auto()
    SEM301_NOT_CALLABLE = auto()
    SEM302_ARGUMENT_COUNT_MISMATCH = auto()
    SEM303_MISSING_RETURN = auto()
    SEM304_RETURN_OUTSIDE_FUNCTION = auto()
    SEM305_BREAK_OUTSIDE_LOOP = auto()
    SEM306_CONTINUE_OUTSIDE_LOOP = auto()
    SEM307_CANNOT_INDEX = auto()
    SEM308_INDEX_MUST_BE_NUMERIC = auto()
    SEM309_CANNOT_SET_PROPERTY = auto()
    SEM310_NO_SUCH_PROPERTY = auto()

    # ── Import/Export Errors (SEM400-SEM499) ────────────────────
    SEM400_MODULE_NOT_FOUND = auto()
    SEM401_DUPLICATE_IMPORT = auto()
    SEM402_CIRCULAR_IMPORT = auto()
    SEM403_IMPORT_NOT_PUBLIC = auto()
    SEM404_EXPORT_NOT_FOUND = auto()
    SEM405_PRIVATE_ACCESS = auto()

    # ── Constant Evaluation Errors (SEM500-SEM599) ─────────────
    SEM500_NOT_A_CONSTANT = auto()
    SEM501_DIVISION_BY_ZERO = auto()
    SEM502_CONST_TYPE_MISMATCH = auto()

    # ── Control Flow Errors (SEM600-SEM699) ─────────────────────
    SEM600_UNREACHABLE_CODE = auto()
    SEM601_MISSING_RETURN_PATH = auto()
    SEM602_UNINITIALIZED_VARIABLE = auto()

    # ── Visibility Errors (SEM700-SEM799) ──────────────────────
    SEM700_VISIBILITY_RESTRICTED = auto()
    SEM701_MODULE_NOT_EXPORTED = auto()
    SEM702_SYMBOL_NOT_VISIBLE = auto()


class SemanticSeverity(Enum):
    """Severity level for diagnostics."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# ── Bilingual Message Database ──────────────────────────────────────

_MESSAGES: Dict[SemanticErrorCode, Tuple[str, str]] = {
    # (Kinyarwanda, English)
    # Declaration Errors
    SemanticErrorCode.SEM100_DUPLICATE_VARIABLE: (
        "Ikibeto '%s' cyateye akere mu bwoko bwinewe",
        "Duplicate variable '%s' in the same scope",
    ),
    SemanticErrorCode.SEM101_DUPLICATE_FUNCTION: (
        "Umurimo '%s' uhereye mu bwoko bwinewe",
        "Duplicate function '%s' in the same scope",
    ),
    SemanticErrorCode.SEM102_DUPLICATE_PARAMETER: (
        "Igiparamita '%s' kabiri mu murimo '%s'",
        "Duplicate parameter '%s' in function '%s'",
    ),
    SemanticErrorCode.SEM103_DUPLICATE_CLASS: (
        "Urwego '%s' rwararangira mu bwoko bwinewe",
        "Duplicate class '%s' in the same scope",
    ),
    SemanticErrorCode.SEM104_DUPLICATE_METHOD: (
        "Ububiko '%s' bwakabiri mu urwego '%s'",
        "Duplicate method '%s' in class '%s'",
    ),
    SemanticErrorCode.SEM105_DUPLICATE_MODULE: (
        "Modile '%s' yararangire",
        "Duplicate module '%s'",
    ),
    SemanticErrorCode.SEM106_DUPLICATE_STRUCT: (
        "Igiceri '%s' cyakabiri mu bwoko bwinewe",
        "Duplicate struct '%s' in the same scope",
    ),
    SemanticErrorCode.SEM107_DUPLICATE_ENUM: (
        "Ikindi '%s' cyakabiri mu bwoko bwinewe",
        "Duplicate enum '%s' in the same scope",
    ),
    SemanticErrorCode.SEM108_DUPLICATE_TRAIT: (
        "Urubingo '%s' rwakabiri mu bwoko bwinewe",
        "Duplicate trait '%s' in the same scope",
    ),
    SemanticErrorCode.SEM109_DUPLICATE_INTERFACE: (
        "Akabuto '%s' kacakabiri mu bwoko bwinewe",
        "Duplicate interface '%s' in the same scope",
    ),
    SemanticErrorCode.SEM110_RESERVED_KEYWORD: (
        "Izina '%s' ni iri mu jambo ry'uburyo — ntabwo ryemerewe",
        "Name '%s' is a reserved keyword — not allowed as identifier",
    ),
    SemanticErrorCode.SEM111_ILLEGAL_IDENTIFIER: (
        "Izina '%s' si izina ryemewe mu I",
        "Identifier '%s' is not valid in I",
    ),

    # Name Resolution Errors
    SemanticErrorCode.SEM200_UNDEFINED_VARIABLE: (
        "Ikibeto '%s' ntabwo kibonetse",
        "Undefined variable '%s'",
    ),
    SemanticErrorCode.SEM201_UNDEFINED_FUNCTION: (
        "Umurimo '%s' ntabwo ubonetse",
        "Undefined function '%s'",
    ),
    SemanticErrorCode.SEM202_UNDEFINED_CLASS: (
        "Urwego '%s' ntabwo rwabonetse",
        "Undefined class '%s'",
    ),
    SemanticErrorCode.SEM203_UNDEFINED_MODULE: (
        "Modile '%s' ntabwo yabonetse",
        "Undefined module '%s'",
    ),
    SemanticErrorCode.SEM204_UNDEFINED_TYPE: (
        "Ubwoko '%s' ntabwo bwabonetse",
        "Undefined type '%s'",
    ),
    SemanticErrorCode.SEM205_UNDEFINED_STRUCT: (
        "Igiceri '%s' ntabwo cyabonetse",
        "Undefined struct '%s'",
    ),
    SemanticErrorCode.SEM206_UNDEFINED_ENUM: (
        "Ikindi '%s' ntabwo cyabonetse",
        "Undefined enum '%s'",
    ),
    SemanticErrorCode.SEM207_UNDEFINED_METHOD: (
        "Ububiko '%s' ntabwo bwabonetse mu urwego '%s'",
        "Undefined method '%s' in class '%s'",
    ),
    SemanticErrorCode.SEM208_UNDEFINED_TRAIT: (
        "Urubingo '%s' ntabwo rwabonetse",
        "Undefined trait '%s'",
    ),
    SemanticErrorCode.SEM209_UNDEFINED_INTERFACE: (
        "Akabuto '%s' ntabwo kabonetse",
        "Undefined interface '%s'",
    ),

    # Type Errors
    SemanticErrorCode.SEM300_TYPE_MISMATCH: (
        "Ubwoko butemewe: ndabona '%s' ariko nabonye '%s'",
        "Type mismatch: expected '%s' but got '%s'",
    ),
    SemanticErrorCode.SEM301_NOT_CALLABLE: (
        "Ibiri mu '%s' ntabwo bishobora gukoreshwa nka umurimo",
        "Value of type '%s' is not callable",
    ),
    SemanticErrorCode.SEM302_ARGUMENT_COUNT_MISMATCH: (
        "Ibihanya byatanzwe: %d ariko nabonye %d",
        "Argument count mismatch: expected %d but got %d",
    ),
    SemanticErrorCode.SEM303_MISSING_RETURN: (
        "Umurimo '%s' ushobora kutagarura agaciro",
        "Function '%s' may not return a value on all paths",
    ),
    SemanticErrorCode.SEM304_RETURN_OUTSIDE_FUNCTION: (
        "Ijambo 'subira' ntabwo rishobora gukoreshwa hanze y'umurimo",
        "'return' statement cannot be used outside a function",
    ),
    SemanticErrorCode.SEM305_BREAK_OUTSIDE_LOOP: (
        "Ijambo 'gukoma' ntabwo rishobora gukoreshwa hanze y'uruziga",
        "'break' statement cannot be used outside a loop",
    ),
    SemanticErrorCode.SEM306_CONTINUE_OUTSIDE_LOOP: (
        "Ijambo 'kugenda' ntabwo rishobora gukoreshwa hanze y'uruziga",
        "'continue' statement cannot be used outside a loop",
    ),
    SemanticErrorCode.SEM307_CANNOT_INDEX: (
        "Ubwoko '%s' ntabwo bushobora kwibitswa",
        "Type '%s' does not support indexing",
    ),
    SemanticErrorCode.SEM308_INDEX_MUST_BE_NUMERIC: (
        "Igice cy'ububiko bugenewe kuba numeric",
        "Index must be numeric",
    ),
    SemanticErrorCode.SEM309_CANNOT_SET_PROPERTY: (
        "Ubwoko '%s' ntabwo bushobora guhindura ibintu",
        "Type '%s' does not support property assignment",
    ),
    SemanticErrorCode.SEM310_NO_SUCH_PROPERTY: (
        "Urwego '%s' ntabwo rwafite ubwoko '%s'",
        "Class '%s' has no property '%s'",
    ),

    # Import/Export Errors
    SemanticErrorCode.SEM400_MODULE_NOT_FOUND: (
        "Modile '%s' ntabwo yabonetse",
        "Module '%s' not found",
    ),
    SemanticErrorCode.SEM401_DUPLICATE_IMPORT: (
        "Modile '%s' yasizwe kabiri",
        "Module '%s' imported twice",
    ),
    SemanticErrorCode.SEM402_CIRCULAR_IMPORT: (
        "Modile '%s' ifite ikibazo cy'uburambe",
        "Circular import detected: module '%s'",
    ),
    SemanticErrorCode.SEM403_IMPORT_NOT_PUBLIC: (
        "Ikibeto '%s' ntabwo kitangwa mu modile '%s'",
        "Symbol '%s' is not exported from module '%s'",
    ),
    SemanticErrorCode.SEM404_EXPORT_NOT_FOUND: (
        "Ikibeto '%s' ntabwo kibonetse mu modile yano",
        "Exported symbol '%s' not found in this module",
    ),
    SemanticErrorCode.SEM405_PRIVATE_ACCESS: (
        "Ikibeto '%s' ni iri mu buryo bwihariye",
        "Symbol '%s' is private and cannot be accessed here",
    ),

    # Constant Evaluation Errors
    SemanticErrorCode.SEM500_NOT_A_CONSTANT: (
        "Igice '%s' ntabwo gishobora kuba agaciro",
        "Expression '%s' is not a constant value",
    ),
    SemanticErrorCode.SEM501_DIVISION_BY_ZERO: (
        "Kugabanya kuri zero",
        "Division by zero",
    ),
    SemanticErrorCode.SEM502_CONST_TYPE_MISMATCH: (
        "Ikibeto 'shyira_ko' kitashobora kwakira ubwoko '%s'",
        "Constant 'shyira_ko' cannot accept type '%s'",
    ),

    # Control Flow Errors
    SemanticErrorCode.SEM600_UNREACHABLE_CODE: (
        "Ibiri munsi y'ubwo ni ubusa — ntabwo byegererewe",
        "Code after this point is unreachable",
    ),
    SemanticErrorCode.SEM601_MISSING_RETURN_PATH: (
        "Umurimo '%s' ntago aho asubira",
        "Function '%s' does not return on all paths",
    ),
    SemanticErrorCode.SEM602_UNINITIALIZED_VARIABLE: (
        "Ikibeto '%s' ntabwo cyatangiye",
        "Variable '%s' may be used before initialization",
    ),

    # Visibility Errors
    SemanticErrorCode.SEM700_VISIBILITY_RESTRICTED: (
        "Ikibeto '%s' ntabwo riri mu bwoko bwemerewe",
        "Symbol '%s' has restricted visibility",
    ),
    SemanticErrorCode.SEM701_MODULE_NOT_EXPORTED: (
        "Modile '%s' ntabwo itangwa",
        "Module '%s' is not exported",
    ),
    SemanticErrorCode.SEM702_SYMBOL_NOT_VISIBLE: (
        "Ikibeto '%s' ntabwo kibonetse mu buryo bwari bwose",
        "Symbol '%s' is not visible from the current scope",
    ),
}


def get_bilingual_message(code: SemanticErrorCode, *args: Any) -> Tuple[str, str]:
    """Get bilingual message for an error code with optional format args."""
    template = _MESSAGES.get(code, ("Ikosa ryateye akere", "Unknown error"))
    if args:
        try:
            return (template[0] % args, template[1] % args)
        except (TypeError, ValueError):
            return template
    return template


@dataclass(frozen=True)
class SourceLocation:
    """Source location for a diagnostic."""

    file: str = "<input>"
    line: int = 0
    column: int = 0
    end_line: int = 0
    end_column: int = 0
    offset: int = 0
    end_offset: int = 0

    def __str__(self) -> str:
        if self.line == 0:
            return self.file
        if self.line == self.end_line:
            return f"{self.file}:{self.line}:{self.column}"
        return f"{self.file}:{self.line}:{self.column}-{self.end_line}:{self.end_column}"

    @classmethod
    def from_token(cls, token: Any, file: str = "<input>") -> SourceLocation:
        """Create from a Token object."""
        return cls(
            file=file,
            line=getattr(token, 'line', 0),
            column=getattr(token, 'column', 0),
            end_line=getattr(token, 'line', 0),
            end_column=getattr(token, 'column', 0) + getattr(token, 'span', 1),
            offset=getattr(token, 'offset', 0),
            end_offset=getattr(token, 'offset', 0) + getattr(token, 'span', 1),
        )

    @classmethod
    def from_node(cls, node: Any, file: str = "<input>") -> SourceLocation:
        """Create from an AST node with a span or location attribute."""
        if hasattr(node, 'span'):
            s = node.span
            return cls(
                file=file,
                line=getattr(s, 'start_line', 0),
                column=getattr(s, 'start_column', 0),
                end_line=getattr(s, 'end_line', 0),
                end_column=getattr(s, 'end_column', 0),
                offset=getattr(s, 'start_offset', 0),
                end_offset=getattr(s, 'end_offset', 0),
            )
        if hasattr(node, 'location'):
            loc = node.location
            return cls(
                file=getattr(loc, 'file', file),
                line=getattr(loc, 'start_line', 0),
                column=getattr(loc, 'start_column', 0),
                end_line=getattr(loc, 'end_line', 0),
                end_column=getattr(loc, 'end_column', 0),
                offset=getattr(loc, 'start_offset', 0),
                end_offset=getattr(loc, 'end_offset', 0),
            )
        return cls(file=file)


@dataclass
class SemanticDiagnostic:
    """A single semantic analysis diagnostic."""

    code: SemanticErrorCode
    severity: SemanticSeverity
    location: SourceLocation
    message_rw: str
    message_en: str
    related_symbols: List[str] = field(default_factory=list)
    suggested_fix: Optional[str] = None
    reference_doc: Optional[str] = None

    def __str__(self) -> str:
        loc = str(self.location) if self.location.line > 0 else ""
        prefix = f"[{self.severity.value.upper()}]" if self.severity != SemanticSeverity.ERROR else "[ERROR]"
        code_name = self.code.name
        location_part = f" {loc}" if loc else ""
        return f"{prefix} {code_name}{location_part}: {self.message_en}"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize diagnostic to dictionary."""
        d = {
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
                'end_line': self.location.end_line,
                'end_column': self.location.end_column,
            }
        if self.related_symbols:
            d['related_symbols'] = self.related_symbols
        if self.suggested_fix:
            d['suggested_fix'] = self.suggested_fix
        return d

    def bilingual_str(self) -> str:
        """Full bilingual representation."""
        loc = str(self.location) if self.location.line > 0 else ""
        location_part = f"\n  Location: {loc}" if loc else ""
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
            f"{location_part}{related}{fix}{ref}"
        )


class SemanticErrorCollection:
    """Collects diagnostics during semantic analysis."""

    def __init__(self) -> None:
        self._diagnostics: List[SemanticDiagnostic] = []
        self._max_errors = 100

    @property
    def diagnostics(self) -> List[SemanticDiagnostic]:
        return list(self._diagnostics)

    @property
    def errors(self) -> List[SemanticDiagnostic]:
        return [d for d in self._diagnostics if d.severity == SemanticSeverity.ERROR]

    @property
    def warnings(self) -> List[SemanticDiagnostic]:
        return [d for d in self._diagnostics if d.severity == SemanticSeverity.WARNING]

    @property
    def has_errors(self) -> bool:
        return any(d.severity == SemanticSeverity.ERROR for d in self._diagnostics)

    @property
    def has_warnings(self) -> bool:
        return any(d.severity == SemanticSeverity.WARNING for d in self._diagnostics)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def should_abort(self) -> bool:
        return len(self.errors) >= self._max_errors

    def add(
        self,
        code: SemanticErrorCode,
        severity: SemanticSeverity,
        location: SourceLocation,
        *args: Any,
        related_symbols: Optional[List[str]] = None,
        suggested_fix: Optional[str] = None,
        reference_doc: Optional[str] = None,
    ) -> SemanticDiagnostic:
        """Add a diagnostic."""
        msg_rw, msg_en = get_bilingual_message(code, *args)
        diag = SemanticDiagnostic(
            code=code,
            severity=severity,
            location=location,
            message_rw=msg_rw,
            message_en=msg_en,
            related_symbols=related_symbols or [],
            suggested_fix=suggested_fix,
            reference_doc=reference_doc,
        )
        self._diagnostics.append(diag)
        return diag

    def error(
        self,
        code: SemanticErrorCode,
        location: SourceLocation,
        *args: Any,
        **kwargs: Any,
    ) -> SemanticDiagnostic:
        """Add an error diagnostic."""
        return self.add(code, SemanticSeverity.ERROR, location, *args, **kwargs)

    def warning(
        self,
        code: SemanticErrorCode,
        location: SourceLocation,
        *args: Any,
        **kwargs: Any,
    ) -> SemanticDiagnostic:
        """Add a warning diagnostic."""
        return self.add(code, SemanticSeverity.WARNING, location, *args, **kwargs)

    def info(
        self,
        code: SemanticErrorCode,
        location: SourceLocation,
        *args: Any,
        **kwargs: Any,
    ) -> SemanticDiagnostic:
        """Add an info diagnostic."""
        return self.add(code, SemanticSeverity.INFO, location, *args, **kwargs)

    def clear(self) -> None:
        self._diagnostics.clear()

    def format_all(self, bilingual: bool = False) -> str:
        """Format all diagnostics."""
        lines = []
        for d in self._diagnostics:
            if bilingual:
                lines.append(d.bilingual_str())
            else:
                lines.append(str(d))
        return "\n\n".join(lines)
