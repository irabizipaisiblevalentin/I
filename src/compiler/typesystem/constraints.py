"""
Type Constraint Solver for the I Programming Language

Solves type constraints generated during type inference.
Uses a unification-based algorithm with support for:
- Equality constraints
- Subtype constraints
- Upper/lower bound constraints
- Collection constraints
- Function signature constraints
- Generic parameter constraints
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple

from .types import (
    Type, TypeKind, TypeVariable, FunctionType, OptionalType,
    ListType, MapType, SetType, TupleType, RangeType, GenericType, NoneType,
    TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_STRING, TYPE_NONE,
    TYPE_ANY, TYPE_UNKNOWN, TYPE_NEVER, common_type,
)


# ══════════════════════════════════════════════════════════════════
# Constraint Types
# ══════════════════════════════════════════════════════════════════


class ConstraintKind(Enum):
    """Classification of type constraints."""

    EQUALS = auto()          # T == U
    SUBTYPE = auto()         # T <: U
    SUPERTYPE = auto()       # T :> U
    UPPER_BOUND = auto()     # T <= U (T is upper bounded by U)
    LOWER_BOUND = auto()     # T >= U (T is lower bounded by U)
    NOT_EQUAL = auto()       # T != U
    ASSIGNABLE = auto()      # T can be assigned to U
    CALLABLE = auto()        # T is callable with given signature
    INDEXABLE = auto()       # T supports indexing with key type K returning V
    HAS_MEMBER = auto()      # T has member M of type U
    IMPLEMENTS = auto()      # T implements trait/interface I
    UNIFY = auto()           # T and U must unify (bidirectional)


@dataclass(frozen=True)
class Constraint:
    """A single type constraint."""

    kind: ConstraintKind
    left: Type
    right: Type
    source: str = ""
    line: int = 0

    def __repr__(self) -> str:
        op_map = {
            ConstraintKind.EQUALS: "==",
            ConstraintKind.SUBTYPE: "<:",
            ConstraintKind.SUPERTYPE: ":>",
            ConstraintKind.UPPER_BOUND: "<=",
            ConstraintKind.LOWER_BOUND: ">=",
            ConstraintKind.NOT_EQUAL: "!=",
            ConstraintKind.ASSIGNABLE: "=?",
            ConstraintKind.CALLABLE: "callable",
            ConstraintKind.INDEXABLE: "indexable",
            ConstraintKind.HAS_MEMBER: "has",
            ConstraintKind.IMPLEMENTS: "impl",
            ConstraintKind.UNIFY: "~",
        }
        op = op_map.get(self.kind, "?")
        return f"{self.left} {op} {self.right}"


# ══════════════════════════════════════════════════════════════════
# Substitution Map
# ══════════════════════════════════════════════════════════════════


class Substitution:
    """
    Maps type variables to their resolved types.

    Used during constraint solving to track which type variables
    have been resolved to concrete types.
    """

    def __init__(self) -> None:
        self._map: Dict[str, Type] = {}

    def bind(self, name: str, typ: Type) -> bool:
        """
        Bind a type variable to a type.
        Returns False if already bound to a different type.
        """
        if name in self._map:
            existing = self._map[name]
            if existing == typ:
                return True
            if existing.kind == TypeKind.UNKNOWN:
                self._map[name] = typ
                return True
            if typ.kind == TypeKind.UNKNOWN:
                return True
            return False
        self._map[name] = typ
        return True

    def lookup(self, name: str) -> Optional[Type]:
        """Look up a binding."""
        return self._map.get(name)

    def resolve(self, typ: Type) -> Type:
        """Resolve a type by applying all current bindings."""
        if typ.kind == TypeKind.TYPE_VAR:
            binding = self._map.get(typ.name)
            if binding:
                return self.resolve(binding)
            return typ
        if typ.kind == TypeKind.OPTIONAL:
            resolved_inner = self.resolve(typ.inner)
            if resolved_inner != typ.inner:
                return OptionalType(resolved_inner)
            return typ
        if typ.kind == TypeKind.LIST:
            resolved_elem = self.resolve(typ.element_type)
            if resolved_elem != typ.element_type:
                return ListType(resolved_elem)
            return typ
        if typ.kind == TypeKind.MAP:
            resolved_k = self.resolve(typ.key_type)
            resolved_v = self.resolve(typ.value_type)
            if resolved_k != typ.key_type or resolved_v != typ.value_type:
                return MapType(resolved_k, resolved_v)
            return typ
        if typ.kind == TypeKind.TUPLE:
            resolved_elems = tuple(self.resolve(e) for e in typ.element_types)
            if resolved_elems != typ.element_types:
                return TupleType(resolved_elems)
            return typ
        if typ.kind == TypeKind.FUNCTION:
            resolved_params = tuple(self.resolve(p) for p in typ.param_types)
            resolved_ret = self.resolve(typ.return_type)
            if resolved_params != typ.param_types or resolved_ret != typ.return_type:
                return FunctionType(resolved_params, resolved_ret)
            return typ
        if typ.kind == TypeKind.SET:
            resolved_elem = self.resolve(typ.element_type)
            if resolved_elem != typ.element_type:
                return SetType(resolved_elem)
            return typ
        if typ.kind == TypeKind.RANGE:
            resolved_elem = self.resolve(typ.element_type)
            if resolved_elem != typ.element_type:
                return RangeType(resolved_elem)
            return typ
        return typ

    def has(self, name: str) -> bool:
        return name in self._map

    @property
    def bindings(self) -> Dict[str, Type]:
        return dict(self._map)

    def clear(self) -> None:
        self._map.clear()

    def __len__(self) -> int:
        return len(self._map)


# ══════════════════════════════════════════════════════════════════
# Constraint Solver
# ══════════════════════════════════════════════════════════════════


class ConstraintSolver:
    """
    Solves type constraints using a unification-based algorithm.

    The solver processes constraints iteratively, building up a
    substitution map that resolves all type variables to concrete types.

    Algorithm:
    1. Collect all constraints
    2. Process equality constraints first (simplest)
    3. Process subtype/supertype constraints
    4. Process complex constraints (callable, indexable, etc.)
    5. Apply substitution and verify consistency
    """

    def __init__(self) -> None:
        self._constraints: List[Constraint] = []
        self._substitution = Substitution()
        self._resolved: Set[int] = set()
        self._iterations = 0
        self._max_iterations = 100
        self._failed: List[str] = []

    @property
    def substitution(self) -> Substitution:
        return self._substitution

    @property
    def is_solved(self) -> bool:
        return len(self._failed) == 0

    @property
    def iterations(self) -> int:
        return self._iterations

    @property
    def failure_messages(self) -> List[str]:
        return list(self._failed)

    def add_constraint(self, constraint: Constraint) -> None:
        """Add a constraint to the solver."""
        self._constraints.append(constraint)

    def add_equality(self, left: Type, right: Type, source: str = "") -> None:
        """Add an equality constraint."""
        self._constraints.append(Constraint(
            ConstraintKind.EQUALS, left, right, source,
        ))

    def add_subtype(self, subtype: Type, supertype: Type, source: str = "") -> None:
        """Add a subtype constraint."""
        self._constraints.append(Constraint(
            ConstraintKind.SUBTYPE, subtype, supertype, source,
        ))

    def add_upper_bound(self, var: Type, bound: Type, source: str = "") -> None:
        """Add an upper bound constraint."""
        self._constraints.append(Constraint(
            ConstraintKind.UPPER_BOUND, var, bound, source,
        ))

    def add_lower_bound(self, var: Type, bound: Type, source: str = "") -> None:
        """Add a lower bound constraint."""
        self._constraints.append(Constraint(
            ConstraintKind.LOWER_BOUND, var, bound, source,
        ))

    def add_assignable(self, source: Type, target: Type, source_loc: str = "") -> None:
        """Add an assignability constraint."""
        self._constraints.append(Constraint(
            ConstraintKind.ASSIGNABLE, source, target, source_loc,
        ))

    def solve(self) -> Substitution:
        """
        Solve all constraints and return the resulting substitution.

        Returns the substitution map mapping type variables to their
        resolved concrete types.
        """
        self._iterations = 0
        self._failed.clear()

        while self._iterations < self._max_iterations:
            if len(self._resolved) >= len(self._constraints):
                break

            self._iterations += 1
            progress = False

            for i, constraint in enumerate(self._constraints):
                if id(constraint) in self._resolved:
                    continue

                resolved_left = self._substitution.resolve(constraint.left)
                resolved_right = self._substitution.resolve(constraint.right)

                success = self._process_constraint(
                    constraint.kind, resolved_left, resolved_right, constraint,
                )

                if success:
                    self._resolved.add(id(constraint))
                    progress = True
                elif not success and constraint.kind in (
                    ConstraintKind.EQUALS, ConstraintKind.UNIFY,
                ):
                    self._failed.append(
                        f"Cannot unify '{resolved_left}' with '{resolved_right}'"
                    )
                    self._resolved.add(id(constraint))

            if not progress:
                break

        self._propagate()
        return self._substitution

    def _process_constraint(
        self,
        kind: ConstraintKind,
        left: Type,
        right: Type,
        original: Constraint,
    ) -> bool:
        """Process a single constraint. Returns True if resolved."""

        if kind == ConstraintKind.EQUALS:
            return self._solve_equals(left, right)
        if kind == ConstraintKind.SUBTYPE:
            return self._solve_subtype(left, right)
        if kind == ConstraintKind.UPPER_BOUND:
            return self._solve_upper_bound(left, right)
        if kind == ConstraintKind.LOWER_BOUND:
            return self._solve_lower_bound(left, right)
        if kind == ConstraintKind.ASSIGNABLE:
            return self._solve_assignable(left, right)
        if kind == ConstraintKind.UNIFY:
            return self._solve_unify(left, right)

        return False

    def _solve_equals(self, left: Type, right: Type) -> bool:
        """Solve an equality constraint."""
        if left.kind == TypeKind.TYPE_VAR:
            if left.kind == right.kind and left.name == right.name:
                return True
            return self._substitution.bind(left.name, right)

        if right.kind == TypeKind.TYPE_VAR:
            return self._substitution.bind(right.name, left)

        if left.kind == TypeKind.UNKNOWN:
            return True
        if right.kind == TypeKind.UNKNOWN:
            return True

        if left.kind != right.kind:
            if left.is_numeric and right.is_numeric:
                return True
            return False

        if left.kind == TypeKind.FUNCTION:
            if len(left.param_types) != len(right.param_types):
                return False
            for lp, rp in zip(left.param_types, right.param_types):
                if not self._solve_equals(lp, rp):
                    return False
            return self._solve_equals(left.return_type, right.return_type)

        if left.kind == TypeKind.LIST:
            return self._solve_equals(left.element_type, right.element_type)

        if left.kind == TypeKind.MAP:
            return (self._solve_equals(left.key_type, right.key_type) and
                    self._solve_equals(left.value_type, right.value_type))

        if left.kind == TypeKind.OPTIONAL:
            return self._solve_equals(left.inner, right.inner)

        return left.name == right.name

    def _solve_subtype(self, subtype: Type, supertype: Type) -> bool:
        """Solve a subtype constraint."""
        if supertype.kind == TypeKind.ANY:
            return True
        if subtype.kind == TypeKind.NEVER:
            return True
        if subtype.kind == TypeKind.TYPE_VAR:
            return self._substitution.bind(subtype.name, supertype)
        if supertype.kind == TypeKind.TYPE_VAR:
            return self._substitution.bind(supertype.name, subtype)
        if subtype.is_assignable_to(supertype):
            return True
        if subtype.kind == supertype.kind:
            return subtype.name == supertype.name
        if subtype.is_numeric and supertype.is_numeric:
            return True
        return False

    def _solve_upper_bound(self, var: Type, bound: Type) -> bool:
        """Solve an upper bound constraint."""
        if var.kind == TypeKind.TYPE_VAR:
            existing = self._substitution.lookup(var.name)
            if existing:
                return self._solve_subtype(existing, bound)
            return self._substitution.bind(var.name, bound)
        return var.is_assignable_to(bound)

    def _solve_lower_bound(self, var: Type, bound: Type) -> bool:
        """Solve a lower bound constraint."""
        if var.kind == TypeKind.TYPE_VAR:
            existing = self._substitution.lookup(var.name)
            if existing:
                return self._solve_subtype(bound, existing)
            return self._substitution.bind(var.name, bound)
        return bound.is_assignable_to(var)

    def _solve_assignable(self, source: Type, target: Type) -> bool:
        """Solve an assignability constraint."""
        if target.kind == TypeKind.ANY:
            return True
        if source.kind == TypeKind.TYPE_VAR:
            return self._substitution.bind(source.name, target)
        if target.kind == TypeKind.TYPE_VAR:
            return self._substitution.bind(target.name, source)
        return source.is_assignable_to(target)

    def _solve_unify(self, left: Type, right: Type) -> bool:
        """Solve a unification constraint (bidirectional)."""
        if left.kind == TypeKind.TYPE_VAR:
            return self._substitution.bind(left.name, right)
        if right.kind == TypeKind.TYPE_VAR:
            return self._substitution.bind(right.name, left)
        if left.kind == right.kind and left.name == right.name:
            return True
        if left.is_numeric and right.is_numeric:
            return True
        return False

    def _propagate(self) -> None:
        """Propagate substitutions through all bindings."""
        for _ in range(self._max_iterations):
            changed = False
            for name, typ in list(self._substitution.bindings.items()):
                resolved = self._substitution.resolve(typ)
                if resolved != typ:
                    self._substitution.bind(name, resolved)
                    changed = True
            if not changed:
                break

    def resolve_type(self, typ: Type) -> Type:
        """Resolve a type through the current substitution."""
        return self._substitution.resolve(typ)

    def get_bindings(self) -> Dict[str, Type]:
        """Get all resolved bindings."""
        result = {}
        for name in self._substitution.bindings:
            resolved = self._substitution.resolve(
                TypeVariable(name)
            )
            result[name] = resolved
        return result

    @property
    def failed_count(self) -> int:
        """Number of failed constraints."""
        return len(self._failed)

    @property
    def constraint_count(self) -> int:
        """Total number of constraints."""
        return len(self._constraints)

    @property
    def resolved_count(self) -> int:
        """Number of resolved constraints."""
        return len(self._resolved)

    def get_all_resolved_types(self) -> Dict[str, Type]:
        """Get all type variables and their resolved types."""
        result = {}
        for name in self._substitution.bindings:
            resolved = self._substitution.resolve(TypeVariable(name))
            result[name] = resolved
        return result

    def is_type_var_resolved(self, name: str) -> bool:
        """Check if a type variable has been resolved."""
        resolved = self._substitution.resolve(TypeVariable(name))
        return resolved.kind != TypeKind.TYPE_VAR

    def clear(self) -> None:
        """Clear all constraints and state."""
        self._constraints.clear()
        self._substitution.clear()
        self._resolved.clear()
        self._iterations = 0
        self._failed.clear()
