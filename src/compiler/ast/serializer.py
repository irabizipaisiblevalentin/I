"""
AST Serialization for the I Programming Language

JSON-based serialization/deserialization of AST trees.
Useful for caching, debugging, and cross-language interop.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Type

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
    NodeType,
    NamedType,
    OptionalType,
    Parameter,
    PlaceholderExpr,
    Program,
    ReturnStmt,
    SelfExpr,
    SetExpr,
    SliceExpr,
    SourceLocation,
    StructDecl,
    StructField,
    SuperExpr,
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
# Serializer — AST → JSON
# ══════════════════════════════════════════════════════════════════


class ASTSerializer(ASTVisitor):
    """
    Serializes an AST to a JSON-serializable dictionary.

    Usage:
        serializer = ASTSerializer()
        data = serializer.to_dict(program)
        json_str = json.dumps(data, indent=2)
    """

    def __init__(self) -> None:
        self._result: Any = None

    def to_dict(self, node: ASTNode) -> Dict[str, Any]:
        """Serialize an AST node to a dictionary."""
        self._result = None
        node.accept(self)
        return self._result

    def to_json(self, node: ASTNode, indent: int = 2) -> str:
        """Serialize an AST node to a JSON string."""
        return json.dumps(self.to_dict(node), indent=indent, ensure_ascii=False)

    def _loc_dict(self, loc: SourceLocation) -> Dict[str, Any]:
        return {
            "file": loc.file,
            "start_line": loc.start_line,
            "start_column": loc.start_column,
            "end_line": loc.end_line,
            "end_column": loc.end_column,
            "start_offset": loc.start_offset,
            "end_offset": loc.end_offset,
        }

    def _node(self, node: ASTNode, kind: str, **extra: Any) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "kind": kind,
            "node_id": node.node_id,
            "location": self._loc_dict(node.location),
        }
        d.update(extra)
        self._result = d
        return d

    def _serialize_list(self, nodes: list) -> List[Dict[str, Any]]:
        results = []
        for n in nodes:
            n.accept(self)
            results.append(self._result)
        return results

    # ── Expressions ────────────────────────────────────────────

    def visit_literal_expr(self, expr: LiteralExpr) -> None:
        self._node(expr, "LiteralExpr", value=expr.value,
                   token_type=expr.token_type.name if expr.token_type else None)

    def visit_identifier_expr(self, expr: IdentifierExpr) -> None:
        self._node(expr, "IdentifierExpr", name=expr.name)

    def visit_unary_expr(self, expr: UnaryExpr) -> None:
        expr.right.accept(self)
        right = self._result
        self._node(expr, "UnaryExpr", operator=expr.operator, right=right)

    def visit_binary_expr(self, expr: BinaryExpr) -> None:
        expr.left.accept(self)
        left = self._result
        expr.right.accept(self)
        right = self._result
        self._node(expr, "BinaryExpr", operator=expr.operator, left=left, right=right)

    def visit_logical_expr(self, expr: LogicalExpr) -> None:
        expr.left.accept(self)
        left = self._result
        expr.right.accept(self)
        right = self._result
        self._node(expr, "LogicalExpr", operator=expr.operator, left=left, right=right)

    def visit_assignment_expr(self, expr: AssignmentExpr) -> None:
        expr.target.accept(self)
        target = self._result
        expr.value.accept(self)
        value = self._result
        self._node(expr, "AssignmentExpr", target=target, value=value)

    def visit_compound_assignment_expr(self, expr: CompoundAssignmentExpr) -> None:
        expr.target.accept(self)
        target = self._result
        expr.value.accept(self)
        value = self._result
        self._node(expr, "CompoundAssignmentExpr", target=target,
                   operator=expr.operator, value=value)

    def visit_call_expr(self, expr: CallExpr) -> None:
        expr.callee.accept(self)
        callee = self._result
        args = self._serialize_list(expr.arguments)
        self._node(expr, "CallExpr", callee=callee, arguments=args)

    def visit_method_call_expr(self, expr: MethodCallExpr) -> None:
        expr.object.accept(self)
        obj = self._result
        args = self._serialize_list(expr.arguments)
        self._node(expr, "MethodCallExpr", object=obj, method=expr.method,
                   arguments=args)

    def visit_constructor_expr(self, expr: ConstructorExpr) -> None:
        args = self._serialize_list(expr.arguments)
        self._node(expr, "ConstructorExpr", class_name=expr.class_name, arguments=args)

    def visit_get_expr(self, expr: GetExpr) -> None:
        expr.object.accept(self)
        obj = self._result
        self._node(expr, "GetExpr", object=obj, property=expr.property)

    def visit_set_expr(self, expr: SetExpr) -> None:
        expr.object.accept(self)
        obj = self._result
        expr.value.accept(self)
        value = self._result
        self._node(expr, "SetExpr", object=obj, property=expr.property, value=value)

    def visit_index_expr(self, expr: IndexExpr) -> None:
        expr.object.accept(self)
        obj = self._result
        expr.index.accept(self)
        idx = self._result
        self._node(expr, "IndexExpr", object=obj, index=idx)

    def visit_slice_expr(self, expr: SliceExpr) -> None:
        expr.object.accept(self)
        obj = self._result
        start = None
        if expr.start:
            expr.start.accept(self)
            start = self._result
        end = None
        if expr.end:
            expr.end.accept(self)
            end = self._result
        self._node(expr, "SliceExpr", object=obj, start=start, end=end)

    def visit_self_expr(self, expr: SelfExpr) -> None:
        self._node(expr, "SelfExpr")

    def visit_super_expr(self, expr: SuperExpr) -> None:
        self._node(expr, "SuperExpr", method=expr.method)

    def visit_list_expr(self, expr: ListExpr) -> None:
        elements = self._serialize_list(expr.elements)
        self._node(expr, "ListExpr", elements=elements)

    def visit_dict_expr(self, expr: DictExpr) -> None:
        keys = self._serialize_list(expr.keys)
        vals = self._serialize_list(expr.values)
        self._node(expr, "DictExpr", keys=keys, values=vals)

    def visit_tuple_expr(self, expr: TupleExpr) -> None:
        elements = self._serialize_list(expr.elements)
        self._node(expr, "TupleExpr", elements=elements)

    def visit_lambda_expr(self, expr: LambdaExpr) -> None:
        params = self._serialize_list(expr.parameters)
        expr.body.accept(self)
        self._node(expr, "LambdaExpr", parameters=params, body=self._result)

    def visit_if_expr(self, expr: IfExpr) -> None:
        expr.condition.accept(self)
        cond = self._result
        expr.then_branch.accept(self)
        then = self._result
        else_b = None
        if expr.else_branch:
            expr.else_branch.accept(self)
            else_b = self._result
        self._node(expr, "IfExpr", condition=cond, then_branch=then, else_branch=else_b)

    def visit_grouping_expr(self, expr: GroupingExpr) -> None:
        expr.expression.accept(self)
        self._node(expr, "GroupingExpr", expression=self._result)

    def visit_placeholder_expr(self, expr: PlaceholderExpr) -> None:
        self._node(expr, "PlaceholderExpr", description=expr.description)

    # ── Types ──────────────────────────────────────────────────

    def visit_named_type(self, t: NamedType) -> None:
        self._node(t, "NamedType", name=t.name)

    def visit_generic_type(self, t: GenericType) -> None:
        args = self._serialize_list(t.type_args)
        self._node(t, "GenericType", name=t.name, type_args=args)

    def visit_function_type(self, t: FunctionType) -> None:
        params = self._serialize_list(t.params)
        t.return_type.accept(self)
        self._node(t, "FunctionType", params=params, return_type=self._result)

    def visit_optional_type(self, t: OptionalType) -> None:
        t.inner.accept(self)
        self._node(t, "OptionalType", inner=self._result)

    def visit_tuple_type(self, t: TupleType) -> None:
        elements = self._serialize_list(t.elements)
        self._node(t, "TupleType", elements=elements)

    # ── Declarations ───────────────────────────────────────────

    def visit_var_decl(self, decl: VarDecl) -> None:
        type_ann = None
        if decl.type_annotation:
            decl.type_annotation.accept(self)
            type_ann = self._result
        init = None
        if decl.initializer:
            decl.initializer.accept(self)
            init = self._result
        self._node(decl, "VarDecl", name=decl.name, type_annotation=type_ann,
                   initializer=init, is_const=decl.is_const)

    def visit_function_decl(self, decl: FunctionDecl) -> None:
        params = self._serialize_list(decl.parameters)
        ret = None
        if decl.return_type:
            decl.return_type.accept(self)
            ret = self._result
        decl.body.accept(self)
        self._node(decl, "FunctionDecl", name=decl.name, parameters=params,
                   return_type=ret, body=self._result)

    def visit_method_decl(self, decl: MethodDecl) -> None:
        params = self._serialize_list(decl.parameters)
        ret = None
        if decl.return_type:
            decl.return_type.accept(self)
            ret = self._result
        decl.body.accept(self)
        self._node(decl, "MethodDecl", name=decl.name, parameters=params,
                   return_type=ret, body=self._result, is_static=decl.is_static)

    def visit_struct_decl(self, decl: StructDecl) -> None:
        fields = self._serialize_list(decl.fields)
        methods = self._serialize_list(decl.methods)
        self._node(decl, "StructDecl", name=decl.name, fields=fields, methods=methods)

    def visit_enum_decl(self, decl: EnumDecl) -> None:
        variants = self._serialize_list(decl.variants)
        self._node(decl, "EnumDecl", name=decl.name, variants=variants)

    def visit_class_decl(self, decl: ClassDecl) -> None:
        members = self._serialize_list(decl.members)
        self._node(decl, "ClassDecl", name=decl.name, parent=decl.parent, members=members)

    def visit_trait_decl(self, decl: TraitDecl) -> None:
        members = self._serialize_list(decl.members)
        self._node(decl, "TraitDecl", name=decl.name, members=members)

    def visit_interface_decl(self, decl: InterfaceDecl) -> None:
        members = self._serialize_list(decl.members)
        self._node(decl, "InterfaceDecl", name=decl.name, members=members)

    def visit_import_decl(self, decl: ImportDecl) -> None:
        self._node(decl, "ImportDecl", path=decl.path, alias=decl.alias)

    def visit_export_decl(self, decl: ExportDecl) -> None:
        self._node(decl, "ExportDecl", name=decl.name)

    # ── Statements ─────────────────────────────────────────────

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        stmts = self._serialize_list(stmt.statements)
        self._node(stmt, "BlockStmt", statements=stmts)

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        stmt.condition.accept(self)
        cond = self._result
        stmt.then_branch.accept(self)
        then = self._result
        elifs = self._serialize_list(stmt.elif_branches)
        else_b = None
        if stmt.else_branch:
            stmt.else_branch.accept(self)
            else_b = self._result
        self._node(stmt, "IfStmt", condition=cond, then_branch=then,
                   elif_branches=elifs, else_branch=else_b)

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        stmt.condition.accept(self)
        cond = self._result
        stmt.body.accept(self)
        self._node(stmt, "WhileStmt", condition=cond, body=self._result)

    def visit_until_stmt(self, stmt: UntilStmt) -> None:
        stmt.condition.accept(self)
        cond = self._result
        stmt.body.accept(self)
        self._node(stmt, "UntilStmt", condition=cond, body=self._result)

    def visit_for_stmt(self, stmt: ForStmt) -> None:
        stmt.start.accept(self)
        start = self._result
        stmt.end.accept(self)
        end = self._result
        step = None
        if stmt.step:
            stmt.step.accept(self)
            step = self._result
        stmt.body.accept(self)
        self._node(stmt, "ForStmt", variable=stmt.variable, start=start,
                   end=end, step=step, body=self._result)

    def visit_for_each_stmt(self, stmt: ForEachStmt) -> None:
        stmt.iterable.accept(self)
        iterable = self._result
        stmt.body.accept(self)
        self._node(stmt, "ForEachStmt", element=stmt.element, iterable=iterable,
                   body=self._result)

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        val = None
        if stmt.value:
            stmt.value.accept(self)
            val = self._result
        self._node(stmt, "ReturnStmt", value=val)

    def visit_break_stmt(self, stmt: BreakStmt) -> None:
        self._node(stmt, "BreakStmt")

    def visit_continue_stmt(self, stmt: ContinueStmt) -> None:
        self._node(stmt, "ContinueStmt")

    def visit_throw_stmt(self, stmt: ThrowStmt) -> None:
        stmt.value.accept(self)
        self._node(stmt, "ThrowStmt", value=self._result)

    def visit_try_stmt(self, stmt: TryStmt) -> None:
        stmt.try_body.accept(self)
        try_b = self._result
        catch_b = None
        if stmt.catch_body:
            stmt.catch_body.accept(self)
            catch_b = self._result
        finally_b = None
        if stmt.finally_body:
            stmt.finally_body.accept(self)
            finally_b = self._result
        self._node(stmt, "TryStmt", try_body=try_b, catch_var=stmt.catch_var,
                   catch_body=catch_b, finally_body=finally_b)

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        stmt.expression.accept(self)
        self._node(stmt, "ExpressionStmt", expression=self._result)

    def visit_empty_stmt(self, stmt: EmptyStmt) -> None:
        self._node(stmt, "EmptyStmt")

    # ── Root ───────────────────────────────────────────────────

    def visit_program(self, program: Program) -> None:
        decls = self._serialize_list(program.declarations)
        self._node(program, "Program", declarations=decls)

    def visit_module(self, module: Module) -> None:
        imports = self._serialize_list(module.imports)
        decls = self._serialize_list(module.declarations)
        self._node(module, "Module", name=module.name, imports=imports,
                   declarations=decls)

    # ── Helpers ────────────────────────────────────────────────

    def visit_parameter(self, param: Parameter) -> None:
        type_ann = None
        if param.type_annotation:
            param.type_annotation.accept(self)
            type_ann = self._result
        default = None
        if param.default:
            param.default.accept(self)
            default = self._result
        self._node(param, "Parameter", name=param.name, type_annotation=type_ann,
                   default=default)

    def visit_struct_field(self, field: StructField) -> None:
        field.type_annotation.accept(self)
        type_ann = self._result
        default = None
        if field.default:
            field.default.accept(self)
            default = self._result
        self._node(field, "StructField", name=field.name, type_annotation=type_ann,
                   default=default)

    def visit_enum_variant(self, variant: EnumVariant) -> None:
        val = None
        if variant.value:
            variant.value.accept(self)
            val = self._result
        self._node(variant, "EnumVariant", name=variant.name, value=val)

    def visit_elif_branch(self, branch: ElifBranch) -> None:
        branch.condition.accept(self)
        cond = self._result
        branch.body.accept(self)
        self._node(branch, "ElifBranch", condition=cond, body=self._result)


# ══════════════════════════════════════════════════════════════════
# Deserializer — JSON → AST
# ══════════════════════════════════════════════════════════════════


class ASTDeserializer:
    """
    Deserializes a JSON dictionary back into AST nodes.

    Usage:
        deserializer = ASTDeserializer()
        program = deserializer.from_dict(data)
        program = deserializer.from_json(json_str)
    """

    def from_json(self, json_str: str) -> ASTNode:
        """Deserialize a JSON string into an AST node."""
        data = json.loads(json_str)
        return self.from_dict(data)

    def from_dict(self, data: Dict[str, Any]) -> ASTNode:
        """Deserialize a dictionary into an AST node."""
        kind = data["kind"]
        handler = getattr(self, f"_deserialize_{kind}", None)
        if handler is None:
            raise ValueError(f"Unknown node kind: {kind}")
        return handler(data)

    def _loc(self, data: Dict[str, Any]) -> SourceLocation:
        loc = data["location"]
        return SourceLocation(
            file=loc["file"],
            start_line=loc["start_line"],
            start_column=loc["start_column"],
            end_line=loc["end_line"],
            end_column=loc["end_column"],
            start_offset=loc.get("start_offset", 0),
            end_offset=loc.get("end_offset", 0),
        )

    def _node(self, data: Dict[str, Any], **overrides: Any) -> Dict[str, Any]:
        d = {"node_id": data["node_id"], "location": self._loc(data)}
        d.update(overrides)
        return d

    def _deserialize_list(self, items: List[Dict[str, Any]]) -> list:
        return [self.from_dict(item) for item in items]

    # ── Expressions ────────────────────────────────────────────

    def _deserialize_LiteralExpr(self, data: Dict[str, Any]) -> LiteralExpr:
        token_type = None
        if data.get("token_type"):
            from ..lexer.token import TokenType
            token_type = TokenType[data["token_type"]]
        return LiteralExpr(**self._node(data), value=data["value"], token_type=token_type)

    def _deserialize_IdentifierExpr(self, data: Dict[str, Any]) -> IdentifierExpr:
        return IdentifierExpr(**self._node(data), name=data["name"])

    def _deserialize_UnaryExpr(self, data: Dict[str, Any]) -> UnaryExpr:
        return UnaryExpr(**self._node(data), operator=data["operator"],
                        right=self.from_dict(data["right"]))

    def _deserialize_BinaryExpr(self, data: Dict[str, Any]) -> BinaryExpr:
        return BinaryExpr(**self._node(data), operator=data["operator"],
                         left=self.from_dict(data["left"]),
                         right=self.from_dict(data["right"]))

    def _deserialize_LogicalExpr(self, data: Dict[str, Any]) -> LogicalExpr:
        return LogicalExpr(**self._node(data), operator=data["operator"],
                          left=self.from_dict(data["left"]),
                          right=self.from_dict(data["right"]))

    def _deserialize_AssignmentExpr(self, data: Dict[str, Any]) -> AssignmentExpr:
        return AssignmentExpr(**self._node(data),
                             target=self.from_dict(data["target"]),
                             value=self.from_dict(data["value"]))

    def _deserialize_CompoundAssignmentExpr(self, data: Dict[str, Any]) -> CompoundAssignmentExpr:
        return CompoundAssignmentExpr(**self._node(data),
                                     target=self.from_dict(data["target"]),
                                     operator=data["operator"],
                                     value=self.from_dict(data["value"]))

    def _deserialize_CallExpr(self, data: Dict[str, Any]) -> CallExpr:
        return CallExpr(**self._node(data),
                       callee=self.from_dict(data["callee"]),
                       arguments=self._deserialize_list(data["arguments"]))

    def _deserialize_MethodCallExpr(self, data: Dict[str, Any]) -> MethodCallExpr:
        return MethodCallExpr(**self._node(data),
                             object=self.from_dict(data["object"]),
                             method=data["method"],
                             arguments=self._deserialize_list(data["arguments"]))

    def _deserialize_ConstructorExpr(self, data: Dict[str, Any]) -> ConstructorExpr:
        return ConstructorExpr(**self._node(data),
                              class_name=data["class_name"],
                              arguments=self._deserialize_list(data["arguments"]))

    def _deserialize_GetExpr(self, data: Dict[str, Any]) -> GetExpr:
        return GetExpr(**self._node(data),
                      object=self.from_dict(data["object"]),
                      property=data["property"])

    def _deserialize_SetExpr(self, data: Dict[str, Any]) -> SetExpr:
        return SetExpr(**self._node(data),
                      object=self.from_dict(data["object"]),
                      property=data["property"],
                      value=self.from_dict(data["value"]))

    def _deserialize_IndexExpr(self, data: Dict[str, Any]) -> IndexExpr:
        return IndexExpr(**self._node(data),
                        object=self.from_dict(data["object"]),
                        index=self.from_dict(data["index"]))

    def _deserialize_SliceExpr(self, data: Dict[str, Any]) -> SliceExpr:
        start = self.from_dict(data["start"]) if data.get("start") else None
        end = self.from_dict(data["end"]) if data.get("end") else None
        return SliceExpr(**self._node(data),
                        object=self.from_dict(data["object"]),
                        start=start, end=end)

    def _deserialize_SelfExpr(self, data: Dict[str, Any]) -> SelfExpr:
        return SelfExpr(**self._node(data))

    def _deserialize_SuperExpr(self, data: Dict[str, Any]) -> SuperExpr:
        return SuperExpr(**self._node(data), method=data["method"])

    def _deserialize_ListExpr(self, data: Dict[str, Any]) -> ListExpr:
        return ListExpr(**self._node(data),
                       elements=self._deserialize_list(data["elements"]))

    def _deserialize_DictExpr(self, data: Dict[str, Any]) -> DictExpr:
        return DictExpr(**self._node(data),
                       keys=self._deserialize_list(data["keys"]),
                       values=self._deserialize_list(data["values"]))

    def _deserialize_TupleExpr(self, data: Dict[str, Any]) -> TupleExpr:
        return TupleExpr(**self._node(data),
                        elements=self._deserialize_list(data["elements"]))

    def _deserialize_LambdaExpr(self, data: Dict[str, Any]) -> LambdaExpr:
        return LambdaExpr(**self._node(data),
                         parameters=self._deserialize_list(data["parameters"]),
                         body=self.from_dict(data["body"]))

    def _deserialize_IfExpr(self, data: Dict[str, Any]) -> IfExpr:
        else_b = self.from_dict(data["else_branch"]) if data.get("else_branch") else None
        return IfExpr(**self._node(data),
                     condition=self.from_dict(data["condition"]),
                     then_branch=self.from_dict(data["then_branch"]),
                     else_branch=else_b)

    def _deserialize_GroupingExpr(self, data: Dict[str, Any]) -> GroupingExpr:
        return GroupingExpr(**self._node(data),
                           expression=self.from_dict(data["expression"]))

    def _deserialize_PlaceholderExpr(self, data: Dict[str, Any]) -> PlaceholderExpr:
        return PlaceholderExpr(**self._node(data),
                              description=data.get("description", ""))

    # ── Types ──────────────────────────────────────────────────

    def _deserialize_NamedType(self, data: Dict[str, Any]) -> NamedType:
        return NamedType(**self._node(data), name=data["name"])

    def _deserialize_GenericType(self, data: Dict[str, Any]) -> GenericType:
        return GenericType(**self._node(data), name=data["name"],
                          type_args=self._deserialize_list(data["type_args"]))

    def _deserialize_FunctionType(self, data: Dict[str, Any]) -> FunctionType:
        return FunctionType(**self._node(data),
                           params=self._deserialize_list(data["params"]),
                           return_type=self.from_dict(data["return_type"]))

    def _deserialize_OptionalType(self, data: Dict[str, Any]) -> OptionalType:
        return OptionalType(**self._node(data),
                           inner=self.from_dict(data["inner"]))

    def _deserialize_TupleType(self, data: Dict[str, Any]) -> TupleType:
        return TupleType(**self._node(data),
                        elements=self._deserialize_list(data["elements"]))

    # ── Declarations ───────────────────────────────────────────

    def _deserialize_VarDecl(self, data: Dict[str, Any]) -> VarDecl:
        type_ann = self.from_dict(data["type_annotation"]) if data.get("type_annotation") else None
        init = self.from_dict(data["initializer"]) if data.get("initializer") else None
        return VarDecl(**self._node(data), name=data["name"],
                      type_annotation=type_ann, initializer=init,
                      is_const=data.get("is_const", False))

    def _deserialize_FunctionDecl(self, data: Dict[str, Any]) -> FunctionDecl:
        ret = self.from_dict(data["return_type"]) if data.get("return_type") else None
        return FunctionDecl(**self._node(data), name=data["name"],
                           parameters=self._deserialize_list(data["parameters"]),
                           return_type=ret,
                           body=self.from_dict(data["body"]))

    def _deserialize_MethodDecl(self, data: Dict[str, Any]) -> MethodDecl:
        ret = self.from_dict(data["return_type"]) if data.get("return_type") else None
        return MethodDecl(**self._node(data), name=data["name"],
                         parameters=self._deserialize_list(data["parameters"]),
                         return_type=ret,
                         body=self.from_dict(data["body"]),
                         is_static=data.get("is_static", False))

    def _deserialize_StructDecl(self, data: Dict[str, Any]) -> StructDecl:
        return StructDecl(**self._node(data), name=data["name"],
                         fields=self._deserialize_list(data["fields"]),
                         methods=self._deserialize_list(data["methods"]))

    def _deserialize_EnumDecl(self, data: Dict[str, Any]) -> EnumDecl:
        return EnumDecl(**self._node(data), name=data["name"],
                       variants=self._deserialize_list(data["variants"]))

    def _deserialize_ClassDecl(self, data: Dict[str, Any]) -> ClassDecl:
        return ClassDecl(**self._node(data), name=data["name"],
                        parent=data.get("parent"),
                        members=self._deserialize_list(data["members"]))

    def _deserialize_TraitDecl(self, data: Dict[str, Any]) -> TraitDecl:
        return TraitDecl(**self._node(data), name=data["name"],
                        members=self._deserialize_list(data["members"]))

    def _deserialize_InterfaceDecl(self, data: Dict[str, Any]) -> InterfaceDecl:
        return InterfaceDecl(**self._node(data), name=data["name"],
                            members=self._deserialize_list(data["members"]))

    def _deserialize_ImportDecl(self, data: Dict[str, Any]) -> ImportDecl:
        return ImportDecl(**self._node(data), path=data["path"], alias=data.get("alias"))

    def _deserialize_ExportDecl(self, data: Dict[str, Any]) -> ExportDecl:
        return ExportDecl(**self._node(data), name=data["name"])

    # ── Statements ─────────────────────────────────────────────

    def _deserialize_BlockStmt(self, data: Dict[str, Any]) -> BlockStmt:
        return BlockStmt(**self._node(data),
                        statements=self._deserialize_list(data["statements"]))

    def _deserialize_IfStmt(self, data: Dict[str, Any]) -> IfStmt:
        else_b = self.from_dict(data["else_branch"]) if data.get("else_branch") else None
        return IfStmt(**self._node(data),
                     condition=self.from_dict(data["condition"]),
                     then_branch=self.from_dict(data["then_branch"]),
                     elif_branches=self._deserialize_list(data["elif_branches"]),
                     else_branch=else_b)

    def _deserialize_WhileStmt(self, data: Dict[str, Any]) -> WhileStmt:
        return WhileStmt(**self._node(data),
                        condition=self.from_dict(data["condition"]),
                        body=self.from_dict(data["body"]))

    def _deserialize_UntilStmt(self, data: Dict[str, Any]) -> UntilStmt:
        return UntilStmt(**self._node(data),
                        condition=self.from_dict(data["condition"]),
                        body=self.from_dict(data["body"]))

    def _deserialize_ForStmt(self, data: Dict[str, Any]) -> ForStmt:
        step = self.from_dict(data["step"]) if data.get("step") else None
        return ForStmt(**self._node(data), variable=data["variable"],
                      start=self.from_dict(data["start"]),
                      end=self.from_dict(data["end"]),
                      step=step,
                      body=self.from_dict(data["body"]))

    def _deserialize_ForEachStmt(self, data: Dict[str, Any]) -> ForEachStmt:
        return ForEachStmt(**self._node(data), element=data["element"],
                          iterable=self.from_dict(data["iterable"]),
                          body=self.from_dict(data["body"]))

    def _deserialize_ReturnStmt(self, data: Dict[str, Any]) -> ReturnStmt:
        val = self.from_dict(data["value"]) if data.get("value") else None
        return ReturnStmt(**self._node(data), value=val)

    def _deserialize_BreakStmt(self, data: Dict[str, Any]) -> BreakStmt:
        return BreakStmt(**self._node(data))

    def _deserialize_ContinueStmt(self, data: Dict[str, Any]) -> ContinueStmt:
        return ContinueStmt(**self._node(data))

    def _deserialize_ThrowStmt(self, data: Dict[str, Any]) -> ThrowStmt:
        return ThrowStmt(**self._node(data),
                        value=self.from_dict(data["value"]))

    def _deserialize_TryStmt(self, data: Dict[str, Any]) -> TryStmt:
        catch_b = self.from_dict(data["catch_body"]) if data.get("catch_body") else None
        finally_b = self.from_dict(data["finally_body"]) if data.get("finally_body") else None
        return TryStmt(**self._node(data),
                      try_body=self.from_dict(data["try_body"]),
                      catch_var=data.get("catch_var"),
                      catch_body=catch_b,
                      finally_body=finally_b)

    def _deserialize_ExpressionStmt(self, data: Dict[str, Any]) -> ExpressionStmt:
        return ExpressionStmt(**self._node(data),
                             expression=self.from_dict(data["expression"]))

    def _deserialize_EmptyStmt(self, data: Dict[str, Any]) -> EmptyStmt:
        return EmptyStmt(**self._node(data))

    # ── Root ───────────────────────────────────────────────────

    def _deserialize_Program(self, data: Dict[str, Any]) -> Program:
        return Program(**self._node(data),
                      declarations=self._deserialize_list(data["declarations"]))

    def _deserialize_Module(self, data: Dict[str, Any]) -> Module:
        return Module(**self._node(data), name=data["name"],
                     imports=self._deserialize_list(data.get("imports", [])),
                     declarations=self._deserialize_list(data["declarations"]))

    # ── Helpers ────────────────────────────────────────────────

    def _deserialize_Parameter(self, data: Dict[str, Any]) -> Parameter:
        type_ann = self.from_dict(data["type_annotation"]) if data.get("type_annotation") else None
        default = self.from_dict(data["default"]) if data.get("default") else None
        return Parameter(**self._node(data), name=data["name"],
                        type_annotation=type_ann, default=default)

    def _deserialize_StructField(self, data: Dict[str, Any]) -> StructField:
        default = self.from_dict(data["default"]) if data.get("default") else None
        return StructField(**self._node(data), name=data["name"],
                          type_annotation=self.from_dict(data["type_annotation"]),
                          default=default)

    def _deserialize_EnumVariant(self, data: Dict[str, Any]) -> EnumVariant:
        val = self.from_dict(data["value"]) if data.get("value") else None
        return EnumVariant(**self._node(data), name=data["name"], value=val)

    def _deserialize_ElifBranch(self, data: Dict[str, Any]) -> ElifBranch:
        return ElifBranch(**self._node(data),
                         condition=self.from_dict(data["condition"]),
                         body=self.from_dict(data["body"]))


# ══════════════════════════════════════════════════════════════════
# Binary Serialization — compact binary format
# ══════════════════════════════════════════════════════════════════

AST_SERIAL_VERSION = 1


class ASTBinarySerializer:
    """
    Serializes/deserializes AST trees to/from a compact binary format.
    Uses JSON + zlib compression for compactness and speed.

    Usage:
        serializer = ASTBinarySerializer()
        data = serializer.to_bytes(program)
        program = serializer.from_bytes(data)
    """

    def __init__(self) -> None:
        self._json_serializer = ASTSerializer()
        self._json_deserializer = ASTDeserializer()

    def to_bytes(self, node: ASTNode) -> bytes:
        """Serialize an AST node to compressed bytes."""
        import zlib
        json_str = self._json_serializer.to_json(node)
        payload = json_str.encode("utf-8")
        compressed = zlib.compress(payload, level=6)
        header = f"I-AST-v{AST_SERIAL_VERSION}\n".encode("ascii")
        return header + compressed

    def from_bytes(self, data: bytes) -> ASTNode:
        """Deserialize compressed bytes back to an AST node."""
        import zlib
        lines = data.split(b"\n", 1)
        header = lines[0].decode("ascii")
        if not header.startswith("I-AST-v"):
            raise ValueError(f"Invalid AST binary format header: {header}")
        version_str = header[len("I-AST-v"):]
        version = int(version_str)
        if version != AST_SERIAL_VERSION:
            raise ValueError(
                f"Unsupported AST version: {version} (expected {AST_SERIAL_VERSION})"
            )
        compressed = lines[1]
        payload = zlib.decompress(compressed)
        json_str = payload.decode("utf-8")
        return self._json_deserializer.from_json(json_str)

    def to_file(self, node: ASTNode, path: str) -> None:
        """Serialize an AST to a binary file."""
        with open(path, "wb") as f:
            f.write(self.to_bytes(node))

    def from_file(self, path: str) -> ASTNode:
        """Deserialize an AST from a binary file."""
        with open(path, "rb") as f:
            return self.from_bytes(f.read())


# ══════════════════════════════════════════════════════════════════
# Versioned Serialization — JSON with version metadata
# ══════════════════════════════════════════════════════════════════


class ASTVersionedSerializer:
    """
    Serializes/deserializes AST trees with version metadata.
    Wraps the standard JSON serialization with a version envelope.

    Usage:
        serializer = ASTVersionedSerializer()
        json_str = serializer.to_json(program)
        program = serializer.from_json(json_str)
    """

    FORMAT_VERSION = "1.0"

    def __init__(self) -> None:
        self._serializer = ASTSerializer()
        self._deserializer = ASTDeserializer()

    def to_dict(self, node: ASTNode) -> Dict[str, Any]:
        """Serialize to a versioned dictionary."""
        ast_data = self._serializer.to_dict(node)
        return {
            "format_version": self.FORMAT_VERSION,
            "ast_version": AST_SERIAL_VERSION,
            "ast": ast_data,
        }

    def to_json(self, node: ASTNode, indent: int = 2) -> str:
        """Serialize to versioned JSON."""
        return json.dumps(self.to_dict(node), indent=indent, ensure_ascii=False)

    def from_dict(self, data: Dict[str, Any]) -> ASTNode:
        """Deserialize from a versioned dictionary."""
        version = data.get("ast_version", AST_SERIAL_VERSION)
        if version != AST_SERIAL_VERSION:
            raise ValueError(
                f"Unsupported AST version: {version} (expected {AST_SERIAL_VERSION})"
            )
        return self._deserializer.from_dict(data["ast"])

    def from_json(self, json_str: str) -> ASTNode:
        """Deserialize from versioned JSON."""
        data = json.loads(json_str)
        return self.from_dict(data)
