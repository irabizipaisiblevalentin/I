"""
AST Node Definitions for the I Programming Language

Complete, immutable, extensible AST framework.
Each node includes source location, unique ID, type enum, and visitor pattern.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple

from ..lexer.token import Token


# ══════════════════════════════════════════════════════════════════
# Node Type Enumeration
# ══════════════════════════════════════════════════════════════════


class NodeType(Enum):
    """Enumeration of all AST node types."""

    # Root
    PROGRAM = auto()
    MODULE = auto()

    # Declarations
    VAR_DECL = auto()
    METHOD_DECL = auto()
    FUNCTION_DECL = auto()
    STRUCT_DECL = auto()
    ENUM_DECL = auto()
    CLASS_DECL = auto()
    TRAIT_DECL = auto()
    INTERFACE_DECL = auto()
    TYPE_ALIAS_DECL = auto()
    IMPORT_DECL = auto()
    EXPORT_DECL = auto()

    # Statements
    BLOCK_STMT = auto()
    IF_STMT = auto()
    WHILE_STMT = auto()
    UNTIL_STMT = auto()
    FOR_STMT = auto()
    FOR_EACH_STMT = auto()
    RETURN_STMT = auto()
    BREAK_STMT = auto()
    CONTINUE_STMT = auto()
    THROW_STMT = auto()
    TRY_STMT = auto()
    EXPRESSION_STMT = auto()
    EMPTY_STMT = auto()

    # Expressions
    LITERAL_EXPR = auto()
    IDENTIFIER_EXPR = auto()
    BINARY_EXPR = auto()
    UNARY_EXPR = auto()
    LOGICAL_EXPR = auto()
    ASSIGNMENT_EXPR = auto()
    COMPOUND_ASSIGNMENT_EXPR = auto()
    CALL_EXPR = auto()
    METHOD_CALL_EXPR = auto()
    CONSTRUCTOR_EXPR = auto()
    PLACEHOLDER_EXPR = auto()
    GET_EXPR = auto()
    SET_EXPR = auto()
    INDEX_EXPR = auto()
    SLICE_EXPR = auto()
    SELF_EXPR = auto()
    SUPER_EXPR = auto()
    LIST_EXPR = auto()
    DICT_EXPR = auto()
    TUPLE_EXPR = auto()
    LAMBDA_EXPR = auto()
    IF_EXPR = auto()
    GROUPING_EXPR = auto()

    # Types
    NAMED_TYPE = auto()
    GENERIC_TYPE = auto()
    FUNCTION_TYPE = auto()
    OPTIONAL_TYPE = auto()
    TUPLE_TYPE = auto()


# ══════════════════════════════════════════════════════════════════
# Source Location
# ══════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class SourceLocation:
    """Source file location with full metadata."""

    file: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    start_offset: int = 0
    end_offset: int = 0

    @classmethod
    def from_token(cls, token: Token, file: str = "<input>") -> SourceLocation:
        """Create from a token."""
        return cls(
            file=file,
            start_line=token.line,
            start_column=token.column,
            end_line=token.line,
            end_column=token.column + token.span,
            start_offset=token.offset,
            end_offset=token.offset + token.span,
        )

    @classmethod
    def merge(cls, start: SourceLocation, end: SourceLocation) -> SourceLocation:
        """Merge two locations."""
        return cls(
            file=start.file,
            start_line=start.start_line,
            start_column=start.start_column,
            end_line=end.end_line,
            end_column=end.end_column,
            start_offset=start.start_offset,
            end_offset=end.end_offset,
        )

    @property
    def line_count(self) -> int:
        """Number of lines spanned."""
        return self.end_line - self.start_line + 1

    def __str__(self) -> str:
        if self.start_line == self.end_line:
            return f"{self.file}:{self.start_line}:{self.start_column}"
        return f"{self.file}:{self.start_line}:{self.start_column}-{self.end_line}:{self.end_column}"


# ══════════════════════════════════════════════════════════════════
# Node ID Generator
# ══════════════════════════════════════════════════════════════════


class _NodeIDGenerator:
    """Thread-safe node ID generator."""

    def __init__(self) -> None:
        self._counter = 0

    def next(self) -> int:
        self._counter += 1
        return self._counter

    def reset(self) -> None:
        self._counter = 0


_node_id_gen = _NodeIDGenerator()


def _next_node_id() -> int:
    """Get next unique node ID."""
    return _node_id_gen.next()


# ══════════════════════════════════════════════════════════════════
# Base Classes
# ══════════════════════════════════════════════════════════════════


@dataclass(kw_only=True)
class ASTNode(ABC):
    """
    Base class for all AST nodes.
    
    Every node has:
    - Unique ID for tracking
    - Node type enum
    - Source location
    - Metadata dictionary for compiler passes
    """

    node_id: int = field(default_factory=_next_node_id)
    location: SourceLocation = field(default_factory=lambda: SourceLocation("<input>", 0, 0, 0, 0))
    metadata: Dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def node_type(self) -> NodeType:
        """Get the node type."""
        raise NotImplementedError

    @abstractmethod
    def accept(self, visitor: ASTVisitor) -> Any:
        """Accept a visitor."""
        ...

    @abstractmethod
    def children(self) -> List[ASTNode]:
        """Get child nodes."""
        ...

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata value."""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value."""
        return self.metadata.get(key, default)


@dataclass
class Expr(ASTNode):
    """Base class for expression nodes."""

    @property
    def is_lvalue(self) -> bool:
        """Check if this expression can be assigned to."""
        return isinstance(self, (IdentifierExpr, GetExpr, IndexExpr))


@dataclass
class Stmt(ASTNode):
    """Base class for statement nodes."""
    pass


@dataclass
class Decl(Stmt):
    """Base class for declaration nodes."""
    pass


@dataclass
class TypeNode(ASTNode):
    """Base class for type nodes."""
    pass


# ══════════════════════════════════════════════════════════════════
# Expression Nodes
# ══════════════════════════════════════════════════════════════════


@dataclass
class LiteralExpr(Expr):
    """Literal: integer, float, string, char, bool, null."""

    value: Any
    token_type: TokenType = field(default=None)

    @property
    def node_type(self) -> NodeType:
        return NodeType.LITERAL_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_literal_expr(self)

    def children(self) -> List[ASTNode]:
        return []


@dataclass
class IdentifierExpr(Expr):
    """Identifier reference."""

    name: str

    @property
    def node_type(self) -> NodeType:
        return NodeType.IDENTIFIER_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_identifier_expr(self)

    def children(self) -> List[ASTNode]:
        return []


@dataclass
class UnaryExpr(Expr):
    """Unary expression: op right."""

    operator: str
    right: Expr

    @property
    def node_type(self) -> NodeType:
        return NodeType.UNARY_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_unary_expr(self)

    def children(self) -> List[ASTNode]:
        return [self.right]


@dataclass
class BinaryExpr(Expr):
    """Binary expression: left op right."""

    left: Expr
    operator: str
    right: Expr

    @property
    def node_type(self) -> NodeType:
        return NodeType.BINARY_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_binary_expr(self)

    def children(self) -> List[ASTNode]:
        return [self.left, self.right]


@dataclass
class LogicalExpr(Expr):
    """Logical expression: left and/or right."""

    left: Expr
    operator: str
    right: Expr

    @property
    def node_type(self) -> NodeType:
        return NodeType.LOGICAL_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_logical_expr(self)

    def children(self) -> List[ASTNode]:
        return [self.left, self.right]


@dataclass
class AssignmentExpr(Expr):
    """Assignment: target = value."""

    target: Expr
    value: Expr

    @property
    def node_type(self) -> NodeType:
        return NodeType.ASSIGNMENT_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_assignment_expr(self)

    def children(self) -> List[ASTNode]:
        return [self.target, self.value]


@dataclass
class CompoundAssignmentExpr(Expr):
    """Compound assignment: target op= value."""

    target: Expr
    operator: str
    value: Expr

    @property
    def node_type(self) -> NodeType:
        return NodeType.COMPOUND_ASSIGNMENT_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_compound_assignment_expr(self)

    def children(self) -> List[ASTNode]:
        return [self.target, self.value]


@dataclass
class CallExpr(Expr):
    """Function call: callee(args)."""

    callee: Expr
    arguments: List[Expr]

    @property
    def node_type(self) -> NodeType:
        return NodeType.CALL_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_call_expr(self)

    def children(self) -> List[ASTNode]:
        return [self.callee] + self.arguments


@dataclass
class MethodCallExpr(Expr):
    """Method call: object.method(args)."""

    object: Expr
    method: str
    arguments: List[Expr]

    @property
    def node_type(self) -> NodeType:
        return NodeType.METHOD_CALL_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_method_call_expr(self)

    def children(self) -> List[ASTNode]:
        return [self.object] + self.arguments


@dataclass
class ConstructorExpr(Expr):
    """Object construction: gukora ClassName(args)."""

    class_name: str
    arguments: List[Expr]

    @property
    def node_type(self) -> NodeType:
        return NodeType.CONSTRUCTOR_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_constructor_expr(self)

    def children(self) -> List[ASTNode]:
        return list(self.arguments)


@dataclass
class GetExpr(Expr):
    """Property access: object.property."""

    object: Expr
    property: str

    @property
    def node_type(self) -> NodeType:
        return NodeType.GET_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_get_expr(self)

    def children(self) -> List[ASTNode]:
        return [self.object]


@dataclass
class SetExpr(Expr):
    """Property assignment: object.property = value."""

    object: Expr
    property: str
    value: Expr

    @property
    def node_type(self) -> NodeType:
        return NodeType.SET_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_set_expr(self)

    def children(self) -> List[ASTNode]:
        return [self.object, self.value]


@dataclass
class IndexExpr(Expr):
    """Index access: object[index]."""

    object: Expr
    index: Expr

    @property
    def node_type(self) -> NodeType:
        return NodeType.INDEX_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_index_expr(self)

    def children(self) -> List[ASTNode]:
        return [self.object, self.index]


@dataclass
class SliceExpr(Expr):
    """Slice: object[start:end]."""

    object: Expr
    start: Optional[Expr]
    end: Optional[Expr]

    @property
    def node_type(self) -> NodeType:
        return NodeType.SLICE_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_slice_expr(self)

    def children(self) -> List[ASTNode]:
        result = [self.object]
        if self.start:
            result.append(self.start)
        if self.end:
            result.append(self.end)
        return result


@dataclass
class SelfExpr(Expr):
    """Self reference."""

    @property
    def node_type(self) -> NodeType:
        return NodeType.SELF_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_self_expr(self)

    def children(self) -> List[ASTNode]:
        return []


@dataclass
class SuperExpr(Expr):
    """Super reference: super.method."""

    method: str

    @property
    def node_type(self) -> NodeType:
        return NodeType.SUPER_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_super_expr(self)

    def children(self) -> List[ASTNode]:
        return []


@dataclass
class ListExpr(Expr):
    """List literal: [elements]."""

    elements: List[Expr]

    @property
    def node_type(self) -> NodeType:
        return NodeType.LIST_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_list_expr(self)

    def children(self) -> List[ASTNode]:
        return list(self.elements)


@dataclass
class DictExpr(Expr):
    """Dict literal: {key: value}."""

    keys: List[Expr]
    values: List[Expr]

    @property
    def node_type(self) -> NodeType:
        return NodeType.DICT_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_dict_expr(self)

    def children(self) -> List[ASTNode]:
        result = []
        for k, v in zip(self.keys, self.values):
            result.extend([k, v])
        return result


@dataclass
class TupleExpr(Expr):
    """Tuple literal: (elements)."""

    elements: List[Expr]

    @property
    def node_type(self) -> NodeType:
        return NodeType.TUPLE_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_tuple_expr(self)

    def children(self) -> List[ASTNode]:
        return list(self.elements)


@dataclass
class LambdaExpr(Expr):
    """Lambda: (params) => body."""

    parameters: List[Parameter]
    body: Expr

    @property
    def node_type(self) -> NodeType:
        return NodeType.LAMBDA_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_lambda_expr(self)

    def children(self) -> List[ASTNode]:
        return list(self.parameters) + [self.body]


@dataclass
class IfExpr(Expr):
    """If expression: niba cond kora expr iherezo."""

    condition: Expr
    then_branch: Expr
    else_branch: Optional[Expr]

    @property
    def node_type(self) -> NodeType:
        return NodeType.IF_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_if_expr(self)

    def children(self) -> List[ASTNode]:
        result = [self.condition, self.then_branch]
        if self.else_branch:
            result.append(self.else_branch)
        return result


@dataclass
class GroupingExpr(Expr):
    """Grouping: (expression)."""

    expression: Expr

    @property
    def node_type(self) -> NodeType:
        return NodeType.GROUPING_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_grouping_expr(self)

    def children(self) -> List[ASTNode]:
        return [self.expression]


@dataclass
class PlaceholderExpr(Expr):
    """Placeholder for future extension or incomplete parsing."""

    description: str = ""

    @property
    def node_type(self) -> NodeType:
        return NodeType.PLACEHOLDER_EXPR

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_placeholder_expr(self)

    def children(self) -> List[ASTNode]:
        return []


# Need to import TokenType for LiteralExpr
from ..lexer.token import TokenType


# ══════════════════════════════════════════════════════════════════
# Type Nodes
# ══════════════════════════════════════════════════════════════════


@dataclass
class NamedType(TypeNode):
    """Named type reference."""

    name: str

    @property
    def node_type(self) -> NodeType:
        return NodeType.NAMED_TYPE

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_named_type(self)

    def children(self) -> List[ASTNode]:
        return []


@dataclass
class GenericType(TypeNode):
    """Generic type: name<T>."""

    name: str
    type_args: List[TypeNode]

    @property
    def node_type(self) -> NodeType:
        return NodeType.GENERIC_TYPE

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_generic_type(self)

    def children(self) -> List[ASTNode]:
        return list(self.type_args)


@dataclass
class FunctionType(TypeNode):
    """Function type: (params) -> return_type."""

    params: List[TypeNode]
    return_type: TypeNode

    @property
    def node_type(self) -> NodeType:
        return NodeType.FUNCTION_TYPE

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_function_type(self)

    def children(self) -> List[ASTNode]:
        return list(self.params) + [self.return_type]


@dataclass
class OptionalType(TypeNode):
    """Optional type: T?."""

    inner: TypeNode

    @property
    def node_type(self) -> NodeType:
        return NodeType.OPTIONAL_TYPE

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_optional_type(self)

    def children(self) -> List[ASTNode]:
        return [self.inner]


@dataclass
class TupleType(TypeNode):
    """Tuple type: (T1, T2, ...)."""

    elements: List[TypeNode]

    @property
    def node_type(self) -> NodeType:
        return NodeType.TUPLE_TYPE

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_tuple_type(self)

    def children(self) -> List[ASTNode]:
        return list(self.elements)


# ══════════════════════════════════════════════════════════════════
# Parameter & Field Types
# ══════════════════════════════════════════════════════════════════


@dataclass
class Parameter(ASTNode):
    """Function parameter."""

    name: str
    type_annotation: Optional[TypeNode] = None
    default: Optional[Expr] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_parameter(self)

    def children(self) -> List[ASTNode]:
        result = []
        if self.type_annotation:
            result.append(self.type_annotation)
        if self.default:
            result.append(self.default)
        return result


@dataclass
class StructField(ASTNode):
    """Struct field."""

    name: str
    type_annotation: TypeNode
    default: Optional[Expr] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_struct_field(self)

    def children(self) -> List[ASTNode]:
        result = [self.type_annotation]
        if self.default:
            result.append(self.default)
        return result


@dataclass
class EnumVariant(ASTNode):
    """Enum variant."""

    name: str
    value: Optional[Expr] = None

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_enum_variant(self)

    def children(self) -> List[ASTNode]:
        return [self.value] if self.value else []


@dataclass
class ElifBranch(ASTNode):
    """Single elif branch."""

    condition: Expr
    body: BlockStmt

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_elif_branch(self)

    def children(self) -> List[ASTNode]:
        return [self.condition, self.body]


# ══════════════════════════════════════════════════════════════════
# Declaration Nodes
# ══════════════════════════════════════════════════════════════════


@dataclass
class VarDecl(Decl):
    """Variable declaration: shyira name = value."""

    name: str
    type_annotation: Optional[TypeNode]
    initializer: Optional[Expr]
    is_const: bool = False

    @property
    def node_type(self) -> NodeType:
        return NodeType.VAR_DECL

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_var_decl(self)

    def children(self) -> List[ASTNode]:
        result = []
        if self.type_annotation:
            result.append(self.type_annotation)
        if self.initializer:
            result.append(self.initializer)
        return result


@dataclass
class FunctionDecl(Decl):
    """Function: umurimo name(params) return_type body."""

    name: str
    parameters: List[Parameter]
    return_type: Optional[TypeNode]
    body: BlockStmt

    @property
    def node_type(self) -> NodeType:
        return NodeType.FUNCTION_DECL

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_function_decl(self)

    def children(self) -> List[ASTNode]:
        result = list(self.parameters)
        if self.return_type:
            result.append(self.return_type)
        result.append(self.body)
        return result


@dataclass
class StructDecl(Decl):
    """Struct: igiceri name kora fields iherezo."""

    name: str
    fields: List[StructField]
    methods: List[FunctionDecl]

    @property
    def node_type(self) -> NodeType:
        return NodeType.STRUCT_DECL

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_struct_decl(self)

    def children(self) -> List[ASTNode]:
        return list(self.fields) + list(self.methods)


@dataclass
class EnumDecl(Decl):
    """Enum: ikindi name kora variants iherezo."""

    name: str
    variants: List[EnumVariant]

    @property
    def node_type(self) -> NodeType:
        return NodeType.ENUM_DECL

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_enum_decl(self)

    def children(self) -> List[ASTNode]:
        return list(self.variants)


@dataclass
class ClassDecl(Decl):
    """Class: urwego name [kugira parent] kora members iherezo."""

    name: str
    parent: Optional[str]
    members: List[Decl]

    @property
    def node_type(self) -> NodeType:
        return NodeType.CLASS_DECL

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_class_decl(self)

    def children(self) -> List[ASTNode]:
        return list(self.members)


@dataclass
class TraitDecl(Decl):
    """Trait: urubingo name kora members iherezo."""

    name: str
    members: List[Decl]

    @property
    def node_type(self) -> NodeType:
        return NodeType.TRAIT_DECL

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_trait_decl(self)

    def children(self) -> List[ASTNode]:
        return list(self.members)


@dataclass
class InterfaceDecl(Decl):
    """Interface: akabuto name kora members iherezo."""

    name: str
    members: List[Decl]

    @property
    def node_type(self) -> NodeType:
        return NodeType.INTERFACE_DECL

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_interface_decl(self)

    def children(self) -> List[ASTNode]:
        return list(self.members)


@dataclass
class ImportDecl(Decl):
    """Import: shyiramo path [kugira_ngo alias]."""

    path: str
    alias: Optional[str] = None

    @property
    def node_type(self) -> NodeType:
        return NodeType.IMPORT_DECL

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_import_decl(self)

    def children(self) -> List[ASTNode]:
        return []


@dataclass
class ExportDecl(Decl):
    """Export: tanga name."""

    name: str

    @property
    def node_type(self) -> NodeType:
        return NodeType.EXPORT_DECL

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_export_decl(self)

    def children(self) -> List[ASTNode]:
        return []


@dataclass
class MethodDecl(Decl):
    """Method declaration: object.method(params) return_type body."""

    name: str
    parameters: List[Parameter]
    return_type: Optional[TypeNode]
    body: BlockStmt
    is_static: bool = False

    @property
    def node_type(self) -> NodeType:
        return NodeType.METHOD_DECL

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_method_decl(self)

    def children(self) -> List[ASTNode]:
        result = list(self.parameters)
        if self.return_type:
            result.append(self.return_type)
        result.append(self.body)
        return result


# ══════════════════════════════════════════════════════════════════
# Statement Nodes
# ══════════════════════════════════════════════════════════════════


@dataclass
class BlockStmt(Stmt):
    """Block: kora stmts iherezo."""

    statements: List[Stmt]

    @property
    def node_type(self) -> NodeType:
        return NodeType.BLOCK_STMT

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_block_stmt(self)

    def children(self) -> List[ASTNode]:
        return list(self.statements)


@dataclass
class IfStmt(Stmt):
    """If/elif/else."""

    condition: Expr
    then_branch: BlockStmt
    elif_branches: List[ElifBranch]
    else_branch: Optional[BlockStmt]

    @property
    def node_type(self) -> NodeType:
        return NodeType.IF_STMT

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_if_stmt(self)

    def children(self) -> List[ASTNode]:
        result = [self.condition, self.then_branch]
        result.extend(self.elif_branches)
        if self.else_branch:
            result.append(self.else_branch)
        return result


@dataclass
class WhileStmt(Stmt):
    """While loop."""

    condition: Expr
    body: BlockStmt

    @property
    def node_type(self) -> NodeType:
        return NodeType.WHILE_STMT

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_while_stmt(self)

    def children(self) -> List[ASTNode]:
        return [self.condition, self.body]


@dataclass
class UntilStmt(Stmt):
    """Until loop."""

    condition: Expr
    body: BlockStmt

    @property
    def node_type(self) -> NodeType:
        return NodeType.UNTIL_STMT

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_until_stmt(self)

    def children(self) -> List[ASTNode]:
        return [self.condition, self.body]


@dataclass
class ForStmt(Stmt):
    """For loop: kuri var = start kugeza end."""

    variable: str
    start: Expr
    end: Expr
    step: Optional[Expr]
    body: BlockStmt

    @property
    def node_type(self) -> NodeType:
        return NodeType.FOR_STMT

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_for_stmt(self)

    def children(self) -> List[ASTNode]:
        result = [self.start, self.end]
        if self.step:
            result.append(self.step)
        result.append(self.body)
        return result


@dataclass
class ForEachStmt(Stmt):
    """For-each loop: buri element muri iterable."""

    element: str
    iterable: Expr
    body: BlockStmt

    @property
    def node_type(self) -> NodeType:
        return NodeType.FOR_EACH_STMT

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_for_each_stmt(self)

    def children(self) -> List[ASTNode]:
        return [self.iterable, self.body]


@dataclass
class ReturnStmt(Stmt):
    """Return: subira value."""

    value: Optional[Expr]

    @property
    def node_type(self) -> NodeType:
        return NodeType.RETURN_STMT

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_return_stmt(self)

    def children(self) -> List[ASTNode]:
        return [self.value] if self.value else []


@dataclass
class BreakStmt(Stmt):
    """Break: gukoma."""

    @property
    def node_type(self) -> NodeType:
        return NodeType.BREAK_STMT

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_break_stmt(self)

    def children(self) -> List[ASTNode]:
        return []


@dataclass
class ContinueStmt(Stmt):
    """Continue: kugenda."""

    @property
    def node_type(self) -> NodeType:
        return NodeType.CONTINUE_STMT

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_continue_stmt(self)

    def children(self) -> List[ASTNode]:
        return []


@dataclass
class ThrowStmt(Stmt):
    """Throw: gushyingura expression."""

    value: Expr

    @property
    def node_type(self) -> NodeType:
        return NodeType.THROW_STMT

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_throw_stmt(self)

    def children(self) -> List[ASTNode]:
        return [self.value]


@dataclass
class TryStmt(Stmt):
    """Try-catch-finally."""

    try_body: BlockStmt
    catch_var: Optional[str]
    catch_body: Optional[BlockStmt]
    finally_body: Optional[BlockStmt] = None

    @property
    def node_type(self) -> NodeType:
        return NodeType.TRY_STMT

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_try_stmt(self)

    def children(self) -> List[ASTNode]:
        result = [self.try_body]
        if self.catch_body:
            result.append(self.catch_body)
        if self.finally_body:
            result.append(self.finally_body)
        return result


@dataclass
class ExpressionStmt(Stmt):
    """Expression statement."""

    expression: Expr

    @property
    def node_type(self) -> NodeType:
        return NodeType.EXPRESSION_STMT

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_expression_stmt(self)

    def children(self) -> List[ASTNode]:
        return [self.expression]


@dataclass
class EmptyStmt(Stmt):
    """Empty statement."""

    @property
    def node_type(self) -> NodeType:
        return NodeType.EMPTY_STMT

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_empty_stmt(self)

    def children(self) -> List[ASTNode]:
        return []


# ══════════════════════════════════════════════════════════════════
# Root Node
# ══════════════════════════════════════════════════════════════════


@dataclass
class Program(Stmt):
    """Root program node."""

    declarations: List[Decl]

    @property
    def node_type(self) -> NodeType:
        return NodeType.PROGRAM

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_program(self)

    def children(self) -> List[ASTNode]:
        return list(self.declarations)


@dataclass
class Module(Stmt):
    """Module: named container for declarations."""

    name: str
    declarations: List[Decl]
    imports: List[ImportDecl]

    @property
    def node_type(self) -> NodeType:
        return NodeType.MODULE

    def accept(self, visitor: ASTVisitor) -> Any:
        return visitor.visit_module(self)

    def children(self) -> List[ASTNode]:
        return list(self.imports) + list(self.declarations)


# ══════════════════════════════════════════════════════════════════
# Visitor Interface
# ══════════════════════════════════════════════════════════════════


class ASTVisitor(ABC):
    """Visitor interface for all AST nodes."""

    # Expressions
    def visit_literal_expr(self, expr: LiteralExpr) -> Any: ...
    def visit_identifier_expr(self, expr: IdentifierExpr) -> Any: ...
    def visit_unary_expr(self, expr: UnaryExpr) -> Any: ...
    def visit_binary_expr(self, expr: BinaryExpr) -> Any: ...
    def visit_logical_expr(self, expr: LogicalExpr) -> Any: ...
    def visit_assignment_expr(self, expr: AssignmentExpr) -> Any: ...
    def visit_compound_assignment_expr(self, expr: CompoundAssignmentExpr) -> Any: ...
    def visit_call_expr(self, expr: CallExpr) -> Any: ...
    def visit_method_call_expr(self, expr: MethodCallExpr) -> Any: ...
    def visit_constructor_expr(self, expr: ConstructorExpr) -> Any: ...
    def visit_get_expr(self, expr: GetExpr) -> Any: ...
    def visit_set_expr(self, expr: SetExpr) -> Any: ...
    def visit_index_expr(self, expr: IndexExpr) -> Any: ...
    def visit_slice_expr(self, expr: SliceExpr) -> Any: ...
    def visit_self_expr(self, expr: SelfExpr) -> Any: ...
    def visit_super_expr(self, expr: SuperExpr) -> Any: ...
    def visit_list_expr(self, expr: ListExpr) -> Any: ...
    def visit_dict_expr(self, expr: DictExpr) -> Any: ...
    def visit_tuple_expr(self, expr: TupleExpr) -> Any: ...
    def visit_lambda_expr(self, expr: LambdaExpr) -> Any: ...
    def visit_if_expr(self, expr: IfExpr) -> Any: ...
    def visit_grouping_expr(self, expr: GroupingExpr) -> Any: ...
    def visit_placeholder_expr(self, expr: PlaceholderExpr) -> Any: ...

    # Types
    def visit_named_type(self, t: NamedType) -> Any: ...
    def visit_generic_type(self, t: GenericType) -> Any: ...
    def visit_function_type(self, t: FunctionType) -> Any: ...
    def visit_optional_type(self, t: OptionalType) -> Any: ...
    def visit_tuple_type(self, t: TupleType) -> Any: ...

    # Declarations
    def visit_var_decl(self, decl: VarDecl) -> Any: ...
    def visit_function_decl(self, decl: FunctionDecl) -> Any: ...
    def visit_method_decl(self, decl: MethodDecl) -> Any: ...
    def visit_struct_decl(self, decl: StructDecl) -> Any: ...
    def visit_enum_decl(self, decl: EnumDecl) -> Any: ...
    def visit_class_decl(self, decl: ClassDecl) -> Any: ...
    def visit_trait_decl(self, decl: TraitDecl) -> Any: ...
    def visit_interface_decl(self, decl: InterfaceDecl) -> Any: ...
    def visit_import_decl(self, decl: ImportDecl) -> Any: ...
    def visit_export_decl(self, decl: ExportDecl) -> Any: ...

    # Statements
    def visit_block_stmt(self, stmt: BlockStmt) -> Any: ...
    def visit_if_stmt(self, stmt: IfStmt) -> Any: ...
    def visit_while_stmt(self, stmt: WhileStmt) -> Any: ...
    def visit_until_stmt(self, stmt: UntilStmt) -> Any: ...
    def visit_for_stmt(self, stmt: ForStmt) -> Any: ...
    def visit_for_each_stmt(self, stmt: ForEachStmt) -> Any: ...
    def visit_return_stmt(self, stmt: ReturnStmt) -> Any: ...
    def visit_break_stmt(self, stmt: BreakStmt) -> Any: ...
    def visit_continue_stmt(self, stmt: ContinueStmt) -> Any: ...
    def visit_throw_stmt(self, stmt: ThrowStmt) -> Any: ...
    def visit_try_stmt(self, stmt: TryStmt) -> Any: ...
    def visit_expression_stmt(self, stmt: ExpressionStmt) -> Any: ...
    def visit_empty_stmt(self, stmt: EmptyStmt) -> Any: ...

    # Root
    def visit_program(self, program: Program) -> Any: ...
    def visit_module(self, module: Module) -> Any: ...

    # Helpers
    def visit_parameter(self, param: Parameter) -> Any: ...
    def visit_struct_field(self, field: StructField) -> Any: ...
    def visit_enum_variant(self, variant: EnumVariant) -> Any: ...
    def visit_elif_branch(self, branch: ElifBranch) -> Any: ...


# ══════════════════════════════════════════════════════════════════
# Backwards-compatible aliases (used by parser)
# ══════════════════════════════════════════════════════════════════

BlockExpr = BlockStmt
ClassStmt = ClassDecl
EnumStmt = EnumDecl
FunctionParam = Parameter
FunctionStmt = FunctionDecl
ImportStmt = ImportDecl
InterfaceStmt = InterfaceDecl
SourceSpan = SourceLocation
StructStmt = StructDecl
TraitStmt = TraitDecl
VarStmt = VarDecl
ExportStmt = ExportDecl
VariableExpr = IdentifierExpr
AssignExpr = AssignmentExpr


class ExprVisitor(ASTVisitor):
    """Backwards-compatible visitor base for expressions only."""
    pass


class StmtVisitor(ASTVisitor):
    """Backwards-compatible visitor base for statements only."""
    pass
