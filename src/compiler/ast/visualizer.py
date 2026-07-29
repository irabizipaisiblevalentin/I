"""
AST Visualization for the I Programming Language

Generates visual representations of AST trees:
- Text-based tree diagrams (for terminal output)
- Graphviz DOT output (for graph rendering)
"""

from __future__ import annotations

from typing import List, TextIO

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
    SelfExpr,
    SetExpr,
    SliceExpr,
    StructDecl,
    StructField,
    SuperExpr,
    ThrowStmt,
    TryStmt,
    TupleExpr,
    TupleType,
    TypeNode,
    TraitDecl,
    UnaryExpr,
    UntilStmt,
    VarDecl,
    WhileStmt,
)


# ══════════════════════════════════════════════════════════════════
# Text Tree — terminal-friendly tree view
# ══════════════════════════════════════════════════════════════════


class TextTreeVisualizer:
    """
    Generates a Unicode box-drawing tree diagram.

    Usage:
        visualizer = TextTreeVisualizer()
        print(visualizer.render(program))
    """

    def __init__(self, show_ids: bool = False, show_location: bool = False) -> None:
        self._show_ids = show_ids
        self._show_location = show_location
        self._lines: List[str] = []
        self._prefix = ""

    def render(self, node: ASTNode) -> str:
        """Render the AST as a text tree."""
        self._lines = []
        self._render_node(node, "", True)
        return "\n".join(self._lines)

    def _render_node(self, node: ASTNode, prefix: str, is_last: bool) -> None:
        connector = "└── " if is_last else "├── "
        label = self._node_label(node)
        self._lines.append(prefix + connector + label)

        children = node.children()
        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(children):
            self._render_node(child, new_prefix, i == len(children) - 1)

    def _node_label(self, node: ASTNode) -> str:
        parts = [node.__class__.__name__]
        if self._show_ids:
            parts.append(f"#{node.node_id}")
        if self._show_location:
            loc = node.location
            parts.append(f"@{loc.start_line}:{loc.start_column}")

        # Add semantic info
        extra = self._semantic_info(node)
        if extra:
            parts.append(extra)

        return " ".join(parts)

    def _semantic_info(self, node: ASTNode) -> str:
        if isinstance(node, LiteralExpr):
            return f"({node.value!r})"
        if isinstance(node, IdentifierExpr):
            return f"({node.name})"
        if isinstance(node, (BinaryExpr, LogicalExpr)):
            return f"({node.operator})"
        if isinstance(node, UnaryExpr):
            return f"({node.operator})"
        if isinstance(node, CompoundAssignmentExpr):
            return f"({node.operator})"
        if isinstance(node, (VarDecl, FunctionDecl, StructDecl, EnumDecl,
                             ClassDecl, TraitDecl, InterfaceDecl, MethodDecl)):
            return f"({node.name})"
        if isinstance(node, NamedType):
            return f"({node.name})"
        if isinstance(node, GenericType):
            return f"({node.name}<...>)"
        if isinstance(node, FunctionType):
            return "(-> ...)"
        if isinstance(node, Parameter):
            return f"({node.name})"
        if isinstance(node, StructField):
            return f"({node.name})"
        if isinstance(node, EnumVariant):
            return f"({node.name})"
        if isinstance(node, ImportDecl):
            return f"({node.path})"
        if isinstance(node, ExportDecl):
            return f"({node.name})"
        if isinstance(node, ForStmt):
            return f"({node.variable})"
        if isinstance(node, ForEachStmt):
            return f"({node.element})"
        if isinstance(node, GetExpr):
            return f"({node.property})"
        if isinstance(node, SetExpr):
            return f"({node.property})"
        if isinstance(node, ConstructorExpr):
            return f"({node.class_name})"
        if isinstance(node, SuperExpr):
            return f"({node.method})"
        if isinstance(node, MethodCallExpr):
            return f"({node.method})"
        if isinstance(node, Module):
            return f"({node.name})"
        if isinstance(node, PlaceholderExpr):
            return f"({node.description})" if node.description else ""
        if isinstance(node, TryStmt) and node.catch_var:
            return f"({node.catch_var})"
        if isinstance(node, ClassDecl) and node.parent:
            return f"(extends {node.parent})"
        return ""


# ══════════════════════════════════════════════════════════════════
# Graphviz DOT — renderable graph output
# ══════════════════════════════════════════════════════════════════


