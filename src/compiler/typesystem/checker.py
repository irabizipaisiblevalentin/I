"""
Type Checker Engine for the I Programming Language

The main type checking engine that walks the AST and validates
all types. Integrates all type system components:
- Type Registry
- Type Database
- Type Environment
- Type Context
- Inference Engine
- Constraint Solver
- Generic Engine
- Trait Resolver
- Compile-Time Evaluator
- Diagnostics Engine

This is the authoritative implementation of all static typing rules.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from ..ast.nodes import (
    ASTVisitor, ASTNode, Expr, Stmt, Decl, TypeNode,
    LiteralExpr, IdentifierExpr, UnaryExpr, BinaryExpr, LogicalExpr,
    AssignmentExpr, CompoundAssignmentExpr, CallExpr, ConstructorExpr,
    GetExpr, SetExpr, IndexExpr, SliceExpr, SelfExpr, SuperExpr,
    ListExpr, DictExpr, TupleExpr, LambdaExpr, IfExpr, GroupingExpr,
    PlaceholderExpr, MethodCallExpr,
    NamedType, GenericType as ASTGenericType, FunctionType as ASTFunctionType,
    OptionalType as ASTOptionalType, TupleType as ASTTupleType,
    VarDecl, FunctionDecl, StructDecl, EnumDecl, ClassDecl,
    TraitDecl, InterfaceDecl, ImportDecl, ExportDecl, MethodDecl,
    Parameter, StructField, EnumVariant, ElifBranch,
    BlockStmt, IfStmt, WhileStmt, UntilStmt, ForStmt, ForEachStmt,
    ReturnStmt, BreakStmt, ContinueStmt, ThrowStmt, TryStmt,
    ExpressionStmt, EmptyStmt, Program,
    SourceLocation as ASTSourceLocation,
)
from ..ast.nodes import NodeType
from .types import (
    Type, TypeKind, TypeVariable, FunctionType, OptionalType,
    ListType, MapType, SetType, TupleType, RangeType, GenericType,
    ClassType, StructType, EnumType, TraitType, InterfaceType,
    NamedType as TNamedType, ModuleType,
    TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_CHAR, TYPE_STRING,
    TYPE_NONE, TYPE_ANY, TYPE_UNKNOWN, TYPE_NEVER,
    common_type, make_list, make_map, make_function, make_optional,
)
from .registry import TypeRegistry, TypeDefinition, MemberInfo, MethodSignature
from .database import TypeDatabase
from .environment import TypeEnvironment
from .context import TypeContext
from .inference import InferenceEngine
from .constraints import ConstraintSolver
from .generics import GenericEngine, GenericParamDef
from .traits import TraitResolver, TraitDefinition, InterfaceDefinition
from .compiletime import CompileTimeEvaluator, ConstValue
from .diagnostics import (
    TypeDiagnostics, TypeErrorCode, TypeSeverity, TypeLocation,
)


# ══════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════


def _loc(node: Any, file: str = "<input>") -> TypeLocation:
    """Extract TypeLocation from an AST node."""
    if hasattr(node, 'location'):
        loc = node.location
        return TypeLocation(
            file=getattr(loc, 'file', file),
            line=getattr(loc, 'start_line', 0),
            column=getattr(loc, 'start_column', 0),
            end_line=getattr(loc, 'end_line', 0),
            end_column=getattr(loc, 'end_column', 0),
        )
    return TypeLocation(file=file)


def _name_of(node: Any) -> str:
    """Extract name from AST node or token."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if hasattr(node, 'name'):
        n = node.name
        return _name_of(n) if not isinstance(n, str) else n
    if hasattr(node, 'lexeme'):
        return node.lexeme
    return str(node)


def _type_name_of(type_node: Any) -> str:
    """Extract type name from a TypeNode."""
    if type_node is None:
        return ""
    if isinstance(type_node, str):
        return type_node
    if isinstance(type_node, NamedType):
        return type_node.name
    if hasattr(type_node, 'lexeme'):
        return type_node.lexeme
    if hasattr(type_node, 'name'):
        return _type_name_of(type_node.name)
    return str(type_node)


# ══════════════════════════════════════════════════════════════════
# Type Checker Engine
# ══════════════════════════════════════════════════════════════════


