"""
Type Inference Engine for the I Programming Language

Infers types for expressions, variables, function returns,
and generic parameters using constraint-based inference with
bidirectional type checking.

Supports:
- Local variable inference
- Function return type inference
- Constant inference
- Collection inference
- Expression inference
- Generic inference
- Lambda inference
- Constraint propagation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from .types import (
    Type, TypeKind, TypeVariable, FunctionType, OptionalType,
    ListType, MapType, SetType, TupleType, RangeType,
    GenericType, NoneType, ClassType,
    TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_STRING, TYPE_NONE,
    TYPE_ANY, TYPE_UNKNOWN, TYPE_NEVER, common_type,
)
from .constraints import ConstraintSolver, Constraint, ConstraintKind
from .environment import TypeEnvironment
from .context import TypeContext
from .diagnostics import TypeDiagnostics, TypeErrorCode, TypeLocation


# ══════════════════════════════════════════════════════════════════
# Inference Result
# ══════════════════════════════════════════════════════════════════


@dataclass
class InferenceResult:
    """Result of a type inference operation."""

    inferred_type: Type
    constraints_generated: int = 0
    is_complete: bool = True
    ambiguous: bool = False
    source: str = ""


# ══════════════════════════════════════════════════════════════════
# Inference Engine
# ══════════════════════════════════════════════════════════════════


class InferenceEngine:
    """
    Type inference engine using constraint-based inference.

    The engine collects type constraints while walking the AST,
    then uses the constraint solver to find a consistent assignment
    of types to all untyped positions.
    """

    def __init__(
        self,
        ctx: TypeContext,
        diagnostics: TypeDiagnostics,
    ) -> None:
        self.ctx = ctx
        self.diagnostics = diagnostics
        self.solver = ConstraintSolver()
        self._type_var_counter = 0
        self._inferred_cache: Dict[int, Type] = {}

    def new_type_var(self, name: Optional[str] = None) -> TypeVariable:
        """Create a fresh type variable."""
        if name is None:
            self._type_var_counter += 1
            name = f"_T{self._type_var_counter}"
        var = TypeVariable(name)
        self.ctx.add_generic(name, var)
        return var

    # ── Literal Inference ─────────────────────────────────────────

    def infer_literal(self, value: Any) -> Type:
        """Infer the type of a literal value."""
        if value is None:
            return TYPE_NONE
        if isinstance(value, bool):
            return TYPE_BOOL
        if isinstance(value, int):
            return TYPE_INT
        if isinstance(value, float):
            return TYPE_FLOAT
        if isinstance(value, str):
            return TYPE_STRING
        return TYPE_ANY

    # ── Identifier Inference ──────────────────────────────────────

    def infer_identifier(self, name: str, location: TypeLocation) -> Type:
        """Infer the type of an identifier reference."""
        typ = self.ctx.environment.lookup(name)
        if typ and typ.kind != TypeKind.UNKNOWN:
            return typ

        # Check generics
        generic = self.ctx.get_generic(name)
        if generic:
            return generic

        self.diagnostics.undefined_variable(location, name)
        return TYPE_UNKNOWN

    # ── Binary Expression Inference ───────────────────────────────

    def infer_binary(
        self,
        left_type: Type,
        operator: str,
        right_type: Type,
        location: TypeLocation,
    ) -> Type:
        """Infer the type of a binary expression."""
        op = operator if isinstance(operator, str) else str(operator)

        # Arithmetic operators
        if op in ('+', '-', '*', '/', '%', '**'):
            return self._infer_arithmetic(left_type, op, right_type, location)

        # Comparison operators
        if op in ('==', '!=', '===', '!==', '>', '<', '>=', '<='):
            return TYPE_BOOL

        # Bitwise operators
        if op in ('&', '|', '^', '<<', '>>', '>>>'):
            if left_type.is_numeric:
                return left_type
            if left_type.kind == TypeKind.ANY:
                return TYPE_ANY
            self.diagnostics.error(
                TypeErrorCode.TYP104_INCOMPATIBLE_TYPES,
                location,
                "numeric type", str(left_type),
                expected_type=TYPE_INT, actual_type=left_type,
            )
            return TYPE_ANY

        # String concatenation
        if op == '+':
            if left_type.kind == TypeKind.STRING or right_type.kind == TypeKind.STRING:
                return TYPE_STRING

        # Logical operators
        if op in ('and', 'or', '&&', '||'):
            return TYPE_BOOL

        return TYPE_ANY

    def _infer_arithmetic(
        self,
        left: Type,
        op: str,
        right: Type,
        location: TypeLocation,
    ) -> Type:
        """Infer type for arithmetic operations."""
        if left.kind == TypeKind.ANY or right.kind == TypeKind.ANY:
            return TYPE_ANY

        if left.kind in (TypeKind.INT, TypeKind.FLOAT) and right.kind in (TypeKind.INT, TypeKind.FLOAT):
            if left.kind == TypeKind.FLOAT or right.kind == TypeKind.FLOAT:
                return TYPE_FLOAT
            return TYPE_INT

        if op == '+':
            if left.kind == TypeKind.STRING and right.kind == TypeKind.STRING:
                return TYPE_STRING

        self.diagnostics.error(
            TypeErrorCode.TYP104_INCOMPATIBLE_TYPES,
            location,
            "numeric or string", f"{left} {op} {right}",
            expected_type=TYPE_INT, actual_type=left,
        )
        return TYPE_ANY

    # ── Unary Expression Inference ────────────────────────────────

    def infer_unary(
        self,
        operator: str,
        operand_type: Type,
        location: TypeLocation,
    ) -> Type:
        """Infer the type of a unary expression."""
        op = operator if isinstance(operator, str) else str(operator)

        if op in ('-', 'MINUS'):
            if operand_type.is_numeric:
                return operand_type
            if operand_type.kind == TypeKind.ANY:
                return TYPE_ANY
            self.diagnostics.error(
                TypeErrorCode.TYP104_INCOMPATIBLE_TYPES,
                location,
                "numeric", str(operand_type),
                expected_type=TYPE_INT, actual_type=operand_type,
            )
            return TYPE_ANY

        if op in ('!', 'si'):
            return TYPE_BOOL

        if op in ('~',):
            if operand_type.is_numeric:
                return operand_type
            return TYPE_ANY

        return TYPE_ANY

    # ── Collection Inference ──────────────────────────────────────

    def infer_list_literal(self, element_types: List[Type]) -> ListType:
        """Infer type of a list literal."""
        if not element_types:
            return ListType(self.new_type_var("_Elem"))

        first = element_types[0]
        for elem in element_types[1:]:
            unified = common_type(first, elem)
            if unified is None:
                self._add_collection_constraint(first, elem)
                return ListType(first)
            first = unified

        return ListType(first)

    def infer_dict_literal(
        self,
        key_types: List[Type],
        value_types: List[Type],
    ) -> MapType:
        """Infer type of a dictionary literal."""
        if not key_types or not value_types:
            kt = self.new_type_var("_Key")
            vt = self.new_type_var("_Val")
            return MapType(kt, vt)

        k_type = key_types[0]
        v_type = value_types[0]

        for kt in key_types[1:]:
            unified = common_type(k_type, kt)
            if unified:
                k_type = unified

        for vt in value_types[1:]:
            unified = common_type(v_type, vt)
            if unified:
                v_type = unified

        return MapType(k_type, v_type)

    def infer_set_literal(self, element_types: List[Type]) -> SetType:
        """Infer type of a set literal."""
        if not element_types:
            return SetType(self.new_type_var("_Elem"))

        first = element_types[0]
        for elem in element_types[1:]:
            unified = common_type(first, elem)
            if unified:
                first = unified
        return SetType(first)

    def infer_tuple_literal(self, element_types: List[Type]) -> TupleType:
        """Infer type of a tuple literal."""
        return TupleType(tuple(element_types))

    def _add_collection_constraint(self, t1: Type, t2: Type) -> None:
        """Add constraint that two collection elements must match."""
        self.solver.add_equality(t1, t2, "collection_homogeneity")

    # ── Function Inference ────────────────────────────────────────

    def infer_lambda(
        self,
        param_names: List[str],
        param_types: List[Optional[Type]],
        body_type: Optional[Type],
    ) -> FunctionType:
        """Infer type of a lambda expression."""
        resolved_params: List[Type] = []
        for pt in param_types:
            if pt:
                resolved_params.append(pt)
            else:
                resolved_params.append(self.new_type_var("_Param"))

        ret = body_type or self.new_type_var("_Ret")
        return FunctionType(tuple(resolved_params), ret)

    def infer_function_return(
        self,
        return_type: Optional[Type],
        body_type: Type,
        location: TypeLocation,
    ) -> Type:
        """Infer the return type of a function."""
        if return_type and return_type.kind != TypeKind.UNKNOWN:
            if body_type.kind != TypeKind.UNKNOWN:
                self.solver.add_equality(return_type, body_type, "return_type")
            return return_type

        return body_type

    # ── Assignment Inference ──────────────────────────────────────

    def infer_assignment(
        self,
        name: str,
        value_type: Type,
        annotation: Optional[Type],
        is_const: bool,
        location: TypeLocation,
    ) -> Type:
        """Infer type for a variable assignment."""
        if annotation:
            if value_type.kind != TypeKind.UNKNOWN:
                self.solver.add_assignable(value_type, annotation, f"assign:{name}")
            return annotation

        if is_const and value_type.kind == TypeKind.UNKNOWN:
            self.diagnostics.error(
                TypeErrorCode.TYP600_CANNOT_INFER_TYPE,
                location,
                name,
            )
            return TYPE_UNKNOWN

        return value_type

    # ── Generic Inference ─────────────────────────────────────────

    def infer_generic_call(
        self,
        type_params: List[TypeVariable],
        arg_types: List[Type],
        param_types: List[Type],
        location: TypeLocation,
    ) -> Dict[str, Type]:
        """
        Infer generic type parameters from call arguments.

        Returns a mapping from type variable names to their inferred types.
        """
        inferred: Dict[str, Type] = {}

        for tp in type_params:
            self.solver.add_equality(
                tp, self.new_type_var(f"_Inferred_{tp.name}"),
                "generic_init",
            )

        for arg_t, param_t in zip(arg_types, param_types):
            resolved_param = self.solver.resolve_type(param_t)
            self.solver.add_equality(arg_t, resolved_param, "generic_arg")

        solution = self.solver.solve()

        for tp in type_params:
            resolved = solution.resolve(tp)
            if resolved.kind != TypeKind.TYPE_VAR:
                inferred[tp.name] = resolved
            else:
                self.diagnostics.error(
                    TypeErrorCode.TYP302_CANNOT_INFER_GENERIC,
                    location,
                    tp.name,
                )

        return inferred

    # ── Expression Inference ──────────────────────────────────────

    def infer_call(
        self,
        callee_type: Type,
        arg_types: List[Type],
        location: TypeLocation,
    ) -> Type:
        """Infer the result type of a function call."""
        if callee_type.kind == TypeKind.ANY:
            return TYPE_ANY

        if callee_type.kind == TypeKind.FUNCTION:
            if len(arg_types) != len(callee_type.param_types):
                self.diagnostics.wrong_arg_count(
                    location, len(callee_type.param_types), len(arg_types),
                )
                return callee_type.return_type

            for i, (arg_t, param_t) in enumerate(zip(arg_types, callee_type.param_types)):
                if not arg_t.is_assignable_to(param_t):
                    self.diagnostics.error(
                        TypeErrorCode.TYP103_ARGUMENT_TYPE_MISMATCH,
                        location,
                        i + 1, str(param_t), str(arg_t),
                        expected_type=param_t,
                        actual_type=arg_t,
                    )

            return callee_type.return_type

        if callee_type.kind == TypeKind.CLASS:
            return callee_type

        self.diagnostics.not_callable(location, callee_type)
        return TYPE_UNKNOWN

    def infer_method_call(
        self,
        object_type: Type,
        method_name: str,
        arg_types: List[Type],
        location: TypeLocation,
    ) -> Type:
        """Infer the result type of a method call."""
        if object_type.kind == TypeKind.ANY:
            return TYPE_ANY

        type_name = object_type.name
        methods = self.ctx.registry.get_methods(type_name)

        if method_name in methods:
            sig = methods[method_name]
            if len(arg_types) != len(sig.param_types):
                self.diagnostics.wrong_arg_count(
                    location, len(sig.param_types), len(arg_types),
                )
            return sig.return_type

        # Check parent types
        parent = self.ctx.registry.get_parent(type_name)
        while parent:
            parent_methods = self.ctx.registry.get_methods(parent)
            if method_name in parent_methods:
                sig = parent_methods[method_name]
                return sig.return_type
            parent = self.ctx.registry.get_parent(parent)

        self.diagnostics.error(
            TypeErrorCode.TYP254_UNDEFINED_METHOD,
            location,
            method_name, type_name,
            related_symbols=[type_name],
        )
        return TYPE_UNKNOWN

    def infer_index(
        self,
        object_type: Type,
        index_type: Type,
        location: TypeLocation,
    ) -> Type:
        """Infer the result type of an index expression."""
        if object_type.kind == TypeKind.ANY:
            return TYPE_ANY

        if object_type.kind == TypeKind.LIST:
            if not index_type.is_numeric:
                self.diagnostics.error(
                    TypeErrorCode.TYP203_INDEX_MUST_BE_NUMERIC,
                    location,
                    actual_type=index_type,
                )
            return object_type.element_type

        if object_type.kind == TypeKind.MAP:
            self.solver.add_equality(
                index_type, object_type.key_type, "index_key",
            )
            return object_type.value_type

        if object_type.kind == TypeKind.STRING:
            return TYPE_STRING

        if object_type.kind == TypeKind.TUPLE:
            if index_type.kind == TypeKind.INT:
                idx_val = getattr(index_type, 'value', None)
                if idx_val is not None and 0 <= idx_val < len(object_type.element_types):
                    return object_type.element_types[idx_val]
            return TYPE_ANY

        self.diagnostics.error(
            TypeErrorCode.TYP202_CANNOT_INDEX,
            location,
            str(object_type),
            actual_type=object_type,
        )
        return TYPE_UNKNOWN

    # ── If Expression Inference ───────────────────────────────────

    def infer_if_expr(
        self,
        then_type: Type,
        else_type: Optional[Type],
        location: TypeLocation,
    ) -> Type:
        """Infer type of an if expression."""
        if else_type is None:
            return OptionalType(then_type)

        unified = common_type(then_type, else_type)
        if unified:
            return unified

        self.solver.add_equality(then_type, else_type, "if_expr_branches")
        return then_type

    # ── Constraint Solving ────────────────────────────────────────

    def solve_constraints(self) -> Dict[str, Type]:
        """
        Solve all collected constraints.
        Returns the resolved type variable bindings.
        """
        substitution = self.solver.solve()
        result: Dict[str, Type] = {}
        for name in substitution.bindings:
            resolved = substitution.resolve(TypeVariable(name))
            if resolved.kind != TypeKind.TYPE_VAR:
                result[name] = resolved
        return result

    def get_inferred_type(self, type_var: TypeVariable) -> Type:
        """Get the resolved type for a type variable."""
        return self.solver.resolve_type(type_var)

    @property
    def constraint_count(self) -> int:
        """Number of constraints collected."""
        return len(self.solver._constraints)

    @property
    def type_var_count(self) -> int:
        """Number of type variables created."""
        return self._type_var_counter

    def infer_set_literal(self, element_types: List[Type]) -> 'SetType':
        """Infer type of a set literal."""
        if not element_types:
            return SetType(self.new_type_var("_Elem"))
        first = element_types[0]
        for elem in element_types[1:]:
            unified = common_type(first, elem)
            if unified:
                first = unified
        return SetType(first)

    def infer_range_type(self, start_type: Type, end_type: Type) -> 'RangeType':
        """Infer the type of a range expression."""
        elem = common_type(start_type, end_type)
        if elem and elem.is_numeric:
            return RangeType(elem)
        return RangeType(self.new_type_var("_RangeElem"))

    def infer_ternary(
        self,
        cond_type: Type,
        then_type: Type,
        else_type: Type,
        location: TypeLocation,
    ) -> Type:
        """Infer type of a ternary/conditional expression."""
        unified = common_type(then_type, else_type)
        if unified:
            return unified
        self.solver.add_equality(then_type, else_type, "ternary_branches")
        return then_type

    # ── Reset ─────────────────────────────────────────────────────

    def reset(self) -> None:
        """Reset the inference engine for a new analysis pass."""
        self.solver.clear()
        self._type_var_counter = 0
        self._inferred_cache.clear()
