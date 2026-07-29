"""
Diagnostic message.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from .severity import Severity

if TYPE_CHECKING:
    from ..source.position import Span


@dataclass
class Label:
    """Diagnostic label (annotation on source)."""
    
    span: Span
    message: str
    severity: Severity = Severity.NOTE
    
    def __str__(self) -> str:
        return self.message


@dataclass
class Diagnostic:
    """
    Diagnostic message.
    
    Represents a single diagnostic (error, warning, etc.) with location.
    """
    
    severity: Severity
    message: str
    code: Optional[str] = None
    span: Optional[Span] = None
    labels: List[Label] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        parts = [self.severity.name]
        if self.code:
            parts.append(f"[{self.code}]")
        if self.span:
            parts.append(str(self.span))
        parts.append(self.message)
        return " ".join(parts)
    
    def add_label(self, span: Span, message: str) -> None:
        """Add a label."""
        self.labels.append(Label(span=span, message=message))
    
    def add_note(self, note: str) -> None:
        """Add a note."""
        self.notes.append(note)
    
    @property
    def is_error(self) -> bool:
        return self.severity >= Severity.ERROR
    
    @property
    def is_warning(self) -> bool:
        return self.severity == Severity.WARNING