class TypeChecker(ASTVisitor):
    """
    The main type checker for the I programming language.

    Walks the AST and validates all type relationships, performing:
    - Type inference for untyped declarations
    - Type compatibility checking
    - Generic instantiation and validation
    - Trait/interface implementation verification
    - Compile-time constant evaluation
    - Control flow type analysis
    """

    def __init__(
        self,
        registry: Optional[TypeRegistry] = None,
        database: Optional[TypeDatabase] = None,
    ) -> None:
        self.registry = registry or TypeRegistry()
        self.database = database or TypeDatabase()
        self.diagnostics = TypeDiagnostics()
        self.ctx = TypeContext(self.registry, self.database)
        self.inference = InferenceEngine(self.ctx, self.diagnostics)
        self.generics = GenericEngine(self.registry)
        self.trait_resolver = TraitResolver(self.registry, self.diagnostics)
        self.compile_time = CompileTimeEvaluator(self.diagnostics)

        self._return_type_stack: List[Optional[Type]] = []
        self._checked_nodes: set = set()

    # ── Public API ────────────────────────────────────────────────

    def check(self, program: Program) -> TypeDiagnostics:
        """
        Type-check a Program AST node.
        Returns the diagnostics collection.
        """
        self.ctx.clear()
        self.diagnostics.clear()
        self.inference.reset()
        self._checked_nodes.clear()

        program.accept(self)

        self.ctx.process_deferred()
        self._check_trait_implementations()

        return self.diagnostics

    @property
    def has_errors(self) -> bool:
        return self.diagnostics.has_errors

    # ── Program ───────────────────────────────────────────────────

    def visit_program(self, program: Program) -> Type:
        for decl in program.declarations:
            if self.ctx.should_abort:
                break
            decl.accept(self)
        return TYPE_NONE

    # ── Declaration Visitors ──────────────────────────────────────

    def visit_var_decl(self, decl: VarDecl) -> Type:
        loc = _loc(decl, self.ctx.current_file)
        name = _name_of(decl)

        # Type annotation
        ann_type: Optional[Type] = None
        if decl.type_annotation:
            ann_type = self._resolve_type_node(decl.type_annotation)

        # Initializer type
        init_type: Optional[Type] = None
        if decl.initializer:
            init_type = self._check_expr(decl.initializer)

        # Determine final type
        final_type = self.inference.infer_assignment(
            name,
            init_type or TYPE_UNKNOWN,
            ann_type,
            decl.is_const,
            loc,
        )

        # Check type compatibility between annotation and initializer
        if ann_type and init_type and init_type.kind != TypeKind.UNKNOWN:
            if not init_type.is_assignable_to(ann_type):
                self.diagnostics.error(
                    TypeErrorCode.TYP101_ASSIGNMENT_TYPE_MISMATCH,
                    loc,
                    str(ann_type), str(init_type),
                    expected_type=ann_type,
                    actual_type=init_type,
                )

        # Const check
        if decl.is_const and init_type:
            self.ctx.environment.define(
                name, final_type,
                is_mutable=False,
                is_const=True,
                file=self.ctx.current_file,
                line=loc.line,
            )
        else:
            self.ctx.environment.define(
                name, final_type,
                file=self.ctx.current_file,
                line=loc.line,
            )

        return final_type

    def visit_function_decl(self, decl: FunctionDecl) -> Type:
        loc = _loc(decl, self.ctx.current_file)
        name = _name_of(decl)

        # Resolve return type
        ret_type: Type = TYPE_NONE
        if decl.return_type:
            ret_type = self._resolve_type_node(decl.return_type)

        # Resolve parameter types
        param_types: List[Type] = []
        param_names: List[str] = []
        for param in decl.parameters:
            pt: Type = TYPE_ANY
            if param.type_annotation:
                pt = self._resolve_type_node(param.type_annotation)
            param_types.append(pt)
            param_names.append(_name_of(param))

        # Create function type
        func_type = FunctionType(tuple(param_types), ret_type)

        # Register in environment
        self.ctx.environment.define(
            name, func_type,
            is_mutable=False,
            file=self.ctx.current_file,
            line=loc.line,
        )

        # Enter function context
        self.ctx.enter_function(
            name, ret_type, param_types, param_names,
        )
        self._return_type_stack.append(ret_type)

        # Define parameters in child scope
        for param in decl.parameters:
            p_name = _name_of(param)
            pt = TYPE_ANY
            if param.type_annotation:
                pt = self._resolve_type_node(param.type_annotation)
            self.ctx.environment.define(p_name, pt, file=self.ctx.current_file)

        # Check body
        body_type = self._check_block(decl.body)

        # Infer return type if not annotated
        if not decl.return_type or (decl.return_type and _type_name_of(decl.return_type) == 'ubusa'):
            inferred_ret = self.inference.infer_function_return(
                ret_type, body_type, loc,
            )
            if inferred_ret.kind == TypeKind.UNKNOWN:
                inferred_ret = TYPE_NONE

        self._return_type_stack.pop()
        self.ctx.exit_function()

        return func_type

    def visit_method_decl(self, decl: MethodDecl) -> Type:
        loc = _loc(decl, self.ctx.current_file)
        name = _name_of(decl)
        class_ctx = self.ctx.current_class
        class_name = class_ctx.name if class_ctx else "<unknown>"

        # Resolve return type
        ret_type: Type = TYPE_NONE
        if decl.return_type:
            ret_type = self._resolve_type_node(decl.return_type)

        # Resolve parameter types
        param_types: List[Type] = []
        param_names: List[str] = []
        for param in decl.parameters:
            pt: Type = TYPE_ANY
            if param.type_annotation:
                pt = self._resolve_type_node(param.type_annotation)
            param_types.append(pt)
            param_names.append(_name_of(param))

        # Register method in registry
        sig = MethodSignature(
            name=name,
            param_types=param_types,
            param_names=param_names,
            return_type=ret_type,
            is_static=decl.is_static,
            declaration_file=self.ctx.current_file,
            declaration_line=loc.line,
        )

        defn = self.registry.get(class_name)
        if defn:
            defn.methods[name] = sig

        # Enter method context
        method_type = FunctionType(tuple(param_types), ret_type)
        self.ctx.enter_function(
            f"{class_name}.{name}", ret_type, param_types, param_names,
        )
        self._return_type_stack.append(ret_type)

        # Define parameters
        for param in decl.parameters:
            p_name = _name_of(param)
            pt = TYPE_ANY
            if param.type_annotation:
                pt = self._resolve_type_node(param.type_annotation)
            self.ctx.environment.define(p_name, pt, file=self.ctx.current_file)

        # Define self
        if not decl.is_static:
            class_type = ClassType(class_name)
            self.ctx.environment.define("self", class_type, is_const=True)

        # Check body
        self._check_block(decl.body)

        self._return_type_stack.pop()
        self.ctx.exit_function()

        return method_type

    def visit_struct_decl(self, decl: StructDecl) -> Type:
        loc = _loc(decl, self.ctx.current_file)
        name = _name_of(decl)

        struct_type = StructType(name)
        defn = TypeDefinition(
            name=name,
            kind=TypeKind.STRUCT,
            type_obj=struct_type,
            declaration_file=self.ctx.current_file,
            declaration_line=loc.line,
        )

        # Check fields
        for field in decl.fields:
            fname = _name_of(field)
            floc = _loc(field, self.ctx.current_file)
            ft = TYPE_ANY
            if field.type_annotation:
                ft = self._resolve_type_node(field.type_annotation)
            defn.members[fname] = MemberInfo(
                name=fname, type=ft,
                declaration_file=self.ctx.current_file,
                declaration_line=floc.line,
            )
            if field.default:
                self._check_expr(field.default)

        self.registry.register(defn, self.ctx.current_file)

        # Enter class context for methods
        self.ctx.enter_class(name)
        for method in decl.methods:
            method.accept(self)
        self.ctx.exit_class()

        return struct_type

    def visit_enum_decl(self, decl: EnumDecl) -> Type:
        loc = _loc(decl, self.ctx.current_file)
        name = _name_of(decl)

        enum_type = EnumType(name)
        defn = TypeDefinition(
            name=name,
            kind=TypeKind.ENUM,
            type_obj=enum_type,
            declaration_file=self.ctx.current_file,
            declaration_line=loc.line,
        )

        for variant in decl.variants:
            v_name = _name_of(variant)
            defn.members[v_name] = MemberInfo(
                name=v_name, type=enum_type, is_const=True,
                declaration_file=self.ctx.current_file,
            )

        self.registry.register(defn, self.ctx.current_file)
        return enum_type

    def visit_class_decl(self, decl: ClassDecl) -> Type:
        loc = _loc(decl, self.ctx.current_file)
        name = _name_of(decl)

        parent_name = decl.parent
        class_type = ClassType(name, parent_name)

        defn = TypeDefinition(
            name=name,
            kind=TypeKind.CLASS,
            type_obj=class_type,
            parent_name=parent_name,
            declaration_file=self.ctx.current_file,
            declaration_line=loc.line,
        )

        # Check inheritance compatibility
        if parent_name:
            parent_defn = self.registry.get(parent_name)
            if parent_defn and parent_defn.is_sealed:
                self.diagnostics.error(
                    TypeErrorCode.TYP404_INCOMPATIBLE_INHERITANCE,
                    loc, name, parent_name,
                )
            if parent_name == name:
                self.diagnostics.error(
                    TypeErrorCode.TYP304_CYCLIC_GENERIC,
                    loc, name,
                )

        self.registry.register(defn, self.ctx.current_file)

        # Enter class context
        self.ctx.enter_class(name, parent_name)

        # Define self
        self.ctx.environment.define("self", class_type, is_const=True)

        # Check members
        for member in decl.members:
            member.accept(self)

        self.ctx.exit_class()

        return class_type

    def visit_trait_decl(self, decl: TraitDecl) -> Type:
        loc = _loc(decl, self.ctx.current_file)
        name = _name_of(decl)

        trait_type = TraitType(name)
        defn = TypeDefinition(
            name=name,
            kind=TypeKind.TRAIT,
            type_obj=trait_type,
            declaration_file=self.ctx.current_file,
            declaration_line=loc.line,
        )

        self.registry.register(defn, self.ctx.current_file)

        trait_def = TraitDefinition(
            name=name,
            declaration_file=self.ctx.current_file,
            declaration_line=loc.line,
        )

        # Enter class context for members
        self.ctx.enter_class(name)
        for member in decl.members:
            if isinstance(member, MethodDecl):
                m_name = _name_of(member)
                ret_type = TYPE_NONE
                if member.return_type:
                    ret_type = self._resolve_type_node(member.return_type)
                param_types = []
                for p in member.parameters:
                    pt = TYPE_ANY
                    if p.type_annotation:
                        pt = self._resolve_type_node(p.type_annotation)
                    param_types.append(pt)

                sig = MethodSignature(
                    name=m_name,
                    param_types=param_types,
                    return_type=ret_type,
                    declaration_file=self.ctx.current_file,
                )
                trait_def.required_methods[m_name] = sig
                defn.methods[m_name] = sig

            member.accept(self)

        self.ctx.exit_class()

        self.trait_resolver.register_trait(trait_def)
        return trait_type

    def visit_interface_decl(self, decl: InterfaceDecl) -> Type:
        loc = _loc(decl, self.ctx.current_file)
        name = _name_of(decl)

        iface_type = InterfaceType(name)
        defn = TypeDefinition(
            name=name,
            kind=TypeKind.INTERFACE,
            type_obj=iface_type,
            declaration_file=self.ctx.current_file,
            declaration_line=loc.line,
        )

        self.registry.register(defn, self.ctx.current_file)

        iface_def = InterfaceDefinition(
            name=name,
            declaration_file=self.ctx.current_file,
            declaration_line=loc.line,
        )

        self.ctx.enter_class(name)
        for member in decl.members:
            if isinstance(member, MethodDecl):
                m_name = _name_of(member)
                ret_type = TYPE_NONE
                if member.return_type:
                    ret_type = self._resolve_type_node(member.return_type)
                param_types = []
                for p in member.parameters:
                    pt = TYPE_ANY
                    if p.type_annotation:
                        pt = self._resolve_type_node(p.type_annotation)
                    param_types.append(pt)

                sig = MethodSignature(
                    name=m_name,
                    param_types=param_types,
                    return_type=ret_type,
                    declaration_file=self.ctx.current_file,
                )
                iface_def.required_methods[m_name] = sig

            member.accept(self)

        self.ctx.exit_class()

        self.trait_resolver.register_interface(iface_def)
        return iface_type

    def visit_import_decl(self, decl: ImportDecl) -> Type:
        return TYPE_NONE

    def visit_export_decl(self, decl: ExportDecl) -> Type:
        return TYPE_NONE

    # ── Statement Visitors ────────────────────────────────────────

    def visit_block_stmt(self, stmt: BlockStmt) -> Type:
        return self._check_block(stmt)

    def _check_block(self, block: BlockStmt) -> Type:
        self.ctx.environment.push("<block>")
        last_type: Type = TYPE_NONE
        for s in block.statements:
            if self.ctx.should_abort:
                break
            last_type = s.accept(self)
        self.ctx.environment.pop()
        return last_type

    def visit_if_stmt(self, stmt: IfStmt) -> Type:
        cond_type = self._check_expr(stmt.condition)
        if cond_type.kind not in (TypeKind.BOOL, TypeKind.ANY, TypeKind.UNKNOWN):
            self.diagnostics.warning(
                TypeErrorCode.TYP100_TYPE_MISMATCH,
                _loc(stmt.condition, self.ctx.current_file),
                "bool", str(cond_type),
                expected_type=TYPE_BOOL, actual_type=cond_type,
            )

        then_type = self._check_block(stmt.then_branch)

        elif_types: List[Type] = []
        for elif_b in stmt.elif_branches:
            self._check_expr(elif_b.condition)
            elif_types.append(self._check_block(elif_b.body))

        else_type: Optional[Type] = None
        if stmt.else_branch:
            else_type = self._check_block(stmt.else_branch)

        # Return the common type
        if else_type:
            common = common_type(then_type, else_type)
            return common or then_type
        return OptionalType(then_type)

    def visit_while_stmt(self, stmt: WhileStmt) -> Type:
        cond_type = self._check_expr(stmt.condition)
        if cond_type.kind not in (TypeKind.BOOL, TypeKind.ANY, TypeKind.UNKNOWN):
            self.diagnostics.warning(
                TypeErrorCode.TYP100_TYPE_MISMATCH,
                _loc(stmt.condition, self.ctx.current_file),
                "bool", str(cond_type),
            )

        self.ctx.enter_loop("while")
        self._check_block(stmt.body)
        self.ctx.exit_loop()
        return TYPE_NONE

    def visit_until_stmt(self, stmt: UntilStmt) -> Type:
        self._check_expr(stmt.condition)
        self.ctx.enter_loop("until")
        self._check_block(stmt.body)
        self.ctx.exit_loop()
        return TYPE_NONE

    def visit_for_stmt(self, stmt: ForStmt) -> Type:
        self._check_expr(stmt.start)
        self._check_expr(stmt.end)
        if stmt.step:
            self._check_expr(stmt.step)

        self.ctx.enter_loop("for")
        self.ctx.environment.push("<for>")
        var_name = stmt.variable
        self.ctx.environment.define(var_name, TYPE_INT, file=self.ctx.current_file)
        self._check_block(stmt.body)
        self.ctx.environment.pop()
        self.ctx.exit_loop()
        return TYPE_NONE

    def visit_for_each_stmt(self, stmt: ForEachStmt) -> Type:
        iterable_type = self._check_expr(stmt.iterable)

        elem_type: Type = TYPE_ANY
        if iterable_type.kind == TypeKind.LIST:
            elem_type = iterable_type.element_type
        elif iterable_type.kind == TypeKind.MAP:
            elem_type = iterable_type.key_type

        self.ctx.enter_loop("foreach")
        self.ctx.environment.push("<foreach>")
        self.ctx.environment.define(stmt.element, elem_type, file=self.ctx.current_file)
        self._check_block(stmt.body)
        self.ctx.environment.pop()
        self.ctx.exit_loop()
        return TYPE_NONE

    def visit_return_stmt(self, stmt: ReturnStmt) -> Type:
        if not self.ctx.in_function:
            loc = _loc(stmt, self.ctx.current_file)
            self.diagnostics.error(
                TypeErrorCode.TYP250_UNDEFINED_VARIABLE,
                loc,
                "return",
            )
            return TYPE_NEVER

        value_type: Type = TYPE_NONE
        if stmt.value:
            value_type = self._check_expr(stmt.value)

        expected = self.ctx.current_return_type
        if expected and expected.kind != TypeKind.NONE_TYPE:
            if not value_type.is_assignable_to(expected):
                loc = _loc(stmt, self.ctx.current_file)
                self.diagnostics.error(
                    TypeErrorCode.TYP102_RETURN_TYPE_MISMATCH,
                    loc,
                    str(expected), str(value_type),
                    expected_type=expected,
                    actual_type=value_type,
                )

        return value_type

    def visit_break_stmt(self, stmt: BreakStmt) -> Type:
        if not self.ctx.in_loop:
            loc = _loc(stmt, self.ctx.current_file)
            self.diagnostics.error(
                TypeErrorCode.TYP250_UNDEFINED_VARIABLE,
                loc,
                "break",
            )
        return TYPE_NEVER

    def visit_continue_stmt(self, stmt: ContinueStmt) -> Type:
        if not self.ctx.in_loop:
            loc = _loc(stmt, self.ctx.current_file)
            self.diagnostics.error(
                TypeErrorCode.TYP250_UNDEFINED_VARIABLE,
                loc,
                "continue",
            )
        return TYPE_NEVER

    def visit_throw_stmt(self, stmt: ThrowStmt) -> Type:
        self._check_expr(stmt.value)
        return TYPE_NEVER

    def visit_try_stmt(self, stmt: TryStmt) -> Type:
        self._check_block(stmt.try_body)
        if stmt.catch_body:
            self.ctx.environment.push("<catch>")
            if stmt.catch_var:
                self.ctx.environment.define(
                    stmt.catch_var, TYPE_ANY,
                    file=self.ctx.current_file,
                )
            self._check_block(stmt.catch_body)
            self.ctx.environment.pop()
        if stmt.finally_body:
            self._check_block(stmt.finally_body)
        return TYPE_NONE

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> Type:
        return self._check_expr(stmt.expression)

    def visit_empty_stmt(self, stmt: EmptyStmt) -> Type:
        return TYPE_NONE

    # ── Expression Visitors ───────────────────────────────────────

    def visit_literal_expr(self, expr: LiteralExpr) -> Type:
        return self.inference.infer_literal(expr.value)

    def visit_identifier_expr(self, expr: IdentifierExpr) -> Type:
        loc = _loc(expr, self.ctx.current_file)
        return self.inference.infer_identifier(expr.name, loc)

    def visit_unary_expr(self, expr: UnaryExpr) -> Type:
        operand_type = self._check_expr(expr.right)
        loc = _loc(expr, self.ctx.current_file)
        op = expr.operator if isinstance(expr.operator, str) else getattr(expr.operator, 'lexeme', str(expr.operator))
        return self.inference.infer_unary(op, operand_type, loc)

    def visit_binary_expr(self, expr: BinaryExpr) -> Type:
        left_type = self._check_expr(expr.left)
        right_type = self._check_expr(expr.right)
        loc = _loc(expr, self.ctx.current_file)
        op = expr.operator if isinstance(expr.operator, str) else getattr(expr.operator, 'lexeme', str(expr.operator))
        return self.inference.infer_binary(left_type, op, right_type, loc)

    def visit_logical_expr(self, expr: LogicalExpr) -> Type:
        left_type = self._check_expr(expr.left)
        right_type = self._check_expr(expr.right)
        loc = _loc(expr, self.ctx.current_file)

        if left_type.kind not in (TypeKind.BOOL, TypeKind.ANY, TypeKind.UNKNOWN):
            self.diagnostics.warning(
                TypeErrorCode.TYP100_TYPE_MISMATCH,
                _loc(expr.left, self.ctx.current_file),
                "bool", str(left_type),
            )
        if right_type.kind not in (TypeKind.BOOL, TypeKind.ANY, TypeKind.UNKNOWN):
            self.diagnostics.warning(
                TypeErrorCode.TYP100_TYPE_MISMATCH,
                _loc(expr.right, self.ctx.current_file),
                "bool", str(right_type),
            )

        return TYPE_BOOL

    def visit_assignment_expr(self, expr: AssignmentExpr) -> Type:
        target_type = self._check_expr(expr.target)
        value_type = self._check_expr(expr.value)
        loc = _loc(expr, self.ctx.current_file)

        # Check const assignment
        if isinstance(expr.target, IdentifierExpr):
            name = _name_of(expr.target)
            if self.ctx.environment.is_const(name):
                self.diagnostics.error(
                    TypeErrorCode.TYP500_CANNOT_ASSIGN_CONST,
                    loc, name,
                )

        # Type compatibility check
        if value_type.kind != TypeKind.UNKNOWN and target_type.kind != TypeKind.UNKNOWN:
            if not value_type.is_assignable_to(target_type):
                self.diagnostics.error(
                    TypeErrorCode.TYP101_ASSIGNMENT_TYPE_MISMATCH,
                    loc,
                    str(target_type), str(value_type),
                    expected_type=target_type,
                    actual_type=value_type,
                )

        return value_type

    def visit_compound_assignment_expr(self, expr: CompoundAssignmentExpr) -> Type:
        target_type = self._check_expr(expr.target)
        value_type = self._check_expr(expr.value)
        loc = _loc(expr, self.ctx.current_file)

        op = expr.operator if isinstance(expr.operator, str) else str(expr.operator)
        return self.inference.infer_binary(target_type, op, value_type, loc)

    def visit_call_expr(self, expr: CallExpr) -> Type:
        callee_type = self._check_expr(expr.callee)
        arg_types = [self._check_expr(arg) for arg in expr.arguments]
        loc = _loc(expr, self.ctx.current_file)
        return self.inference.infer_call(callee_type, arg_types, loc)

    def visit_method_call_expr(self, expr: MethodCallExpr) -> Type:
        obj_type = self._check_expr(expr.object)
        arg_types = [self._check_expr(arg) for arg in expr.arguments]
        loc = _loc(expr, self.ctx.current_file)
        return self.inference.infer_method_call(obj_type, expr.method, arg_types, loc)

    def visit_constructor_expr(self, expr: ConstructorExpr) -> Type:
        class_name = _name_of(expr)
        loc = _loc(expr, self.ctx.current_file)

        class_type = self.registry.get_type(class_name)
        if class_type is None:
            self.diagnostics.error(
                TypeErrorCode.TYP252_UNDEFINED_TYPE,
                loc, class_name,
            )
            for arg in expr.arguments:
                self._check_expr(arg)
            return TYPE_UNKNOWN

        for arg in expr.arguments:
            self._check_expr(arg)

        return class_type

    def visit_get_expr(self, expr: GetExpr) -> Type:
        obj_type = self._check_expr(expr.object)
        prop_name = expr.property
        loc = _loc(expr, self.ctx.current_file)

        if obj_type.kind == TypeKind.ANY:
            return TYPE_ANY

        type_name = obj_type.name
        members = self.registry.get_members(type_name)
        if prop_name in members:
            return members[prop_name].type

        methods = self.registry.get_methods(type_name)
        if prop_name in methods:
            sig = methods[prop_name]
            return FunctionType(tuple(sig.param_types), sig.return_type)

        # Check parent types
        parent = self.registry.get_parent(type_name)
        while parent:
            p_members = self.registry.get_members(parent)
            if prop_name in p_members:
                return p_members[prop_name].type
            p_methods = self.registry.get_methods(parent)
            if prop_name in p_methods:
                sig = p_methods[prop_name]
                return FunctionType(tuple(sig.param_types), sig.return_type)
            parent = self.registry.get_parent(parent)

        self.diagnostics.error(
            TypeErrorCode.TYP253_UNDEFINED_MEMBER,
            loc, type_name, prop_name,
            related_symbols=[type_name],
        )
        return TYPE_ANY

    def visit_set_expr(self, expr: SetExpr) -> Type:
        obj_type = self._check_expr(expr.object)
        value_type = self._check_expr(expr.value)
        return value_type

    def visit_index_expr(self, expr: IndexExpr) -> Type:
        obj_type = self._check_expr(expr.object)
        index_type = self._check_expr(expr.index)
        loc = _loc(expr, self.ctx.current_file)
        return self.inference.infer_index(obj_type, index_type, loc)

    def visit_slice_expr(self, expr: SliceExpr) -> Type:
        obj_type = self._check_expr(expr.object)
        if expr.start:
            self._check_expr(expr.start)
        if expr.end:
            self._check_expr(expr.end)
        return obj_type

    def visit_self_expr(self, expr: SelfExpr) -> Type:
        if not self.ctx.in_class:
            loc = _loc(expr, self.ctx.current_file)
            self.diagnostics.error(
                TypeErrorCode.TYP250_UNDEFINED_VARIABLE,
                loc, "self",
            )
            return TYPE_UNKNOWN

        class_ctx = self.ctx.current_class
        if class_ctx:
            return ClassType(class_ctx.name)
        return TYPE_ANY

    def visit_super_expr(self, expr: SuperExpr) -> Type:
        if not self.ctx.current_class or not self.ctx.current_class.parent_name:
            loc = _loc(expr, self.ctx.current_file)
            self.diagnostics.error(
                TypeErrorCode.TYP250_UNDEFINED_VARIABLE,
                loc, "super",
            )
            return TYPE_UNKNOWN
        parent_name = self.ctx.current_class.parent_name
        parent_type = self.registry.get_type(parent_name)
        return parent_type or ClassType(parent_name)

    def visit_list_expr(self, expr: ListExpr) -> Type:
        elem_types = [self._check_expr(e) for e in expr.elements]
        return self.inference.infer_list_literal(elem_types)

    def visit_dict_expr(self, expr: DictExpr) -> Type:
        key_types = [self._check_expr(k) for k in expr.keys]
        val_types = [self._check_expr(v) for v in expr.values]
        return self.inference.infer_dict_literal(key_types, val_types)

    def visit_tuple_expr(self, expr: TupleExpr) -> Type:
        elem_types = [self._check_expr(e) for e in expr.elements]
        return self.inference.infer_tuple_literal(elem_types)

    def visit_lambda_expr(self, expr: LambdaExpr) -> Type:
        self.ctx.environment.push("<lambda>")

        param_types: List[Optional[Type]] = []
        param_names: List[str] = []
        for param in expr.parameters:
            p_name = _name_of(param)
            pt: Optional[Type] = None
            if param.type_annotation:
                pt = self._resolve_type_node(param.type_annotation)
            else:
                pt = self.inference.new_type_var(f"_P_{p_name}")
            param_types.append(pt)
            self.ctx.environment.define(p_name, pt or TYPE_ANY, file=self.ctx.current_file)
            param_names.append(p_name)

        body_type = self._check_expr(expr.body)
        self.ctx.environment.pop()

        return self.inference.infer_lambda(param_names, param_types, body_type)

    def visit_if_expr(self, expr: IfExpr) -> Type:
        self._check_expr(expr.condition)
        then_type = self._check_expr(expr.then_branch)
        else_type = self._check_expr(expr.else_branch) if expr.else_branch else None
        loc = _loc(expr, self.ctx.current_file)
        return self.inference.infer_if_expr(then_type, else_type, loc)

    def visit_grouping_expr(self, expr: GroupingExpr) -> Type:
        return self._check_expr(expr.expression)

    def visit_placeholder_expr(self, expr: PlaceholderExpr) -> Type:
        return TYPE_ANY

    # ── Type Visitors ─────────────────────────────────────────────

    def visit_named_type(self, t: NamedType) -> Type:
        return self._resolve_type_name(t.name, _loc(t, self.ctx.current_file))

    def visit_generic_type(self, t: ASTGenericType) -> Type:
        return self._resolve_type_name(t.name, _loc(t, self.ctx.current_file))

    def visit_function_type(self, t: ASTFunctionType) -> Type:
        param_types = [self._resolve_type_node(p) for p in t.params]
        ret_type = self._resolve_type_node(t.return_type)
        return FunctionType(tuple(param_types), ret_type)

    def visit_optional_type(self, t: ASTOptionalType) -> Type:
        inner = self._resolve_type_node(t.inner)
        return OptionalType(inner)

    def visit_tuple_type(self, t: ASTTupleType) -> Type:
        elements = [self._resolve_type_node(e) for e in t.elements]
        return TupleType(tuple(elements))

    # ── Helpers ───────────────────────────────────────────────────

    def visit_parameter(self, param: Parameter) -> Type:
        return TYPE_NONE

    def visit_struct_field(self, field: StructField) -> Type:
        return TYPE_NONE

    def visit_enum_variant(self, variant: EnumVariant) -> Type:
        return TYPE_NONE

    def visit_elif_branch(self, branch: ElifBranch) -> Type:
        self._check_expr(branch.condition)
        return self._check_block(branch.body)

    def _check_expr(self, expr: Optional[Expr]) -> Type:
        """Check an expression and return its type."""
        if expr is None:
            return TYPE_NONE
        return expr.accept(self)

    def _resolve_type_node(self, type_node: TypeNode) -> Type:
        """Resolve a TypeNode AST to a Type."""
        return type_node.accept(self)

    def _resolve_type_name(self, name: str, location: TypeLocation) -> Type:
        """Resolve a type name to a Type."""
        # Check generics
        if self.ctx.has_generic(name):
            return self.ctx.get_generic(name) or TYPE_ANY

        # Check type registry
        typ = self.registry.get_type(name)
        if typ:
            return typ

        # Check environment
        env_type = self.ctx.environment.lookup(name)
        if env_type:
            return env_type

        self.diagnostics.error(
            TypeErrorCode.TYP252_UNDEFINED_TYPE,
            location,
            name,
        )
        return TYPE_UNKNOWN

    def _check_trait_implementations(self) -> None:
        """Verify all declared trait implementations are complete."""
        for type_name in self.registry.get_all_type_names():
            defn = self.registry.get(type_name)
            if defn is None:
                continue
            for trait_name in defn.implemented_traits:
                loc = TypeLocation(
                    file=defn.declaration_file,
                    line=defn.declaration_line,
                )
                self.trait_resolver.check_trait_implementation(
                    type_name, trait_name, loc,
                )

    def resolve_type_from_annotation(self, annotation: Optional[TypeNode]) -> Type:
        """Public helper for external code to resolve type annotations."""
        if annotation is None:
            return TYPE_ANY
        return self._resolve_type_node(annotation)


# ══════════════════════════════════════════════════════════════════
# Convenience Function
# ══════════════════════════════════════════════════════════════════


def check_types(
    program: Program,
    file: str = "<input>",
) -> TypeDiagnostics:
    """
    Convenience function to type-check a program.

    Args:
        program: The Program AST to check
        file: Source file path for diagnostics

    Returns:
        TypeDiagnostics with all type errors and warnings
    """
    checker = TypeChecker()
    checker.ctx.current_file = file
    checker.check(program)
    return checker.diagnostics
