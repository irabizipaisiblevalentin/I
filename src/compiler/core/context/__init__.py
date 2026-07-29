"""
Compiler Context

Holds shared state during compilation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..config.types import CompilerConfig
from ..diagnostics.engine import DiagnosticEngine
from ..features import FeatureFlagManager
from ..logging.logger import Logger
from ..timing import TimingCollector

if TYPE_CHECKING:
    from ..source.file import SourceFile


@dataclass
class CompilerContext:
    """
    Shared compiler context.

    Holds all state shared between compiler phases.
    """

    config: CompilerConfig = field(default_factory=CompilerConfig)
    diagnostics: DiagnosticEngine = field(default_factory=DiagnosticEngine)
    logger: Logger = field(default=None)
    features: FeatureFlagManager = field(default_factory=FeatureFlagManager)
    timing: TimingCollector = field(default_factory=TimingCollector)

    # Source files
    source_files: dict[str, SourceFile] = field(default_factory=dict)

    # Symbol tables (populated by semantic analysis)
    symbols: dict[str, Any] = field(default_factory=dict)

    # Shared state between phases
    state: dict[str, Any] = field(default_factory=dict)

    def add_source(self, source: SourceFile) -> None:
        """Add a source file."""
        self.source_files[str(source.path)] = source

    def get_source(self, path: str) -> SourceFile | None:
        """Get source file by path."""
        return self.source_files.get(path)

    def set_state(self, key: str, value: Any) -> None:
        """Set shared state."""
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get shared state."""
        return self.state.get(key, default)

    def reset(self) -> None:
        """Reset context for new compilation."""
        self.diagnostics.clear()
        self.source_files.clear()
        self.symbols.clear()
        self.state.clear()
        self.timing.clear()
