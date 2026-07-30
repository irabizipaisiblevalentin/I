"""
Target description — detailed architecture and platform information.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from compiler.native.target.kind import TargetKind


@dataclass(frozen=True)
class TargetDescription:
    """Describes a compilation target architecture and platform."""

    kind: TargetKind
    bits: int = 64
    triple: str = "x86_64-unknown-unknown"
    features: frozenset[str] = field(default_factory=frozenset)
