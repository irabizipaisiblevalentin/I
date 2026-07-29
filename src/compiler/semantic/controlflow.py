"""
Control Flow Validation

Validates return statements, unreachable code, break/continue usage,
and loop nesting for the I programming language.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Set

from ..ast.nodes import (
    ASTNode, Stmt, BlockStmt, IfStmt, WhileStmt, UntilStmt,
    ForStmt, ForEachStmt, ReturnStmt, BreakStmt, ContinueStmt,
    ThrowStmt, FunctionDecl, MethodDecl, TryStmt, ElifBranch,
)


class FlowState(Enum):
    """Control flow state for a code path."""
    NORMAL = auto()
    RETURNS = auto()
    THROWS = auto()
    TERMINATES = auto()
    ALL_RETURN = auto()


@dataclass
class FlowAnalysis:
    """Result of control flow analysis for a code path."""
    state: FlowState = FlowState.NORMAL
    has_return: bool = False
    has_break: bool = False
    has_continue: bool = False
    all_paths_return: bool = False
    unreachable_statements: List[ASTNode] = field(default_factory=list)


def analyze_function_flow(func_body: BlockStmt) -> FlowAnalysis:
    """
    Analyze the control flow of a function body.
    Returns the flow analysis indicating if the function always returns.
    """
    result = FlowAnalysis()
    final_state = _analyze_block_flow(func_body, result)
    result.state = final_state
    result.all_paths_return = _paths_always_return(final_state)
    return result


def _analyze_block_flow(block: BlockStmt, result: FlowAnalysis) -> FlowState:
    """Analyze control flow through a block, returning the terminal state."""
    current_state = FlowState.NORMAL

    for stmt in block.statements:
        if current_state != FlowState.NORMAL:
            result.unreachable_statements.append(stmt)

        state = _analyze_stmt_flow(stmt, result)
        if state != FlowState.NORMAL:
            current_state = state

    return current_state


def _analyze_stmt_flow(stmt: Stmt, result: FlowAnalysis) -> FlowState:
    """Analyze control flow for a single statement."""
    if isinstance(stmt, ReturnStmt):
        result.has_return = True
        return FlowState.RETURNS

    if isinstance(stmt, ThrowStmt):
        return FlowState.THROWS

    if isinstance(stmt, BreakStmt):
        result.has_break = True
        return FlowState.TERMINATES

    if isinstance(stmt, ContinueStmt):
        result.has_continue = True
        return FlowState.TERMINATES

    if isinstance(stmt, BlockStmt):
        return _analyze_block_flow(stmt, result)

    if isinstance(stmt, IfStmt):
        then_state = _analyze_block_flow(stmt.then_branch, result)
        elif_states = []
        for elif_branch in stmt.elif_branches:
            elif_states.append(_analyze_block_flow(elif_branch.body, result))

        if stmt.else_branch:
            else_state = _analyze_block_flow(stmt.else_branch, result)
            all_branches = [then_state] + elif_states + [else_state]
            if all(s != FlowState.NORMAL for s in all_branches):
                return FlowState.ALL_RETURN
        # No else branch: control may flow past the if

        return FlowState.NORMAL

    if isinstance(stmt, WhileStmt) or isinstance(stmt, UntilStmt):
        _analyze_block_flow(stmt.body, result)
        return FlowState.NORMAL

    if isinstance(stmt, ForStmt) or isinstance(stmt, ForEachStmt):
        _analyze_block_flow(stmt.body, result)
        return FlowState.NORMAL

    if isinstance(stmt, TryStmt):
        try_state = _analyze_block_flow(stmt.try_body, result)
        catch_state = FlowState.NORMAL
        if stmt.catch_body:
            catch_state = _analyze_block_flow(stmt.catch_body, result)
        finally_state = FlowState.NORMAL
        if stmt.finally_body:
            finally_state = _analyze_block_flow(stmt.finally_body, result)
        if (try_state != FlowState.NORMAL and
            catch_state != FlowState.NORMAL and
            finally_state != FlowState.NORMAL):
            return FlowState.ALL_RETURN
        return FlowState.NORMAL

    return FlowState.NORMAL


def _paths_always_return(state: FlowState) -> bool:
    """Check if the given state means all paths return."""
    return state in (FlowState.RETURNS, FlowState.THROWS, FlowState.ALL_RETURN)


def function_always_returns(func_body: BlockStmt) -> bool:
    """Check if a function body always returns a value on all paths."""
    analysis = analyze_function_flow(func_body)
    return analysis.all_paths_return


def get_unreachable_code(func_body: BlockStmt) -> List[ASTNode]:
    """Get a list of unreachable statements in a function body."""
    analysis = analyze_function_flow(func_body)
    return analysis.unreachable_statements
