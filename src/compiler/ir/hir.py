"""
HIR — High-Level Intermediate Representation

The HIR preserves source-level semantics: functions, classes, modules,
namespaces, generics, traits, pattern matching, exceptions, and async.
HIR is the first IR produced after type checking and is the input to
MIR lowering.
"""
from __future__ import annotations

from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

from .module import IRModule
from .function import IRFunction
from .basic_block import BasicBlock
from .types import IRType
from .values import Value, Constant
from .instructions import Instruction

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple
    from .metadata import Metadata


# ══════════════════════════════════════════════════════════════════
# HIR Node Kinds
# ══════════════════════════════════════════════════════════════════


class HIRNodeKind(Enum):
    """Classification of HIR nodes."""
    MODULE = auto()
    FUNCTION = auto()
    CLASS = auto()
    STRUCT = auto()
    ENUM = auto()
    TRAIT = auto()
    INTERFACE = auto()
    VARIABLE = auto()
    CONSTANT = auto()
    PARAMETER = auto()
    BLOCK = auto()
    EXPRESSION = auto()
    STATEMENT = auto()
    PATTERN = auto()
    CLOSURE = auto()
    GENERIC = auto()
    ASSIGNMENT = auto()
    FOR = auto()
    FOR_EACH = auto()
    BREAK = auto()
    CONTINUE = auto()
    MATCH = auto()
    THROW = auto()
    TRY = auto()


# ══════════════════════════════════════════════════════════════════
# HIR Node (Abstract Base)
# ══════════════════════════════════════════════════════════════════


class HIRNode:
    """Base class for all HIR nodes."""
    __slots__ = ("_kind", "_source_ref", "_metadata")

    def __init__(self, kind: HIRNodeKind) -> None:
        object.__setattr__(self, "_kind", kind)
        object.__setattr__(self, "_source_ref", None)
        object.__setattr__(self, "_metadata", {})

    @property
    def kind(self) -> HIRNodeKind:
        return self._kind

    @property
    def source_ref(self):
        return self._source_ref

    @source_ref.setter
    def source_ref(self, ref) -> None:
        object.__setattr__(self, "_source_ref", ref)

    @property
    def metadata(self) -> dict:
        return self._metadata

    def __repr__(self) -> str:
        return f"HIRNode({self._kind.name})"


# ══════════════════════════════════════════════════════════════════
# HIR Declarations
# ══════════════════════════════════════════════════════════════════


class HIRModule(HIRNode):
    """HIR module — top-level container with source-level structure."""
    __slots__ = ("_name", "_functions", "_classes", "_traits",
                 "_imports", "_exports")

    def __init__(self, name: str = "") -> None:
        super().__init__(HIRNodeKind.MODULE)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_functions", [])
        object.__setattr__(self, "_classes", [])
        object.__setattr__(self, "_traits", [])
        object.__setattr__(self, "_imports", [])
        object.__setattr__(self, "_exports", [])

    @property
    def name(self) -> str:
        return self._name

    @property
    def functions(self) -> List[HIRFunctionDecl]:
        return list(self._functions)

    @property
    def classes(self) -> List[HIRClassDecl]:
        return list(self._classes)

    @property
    def traits(self) -> List[HIRTraitDecl]:
        return list(self._traits)

    def add_function(self, func: HIRFunctionDecl) -> None:
        self._functions.append(func)

    def add_class(self, cls: HIRClassDecl) -> None:
        self._classes.append(cls)

    def add_trait(self, trait: HIRTraitDecl) -> None:
        self._traits.append(trait)

    def __repr__(self) -> str:
        return (f"HIRModule({self._name}: "
                f"{len(self._functions)} funcs, "
                f"{len(self._classes)} classes)")


class HIRFunctionDecl(HIRNode):
    """HIR function declaration with full source-level information."""
    __slots__ = ("_name", "_params", "_return_type", "_body",
                 "_generic_params", "_is_async", "_is_pub")

    def __init__(
        self,
        name: str,
        params: Optional[List[HIRParameter]] = None,
        return_type: Optional[IRType] = None,
        body: Optional[HIRBlock] = None,
    ) -> None:
        super().__init__(HIRNodeKind.FUNCTION)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_params", list(params) if params else [])
        object.__setattr__(self, "_return_type", return_type)
        object.__setattr__(self, "_body", body)
        object.__setattr__(self, "_generic_params", [])
        object.__setattr__(self, "_is_async", False)
        object.__setattr__(self, "_is_pub", False)

    @property
    def name(self) -> str:
        return self._name

    @property
    def params(self) -> List[HIRParameter]:
        return list(self._params)

    @property
    def return_type(self) -> Optional[IRType]:
        return self._return_type

    @property
    def body(self) -> Optional[HIRBlock]:
        return self._body

    @property
    def generic_params(self) -> List:
        return list(self._generic_params)

    @property
    def is_async(self) -> bool:
        return self._is_async

    @property
    def is_pub(self) -> bool:
        return self._is_pub

    @property
    def is_declaration(self) -> bool:
        return self._body is None

    def __repr__(self) -> str:
        kind = "async " if self._is_async else ""
        return f"HIRFunction({kind}{self._name})"


