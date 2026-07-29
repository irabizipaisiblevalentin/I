"""
Type Context for the I Programming Language

Per-checking-session state for the type checker, tracking
the current scope, function, class, loop nesting, and all
accumulated type errors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from .types import Type, TypeKind, TypeVariable, TYPE_UNKNOWN, TYPE_ANY
from .environment import TypeEnvironment
from .registry import TypeRegistry
from .database import TypeDatabase


# ══════════════════════════════════════════════════════════════════
# Context State Objects
# ══════════════════════════════════════════════════════════════════


@dataclass
class FunctionContext:
    """Tracks state for the current function being type-checked."""

    name: str
    return_type: Optional[Type] = None
    param_types: List[Type] = field(default_factory=list)
    param_names: List[str] = field(default_factory=list)
    is_const: bool = False
    generic_params: List[TypeVariable] = field(default_factory=list)
    has_return_statement: bool = False
    scope_depth: int = 0


@dataclass
class ClassContext:
    """Tracks state for the current class being type-checked."""

    name: str
    parent_name: Optional[str] = None
    implemented_traits: List[str] = field(default_factory=list)
    implemented_interfaces: List[str] = field(default_factory=list)
    generic_params: List[TypeVariable] = field(default_factory=list)
    is_abstract: bool = False
    scope_depth: int = 0


@dataclass
class LoopContext:
    """Tracks state for the current loop being type-checked."""

    kind: str = "while"
    break_type: Optional[Type] = None
    depth: int = 0


# ══════════════════════════════════════════════════════════════════
# Type Context
# ══════════════════════════════════════════════════════════════════


class TypeContext:
    """
    Per-checking-session state for the type checker.

    Manages:
    - Type environment (scope chain)
    - Function/class/loop context stacks
    - Generic type parameter tracking
    - Deferred type checks for forward references
    - Collected type assignments for constraint solving
    """

    def __init__(
        self,
        registry: Optional[TypeRegistry] = None,
        database: Optional[TypeDatabase] = None,
    ) -> None:
        self.registry = registry or TypeRegistry()
        self.database = database or TypeDatabase()
        self.environment = TypeEnvironment()

        # Context stacks
        self._function_stack: List[FunctionContext] = []
        self._class_stack: List[ClassContext] = []
        self._loop_stack: List[LoopContext] = []

        # Generic tracking
        self._active_generics: Dict[str, TypeVariable] = {}

        # Deferred checks (forward references)
        self._deferred: List[Any] = []

        # Type assignments collected for constraint solving
        self._type_assignments: List[tuple] = []

        # Current file being checked
        self.current_file: str = "<input>"

        # Error tracking
        self._error_count: int = 0
        self._max_errors: int = 100
        self._suppressed_codes: Set[str] = set()

    # ── Function Context ──────────────────────────────────────────

    @property
    def current_function(self) -> Optional[FunctionContext]:
        if self._function_stack:
            return self._function_stack[-1]
        return None

    def enter_function(
        self,
        name: str,
        return_type: Optional[Type] = None,
        param_types: Optional[List[Type]] = None,
        param_names: Optional[List[str]] = None,
        is_const: bool = False,
        generic_params: Optional[List[TypeVariable]] = None,
    ) -> FunctionContext:
        ctx = FunctionContext(
            name=name,
            return_type=return_type,
            param_types=param_types or [],
            param_names=param_names or [],
            is_const=is_const,
            generic_params=generic_params or [],
            scope_depth=self.environment.current_depth,
        )
        self._function_stack.append(ctx)
        self.environment.enter_function(name)
        return ctx

    def exit_function(self) -> Optional[FunctionContext]:
        if self._function_stack:
            self.environment.exit_function()
            return self._function_stack.pop()
        return None

    @property
    def in_function(self) -> bool:
        return len(self._function_stack) > 0

    @property
    def current_return_type(self) -> Optional[Type]:
        fn = self.current_function
        return fn.return_type if fn else None

    # ── Class Context ─────────────────────────────────────────────

    @property
    def current_class(self) -> Optional[ClassContext]:
        if self._class_stack:
            return self._class_stack[-1]
        return None

    def enter_class(
        self,
        name: str,
        parent_name: Optional[str] = None,
        traits: Optional[List[str]] = None,
        interfaces: Optional[List[str]] = None,
        generic_params: Optional[List[TypeVariable]] = None,
        is_abstract: bool = False,
    ) -> ClassContext:
        ctx = ClassContext(
            name=name,
            parent_name=parent_name,
            implemented_traits=traits or [],
            implemented_interfaces=interfaces or [],
            generic_params=generic_params or [],
            is_abstract=is_abstract,
            scope_depth=self.environment.current_depth,
        )
        self._class_stack.append(ctx)
        self.environment.enter_class(name)
        return ctx

    def exit_class(self) -> Optional[ClassContext]:
        if self._class_stack:
            self.environment.exit_class()
            return self._class_stack.pop()
        return None

    @property
    def in_class(self) -> bool:
        return len(self._class_stack) > 0

    @property
    def class_depth(self) -> int:
        return len(self._class_stack)

    # ── Loop Context ──────────────────────────────────────────────

    @property
    def current_loop(self) -> Optional[LoopContext]:
        if self._loop_stack:
            return self._loop_stack[-1]
        return None

    def enter_loop(self, kind: str = "while") -> LoopContext:
        ctx = LoopContext(kind=kind, depth=len(self._loop_stack))
        self._loop_stack.append(ctx)
        self.environment.enter_loop()
        return ctx

    def exit_loop(self) -> Optional[LoopContext]:
        if self._loop_stack:
            self.environment.exit_loop()
            return self._loop_stack.pop()
        return None

    @property
    def in_loop(self) -> bool:
        return len(self._loop_stack) > 0

    @property
    def loop_depth(self) -> int:
        return len(self._loop_stack)

    # ── Generic Tracking ──────────────────────────────────────────

    def add_generic(self, name: str, var: TypeVariable) -> None:
        """Register an active generic type parameter."""
        self._active_generics[name] = var

    def get_generic(self, name: str) -> Optional[TypeVariable]:
        """Look up an active generic type parameter."""
        return self._active_generics.get(name)

    def has_generic(self, name: str) -> bool:
        """Check if a generic parameter is active."""
        return name in self._active_generics

    def clear_generics(self) -> None:
        """Clear all active generic parameters."""
        self._active_generics.clear()

    @property
    def active_generics(self) -> Dict[str, TypeVariable]:
        return dict(self._active_generics)

    # ── Deferred Checks ───────────────────────────────────────────

    def defer_check(self, check: Any) -> None:
        """Add a type check to be performed after the initial pass."""
        self._deferred.append(check)

    def process_deferred(self) -> None:
        """Process all deferred type checks."""
        checks = self._deferred
        self._deferred = []
        for check in checks:
            if callable(check):
                check()

    # ── Constraint Collection ─────────────────────────────────────

    def record_assignment(self, name: str, typ: Type, source: str = "") -> None:
        """Record a type assignment for constraint solving."""
        self._type_assignments.append((name, typ, source))

    def get_assignments(self) -> List[tuple]:
        return list(self._type_assignments)

    def get_constraint_count(self) -> int:
        """Get number of collected type assignments."""
        return len(self._type_assignments)

    @property
    def function_depth(self) -> int:
        """How many functions are nested."""
        return len(self._function_stack)

    @property
    def generic_count(self) -> int:
        """Number of active generic parameters."""
        return len(self._active_generics)

    @property
    def deferred_count(self) -> int:
        """Number of deferred checks."""
        return len(self._deferred)

    # ── Error Tracking ────────────────────────────────────────────

    def record_error(self) -> bool:
        """
        Record that an error occurred.
        Returns True if we should abort (too many errors).
        """
        self._error_count += 1
        return self._error_count >= self._max_errors

    @property
    def has_errors(self) -> bool:
        return self._error_count > 0

    @property
    def error_count(self) -> int:
        return self._error_count

    @property
    def should_abort(self) -> bool:
        return self._error_count >= self._max_errors

    def suppress_error(self, code: str) -> None:
        """Suppress a specific error code."""
        self._suppressed_codes.add(code)

    def is_suppressed(self, code: str) -> bool:
        return code in self._suppressed_codes

    # ── Reset ─────────────────────────────────────────────────────

    def clear(self) -> None:
        """Reset all state for a new analysis session."""
        self.environment.clear()
        self._function_stack.clear()
        self._class_stack.clear()
        self._loop_stack.clear()
        self._active_generics.clear()
        self._deferred.clear()
        self._type_assignments.clear()
        self._error_count = 0
        self._suppressed_codes.clear()
        self.current_file = "<input>"
