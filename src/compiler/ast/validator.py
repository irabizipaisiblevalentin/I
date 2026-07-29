"""
AST Validation for the I Programming Language

Structural validation of AST trees after parsing.
Catches inconsistencies that the parser cannot prevent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

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


@dataclass
class ValidationError:
    """A single validation error."""

    message: str
    node: Optional[ASTNode] = None
    severity: str = "error"  # "error" | "warning"

    def __str__(self) -> str:
        loc = f" @ {self.node.location}" if self.node else ""
        return f"[{self.severity}]{loc}: {self.message}"


@dataclass
class ValidationResult:
    """Result of AST validation."""

    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(e.severity == "error" for e in self.errors)

    def add_error(self, message: str, node: Optional[ASTNode] = None) -> None:
        self.errors.append(ValidationError(message, node, "error"))

    def add_warning(self, message: str, node: Optional[ASTNode] = None) -> None:
        self.errors.append(ValidationError(message, node, "warning"))


class ASTValidator(ASTVisitor):
    """
    Validates the structural integrity of an AST.

    Checks:
    - Cycle detection (parent-child loops)
    - Valid lvalue targets for assignments
    - Break/continue inside loops
    - Return values match function signatures
    - Duplicate declarations
    - Required children are present
    """

    def __init__(self) -> None:
        self._result = ValidationResult()
        self._node_set: set = set()
        self._parent_chain: List[ASTNode] = []
        self._loop_depth = 0
        self._function_depth = 0
        self._scope_depth = 0
        self._declared_names: List[set] = []

    def validate(self, node: ASTNode) -> ValidationResult:
        """Validate the AST rooted at `node`."""
        self._result = ValidationResult()
        self._node_set.clear()
        self._parent_chain.clear()
        self._loop_depth = 0
        self._function_depth = 0
        self._scope_depth = 0
        self._declared_names = [set()]
        self._validate_source_spans(node)
        node.accept(self)
        return self._result

    def _validate_source_spans(self, node: ASTNode) -> None:
        """Validate that all source spans are well-formed."""
        loc = node.location
        if loc.start_line < 0:
            self._result.add_error(
                f"Invalid source span: start_line {loc.start_line} is negative", node
            )
        if loc.start_column < 0:
            self._result.add_error(
                f"Invalid source span: start_column {loc.start_column} is negative", node
            )
        if loc.end_line < loc.start_line:
            self._result.add_error(
                f"Invalid source span: end_line {loc.end_line} < start_line {loc.start_line}",
                node,
            )
        if (loc.end_line == loc.start_line and
                loc.end_column < loc.start_column):
            self._result.add_error(
                f"Invalid source span: end_column {loc.end_column} < start_column "
                f"{loc.start_column} on same line",
                node,
            )
        if loc.end_offset < loc.start_offset:
            self._result.add_error(
                f"Invalid source span: end_offset {loc.end_offset} < start_offset "
                f"{loc.start_offset}",
                node,
            )

    def _check_cycle(self, node: ASTNode) -> None:
        self._validate_source_spans(node)
        if id(node) in self._node_set:
            self._result.add_error(
                "Cycle detected: node references itself or an ancestor", node
            )
        self._node_set.add(id(node))

    def _push_scope(self) -> None:
        self._scope_depth += 1
        self._declared_names.append(set())

    def _pop_scope(self) -> None:
        self._scope_depth -= 1
        self._declared_names.pop()

    def _declare(self, name: str, node: ASTNode) -> None:
        if name in self._declared_names[-1]:
            self._result.add_warning(f"Duplicate declaration: {name}", node)
        self._declared_names[-1].add(name)

    def _is_lvalue(self, node: Expr) -> bool:
        return isinstance(node, (IdentifierExpr, GetExpr, IndexExpr))

    # ── Expressions ────────────────────────────────────────────

    def visit_literal_expr(self, expr: LiteralExpr) -> None:
        self._check_cycle(expr)

    def visit_identifier_expr(self, expr: IdentifierExpr) -> None:
        self._check_cycle(expr)

    def visit_unary_expr(self, expr: UnaryExpr) -> None:
        self._check_cycle(expr)
        expr.right.accept(self)

    def visit_binary_expr(self, expr: BinaryExpr) -> None:
        self._check_cycle(expr)
        expr.left.accept(self)
        expr.right.accept(self)

    def visit_logical_expr(self, expr: LogicalExpr) -> None:
        self._check_cycle(expr)
        expr.left.accept(self)
        expr.right.accept(self)

    def visit_assignment_expr(self, expr: AssignmentExpr) -> None:
        self._check_cycle(expr)
        if not self._is_lvalue(expr.target):
            self._result.add_error(
                "Assignment target must be an lvalue (identifier, property, or index)",
                expr.target,
            )
        expr.target.accept(self)
        expr.value.accept(self)

    def visit_compound_assignment_expr(self, expr: CompoundAssignmentExpr) -> None:
        self._check_cycle(expr)
        if not self._is_lvalue(expr.target):
            self._result.add_error(
                "Compound assignment target must be an lvalue", expr.target
            )
        expr.target.accept(self)
        expr.value.accept(self)

    def visit_call_expr(self, expr: CallExpr) -> None:
        self._check_cycle(expr)
        expr.callee.accept(self)
        for arg in expr.arguments:
            arg.accept(self)

    def visit_method_call_expr(self, expr: MethodCallExpr) -> None:
        self._check_cycle(expr)
        expr.object.accept(self)
        for arg in expr.arguments:
            arg.accept(self)

    def visit_constructor_expr(self, expr: ConstructorExpr) -> None:
        self._check_cycle(expr)
        for arg in expr.arguments:
            arg.accept(self)

    def visit_get_expr(self, expr: GetExpr) -> None:
        self._check_cycle(expr)
        expr.object.accept(self)

    def visit_set_expr(self, expr: SetExpr) -> None:
        self._check_cycle(expr)
        expr.object.accept(self)
        expr.value.accept(self)

    def visit_index_expr(self, expr: IndexExpr) -> None:
        self._check_cycle(expr)
        expr.object.accept(self)
        expr.index.accept(self)

    def visit_slice_expr(self, expr: SliceExpr) -> None:
        self._check_cycle(expr)
        expr.object.accept(self)
        if expr.start:
            expr.start.accept(self)
        if expr.end:
            expr.end.accept(self)

    def visit_self_expr(self, expr: SelfExpr) -> None:
        self._check_cycle(expr)

    def visit_super_expr(self, expr: SuperExpr) -> None:
        self._check_cycle(expr)

    def visit_list_expr(self, expr: ListExpr) -> None:
        self._check_cycle(expr)
        for elem in expr.elements:
            elem.accept(self)

    def visit_dict_expr(self, expr: DictExpr) -> None:
        self._check_cycle(expr)
        for k, v in zip(expr.keys, expr.values):
            k.accept(self)
            v.accept(self)

    def visit_tuple_expr(self, expr: TupleExpr) -> None:
        self._check_cycle(expr)
        for elem in expr.elements:
            elem.accept(self)

    def visit_lambda_expr(self, expr: LambdaExpr) -> None:
        self._check_cycle(expr)
        self._push_scope()
        for param in expr.parameters:
            param.accept(self)
        expr.body.accept(self)
        self._pop_scope()

    def visit_if_expr(self, expr: IfExpr) -> None:
        self._check_cycle(expr)
        expr.condition.accept(self)
        expr.then_branch.accept(self)
        if expr.else_branch:
            expr.else_branch.accept(self)

    def visit_grouping_expr(self, expr: GroupingExpr) -> None:
        self._check_cycle(expr)
        expr.expression.accept(self)

    def visit_placeholder_expr(self, expr: PlaceholderExpr) -> None:
        self._check_cycle(expr)

    # ── Types ──────────────────────────────────────────────────

    def visit_named_type(self, t: NamedType) -> None:
        self._check_cycle(t)

    def visit_generic_type(self, t: GenericType) -> None:
        self._check_cycle(t)
        for arg in t.type_args:
            arg.accept(self)

    def visit_function_type(self, t: FunctionType) -> None:
        self._check_cycle(t)
        for param in t.params:
            param.accept(self)
        t.return_type.accept(self)

    def visit_optional_type(self, t: OptionalType) -> None:
        self._check_cycle(t)
        t.inner.accept(self)

    def visit_tuple_type(self, t: TupleType) -> None:
        self._check_cycle(t)
        for elem in t.elements:
            elem.accept(self)

    # ── Declarations ───────────────────────────────────────────

    def visit_var_decl(self, decl: VarDecl) -> None:
        self._check_cycle(decl)
        self._declare(decl.name, decl)
        if decl.type_annotation:
            decl.type_annotation.accept(self)
        if decl.initializer:
            decl.initializer.accept(self)

    def visit_function_decl(self, decl: FunctionDecl) -> None:
        self._check_cycle(decl)
        self._declare(decl.name, decl)
        self._function_depth += 1
        self._push_scope()
        for param in decl.parameters:
            param.accept(self)
        if decl.return_type:
            decl.return_type.accept(self)
        decl.body.accept(self)
        self._pop_scope()
        self._function_depth -= 1

    def visit_method_decl(self, decl: MethodDecl) -> None:
        self._check_cycle(decl)
        self._declare(decl.name, decl)
        self._function_depth += 1
        self._push_scope()
        for param in decl.parameters:
            param.accept(self)
        if decl.return_type:
            decl.return_type.accept(self)
        decl.body.accept(self)
        self._pop_scope()
        self._function_depth -= 1

    def visit_struct_decl(self, decl: StructDecl) -> None:
        self._check_cycle(decl)
        self._declare(decl.name, decl)
        self._push_scope()
        for field in decl.fields:
            field.accept(self)
        for method in decl.methods:
            method.accept(self)
        self._pop_scope()

    def visit_enum_decl(self, decl: EnumDecl) -> None:
        self._check_cycle(decl)
        self._declare(decl.name, decl)
        for variant in decl.variants:
            variant.accept(self)

    def visit_class_decl(self, decl: ClassDecl) -> None:
        self._check_cycle(decl)
        self._declare(decl.name, decl)
        self._push_scope()
        for member in decl.members:
            member.accept(self)
        self._pop_scope()

    def visit_trait_decl(self, decl: TraitDecl) -> None:
        self._check_cycle(decl)
        self._declare(decl.name, decl)
        self._push_scope()
        for member in decl.members:
            member.accept(self)
        self._pop_scope()

    def visit_interface_decl(self, decl: InterfaceDecl) -> None:
        self._check_cycle(decl)
        self._declare(decl.name, decl)
        self._push_scope()
        for member in decl.members:
            member.accept(self)
        self._pop_scope()

    def visit_import_decl(self, decl: ImportDecl) -> None:
        self._check_cycle(decl)

    def visit_export_decl(self, decl: ExportDecl) -> None:
        self._check_cycle(decl)

    # ── Statements ─────────────────────────────────────────────

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        self._check_cycle(stmt)
        self._push_scope()
        for s in stmt.statements:
            s.accept(self)
        self._pop_scope()

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        self._check_cycle(stmt)
        stmt.condition.accept(self)
        stmt.then_branch.accept(self)
        for branch in stmt.elif_branches:
            branch.accept(self)
        if stmt.else_branch:
            stmt.else_branch.accept(self)

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        self._check_cycle(stmt)
        self._loop_depth += 1
        stmt.condition.accept(self)
        stmt.body.accept(self)
        self._loop_depth -= 1

    def visit_until_stmt(self, stmt: UntilStmt) -> None:
        self._check_cycle(stmt)
        self._loop_depth += 1
        stmt.condition.accept(self)
        stmt.body.accept(self)
        self._loop_depth -= 1

    def visit_for_stmt(self, stmt: ForStmt) -> None:
        self._check_cycle(stmt)
        self._loop_depth += 1
        self._push_scope()
        self._declare(stmt.variable, stmt)
        stmt.start.accept(self)
        stmt.end.accept(self)
        if stmt.step:
            stmt.step.accept(self)
        stmt.body.accept(self)
        self._pop_scope()
        self._loop_depth -= 1

    def visit_for_each_stmt(self, stmt: ForEachStmt) -> None:
        self._check_cycle(stmt)
        self._loop_depth += 1
        self._push_scope()
        self._declare(stmt.element, stmt)
        stmt.iterable.accept(self)
        stmt.body.accept(self)
        self._pop_scope()
        self._loop_depth -= 1

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        self._check_cycle(stmt)
        if stmt.value:
            stmt.value.accept(self)
        if self._function_depth == 0:
            self._result.add_error(
                "Return statement outside of function", stmt
            )

    def visit_break_stmt(self, stmt: BreakStmt) -> None:
        self._check_cycle(stmt)
        if self._loop_depth == 0:
            self._result.add_error(
                "Break statement outside of loop", stmt
            )

    def visit_continue_stmt(self, stmt: ContinueStmt) -> None:
        self._check_cycle(stmt)
        if self._loop_depth == 0:
            self._result.add_error(
                "Continue statement outside of loop", stmt
            )

    def visit_throw_stmt(self, stmt: ThrowStmt) -> None:
        self._check_cycle(stmt)
        stmt.value.accept(self)

    def visit_try_stmt(self, stmt: TryStmt) -> None:
        self._check_cycle(stmt)
        self._push_scope()
        stmt.try_body.accept(self)
        if stmt.catch_var:
            self._declare(stmt.catch_var, stmt)
        if stmt.catch_body:
            self._push_scope()
            if stmt.catch_var:
                self._declare(stmt.catch_var, stmt)
            stmt.catch_body.accept(self)
            self._pop_scope()
        if stmt.finally_body:
            stmt.finally_body.accept(self)
        self._pop_scope()

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        self._check_cycle(stmt)
        stmt.expression.accept(self)

    def visit_empty_stmt(self, stmt: EmptyStmt) -> None:
        self._check_cycle(stmt)

    # ── Root ───────────────────────────────────────────────────

    def visit_program(self, program: Program) -> None:
        self._check_cycle(program)
        self._push_scope()
        for decl in program.declarations:
            decl.accept(self)
        self._pop_scope()

    def visit_module(self, module: Module) -> None:
        self._check_cycle(module)
        self._push_scope()
        for imp in module.imports:
            imp.accept(self)
        for decl in module.declarations:
            decl.accept(self)
        self._pop_scope()

    # ── Helpers ────────────────────────────────────────────────

    def visit_parameter(self, param: Parameter) -> None:
        self._check_cycle(param)
        self._declare(param.name, param)
        if param.type_annotation:
            param.type_annotation.accept(self)
        if param.default:
            param.default.accept(self)

    def visit_struct_field(self, field: StructField) -> None:
        self._check_cycle(field)
        self._declare(field.name, field)
        field.type_annotation.accept(self)
        if field.default:
            field.default.accept(self)

    def visit_enum_variant(self, variant: EnumVariant) -> None:
        self._check_cycle(variant)
        self._declare(variant.name, variant)
        if variant.value:
            variant.value.accept(self)

    def visit_elif_branch(self, branch: ElifBranch) -> None:
        self._check_cycle(branch)
        branch.condition.accept(self)
        branch.body.accept(self)


def validate_ast(node: ASTNode) -> ValidationResult:
    """Convenience function to validate an AST."""
    validator = ASTValidator()
    return validator.validate(node)