class HIRParameter(HIRNode):
    """Function parameter with name, type, and optional default."""
    __slots__ = ("_name", "_type", "_default", "_is_variadic")

    def __init__(
        self,
        name: str,
        typ: Optional[IRType] = None,
        default: Optional[Constant] = None,
    ) -> None:
        super().__init__(HIRNodeKind.PARAMETER)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_type", typ)
        object.__setattr__(self, "_default", default)
        object.__setattr__(self, "_is_variadic", False)

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> Optional[IRType]:
        return self._type

    @property
    def default(self) -> Optional[Constant]:
        return self._default

    @property
    def has_default(self) -> bool:
        return self._default is not None


class HIRClassDecl(HIRNode):
    """HIR class declaration."""
    __slots__ = ("_name", "_fields", "_methods", "_parent",
                 "_implements", "_generic_params", "_is_abstract", "_is_pub")

    def __init__(self, name: str) -> None:
        super().__init__(HIRNodeKind.CLASS)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_fields", [])
        object.__setattr__(self, "_methods", [])
        object.__setattr__(self, "_parent", None)
        object.__setattr__(self, "_implements", [])
        object.__setattr__(self, "_generic_params", [])
        object.__setattr__(self, "_is_abstract", False)
        object.__setattr__(self, "_is_pub", False)

    @property
    def name(self) -> str:
        return self._name

    @property
    def fields(self) -> List:
        return list(self._fields)

    @property
    def methods(self) -> List[HIRFunctionDecl]:
        return list(self._methods)

    @property
    def parent(self) -> Optional[str]:
        return self._parent

    @property
    def implements(self) -> List[str]:
        return list(self._implements)

    @property
    def is_abstract(self) -> bool:
        return self._is_abstract

    def add_field(self, name: str, typ: IRType) -> None:
        self._fields.append((name, typ))

    def add_method(self, method: HIRFunctionDecl) -> None:
        self._methods.append(method)


class HIRTraitDecl(HIRNode):
    """HIR trait declaration."""
    __slots__ = ("_name", "_methods", "_required_traits", "_is_pub")

    def __init__(self, name: str) -> None:
        super().__init__(HIRNodeKind.TRAIT)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_methods", [])
        object.__setattr__(self, "_required_traits", [])
        object.__setattr__(self, "_is_pub", False)

    @property
    def name(self) -> str:
        return self._name

    @property
    def methods(self) -> List[HIRFunctionDecl]:
        return list(self._methods)

    def add_method(self, method: HIRFunctionDecl) -> None:
        self._methods.append(method)


# ══════════════════════════════════════════════════════════════════
# HIR Additional Declarations
# ══════════════════════════════════════════════════════════════════


class HIRBlock(HIRNode):
    """HIR block — sequence of statements."""
    __slots__ = ("_statements",)

    def __init__(self, statements: Optional[List[HIRStatement]] = None) -> None:
        super().__init__(HIRNodeKind.BLOCK)
        object.__setattr__(self, "_statements", list(statements) if statements else [])

    @property
    def statements(self) -> List[HIRStatement]:
        return list(self._statements)

    def add_statement(self, stmt: HIRStatement) -> None:
        self._statements.append(stmt)


class HIRStatement(HIRNode):
    """HIR statement — an executable unit."""
    __slots__ = ("_kind_name",)

    def __init__(self, kind: HIRNodeKind = HIRNodeKind.STATEMENT) -> None:
        super().__init__(kind)


class HIRReturn(HIRStatement):
    """Return statement."""
    __slots__ = ("_value",)

    def __init__(self, value: Optional[Value] = None) -> None:
        super().__init__()
        object.__setattr__(self, "_value", value)

    @property
    def value(self) -> Optional[Value]:
        return self._value


