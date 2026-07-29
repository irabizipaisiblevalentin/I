"""
Generic Type Engine for the I Programming Language

Handles generic type parameters, constraints, instantiation,
and type argument resolution. Supports:
- Generic functions
- Generic classes
- Generic collections
- Generic constraints (bounds)
- Default type parameters
- Future monomorphization and specialization
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .types import (
    Type, TypeKind, TypeVariable, GenericType, FunctionType,
    ListType, MapType, SetType, TupleType, OptionalType,
    TYPE_ANY, TYPE_UNKNOWN,
)
from .registry import TypeRegistry, TypeDefinition, MethodSignature, MemberInfo


# ══════════════════════════════════════════════════════════════════
# Generic Parameter Definition
# ══════════════════════════════════════════════════════════════════


@dataclass
class GenericParamDef:
    """Definition of a generic type parameter."""

    name: str
    upper_bound: Optional[Type] = None
    lower_bound: Optional[Type] = None
    default: Optional[Type] = None
    constraints: List[Type] = field(default_factory=list)
    variance: str = "invariant"  # "invariant", "covariant", "contravariant"

    def to_type_variable(self) -> TypeVariable:
        """Convert to a TypeVariable."""
        return TypeVariable(self.name, self.upper_bound, self.lower_bound)


# ══════════════════════════════════════════════════════════════════
# Generic Instantiation Record
# ══════════════════════════════════════════════════════════════════


@dataclass
class GenericInstantiation:
    """Records a concrete instantiation of a generic type."""

    base_name: str
    type_args: Tuple[Type, ...]
    specialized_name: str
    file: str = ""
    line: int = 0


# ══════════════════════════════════════════════════════════════════
# Generic Type Engine
# ══════════════════════════════════════════════════════════════════


class GenericEngine:
    """
    Manages generic types in the I programming language.

    Responsibilities:
    - Register generic type parameters for functions and classes
    - Validate generic constraints (bounds)
    - Instantiate generic types with concrete type arguments
    - Track generic instantiations for monomorphization
    - Resolve default type parameters
    """

    def __init__(self, registry: TypeRegistry) -> None:
        self.registry = registry
        self._generic_params: Dict[str, List[GenericParamDef]] = {}
        self._instantiations: List[GenericInstantiation] = []
        self._instantiation_map: Dict[str, GenericType] = {}
        self._specialization_count = 0

    # ── Registration ──────────────────────────────────────────────

    def register_generic_function(
        self,
        name: str,
        params: List[GenericParamDef],
    ) -> None:
        """Register generic type parameters for a function."""
        self._generic_params[name] = params

    def register_generic_class(
        self,
        name: str,
        params: List[GenericParamDef],
    ) -> None:
        """Register generic type parameters for a class."""
        self._generic_params[name] = params

    def get_generic_params(self, name: str) -> List[GenericParamDef]:
        """Get generic parameters for a declaration."""
        return list(self._generic_params.get(name, []))

    def has_generics(self, name: str) -> bool:
        """Check if a declaration has generic parameters."""
        return name in self._generic_params

    # ── Constraint Validation ─────────────────────────────────────

    def validate_constraints(
        self,
        base_name: str,
        type_args: List[Type],
    ) -> List[str]:
        """
        Validate that type arguments satisfy all generic constraints.
        Returns a list of error messages (empty if all valid).
        """
        errors: List[str] = []
        params = self._generic_params.get(base_name, [])

        if len(params) != len(type_args):
            errors.append(
                f"Expected {len(params)} type argument(s) for '{base_name}' "
                f"but got {len(type_args)}"
            )
            return errors

        for param, arg in zip(params, type_args):
            if param.upper_bound and not self._satisfies_constraint(arg, param.upper_bound):
                errors.append(
                    f"Type '{arg}' does not satisfy upper bound '{param.upper_bound}' "
                    f"for generic parameter '{param.name}'"
                )

            if param.lower_bound and not self._satisfies_constraint(param.lower_bound, arg):
                errors.append(
                    f"Type '{arg}' does not satisfy lower bound '{param.lower_bound}' "
                    f"for generic parameter '{param.name}'"
                )

            for constraint in param.constraints:
                if not self._satisfies_constraint(arg, constraint):
                    errors.append(
                        f"Type '{arg}' does not satisfy constraint '{constraint}' "
                        f"for generic parameter '{param.name}'"
                    )

        return errors

    def _satisfies_constraint(self, typ: Type, constraint: Type) -> bool:
        """Check if a type satisfies a constraint."""
        if constraint.kind == TypeKind.ANY:
            return True
        if typ.is_subtype_of(constraint):
            return True
        if typ.kind == TypeKind.CLASS and constraint.kind == TypeKind.CLASS:
            return self.registry.is_subclass_of(typ.name, constraint.name)
        return False

    # ── Instantiation ─────────────────────────────────────────────

    def instantiate_generic(
        self,
        base_name: str,
        type_args: List[Type],
        file: str = "",
        line: int = 0,
    ) -> Optional[GenericType]:
        """
        Instantiate a generic type with concrete type arguments.

        Validates constraints and creates a parameterized type.
        Returns None if constraints are violated.
        """
        errors = self.validate_constraints(base_name, type_args)
        if errors:
            return None

        specialized = self._make_specialized_name(base_name, type_args)
        gen_type = GenericType(base_name, tuple(type_args))

        inst = GenericInstantiation(
            base_name=base_name,
            type_args=tuple(type_args),
            specialized_name=specialized,
            file=file,
            line=line,
        )
        self._instantiations.append(inst)
        self._instantiation_map[specialized] = gen_type
        self._specialization_count += 1

        return gen_type

    def _make_specialized_name(
        self,
        base_name: str,
        type_args: List[Type],
    ) -> str:
        """Create a mangled specialized name."""
        args_str = "_".join(a.name.replace("<", "_").replace(">", "_") for a in type_args)
        return f"{base_name}__{args_str}"

    # ── Function Instantiation ────────────────────────────────────

    def instantiate_generic_function(
        self,
        func_type: FunctionType,
        type_args: List[Type],
        generic_params: List[TypeVariable],
    ) -> FunctionType:
        """
        Instantiate a generic function with concrete type arguments.

        Replaces all occurrences of generic type parameters with the
        given concrete type arguments in the function signature.
        """
        substitution = {}
        for param, arg in zip(generic_params, type_args):
            substitution[param.name] = arg

        new_params = tuple(self._apply_substitution(p, substitution) for p in func_type.param_types)
        new_ret = self._apply_substitution(func_type.return_type, substitution)

        return FunctionType(new_params, new_ret)

    def _apply_substitution(self, typ: Type, substitution: Dict[str, Type]) -> Type:
        """Apply a type variable substitution to a type."""
        if typ.kind == TypeKind.TYPE_VAR:
            if typ.name in substitution:
                return substitution[typ.name]
            return typ
        if typ.kind == TypeKind.LIST:
            new_elem = self._apply_substitution(typ.element_type, substitution)
            if new_elem != typ.element_type:
                return ListType(new_elem)
            return typ
        if typ.kind == TypeKind.MAP:
            new_k = self._apply_substitution(typ.key_type, substitution)
            new_v = self._apply_substitution(typ.value_type, substitution)
            if new_k != typ.key_type or new_v != typ.value_type:
                return MapType(new_k, new_v)
            return typ
        if typ.kind == TypeKind.OPTIONAL:
            new_inner = self._apply_substitution(typ.inner, substitution)
            if new_inner != typ.inner:
                return OptionalType(new_inner)
            return typ
        if typ.kind == TypeKind.TUPLE:
            new_elems = tuple(self._apply_substitution(e, substitution) for e in typ.element_types)
            if new_elems != typ.element_types:
                return TupleType(new_elems)
            return typ
        if typ.kind == TypeKind.FUNCTION:
            new_params = tuple(self._apply_substitution(p, substitution) for p in typ.param_types)
            new_ret = self._apply_substitution(typ.return_type, substitution)
            if new_params != typ.param_types or new_ret != typ.return_type:
                return FunctionType(new_params, new_ret)
            return typ
        return typ

    # ── Default Parameters ────────────────────────────────────────

    def fill_defaults(
        self,
        base_name: str,
        provided_args: List[Type],
    ) -> List[Type]:
        """
        Fill in missing type arguments with defaults.
        Returns the complete list of type arguments.
        """
        params = self._generic_params.get(base_name, [])
        result = list(provided_args)

        for i in range(len(result), len(params)):
            if params[i].default:
                result.append(params[i].default)
            else:
                result.append(TYPE_ANY)

        return result

    # ── Query ─────────────────────────────────────────────────────

    def get_instantiation(self, specialized_name: str) -> Optional[GenericType]:
        """Look up a specialization by its mangled name."""
        return self._instantiation_map.get(specialized_name)

    def get_all_instantiations(self) -> List[GenericInstantiation]:
        """Get all recorded instantiations."""
        return list(self._instantiations)

    def get_instantiations_of(self, base_name: str) -> List[GenericInstantiation]:
        """Get all instantiations of a specific generic."""
        return [i for i in self._instantiations if i.base_name == base_name]

    @property
    def specialization_count(self) -> int:
        return self._specialization_count

    def clear(self) -> None:
        """Reset all state."""
        self._generic_params.clear()
        self._instantiations.clear()
        self._instantiation_map.clear()
        self._specialization_count = 0

    def detect_cyclic_constraint(self, base_name: str) -> bool:
        """Detect if a generic type has a cyclic constraint."""
        visited: Set[str] = set()
        return self._check_cyclic(base_name, visited)

    def _check_cyclic(self, name: str, visited: Set[str]) -> bool:
        """Internal cycle detection for generic constraints."""
        if name in visited:
            return True
        visited.add(name)
        params = self._generic_params.get(name, [])
        for param in params:
            if param.upper_bound and param.upper_bound.kind == TypeKind.PARAMETERIZED:
                if self._check_cyclic(param.upper_bound.base_name, set(visited)):
                    return True
        return False

    def get_variance(self, base_name: str, param_name: str) -> str:
        """Get the variance of a generic parameter."""
        params = self._generic_params.get(base_name, [])
        for param in params:
            if param.name == param_name:
                return param.variance
        return "invariant"

    def count_instantiations_of(self, base_name: str) -> int:
        """Count how many times a generic has been instantiated."""
        return sum(1 for i in self._instantiations if i.base_name == base_name)

    def get_all_generic_names(self) -> List[str]:
        """Get all registered generic declaration names."""
        return list(self._generic_params.keys())
