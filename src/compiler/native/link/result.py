"""
Compilation result types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

OutputFormat = Literal["object", "executable", "assembly", "ir"]


@dataclass
class CompileResult:
    """Result of a single compilation invocation."""

    success: bool = True
    output_path: Path | None = None
    object_bytes: bytes = b""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
