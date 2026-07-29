"""
AST Visitor Implementations for the I Programming Language

Provides concrete visitor implementations:
- ASTWalker: walks the tree without modifying it
- ASTTransformer: transforms nodes into new nodes
- PrettyPrinter: human-readable AST output
- DebugPrinter: detailed debug output with node IDs
"""

from __future__ import annotations

from abc import ABC
from typing import Any, List, Optional

from .nodes import (
    ASTNode,
    ASTVisitor,
    AssignmentExpr,
    BinaryExpr,
    BlockStmt,
    BreakStmt,
    CallExpr,
    ClassDecl,
    CompoundAssignmentExpr,
    ConstructorExpr,
    ContinueStmt,
    Decl,
    DictExpr,
    ElifBranch,
    EmptyStmt,
    EnumDecl,
    EnumVariant,
    Expr,
    ExportDecl,
    ExpressionStmt,
    ForEachStmt,
    ForStmt,
    FunctionDecl,
    FunctionType,
    GetExpr,
    GenericType,
    GroupingExpr,
    IfExpr,
    IfStmt,
    IdentifierExpr,
    ImportDecl,
    IndexExpr,
    InterfaceDecl,
    LambdaExpr,
    ListExpr,
    LiteralExpr,
    LogicalExpr,
    MethodCallExpr,
    MethodDecl,
    Module,
    NamedType,
    OptionalType,
    Parameter,
    PlaceholderExpr,
    Program,
    ReturnStmt,
    SetExpr,
    SliceExpr,
    StructDecl,
    StructField,
    SuperExpr,
    SelfExpr,
    Stmt,
    ThrowStmt,
    TryStmt,
    TupleExpr,
    TupleType,
    TypeNode,
    UnaryExpr,
    UntilStmt,
    VarDecl,
    WhileStmt,
)


# ══════════════════════════════════════════════════════════════════
# ASTWalker — walk the tree, collecting results
# ══════════════════════════════════════════════════════════════════


