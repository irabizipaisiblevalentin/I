"""
Semantic Analyzer for the I Programming Language

The canonical implementation of all language semantic rules.
Transforms a syntactically valid AST into a semantically valid program.

This module NEVER:
- Generates bytecode
- Executes code
- Optimizes code
- Infers final runtime behavior

Its responsibility is correctness and program validity.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..ast.nodes import (
    ASTNode, ASTVisitor, Expr, Stmt, Decl, TypeNode,
    LiteralExpr, IdentifierExpr, UnaryExpr, BinaryExpr, LogicalExpr,
    AssignmentExpr, CompoundAssignmentExpr, CallExpr, ConstructorExpr,
    GetExpr, SetExpr, IndexExpr, SliceExpr, SelfExpr, SuperExpr,
    ListExpr, DictExpr, TupleExpr, LambdaExpr, IfExpr, GroupingExpr,
    BlockStmt, IfStmt, WhileStmt, UntilStmt, ForStmt, ForEachStmt,
    ReturnStmt, BreakStmt, ContinueStmt, ThrowStmt, TryStmt,
    ExpressionStmt, EmptyStmt, Program,
    VarDecl, FunctionDecl, StructDecl, EnumDecl, ClassDecl,
    TraitDecl, InterfaceDecl, ImportDecl, ExportDecl, MethodDecl,
    Parameter, StructField, EnumVariant, ElifBranch,
    NamedType,
)
from .errors import SemanticErrorCode, SemanticErrorCollection, SourceLocation, SemanticSeverity
from .symbols import (
    Symbol, SymbolKind, TypeDescriptor, SymbolType, Visibility,
    make_variable, make_constant, make_function, make_method,
    make_class, make_struct, make_enum, make_trait, make_interface,
    make_parameter, TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_STRING,
    TYPE_NONE, TYPE_ANY,
)
from .scopes import Scope, ScopeKind, ScopeManager
from .builtins import register_builtins, is_reserved_keyword, is_builtin_type
from .names import resolve_name, resolve_function, resolve_class, resolve_type
from .imports import ImportResolver
from .constants import is_constant_expression, evaluate_constant, get_constant_value
from .controlflow import analyze_function_flow, function_always_returns
from .visibility import check_visibility
from .context import AnalysisContext


# ── Helpers ──────────────────────────────────────────────────────


def _name_of(node_or_token: Any) -> str:
    """Extract string name from a Token, string, or AST node."""
    if node_or_token is None:
        return ""
    if isinstance(node_or_token, str):
        return node_or_token
    if isinstance(node_or_token, IdentifierExpr):
        return _name_of(node_or_token.name)
    if hasattr(node_or_token, 'lexeme'):
        return node_or_token.lexeme
    if hasattr(node_or_token, 'name'):
        return _name_of(node_or_token.name)
    return str(node_or_token)


def _location_of(node: Any, file: str = "<input>") -> SourceLocation:
    """Extract SourceLocation from an AST node or token."""
    if node is None:
        return SourceLocation(file)
    if hasattr(node, 'span'):
        s = node.span
        return SourceLocation(
            file=file,
            line=getattr(s, 'start_line', 0),
            column=getattr(s, 'start_column', 0),
            end_line=getattr(s, 'end_line', 0),
            end_column=getattr(s, 'end_column', 0),
        )
    if hasattr(node, 'location'):
        loc = node.location
        return SourceLocation(
            file=getattr(loc, 'file', file),
            line=getattr(loc, 'start_line', 0),
            column=getattr(loc, 'start_column', 0),
            end_line=getattr(loc, 'end_line', 0),
            end_column=getattr(loc, 'end_column', 0),
        )
    if hasattr(node, 'line'):
        return SourceLocation(
            file=file,
            line=getattr(node, 'line', 0),
            column=getattr(node, 'column', 0),
            end_line=getattr(node, 'line', 0),
            end_column=getattr(node, 'column', 0) + getattr(node, 'span', 1),
        )
    return SourceLocation(file)


def _type_name_of(type_node: Any) -> str:
    """Extract type name from a TypeNode, Token, or string."""
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
# Semantic Analyzer
# ══════════════════════════════════════════════════════════════════


class SemanticAnalyzer(ASTVisitor):
    """
    Semantic analyzer for the I programming language.

    Performs:
    - Declaration validation (duplicates, reserved keywords)
    - Name resolution (variables, functions, classes, modules)
    - Basic type inference and checking
    - Control flow validation (return, break, continue)
    - Compile-time constant evaluation
    - Import/export resolution
    - Visibility enforcement
    """

    def __init__(self) -> None:
        self.ctx = AnalysisContext()
        self._return_type_stack: List[Optional[TypeDescriptor]] = []

    @property
    def diagnostics(self) -> SemanticErrorCollection:
        return self.ctx.diagnostics

    @property
    def has_errors(self) -> bool:
        return self.ctx.has_errors

    def analyze(self, program: Program) -> Program:
        """
        Analyze a Program AST node.
        Returns the same program after semantic validation.
        """
        self.ctx.clear()
        register_builtins(self.ctx.scopes.global_scope)

        program.accept(self)
        self.ctx.process_deferred_checks()
        return program

    # ── Declaration Visitors ────────────────────────────────────

    def visit_program(self, program: Program) -> None:
        for decl in program.declarations:
            if self.ctx.should_abort:
                break
            decl.accept(self)

    def visit_var_decl(self, decl: VarDecl) -> None:
        name = _name_of(decl)
        loc = _location_of(decl, self.ctx.current_file)

        # Check reserved keyword
        if is_reserved_keyword(name):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM110_RESERVED_KEYWORD, loc, name,
            )
            return

        # Check duplicate in same scope
        existing = self.ctx.scopes.lookup_local(name)
        if existing and existing.kind not in (SymbolKind.BUILTIN_TYPE, SymbolKind.BUILTIN_FUNCTION):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM100_DUPLICATE_VARIABLE, loc, name,
            )
            return

        # Type inference from initializer
        init_type = None
        if decl.initializer:
            init_type = self._analyze_expr(decl.initializer)

        # Type annotation
        ann_type = None
        if decl.type_annotation:
            type_name = _type_name_of(decl.type_annotation)
            if type_name:
                ann_type = resolve_type(
                    type_name, self.ctx.scopes.current,
                    self.ctx.diagnostics, loc,
                )

        # Determine final type
        final_type = ann_type or init_type or TYPE_ANY

        # Check const assignment
        if decl.is_const and decl.initializer:
            if not is_constant_expression(decl.initializer):
                self.ctx.diagnostics.warning(
                    SemanticErrorCode.SEM500_NOT_A_CONSTANT, loc, name,
                )

        # Check type compatibility
        if ann_type and init_type and not init_type.is_compatible_with(ann_type):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM300_TYPE_MISMATCH, loc,
                str(ann_type), str(init_type),
            )

        # Create symbol
        symbol = make_variable(
            name, final_type,
            is_const=decl.is_const,
            loc=loc,
        )

        # Define in current scope
        self.ctx.scopes.define(symbol)
        self.ctx.collected_symbols[name] = symbol

    def visit_function_decl(self, decl: FunctionDecl) -> None:
        name = _name_of(decl)
        loc = _location_of(decl, self.ctx.current_file)

        # Check reserved keyword
        if is_reserved_keyword(name):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM110_RESERVED_KEYWORD, loc, name,
            )
            return

        # Check duplicate
        existing = self.ctx.scopes.lookup_local(name)
        if existing and existing.kind not in (SymbolKind.BUILTIN_TYPE, SymbolKind.BUILTIN_FUNCTION):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM101_DUPLICATE_FUNCTION, loc, name,
            )
            return

        # Resolve return type
        ret_type = TYPE_NONE
        if decl.return_type:
            type_name = _type_name_of(decl.return_type)
            if type_name and type_name != 'ubusa':
                ret_type = resolve_type(
                    type_name, self.ctx.scopes.current,
                    self.ctx.diagnostics, loc,
                ) or TYPE_ANY

        # Collect parameter types
        param_types: List[TypeDescriptor] = []
        param_names: List[str] = []
        for param in decl.parameters:
            p_type = TYPE_ANY
            if param.type_annotation:
                tname = _type_name_of(param.type_annotation)
                if tname:
                    p_type = resolve_type(
                        tname, self.ctx.scopes.current,
                        self.ctx.diagnostics, loc,
                    ) or TYPE_ANY
            param_types.append(p_type)
            param_names.append(_name_of(param))

        # Create function symbol and define
        func_sym = make_function(name, param_types, ret_type, loc=loc)
        self.ctx.scopes.define(func_sym)
        self.ctx.collected_symbols[name] = func_sym

        # Enter function scope
        self.ctx.enter_function(name, ret_type)
        self._return_type_stack.append(ret_type)

        # Define parameters
        seen_params: Dict[str, bool] = {}
        for param in decl.parameters:
            p_name = _name_of(param)
            if p_name in seen_params:
                self.ctx.diagnostics.error(
                    SemanticErrorCode.SEM102_DUPLICATE_PARAMETER,
                    _location_of(param, self.ctx.current_file),
                    p_name, name,
                )
                continue
            seen_params[p_name] = True

            p_type = TYPE_ANY
            if param.type_annotation:
                tname = _type_name_of(param.type_annotation)
                if tname:
                    p_type = resolve_type(
                        tname, self.ctx.scopes.current,
                        self.ctx.diagnostics,
                        _location_of(param, self.ctx.current_file),
                    ) or TYPE_ANY

            param_sym = make_parameter(p_name, p_type)
            self.ctx.scopes.define(param_sym)

        # Analyze body
        decl.body.accept(self)

        # Check all return paths
        if ret_type.kind != SymbolType.NONE and not function_always_returns(decl.body):
            self.ctx.diagnostics.warning(
                SemanticErrorCode.SEM601_MISSING_RETURN_PATH, loc, name,
            )

        self._return_type_stack.pop()
        self.ctx.exit_function()

    def visit_method_decl(self, decl: MethodDecl) -> None:
        name = _name_of(decl)
        loc = _location_of(decl, self.ctx.current_file)

        # Determine class context
        class_name = self.ctx.current_class.name if self.ctx.current_class else "<unknown>"

        # Check duplicate in class
        if self.ctx.current_class and self.ctx.current_class.symbol:
            if name in self.ctx.current_class.symbol.members:
                self.ctx.diagnostics.error(
                    SemanticErrorCode.SEM104_DUPLICATE_METHOD, loc, name, class_name,
                )
                return

        # Resolve return type
        ret_type = TYPE_NONE
        if decl.return_type:
            type_name = _type_name_of(decl.return_type)
            if type_name and type_name != 'ubusa':
                ret_type = resolve_type(
                    type_name, self.ctx.scopes.current,
                    self.ctx.diagnostics, loc,
                ) or TYPE_ANY

        # Collect params
        param_types: List[TypeDescriptor] = []
        for param in decl.parameters:
            p_type = TYPE_ANY
            if param.type_annotation:
                tname = _type_name_of(param.type_annotation)
                if tname:
                    p_type = resolve_type(
                        tname, self.ctx.scopes.current,
                        self.ctx.diagnostics, loc,
                    ) or TYPE_ANY
            param_types.append(p_type)

        # Create method symbol
        method_sym = make_method(name, param_types, ret_type, is_static=decl.is_static, loc=loc)
        if self.ctx.current_class and self.ctx.current_class.symbol:
            self.ctx.current_class.symbol.members[name] = method_sym

        # Enter method scope
        self.ctx.enter_function(name, ret_type)
        self._return_type_stack.append(ret_type)

        # Define parameters
        seen_params: Dict[str, bool] = {}
        for param in decl.parameters:
            p_name = _name_of(param)
            if p_name in seen_params:
                self.ctx.diagnostics.error(
                    SemanticErrorCode.SEM102_DUPLICATE_PARAMETER,
                    _location_of(param, self.ctx.current_file),
                    p_name, f"{class_name}.{name}",
                )
                continue
            seen_params[p_name] = True

            p_type = TYPE_ANY
            if param.type_annotation:
                tname = _type_name_of(param.type_annotation)
                if tname:
                    p_type = resolve_type(
                        tname, self.ctx.scopes.current,
                        self.ctx.diagnostics,
                        _location_of(param, self.ctx.current_file),
                    ) or TYPE_ANY

            param_sym = make_parameter(p_name, p_type)
            self.ctx.scopes.define(param_sym)

        # If not static, define 'self'
        if not decl.is_static:
            self_sym = Symbol('self', SymbolKind.VARIABLE, TYPE_ANY)
            self.ctx.scopes.define(self_sym)

        # Analyze body
        decl.body.accept(self)

        self._return_type_stack.pop()
        self.ctx.exit_function()

    def visit_struct_decl(self, decl: StructDecl) -> None:
        name = _name_of(decl)
        loc = _location_of(decl, self.ctx.current_file)

        if is_reserved_keyword(name):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM110_RESERVED_KEYWORD, loc, name,
            )
            return

        existing = self.ctx.scopes.lookup_local(name)
        if existing and existing.kind not in (SymbolKind.BUILTIN_TYPE, SymbolKind.BUILTIN_FUNCTION):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM106_DUPLICATE_STRUCT, loc, name,
            )
            return

        struct_sym = make_struct(name, loc=loc)
        self.ctx.scopes.define(struct_sym)
        self.ctx.collected_symbols[name] = struct_sym

        # Analyze fields
        for field in decl.fields:
            fname = _name_of(field)
            floc = _location_of(field, self.ctx.current_file)
            f_type = TYPE_ANY
            if field.type_annotation:
                tname = _type_name_of(field.type_annotation)
                if tname:
                    f_type = resolve_type(
                        tname, self.ctx.scopes.current,
                        self.ctx.diagnostics, floc,
                    ) or TYPE_ANY

            field_sym = make_variable(fname, f_type, loc=floc)
            struct_sym.members[fname] = field_sym

            # Check default value
            if field.default:
                self._analyze_expr(field.default)

        # Analyze methods
        for method in decl.methods:
            method.accept(self)

    def visit_enum_decl(self, decl: EnumDecl) -> None:
        name = _name_of(decl)
        loc = _location_of(decl, self.ctx.current_file)

        if is_reserved_keyword(name):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM110_RESERVED_KEYWORD, loc, name,
            )
            return

        existing = self.ctx.scopes.lookup_local(name)
        if existing and existing.kind not in (SymbolKind.BUILTIN_TYPE, SymbolKind.BUILTIN_FUNCTION):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM107_DUPLICATE_ENUM, loc, name,
            )
            return

        enum_sym = make_enum(name, loc=loc)
        self.ctx.scopes.define(enum_sym)
        self.ctx.collected_symbols[name] = enum_sym

        # Register variants
        for variant in decl.variants:
            v_name = _name_of(variant)
            v_loc = _location_of(variant, self.ctx.current_file)
            v_type = TYPE_ANY
            if variant.value:
                v_type = self._analyze_expr(variant.value) or TYPE_ANY
            v_sym = make_variable(v_name, v_type, is_const=True, loc=v_loc)
            enum_sym.members[v_name] = v_sym

    def visit_class_decl(self, decl: ClassDecl) -> None:
        name = _name_of(decl)
        loc = _location_of(decl, self.ctx.current_file)

        if is_reserved_keyword(name):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM110_RESERVED_KEYWORD, loc, name,
            )
            return

        existing = self.ctx.scopes.lookup_local(name)
        if existing and existing.kind not in (SymbolKind.BUILTIN_TYPE, SymbolKind.BUILTIN_FUNCTION):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM103_DUPLICATE_CLASS, loc, name,
            )
            return

        parent_name = decl.parent
        class_sym = make_class(name, parent_name, loc=loc)
        self.ctx.scopes.define(class_sym)
        self.ctx.collected_symbols[name] = class_sym

        # Enter class scope
        self.ctx.enter_class(name, parent_name)

        # Define 'self' in class scope
        self_sym = Symbol('self', SymbolKind.VARIABLE, TYPE_ANY)
        self.ctx.scopes.define(self_sym)

        # Analyze members
        for member in decl.members:
            member.accept(self)

        self.ctx.exit_class()

    def visit_trait_decl(self, decl: TraitDecl) -> None:
        name = _name_of(decl)
        loc = _location_of(decl, self.ctx.current_file)

        existing = self.ctx.scopes.lookup_local(name)
        if existing and existing.kind not in (SymbolKind.BUILTIN_TYPE, SymbolKind.BUILTIN_FUNCTION):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM108_DUPLICATE_TRAIT, loc, name,
            )
            return

        trait_sym = make_trait(name, loc=loc)
        self.ctx.scopes.define(trait_sym)
        self.ctx.collected_symbols[name] = trait_sym

        self.ctx.enter_class(name)
        for member in decl.members:
            member.accept(self)
        self.ctx.exit_class()

    def visit_interface_decl(self, decl: InterfaceDecl) -> None:
        name = _name_of(decl)
        loc = _location_of(decl, self.ctx.current_file)

        existing = self.ctx.scopes.lookup_local(name)
        if existing and existing.kind not in (SymbolKind.BUILTIN_TYPE, SymbolKind.BUILTIN_FUNCTION):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM109_DUPLICATE_INTERFACE, loc, name,
            )
            return

        iface_sym = make_interface(name, loc=loc)
        self.ctx.scopes.define(iface_sym)
        self.ctx.collected_symbols[name] = iface_sym

        self.ctx.enter_class(name)
        for member in decl.members:
            member.accept(self)
        self.ctx.exit_class()

    def visit_import_decl(self, decl: ImportDecl) -> None:
        path = _name_of(decl.path)
        loc = _location_of(decl, self.ctx.current_file)
        alias = decl.alias
        if alias is not None:
            alias = _name_of(alias) if not isinstance(alias, str) else alias

        module_sym = self.ctx.imports.resolve_import(
            path, alias, self.ctx.diagnostics, loc,
        )
        if module_sym is not None:
            self.ctx.scopes.define(module_sym)

    def visit_export_decl(self, decl: ExportDecl) -> None:
        name = _name_of(decl)
        loc = _location_of(decl, self.ctx.current_file)

        # Verify the symbol exists in current scope
        symbol = self.ctx.scopes.lookup_local(name)
        if symbol is None:
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM404_EXPORT_NOT_FOUND, loc, name,
            )
            return

        symbol.visibility = Visibility.PUBLIC

    # ── Statement Visitors ──────────────────────────────────────

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        self.ctx.enter_block()
        for s in stmt.statements:
            if self.ctx.should_abort:
                break
            s.accept(self)
        self.ctx.exit_block()

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        cond_type = self._analyze_expr(stmt.condition)
        if cond_type and cond_type.kind not in (SymbolType.BOOL, SymbolType.ANY):
            self.ctx.diagnostics.warning(
                SemanticErrorCode.SEM300_TYPE_MISMATCH,
                _location_of(stmt.condition, self.ctx.current_file),
                "bool", str(cond_type),
            )
        stmt.then_branch.accept(self)
        for elif_b in stmt.elif_branches:
            elif_b.condition.accept(self)
            elif_b.body.accept(self)
        if stmt.else_branch:
            stmt.else_branch.accept(self)

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        self._analyze_expr(stmt.condition)
        self.ctx.enter_loop()
        stmt.body.accept(self)
        self.ctx.exit_loop()

    def visit_until_stmt(self, stmt: UntilStmt) -> None:
        self._analyze_expr(stmt.condition)
        self.ctx.enter_loop()
        stmt.body.accept(self)
        self.ctx.exit_loop()

    def visit_for_stmt(self, stmt: ForStmt) -> None:
        self._analyze_expr(stmt.start)
        self._analyze_expr(stmt.end)
        if stmt.step:
            self._analyze_expr(stmt.step)

        self.ctx.enter_loop()
        self.ctx.enter_block("for")
        var_name = _name_of(stmt) if hasattr(stmt, 'name') else ""
        if not var_name:
            # ForStmt has 'variable' attribute
            var_name = getattr(stmt, 'variable', None)
            if var_name is not None:
                var_name = _name_of(var_name)
            else:
                var_name = ""
        var_sym = make_variable(var_name, TYPE_INT, loc=_location_of(stmt, self.ctx.current_file))
        self.ctx.scopes.define(var_sym)
        stmt.body.accept(self)
        self.ctx.exit_block()
        self.ctx.exit_loop()

    def visit_for_each_stmt(self, stmt: ForEachStmt) -> None:
        iterable_type = self._analyze_expr(stmt.iterable)
        self.ctx.enter_loop()
        self.ctx.enter_block("foreach")
        elem_name = getattr(stmt, 'element', None) or ""
        if not isinstance(elem_name, str):
            elem_name = _name_of(elem_name)
        elem_type = TYPE_ANY
        if iterable_type and iterable_type.kind == SymbolType.LIST and iterable_type.element_type:
            elem_type = iterable_type.element_type
        elem_sym = make_variable(elem_name, elem_type, loc=_location_of(stmt, self.ctx.current_file))
        self.ctx.scopes.define(elem_sym)
        stmt.body.accept(self)
        self.ctx.exit_block()
        self.ctx.exit_loop()

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        if not self.ctx.in_function:
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM304_RETURN_OUTSIDE_FUNCTION,
                _location_of(stmt, self.ctx.current_file),
            )
            return

        if stmt.value:
            ret_type = self._analyze_expr(stmt.value)
        else:
            ret_type = TYPE_NONE

        # Check against expected return type
        expected = self.ctx.current_function.return_type if self.ctx.current_function else None
        if expected and ret_type and expected.kind != SymbolType.NONE:
            if not ret_type.is_compatible_with(expected):
                self.ctx.diagnostics.error(
                    SemanticErrorCode.SEM300_TYPE_MISMATCH,
                    _location_of(stmt, self.ctx.current_file),
                    str(expected), str(ret_type),
                )

    def visit_break_stmt(self, stmt: BreakStmt) -> None:
        if not self.ctx.in_loop:
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM305_BREAK_OUTSIDE_LOOP,
                _location_of(stmt, self.ctx.current_file),
            )

    def visit_continue_stmt(self, stmt: ContinueStmt) -> None:
        if not self.ctx.in_loop:
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM306_CONTINUE_OUTSIDE_LOOP,
                _location_of(stmt, self.ctx.current_file),
            )

    def visit_throw_stmt(self, stmt: ThrowStmt) -> None:
        self._analyze_expr(stmt.value)

    def visit_try_stmt(self, stmt: TryStmt) -> None:
        stmt.try_body.accept(self)
        if stmt.catch_body:
            self.ctx.enter_block("catch")
            if stmt.catch_var:
                catch_name = _name_of(stmt) if hasattr(stmt, 'catch_var') else ""
                if not catch_name:
                    catch_name = getattr(stmt, 'catch_var', '')
                    if catch_name is not None:
                        catch_name = _name_of(catch_name) if not isinstance(catch_name, str) else catch_name
                    else:
                        catch_name = ""
                catch_sym = make_variable(catch_name, TYPE_ANY, loc=_location_of(stmt, self.ctx.current_file))
                self.ctx.scopes.define(catch_sym)
            stmt.catch_body.accept(self)
            self.ctx.exit_block()
        if stmt.finally_body:
            stmt.finally_body.accept(self)

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        self._analyze_expr(stmt.expression)

    def visit_empty_stmt(self, stmt: EmptyStmt) -> None:
        pass

    def visit_parameter(self, param: Parameter) -> None:
        pass

    def visit_struct_field(self, field: StructField) -> None:
        pass

    def visit_enum_variant(self, variant: EnumVariant) -> None:
        pass

    def visit_elif_branch(self, branch: ElifBranch) -> None:
        self._analyze_expr(branch.condition)
        branch.body.accept(self)

    # ── Expression Visitors ─────────────────────────────────────

    def visit_literal_expr(self, expr: LiteralExpr) -> TypeDescriptor:
        if expr.value is None:
            return TYPE_NONE
        if isinstance(expr.value, bool):
            return TYPE_BOOL
        if isinstance(expr.value, int):
            return TYPE_INT
        if isinstance(expr.value, float):
            return TYPE_FLOAT
        if isinstance(expr.value, str):
            return TYPE_STRING
        return TYPE_ANY

    def visit_identifier_expr(self, expr: IdentifierExpr) -> TypeDescriptor:
        name = _name_of(expr)
        loc = _location_of(expr, self.ctx.current_file)
        symbol = resolve_name(name, self.ctx.scopes.current, self.ctx.diagnostics, loc)
        if symbol and symbol.type_descriptor:
            return symbol.type_descriptor
        return TYPE_ANY

    def visit_unary_expr(self, expr: UnaryExpr) -> TypeDescriptor:
        operand_type = self._analyze_expr(expr.right)
        op = expr.operator
        op_str = op if isinstance(op, str) else getattr(op, 'lexeme', str(op))

        if op_str in ('-', 'MINUS'):
            if operand_type.kind not in (SymbolType.INT, SymbolType.FLOAT, SymbolType.ANY):
                self.ctx.diagnostics.error(
                    SemanticErrorCode.SEM300_TYPE_MISMATCH,
                    _location_of(expr, self.ctx.current_file),
                    "numeric", str(operand_type),
                )
            return operand_type

        if op_str in ('!', 'si'):
            if operand_type.kind not in (SymbolType.BOOL, SymbolType.ANY):
                self.ctx.diagnostics.error(
                    SemanticErrorCode.SEM300_TYPE_MISMATCH,
                    _location_of(expr, self.ctx.current_file),
                    "bool", str(operand_type),
                )
            return TYPE_BOOL

        return TYPE_ANY

    def visit_binary_expr(self, expr: BinaryExpr) -> TypeDescriptor:
        left_type = self._analyze_expr(expr.left)
        right_type = self._analyze_expr(expr.right)
        op = expr.operator
        op_str = op if isinstance(op, str) else getattr(op, 'lexeme', str(op))

        # Arithmetic operators
        if op_str in ('+', '-', '*', '/', '%', '**'):
            if left_type.kind in (SymbolType.INT, SymbolType.FLOAT, SymbolType.ANY):
                if right_type.kind in (SymbolType.INT, SymbolType.FLOAT, SymbolType.ANY):
                    if left_type.kind == SymbolType.FLOAT or right_type.kind == SymbolType.FLOAT:
                        return TYPE_FLOAT
                    return TYPE_INT
            if op_str == '+':
                if left_type.kind == SymbolType.STRING and right_type.kind == SymbolType.STRING:
                    return TYPE_STRING
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM300_TYPE_MISMATCH,
                _location_of(expr, self.ctx.current_file),
                "numeric or string", f"{left_type} {op_str} {right_type}",
            )
            return TYPE_ANY

        # Comparison operators
        if op_str in ('==', '!=', '===', '!==', '>', '<', '>=', '<=',
                      'irenze', 'munsi', 'munsi_ya'):
            return TYPE_BOOL

        # Bitwise operators
        if op_str in ('&', '|', '^', '<<', '>>', '>>>'):
            return left_type

        # String concatenation
        if op_str == '+' and (left_type.kind == SymbolType.STRING or right_type.kind == SymbolType.STRING):
            return TYPE_STRING

        return TYPE_ANY

    def visit_logical_expr(self, expr: LogicalExpr) -> TypeDescriptor:
        left_type = self._analyze_expr(expr.left)
        right_type = self._analyze_expr(expr.right)
        return TYPE_BOOL

    def visit_assignment_expr(self, expr: AssignmentExpr) -> TypeDescriptor:
        target_type = self._analyze_expr(expr.target)
        value_type = self._analyze_expr(expr.value)

        # Check target is assignable
        if isinstance(expr.target, IdentifierExpr):
            name = _name_of(expr.target)
            symbol = self.ctx.scopes.lookup(name)
            if symbol:
                if symbol.is_const:
                    self.ctx.diagnostics.error(
                        SemanticErrorCode.SEM300_TYPE_MISMATCH,
                        _location_of(expr, self.ctx.current_file),
                        f"mutable '{name}'", "constant",
                    )
            else:
                self.ctx.diagnostics.error(
                    SemanticErrorCode.SEM200_UNDEFINED_VARIABLE,
                    _location_of(expr.target, self.ctx.current_file),
                    name,
                )

        if value_type and target_type and not value_type.is_compatible_with(target_type):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM300_TYPE_MISMATCH,
                _location_of(expr, self.ctx.current_file),
                str(target_type), str(value_type),
            )

        return value_type or TYPE_ANY

    def visit_compound_assignment_expr(self, expr: CompoundAssignmentExpr) -> TypeDescriptor:
        target_type = self._analyze_expr(expr.target)
        value_type = self._analyze_expr(expr.value)
        return target_type or TYPE_ANY

    def visit_call_expr(self, expr: CallExpr) -> TypeDescriptor:
        callee_type = self._analyze_expr(expr.callee)
        loc = _location_of(expr, self.ctx.current_file)

        if callee_type.kind == SymbolType.FUNCTION:
            if callee_type.return_type:
                return callee_type.return_type
            return TYPE_NONE

        if callee_type.kind == SymbolType.ANY:
            for arg in expr.arguments:
                self._analyze_expr(arg)
            return TYPE_ANY

        self.ctx.diagnostics.error(
            SemanticErrorCode.SEM301_NOT_CALLABLE,
            loc, str(callee_type),
        )
        for arg in expr.arguments:
            self._analyze_expr(arg)
        return TYPE_ANY

    def visit_constructor_expr(self, expr: ConstructorExpr) -> TypeDescriptor:
        class_name = _name_of(expr)
        loc = _location_of(expr, self.ctx.current_file)

        class_sym = self.ctx.scopes.lookup(class_name)
        if class_sym is None:
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM202_UNDEFINED_CLASS, loc, class_name,
            )

        for arg in expr.arguments:
            self._analyze_expr(arg)

        return TypeDescriptor(SymbolType.CLASS, class_name)

    def visit_get_expr(self, expr: GetExpr) -> TypeDescriptor:
        obj_type = self._analyze_expr(expr.object)
        prop_name = _name_of(expr) if hasattr(expr, 'name') else ""
        if not prop_name:
            prop_name = getattr(expr, 'property', '')
            if prop_name is not None:
                prop_name = _name_of(prop_name) if not isinstance(prop_name, str) else prop_name
            else:
                prop_name = ""

        if obj_type.kind in (SymbolType.CLASS, SymbolType.STRUCT):
            obj_name = obj_type.name
            obj_sym = self.ctx.scopes.lookup(obj_name)
            if obj_sym and prop_name in obj_sym.members:
                member = obj_sym.members[prop_name]
                if member.type_descriptor:
                    return member.type_descriptor

        if obj_type.kind == SymbolType.ANY:
            return TYPE_ANY

        return TYPE_ANY

    def visit_set_expr(self, expr: SetExpr) -> TypeDescriptor:
        obj_type = self._analyze_expr(expr.object)
        value_type = self._analyze_expr(expr.value)
        prop_name = _name_of(expr) if hasattr(expr, 'name') else ""
        if not prop_name:
            prop_name = getattr(expr, 'property', '')
            if prop_name is not None:
                prop_name = _name_of(prop_name) if not isinstance(prop_name, str) else prop_name
            else:
                prop_name = ""
        return value_type or TYPE_ANY

    def visit_index_expr(self, expr: IndexExpr) -> TypeDescriptor:
        obj_type = self._analyze_expr(expr.object)
        index_type = self._analyze_expr(expr.index)
        loc = _location_of(expr, self.ctx.current_file)

        if index_type.kind not in (SymbolType.INT, SymbolType.ANY):
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM308_INDEX_MUST_BE_NUMERIC, loc,
            )

        if obj_type.kind == SymbolType.LIST and obj_type.element_type:
            return obj_type.element_type
        if obj_type.kind == SymbolType.DICT and obj_type.value_type:
            return obj_type.value_type
        if obj_type.kind == SymbolType.STRING:
            return TYPE_STRING
        if obj_type.kind == SymbolType.ANY:
            return TYPE_ANY

        self.ctx.diagnostics.error(
            SemanticErrorCode.SEM307_CANNOT_INDEX, loc, str(obj_type),
        )
        return TYPE_ANY

    def visit_slice_expr(self, expr: SliceExpr) -> TypeDescriptor:
        obj_type = self._analyze_expr(expr.object)
        if expr.start:
            self._analyze_expr(expr.start)
        if expr.end:
            self._analyze_expr(expr.end)
        return obj_type or TYPE_ANY

    def visit_self_expr(self, expr: SelfExpr) -> TypeDescriptor:
        if not self.ctx.in_class:
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM200_UNDEFINED_VARIABLE,
                _location_of(expr, self.ctx.current_file),
                "self",
            )
        return TYPE_ANY

    def visit_super_expr(self, expr: SuperExpr) -> TypeDescriptor:
        if not self.ctx.current_class or not self.ctx.current_class.parent_name:
            self.ctx.diagnostics.error(
                SemanticErrorCode.SEM200_UNDEFINED_VARIABLE,
                _location_of(expr, self.ctx.current_file),
                "super",
            )
        return TYPE_ANY

    def visit_list_expr(self, expr: ListExpr) -> TypeDescriptor:
        if not expr.elements:
            return TypeDescriptor(SymbolType.LIST, "urutonde", element_type=TYPE_ANY)
        first_type = self._analyze_expr(expr.elements[0])
        for elem in expr.elements[1:]:
            self._analyze_expr(elem)
        return TypeDescriptor(SymbolType.LIST, "urutonde", element_type=first_type)

    def visit_dict_expr(self, expr: DictExpr) -> TypeDescriptor:
        k_type = TYPE_ANY
        v_type = TYPE_ANY
        if expr.keys:
            k_type = self._analyze_expr(expr.keys[0])
        if expr.values:
            v_type = self._analyze_expr(expr.values[0])
        for k, v in zip(expr.keys[1:], expr.values[1:]):
            self._analyze_expr(k)
            self._analyze_expr(v)
        return TypeDescriptor(SymbolType.DICT, "ikarita",
                             key_type=k_type, value_type=v_type)

    def visit_tuple_expr(self, expr: TupleExpr) -> TypeDescriptor:
        for elem in expr.elements:
            self._analyze_expr(elem)
        return TYPE_ANY

    def visit_lambda_expr(self, expr: LambdaExpr) -> TypeDescriptor:
        self.ctx.enter_function("<lambda>")
        for param in expr.parameters:
            p_name = _name_of(param)
            p_sym = make_parameter(p_name, TYPE_ANY)
            self.ctx.scopes.define(p_sym)
        self._analyze_expr(expr.body)
        self.ctx.exit_function()
        return TYPE_ANY

    def visit_if_expr(self, expr: IfExpr) -> TypeDescriptor:
        self._analyze_expr(expr.condition)
        then_type = self._analyze_expr(expr.then_branch)
        else_type = self._analyze_expr(expr.else_branch) if expr.else_branch else TYPE_NONE
        return then_type or TYPE_ANY

    def visit_grouping_expr(self, expr: GroupingExpr) -> TypeDescriptor:
        return self._analyze_expr(expr.expression)

    def visit_placeholder_expr(self, expr: PlaceholderExpr) -> TypeDescriptor:
        return TYPE_ANY

    # ── Type Visitors (mostly no-ops) ───────────────────────────

    def visit_named_type(self, t: NamedType) -> None:
        pass

    def visit_generic_type(self, t: Any) -> None:
        pass

    def visit_function_type(self, t: Any) -> None:
        pass

    def visit_optional_type(self, t: Any) -> None:
        pass

    def visit_tuple_type(self, t: Any) -> None:
        pass

    # ── Internal Helpers ────────────────────────────────────────

    def _analyze_expr(self, expr: Optional[Expr]) -> Optional[TypeDescriptor]:
        """Analyze an expression and return its type."""
        if expr is None:
            return TYPE_NONE
        return expr.accept(self)


# ══════════════════════════════════════════════════════════════════
# Convenience
# ══════════════════════════════════════════════════════════════════


def analyze(program: Program, file: str = "<input>") -> SemanticErrorCollection:
    """
    Convenience function to perform semantic analysis.

    Args:
        program: The Program AST to analyze
        file: Source file path for diagnostics

    Returns:
        SemanticErrorCollection with all diagnostics
    """
    analyzer = SemanticAnalyzer()
    analyzer.ctx.current_file = file
    analyzer.analyze(program)
    return analyzer.diagnostics