class HIRIf(HIRStatement):
    """If statement with optional else."""
    __slots__ = ("_condition", "_then_block", "_else_block")

    def __init__(
        self,
        condition: Value,
        then_block: HIRBlock,
        else_block: Optional[HIRBlock] = None,
    ) -> None:
        super().__init__()
        object.__setattr__(self, "_condition", condition)
        object.__setattr__(self, "_then_block", then_block)
        object.__setattr__(self, "_else_block", else_block)

    @property
    def condition(self) -> Value:
        return self._condition

    @property
    def then_block(self) -> HIRBlock:
        return self._then_block

    @property
    def else_block(self) -> Optional[HIRBlock]:
        return self._else_block


class HIRWhile(HIRStatement):
    """While loop."""
    __slots__ = ("_condition", "_body")

    def __init__(self, condition: Value, body: HIRBlock) -> None:
        super().__init__()
        object.__setattr__(self, "_condition", condition)
        object.__setattr__(self, "_body", body)

    @property
    def condition(self) -> Value:
        return self._condition

    @property
    def body(self) -> HIRBlock:
        return self._body


class HIREnumDecl(HIRNode):
    """HIR enum declaration."""
    __slots__ = ("_name", "_variants", "_is_pub")

    def __init__(self, name: str, variants: Optional[List] = None) -> None:
        super().__init__(HIRNodeKind.ENUM)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_variants", list(variants) if variants else [])
        object.__setattr__(self, "_is_pub", False)

    @property
    def name(self) -> str:
        return self._name

    @property
    def variants(self) -> List:
        return list(self._variants)

    @property
    def is_pub(self) -> bool:
        return self._is_pub


class HIRInterfaceDecl(HIRNode):
    """HIR interface declaration (alias for trait)."""
    __slots__ = ("_name", "_methods", "_is_pub")

    def __init__(self, name: str) -> None:
        super().__init__(HIRNodeKind.INTERFACE)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_methods", [])
        object.__setattr__(self, "_is_pub", False)

    @property
    def name(self) -> str:
        return self._name

    @property
    def methods(self) -> List[HIRFunctionDecl]:
        return list(self._methods)

    def add_method(self, method: HIRFunctionDecl) -> None:
        self._methods.append(method)

    @property
    def is_pub(self) -> bool:
        return self._is_pub


class HIRVariable(HIRStatement):
    """Variable declaration."""
    __slots__ = ("_name", "_type", "_init_value", "_is_const", "_is_mut")

    def __init__(
        self,
        name: str,
        typ: Optional[IRType] = None,
        init_value: Optional[Value] = None,
        is_const: bool = False,
        is_mut: bool = False,
    ) -> None:
        super().__init__(HIRNodeKind.VARIABLE)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_type", typ)
        object.__setattr__(self, "_init_value", init_value)
        object.__setattr__(self, "_is_const", is_const)
        object.__setattr__(self, "_is_mut", is_mut)

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> Optional[IRType]:
        return self._type

    @property
    def init_value(self) -> Optional[Value]:
        return self._init_value

    @property
    def is_const(self) -> bool:
        return self._is_const

    @property
    def is_mut(self) -> bool:
        return self._is_mut