class DOTVisualizer(ASTVisitor):
    """
    Generates Graphviz DOT format output for AST visualization.

    Usage:
        visualizer = DOTVisualizer()
        dot = visualizer.to_dot(program)
        # Save to file: open("ast.dot", "w").write(dot)
        # Render: dot -Tpng ast.dot -o ast.png
    """

    def __init__(self, show_ids: bool = True, show_location: bool = False) -> None:
        self._show_ids = show_ids
        self._show_location = show_location
        self._nodes: List[str] = []
        self._edges: List[str] = []
        self._counter = 0

    def to_dot(self, node: ASTNode) -> str:
        """Generate DOT format string."""
        self._nodes = []
        self._edges = []
        self._counter = 0
        node.accept(self)
        lines = [
            "digraph AST {",
            '  node [shape=box, fontname="monospace", fontsize=10];',
            '  edge [fontname="monospace", fontsize=8];',
        ]
        lines.extend(self._nodes)
        lines.extend(self._edges)
        lines.append("}")
        return "\n".join(lines)

    def _next_id(self) -> str:
        self._counter += 1
        return f"n{self._counter}"

    def _escape(self, s: str) -> str:
        return s.replace('"', '\\"')

    def _make_label(self, node: ASTNode) -> str:
        parts = [node.__class__.__name__]
        if self._show_ids:
            parts.append(f"#{node.node_id}")
        extra = self._semantic_info(node)
        if extra:
            parts.append(extra)
        if self._show_location:
            loc = node.location
            parts.append(f"\\n@{loc.start_line}:{loc.start_column}")
        return self._escape(" ".join(parts))

    def _semantic_info(self, node: ASTNode) -> str:
        if isinstance(node, LiteralExpr):
            return f"{node.value!r}"
        if isinstance(node, IdentifierExpr):
            return node.name
        if isinstance(node, (BinaryExpr, LogicalExpr)):
            return node.operator
        if isinstance(node, UnaryExpr):
            return node.operator
        if isinstance(node, CompoundAssignmentExpr):
            return node.operator
        if isinstance(node, (VarDecl, FunctionDecl, StructDecl, EnumDecl,
                             ClassDecl, TraitDecl, InterfaceDecl, MethodDecl)):
            return node.name
        if isinstance(node, NamedType):
            return node.name
        if isinstance(node, GenericType):
            return f"{node.name}<...>"
        if isinstance(node, Parameter):
            return node.name
        if isinstance(node, StructField):
            return node.name
        if isinstance(node, EnumVariant):
            return node.name
        if isinstance(node, ImportDecl):
            return node.path
        if isinstance(node, ExportDecl):
            return node.name
        if isinstance(node, ForStmt):
            return node.variable
        if isinstance(node, ForEachStmt):
            return node.element
        if isinstance(node, GetExpr):
            return node.property
        if isinstance(node, SetExpr):
            return node.property
        if isinstance(node, ConstructorExpr):
            return node.class_name
        if isinstance(node, SuperExpr):
            return node.method
        if isinstance(node, MethodCallExpr):
            return node.method
        if isinstance(node, Module):
            return node.name
        return ""

    def _color(self, node: ASTNode) -> str:
        """Return a color based on node category."""
        if isinstance(node, Expr):
            return "#e8f5e9"  # green for expressions
        if isinstance(node, TypeNode):
            return "#e3f2fd"  # blue for types
        if isinstance(node, Decl):
            return "#fff3e0"  # orange for declarations
        if isinstance(node, (Program, Module)):
            return "#fce4ec"  # pink for root
        return "#f5f5f5"  # gray default

    def _add_node(self, node: ASTNode) -> str:
        nid = self._next_id()
        label = self._make_label(node)
        color = self._color(node)
        self._nodes.append(
            f'  {nid} [label="{label}", style=filled, fillcolor="{color}"];'
        )
        return nid

    def _walk_children(self, parent_id: str, node: ASTNode) -> None:
        for child in node.children():
            child_id = self._add_node(child)
            self._edges.append(f'  {parent_id} -> {child_id};')
            child.accept(self)

    # ── Generic accept ─────────────────────────────────────────

    def visit_literal_expr(self, e: LiteralExpr) -> None: pass
    def visit_identifier_expr(self, e: IdentifierExpr) -> None: pass
    def visit_unary_expr(self, e: UnaryExpr) -> None: pass
    def visit_binary_expr(self, e: BinaryExpr) -> None: pass
    def visit_logical_expr(self, e: LogicalExpr) -> None: pass
    def visit_assignment_expr(self, e: AssignmentExpr) -> None: pass
    def visit_compound_assignment_expr(self, e: CompoundAssignmentExpr) -> None: pass
    def visit_call_expr(self, e: CallExpr) -> None: pass
    def visit_constructor_expr(self, e: ConstructorExpr) -> None: pass
    def visit_get_expr(self, e: GetExpr) -> None: pass
    def visit_set_expr(self, e: SetExpr) -> None: pass
    def visit_index_expr(self, e: IndexExpr) -> None: pass
    def visit_slice_expr(self, e: SliceExpr) -> None: pass
    def visit_self_expr(self, e: SelfExpr) -> None: pass
    def visit_super_expr(self, e: SuperExpr) -> None: pass
    def visit_list_expr(self, e: ListExpr) -> None: pass
    def visit_dict_expr(self, e: DictExpr) -> None: pass
    def visit_tuple_expr(self, e: TupleExpr) -> None: pass
    def visit_lambda_expr(self, e: LambdaExpr) -> None: pass
    def visit_if_expr(self, e: IfExpr) -> None: pass
    def visit_grouping_expr(self, e: GroupingExpr) -> None: pass
    def visit_named_type(self, t: NamedType) -> None: pass
    def visit_generic_type(self, t: GenericType) -> None: pass
    def visit_function_type(self, t: FunctionType) -> None: pass
    def visit_optional_type(self, t: OptionalType) -> None: pass
    def visit_tuple_type(self, t: TupleType) -> None: pass
    def visit_var_decl(self, d: VarDecl) -> None: pass
    def visit_function_decl(self, d: FunctionDecl) -> None: pass
    def visit_struct_decl(self, d: StructDecl) -> None: pass
    def visit_enum_decl(self, d: EnumDecl) -> None: pass
    def visit_class_decl(self, d: ClassDecl) -> None: pass
    def visit_trait_decl(self, d: TraitDecl) -> None: pass
    def visit_interface_decl(self, d: InterfaceDecl) -> None: pass
    def visit_import_decl(self, d: ImportDecl) -> None: pass
    def visit_export_decl(self, d: ExportDecl) -> None: pass
    def visit_block_stmt(self, s: BlockStmt) -> None: pass
    def visit_if_stmt(self, s: IfStmt) -> None: pass
    def visit_while_stmt(self, s: WhileStmt) -> None: pass
    def visit_until_stmt(self, s: UntilStmt) -> None: pass
    def visit_for_stmt(self, s: ForStmt) -> None: pass
    def visit_for_each_stmt(self, s: ForEachStmt) -> None: pass
    def visit_return_stmt(self, s: ReturnStmt) -> None: pass
    def visit_break_stmt(self, s: BreakStmt) -> None: pass
    def visit_continue_stmt(self, s: ContinueStmt) -> None: pass
    def visit_throw_stmt(self, s: ThrowStmt) -> None: pass
    def visit_try_stmt(self, s: TryStmt) -> None: pass
    def visit_expression_stmt(self, s: ExpressionStmt) -> None: pass
    def visit_empty_stmt(self, s: EmptyStmt) -> None: pass
    def visit_program(self, p: Program) -> None: pass
    def visit_parameter(self, p: Parameter) -> None: pass
    def visit_struct_field(self, f: StructField) -> None: pass
    def visit_enum_variant(self, v: EnumVariant) -> None: pass
    def visit_elif_branch(self, b: ElifBranch) -> None: pass

    # Override all visit methods to add node and walk children
    def _visit(self, node: ASTNode) -> str:
        nid = self._add_node(node)
        self._walk_children(nid, node)
        return nid

    def visit_literal_expr(self, e: LiteralExpr) -> None: self._visit(e)
    def visit_identifier_expr(self, e: IdentifierExpr) -> None: self._visit(e)
    def visit_unary_expr(self, e: UnaryExpr) -> None: self._visit(e)
    def visit_binary_expr(self, e: BinaryExpr) -> None: self._visit(e)
    def visit_logical_expr(self, e: LogicalExpr) -> None: self._visit(e)
    def visit_assignment_expr(self, e: AssignmentExpr) -> None: self._visit(e)
    def visit_compound_assignment_expr(self, e: CompoundAssignmentExpr) -> None: self._visit(e)
    def visit_call_expr(self, e: CallExpr) -> None: self._visit(e)
    def visit_method_call_expr(self, e: MethodCallExpr) -> None: self._visit(e)
    def visit_constructor_expr(self, e: ConstructorExpr) -> None: self._visit(e)
    def visit_get_expr(self, e: GetExpr) -> None: self._visit(e)
    def visit_set_expr(self, e: SetExpr) -> None: self._visit(e)
    def visit_index_expr(self, e: IndexExpr) -> None: self._visit(e)
    def visit_slice_expr(self, e: SliceExpr) -> None: self._visit(e)
    def visit_self_expr(self, e: SelfExpr) -> None: self._visit(e)
    def visit_super_expr(self, e: SuperExpr) -> None: self._visit(e)
    def visit_list_expr(self, e: ListExpr) -> None: self._visit(e)
    def visit_dict_expr(self, e: DictExpr) -> None: self._visit(e)
    def visit_tuple_expr(self, e: TupleExpr) -> None: self._visit(e)
    def visit_lambda_expr(self, e: LambdaExpr) -> None: self._visit(e)
    def visit_if_expr(self, e: IfExpr) -> None: self._visit(e)
    def visit_grouping_expr(self, e: GroupingExpr) -> None: self._visit(e)
    def visit_placeholder_expr(self, e: PlaceholderExpr) -> None: self._visit(e)
    def visit_named_type(self, t: NamedType) -> None: self._visit(t)
    def visit_generic_type(self, t: GenericType) -> None: self._visit(t)
    def visit_function_type(self, t: FunctionType) -> None: self._visit(t)
    def visit_optional_type(self, t: OptionalType) -> None: self._visit(t)
    def visit_tuple_type(self, t: TupleType) -> None: self._visit(t)
    def visit_var_decl(self, d: VarDecl) -> None: self._visit(d)
    def visit_function_decl(self, d: FunctionDecl) -> None: self._visit(d)
    def visit_method_decl(self, d: MethodDecl) -> None: self._visit(d)
    def visit_struct_decl(self, d: StructDecl) -> None: self._visit(d)
    def visit_enum_decl(self, d: EnumDecl) -> None: self._visit(d)
    def visit_class_decl(self, d: ClassDecl) -> None: self._visit(d)
    def visit_trait_decl(self, d: TraitDecl) -> None: self._visit(d)
    def visit_interface_decl(self, d: InterfaceDecl) -> None: self._visit(d)
    def visit_import_decl(self, d: ImportDecl) -> None: self._visit(d)
    def visit_export_decl(self, d: ExportDecl) -> None: self._visit(d)
    def visit_block_stmt(self, s: BlockStmt) -> None: self._visit(s)
    def visit_if_stmt(self, s: IfStmt) -> None: self._visit(s)
    def visit_while_stmt(self, s: WhileStmt) -> None: self._visit(s)
    def visit_until_stmt(self, s: UntilStmt) -> None: self._visit(s)
    def visit_for_stmt(self, s: ForStmt) -> None: self._visit(s)
    def visit_for_each_stmt(self, s: ForEachStmt) -> None: self._visit(s)
    def visit_return_stmt(self, s: ReturnStmt) -> None: self._visit(s)
    def visit_break_stmt(self, s: BreakStmt) -> None: self._visit(s)
    def visit_continue_stmt(self, s: ContinueStmt) -> None: self._visit(s)
    def visit_throw_stmt(self, s: ThrowStmt) -> None: self._visit(s)
    def visit_try_stmt(self, s: TryStmt) -> None: self._visit(s)
    def visit_expression_stmt(self, s: ExpressionStmt) -> None: self._visit(s)
    def visit_empty_stmt(self, s: EmptyStmt) -> None: self._visit(s)
    def visit_program(self, p: Program) -> None: self._visit(p)
    def visit_module(self, m: Module) -> None: self._visit(m)
    def visit_parameter(self, p: Parameter) -> None: self._visit(p)
    def visit_struct_field(self, f: StructField) -> None: self._visit(f)
    def visit_enum_variant(self, v: EnumVariant) -> None: self._visit(v)
    def visit_elif_branch(self, b: ElifBranch) -> None: self._visit(b)
