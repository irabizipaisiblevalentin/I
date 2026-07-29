"""
Bytecode Generator for the I programming language.

This module converts AST nodes into bytecode instructions.
Uses the ASTVisitor pattern to walk the tree.
"""

from typing import Any, Dict, List, Optional
from compiler.ast.nodes import (
    ASTVisitor, Program, Module,
    Expr, Stmt, Decl, TypeNode,
    LiteralExpr, IdentifierExpr, UnaryExpr, BinaryExpr, LogicalExpr,
    AssignmentExpr, CompoundAssignmentExpr, CallExpr, MethodCallExpr,
    ConstructorExpr, GetExpr, SetExpr, IndexExpr, SliceExpr,
    SelfExpr, SuperExpr, ListExpr, DictExpr, TupleExpr,
    LambdaExpr, IfExpr, GroupingExpr, PlaceholderExpr,
    BlockStmt, IfStmt, WhileStmt, UntilStmt, ForStmt, ForEachStmt,
    ReturnStmt, BreakStmt, ContinueStmt, ThrowStmt, TryStmt,
    ExpressionStmt, EmptyStmt,
    VarDecl, FunctionDecl, StructDecl, EnumDecl, ClassDecl,
    TraitDecl, InterfaceDecl, ImportDecl, ExportDecl, MethodDecl,
    Parameter, StructField, EnumVariant, ElifBranch,
    NamedType,
)
from compiler.codegen.bytecode import OpCode, Chunk, Instruction


def _name_of(node: Any) -> str:
    """Extract string name from a node or token."""
    if isinstance(node, str):
        return node
    if hasattr(node, 'name'):
        return node.name
    if hasattr(node, 'lexeme'):
        return node.lexeme
    return str(node)


def _line_of(node: Any) -> int:
    """Extract line number from a node."""
    if hasattr(node, 'location'):
        return node.location.start_line
    if hasattr(node, 'line'):
        return node.line
    return 0