class HIRConstant(HIRStatement):
    """Constant declaration."""
    __slots__ = ("_name", "_type", "_value")

    def __init__(
        self,
        name: str,
        typ: Optional[IRType] = None,
        value: Optional[Value] = None,
    ) -> None:
        super().__init__(HIRNodeKind.CONSTANT)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_type", typ)
        object.__setattr__(self, "_value", value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> Optional[IRType]:
        return self._type

    @property
    def value(self) -> Optional[Value]:
        return self._value


class HIRAssignment(HIRStatement):
    """Assignment statement."""
    __slots__ = ("_target", "_value")

    def __init__(self, target: str, value: Value) -> None:
        super().__init__(HIRNodeKind.ASSIGNMENT)
        object.__setattr__(self, "_target", target)
        object.__setattr__(self, "_value", value)

    @property
    def target(self) -> str:
        return self._target

    @property
    def value(self) -> Value:
        return self._value


class HIRFor(HIRStatement):
    """For loop."""
    __slots__ = ("_variable", "_iterable", "_body")

    def __init__(
        self,
        variable: str,
        iterable: Value,
        body: HIRBlock,
    ) -> None:
        super().__init__(HIRNodeKind.FOR)
        object.__setattr__(self, "_variable", variable)
        object.__setattr__(self, "_iterable", iterable)
        object.__setattr__(self, "_body", body)

    @property
    def variable(self) -> str:
        return self._variable

    @property
    def iterable(self) -> Value:
        return self._iterable

    @property
    def body(self) -> HIRBlock:
        return self._body


class HIRForEach(HIRStatement):
    """For-each loop."""
    __slots__ = ("_variable", "_iterable", "_body")

    def __init__(
        self,
        variable: str,
        iterable: Value,
        body: HIRBlock,
    ) -> None:
        super().__init__(HIRNodeKind.FOR_EACH)
        object.__setattr__(self, "_variable", variable)
        object.__setattr__(self, "_iterable", iterable)
        object.__setattr__(self, "_body", body)

    @property
    def variable(self) -> str:
        return self._variable

    @property
    def iterable(self) -> Value:
        return self._iterable

    @property
    def body(self) -> HIRBlock:
        return self._body


class HIRBreak(HIRStatement):
    """Break statement."""
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(HIRNodeKind.BREAK)


class HIRContinue(HIRStatement):
    """Continue statement."""
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__(HIRNodeKind.CONTINUE)


class HIRExpression(HIRStatement):
    """Expression statement."""
    __slots__ = ("_expression",)

    def __init__(self, expression: Value) -> None:
        super().__init__(HIRNodeKind.EXPRESSION)
        object.__setattr__(self, "_expression", expression)

    @property
    def expression(self) -> Value:
        return self._expression


class HIRMatch(HIRStatement):
    """Pattern matching."""
    __slots__ = ("_value", "_cases")

    def __init__(self, value: Value, cases: Optional[List] = None) -> None:
        super().__init__(HIRNodeKind.MATCH)
        object.__setattr__(self, "_value", value)
        object.__setattr__(self, "_cases", list(cases) if cases else [])

    @property
    def value(self) -> Value:
        return self._value

    @property
    def cases(self) -> List:
        return list(self._cases)


class HIRThrow(HIRStatement):
    """Throw exception."""
    __slots__ = ("_value",)

    def __init__(self, value: Optional[Value] = None) -> None:
        super().__init__(HIRNodeKind.THROW)
        object.__setattr__(self, "_value", value)

    @property
    def value(self) -> Optional[Value]:
        return self._value


class HIRTry(HIRStatement):
    """Try-catch block."""
    __slots__ = ("_try_body", "_catch_clauses", "_finally_body")

    def __init__(
        self,
        try_body: HIRBlock,
        catch_clauses: Optional[List] = None,
        finally_body: Optional[HIRBlock] = None,
    ) -> None:
        super().__init__(HIRNodeKind.TRY)
        object.__setattr__(self, "_try_body", try_body)
        object.__setattr__(self, "_catch_clauses", list(catch_clauses) if catch_clauses else [])
        object.__setattr__(self, "_finally_body", finally_body)

    @property
    def try_body(self) -> HIRBlock:
        return self._try_body

    @property
    def catch_clauses(self) -> List:
        return list(self._catch_clauses)

    @property
    def finally_body(self) -> Optional[HIRBlock]:
        return self._finally_body


# ══════════════════════════════════════════════════════════════════
# HIR → Module Bridge
# ══════════════════════════════════════════════════════════════════


def hir_to_ir_module(hir: HIRModule) -> IRModule:
    """Convert an HIR module to an IR module with full body lowering."""
    module = IRModule(hir.name)
    for hir_func in hir.functions:
        from .types import IRFunctionType, IRVoid
        param_types = tuple(
            p.type or IRVoid() for p in hir_func.params
        )
        ret_type = hir_func.return_type or IRVoid()
        func_type = IRFunctionType(param_types, ret_type)
        ir_func = IRFunction(hir_func.name, func_type)
        module.add_function(ir_func)

        if not hir_func.is_declaration and hir_func.body is not None:
            _lower_body(ir_func, hir_func.body)

    return module


def _lower_body(ir_func: IRFunction, hir_body: HIRBlock) -> None:
    """Lower an HIR function body into IR basic blocks and instructions."""
    from .builder import IRBuilder
    from .context import IRContext

    ctx = IRContext()
    builder = IRBuilder(ctx)
    variables = {}
    loop_stack = []

    entry = builder.create_block("entry")
    ir_func.append_block(entry)
    builder.position_at_end(entry)

    _lower_block(builder, ir_func, hir_body, variables, loop_stack)

    if builder.block is not None and builder.block.terminator is None:
        if ir_func.return_type.is_void:
            builder.ret()
        else:
            builder.unreachable()


def _lower_block(
    builder: IRBuilder,
    ir_func: IRFunction,
    hir_block: HIRBlock,
    variables: dict,
    loop_stack: list,
) -> None:
    """Lower all statements in an HIR block."""
    for stmt in hir_block.statements:
        if builder.block is not None and builder.block.terminator is not None:
            break
        _lower_statement(builder, ir_func, stmt, variables, loop_stack)


def _lower_statement(
    builder: IRBuilder,
    ir_func: IRFunction,
    stmt: HIRStatement,
    variables: dict,
    loop_stack: list,
) -> None:
    """Lower a single HIR statement to IR instructions."""
    if isinstance(stmt, HIRReturn):
        _lower_return(builder, stmt)
    elif isinstance(stmt, HIRIf):
        _lower_if(builder, ir_func, stmt, variables, loop_stack)
    elif isinstance(stmt, HIRWhile):
        _lower_while(builder, ir_func, stmt, variables, loop_stack)
    elif isinstance(stmt, HIRVariable):
        _lower_variable(builder, stmt, variables)
    elif isinstance(stmt, HIRAssignment):
        _lower_assignment(builder, stmt, variables)
    elif isinstance(stmt, HIRBreak):
        _lower_break(builder, loop_stack)
    elif isinstance(stmt, HIRContinue):
        _lower_continue(builder, loop_stack)
    elif isinstance(stmt, HIRExpression):
        pass
    elif isinstance(stmt, HIRMatch):
        pass
    elif isinstance(stmt, HIRThrow):
        _lower_throw(builder)
    elif isinstance(stmt, HIRTry):
        pass


def _lower_return(builder: IRBuilder, stmt: HIRReturn) -> None:
    if stmt.value is not None:
        builder.ret(stmt.value)
    else:
        builder.ret()


def _lower_if(
    builder: IRBuilder,
    ir_func: IRFunction,
    stmt: HIRIf,
    variables: dict,
    loop_stack: list,
) -> None:
    from .instructions import TerminatorInst

    cond = stmt.condition
    has_else = stmt.else_block is not None

    then_bb = builder.create_block("if.then")
    else_bb = builder.create_block("if.else") if has_else else None
    merge_bb = builder.create_block("if.end")

    if has_else:
        builder.cond_branch(cond, then_bb, else_bb)
    else:
        builder.cond_branch(cond, then_bb, merge_bb)

    builder.position_at_end(then_bb)
    _lower_block(builder, ir_func, stmt.then_block, variables, loop_stack)
    if not (builder.block and builder.block.terminator is not None):
        builder.branch(merge_bb)

    if has_else:
        builder.position_at_end(else_bb)
        _lower_block(builder, ir_func, stmt.else_block, variables, loop_stack)
        if not (builder.block and builder.block.terminator is not None):
            builder.branch(merge_bb)

    builder.position_at_end(merge_bb)


def _lower_while(
    builder: IRBuilder,
    ir_func: IRFunction,
    stmt: HIRWhile,
    variables: dict,
    loop_stack: list,
) -> None:
    header_bb = builder.create_block("while.cond")
    body_bb = builder.create_block("while.body")
    exit_bb = builder.create_block("while.end")

    builder.branch(header_bb)

    builder.position_at_end(header_bb)
    builder.cond_branch(stmt.condition, body_bb, exit_bb)

    loop_stack.append((header_bb, exit_bb))
    builder.position_at_end(body_bb)
    _lower_block(builder, ir_func, stmt.body, variables, loop_stack)
    if not (builder.block and builder.block.terminator is not None):
        builder.branch(header_bb)
    loop_stack.pop()

    builder.position_at_end(exit_bb)


def _lower_variable(
    builder: IRBuilder,
    stmt: HIRVariable,
    variables: dict,
) -> None:
    from .types import IRVoid

    typ = stmt.type or IRVoid()
    alloca_inst = builder.alloca(typ, stmt.name)
    variables[stmt.name] = alloca_inst
    if stmt.init_value is not None:
        builder.store(stmt.init_value, alloca_inst)


def _lower_assignment(
    builder: IRBuilder,
    stmt: HIRAssignment,
    variables: dict,
) -> None:
    ptr = variables.get(stmt.target)
    if ptr is not None:
        builder.store(stmt.value, ptr)


def _lower_break(builder: IRBuilder, loop_stack: list) -> None:
    if loop_stack:
        _, exit_bb = loop_stack[-1]
        builder.branch(exit_bb)


def _lower_continue(builder: IRBuilder, loop_stack: list) -> None:
    if loop_stack:
        header_bb, _ = loop_stack[-1]
        builder.branch(header_bb)


def _lower_throw(builder: IRBuilder) -> None:
    builder.unreachable()
