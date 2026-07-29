"""
Analysis Context

Per-file/per-module state for the semantic analyzer, tracking
current scope, current function, current class, loop nesting,
and all accumulated diagnostics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from .errors import SemanticErrorCollection, SourceLocation
from .scopes import Scope, ScopeKind, ScopeManager
from .symbols import Symbol, SymbolKind, TypeDescriptor, SymbolType
from .imports import ImportResolver


@dataclass
class FunctionContext:
    """Tracks state for the current function being analyzed."""
    name: str
    return_type: Optional[TypeDescriptor] = None
    has_return_statement: bool = False
    scope: Optional[Scope] = None


@dataclass
class ClassContext:
    """Tracks state for the current class being analyzed."""
    name: str
    parent_name: Optional[str] = None
    symbol: Optional[Symbol] = None
    scope: Optional[Scope] = None


@dataclass
class AnalysisContext:
    """
    Per-analysis-session state for the semantic analyzer.

    Maintains all mutable state needed during a single pass of
    semantic analysis over one or more files.
    """

    # Diagnostics
    diagnostics: SemanticErrorCollection = field(
        default_factory=SemanticErrorCollection
    )

    # Scope management
    scopes: ScopeManager = field(default_factory=ScopeManager)

    # Import resolution
    imports: ImportResolver = field(default_factory=ImportResolver)

    # Current function context stack (None if not inside a function)
    _function_stack: List[Optional[FunctionContext]] = field(default_factory=list)

    # Current class context (None if not inside a class)
    current_class: Optional[ClassContext] = None

    # Loop depth counter
    loop_depth: int = 0

    # Module name
    current_module: Optional[str] = None

    # File path being analyzed
    current_file: str = "<input>"

    # Deferred type checks (for forward references)
    deferred_checks: List[Any] = field(default_factory=list)

    # Symbol table: collected symbols for this analysis
    collected_symbols: Dict[str, Symbol] = field(default_factory=dict)

    @property
    def current_function(self) -> Optional[FunctionContext]:
        if self._function_stack:
            return self._function_stack[-1]
        return None

    def enter_function(self, name: str, return_type: Optional[TypeDescriptor] = None) -> None:
        """Enter a function scope."""
        self._function_stack.append(FunctionContext(name, return_type))
        self.scopes.push(ScopeKind.FUNCTION, name)

    def exit_function(self) -> None:
        """Exit a function scope, restoring the previous function context."""
        if self._function_stack:
            self._function_stack.pop()
        self.scopes.pop()

    def enter_class(self, name: str, parent_name: Optional[str] = None) -> None:
        """Enter a class scope."""
        self.current_class = ClassContext(name, parent_name)
        self.scopes.push(ScopeKind.CLASS, name)

    def exit_class(self) -> None:
        """Exit a class scope."""
        self.current_class = None
        self.scopes.pop()

    def enter_loop(self) -> None:
        """Enter a loop scope."""
        self.loop_depth += 1
        self.scopes.push(ScopeKind.LOOP)

    def exit_loop(self) -> None:
        """Exit a loop scope."""
        self.loop_depth = max(0, self.loop_depth - 1)
        self.scopes.pop()

    def enter_block(self, name: str = "") -> None:
        """Enter a generic block scope."""
        self.scopes.push(ScopeKind.BLOCK, name)

    def exit_block(self) -> None:
        """Exit a block scope."""
        self.scopes.pop()

    def enter_module(self, name: str) -> None:
        """Enter a module scope."""
        self.current_module = name
        self.scopes.push(ScopeKind.MODULE, name)
        self.imports.start_module(name)

    def exit_module(self) -> None:
        """Exit a module scope."""
        self.imports.end_module()
        self.current_module = None
        self.scopes.pop()

    @property
    def in_function(self) -> bool:
        return self.current_function is not None

    @property
    def in_class(self) -> bool:
        return self.current_class is not None

    @property
    def in_loop(self) -> bool:
        return self.loop_depth > 0

    @property
    def has_errors(self) -> bool:
        return self.diagnostics.has_errors

    @property
    def should_abort(self) -> bool:
        return self.diagnostics.should_abort

    def add_deferred_check(self, check: Any) -> None:
        """Add a type check to be performed after the initial pass."""
        self.deferred_checks.append(check)

    def process_deferred_checks(self) -> None:
        """Process all deferred type checks."""
        checks = self.deferred_checks
        self.deferred_checks = []
        for check in checks:
            if callable(check):
                check()

    def clear(self) -> None:
        """Reset all analysis state."""
        self.diagnostics.clear()
        self.scopes = ScopeManager()
        self.imports = ImportResolver()
        self._function_stack.clear()
        self.current_class = None
        self.loop_depth = 0
        self.current_module = None
        self.deferred_checks.clear()
        self.collected_symbols.clear()
