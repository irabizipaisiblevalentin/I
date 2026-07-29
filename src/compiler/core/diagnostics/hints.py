"""
Diagnostic hints.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..source.position import Span


class HintKind(Enum):
    """Types of hints."""
    SUGGESTION = auto()
    SIMILAR_NAME = auto()
    DID_YOU_MEAN = auto()
    IMPORT_SUGGESTION = auto()
    FIX_SUGGESTION = auto()


@dataclass
class Hint:
    """
    Diagnostic hint.
    
    Provides actionable suggestions for fixing issues.
    """
    
    kind: HintKind
    message: str
    replacement: Optional[str] = None
    span: Optional[Span] = None
    
    def __str__(self) -> str:
        prefix = {
            HintKind.SUGGESTION: "suggestion",
            HintKind.SIMILAR_NAME: "similar name",
            HintKind.DID_YOU_MEAN: "did you mean",
            HintKind.IMPORT_SUGGESTION: "import",
            HintKind.FIX_SUGGESTION: "fix",
        }.get(self.kind, "hint")
        
        return f"{prefix}: {self.message}"
