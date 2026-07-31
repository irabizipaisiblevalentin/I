"""
AST-to-IR Lowering Pass

Walks a fully typed AST and emits an IRModule with corresponding
IRFunctions, basic blocks, and instructions. Requires type annotations
set by the TypeChecker via set_metadata('type', ...).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..ast.nodes import (
    AssignmentExpr,
    ASTNode,
    ASTVisitor,
    BinaryExpr,
    BlockStmt,
    BreakStmt,
    CallExpr,
    ClassDecl,
    ConstructorExpr,
    ContinueStmt,
    DictExpr,
    ElifBranch,
    EmptyStmt,
    EnumDecl,
    EnumVariant,
    ExportDecl,
    ExpressionStmt,
    ForEachStmt,
    ForStmt,
    FunctionDecl,
    GetExpr,
    GroupingExpr,
    IdentifierExpr,
    IfExpr,
    IfStmt,
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
    UnaryExpr,
    UntilStmt,
    VarDecl,
    WhileStmt,
)
from .basic_block import BasicBlock
from .builder import IRBuilder
from .function import IRFunction
from .instructions import (
    Alloca,
    ICmpPredicate,
    Store,
)
from .metadata import DebugLocation
from .module import IRModule
from .type_mapper import map_type
from .types import (
    IR_F64,
    IR_I1,
    IR_I8,
    IR_I32,
    IR_I64,
    IntegerType,
    IRFunctionType,
    IRType,
    PointerType,
)
from .values import BoolConstant, FloatConstant, IntConstant, StringConstant, Value

if TYPE_CHECKING:
    from ..typesystem.types import Type


class LoweringError(Exception):
    """Raised when AST lowering fails."""
    pass


class ASTLowering(ASTVisitor):
    """Lower a fully typed AST to an IRModule.

    Usage:
        lowerer = ASTLowering()
        ir_module = lowerer.lower(program)"""

    def __init__(self, module_name: str = "") -> None:
        self.module = IRModule(module_name)
        self.builder = IRBuilder()
        self._vars: dict[str, Alloca] = {}
        self._current_func: IRFunction | None = None
        self._break_blocks: list[BasicBlock] = []
        self._continue_blocks: list[BasicBlock] = []

    def lower(self, node: ASTNode) -> IRModule:
        node.accept(self)
        return self.module

    # ── Helpers ────────────────────────────────────────────────

    def _get_type(self, node: ASTNode) -> Type:
        t = node.get_metadata('type')
        if t is None:
            raise LoweringError(f"No type metadata on {node.node_type} at {node.location}")
        return t

    def _ir_type(self, node: ASTNode) -> IRType:
        return map_type(self._get_type(node))

    def _alloc_var(self, name: str, ir_type: IRType) -> Alloca:
        if name in self._vars:
            return self._vars[name]
        alloca = self.builder.alloca(ir_type, name)
        self._vars[name] = alloca
        return alloca

    def _load_var(self, name: str) -> Value:
        alloca = self._vars.get(name)
        if alloca is None:
            raise LoweringError(f"Variable '{name}' not allocated")
        ptr_type = alloca.type
        elem_type = ptr_type.element_type if isinstance(ptr_type, PointerType) else IR_I64
        return self.builder.load(elem_type, alloca, name)

    def _store_var(self, name: str, value: Value) -> Store:
        alloca = self._vars.get(name)
        if alloca is None:
            raise LoweringError(f"Variable '{name}' not allocated")
        return self.builder.store(value, alloca)

    def _emit_expr(self, expr: ASTNode) -> Value:
        return expr.accept(self)

    def _make_debug_loc(self, node: ASTNode) -> DebugLocation | None:
        loc = node.location
        if loc is None:
            return None
        return DebugLocation(loc.start_line, loc.start_column, loc.file)

    # ── Root ───────────────────────────────────────────────────

    def visit_program(self, program: Program) -> None:
        for decl in program.declarations:
            decl.accept(self)

    def visit_module(self, module: Module) -> None:
        pass
        for decl in module.declarations:
            decl.accept(self)

    # ── Declarations ───────────────────────────────────────────

    def visit_var_decl(self, decl: VarDecl) -> None:
        ir_type = self._ir_type(decl)
        self._alloc_var(decl.name, ir_type)
        if decl.initializer:
            value = self._emit_expr(decl.initializer)
            self._store_var(decl.name, value)

    def visit_function_decl(self, decl: FunctionDecl) -> None:
        func_type: Type = self._get_type(decl)
        ir_func_type = map_type(func_type)
        if not isinstance(ir_func_type, IRFunctionType):
            raise LoweringError(f"Expected IRFunctionType for function '{decl.name}'")
        ir_func = IRFunction(decl.name, ir_func_type)
        self.module.add_function(ir_func)

        prev_func = self._current_func
        prev_vars = dict(self._vars)
        self._current_func = ir_func
        self._vars.clear()

        entry = BasicBlock("entry")
        ir_func.append_block(entry)
        self.builder.position_at_end(entry)

        for i, param in enumerate(decl.parameters):
            param_ir_type = map_type(self._get_type(param))
            alloca = self._alloc_var(param.name, param_ir_type)
            self.builder.store(ir_func.args[i], alloca)

        decl.body.accept(self)

        self.builder.position_at_end(entry)
        if not self._block_terminated(entry):
            self.builder.ret()

        self._current_func = prev_func
        self._vars = prev_vars

    def visit_method_decl(self, decl: MethodDecl) -> None:
        func_type: Type = self._get_type(decl)
        ir_func_type = map_type(func_type)
        if not isinstance(ir_func_type, IRFunctionType):
            raise LoweringError(f"Expected IRFunctionType for method '{decl.name}'")
        method_name = decl.name
        ir_func = IRFunction(method_name, ir_func_type)
        self.module.add_function(ir_func)

        prev_func = self._current_func
        prev_vars = dict(self._vars)
        self._current_func = ir_func
        self._vars.clear()

        entry = BasicBlock("entry")
        ir_func.append_block(entry)
        self.builder.position_at_end(entry)

        for i, param in enumerate(decl.parameters):
            param_ir_type = map_type(self._get_type(param))
            alloca = self._alloc_var(param.name, param_ir_type)
            self.builder.store(ir_func.args[i], alloca)

        if not decl.is_static:
            self_ir_type = IR_I8
            self._alloc_var("self", PointerType(self_ir_type))

        decl.body.accept(self)

        if not self._block_terminated(entry):
            self.builder.ret()

        self._current_func = prev_func
        self._vars = prev_vars

    def visit_struct_decl(self, decl: StructDecl) -> None:
        pass

    def visit_enum_decl(self, decl: EnumDecl) -> None:
        pass

    def visit_class_decl(self, decl: ClassDecl) -> None:
        pass

    def visit_trait_decl(self, decl: InterfaceDecl) -> None:
        pass

    def visit_interface_decl(self, decl: InterfaceDecl) -> None:
        pass

    def visit_import_decl(self, decl: ImportDecl) -> None:
        pass

    def visit_export_decl(self, decl: ExportDecl) -> None:
        pass

    # ── Statements ─────────────────────────────────────────────

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        prev_vars_len = len(self._vars)
        for s in stmt.statements:
            s.accept(self)
        self._trim_vars(prev_vars_len)

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        self._emit_expr(stmt.expression)

    def visit_empty_stmt(self, stmt: EmptyStmt) -> None:
        pass

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        if stmt.value:
            value = self._emit_expr(stmt.value)
            self.builder.ret(value)
        else:
            self.builder.ret()

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        if self._current_func is None:
            raise LoweringError("if outside function")
        cond = self._emit_expr(stmt.condition)
        then_block = BasicBlock("if.then")
        else_block = BasicBlock("if.else")
        merge_block = BasicBlock("if.end")
        self._current_func.append_block(then_block)
        self._current_func.append_block(else_block)
        self._current_func.append_block(merge_block)
        self.builder.cond_branch(cond, then_block, else_block)

        self.builder.position_at_end(then_block)
        stmt.then_branch.accept(self)
        if not self._block_terminated(self.builder.block):
            self.builder.branch(merge_block)

        self.builder.position_at_end(else_block)
        if stmt.else_branch:
            stmt.else_branch.accept(self)
        if not self._block_terminated(self.builder.block):
            self.builder.branch(merge_block)

        self.builder.position_at_end(merge_block)

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        if self._current_func is None:
            raise LoweringError("while outside function")
        header_block = BasicBlock("while.header")
        body_block = BasicBlock("while.body")
        end_block = BasicBlock("while.end")
        self._current_func.append_block(header_block)
        self._current_func.append_block(body_block)
        self._current_func.append_block(end_block)

        self._break_blocks.append(end_block)
        self._continue_blocks.append(header_block)

        self.builder.branch(header_block)
        self.builder.position_at_end(header_block)
        cond = self._emit_expr(stmt.condition)
        self.builder.cond_branch(cond, body_block, end_block)

        self.builder.position_at_end(body_block)
        stmt.body.accept(self)
        if not self._block_terminated(self.builder.block):
            self.builder.branch(header_block)

        self.builder.position_at_end(end_block)
        self._break_blocks.pop()
        self._continue_blocks.pop()

    def visit_until_stmt(self, stmt: UntilStmt) -> None:
        if self._current_func is None:
            raise LoweringError("until outside function")
        header_block = BasicBlock("until.header")
        body_block = BasicBlock("until.body")
        end_block = BasicBlock("until.end")
        self._current_func.append_block(header_block)
        self._current_func.append_block(body_block)
        self._current_func.append_block(end_block)

        self._break_blocks.append(end_block)
        self._continue_blocks.append(header_block)

        self.builder.branch(header_block)
        self.builder.position_at_end(header_block)
        cond = self._emit_expr(stmt.condition)
        self.builder.cond_branch(cond, end_block, body_block)

        self.builder.position_at_end(body_block)
        stmt.body.accept(self)
        if not self._block_terminated(self.builder.block):
            self.builder.branch(header_block)

        self.builder.position_at_end(end_block)
        self._break_blocks.pop()
        self._continue_blocks.pop()

    def visit_for_stmt(self, stmt: ForStmt) -> None:
        if self._current_func is None:
            raise LoweringError("for outside function")
        start_val = self._emit_expr(stmt.start)
        end_val = self._emit_expr(stmt.end)
        ir_type = self._ir_type(stmt.start)
        self._alloc_var(stmt.variable, ir_type)
        self._store_var(stmt.variable, start_val)

        header_block = BasicBlock("for.header")
        body_block = BasicBlock("for.body")
        step_end = BasicBlock("for.step")
        end_block = BasicBlock("for.end")
        self._current_func.append_block(header_block)
        self._current_func.append_block(body_block)
        self._current_func.append_block(step_end)
        self._current_func.append_block(end_block)

        self._break_blocks.append(end_block)
        self._continue_blocks.append(step_end)

        self.builder.branch(header_block)
        self.builder.position_at_end(header_block)
        var_val = self._load_var(stmt.variable)
        cond = self.builder.icmp(ICmpPredicate.SLT, var_val, end_val, "for.cond")
        self.builder.cond_branch(cond, body_block, end_block)

        self.builder.position_at_end(body_block)
        stmt.body.accept(self)
        if not self._block_terminated(self.builder.block):
            self.builder.branch(step_end)

        self.builder.position_at_end(step_end)
        var_val = self._load_var(stmt.variable)
        one = IntConstant(1, IntegerType(64))
        step = stmt.step.accept(self) if stmt.step else one
        inc = self.builder.add(var_val, step)
        self._store_var(stmt.variable, inc)
        self.builder.branch(header_block)

        self.builder.position_at_end(end_block)
        self._break_blocks.pop()
        self._continue_blocks.pop()

    def visit_for_each_stmt(self, stmt: ForEachStmt) -> None:
        if self._current_func is None:
            raise LoweringError("foreach outside function")
        self._emit_expr(stmt.iterable)
        header_block = BasicBlock("foreach.header")
        body_block = BasicBlock("foreach.body")
        end_block = BasicBlock("foreach.end")
        self._current_func.append_block(header_block)
        self._current_func.append_block(body_block)
        self._current_func.append_block(end_block)

        self._break_blocks.append(end_block)
        self._continue_blocks.append(header_block)

        iter_type = self._ir_type(stmt.iterable)
        self._alloc_var("__iter", iter_type)
        zero = IntConstant(0, IntegerType(64))
        max_val = IntConstant(100, IntegerType(64))
        self._alloc_var("__idx", IR_I64)
        self._store_var("__idx", zero)

        self.builder.branch(header_block)
        self.builder.position_at_end(header_block)
        idx = self._load_var("__idx")
        idx_cond = self.builder.icmp(ICmpPredicate.SLT, idx, max_val, "foreach.cond")
        self.builder.cond_branch(idx_cond, body_block, end_block)

        self.builder.position_at_end(body_block)
        elem_type = self._ir_type(stmt.element)
        self._alloc_var(stmt.element, elem_type)
        elem_val = self._load_var("__idx")
        self._store_var(stmt.element, elem_val)
        stmt.body.accept(self)

        for name in list(self._vars.keys()):
            if name.startswith("__"):
                continue
            if name not in self._vars:
                continue
        if not self._block_terminated(self.builder.block):
            idx = self._load_var("__idx")
            one = IntConstant(1, IntegerType(64))
            inc = self.builder.add(idx, one)
            self._store_var("__idx", inc)
            self.builder.branch(header_block)

        self.builder.position_at_end(end_block)
        self._break_blocks.pop()
        self._continue_blocks.pop()

    def visit_break_stmt(self, stmt: BreakStmt) -> None:
        if self._break_blocks:
            self.builder.branch(self._break_blocks[-1])

    def visit_continue_stmt(self, stmt: ContinueStmt) -> None:
        if self._continue_blocks:
            self.builder.branch(self._continue_blocks[-1])

    def visit_throw_stmt(self, stmt: ThrowStmt) -> None:
        self._emit_expr(stmt.value)
        self.builder.unreachable()

    def visit_try_stmt(self, stmt: TryStmt) -> None:
        stmt.try_body.accept(self)
        if stmt.catch_body:
            stmt.catch_body.accept(self)
        if stmt.finally_body:
            stmt.finally_body.accept(self)

    # ── Expressions ────────────────────────────────────────────

    def visit_literal_expr(self, expr: LiteralExpr) -> Value:
        val = expr.value
        if isinstance(val, bool):
            return BoolConstant(val)
        elif isinstance(val, int):
            return IntConstant(val, IR_I64)
        elif isinstance(val, float):
            return FloatConstant(val, IR_F64)
        elif isinstance(val, str):
            return StringConstant(val)
        elif val is None:
            zero = IntConstant(0, IR_I8)
            return zero
        return IntConstant(0, IR_I64)

    def visit_identifier_expr(self, expr: IdentifierExpr) -> Value:
        return self._load_var(expr.name)

    def visit_binary_expr(self, expr: BinaryExpr) -> Value:
        left = self._emit_expr(expr.left)
        right = self._emit_expr(expr.right)
        op = expr.operator
        name = self.builder._context.unique_name("binop")

        if op == '+':
            return self.builder.add(left, right, name)
        elif op == '-':
            return self.builder.sub(left, right, name)
        elif op == '*':
            return self.builder.mul(left, right, name)
        elif op == '/':
            return self.builder.sdiv(left, right, name)
        elif op == '%':
            return self.builder.srem(left, right, name)
        elif op == '==':
            return self.builder.icmp(ICmpPredicate.EQ, left, right, name)
        elif op == '!=':
            return self.builder.icmp(ICmpPredicate.NE, left, right, name)
        elif op == '<':
            return self.builder.icmp(ICmpPredicate.SLT, left, right, name)
        elif op == '<=':
            return self.builder.icmp(ICmpPredicate.SLE, left, right, name)
        elif op == '>':
            return self.builder.icmp(ICmpPredicate.SGT, left, right, name)
        elif op == '>=':
            return self.builder.icmp(ICmpPredicate.SGE, left, right, name)
        elif op == '&':
            return self.builder.and_(left, right, name)
        elif op == '|':
            return self.builder.or_(left, right, name)
        elif op == '^':
            return self.builder.xor(left, right, name)
        elif op == '<<':
            return self.builder.shl(left, right, name)
        elif op == '>>':
            return self.builder.ashr(left, right, name)
        raise LoweringError(f"Unknown binary operator '{op}' at {expr.location}")

    def visit_unary_expr(self, expr: UnaryExpr) -> Value:
        right = self._emit_expr(expr.right)
        op = expr.operator
        name = self.builder._context.unique_name("unary")
        if op == '-':
            return self.builder.neg(right, name)
        elif op == '!':
            return self.builder.not_(right, name)
        return right

    def visit_logical_expr(self, expr: LogicalExpr) -> Value:
        left = self._emit_expr(expr.left)
        op = expr.operator
        name = self.builder._context.unique_name("logical")

        if op == 'and':
            rhs_block = BasicBlock("logical.rhs")
            end_block = BasicBlock("logical.end")
            result = self.builder.phi(IR_I1, name)
            self.builder.cond_branch(left, rhs_block, end_block)
            self.builder.position_at_end(rhs_block)
            right = self._emit_expr(expr.right)
            if not self._block_terminated(self.builder.block):
                self.builder.branch(end_block)
            self.builder.position_at_end(end_block)
            result.add_incoming(left, self.builder.block)
            result.add_incoming(right, rhs_block)
            return result
        elif op == 'or':
            rhs_block = BasicBlock("logical.rhs")
            end_block = BasicBlock("logical.end")
            result = self.builder.phi(IR_I1, name)
            self.builder.cond_branch(left, end_block, rhs_block)
            self.builder.position_at_end(rhs_block)
            right = self._emit_expr(expr.right)
            if not self._block_terminated(self.builder.block):
                self.builder.branch(end_block)
            self.builder.position_at_end(end_block)
            result.add_incoming(left, self.builder.block)
            result.add_incoming(right, rhs_block)
            return result
        return left

    def visit_assignment_expr(self, expr: AssignmentExpr) -> Value:
        value = self._emit_expr(expr.value)
        if isinstance(expr.target, IdentifierExpr):
            self._store_var(expr.target.name, value)
        return value

    def visit_grouping_expr(self, expr: GroupingExpr) -> Value:
        return self._emit_expr(expr.expression)

    def visit_call_expr(self, expr: CallExpr) -> Value:
        callee = self._emit_expr(expr.callee)
        args = [self._emit_expr(a) for a in expr.arguments]
        ir_type = self._ir_type(expr)
        name = self.builder._context.unique_name("call")

        if isinstance(ir_type, IRFunctionType):
            return self.builder.call(ir_type, callee, args, name)
        ret_type = ir_type
        func_ptr_type = IRFunctionType(tuple(), ret_type)
        return self.builder.call(func_ptr_type, callee, args, name)

    def visit_method_call_expr(self, expr: MethodCallExpr) -> Value:
        obj = self._emit_expr(expr.object)
        args = [obj] + [self._emit_expr(a) for a in expr.arguments]
        ir_type = self._ir_type(expr)
        name = self.builder._context.unique_name("call")
        func_ptr_type = IRFunctionType(tuple(IR_I64 for _ in args), ir_type)
        return self.builder.call(func_ptr_type, obj, args, name)

    def visit_get_expr(self, expr: GetExpr) -> Value:
        obj = self._emit_expr(expr.object)
        name = self.builder._context.unique_name("get")
        return self.builder.gep(IR_I8, obj, [IntConstant(0, IR_I32)], name)

    def visit_set_expr(self, expr: SetExpr) -> Value:
        obj = self._emit_expr(expr.object)
        value = self._emit_expr(expr.value)
        ptr = self.builder.gep(IR_I8, obj, [IntConstant(0, IR_I32)])
        self.builder.store(value, ptr)
        return value

    def visit_index_expr(self, expr: IndexExpr) -> Value:
        obj = self._emit_expr(expr.object)
        idx = self._emit_expr(expr.index)
        name = self.builder._context.unique_name("index")
        elem_type = self._ir_type(expr)
        return self.builder.gep(elem_type, obj, [idx], name)

    def visit_slice_expr(self, expr: SliceExpr) -> Value:
        obj = self._emit_expr(expr.object)
        return obj

    def visit_self_expr(self, expr: SelfExpr) -> Value:
        return self._load_var("self")

    def visit_super_expr(self, expr: SuperExpr) -> Value:
        return self._load_var("self")

    def visit_list_expr(self, expr: ListExpr) -> Value:
        result = IntConstant(0, IR_I64)
        for elem in expr.elements:
            self._emit_expr(elem)
        return result

    def visit_dict_expr(self, expr: DictExpr) -> Value:
        result = IntConstant(0, IR_I64)
        return result

    def visit_tuple_expr(self, expr: TupleExpr) -> Value:
        if not expr.elements:
            return IntConstant(0, IR_I64)
        result = self._emit_expr(expr.elements[0])
        return result

    def visit_lambda_expr(self, expr: LambdaExpr) -> Value:
        return IntConstant(0, IR_I64)

    def visit_if_expr(self, expr: IfExpr) -> Value:
        cond = self._emit_expr(expr.condition)
        then_block = BasicBlock("ifexpr.then")
        else_block = BasicBlock("ifexpr.else")
        merge_block = BasicBlock("ifexpr.end")

        self.builder.cond_branch(cond, then_block, else_block)

        self.builder.position_at_end(then_block)
        then_val = self._emit_expr(expr.then_branch)
        if not isinstance(then_val, Value):
            then_val = IntConstant(0, IR_I64)
        if not self._block_terminated(self.builder.block):
            self.builder.branch(merge_block)

        self.builder.position_at_end(else_block)
        if expr.else_branch:
            else_val = self._emit_expr(expr.else_branch)
        else:
            else_val = IntConstant(0, IR_I64)
        if not isinstance(else_val, Value):
            else_val = IntConstant(0, IR_I64)
        if not self._block_terminated(self.builder.block):
            self.builder.branch(merge_block)

        self.builder.position_at_end(merge_block)
        result_type = self._ir_type(expr)
        name = self.builder._context.unique_name("ifexpr")
        phi = self.builder.phi(result_type, name)
        phi.add_incoming(then_val, then_block)
        phi.add_incoming(else_val, else_block)
        self._current_func.append_block(then_block)
        self._current_func.append_block(else_block)
        self._current_func.append_block(merge_block)
        return phi

    def visit_constructor_expr(self, expr: ConstructorExpr) -> Value:
        result = IntConstant(0, IR_I64)
        for arg in expr.arguments:
            self._emit_expr(arg)
        return result

    def visit_placeholder_expr(self, expr: PlaceholderExpr) -> Value:
        return IntConstant(0, IR_I64)

    # ── Parameter / Field ──────────────────────────────────────

    def visit_parameter(self, param: Parameter) -> None:
        pass

    def visit_struct_field(self, field: StructField) -> None:
        pass

    def visit_enum_variant(self, variant: EnumVariant) -> None:
        pass

    def visit_elif_branch(self, branch: ElifBranch) -> None:
        pass

    # ── Helpers ────────────────────────────────────────────────

    def _block_terminated(self, block) -> bool:
        if block is None:
            return False
        if not block.instructions:
            return False
        last = block.instructions[-1]
        return last.is_terminator

    def _trim_vars(self, target_len: int) -> None:
        keys = list(self._vars.keys())
        while len(self._vars) > target_len:
            del self._vars[keys[len(self._vars) - 1]]
