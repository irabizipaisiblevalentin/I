# AST Design

This document specifies the complete Abstract Syntax Tree (AST) node hierarchy for the I Programming Language.

## Table of Contents

- [Overview](#overview)
- [Base Node Structure](#base-node-structure)
- [Node Categories](#node-categories)
- [Program Node](#program-node)
- [Declaration Nodes](#declaration-nodes)
- [Statement Nodes](#statement-nodes)
- [Expression Nodes](#expression-nodes)
- [Type Nodes](#type-nodes)
- [Pattern Nodes](#pattern-nodes)
- [Attribute Nodes](#attribute-nodes)
- [Visitor Pattern](#visitor-pattern)
- [Node Relationships](#node-relationships)
- [AST Transformations](#ast-transformations)
- [Serialization](#serialization)
- [Performance](#performance)

## Overview

The AST is the intermediate representation between the parser and the rest of the compiler. It provides a hierarchical, structured representation of the program that:

1. **Abstracts away syntax**: No parentheses, semicolons, or delimiters
2. **Preserves semantics**: All semantic information is available
3. **Enables transformation**: Supports visitor pattern for analysis and rewriting
4. **Tracks source locations**: Every node knows where it came from in the source
5. **Supports annotations**: Subsequent stages can attach metadata

## Base Node Structure

### SourceLocation

Every AST node records its position in the source:

```
SourceLocation {
    file: string           // File path
    line: int              // 1-indexed line number
    column: int            // 1-indexed column number
    offset: int            // Byte offset from start of file
    end_offset: int        // Byte offset of end of node
}
```

### ASTNode (Base)

All AST nodes inherit from a base:

```
ASTNode {
    id: int                        // Unique node ID
    node_type: NodeType            // Enum of node types
    location: SourceLocation       // Source location
    annotations: Map<String, Any>  // Stage-specific metadata
}
```

### NodeType Enumeration

```
NodeType enum {
    // Root
    PROGRAM

    // Declarations
    FUNCTION_DECL
    VARIABLE_DECL
    STRUCT_DECL
    ENUM_DECL
    CLASS_DECL
    TRAIT_DECL
    INTERFACE_DECL
    TYPE_ALIAS_DECL
    IMPORT_DECL
    EXPORT_DECL

    // Statements
    BLOCK_STMT
    IF_STMT
    WHILE_STMT
    UNTIL_STMT
    FOR_STMT
    FOR_EACH_STMT
    RETURN_STMT
    BREAK_STMT
    CONTINUE_STMT
    THROW_STMT
    TRY_STMT
    EXPRESSION_STMT
    EMPTY_STMT

    // Expressions
    LITERAL_EXPR
    IDENTIFIER_EXPR
    BINARY_EXPR
    UNARY_EXPR
    ASSIGNMENT_EXPR
    COMPOUND_ASSIGNMENT_EXPR
    CALL_EXPR
    CONSTRUCTOR_EXPR
    MEMBER_EXPR
    INDEX_EXPR
    LAMBDA_EXPR
    LIST_EXPR
    DICT_EXPR
    TUPLE_EXPR
    IF_EXPR
    BLOCK_EXPR
    SELF_EXPR
    SUPER_EXPR

    // Types
    NAMED_TYPE
    GENERIC_TYPE
    FUNCTION_TYPE
    OPTIONAL_TYPE
    TUPLE_TYPE

    // Patterns
    LITERAL_PATTERN
    IDENTIFIER_PATTERN
    WILDCARD_PATTERN
    TUPLE_PATTERN
    STRUCT_PATTERN

    // Other
    PARAMETER
    FIELD
    VARIANT
    MATCH_CASE
    ATTRIBUTE
}
```

## Node Categories

### Hierarchy

```
ASTNode
    ├── Program
    ├── Declaration
    │   ├── FunctionDecl
    │   ├── VariableDecl
    │   ├── StructDecl
    │   ├── EnumDecl
    │   ├── ClassDecl
    │   ├── TraitDecl
    │   ├── InterfaceDecl
    │   ├── TypeAliasDecl
    │   ├── ImportDecl
    │   └── ExportDecl
    ├── Statement
    │   ├── BlockStmt
    │   ├── IfStmt
    │   ├── WhileStmt
    │   ├── UntilStmt
    │   ├── ForStmt
    │   ├── ForEachStmt
    │   ├── ReturnStmt
    │   ├── BreakStmt
    │   ├── ContinueStmt
    │   ├── ThrowStmt
    │   ├── TryStmt
    │   ├── ExpressionStmt
    │   └── EmptyStmt
    ├── Expression
    │   ├── LiteralExpr
    │   ├── IdentifierExpr
    │   ├── BinaryExpr
    │   ├── UnaryExpr
    │   ├── AssignmentExpr
    │   ├── CompoundAssignmentExpr
    │   ├── CallExpr
    │   ├── ConstructorExpr
    │   ├── MemberExpr
    │   ├── IndexExpr
    │   ├── LambdaExpr
    │   ├── ListExpr
    │   ├── DictExpr
    │   ├── TupleExpr
    │   ├── IfExpr
    │   ├── BlockExpr
    │   ├── SelfExpr
    │   └── SuperExpr
    ├── Type
    │   ├── NamedType
    │   ├── GenericType
    │   ├── FunctionType
    │   ├── OptionalType
    │   └── TupleType
    └── Pattern
        ├── LiteralPattern
        ├── IdentifierPattern
        ├── WildcardPattern
        ├── TuplePattern
        └── StructPattern
```

## Program Node

### Program

The root node of every AST:

```
Program(ASTNode) {
    declarations: List<Declaration>    // Top-level declarations
    imports: List<ImportDecl>          // All import declarations (extracted for convenience)
    source: string                     // Original source text (optional, for diagnostics)

    // Example:
    // shyiramo "std/io"
    // umurimo main() -> void
    //     andika "Muraho"
    // iherezo
}
```

## Declaration Nodes

### FunctionDecl

```
FunctionDecl(Declaration) {
    name: string                          // Function name
    parameters: List<Parameter>           // Parameters
    return_type: Optional<Type>           // Return type annotation
    body: BlockStmt                       // Function body
    is_async: bool                        // async function (future)
    is_generator: bool                    // generator function (future)
    visibility: Visibility                // public/private/protected
    doc_comments: List<string>            // Documentation comments
    attributes: List<Attribute>           // Compiler attributes

    // Example:
    // umurimo add(a: int, b: int) -> int
    //     subira a + b
    // iherezo
}
```

### Parameter

```
Parameter(ASTNode) {
    name: string                          // Parameter name
    param_type: Optional<Type>            // Type annotation
    default_value: Optional<Expression>   // Default value
    is_variadic: bool                     // ... rest parameter
    is_mutable: bool                      // mut parameter (future)

    // Example:
    // name: string = "World"
}
```

### VariableDecl

```
VariableDecl(Declaration) {
    name: string                          // Variable name
    var_type: Optional<Type>              // Type annotation
    initializer: Optional<Expression>     // Initial value
    is_mutable: bool                      // shyira (let) = true, shyira_ko (const) = false
    visibility: Visibility                // public/private
    doc_comments: List[string]            // Documentation comments

    // Example:
    // shyira x: int = 42
    // shyira_ko PI = 3.14159
}
```

### StructDecl

```
StructDecl(Declaration) {
    name: string                          // Struct name
    fields: List<Field>                   // Fields
    methods: List<FunctionDecl>           // Methods
    attributes: List<Attribute>           // Attributes
    doc_comments: List[string]            // Documentation comments

    // Example:
    // igiceri Person
    //     izina: string
    //     imyaka: int
    // iherezo
}
```

### Field

```
Field(ASTNode) {
    name: string                          // Field name
    field_type: Type                      // Type annotation
    default_value: Optional<Expression>   // Default value
    visibility: Visibility                // public/private

    // Example:
    // izina: string
}
```

### EnumDecl

```
EnumDecl(Declaration) {
    name: string                          // Enum name
    variants: List<Variant>               // Variants
    attributes: List<Attribute>           // Attributes
    doc_comments: List[string]            // Documentation comments

    // Example:
    // ikindi Color
    //     Red
    //     Green
    //     Blue
    // iherezo
}
```

### Variant

```
Variant(ASTNode) {
    name: string                          // Variant name
    types: List<Type>                     // Associated types (tuple variants)

    // Example:
    // Some(T)  =>  name="Some", types=[T]
    // None     =>  name="None", types=[]
}
```

### ClassDecl

```
ClassDecl(Declaration) {
    name: string                          // Class name
    parent: Optional<string>              // Parent class (from 'kugira')
    fields: List<Field>                   // Fields
    methods: List<FunctionDecl>           // Methods
    constructor: Optional<FunctionDecl>   // Constructor method
    traits: List<string>                  // Implemented traits
    attributes: List<Attribute>           // Attributes
    doc_comments: List[string]            // Documentation comments

    // Example:
    // urwego Dog kugira Animal
    //     breed: string
    //     umurimo speak() -> string
    //         subira "Woof"
    //     iherezo
    // iherezo
}
```

### TraitDecl

```
TraitDecl(Declaration) {
    name: string                          // Trait name
    methods: List<FunctionDecl>           // Method signatures
    attributes: List[Attribute>           // Attributes
    doc_comments: List[string]            // Documentation comments

    // Example:
    // urubingo Serializable
    //     umurimo serialize() -> string
    //     umurimo deserialize(data: string) -> void
    // iherezo
}
```

### InterfaceDecl

```
InterfaceDecl(Declaration) {
    name: string                          // Interface name
    methods: List<FunctionDecl>           // Method signatures
    attributes: List<Attribute>           // Attributes
    doc_comments: List[string]            // Documentation comments

    // Example:
    // akabuto Drawable
    //     umurimo draw() -> void
    // iherezo
}
```

### TypeAliasDecl

```
TypeAliasDecl(Declaration) {
    name: string                          // Alias name
    aliased_type: Type                    // The type being aliased
    doc_comments: List<string>            // Documentation comments

    // Example:
    // type UserId = int
}
```

### ImportDecl

```
ImportDecl(Declaration) {
    module_path: string                   // Module path
    alias: Optional[string]               // 'kugira_ngo' alias
    specific_imports: Optional<List<string>>  // Specific imports

    // Examples:
    // shyiramo "std/io"  =>  module_path="std/io", alias=null
    // shyiramo "std/io" kugira_ngo io  =>  module_path="std/io", alias="io"
}
```

### ExportDecl

```
ExportDecl(Declaration) {
    declaration: Declaration              // The exported declaration
    name: Optional[string]                // Exported name (for re-exports)

    // Example:
    // tanga function_name
}
```

## Statement Nodes

### BlockStmt

```
BlockStmt(Statement) {
    statements: List[Statement]           // Statements in the block

    // Example:
    // kora
    //     shyira x = 10
    //     andika x
    // iherezo
}
```

### IfStmt

```
IfStmt(Statement) {
    condition: Expression                 // Condition
    then_branch: BlockStmt               // Then branch
    elif_branches: List<(Expression, BlockStmt)>  // Elif branches
    else_branch: Optional<BlockStmt>     // Else branch

    // Example:
    // niba x > 0
    //     andika "positive"
    // cyangwa_niba x < 0
    //     andika "negative"
    // cyangwa
    //     andika "zero"
    // iherezo
}
```

### WhileStmt

```
WhileStmt(Statement) {
    condition: Expression                 // Loop condition
    body: BlockStmt                       // Loop body

    // Example:
    // wihuse x > 0
    //     x = x - 1
    // iherezo
}
```

### UntilStmt

```
UntilStmt(Statement) {
    condition: Expression                 // Exit condition
    body: BlockStmt                       // Loop body

    // Example:
    // kugeza x == 0
    //     x = x - 1
    // iherezo
}
```

### ForStmt

```
ForStmt(Statement) {
    variable: string                      // Loop variable name
    start: Expression                     // Start value
    end: Expression                       // End value
    body: BlockStmt                       // Loop body

    // Example:
    // kuri i muri 0 kugeza 10
    //     andika i
    // iherezo
}
```

### ForEachStmt

```
ForEachStmt(Statement) {
    variable: string                      // Element variable name
    iterable: Expression                  // Collection expression
    body: BlockStmt                       // Loop body

    // Example:
    // buri item muri collection
    //     andika item
    // iherezo
}
```

### ReturnStmt

```
ReturnStmt(Statement) {
    value: Optional<Expression>           // Return value

    // Example:
    // subira x + 1
    // subira  (void return)
}
```

### BreakStmt

```
BreakStmt(Statement) {
    label: Optional[string]               // Loop label (for nested loops)

    // Example:
    // gukoma
    // gukoma 'outer
}
```

### ContinueStmt

```
ContinueStmt(Statement) {
    label: Optional[string]               // Loop label

    // Example:
    // kugenda
    // kugenda 'outer
}
```

### ThrowStmt

```
ThrowStmt(Statement) {
    value: Expression                     // Exception value

    // Example:
    // gushyingura ValueError("Invalid value")
}
```

### TryStmt

```
TryStmt(Statement) {
    try_block: BlockStmt                  // Try block
    catch_var: Optional[string>           // Catch variable name
    catch_block: Optional<BlockStmt>      // Catch block
    finally_block: Optional<BlockStmt>    // Finally block

    // Example:
    // kora
    //     risky_operation()
    // kubika error
    //     handle_error(error)
    // ikinyoma
    //     cleanup()
    // iherezo
}
```

### ExpressionStmt

```
ExpressionStmt(Statement) {
    expression: Expression                // The expression

    // Example:
    // andika "Hello"
    // x + 1  (if used as statement)
}
```

### EmptyStmt

```
EmptyStmt(Statement) {
    // Empty statement (just 'iherezo' or ';')
}
```

## Expression Nodes

### LiteralExpr

```
LiteralExpr(Expression) {
    value: LiteralValue                   // The literal value
    literal_type: LiteralType             // INTEGER, FLOAT, STRING, CHAR, BOOLEAN, NULL

    // Examples:
    // 42         =>  value=42, literal_type=INTEGER
    // 3.14       =>  value=3.14, literal_type=FLOAT
    // "Muraho"   =>  value="Muraho", literal_type=STRING
    // 'a'        =>  value='a', literal_type=CHAR
    // yego       =>  value=true, literal_type=BOOLEAN
    // ubusa      =>  value=null, literal_type=NULL
}
```

### LiteralValue

```
LiteralValue {
    kind: LiteralType
    int_value: Optional<int>
    float_value: Optional<float>
    string_value: Optional<string>
    char_value: Optional<char>
    bool_value: Optional<bool>
}
```

### IdentifierExpr

```
IdentifierExpr(Expression) {
    name: string                          // Variable name

    // Example:
    // x
    // my_variable
    // umuntu
}
```

### BinaryExpr

```
BinaryExpr(Expression) {
    left: Expression                      // Left operand
    operator: BinaryOperator              // Operator
    right: Expression                     // Right operand

    // Example:
    // a + b   =>  left=a, operator=ADD, right=b
    // x > 5   =>  left=x, operator=GT, right=5
}
```

### BinaryOperator Enumeration

```
BinaryOperator enum {
    // Arithmetic
    ADD              // +
    SUBTRACT         // -
    MULTIPLY         // *
    DIVIDE           // /
    MODULO           // %
    POWER            // **
    FLOOR_DIVIDE     // //

    // Comparison
    EQUAL            // ==
    NOT_EQUAL        // !=
    LESS             // <
    LESS_EQUAL       // <=
    GREATER          // >
    GREATER_EQUAL    // >=
    IDENTITY         // ===
    NOT_IDENTITY     // !==

    // Logical
    AND              // kandi / &&
    OR               // cyangwa / ||

    // Bitwise
    BIT_AND          // &
    BIT_OR           // |
    BIT_XOR          // ^
    LEFT_SHIFT       // <<
    RIGHT_SHIFT      // >>
    UNSIGNED_RIGHT_SHIFT  // >>>
}
```

### UnaryExpr

```
UnaryExpr(Expression) {
    operator: UnaryOperator               // Operator
    operand: Expression                   // Operand

    // Example:
    // -x      =>  operator=NEGATE, operand=x
    // si x    =>  operator=NOT, operand=x
    // ~bits   =>  operator=BIT_NOT, operand=bits
}
```

### UnaryOperator Enumeration

```
UnaryOperator enum {
    NEGATE            // -
    NOT               // si / !
    BIT_NOT           // ~
    DEREFERENCE       // * (future)
    REFERENCE         // & (future)
    INCREMENT         // ++ (future)
    DECREMENT         // -- (future)
}
```

### AssignmentExpr

```
AssignmentExpr(Expression) {
    target: Expression                    // Assignment target (must be assignable)
    value: Expression                     // Assigned value

    // Example:
    // x = 10   =>  target=x, value=10
}
```

### CompoundAssignmentExpr

```
CompoundAssignmentExpr(Expression) {
    target: Expression                    // Assignment target
    operator: BinaryOperator              // The compound operator
    value: Expression                     // Right-hand side

    // Example:
    // x += 5   =>  target=x, operator=ADD, value=5
    // x *= 2   =>  target=x, operator=MULTIPLY, value=2
}
```

### CallExpr

```
CallExpr(Expression) {
    callee: Expression                    // What is being called
    arguments: List<Expression>           // Arguments

    // Example:
    // add(1, 2)  =>  callee=IdentifierExpr("add"), arguments=[1, 2]
    // obj.method(x)  =>  callee=MemberExpr(...), arguments=[x]
}
```

### ConstructorExpr

```
ConstructorExpr(Expression) {
    class_name: string                    // Class name
    arguments: List<Expression>           // Constructor arguments

    // Example:
    // gukora Person("Jean", 25)
}
```

### MemberExpr

```
MemberExpr(Expression) {
    object: Expression                    // Object expression
    member: string                        // Member name
    is_safe: bool                         // ?. operator (future)

    // Example:
    // point.x  =>  object=point, member="x"
}
```

### IndexExpr

```
IndexExpr(Expression) {
    object: Expression                    // Object expression
    index: Expression                     // Index expression

    // Example:
    // array[0]  =>  object=array, index=0
    // map["key"]  =>  object=map, index="key"
}
```

### LambdaExpr

```
LambdaExpr(Expression) {
    parameters: List<Parameter>           // Lambda parameters
    return_type: Optional<Type>           // Return type
    body: Expression                      // Lambda body

    // Example:
    // (a: int, b: int) -> int => a + b
}
```

### ListExpr

```
ListExpr(Expression) {
    elements: List<Expression>            // List elements

    // Example:
    // [1, 2, 3]  =>  elements=[1, 2, 3]
}
```

### DictExpr

```
DictExpr(Expression) {
    keys: List<Expression>                // Dictionary keys
    values: List<Expression>              // Dictionary values

    // Example:
    // {name: "Jean", age: 25}
}
```

### TupleExpr

```
TupleExpr(Expression) {
    elements: List<Expression>            // Tuple elements

    // Example:
    // (1, 2, 3)  =>  elements=[1, 2, 3]
}
```

### IfExpr

```
IfExpr(Expression) {
    condition: Expression                 // Condition
    then_expr: Expression                 // Then expression
    else_expr: Expression                 // Else expression

    // Example:
    // niba x > 0 => "positive" cyangwa "non-positive"
}
```

### BlockExpr

```
BlockExpr(Expression) {
    statements: List[Statement]           // Statements
    result: Expression                    // Final expression (result)

    // Example:
    // kora
    //     shyira x = 5
    //     x + 1
    // iherezo
}
```

### SelfExpr

```
SelfExpr(Expression) {
    // Reference to current instance
    // Used inside class methods
    // self.field
}
```

### SuperExpr

```
SuperExpr(Expression) {
    method: string                        // Parent method name

    // Example:
    // super.method()
}
```

## Type Nodes

### NamedType

```
NamedType(Type) {
    name: string                          // Type name
    module: Optional[string>              // Module qualifier

    // Examples:
    // int             =>  name="int", module=null
    // string          =>  name="string", module=null
    // std::io::File   =>  name="File", module="std::io"
}
```

### GenericType

```
GenericType(Type) {
    name: string                          // Base type name
    type_arguments: List<Type>            // Type arguments

    // Examples:
    // List<int>         =>  name="List", type_arguments=[NamedType("int")]
    // Map<string, int>  =>  name="Map", type_arguments=[NamedType("string"), NamedType("int")]
}
```

### FunctionType

```
FunctionType(Type) {
    parameters: List<Type>                // Parameter types
    return_type: Type                     // Return type

    // Example:
    // (int, int) -> int
}
```

### OptionalType

```
OptionalType(Type) {
    inner_type: Type                      // The inner type

    // Example:
    // int?  =>  inner_type=NamedType("int")
    // Equivalent to: int | null
}
```

### TupleType

```
TupleType(Type) {
    elements: List<Type>                  // Element types

    // Example:
    // (int, string, bool)  =>  elements=[NamedType("int"), NamedType("string"), NamedType("bool")]
}
```

## Pattern Nodes

### LiteralPattern

```
LiteralPattern(Pattern) {
    value: LiteralValue                   // The literal value

    // Example:
    // match x {
    //     0 => ...
    //     "hello" => ...
    // }
}
```

### IdentifierPattern

```
IdentifierPattern(Pattern) {
    name: string                          // Variable name
    is_ref: bool                          // Reference binding (future)

    // Example:
    // match option {
    //     Some(x) => ...
    // }
}
```

### WildcardPattern

```
WildcardPattern(Pattern) {
    // Matches anything
    // match x {
    //     _ => ...
    // }
}
```

### TuplePattern

```
TuplePattern(Pattern) {
    patterns: List<Pattern>               // Element patterns

    // Example:
    // match point {
    //     (0, 0) => ...
    //     (x, y) => ...
    // }
}
```

### StructPattern

```
StructPattern(Pattern) {
    type_name: string                     // Type name
    fields: Map<String, Pattern>          // Field patterns

    // Example:
    // match person {
    //     Person { izina: "Jean", imyaka: age } => ...
    // }
}
```

## Attribute Nodes

### Attribute

```
Attribute(ASTNode) {
    name: string                          // Attribute name
    arguments: List<Expression>           // Arguments

    // Examples:
    // #[inline]
    // #[deprecated("use new_function instead")]
    // #[test]
}
```

## Visitor Pattern

### ASTVisitor Interface

The AST supports the visitor pattern for traversal:

```
ASTVisitor<T> {
    visit_program(node: Program) -> T
    visit_function_decl(node: FunctionDecl) -> T
    visit_variable_decl(node: VariableDecl) -> T
    visit_struct_decl(node: StructDecl) -> T
    visit_enum_decl(node: EnumDecl) -> T
    visit_class_decl(node: ClassDecl) -> T
    visit_trait_decl(node: TraitDecl) -> T
    visit_interface_decl(node: InterfaceDecl) -> T
    visit_type_alias_decl(node: TypeAliasDecl) -> T
    visit_import_decl(node: ImportDecl) -> T
    visit_export_decl(node: ExportDecl) -> T
    visit_block_stmt(node: BlockStmt) -> T
    visit_if_stmt(node: IfStmt) -> T
    visit_while_stmt(node: WhileStmt) -> T
    visit_until_stmt(node: UntilStmt) -> T
    visit_for_stmt(node: ForStmt) -> T
    visit_for_each_stmt(node: ForEachStmt) -> T
    visit_return_stmt(node: ReturnStmt) -> T
    visit_break_stmt(node: BreakStmt) -> T
    visit_continue_stmt(node: ContinueStmt) -> T
    visit_throw_stmt(node: ThrowStmt) -> T
    visit_try_stmt(node: TryStmt) -> T
    visit_expression_stmt(node: ExpressionStmt) -> T
    visit_empty_stmt(node: EmptyStmt) -> T
    visit_literal_expr(node: LiteralExpr) -> T
    visit_identifier_expr(node: IdentifierExpr) -> T
    visit_binary_expr(node: BinaryExpr) -> T
    visit_unary_expr(node: UnaryExpr) -> T
    visit_assignment_expr(node: AssignmentExpr) -> T
    visit_compound_assignment_expr(node: CompoundAssignmentExpr) -> T
    visit_call_expr(node: CallExpr) -> T
    visit_constructor_expr(node: ConstructorExpr) -> T
    visit_member_expr(node: MemberExpr) -> T
    visit_index_expr(node: IndexExpr) -> T
    visit_lambda_expr(node: LambdaExpr) -> T
    visit_list_expr(node: ListExpr) -> T
    visit_dict_expr(node: DictExpr) -> T
    visit_tuple_expr(node: TupleExpr) -> T
    visit_if_expr(node: IfExpr) -> T
    visit_block_expr(node: BlockExpr) -> T
    visit_self_expr(node: SelfExpr) -> T
    visit_super_expr(node: SuperExpr) -> T
    visit_named_type(node: NamedType) -> T
    visit_generic_type(node: GenericType) -> T
    visit_function_type(node: FunctionType) -> T
    visit_optional_type(node: OptionalType) -> T
    visit_tuple_type(node: TupleType) -> T
}
```

### Default Visitor (Walk)

A default visitor that walks all children:

```
class ASTWalker implements ASTVisitor<void> {
    walk(node: ASTNode):
        node.accept(this)

    visit_program(node: Program):
        for decl in node.declarations:
            walk(decl)

    visit_function_decl(node: FunctionDecl):
        for param in node.parameters:
            walk(param)
        walk(node.body)

    // ... (similar for all other nodes)
}
```

## Node Relationships

```
Program
    └── declarations: Declaration[]
        ├── FunctionDecl
        │   ├── parameters: Parameter[]
        │   │   └── param_type: Type
        │   ├── return_type: Type
        │   └── body: BlockStmt
        │       └── statements: Statement[]
        │           ├── VariableDecl
        │           │   └── initializer: Expression
        │           ├── ExpressionStmt
        │           │   └── expression: Expression
        │           ├── ReturnStmt
        │           │   └── value: Expression
        │           ├── IfStmt
        │           │   ├── condition: Expression
        │           │   ├── then_branch: BlockStmt
        │           │   └── else_branch: BlockStmt
        │           └── ...
        ├── VariableDecl
        │   ├── var_type: Type
        │   └── initializer: Expression
        ├── StructDecl
        │   ├── fields: Field[]
        │   └── methods: FunctionDecl[]
        ├── EnumDecl
        │   └── variants: Variant[]
        ├── ClassDecl
        │   ├── parent: string
        │   ├── fields: Field[]
        │   ├── methods: FunctionDecl[]
        │   └── traits: string[]
        ├── ImportDecl
        └── ExportDecl
            └── declaration: Declaration
```

## AST Transformations

The AST is designed to support tree transformations:

### Constant Folding

```
// Before:
BinaryExpr(
    left=LiteralExpr(2),
    operator=ADD,
    right=LiteralExpr(3)
)

// After optimization:
LiteralExpr(5)
```

### Dead Code Elimination

```
// Before:
IfStmt(
    condition=LiteralExpr(false),
    then_branch=BlockStmt([...]),
    else_branch=null
)

// After optimization:
(empty - node removed)
```

### Function Inlining

```
// Before:
CallExpr(
    callee=IdentifierExpr("add"),
    arguments=[LiteralExpr(1), LiteralExpr(2)]
)

// After inlining:
BinaryExpr(
    left=LiteralExpr(1),
    operator=ADD,
    right=LiteralExpr(2)
)
```

## Serialization

### JSON Format

The AST can be serialized to JSON for debugging and tooling:

```json
{
  "node_type": "Program",
  "id": 1,
  "location": {"file": "main.i", "line": 1, "column": 1},
  "declarations": [
    {
      "node_type": "FunctionDecl",
      "id": 2,
      "name": "main",
      "parameters": [],
      "return_type": null,
      "body": {
        "node_type": "BlockStmt",
        "id": 3,
        "statements": [
          {
            "node_type": "ExpressionStmt",
            "id": 4,
            "expression": {
              "node_type": "CallExpr",
              "id": 5,
              "callee": {
                "node_type": "IdentifierExpr",
                "id": 6,
                "name": "andika"
              },
              "arguments": [
                {
                  "node_type": "LiteralExpr",
                  "id": 7,
                  "value": "Muraho",
                  "literal_type": "STRING"
                }
              ]
            }
          }
        ]
      }
    }
  ]
}
```

## Performance

### Memory Layout

- **ASTNode base**: 16 bytes (id: 4, node_type: 4, location pointer: 8)
- **Average node**: 48-64 bytes
- **String storage**: Interpreted, shared across nodes

### Arena Allocation

All AST nodes are allocated from a single arena allocator:

1. Allocate all nodes from a contiguous memory block
2. Nodes are never individually freed
3. The entire arena is freed when the AST is no longer needed

### Node Reuse

For transformations that produce new ASTs, nodes that don't change can be shared between the old and new trees.

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
