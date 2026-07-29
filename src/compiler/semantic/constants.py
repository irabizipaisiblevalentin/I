"""
Compile-time Constant Evaluation

Evaluates expressions that can be resolved at compile time:
numbers, booleans, strings, arithmetic, comparisons, logical operations.
"""

from __future__ import annotations

from typing import Any, Optional, Tuple

from ..ast.nodes import (
    ASTNode, LiteralExpr, IdentifierExpr, BinaryExpr, UnaryExpr,
    LogicalExpr, GroupingExpr,
)


def is_constant_expression(node: ASTNode) -> bool:
    """
    Check if an AST node represents a compile-time constant expression.
    """
    if isinstance(node, LiteralExpr):
        return True
    if isinstance(node, GroupingExpr):
        return is_constant_expression(node.expression)
    if isinstance(node, BinaryExpr):
        return (is_constant_expression(node.left) and
                is_constant_expression(node.right))
    if isinstance(node, UnaryExpr):
        return is_constant_expression(node.right)
    if isinstance(node, LogicalExpr):
        return (is_constant_expression(node.left) and
                is_constant_expression(node.right))
    return False


def evaluate_constant(node: ASTNode) -> Tuple[bool, Any]:
    """
    Attempt to evaluate an AST node as a compile-time constant.
    Returns (success, value).
    """
    if isinstance(node, LiteralExpr):
        return True, node.value

    if isinstance(node, GroupingExpr):
        return evaluate_constant(node.expression)

    if isinstance(node, UnaryExpr):
        success, val = evaluate_constant(node.right)
        if not success:
            return False, None
        op = node.operator
        if isinstance(op, str):
            op_str = op
        else:
            op_str = getattr(op, 'lexeme', str(op))
        if op_str == '-' or op_str == 'MINUS':
            if isinstance(val, (int, float)):
                return True, -val
        if op_str == '!' or op_str == 'si':
            if isinstance(val, bool):
                return True, not val
        return False, None

    if isinstance(node, BinaryExpr):
        left_ok, left_val = evaluate_constant(node.left)
        right_ok, right_val = evaluate_constant(node.right)
        if not left_ok or not right_ok:
            return False, None
        op = node.operator
        if isinstance(op, str):
            op_str = op
        else:
            op_str = getattr(op, 'lexeme', str(op))
        return _eval_binary(op_str, left_val, right_val)

    if isinstance(node, LogicalExpr):
        left_ok, left_val = evaluate_constant(node.left)
        right_ok, right_val = evaluate_constant(node.right)
        if not left_ok or not right_ok:
            return False, None
        op = node.operator
        if isinstance(op, str):
            op_str = op
        else:
            op_str = getattr(op, 'lexeme', str(op))
        if op_str in ('kandi', '&&', 'and'):
            return True, bool(left_val and right_val)
        if op_str in ('cyangwa', '||', 'or'):
            return True, bool(left_val or right_val)
        return False, None

    return False, None


def _eval_binary(op: str, left: Any, right: Any) -> Tuple[bool, Any]:
    """Evaluate a binary operation on constant values."""
    # Arithmetic
    if op == '+':
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return True, left + right
        if isinstance(left, str) and isinstance(right, str):
            return True, left + right
    if op == '-':
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return True, left - right
    if op == '*':
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return True, left * right
    if op == '/':
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            if right == 0:
                return False, None  # Division by zero
            return True, left / right
    if op == '%':
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            if right == 0:
                return False, None
            return True, left % right
    if op == '**':
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return True, left ** right

    # Comparison
    if op == '==':
        return True, left == right
    if op == '!=':
        return True, left != right
    if op == '>':
        return True, left > right
    if op == '<':
        return True, left < right
    if op == '>=':
        return True, left >= right
    if op == '<=':
        return True, left <= right

    # Bitwise
    if op == '&':
        if isinstance(left, int) and isinstance(right, int):
            return True, left & right
    if op == '|':
        if isinstance(left, int) and isinstance(right, int):
            return True, left | right
    if op == '^':
        if isinstance(left, int) and isinstance(right, int):
            return True, left ^ right
    if op == '<<':
        if isinstance(left, int) and isinstance(right, int):
            return True, left << right
    if op == '>>':
        if isinstance(left, int) and isinstance(right, int):
            return True, left >> right

    return False, None


def get_constant_value(node: ASTNode) -> Optional[Any]:
    """Try to get the constant value of a node, returning None if not constant."""
    success, value = evaluate_constant(node)
    return value if success else None
