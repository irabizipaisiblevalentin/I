"""
Compile-Time Evaluation for the I Programming Language

Evaluates constant expressions at compile time, supporting:
- Compile-time constants
- Arithmetic expressions
- String operations
- Boolean logic
- Type assertions
- Future macros and metaprogramming
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

from .types import Type, TypeKind, TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_STRING, TYPE_NONE
from .diagnostics import TypeDiagnostics, TypeErrorCode, TypeLocation


# ══════════════════════════════════════════════════════════════════
# Compile-Time Value
# ══════════════════════════════════════════════════════════════════


class ConstValueKind(Enum):
    """Classification of compile-time values."""

    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    STRING = auto()
    NONE = auto()
    ERROR = auto()


@dataclass
class ConstValue:
    """A compile-time computed value."""

    kind: ConstValueKind
    value: Any = None
    type: Optional[Type] = None
    is_error: bool = False
    error_message: str = ""

    @classmethod
    def int_val(cls, value: int) -> ConstValue:
        return cls(ConstValueKind.INT, value, TYPE_INT)

    @classmethod
    def float_val(cls, value: float) -> ConstValue:
        return cls(ConstValueKind.FLOAT, value, TYPE_FLOAT)

    @classmethod
    def bool_val(cls, value: bool) -> ConstValue:
        return cls(ConstValueKind.BOOL, value, TYPE_BOOL)

    @classmethod
    def string_val(cls, value: str) -> ConstValue:
        return cls(ConstValueKind.STRING, value, TYPE_STRING)

    @classmethod
    def none_val(cls) -> ConstValue:
        return cls(ConstValueKind.NONE, None, TYPE_NONE)

    @classmethod
    def error(cls, message: str) -> ConstValue:
        return cls(ConstValueKind.ERROR, None, None, True, message)

    @property
    def is_numeric(self) -> bool:
        return self.kind in (ConstValueKind.INT, ConstValueKind.FLOAT)

    def __repr__(self) -> str:
        if self.is_error:
            return f"ConstValue(ERROR: {self.error_message})"
        return f"ConstValue({self.value})"


# ══════════════════════════════════════════════════════════════════
# Compile-Time Evaluator
# ══════════════════════════════════════════════════════════════════


class CompileTimeEvaluator:
    """
    Evaluates expressions at compile time.

    The evaluator processes AST nodes representing constant expressions
    and produces compile-time values. Used for:
    - Constant declarations
    - Default parameter values
    - Array sizes
    - Type-level computations
    """

    def __init__(self, diagnostics: TypeDiagnostics) -> None:
        self.diagnostics = diagnostics
        self._constants: Dict[str, ConstValue] = {}
        self._evaluation_count = 0

    def define_constant(self, name: str, value: ConstValue) -> None:
        """Register a compile-time constant."""
        self._constants[name] = value

    def get_constant(self, name: str) -> Optional[ConstValue]:
        """Look up a compile-time constant."""
        return self._constants.get(name)

    # ── Arithmetic Evaluation ─────────────────────────────────────

    def eval_add(self, left: ConstValue, right: ConstValue,
                 location: TypeLocation) -> ConstValue:
        """Evaluate addition at compile time."""
        self._evaluation_count += 1

        if left.is_error or right.is_error:
            return left if left.is_error else right

        if left.kind == ConstValueKind.INT and right.kind == ConstValueKind.INT:
            try:
                result = left.value + right.value
                return ConstValue.int_val(result)
            except OverflowError:
                self.diagnostics.error(
                    TypeErrorCode.TYP703_OVERFLOW, location,
                )
                return ConstValue.error("integer overflow")

        if left.kind == ConstValueKind.FLOAT and right.kind == ConstValueKind.FLOAT:
            return ConstValue.float_val(left.value + right.value)

        if left.kind == ConstValueKind.INT and right.kind == ConstValueKind.FLOAT:
            return ConstValue.float_val(float(left.value) + right.value)

        if left.kind == ConstValueKind.FLOAT and right.kind == ConstValueKind.INT:
            return ConstValue.float_val(left.value + float(right.value))

        if left.kind == ConstValueKind.STRING and right.kind == ConstValueKind.STRING:
            return ConstValue.string_val(left.value + right.value)

        return ConstValue.error("cannot add non-numeric/non-string types")

    def eval_subtract(self, left: ConstValue, right: ConstValue,
                      location: TypeLocation) -> ConstValue:
        """Evaluate subtraction at compile time."""
        self._evaluation_count += 1

        if left.is_error or right.is_error:
            return left if left.is_error else right

        if left.kind == ConstValueKind.INT and right.kind == ConstValueKind.INT:
            try:
                result = left.value - right.value
                return ConstValue.int_val(result)
            except OverflowError:
                self.diagnostics.error(
                    TypeErrorCode.TYP703_OVERFLOW, location,
                )
                return ConstValue.error("integer overflow")

        if left.kind == ConstValueKind.FLOAT and right.kind == ConstValueKind.FLOAT:
            return ConstValue.float_val(left.value - right.value)

        return ConstValue.error("cannot subtract non-numeric types")

    def eval_multiply(self, left: ConstValue, right: ConstValue,
                      location: TypeLocation) -> ConstValue:
        """Evaluate multiplication at compile time."""
        self._evaluation_count += 1

        if left.is_error or right.is_error:
            return left if left.is_error else right

        if left.kind == ConstValueKind.INT and right.kind == ConstValueKind.INT:
            try:
                result = left.value * right.value
                return ConstValue.int_val(result)
            except OverflowError:
                self.diagnostics.error(
                    TypeErrorCode.TYP703_OVERFLOW, location,
                )
                return ConstValue.error("integer overflow")

        if left.kind == ConstValueKind.FLOAT and right.kind == ConstValueKind.FLOAT:
            return ConstValue.float_val(left.value * right.value)

        return ConstValue.error("cannot multiply non-numeric types")

    def eval_divide(self, left: ConstValue, right: ConstValue,
                    location: TypeLocation) -> ConstValue:
        """Evaluate division at compile time."""
        self._evaluation_count += 1

        if left.is_error or right.is_error:
            return left if left.is_error else right

        if right.kind == ConstValueKind.INT and right.value == 0:
            self.diagnostics.error(
                TypeErrorCode.TYP702_DIVISION_BY_ZERO, location,
            )
            return ConstValue.error("division by zero")

        if right.kind == ConstValueKind.FLOAT and right.value == 0.0:
            self.diagnostics.error(
                TypeErrorCode.TYP702_DIVISION_BY_ZERO, location,
            )
            return ConstValue.error("division by zero")

        if left.kind == ConstValueKind.INT and right.kind == ConstValueKind.INT:
            if right.value == 0:
                self.diagnostics.error(
                    TypeErrorCode.TYP702_DIVISION_BY_ZERO, location,
                )
                return ConstValue.error("division by zero")
            return ConstValue.int_val(left.value // right.value)

        if left.kind in (ConstValueKind.INT, ConstValueKind.FLOAT) and \
           right.kind in (ConstValueKind.INT, ConstValueKind.FLOAT):
            l_val = float(left.value)
            r_val = float(right.value)
            if r_val == 0.0:
                self.diagnostics.error(
                    TypeErrorCode.TYP702_DIVISION_BY_ZERO, location,
                )
                return ConstValue.error("division by zero")
            return ConstValue.float_val(l_val / r_val)

        return ConstValue.error("cannot divide non-numeric types")

    def eval_modulo(self, left: ConstValue, right: ConstValue,
                    location: TypeLocation) -> ConstValue:
        """Evaluate modulo at compile time."""
        self._evaluation_count += 1

        if left.is_error or right.is_error:
            return left if left.is_error else right

        if right.kind == ConstValueKind.INT and right.value == 0:
            self.diagnostics.error(
                TypeErrorCode.TYP702_DIVISION_BY_ZERO, location,
            )
            return ConstValue.error("modulo by zero")

        if left.kind == ConstValueKind.INT and right.kind == ConstValueKind.INT:
            return ConstValue.int_val(left.value % right.value)

        return ConstValue.error("modulo requires integer types")

    def eval_power(self, left: ConstValue, right: ConstValue,
                   location: TypeLocation) -> ConstValue:
        """Evaluate exponentiation at compile time."""
        self._evaluation_count += 1

        if left.is_error or right.is_error:
            return left if left.is_error else right

        if left.kind == ConstValueKind.INT and right.kind == ConstValueKind.INT:
            if right.value < 0:
                return ConstValue.float_val(float(left.value) ** right.value)
            try:
                result = left.value ** right.value
                return ConstValue.int_val(result)
            except OverflowError:
                self.diagnostics.error(
                    TypeErrorCode.TYP703_OVERFLOW, location,
                )
                return ConstValue.error("integer overflow")

        if left.kind in (ConstValueKind.INT, ConstValueKind.FLOAT) and \
           right.kind in (ConstValueKind.INT, ConstValueKind.FLOAT):
            return ConstValue.float_val(float(left.value) ** float(right.value))

        return ConstValue.error("cannot exponentiate non-numeric types")

    # ── Comparison Evaluation ─────────────────────────────────────

    def eval_equal(self, left: ConstValue, right: ConstValue) -> ConstValue:
        """Evaluate equality at compile time."""
        if left.is_error or right.is_error:
            return ConstValue.bool_val(False)
        return ConstValue.bool_val(left.value == right.value)

    def eval_not_equal(self, left: ConstValue, right: ConstValue) -> ConstValue:
        """Evaluate inequality at compile time."""
        if left.is_error or right.is_error:
            return ConstValue.bool_val(True)
        return ConstValue.bool_val(left.value != right.value)

    def eval_less(self, left: ConstValue, right: ConstValue) -> ConstValue:
        """Evaluate less-than at compile time."""
        if left.is_error or right.is_error:
            return ConstValue.bool_val(False)
        if left.is_numeric and right.is_numeric:
            return ConstValue.bool_val(left.value < right.value)
        return ConstValue.error("comparison requires numeric types")

    def eval_less_equal(self, left: ConstValue, right: ConstValue) -> ConstValue:
        """Evaluate less-or-equal at compile time."""
        if left.is_error or right.is_error:
            return ConstValue.bool_val(False)
        if left.is_numeric and right.is_numeric:
            return ConstValue.bool_val(left.value <= right.value)
        return ConstValue.error("comparison requires numeric types")

    def eval_greater(self, left: ConstValue, right: ConstValue) -> ConstValue:
        """Evaluate greater-than at compile time."""
        if left.is_error or right.is_error:
            return ConstValue.bool_val(False)
        if left.is_numeric and right.is_numeric:
            return ConstValue.bool_val(left.value > right.value)
        return ConstValue.error("comparison requires numeric types")

    def eval_greater_equal(self, left: ConstValue, right: ConstValue) -> ConstValue:
        """Evaluate greater-or-equal at compile time."""
        if left.is_error or right.is_error:
            return ConstValue.bool_val(False)
        if left.is_numeric and right.is_numeric:
            return ConstValue.bool_val(left.value >= right.value)
        return ConstValue.error("comparison requires numeric types")

    # ── Boolean Evaluation ────────────────────────────────────────

    def eval_and(self, left: ConstValue, right: ConstValue) -> ConstValue:
        """Evaluate logical AND at compile time."""
        if left.kind == ConstValueKind.BOOL and right.kind == ConstValueKind.BOOL:
            return ConstValue.bool_val(left.value and right.value)
        return ConstValue.error("logical AND requires boolean operands")

    def eval_or(self, left: ConstValue, right: ConstValue) -> ConstValue:
        """Evaluate logical OR at compile time."""
        if left.kind == ConstValueKind.BOOL and right.kind == ConstValueKind.BOOL:
            return ConstValue.bool_val(left.value or right.value)
        return ConstValue.error("logical OR requires boolean operands")

    def eval_not(self, operand: ConstValue) -> ConstValue:
        """Evaluate logical NOT at compile time."""
        if operand.kind == ConstValueKind.BOOL:
            return ConstValue.bool_val(not operand.value)
        return ConstValue.error("logical NOT requires boolean operand")

    def eval_negate(self, operand: ConstValue, location: TypeLocation) -> ConstValue:
        """Evaluate arithmetic negation at compile time."""
        self._evaluation_count += 1
        if operand.kind == ConstValueKind.INT:
            return ConstValue.int_val(-operand.value)
        if operand.kind == ConstValueKind.FLOAT:
            return ConstValue.float_val(-operand.value)
        return ConstValue.error("negation requires numeric type")

    # ── Compile-Time Assertions ───────────────────────────────────

    def eval_assert(
        self,
        condition: ConstValue,
        message: Optional[str],
        location: TypeLocation,
    ) -> ConstValue:
        """Evaluate a compile-time assertion."""
        if condition.kind != ConstValueKind.BOOL:
            self.diagnostics.error(
                TypeErrorCode.TYP701_CONST_ASSERT_FAILED, location,
            )
            return ConstValue.error("assertion condition must be boolean")

        if not condition.value:
            msg = message or "compile-time assertion failed"
            self.diagnostics.error(
                TypeErrorCode.TYP701_CONST_ASSERT_FAILED, location,
                msg,
            )
            return ConstValue.error(msg)

        return ConstValue.none_val()

    # ── Query ─────────────────────────────────────────────────────

    @property
    def evaluation_count(self) -> int:
        return self._evaluation_count

    def is_constant_expression(self, name: str) -> bool:
        """Check if a name refers to a compile-time constant."""
        return name in self._constants

    def eval_string_equal(self, left: ConstValue, right: ConstValue) -> ConstValue:
        """Evaluate string equality at compile time."""
        if left.kind == ConstValueKind.STRING and right.kind == ConstValueKind.STRING:
            return ConstValue.bool_val(left.value == right.value)
        return ConstValue.error("string equality requires string operands")

    def eval_string_not_equal(self, left: ConstValue, right: ConstValue) -> ConstValue:
        """Evaluate string inequality at compile time."""
        result = self.eval_string_equal(left, right)
        if result.kind == ConstValueKind.BOOL:
            return ConstValue.bool_val(not result.value)
        return result

    def eval_string_concat(self, left: ConstValue, right: ConstValue) -> ConstValue:
        """Evaluate string concatenation at compile time."""
        if left.kind == ConstValueKind.STRING and right.kind == ConstValueKind.STRING:
            return ConstValue.string_val(left.value + right.value)
        return ConstValue.error("string concatenation requires string operands")

    def eval_ternary(
        self,
        condition: ConstValue,
        then_val: ConstValue,
        else_val: ConstValue,
        location: TypeLocation,
    ) -> ConstValue:
        """Evaluate a ternary expression at compile time."""
        if condition.kind != ConstValueKind.BOOL:
            return ConstValue.error("ternary condition must be boolean")
        return then_val if condition.value else else_val

    def eval_typeof(self, value: ConstValue) -> ConstValue:
        """Evaluate a typeof compile-time operation."""
        if value.type:
            return ConstValue.string_val(value.type.name)
        return ConstValue.string_val("unknown")

    @property
    def constant_count(self) -> int:
        """Number of registered constants."""
        return len(self._constants)

    def clear(self) -> None:
        """Reset all state."""
        self._constants.clear()
        self._evaluation_count = 0