class ASTWalker(ASTVisitor):
    """
    Walks every node in the AST, calling a callback for each.
    Does not modify the tree.

    Usage:
        walker = ASTWalker()
        walker.on_enter(lambda node: print(f"enter: {node.node_type}"))
        walker.on_exit(lambda node: print(f"exit: {node.node_type}"))
        walker.walk(program)
    """

    def __init__(self) -> None:
        self._enter_callbacks: List[Any] = []
        self._exit_callbacks: List[Any] = []
        self._node_stack: List[ASTNode] = []
        self._results: List[Any] = []

    def on_enter(self, callback: Any) -> None:
        """Register a callback invoked when entering a node."""
        self._enter_callbacks.append(callback)

    def on_exit(self, callback: Any) -> None:
        """Register a callback invoked when exiting a node."""
        self._exit_callbacks.append(callback)

    def walk(self, node: ASTNode) -> List[Any]:
        """Walk the AST rooted at `node` and return collected results."""
        self._results.clear()
        node.accept(self)
        return list(self._results)

    def _enter(self, node: ASTNode) -> None:
        self._node_stack.append(node)
        for cb in self._enter_callbacks:
            cb(node)

    def _exit(self, node: ASTNode) -> None:
        for cb in self._exit_callbacks:
            cb(node)
        self._node_stack.pop()

    def _walk_children(self, node: ASTNode) -> None:
        for child in node.children():
            child.accept(self)

    # ── Expressions ────────────────────────────────────────────

    def visit_literal_expr(self, expr: LiteralExpr) -> None:
        self._enter(expr); self._exit(expr)

    def visit_identifier_expr(self, expr: IdentifierExpr) -> None:
        self._enter(expr); self._exit(expr)

    def visit_unary_expr(self, expr: UnaryExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_binary_expr(self, expr: BinaryExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_logical_expr(self, expr: LogicalExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_assignment_expr(self, expr: AssignmentExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_compound_assignment_expr(self, expr: CompoundAssignmentExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_call_expr(self, expr: CallExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_method_call_expr(self, expr: MethodCallExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_constructor_expr(self, expr: ConstructorExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_get_expr(self, expr: GetExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_set_expr(self, expr: SetExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_index_expr(self, expr: IndexExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_slice_expr(self, expr: SliceExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_self_expr(self, expr: SelfExpr) -> None:
        self._enter(expr); self._exit(expr)

    def visit_super_expr(self, expr: SuperExpr) -> None:
        self._enter(expr); self._exit(expr)

    def visit_list_expr(self, expr: ListExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_dict_expr(self, expr: DictExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_tuple_expr(self, expr: TupleExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_lambda_expr(self, expr: LambdaExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_if_expr(self, expr: IfExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_grouping_expr(self, expr: GroupingExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit(expr)

    def visit_placeholder_expr(self, expr: PlaceholderExpr) -> None:
        self._enter(expr); self._exit(expr)

    # ── Types ──────────────────────────────────────────────────

    def visit_named_type(self, t: NamedType) -> None:
        self._enter(t); self._exit(t)

    def visit_generic_type(self, t: GenericType) -> None:
        self._enter(t); self._walk_children(t); self._exit(t)

    def visit_function_type(self, t: FunctionType) -> None:
        self._enter(t); self._walk_children(t); self._exit(t)

    def visit_optional_type(self, t: OptionalType) -> None:
        self._enter(t); self._walk_children(t); self._exit(t)

    def visit_tuple_type(self, t: TupleType) -> None:
        self._enter(t); self._walk_children(t); self._exit(t)

    # ── Declarations ───────────────────────────────────────────

    def visit_var_decl(self, decl: VarDecl) -> None:
        self._enter(decl); self._walk_children(decl); self._exit(decl)

    def visit_function_decl(self, decl: FunctionDecl) -> None:
        self._enter(decl); self._walk_children(decl); self._exit(decl)

    def visit_method_decl(self, decl: MethodDecl) -> None:
        self._enter(decl); self._walk_children(decl); self._exit(decl)

    def visit_struct_decl(self, decl: StructDecl) -> None:
        self._enter(decl); self._walk_children(decl); self._exit(decl)

    def visit_enum_decl(self, decl: EnumDecl) -> None:
        self._enter(decl); self._walk_children(decl); self._exit(decl)

    def visit_class_decl(self, decl: ClassDecl) -> None:
        self._enter(decl); self._walk_children(decl); self._exit(decl)

    def visit_trait_decl(self, decl: TraitDecl) -> None:
        self._enter(decl); self._walk_children(decl); self._exit(decl)

    def visit_interface_decl(self, decl: InterfaceDecl) -> None:
        self._enter(decl); self._walk_children(decl); self._exit(decl)

    def visit_import_decl(self, decl: ImportDecl) -> None:
        self._enter(decl); self._exit(decl)

    def visit_export_decl(self, decl: ExportDecl) -> None:
        self._enter(decl); self._exit(decl)

    # ── Statements ─────────────────────────────────────────────

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit(stmt)

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit(stmt)

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit(stmt)

    def visit_until_stmt(self, stmt: UntilStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit(stmt)

    def visit_for_stmt(self, stmt: ForStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit(stmt)

    def visit_for_each_stmt(self, stmt: ForEachStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit(stmt)

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit(stmt)

    def visit_break_stmt(self, stmt: BreakStmt) -> None:
        self._enter(stmt); self._exit(stmt)

    def visit_continue_stmt(self, stmt: ContinueStmt) -> None:
        self._enter(stmt); self._exit(stmt)

    def visit_throw_stmt(self, stmt: ThrowStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit(stmt)

    def visit_try_stmt(self, stmt: TryStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit(stmt)

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit(stmt)

    def visit_empty_stmt(self, stmt: EmptyStmt) -> None:
        self._enter(stmt); self._exit(stmt)

    # ── Root ───────────────────────────────────────────────────

    def visit_program(self, program: Program) -> None:
        self._enter(program); self._walk_children(program); self._exit(program)

    def visit_module(self, module: Module) -> None:
        self._enter(module); self._walk_children(module); self._exit(module)

    # ── Helpers ────────────────────────────────────────────────

    def visit_parameter(self, param: Parameter) -> None:
        self._enter(param); self._walk_children(param); self._exit(param)

    def visit_struct_field(self, field: StructField) -> None:
        self._enter(field); self._walk_children(field); self._exit(field)

    def visit_enum_variant(self, variant: EnumVariant) -> None:
        self._enter(variant); self._walk_children(variant); self._exit(variant)

    def visit_elif_branch(self, branch: ElifBranch) -> None:
        self._enter(branch); self._walk_children(branch); self._exit(branch)


# ══════════════════════════════════════════════════════════════════
# ASTTransformer — replace nodes with new nodes
# ══════════════════════════════════════════════════════════════════


class ASTTransformer(ASTVisitor):
    """
    Walks the AST and allows replacing any node.
    Subclass and override specific visit methods to transform.

    Usage:
        class ConstantFolder(ASTTransformer):
            def visit_binary_expr(self, expr):
                if isinstance(expr.left, LiteralExpr) and isinstance(expr.right, LiteralExpr):
                    # evaluate and return a new LiteralExpr
                    ...
                return expr  # unchanged
    """

    def transform(self, node: ASTNode) -> ASTNode:
        """Transform the AST rooted at `node` and return the (possibly new) root."""
        return node.accept(self)

    # ── Expressions ────────────────────────────────────────────

    def visit_literal_expr(self, expr: LiteralExpr) -> ASTNode:
        return expr

    def visit_identifier_expr(self, expr: IdentifierExpr) -> ASTNode:
        return expr

    def visit_unary_expr(self, expr: UnaryExpr) -> ASTNode:
        new_right = expr.right.accept(self)
        if new_right is expr.right:
            return expr
        return UnaryExpr(operator=expr.operator, right=new_right,
                         node_id=expr.node_id, location=expr.location)

    def visit_binary_expr(self, expr: BinaryExpr) -> ASTNode:
        new_left = expr.left.accept(self)
        new_right = expr.right.accept(self)
        if new_left is expr.left and new_right is expr.right:
            return expr
        return BinaryExpr(left=new_left, operator=expr.operator, right=new_right,
                          node_id=expr.node_id, location=expr.location)

    def visit_logical_expr(self, expr: LogicalExpr) -> ASTNode:
        new_left = expr.left.accept(self)
        new_right = expr.right.accept(self)
        if new_left is expr.left and new_right is expr.right:
            return expr
        return LogicalExpr(left=new_left, operator=expr.operator, right=new_right,
                           node_id=expr.node_id, location=expr.location)

    def visit_assignment_expr(self, expr: AssignmentExpr) -> ASTNode:
        new_target = expr.target.accept(self)
        new_value = expr.value.accept(self)
        if new_target is expr.target and new_value is expr.value:
            return expr
        return AssignmentExpr(target=new_target, value=new_value,
                              node_id=expr.node_id, location=expr.location)

    def visit_compound_assignment_expr(self, expr: CompoundAssignmentExpr) -> ASTNode:
        new_target = expr.target.accept(self)
        new_value = expr.value.accept(self)
        if new_target is expr.target and new_value is expr.value:
            return expr
        return CompoundAssignmentExpr(target=new_target, operator=expr.operator,
                                      value=new_value, node_id=expr.node_id,
                                      location=expr.location)

    def visit_call_expr(self, expr: CallExpr) -> ASTNode:
        new_callee = expr.callee.accept(self)
        new_args = [a.accept(self) for a in expr.arguments]
        if new_callee is expr.callee and new_args == expr.arguments:
            return expr
        return CallExpr(callee=new_callee, arguments=new_args,
                        node_id=expr.node_id, location=expr.location)

    def visit_method_call_expr(self, expr: MethodCallExpr) -> ASTNode:
        new_obj = expr.object.accept(self)
        new_args = [a.accept(self) for a in expr.arguments]
        if new_obj is expr.object and new_args == expr.arguments:
            return expr
        return MethodCallExpr(object=new_obj, method=expr.method,
                              arguments=new_args, node_id=expr.node_id,
                              location=expr.location)

    def visit_constructor_expr(self, expr: ConstructorExpr) -> ASTNode:
        new_args = [a.accept(self) for a in expr.arguments]
        if new_args == expr.arguments:
            return expr
        return ConstructorExpr(class_name=expr.class_name, arguments=new_args,
                               node_id=expr.node_id, location=expr.location)

    def visit_get_expr(self, expr: GetExpr) -> ASTNode:
        new_obj = expr.object.accept(self)
        if new_obj is expr.object:
            return expr
        return GetExpr(object=new_obj, property=expr.property,
                       node_id=expr.node_id, location=expr.location)

    def visit_set_expr(self, expr: SetExpr) -> ASTNode:
        new_obj = expr.object.accept(self)
        new_value = expr.value.accept(self)
        if new_obj is expr.object and new_value is expr.value:
            return expr
        return SetExpr(object=new_obj, property=expr.property, value=new_value,
                       node_id=expr.node_id, location=expr.location)

    def visit_index_expr(self, expr: IndexExpr) -> ASTNode:
        new_obj = expr.object.accept(self)
        new_idx = expr.index.accept(self)
        if new_obj is expr.object and new_idx is expr.index:
            return expr
        return IndexExpr(object=new_obj, index=new_idx,
                         node_id=expr.node_id, location=expr.location)

    def visit_slice_expr(self, expr: SliceExpr) -> ASTNode:
        new_obj = expr.object.accept(self)
        new_start = expr.start.accept(self) if expr.start else None
        new_end = expr.end.accept(self) if expr.end else None
        if (new_obj is expr.object and new_start is expr.start
                and new_end is expr.end):
            return expr
        return SliceExpr(object=new_obj, start=new_start, end=new_end,
                         node_id=expr.node_id, location=expr.location)

    def visit_self_expr(self, expr: SelfExpr) -> ASTNode:
        return expr

    def visit_super_expr(self, expr: SuperExpr) -> ASTNode:
        return expr

    def visit_list_expr(self, expr: ListExpr) -> ASTNode:
        new_elems = [e.accept(self) for e in expr.elements]
        if new_elems == expr.elements:
            return expr
        return ListExpr(elements=new_elems, node_id=expr.node_id,
                        location=expr.location)

    def visit_dict_expr(self, expr: DictExpr) -> ASTNode:
        new_keys = [k.accept(self) for k in expr.keys]
        new_vals = [v.accept(self) for v in expr.values]
        if new_keys == expr.keys and new_vals == expr.values:
            return expr
        return DictExpr(keys=new_keys, values=new_vals,
                        node_id=expr.node_id, location=expr.location)

    def visit_tuple_expr(self, expr: TupleExpr) -> ASTNode:
        new_elems = [e.accept(self) for e in expr.elements]
        if new_elems == expr.elements:
            return expr
        return TupleExpr(elements=new_elems, node_id=expr.node_id,
                         location=expr.location)

    def visit_lambda_expr(self, expr: LambdaExpr) -> ASTNode:
        new_params = [p.accept(self) for p in expr.parameters]
        new_body = expr.body.accept(self)
        if new_params == expr.parameters and new_body is expr.body:
            return expr
        return LambdaExpr(parameters=new_params, body=new_body,
                          node_id=expr.node_id, location=expr.location)

    def visit_if_expr(self, expr: IfExpr) -> ASTNode:
        new_cond = expr.condition.accept(self)
        new_then = expr.then_branch.accept(self)
        new_else = expr.else_branch.accept(self) if expr.else_branch else None
        if (new_cond is expr.condition and new_then is expr.then_branch
                and new_else is expr.else_branch):
            return expr
        return IfExpr(condition=new_cond, then_branch=new_then,
                      else_branch=new_else, node_id=expr.node_id,
                      location=expr.location)

    def visit_grouping_expr(self, expr: GroupingExpr) -> ASTNode:
        new_inner = expr.expression.accept(self)
        if new_inner is expr.expression:
            return expr
        return GroupingExpr(expression=new_inner, node_id=expr.node_id,
                            location=expr.location)

    def visit_placeholder_expr(self, expr: PlaceholderExpr) -> ASTNode:
        return expr

    # ── Types (no-op, return as-is) ───────────────────────────

    def visit_named_type(self, t: NamedType) -> ASTNode:
        return t

    def visit_generic_type(self, t: GenericType) -> ASTNode:
        return t

    def visit_function_type(self, t: FunctionType) -> ASTNode:
        return t

    def visit_optional_type(self, t: OptionalType) -> ASTNode:
        return t

    def visit_tuple_type(self, t: TupleType) -> ASTNode:
        return t

    # ── Declarations ───────────────────────────────────────────

    def visit_var_decl(self, decl: VarDecl) -> ASTNode:
        new_type = decl.type_annotation.accept(self) if decl.type_annotation else None
        new_init = decl.initializer.accept(self) if decl.initializer else None
        if new_type is decl.type_annotation and new_init is decl.initializer:
            return decl
        return VarDecl(name=decl.name, type_annotation=new_type,
                       initializer=new_init, is_const=decl.is_const,
                       node_id=decl.node_id, location=decl.location)

    def visit_function_decl(self, decl: FunctionDecl) -> ASTNode:
        new_params = [p.accept(self) for p in decl.parameters]
        new_ret = decl.return_type.accept(self) if decl.return_type else None
        new_body = decl.body.accept(self)
        if (new_params == decl.parameters and new_ret is decl.return_type
                and new_body is decl.body):
            return decl
        return FunctionDecl(name=decl.name, parameters=new_params,
                            return_type=new_ret, body=new_body,
                            node_id=decl.node_id, location=decl.location)

    def visit_method_decl(self, decl: MethodDecl) -> ASTNode:
        new_params = [p.accept(self) for p in decl.parameters]
        new_ret = decl.return_type.accept(self) if decl.return_type else None
        new_body = decl.body.accept(self)
        if (new_params == decl.parameters and new_ret is decl.return_type
                and new_body is decl.body):
            return decl
        return MethodDecl(name=decl.name, parameters=new_params,
                          return_type=new_ret, body=new_body,
                          is_static=decl.is_static,
                          node_id=decl.node_id, location=decl.location)

    def visit_struct_decl(self, decl: StructDecl) -> ASTNode:
        new_fields = [f.accept(self) for f in decl.fields]
        new_methods = [m.accept(self) for m in decl.methods]
        if new_fields == decl.fields and new_methods == decl.methods:
            return decl
        return StructDecl(name=decl.name, fields=new_fields, methods=new_methods,
                          node_id=decl.node_id, location=decl.location)

    def visit_enum_decl(self, decl: EnumDecl) -> ASTNode:
        new_variants = [v.accept(self) for v in decl.variants]
        if new_variants == decl.variants:
            return decl
        return EnumDecl(name=decl.name, variants=new_variants,
                        node_id=decl.node_id, location=decl.location)

    def visit_class_decl(self, decl: ClassDecl) -> ASTNode:
        new_members = [m.accept(self) for m in decl.members]
        if new_members == decl.members:
            return decl
        return ClassDecl(name=decl.name, parent=decl.parent,
                         members=new_members, node_id=decl.node_id,
                         location=decl.location)

    def visit_trait_decl(self, decl: TraitDecl) -> ASTNode:
        new_members = [m.accept(self) for m in decl.members]
        if new_members == decl.members:
            return decl
        return TraitDecl(name=decl.name, members=new_members,
                         node_id=decl.node_id, location=decl.location)

    def visit_interface_decl(self, decl: InterfaceDecl) -> ASTNode:
        new_members = [m.accept(self) for m in decl.members]
        if new_members == decl.members:
            return decl
        return InterfaceDecl(name=decl.name, members=new_members,
                             node_id=decl.node_id, location=decl.location)

    def visit_import_decl(self, decl: ImportDecl) -> ASTNode:
        return decl

    def visit_export_decl(self, decl: ExportDecl) -> ASTNode:
        return decl

    # ── Statements ─────────────────────────────────────────────

    def visit_block_stmt(self, stmt: BlockStmt) -> ASTNode:
        new_stmts = [s.accept(self) for s in stmt.statements]
        if new_stmts == stmt.statements:
            return stmt
        return BlockStmt(statements=new_stmts, node_id=stmt.node_id,
                         location=stmt.location)

    def visit_if_stmt(self, stmt: IfStmt) -> ASTNode:
        new_cond = stmt.condition.accept(self)
        new_then = stmt.then_branch.accept(self)
        new_elifs = [b.accept(self) for b in stmt.elif_branches]
        new_else = stmt.else_branch.accept(self) if stmt.else_branch else None
        if (new_cond is stmt.condition and new_then is stmt.then_branch
                and new_elifs == stmt.elif_branches
                and new_else is stmt.else_branch):
            return stmt
        return IfStmt(condition=new_cond, then_branch=new_then,
                      elif_branches=new_elifs, else_branch=new_else,
                      node_id=stmt.node_id, location=stmt.location)

    def visit_while_stmt(self, stmt: WhileStmt) -> ASTNode:
        new_cond = stmt.condition.accept(self)
        new_body = stmt.body.accept(self)
        if new_cond is stmt.condition and new_body is stmt.body:
            return stmt
        return WhileStmt(condition=new_cond, body=new_body,
                         node_id=stmt.node_id, location=stmt.location)

    def visit_until_stmt(self, stmt: UntilStmt) -> ASTNode:
        new_cond = stmt.condition.accept(self)
        new_body = stmt.body.accept(self)
        if new_cond is stmt.condition and new_body is stmt.body:
            return stmt
        return UntilStmt(condition=new_cond, body=new_body,
                         node_id=stmt.node_id, location=stmt.location)

    def visit_for_stmt(self, stmt: ForStmt) -> ASTNode:
        new_start = stmt.start.accept(self)
        new_end = stmt.end.accept(self)
        new_step = stmt.step.accept(self) if stmt.step else None
        new_body = stmt.body.accept(self)
        if (new_start is stmt.start and new_end is stmt.end
                and new_step is stmt.step and new_body is stmt.body):
            return stmt
        return ForStmt(variable=stmt.variable, start=new_start, end=new_end,
                       step=new_step, body=new_body,
                       node_id=stmt.node_id, location=stmt.location)

    def visit_for_each_stmt(self, stmt: ForEachStmt) -> ASTNode:
        new_iter = stmt.iterable.accept(self)
        new_body = stmt.body.accept(self)
        if new_iter is stmt.iterable and new_body is stmt.body:
            return stmt
        return ForEachStmt(element=stmt.element, iterable=new_iter,
                           body=new_body, node_id=stmt.node_id,
                           location=stmt.location)

    def visit_return_stmt(self, stmt: ReturnStmt) -> ASTNode:
        new_val = stmt.value.accept(self) if stmt.value else None
        if new_val is stmt.value:
            return stmt
        return ReturnStmt(value=new_val, node_id=stmt.node_id,
                          location=stmt.location)

    def visit_break_stmt(self, stmt: BreakStmt) -> ASTNode:
        return stmt

    def visit_continue_stmt(self, stmt: ContinueStmt) -> ASTNode:
        return stmt

    def visit_throw_stmt(self, stmt: ThrowStmt) -> ASTNode:
        new_val = stmt.value.accept(self)
        if new_val is stmt.value:
            return stmt
        return ThrowStmt(value=new_val, node_id=stmt.node_id,
                         location=stmt.location)

    def visit_try_stmt(self, stmt: TryStmt) -> ASTNode:
        new_try = stmt.try_body.accept(self)
        new_catch = stmt.catch_body.accept(self) if stmt.catch_body else None
        new_finally = stmt.finally_body.accept(self) if stmt.finally_body else None
        if (new_try is stmt.try_body and new_catch is stmt.catch_body
                and new_finally is stmt.finally_body):
            return stmt
        return TryStmt(try_body=new_try, catch_var=stmt.catch_var,
                       catch_body=new_catch, finally_body=new_finally,
                       node_id=stmt.node_id, location=stmt.location)

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> ASTNode:
        new_expr = stmt.expression.accept(self)
        if new_expr is stmt.expression:
            return stmt
        return ExpressionStmt(expression=new_expr, node_id=stmt.node_id,
                              location=stmt.location)

    def visit_empty_stmt(self, stmt: EmptyStmt) -> ASTNode:
        return stmt

    # ── Root ───────────────────────────────────────────────────

    def visit_program(self, program: Program) -> ASTNode:
        new_decls = [d.accept(self) for d in program.declarations]
        if new_decls == program.declarations:
            return program
        return Program(declarations=new_decls, node_id=program.node_id,
                       location=program.location)

    def visit_module(self, module: Module) -> ASTNode:
        new_imports = [i.accept(self) for i in module.imports]
        new_decls = [d.accept(self) for d in module.declarations]
        if new_imports == module.imports and new_decls == module.declarations:
            return module
        return Module(name=module.name, declarations=new_decls,
                      imports=new_imports, node_id=module.node_id,
                      location=module.location)

    # ── Helpers ────────────────────────────────────────────────

    def visit_parameter(self, param: Parameter) -> ASTNode:
        return param

    def visit_struct_field(self, field: StructField) -> ASTNode:
        return field

    def visit_enum_variant(self, variant: EnumVariant) -> ASTNode:
        return variant

    def visit_elif_branch(self, branch: ElifBranch) -> ASTNode:
        return branch


# ══════════════════════════════════════════════════════════════════
# PrettyPrinter — human-readable tree view
# ══════════════════════════════════════════════════════════════════


class PrettyPrinter(ASTVisitor):
    """
    Produces a human-readable indented tree representation of an AST.

    Usage:
        printer = PrettyPrinter()
        print(printer.print(program))
    """

    def __init__(self, indent: str = "  ") -> None:
        self._indent = indent
        self._lines: List[str] = []
        self._depth = 0

    def print(self, node: ASTNode) -> str:
        """Print the AST rooted at `node`."""
        self._lines.clear()
        self._depth = 0
        node.accept(self)
        return "\n".join(self._lines)

    def _line(self, text: str) -> None:
        self._lines.append(self._indent * self._depth + text)

    def _visit_children(self, node: ASTNode) -> None:
        self._depth += 1
        for child in node.children():
            child.accept(self)
        self._depth -= 1

    # ── Expressions ────────────────────────────────────────────

    def visit_literal_expr(self, expr: LiteralExpr) -> None:
        self._line(f"Literal({expr.value!r})")

    def visit_identifier_expr(self, expr: IdentifierExpr) -> None:
        self._line(f"Identifier({expr.name})")

    def visit_unary_expr(self, expr: UnaryExpr) -> None:
        self._line(f"Unary({expr.operator})")
        self._visit_children(expr)

    def visit_binary_expr(self, expr: BinaryExpr) -> None:
        self._line(f"Binary({expr.operator})")
        self._visit_children(expr)

    def visit_logical_expr(self, expr: LogicalExpr) -> None:
        self._line(f"Logical({expr.operator})")
        self._visit_children(expr)

    def visit_assignment_expr(self, expr: AssignmentExpr) -> None:
        self._line("Assignment")
        self._visit_children(expr)

    def visit_compound_assignment_expr(self, expr: CompoundAssignmentExpr) -> None:
        self._line(f"CompoundAssignment({expr.operator})")
        self._visit_children(expr)

    def visit_call_expr(self, expr: CallExpr) -> None:
        self._line("Call")
        self._visit_children(expr)

    def visit_method_call_expr(self, expr: MethodCallExpr) -> None:
        self._line(f"MethodCall({expr.method})")
        self._visit_children(expr)

    def visit_constructor_expr(self, expr: ConstructorExpr) -> None:
        self._line(f"Constructor({expr.class_name})")
        self._visit_children(expr)

    def visit_get_expr(self, expr: GetExpr) -> None:
        self._line(f"Get({expr.property})")
        self._visit_children(expr)

    def visit_set_expr(self, expr: SetExpr) -> None:
        self._line(f"Set({expr.property})")
        self._visit_children(expr)

    def visit_index_expr(self, expr: IndexExpr) -> None:
        self._line("Index")
        self._visit_children(expr)

    def visit_slice_expr(self, expr: SliceExpr) -> None:
        self._line("Slice")
        self._visit_children(expr)

    def visit_self_expr(self, expr: SelfExpr) -> None:
        self._line("Self")

    def visit_super_expr(self, expr: SuperExpr) -> None:
        self._line(f"Super({expr.method})")

    def visit_list_expr(self, expr: ListExpr) -> None:
        self._line("List")
        self._visit_children(expr)

    def visit_dict_expr(self, expr: DictExpr) -> None:
        self._line("Dict")
        self._visit_children(expr)

    def visit_tuple_expr(self, expr: TupleExpr) -> None:
        self._line("Tuple")
        self._visit_children(expr)

    def visit_lambda_expr(self, expr: LambdaExpr) -> None:
        self._line("Lambda")
        self._visit_children(expr)

    def visit_if_expr(self, expr: IfExpr) -> None:
        self._line("IfExpr")
        self._visit_children(expr)

    def visit_grouping_expr(self, expr: GroupingExpr) -> None:
        self._line("Grouping")
        self._visit_children(expr)

    def visit_placeholder_expr(self, expr: PlaceholderExpr) -> None:
        label = f"Placeholder({expr.description})" if expr.description else "Placeholder"
        self._line(label)

    # ── Types ──────────────────────────────────────────────────

    def visit_named_type(self, t: NamedType) -> None:
        self._line(f"Type({t.name})")

    def visit_generic_type(self, t: GenericType) -> None:
        self._line(f"GenericType({t.name})")
        self._visit_children(t)

    def visit_function_type(self, t: FunctionType) -> None:
        self._line("FunctionType")
        self._visit_children(t)

    def visit_optional_type(self, t: OptionalType) -> None:
        self._line("OptionalType")
        self._visit_children(t)

    def visit_tuple_type(self, t: TupleType) -> None:
        self._line("TupleType")
        self._visit_children(t)

    # ── Declarations ───────────────────────────────────────────

    def visit_var_decl(self, decl: VarDecl) -> None:
        kw = "Const" if decl.is_const else "Var"
        self._line(f"{kw}({decl.name})")
        self._visit_children(decl)

    def visit_function_decl(self, decl: FunctionDecl) -> None:
        self._line(f"Function({decl.name})")
        self._visit_children(decl)

    def visit_method_decl(self, decl: MethodDecl) -> None:
        static = "Static" if decl.is_static else ""
        self._line(f"{static}Method({decl.name})")
        self._visit_children(decl)

    def visit_struct_decl(self, decl: StructDecl) -> None:
        self._line(f"Struct({decl.name})")
        self._visit_children(decl)

    def visit_enum_decl(self, decl: EnumDecl) -> None:
        self._line(f"Enum({decl.name})")
        self._visit_children(decl)

    def visit_class_decl(self, decl: ClassDecl) -> None:
        parent = f" extends {decl.parent}" if decl.parent else ""
        self._line(f"Class({decl.name}{parent})")
        self._visit_children(decl)

    def visit_trait_decl(self, decl: TraitDecl) -> None:
        self._line(f"Trait({decl.name})")
        self._visit_children(decl)

    def visit_interface_decl(self, decl: InterfaceDecl) -> None:
        self._line(f"Interface({decl.name})")
        self._visit_children(decl)

    def visit_import_decl(self, decl: ImportDecl) -> None:
        alias = f" as {decl.alias}" if decl.alias else ""
        self._line(f"Import({decl.path}{alias})")

    def visit_export_decl(self, decl: ExportDecl) -> None:
        self._line(f"Export({decl.name})")

    # ── Statements ─────────────────────────────────────────────

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        self._line("Block")
        self._visit_children(stmt)

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        self._line("If")
        self._visit_children(stmt)

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        self._line("While")
        self._visit_children(stmt)

    def visit_until_stmt(self, stmt: UntilStmt) -> None:
        self._line("Until")
        self._visit_children(stmt)

    def visit_for_stmt(self, stmt: ForStmt) -> None:
        self._line(f"For({stmt.variable})")
        self._visit_children(stmt)

    def visit_for_each_stmt(self, stmt: ForEachStmt) -> None:
        self._line(f"ForEach({stmt.element})")
        self._visit_children(stmt)

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        self._line("Return")
        self._visit_children(stmt)

    def visit_break_stmt(self, stmt: BreakStmt) -> None:
        self._line("Break")

    def visit_continue_stmt(self, stmt: ContinueStmt) -> None:
        self._line("Continue")

    def visit_throw_stmt(self, stmt: ThrowStmt) -> None:
        self._line("Throw")
        self._visit_children(stmt)

    def visit_try_stmt(self, stmt: TryStmt) -> None:
        self._line("Try")
        self._visit_children(stmt)

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        self._line("ExprStmt")
        self._visit_children(stmt)

    def visit_empty_stmt(self, stmt: EmptyStmt) -> None:
        self._line("Empty")

    # ── Root ───────────────────────────────────────────────────

    def visit_program(self, program: Program) -> None:
        self._line("Program")
        self._visit_children(program)

    def visit_module(self, module: Module) -> None:
        self._line(f"Module({module.name})")
        self._visit_children(module)

    # ── Helpers ────────────────────────────────────────────────

    def visit_parameter(self, param: Parameter) -> None:
        self._line(f"Param({param.name})")
        self._visit_children(param)

    def visit_struct_field(self, field: StructField) -> None:
        self._line(f"Field({field.name})")
        self._visit_children(field)

    def visit_enum_variant(self, variant: EnumVariant) -> None:
        self._line(f"Variant({variant.name})")
        self._visit_children(variant)

    def visit_elif_branch(self, branch: ElifBranch) -> None:
        self._line("Elif")
        self._visit_children(branch)


# ══════════════════════════════════════════════════════════════════
# DebugPrinter — detailed output with node IDs
# ══════════════════════════════════════════════════════════════════


class DebugPrinter(ASTVisitor):
    """
    Produces a detailed debug representation of the AST,
    including node IDs, source locations, and metadata.
    """

    def __init__(self, indent: str = "  ") -> None:
        self._indent = indent
        self._lines: List[str] = []
        self._depth = 0

    def print(self, node: ASTNode) -> str:
        self._lines.clear()
        self._depth = 0
        node.accept(self)
        return "\n".join(self._lines)

    def _line(self, text: str) -> None:
        self._lines.append(self._indent * self._depth + text)

    def _visit_children(self, node: ASTNode) -> None:
        self._depth += 1
        for child in node.children():
            child.accept(self)
        self._depth -= 1

    def _header(self, node: ASTNode, label: str) -> str:
        loc = node.location
        meta = f" meta={node.metadata}" if node.metadata else ""
        return f"[{node.node_id}] {label} @ {loc}{meta}"

    # ── Expressions ────────────────────────────────────────────

    def visit_literal_expr(self, expr: LiteralExpr) -> None:
        self._line(self._header(expr, f"Literal({expr.value!r})"))

    def visit_identifier_expr(self, expr: IdentifierExpr) -> None:
        self._line(self._header(expr, f"Identifier({expr.name})"))

    def visit_unary_expr(self, expr: UnaryExpr) -> None:
        self._line(self._header(expr, f"Unary({expr.operator})"))
        self._visit_children(expr)

    def visit_binary_expr(self, expr: BinaryExpr) -> None:
        self._line(self._header(expr, f"Binary({expr.operator})"))
        self._visit_children(expr)

    def visit_logical_expr(self, expr: LogicalExpr) -> None:
        self._line(self._header(expr, f"Logical({expr.operator})"))
        self._visit_children(expr)

    def visit_assignment_expr(self, expr: AssignmentExpr) -> None:
        self._line(self._header(expr, "Assignment"))
        self._visit_children(expr)

    def visit_compound_assignment_expr(self, expr: CompoundAssignmentExpr) -> None:
        self._line(self._header(expr, f"CompoundAssignment({expr.operator})"))
        self._visit_children(expr)

    def visit_call_expr(self, expr: CallExpr) -> None:
        self._line(self._header(expr, "Call"))
        self._visit_children(expr)

    def visit_method_call_expr(self, expr: MethodCallExpr) -> None:
        self._line(self._header(expr, f"MethodCall({expr.method})"))
        self._visit_children(expr)

    def visit_constructor_expr(self, expr: ConstructorExpr) -> None:
        self._line(self._header(expr, f"Constructor({expr.class_name})"))
        self._visit_children(expr)

    def visit_get_expr(self, expr: GetExpr) -> None:
        self._line(self._header(expr, f"Get({expr.property})"))
        self._visit_children(expr)

    def visit_set_expr(self, expr: SetExpr) -> None:
        self._line(self._header(expr, f"Set({expr.property})"))
        self._visit_children(expr)

    def visit_index_expr(self, expr: IndexExpr) -> None:
        self._line(self._header(expr, "Index"))
        self._visit_children(expr)

    def visit_slice_expr(self, expr: SliceExpr) -> None:
        self._line(self._header(expr, "Slice"))
        self._visit_children(expr)

    def visit_self_expr(self, expr: SelfExpr) -> None:
        self._line(self._header(expr, "Self"))

    def visit_super_expr(self, expr: SuperExpr) -> None:
        self._line(self._header(expr, f"Super({expr.method})"))

    def visit_list_expr(self, expr: ListExpr) -> None:
        self._line(self._header(expr, "List"))
        self._visit_children(expr)

    def visit_dict_expr(self, expr: DictExpr) -> None:
        self._line(self._header(expr, "Dict"))
        self._visit_children(expr)

    def visit_tuple_expr(self, expr: TupleExpr) -> None:
        self._line(self._header(expr, "Tuple"))
        self._visit_children(expr)

    def visit_lambda_expr(self, expr: LambdaExpr) -> None:
        self._line(self._header(expr, "Lambda"))
        self._visit_children(expr)

    def visit_if_expr(self, expr: IfExpr) -> None:
        self._line(self._header(expr, "IfExpr"))
        self._visit_children(expr)

    def visit_grouping_expr(self, expr: GroupingExpr) -> None:
        self._line(self._header(expr, "Grouping"))
        self._visit_children(expr)

    def visit_placeholder_expr(self, expr: PlaceholderExpr) -> None:
        label = f"Placeholder({expr.description})" if expr.description else "Placeholder"
        self._line(self._header(expr, label))

    # ── Types ──────────────────────────────────────────────────

    def visit_named_type(self, t: NamedType) -> None:
        self._line(self._header(t, f"Type({t.name})"))

    def visit_generic_type(self, t: GenericType) -> None:
        self._line(self._header(t, f"GenericType({t.name})"))
        self._visit_children(t)

    def visit_function_type(self, t: FunctionType) -> None:
        self._line(self._header(t, "FunctionType"))
        self._visit_children(t)

    def visit_optional_type(self, t: OptionalType) -> None:
        self._line(self._header(t, "OptionalType"))
        self._visit_children(t)

    def visit_tuple_type(self, t: TupleType) -> None:
        self._line(self._header(t, "TupleType"))
        self._visit_children(t)

    # ── Declarations ───────────────────────────────────────────

    def visit_var_decl(self, decl: VarDecl) -> None:
        kw = "Const" if decl.is_const else "Var"
        self._line(self._header(decl, f"{kw}({decl.name})"))
        self._visit_children(decl)

    def visit_function_decl(self, decl: FunctionDecl) -> None:
        self._line(self._header(decl, f"Function({decl.name})"))
        self._visit_children(decl)

    def visit_method_decl(self, decl: MethodDecl) -> None:
        static = "Static" if decl.is_static else ""
        self._line(self._header(decl, f"{static}Method({decl.name})"))
        self._visit_children(decl)

    def visit_struct_decl(self, decl: StructDecl) -> None:
        self._line(self._header(decl, f"Struct({decl.name})"))
        self._visit_children(decl)

    def visit_enum_decl(self, decl: EnumDecl) -> None:
        self._line(self._header(decl, f"Enum({decl.name})"))
        self._visit_children(decl)

    def visit_class_decl(self, decl: ClassDecl) -> None:
        parent = f" extends {decl.parent}" if decl.parent else ""
        self._line(self._header(decl, f"Class({decl.name}{parent})"))
        self._visit_children(decl)

    def visit_trait_decl(self, decl: TraitDecl) -> None:
        self._line(self._header(decl, f"Trait({decl.name})"))
        self._visit_children(decl)

    def visit_interface_decl(self, decl: InterfaceDecl) -> None:
        self._line(self._header(decl, f"Interface({decl.name})"))
        self._visit_children(decl)

    def visit_import_decl(self, decl: ImportDecl) -> None:
        alias = f" as {decl.alias}" if decl.alias else ""
        self._line(self._header(decl, f"Import({decl.path}{alias})"))

    def visit_export_decl(self, decl: ExportDecl) -> None:
        self._line(self._header(decl, f"Export({decl.name})"))

    # ── Statements ─────────────────────────────────────────────

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        self._line(self._header(stmt, "Block"))
        self._visit_children(stmt)

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        self._line(self._header(stmt, "If"))
        self._visit_children(stmt)

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        self._line(self._header(stmt, "While"))
        self._visit_children(stmt)

    def visit_until_stmt(self, stmt: UntilStmt) -> None:
        self._line(self._header(stmt, "Until"))
        self._visit_children(stmt)

    def visit_for_stmt(self, stmt: ForStmt) -> None:
        self._line(self._header(stmt, f"For({stmt.variable})"))
        self._visit_children(stmt)

    def visit_for_each_stmt(self, stmt: ForEachStmt) -> None:
        self._line(self._header(stmt, f"ForEach({stmt.element})"))
        self._visit_children(stmt)

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        self._line(self._header(stmt, "Return"))
        self._visit_children(stmt)

    def visit_break_stmt(self, stmt: BreakStmt) -> None:
        self._line(self._header(stmt, "Break"))

    def visit_continue_stmt(self, stmt: ContinueStmt) -> None:
        self._line(self._header(stmt, "Continue"))

    def visit_throw_stmt(self, stmt: ThrowStmt) -> None:
        self._line(self._header(stmt, "Throw"))
        self._visit_children(stmt)

    def visit_try_stmt(self, stmt: TryStmt) -> None:
        self._line(self._header(stmt, "Try"))
        self._visit_children(stmt)

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        self._line(self._header(stmt, "ExprStmt"))
        self._visit_children(stmt)

    def visit_empty_stmt(self, stmt: EmptyStmt) -> None:
        self._line(self._header(stmt, "Empty"))

    # ── Root ───────────────────────────────────────────────────

    def visit_program(self, program: Program) -> None:
        self._line(self._header(program, "Program"))
        self._visit_children(program)

    def visit_module(self, module: Module) -> None:
        self._line(self._header(module, f"Module({module.name})"))
        self._visit_children(module)

    # ── Helpers ────────────────────────────────────────────────

    def visit_parameter(self, param: Parameter) -> None:
        self._line(self._header(param, f"Param({param.name})"))
        self._visit_children(param)

    def visit_struct_field(self, field: StructField) -> None:
        self._line(self._header(field, f"Field({field.name})"))
        self._visit_children(field)

    def visit_enum_variant(self, variant: EnumVariant) -> None:
        self._line(self._header(variant, f"Variant({variant.name})"))
        self._visit_children(variant)

    def visit_elif_branch(self, branch: ElifBranch) -> None:
        self._line(self._header(branch, "Elif"))
        self._visit_children(branch)


# ══════════════════════════════════════════════════════════════════
# ASTRewriter — replace nodes with a callback-based approach
# ══════════════════════════════════════════════════════════════════


class ASTRewriter(ASTVisitor):
    """
    Walks the AST bottom-up and allows replacing nodes via registered callbacks.
    Unlike ASTTransformer, this uses a registry pattern for more flexible rewriting.

    Usage:
        rewriter = ASTRewriter()
        rewriter.register(LiteralExpr, lambda e: LiteralExpr(e.value * 2, location=e.location))
        new_tree = rewriter.rewrite(program)
    """

    def __init__(self) -> None:
        self._handlers: dict = {}
        self._results: list = []

    def register(self, node_class: type, handler: Any) -> None:
        """Register a rewrite handler for a node class."""
        self._handlers[node_class] = handler

    def rewrite(self, node: ASTNode) -> ASTNode:
        """Rewrite the AST rooted at `node`."""
        node.accept(self)
        return self._results.pop() if self._results else node

    def _result(self, node: ASTNode) -> ASTNode:
        handler = self._handlers.get(type(node))
        if handler:
            node = handler(node)
        self._results.append(node)
        return node

    # ── Expressions ────────────────────────────────────────────

    def visit_literal_expr(self, expr: LiteralExpr) -> None:
        self._result(expr)

    def visit_identifier_expr(self, expr: IdentifierExpr) -> None:
        self._result(expr)

    def visit_unary_expr(self, expr: UnaryExpr) -> None:
        expr.right.accept(self)
        new_right = self._results.pop()
        expr = UnaryExpr(operator=expr.operator, right=new_right,
                         node_id=expr.node_id, location=expr.location)
        self._result(expr)

    def visit_binary_expr(self, expr: BinaryExpr) -> None:
        expr.left.accept(self)
        new_left = self._results.pop()
        expr.right.accept(self)
        new_right = self._results.pop()
        expr = BinaryExpr(left=new_left, operator=expr.operator, right=new_right,
                          node_id=expr.node_id, location=expr.location)
        self._result(expr)

    def visit_logical_expr(self, expr: LogicalExpr) -> None:
        expr.left.accept(self)
        new_left = self._results.pop()
        expr.right.accept(self)
        new_right = self._results.pop()
        expr = LogicalExpr(left=new_left, operator=expr.operator, right=new_right,
                           node_id=expr.node_id, location=expr.location)
        self._result(expr)

    def visit_assignment_expr(self, expr: AssignmentExpr) -> None:
        expr.target.accept(self)
        new_target = self._results.pop()
        expr.value.accept(self)
        new_value = self._results.pop()
        expr = AssignmentExpr(target=new_target, value=new_value,
                              node_id=expr.node_id, location=expr.location)
        self._result(expr)

    def visit_compound_assignment_expr(self, expr: CompoundAssignmentExpr) -> None:
        expr.target.accept(self)
        new_target = self._results.pop()
        expr.value.accept(self)
        new_value = self._results.pop()
        expr = CompoundAssignmentExpr(target=new_target, operator=expr.operator,
                                      value=new_value, node_id=expr.node_id,
                                      location=expr.location)
        self._result(expr)

    def visit_call_expr(self, expr: CallExpr) -> None:
        expr.callee.accept(self)
        new_callee = self._results.pop()
        new_args = []
        for a in expr.arguments:
            a.accept(self)
            new_args.append(self._results.pop())
        expr = CallExpr(callee=new_callee, arguments=new_args,
                        node_id=expr.node_id, location=expr.location)
        self._result(expr)

    def visit_method_call_expr(self, expr: MethodCallExpr) -> None:
        expr.object.accept(self)
        new_obj = self._results.pop()
        new_args = []
        for a in expr.arguments:
            a.accept(self)
            new_args.append(self._results.pop())
        expr = MethodCallExpr(object=new_obj, method=expr.method,
                              arguments=new_args, node_id=expr.node_id,
                              location=expr.location)
        self._result(expr)

    def visit_constructor_expr(self, expr: ConstructorExpr) -> None:
        new_args = []
        for a in expr.arguments:
            a.accept(self)
            new_args.append(self._results.pop())
        expr = ConstructorExpr(class_name=expr.class_name, arguments=new_args,
                               node_id=expr.node_id, location=expr.location)
        self._result(expr)

    def visit_get_expr(self, expr: GetExpr) -> None:
        expr.object.accept(self)
        new_obj = self._results.pop()
        expr = GetExpr(object=new_obj, property=expr.property,
                       node_id=expr.node_id, location=expr.location)
        self._result(expr)

    def visit_set_expr(self, expr: SetExpr) -> None:
        expr.object.accept(self)
        new_obj = self._results.pop()
        expr.value.accept(self)
        new_value = self._results.pop()
        expr = SetExpr(object=new_obj, property=expr.property, value=new_value,
                       node_id=expr.node_id, location=expr.location)
        self._result(expr)

    def visit_index_expr(self, expr: IndexExpr) -> None:
        expr.object.accept(self)
        new_obj = self._results.pop()
        expr.index.accept(self)
        new_idx = self._results.pop()
        expr = IndexExpr(object=new_obj, index=new_idx,
                         node_id=expr.node_id, location=expr.location)
        self._result(expr)

    def visit_slice_expr(self, expr: SliceExpr) -> None:
        expr.object.accept(self)
        new_obj = self._results.pop()
        new_start = None
        if expr.start:
            expr.start.accept(self)
            new_start = self._results.pop()
        new_end = None
        if expr.end:
            expr.end.accept(self)
            new_end = self._results.pop()
        expr = SliceExpr(object=new_obj, start=new_start, end=new_end,
                         node_id=expr.node_id, location=expr.location)
        self._result(expr)

    def visit_self_expr(self, expr: SelfExpr) -> None:
        self._result(expr)

    def visit_super_expr(self, expr: SuperExpr) -> None:
        self._result(expr)

    def visit_list_expr(self, expr: ListExpr) -> None:
        new_elems = []
        for e in expr.elements:
            e.accept(self)
            new_elems.append(self._results.pop())
        expr = ListExpr(elements=new_elems, node_id=expr.node_id,
                        location=expr.location)
        self._result(expr)

    def visit_dict_expr(self, expr: DictExpr) -> None:
        new_keys = []
        for k in expr.keys:
            k.accept(self)
            new_keys.append(self._results.pop())
        new_vals = []
        for v in expr.values:
            v.accept(self)
            new_vals.append(self._results.pop())
        expr = DictExpr(keys=new_keys, values=new_vals,
                        node_id=expr.node_id, location=expr.location)
        self._result(expr)

    def visit_tuple_expr(self, expr: TupleExpr) -> None:
        new_elems = []
        for e in expr.elements:
            e.accept(self)
            new_elems.append(self._results.pop())
        expr = TupleExpr(elements=new_elems, node_id=expr.node_id,
                         location=expr.location)
        self._result(expr)

    def visit_lambda_expr(self, expr: LambdaExpr) -> None:
        new_params = []
        for p in expr.parameters:
            p.accept(self)
            new_params.append(self._results.pop())
        expr.body.accept(self)
        new_body = self._results.pop()
        expr = LambdaExpr(parameters=new_params, body=new_body,
                          node_id=expr.node_id, location=expr.location)
        self._result(expr)

    def visit_if_expr(self, expr: IfExpr) -> None:
        expr.condition.accept(self)
        new_cond = self._results.pop()
        expr.then_branch.accept(self)
        new_then = self._results.pop()
        new_else = None
        if expr.else_branch:
            expr.else_branch.accept(self)
            new_else = self._results.pop()
        expr = IfExpr(condition=new_cond, then_branch=new_then,
                      else_branch=new_else, node_id=expr.node_id,
                      location=expr.location)
        self._result(expr)

    def visit_grouping_expr(self, expr: GroupingExpr) -> None:
        expr.expression.accept(self)
        new_inner = self._results.pop()
        expr = GroupingExpr(expression=new_inner, node_id=expr.node_id,
                            location=expr.location)
        self._result(expr)

    def visit_placeholder_expr(self, expr: PlaceholderExpr) -> None:
        self._result(expr)

    # ── Types ──────────────────────────────────────────────────

    def visit_named_type(self, t: NamedType) -> None:
        self._result(t)

    def visit_generic_type(self, t: GenericType) -> None:
        self._result(t)

    def visit_function_type(self, t: FunctionType) -> None:
        self._result(t)

    def visit_optional_type(self, t: OptionalType) -> None:
        self._result(t)

    def visit_tuple_type(self, t: TupleType) -> None:
        self._result(t)

    # ── Declarations ───────────────────────────────────────────

    def visit_var_decl(self, decl: VarDecl) -> None:
        new_type = None
        if decl.type_annotation:
            decl.type_annotation.accept(self)
            new_type = self._results.pop()
        new_init = None
        if decl.initializer:
            decl.initializer.accept(self)
            new_init = self._results.pop()
        decl = VarDecl(name=decl.name, type_annotation=new_type,
                       initializer=new_init, is_const=decl.is_const,
                       node_id=decl.node_id, location=decl.location)
        self._result(decl)

    def visit_function_decl(self, decl: FunctionDecl) -> None:
        new_params = []
        for p in decl.parameters:
            p.accept(self)
            new_params.append(self._results.pop())
        new_ret = None
        if decl.return_type:
            decl.return_type.accept(self)
            new_ret = self._results.pop()
        decl.body.accept(self)
        new_body = self._results.pop()
        decl = FunctionDecl(name=decl.name, parameters=new_params,
                            return_type=new_ret, body=new_body,
                            node_id=decl.node_id, location=decl.location)
        self._result(decl)

    def visit_method_decl(self, decl: MethodDecl) -> None:
        new_params = []
        for p in decl.parameters:
            p.accept(self)
            new_params.append(self._results.pop())
        new_ret = None
        if decl.return_type:
            decl.return_type.accept(self)
            new_ret = self._results.pop()
        decl.body.accept(self)
        new_body = self._results.pop()
        decl = MethodDecl(name=decl.name, parameters=new_params,
                          return_type=new_ret, body=new_body,
                          is_static=decl.is_static,
                          node_id=decl.node_id, location=decl.location)
        self._result(decl)

    def visit_struct_decl(self, decl: StructDecl) -> None:
        new_fields = []
        for f in decl.fields:
            f.accept(self)
            new_fields.append(self._results.pop())
        new_methods = []
        for m in decl.methods:
            m.accept(self)
            new_methods.append(self._results.pop())
        decl = StructDecl(name=decl.name, fields=new_fields, methods=new_methods,
                          node_id=decl.node_id, location=decl.location)
        self._result(decl)

    def visit_enum_decl(self, decl: EnumDecl) -> None:
        new_variants = []
        for v in decl.variants:
            v.accept(self)
            new_variants.append(self._results.pop())
        decl = EnumDecl(name=decl.name, variants=new_variants,
                        node_id=decl.node_id, location=decl.location)
        self._result(decl)

    def visit_class_decl(self, decl: ClassDecl) -> None:
        new_members = []
        for m in decl.members:
            m.accept(self)
            new_members.append(self._results.pop())
        decl = ClassDecl(name=decl.name, parent=decl.parent,
                         members=new_members, node_id=decl.node_id,
                         location=decl.location)
        self._result(decl)

    def visit_trait_decl(self, decl: TraitDecl) -> None:
        new_members = []
        for m in decl.members:
            m.accept(self)
            new_members.append(self._results.pop())
        decl = TraitDecl(name=decl.name, members=new_members,
                         node_id=decl.node_id, location=decl.location)
        self._result(decl)

    def visit_interface_decl(self, decl: InterfaceDecl) -> None:
        new_members = []
        for m in decl.members:
            m.accept(self)
            new_members.append(self._results.pop())
        decl = InterfaceDecl(name=decl.name, members=new_members,
                             node_id=decl.node_id, location=decl.location)
        self._result(decl)

    def visit_import_decl(self, decl: ImportDecl) -> None:
        self._result(decl)

    def visit_export_decl(self, decl: ExportDecl) -> None:
        self._result(decl)

    # ── Statements ─────────────────────────────────────────────

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        new_stmts = []
        for s in stmt.statements:
            s.accept(self)
            new_stmts.append(self._results.pop())
        stmt = BlockStmt(statements=new_stmts, node_id=stmt.node_id,
                         location=stmt.location)
        self._result(stmt)

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        stmt.condition.accept(self)
        new_cond = self._results.pop()
        stmt.then_branch.accept(self)
        new_then = self._results.pop()
        new_elifs = []
        for b in stmt.elif_branches:
            b.accept(self)
            new_elifs.append(self._results.pop())
        new_else = None
        if stmt.else_branch:
            stmt.else_branch.accept(self)
            new_else = self._results.pop()
        stmt = IfStmt(condition=new_cond, then_branch=new_then,
                      elif_branches=new_elifs, else_branch=new_else,
                      node_id=stmt.node_id, location=stmt.location)
        self._result(stmt)

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        stmt.condition.accept(self)
        new_cond = self._results.pop()
        stmt.body.accept(self)
        new_body = self._results.pop()
        stmt = WhileStmt(condition=new_cond, body=new_body,
                         node_id=stmt.node_id, location=stmt.location)
        self._result(stmt)

    def visit_until_stmt(self, stmt: UntilStmt) -> None:
        stmt.condition.accept(self)
        new_cond = self._results.pop()
        stmt.body.accept(self)
        new_body = self._results.pop()
        stmt = UntilStmt(condition=new_cond, body=new_body,
                         node_id=stmt.node_id, location=stmt.location)
        self._result(stmt)

    def visit_for_stmt(self, stmt: ForStmt) -> None:
        stmt.start.accept(self)
        new_start = self._results.pop()
        stmt.end.accept(self)
        new_end = self._results.pop()
        new_step = None
        if stmt.step:
            stmt.step.accept(self)
            new_step = self._results.pop()
        stmt.body.accept(self)
        new_body = self._results.pop()
        stmt = ForStmt(variable=stmt.variable, start=new_start, end=new_end,
                       step=new_step, body=new_body,
                       node_id=stmt.node_id, location=stmt.location)
        self._result(stmt)

    def visit_for_each_stmt(self, stmt: ForEachStmt) -> None:
        stmt.iterable.accept(self)
        new_iter = self._results.pop()
        stmt.body.accept(self)
        new_body = self._results.pop()
        stmt = ForEachStmt(element=stmt.element, iterable=new_iter,
                           body=new_body, node_id=stmt.node_id,
                           location=stmt.location)
        self._result(stmt)

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        new_val = None
        if stmt.value:
            stmt.value.accept(self)
            new_val = self._results.pop()
        stmt = ReturnStmt(value=new_val, node_id=stmt.node_id,
                          location=stmt.location)
        self._result(stmt)

    def visit_break_stmt(self, stmt: BreakStmt) -> None:
        self._result(stmt)

    def visit_continue_stmt(self, stmt: ContinueStmt) -> None:
        self._result(stmt)

    def visit_throw_stmt(self, stmt: ThrowStmt) -> None:
        stmt.value.accept(self)
        new_val = self._results.pop()
        stmt = ThrowStmt(value=new_val, node_id=stmt.node_id,
                         location=stmt.location)
        self._result(stmt)

    def visit_try_stmt(self, stmt: TryStmt) -> None:
        stmt.try_body.accept(self)
        new_try = self._results.pop()
        new_catch = None
        if stmt.catch_body:
            stmt.catch_body.accept(self)
            new_catch = self._results.pop()
        new_finally = None
        if stmt.finally_body:
            stmt.finally_body.accept(self)
            new_finally = self._results.pop()
        stmt = TryStmt(try_body=new_try, catch_var=stmt.catch_var,
                       catch_body=new_catch, finally_body=new_finally,
                       node_id=stmt.node_id, location=stmt.location)
        self._result(stmt)

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        stmt.expression.accept(self)
        new_expr = self._results.pop()
        stmt = ExpressionStmt(expression=new_expr, node_id=stmt.node_id,
                              location=stmt.location)
        self._result(stmt)

    def visit_empty_stmt(self, stmt: EmptyStmt) -> None:
        self._result(stmt)

    # ── Root ───────────────────────────────────────────────────

    def visit_program(self, program: Program) -> None:
        new_decls = []
        for d in program.declarations:
            d.accept(self)
            new_decls.append(self._results.pop())
        program = Program(declarations=new_decls, node_id=program.node_id,
                          location=program.location)
        self._result(program)

    def visit_module(self, module: Module) -> None:
        new_imports = []
        for i in module.imports:
            i.accept(self)
            new_imports.append(self._results.pop())
        new_decls = []
        for d in module.declarations:
            d.accept(self)
            new_decls.append(self._results.pop())
        module = Module(name=module.name, declarations=new_decls,
                        imports=new_imports, node_id=module.node_id,
                        location=module.location)
        self._result(module)

    # ── Helpers ────────────────────────────────────────────────

    def visit_parameter(self, param: Parameter) -> None:
        new_type = None
        if param.type_annotation:
            param.type_annotation.accept(self)
            new_type = self._results.pop()
        new_default = None
        if param.default:
            param.default.accept(self)
            new_default = self._results.pop()
        param = Parameter(name=param.name, type_annotation=new_type,
                          default=new_default, node_id=param.node_id,
                          location=param.location)
        self._result(param)

    def visit_struct_field(self, field: StructField) -> None:
        field.type_annotation.accept(self)
        new_type = self._results.pop()
        new_default = None
        if field.default:
            field.default.accept(self)
            new_default = self._results.pop()
        field = StructField(name=field.name, type_annotation=new_type,
                            default=new_default, node_id=field.node_id,
                            location=field.location)
        self._result(field)

    def visit_enum_variant(self, variant: EnumVariant) -> None:
        new_val = None
        if variant.value:
            variant.value.accept(self)
            new_val = self._results.pop()
        variant = EnumVariant(name=variant.name, value=new_val,
                              node_id=variant.node_id, location=variant.location)
        self._result(variant)

    def visit_elif_branch(self, branch: ElifBranch) -> None:
        branch.condition.accept(self)
        new_cond = self._results.pop()
        branch.body.accept(self)
        new_body = self._results.pop()
        branch = ElifBranch(condition=new_cond, body=new_body,
                            node_id=branch.node_id, location=branch.location)
        self._result(branch)


# ══════════════════════════════════════════════════════════════════
# ASTInspector — collect information about the tree
# ══════════════════════════════════════════════════════════════════


class ASTInspector(ASTVisitor):
    """
    Walks the AST and collects statistics and structural information.
    Does not modify the tree.

    Usage:
        inspector = ASTInspector()
        stats = inspector.inspect(program)
        print(f"Total nodes: {stats['total_nodes']}")
    """

    def __init__(self) -> None:
        self._reset()

    def _reset(self) -> None:
        self._total_nodes = 0
        self._max_depth = 0
        self._current_depth = 0
        self._node_counts: dict = {}
        self._expressions = 0
        self._statements = 0
        self._declarations = 0
        self._type_nodes = 0
        self._leaf_nodes = 0
        self._identifiers: set = set()
        self._function_names: list = []
        self._method_names: list = []
        self._class_names: list = []
        self._struct_names: list = []
        self._enum_names: list = []
        self._trait_names: list = []
        self._interface_names: list = []
        self._variable_names: set = set()
        self._max_children = 0

    def inspect(self, node: ASTNode) -> dict:
        """Inspect the AST and return statistics."""
        self._reset()
        node.accept(self)
        return {
            "total_nodes": self._total_nodes,
            "max_depth": self._max_depth,
            "node_counts": dict(self._node_counts),
            "expressions": self._expressions,
            "statements": self._statements,
            "declarations": self._declarations,
            "type_nodes": self._type_nodes,
            "leaf_nodes": self._leaf_nodes,
            "identifiers": len(self._identifiers),
            "function_names": list(self._function_names),
            "method_names": list(self._method_names),
            "class_names": list(self._class_names),
            "struct_names": list(self._struct_names),
            "enum_names": list(self._enum_names),
            "trait_names": list(self._trait_names),
            "interface_names": list(self._interface_names),
            "variable_names": len(self._variable_names),
            "max_children": self._max_children,
        }

    def _enter(self, node: ASTNode) -> None:
        self._total_nodes += 1
        name = type(node).__name__
        self._node_counts[name] = self._node_counts.get(name, 0) + 1
        self._current_depth += 1
        if self._current_depth > self._max_depth:
            self._max_depth = self._current_depth
        children = node.children()
        if len(children) > self._max_children:
            self._max_children = len(children)
        if isinstance(node, Expr):
            self._expressions += 1
        elif isinstance(node, TypeNode):
            self._type_nodes += 1
        elif isinstance(node, Decl):
            self._declarations += 1
        elif isinstance(node, Stmt):
            self._statements += 1
        if not children:
            self._leaf_nodes += 1

    def _exit(self) -> None:
        self._current_depth -= 1

    def _walk_children(self, node: ASTNode) -> None:
        for child in node.children():
            child.accept(self)

    # ── Expressions ────────────────────────────────────────────

    def visit_literal_expr(self, expr: LiteralExpr) -> None:
        self._enter(expr); self._exit()

    def visit_identifier_expr(self, expr: IdentifierExpr) -> None:
        self._enter(expr)
        self._identifiers.add(expr.name)
        self._exit()

    def visit_unary_expr(self, expr: UnaryExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_binary_expr(self, expr: BinaryExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_logical_expr(self, expr: LogicalExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_assignment_expr(self, expr: AssignmentExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_compound_assignment_expr(self, expr: CompoundAssignmentExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_call_expr(self, expr: CallExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_method_call_expr(self, expr: MethodCallExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_constructor_expr(self, expr: ConstructorExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_get_expr(self, expr: GetExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_set_expr(self, expr: SetExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_index_expr(self, expr: IndexExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_slice_expr(self, expr: SliceExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_self_expr(self, expr: SelfExpr) -> None:
        self._enter(expr); self._exit()

    def visit_super_expr(self, expr: SuperExpr) -> None:
        self._enter(expr); self._exit()

    def visit_list_expr(self, expr: ListExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_dict_expr(self, expr: DictExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_tuple_expr(self, expr: TupleExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_lambda_expr(self, expr: LambdaExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_if_expr(self, expr: IfExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_grouping_expr(self, expr: GroupingExpr) -> None:
        self._enter(expr); self._walk_children(expr); self._exit()

    def visit_placeholder_expr(self, expr: PlaceholderExpr) -> None:
        self._enter(expr); self._exit()

    # ── Types ──────────────────────────────────────────────────

    def visit_named_type(self, t: NamedType) -> None:
        self._enter(t); self._exit()

    def visit_generic_type(self, t: GenericType) -> None:
        self._enter(t); self._walk_children(t); self._exit()

    def visit_function_type(self, t: FunctionType) -> None:
        self._enter(t); self._walk_children(t); self._exit()

    def visit_optional_type(self, t: OptionalType) -> None:
        self._enter(t); self._walk_children(t); self._exit()

    def visit_tuple_type(self, t: TupleType) -> None:
        self._enter(t); self._walk_children(t); self._exit()

    # ── Declarations ───────────────────────────────────────────

    def visit_var_decl(self, decl: VarDecl) -> None:
        self._enter(decl)
        self._variable_names.add(decl.name)
        self._walk_children(decl)
        self._exit()

    def visit_function_decl(self, decl: FunctionDecl) -> None:
        self._enter(decl)
        self._function_names.append(decl.name)
        self._walk_children(decl)
        self._exit()

    def visit_method_decl(self, decl: MethodDecl) -> None:
        self._enter(decl)
        self._method_names.append(decl.name)
        self._walk_children(decl)
        self._exit()

    def visit_struct_decl(self, decl: StructDecl) -> None:
        self._enter(decl)
        self._struct_names.append(decl.name)
        self._walk_children(decl)
        self._exit()

    def visit_enum_decl(self, decl: EnumDecl) -> None:
        self._enter(decl)
        self._enum_names.append(decl.name)
        self._walk_children(decl)
        self._exit()

    def visit_class_decl(self, decl: ClassDecl) -> None:
        self._enter(decl)
        self._class_names.append(decl.name)
        self._walk_children(decl)
        self._exit()

    def visit_trait_decl(self, decl: TraitDecl) -> None:
        self._enter(decl)
        self._trait_names.append(decl.name)
        self._walk_children(decl)
        self._exit()

    def visit_interface_decl(self, decl: InterfaceDecl) -> None:
        self._enter(decl)
        self._interface_names.append(decl.name)
        self._walk_children(decl)
        self._exit()

    def visit_import_decl(self, decl: ImportDecl) -> None:
        self._enter(decl); self._exit()

    def visit_export_decl(self, decl: ExportDecl) -> None:
        self._enter(decl); self._exit()

    # ── Statements ─────────────────────────────────────────────

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit()

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit()

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit()

    def visit_until_stmt(self, stmt: UntilStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit()

    def visit_for_stmt(self, stmt: ForStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit()

    def visit_for_each_stmt(self, stmt: ForEachStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit()

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit()

    def visit_break_stmt(self, stmt: BreakStmt) -> None:
        self._enter(stmt); self._exit()

    def visit_continue_stmt(self, stmt: ContinueStmt) -> None:
        self._enter(stmt); self._exit()

    def visit_throw_stmt(self, stmt: ThrowStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit()

    def visit_try_stmt(self, stmt: TryStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit()

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        self._enter(stmt); self._walk_children(stmt); self._exit()

    def visit_empty_stmt(self, stmt: EmptyStmt) -> None:
        self._enter(stmt); self._exit()

    # ── Root ───────────────────────────────────────────────────

    def visit_program(self, program: Program) -> None:
        self._enter(program); self._walk_children(program); self._exit()

    def visit_module(self, module: Module) -> None:
        self._enter(module); self._walk_children(module); self._exit()

    # ── Helpers ────────────────────────────────────────────────

    def visit_parameter(self, param: Parameter) -> None:
        self._enter(param); self._walk_children(param); self._exit()

    def visit_struct_field(self, field: StructField) -> None:
        self._enter(field); self._walk_children(field); self._exit()

    def visit_enum_variant(self, variant: EnumVariant) -> None:
        self._enter(variant); self._walk_children(variant); self._exit()

    def visit_elif_branch(self, branch: ElifBranch) -> None:
        self._enter(branch); self._walk_children(branch); self._exit()