class CodeGenerator(ASTVisitor):
    """Bytecode code generator for the I programming language."""

    def __init__(self) -> None:
        self.chunk: Optional[Chunk] = None
        self.locals: List[Dict[str, int]] = []
        self.local_count: int = 0
        self.scope_depth: int = 0
        self.loop_starts: List[int] = []
        self.loop_ends: List[int] = []
        self.function_chunks: List[Chunk] = []
        self.current_chunk: Optional[Chunk] = None

    def generate(self, program: Program, chunk_name: str = "main") -> Chunk:
        """Generate bytecode from a Program AST node."""
        self.chunk = Chunk(chunk_name)
        self.current_chunk = self.chunk
        self.locals = [{}]
        self.local_count = 0
        self.scope_depth = 0
        self.loop_starts = []
        self.loop_ends = []

        program.accept(self)

        self._emit(OpCode.HALT)
        return self.chunk

    def _emit(self, opcode: OpCode, arg: Optional[int] = None, line: int = 0) -> int:
        """Emit a bytecode instruction and return its position."""
        if self.current_chunk is None:
            raise RuntimeError("No chunk initialized")
        return self.current_chunk.emit(opcode, arg, line)

    def _emit_constant(self, value: Any, line: int = 0) -> int:
        """Emit a constant load instruction."""
        if self.current_chunk is None:
            raise RuntimeError("No chunk initialized")
        const_index = self.current_chunk.add_constant(value)
        return self._emit(OpCode.LOAD_CONST, const_index, line)

    def _declare_variable(self, name: str) -> int:
        """Declare a variable in the current scope and return its slot."""
        if self.scope_depth >= len(self.locals):
            self.locals.append({})

        if name in self.locals[self.scope_depth]:
            return self.locals[self.scope_depth][name]

        self.locals[self.scope_depth][name] = self.local_count
        slot = self.local_count
        self.local_count += 1
        return slot

    def _resolve_variable(self, name: str) -> int:
        """Resolve a variable to its stack slot."""
        for depth in range(self.scope_depth, -1, -1):
            if name in self.locals[depth]:
                return self.locals[depth][name]
        raise RuntimeError(f"Undefined variable: {name}")

    def _begin_scope(self) -> None:
        """Begin a new scope."""
        self.scope_depth += 1
        if self.scope_depth >= len(self.locals):
            self.locals.append({})

    def _end_scope(self) -> None:
        """End the current scope and pop locals."""
        self.scope_depth -= 1
        if self.scope_depth >= 0:
            locals_in_scope = (
                len(self.locals[self.scope_depth + 1])
                if self.scope_depth + 1 < len(self.locals)
                else 0
            )
            for _ in range(locals_in_scope):
                self._emit(OpCode.POP)

    def _patch_jump(self, offset: int) -> None:
        """Patch a jump instruction to point to the current position."""
        if self.current_chunk is None:
            return
        jump = self.current_chunk.code[offset]
        if jump.arg is None:
            jump.arg = len(self.current_chunk.code)
        else:
            jump.arg = len(self.current_chunk.code) - jump.arg

    def _get_operator_opcode(self, op: str) -> Optional[OpCode]:
        """Map a string operator to an OpCode."""
        op_map = {
            '+': OpCode.ADD,
            '-': OpCode.SUB,
            '*': OpCode.MUL,
            '/': OpCode.DIV,
            '%': OpCode.MOD,
            '**': OpCode.MUL,
            '==': OpCode.EQ,
            '!=': OpCode.NEQ,
            '===': OpCode.EQ,
            '!==': OpCode.NEQ,
            '>': OpCode.GT,
            '<': OpCode.LT,
            '>=': OpCode.GTE,
            '<=': OpCode.LTE,
            '&': OpCode.BIT_AND,
            '|': OpCode.BIT_OR,
            '^': OpCode.BIT_XOR,
            '<<': OpCode.LEFT_SHIFT,
            '>>': OpCode.RIGHT_SHIFT,
            'and': OpCode.AND,
            'or': OpCode.OR,
            'si': OpCode.NOT,
            '!': OpCode.NOT,
        }
        return op_map.get(op)

    # ── Root Visitors ──────────────────────────────────────────

    def visit_program(self, program: Program) -> None:
        for decl in program.declarations:
            decl.accept(self)

    def visit_module(self, module: Module) -> None:
        for imp in module.imports:
            imp.accept(self)
        for decl in module.declarations:
            decl.accept(self)

    # ── Declaration Visitors ──────────────────────────────────

    def visit_var_decl(self, decl: VarDecl) -> None:
        line = _line_of(decl)

        if decl.initializer:
            decl.initializer.accept(self)
        else:
            self._emit_constant(None, line)

        slot = self._declare_variable(_name_of(decl))
        self._emit(OpCode.STORE_LOCAL, slot, line)

    def visit_function_decl(self, decl: FunctionDecl) -> None:
        line = _line_of(decl)
        name = _name_of(decl)

        # Create function chunk
        self.function_chunks.append(self.current_chunk or Chunk(name))
        saved_chunk = self.current_chunk
        saved_locals = self.locals
        saved_local_count = self.local_count
        saved_scope_depth = self.scope_depth

        func_chunk = Chunk(name)
        self.current_chunk = func_chunk
        self.function_chunks.append(func_chunk)
        self.locals = [{}]
        self.local_count = 0
        self.scope_depth = 0

        # Declare parameters as locals
        for param in decl.parameters:
            self._declare_variable(_name_of(param))

        # Generate body
        decl.body.accept(self)

        # Emit return if none present
        if not func_chunk.code or func_chunk.code[-1].opcode != OpCode.RETURN:
            self._emit_constant(None)
            self._emit(OpCode.RETURN)

        # Restore state
        self.current_chunk = saved_chunk
        self.locals = saved_locals
        self.local_count = saved_local_count
        self.scope_depth = saved_scope_depth
        self.function_chunks.pop()

        # Store function as constant and define as variable
        func_index = (saved_chunk or self.chunk).add_constant(func_chunk)
        self._emit(OpCode.LOAD_CONST, func_index, line)
        slot = self._declare_variable(name)
        self._emit(OpCode.STORE_LOCAL, slot, line)

    def visit_method_decl(self, decl: MethodDecl) -> None:
        # Methods are treated as standalone functions for now
        line = _line_of(decl)
        name = _name_of(decl)

        func_chunk = Chunk(name)
        saved_chunk = self.current_chunk
        saved_locals = self.locals
        saved_local_count = self.local_count
        saved_scope_depth = self.scope_depth

        self.current_chunk = func_chunk
        self.locals = [{}]
        self.local_count = 0
        self.scope_depth = 0

        # Declare parameters
        for param in decl.parameters:
            self._declare_variable(_name_of(param))

        # If not static, first param is 'self'
        if not decl.is_static and decl.parameters:
            self._declare_variable('self')

        # Generate body
        decl.body.accept(self)

        if not func_chunk.code or func_chunk.code[-1].opcode != OpCode.RETURN:
            self._emit_constant(None)
            self._emit(OpCode.RETURN)

        self.current_chunk = saved_chunk
        self.locals = saved_locals
        self.local_count = saved_local_count
        self.scope_depth = saved_scope_depth

    def visit_struct_decl(self, decl: StructDecl) -> None:
        # Structs are handled at runtime (simplified)
        pass

    def visit_enum_decl(self, decl: EnumDecl) -> None:
        # Enums are handled at runtime (simplified)
        pass

    def visit_class_decl(self, decl: ClassDecl) -> None:
        # Classes are handled at runtime (simplified)
        pass

    def visit_trait_decl(self, decl: TraitDecl) -> None:
        pass

    def visit_interface_decl(self, decl: InterfaceDecl) -> None:
        pass

    def visit_import_decl(self, decl: ImportDecl) -> None:
        # Imports are handled at runtime (simplified)
        pass

    def visit_export_decl(self, decl: ExportDecl) -> None:
        # Exports are handled at runtime (simplified)
        pass

    # ── Statement Visitors ──────────────────────────────────────

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        self._begin_scope()
        for s in stmt.statements:
            s.accept(self)
        self._end_scope()

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        line = _line_of(stmt)

        stmt.condition.accept(self)
        else_jump = self._emit(OpCode.JUMP_IF_FALSE)

        stmt.then_branch.accept(self)

        end_jump = self._emit(OpCode.JUMP)
        self._patch_jump(else_jump)

        for elif_branch in stmt.elif_branches:
            elif_branch.condition.accept(self)
            elif_else_jump = self._emit(OpCode.JUMP_IF_FALSE)
            elif_branch.body.accept(self)
            elif_end_jump = self._emit(OpCode.JUMP)
            self._patch_jump(elif_else_jump)
            self._patch_jump(elif_end_jump)

        if stmt.else_branch:
            stmt.else_branch.accept(self)

        self._patch_jump(end_jump)

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        loop_start = len(self.current_chunk.code) if self.current_chunk else 0
        self.loop_starts.append(loop_start)

        stmt.condition.accept(self)
        exit_jump = self._emit(OpCode.JUMP_IF_FALSE)

        self.loop_ends.append(0)  # placeholder
        stmt.body.accept(self)
        self.loop_ends.pop()

        self._emit(OpCode.JUMP, loop_start)
        self._patch_jump(exit_jump)

        self.loop_starts.pop()

    def visit_until_stmt(self, stmt: UntilStmt) -> None:
        line = _line_of(stmt)
        loop_start = len(self.current_chunk.code) if self.current_chunk else 0
        self.loop_starts.append(loop_start)

        stmt.body.accept(self)

        stmt.condition.accept(self)
        self._emit(OpCode.JUMP_IF_FALSE, loop_start, line)

        self.loop_starts.pop()

    def visit_for_stmt(self, stmt: ForStmt) -> None:
        line = _line_of(stmt)

        self._begin_scope()

        # Initialize loop variable
        stmt.start.accept(self)
        slot = self._declare_variable(stmt.variable)
        self._emit(OpCode.STORE_LOCAL, slot, line)

        loop_start = len(self.current_chunk.code) if self.current_chunk else 0
        self.loop_starts.append(loop_start)

        # Load variable and end value, compare
        self._emit(OpCode.LOAD_LOCAL, slot, line)
        stmt.end.accept(self)
        self._emit(OpCode.GTE)
        exit_jump = self._emit(OpCode.JUMP_IF_TRUE)
        self._emit(OpCode.POP)

        self.loop_ends.append(exit_jump)
        stmt.body.accept(self)
        self.loop_ends.pop()

        # Increment variable
        self._emit(OpCode.LOAD_LOCAL, slot, line)
        self._emit_constant(1)
        self._emit(OpCode.ADD)
        self._emit(OpCode.STORE_LOCAL, slot, line)

        # Jump back to start
        self._emit(OpCode.JUMP, loop_start)

        self._patch_jump(exit_jump)
        self._emit(OpCode.POP)

        self.loop_starts.pop()
        self._end_scope()

    def visit_for_each_stmt(self, stmt: ForEachStmt) -> None:
        line = _line_of(stmt)

        self._begin_scope()

        # Get iterator
        stmt.iterable.accept(self)
        self._emit(OpCode.GET_ITER)

        loop_start = len(self.current_chunk.code) if self.current_chunk else 0
        self.loop_starts.append(loop_start)

        # Get next element
        self._emit(OpCode.FOR_ITER)
        exit_jump = self._emit(OpCode.JUMP_IF_FALSE)

        # Store element
        slot = self._declare_variable(stmt.element)
        self._emit(OpCode.STORE_LOCAL, slot, line)

        self.loop_ends.append(exit_jump)
        stmt.body.accept(self)
        self.loop_ends.pop()

        # Jump back to start
        self._emit(OpCode.JUMP, loop_start)

        self._patch_jump(exit_jump)

        self.loop_starts.pop()
        self._end_scope()

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        line = _line_of(stmt)
        if stmt.value:
            stmt.value.accept(self)
        else:
            self._emit_constant(None, line)
        self._emit(OpCode.RETURN, line=line)

    def visit_break_stmt(self, stmt: BreakStmt) -> None:
        if not self.loop_ends:
            raise RuntimeError("break outside of loop")
        self._emit(OpCode.JUMP, self.loop_ends[-1])

    def visit_continue_stmt(self, stmt: ContinueStmt) -> None:
        if not self.loop_starts:
            raise RuntimeError("continue outside of loop")
        self._emit(OpCode.JUMP, self.loop_starts[-1])

    def visit_throw_stmt(self, stmt: ThrowStmt) -> None:
        line = _line_of(stmt)
        stmt.value.accept(self)
        self._emit(OpCode.RAISE, line=line)

    def visit_try_stmt(self, stmt: TryStmt) -> None:
        line = _line_of(stmt)
        self._emit(OpCode.SETUP_TRY, line=line)

        stmt.try_body.accept(self)

        self._emit(OpCode.POP_BLOCK, line=line)
        end_jump = self._emit(OpCode.JUMP)

        # Catch block
        if stmt.catch_var and stmt.catch_body:
            self._begin_scope()
            slot = self._declare_variable(stmt.catch_var)
            self._emit(OpCode.STORE_LOCAL, slot, line)
            stmt.catch_body.accept(self)
            self._end_scope()

        self._patch_jump(end_jump)

        # Finally block
        if stmt.finally_body:
            stmt.finally_body.accept(self)

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        stmt.expression.accept(self)
        self._emit(OpCode.POP, line=_line_of(stmt))

    def visit_empty_stmt(self, stmt: EmptyStmt) -> None:
        pass

    # ── Expression Visitors ─────────────────────────────────────

    def visit_literal_expr(self, expr: LiteralExpr) -> None:
        line = _line_of(expr)
        if expr.value is None:
            self._emit(OpCode.LOAD_NULL, line=line)
        elif isinstance(expr.value, bool):
            if expr.value:
                self._emit(OpCode.LOAD_TRUE, line=line)
            else:
                self._emit(OpCode.LOAD_FALSE, line=line)
        elif isinstance(expr.value, (int, float, str)):
            self._emit_constant(expr.value, line)
        else:
            raise RuntimeError(f"Unknown literal type: {type(expr.value)}")

    def visit_identifier_expr(self, expr: IdentifierExpr) -> None:
        line = _line_of(expr)
        slot = self._resolve_variable(_name_of(expr))
        self._emit(OpCode.LOAD_LOCAL, slot, line)

    def visit_unary_expr(self, expr: UnaryExpr) -> None:
        line = _line_of(expr)
        expr.right.accept(self)
        op = expr.operator
        if op == '-' or op == 'MINUS':
            self._emit(OpCode.NEG, line=line)
        elif op == '!' or op == 'si':
            self._emit(OpCode.NOT, line=line)
        else:
            raise RuntimeError(f"Unknown unary operator: {op}")

    def visit_binary_expr(self, expr: BinaryExpr) -> None:
        line = _line_of(expr)
        expr.left.accept(self)
        expr.right.accept(self)

        opcode = self._get_operator_opcode(expr.operator)
        if opcode:
            self._emit(opcode, line=line)
        else:
            raise RuntimeError(f"Unknown binary operator: {expr.operator}")

    def visit_logical_expr(self, expr: LogicalExpr) -> None:
        line = _line_of(expr)
        expr.left.accept(self)
        expr.right.accept(self)

        opcode = self._get_operator_opcode(expr.operator)
        if opcode:
            self._emit(opcode, line=line)
        else:
            raise RuntimeError(f"Unknown logical operator: {expr.operator}")

    def visit_assignment_expr(self, expr: AssignmentExpr) -> None:
        line = _line_of(expr)
        expr.value.accept(self)

        if isinstance(expr.target, IdentifierExpr):
            slot = self._resolve_variable(_name_of(expr.target))
            self._emit(OpCode.DUP)
            self._emit(OpCode.STORE_LOCAL, slot, line)
        elif isinstance(expr.target, GetExpr):
            expr.target.object.accept(self)
            self._emit(OpCode.SET_ATTR, line=line)
        elif isinstance(expr.target, IndexExpr):
            expr.target.object.accept(self)
            expr.target.index.accept(self)
            self._emit(OpCode.SET_ITEM, line=line)
        else:
            raise RuntimeError(f"Invalid assignment target: {type(expr.target)}")

    def visit_compound_assignment_expr(self, expr: CompoundAssignmentExpr) -> None:
        line = _line_of(expr)

        if isinstance(expr.target, IdentifierExpr):
            slot = self._resolve_variable(_name_of(expr.target))
            # Load current value
            self._emit(OpCode.LOAD_LOCAL, slot, line)
            # Load new value
            expr.value.accept(self)
            # Apply operator
            opcode = self._get_operator_opcode(expr.operator)
            if opcode:
                self._emit(opcode, line=line)
            else:
                raise RuntimeError(f"Unknown compound operator: {expr.operator}")
            # Store result
            self._emit(OpCode.STORE_LOCAL, slot, line)
        else:
            raise RuntimeError(f"Invalid compound assignment target: {type(expr.target)}")

    def visit_call_expr(self, expr: CallExpr) -> None:
        line = _line_of(expr)

        # Push arguments in reverse order
        for arg in reversed(expr.arguments):
            arg.accept(self)

        # Load callee
        expr.callee.accept(self)
        self._emit(OpCode.CALL, len(expr.arguments), line)

    def visit_method_call_expr(self, expr: MethodCallExpr) -> None:
        line = _line_of(expr)

        # Push arguments in reverse order
        for arg in reversed(expr.arguments):
            arg.accept(self)

        # Load object
        expr.object.accept(self)
        # Load method name as constant
        method_index = (self.current_chunk or self.chunk).add_constant(expr.method)
        self._emit(OpCode.LOAD_CONST, method_index, line)
        # Call method
        self._emit(OpCode.CALL, len(expr.arguments), line)

    def visit_constructor_expr(self, expr: ConstructorExpr) -> None:
        line = _line_of(expr)

        # Push arguments in reverse order
        for arg in reversed(expr.arguments):
            arg.accept(self)

        # Load class name as constant
        class_index = (self.current_chunk or self.chunk).add_constant(expr.class_name)
        self._emit(OpCode.LOAD_CONST, class_index, line)
        # Create new instance
        self._emit(OpCode.NEW_INSTANCE, len(expr.arguments), line)

    def visit_get_expr(self, expr: GetExpr) -> None:
        line = _line_of(expr)
        expr.object.accept(self)
        # Store property name as constant
        prop_index = (self.current_chunk or self.chunk).add_constant(expr.property)
        self._emit(OpCode.GET_ATTR, prop_index, line)

    def visit_set_expr(self, expr: SetExpr) -> None:
        line = _line_of(expr)
        expr.object.accept(self)
        expr.value.accept(self)
        prop_index = (self.current_chunk or self.chunk).add_constant(expr.property)
        self._emit(OpCode.SET_ATTR, prop_index, line)

    def visit_index_expr(self, expr: IndexExpr) -> None:
        line = _line_of(expr)
        expr.object.accept(self)
        expr.index.accept(self)
        self._emit(OpCode.GET_ITEM, line=line)

    def visit_slice_expr(self, expr: SliceExpr) -> None:
        line = _line_of(expr)
        expr.object.accept(self)

        if expr.start:
            expr.start.accept(self)
        else:
            self._emit_constant(0)

        if expr.end:
            expr.end.accept(self)
        else:
            self._emit_constant(-1)

        self._emit(OpCode.SLICE, line=line)

    def visit_self_expr(self, expr: SelfExpr) -> None:
        line = _line_of(expr)
        slot = self._resolve_variable('self')
        self._emit(OpCode.LOAD_LOCAL, slot, line)

    def visit_super_expr(self, expr: SuperExpr) -> None:
        line = _line_of(expr)
        # Simplified: load 'super' variable
        try:
            slot = self._resolve_variable('super')
            self._emit(OpCode.LOAD_LOCAL, slot, line)
        except RuntimeError:
            self._emit_constant(None, line)

    def visit_list_expr(self, expr: ListExpr) -> None:
        line = _line_of(expr)
        for elem in expr.elements:
            elem.accept(self)
        self._emit(OpCode.BUILD_LIST, len(expr.elements), line)

    def visit_dict_expr(self, expr: DictExpr) -> None:
        line = _line_of(expr)
        for key, value in zip(expr.keys, expr.values):
            key.accept(self)
            value.accept(self)
        self._emit(OpCode.BUILD_MAP, len(expr.keys), line)

    def visit_tuple_expr(self, expr: TupleExpr) -> None:
        line = _line_of(expr)
        for elem in expr.elements:
            elem.accept(self)
        self._emit(OpCode.BUILD_TUPLE, len(expr.elements), line)

    def visit_lambda_expr(self, expr: LambdaExpr) -> None:
        line = _line_of(expr)

        # Create lambda chunk
        lambda_chunk = Chunk("<lambda>")
        saved_chunk = self.current_chunk
        saved_locals = self.locals
        saved_local_count = self.local_count
        saved_scope_depth = self.scope_depth

        self.current_chunk = lambda_chunk
        self.locals = [{}]
        self.local_count = 0
        self.scope_depth = 0

        # Declare parameters
        for param in expr.parameters:
            self._declare_variable(_name_of(param))

        # Generate body
        expr.body.accept(self)

        if not lambda_chunk.code or lambda_chunk.code[-1].opcode != OpCode.RETURN:
            self._emit_constant(None)
            self._emit(OpCode.RETURN)

        self.current_chunk = saved_chunk
        self.locals = saved_locals
        self.local_count = saved_local_count
        self.scope_depth = saved_scope_depth

        # Load lambda as constant
        lambda_index = (saved_chunk or self.chunk).add_constant(lambda_chunk)
        self._emit(OpCode.LOAD_CONST, lambda_index, line)

    def visit_if_expr(self, expr: IfExpr) -> None:
        line = _line_of(expr)

        expr.condition.accept(self)
        else_jump = self._emit(OpCode.JUMP_IF_FALSE)

        expr.then_branch.accept(self)

        end_jump = self._emit(OpCode.JUMP)
        self._patch_jump(else_jump)

        if expr.else_branch:
            expr.else_branch.accept(self)

        self._patch_jump(end_jump)

    def visit_grouping_expr(self, expr: GroupingExpr) -> None:
        expr.expression.accept(self)

    def visit_placeholder_expr(self, expr: PlaceholderExpr) -> None:
        line = _line_of(expr)
        self._emit_constant(None, line)

    # ── Type Visitors (no-ops) ──────────────────────────────────

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

    # ── Helper Visitors (no-ops for codegen) ────────────────────

    def visit_parameter(self, param: Parameter) -> None:
        pass

    def visit_struct_field(self, field: StructField) -> None:
        pass

    def visit_enum_variant(self, variant: EnumVariant) -> None:
        pass

    def visit_elif_branch(self, branch: ElifBranch) -> None:
        pass


# ── Convenience ──────────────────────────────────────────────────


def generate(program: Program, chunk_name: str = "main") -> Chunk:
    """
    Convenience function to generate bytecode.

    Args:
        program: The Program AST to compile
        chunk_name: The name of the chunk

    Returns:
        A chunk of bytecode
    """
    generator = CodeGenerator()
    return generator.generate(program, chunk_name)
