# AST Implementation — Phase 7, Sprint 3

## Overview

The Abstract Syntax Tree (AST) module provides the complete tree representation of I programs after parsing. It is the central data structure for all compiler passes that follow (semantic analysis, type checking, IR generation, optimization, code generation).

## Architecture

```
compiler/ast/
├── __init__.py      # Package exports
├── nodes.py         # All AST node definitions (41 node types)
├── visitor.py       # ASTWalker, ASTTransformer, PrettyPrinter, DebugPrinter
├── validator.py     # Structural validation (cycles, lvalues, scope)
├── serializer.py    # JSON serialization/deserialization
└── visualizer.py    # Text tree diagrams + Graphviz DOT output
```

## Node Hierarchy

### Base Classes

| Class | Purpose |
|-------|---------|
| `ASTNode` | Root base class. Has `node_id`, `location`, `metadata`, `accept()`, `children()` |
| `Expr` | Base for expressions. Adds `is_lvalue` property |
| `Stmt` | Base for statements |
| `Decl(Stmt)` | Base for declarations (which are also statements) |
| `TypeNode(ASTNode)` | Base for type references |

### NodeType Enum

All 50 node types are enumerated in `NodeType` for runtime type checking and switch-like dispatch.

### Node Categories

| Category | Count | Examples |
|----------|-------|----------|
| **Expressions** | 21 | `LiteralExpr`, `BinaryExpr`, `CallExpr`, `LambdaExpr`, `IfExpr` |
| **Statements** | 13 | `BlockStmt`, `IfStmt`, `WhileStmt`, `ForStmt`, `TryStmt` |
| **Declarations** | 10 | `VarDecl`, `FunctionDecl`, `StructDecl`, `ClassDecl`, `TraitDecl` |
| **Type Nodes** | 5 | `NamedType`, `GenericType`, `FunctionType`, `OptionalType`, `TupleType` |
| **Helpers** | 4 | `Parameter`, `StructField`, `EnumVariant`, `ElifBranch` |
| **Root** | 1 | `Program` |

### SourceLocation

```python
SourceLocation(
    file="main.i",
    start_line=10, start_column=5,
    end_line=10, end_column=15,
    start_offset=42, end_offset=57,
)
```

- `from_token(token, file)` — create from a lexer token
- `merge(a, b)` — span across two locations
- `line_count` — number of lines spanned

### Node IDs

Every node gets a unique `node_id` from a global `_NodeIDGenerator`. IDs are useful for:
- Deduplication during transformations
- Caching type information
- Graph visualization labeling

## Visitors

### ASTWalker

Non-mutating tree traversal with enter/exit callbacks:

```python
walker = ASTWalker()
walker.on_enter(lambda node: print(f"→ {node.node_type}"))
walker.on_exit(lambda node: print(f"← {node.node_type}"))
walker.walk(program)
```

### ASTTransformer

Returns new nodes for modifications. Identity by default — override specific visit methods:

```python
class ConstantFolder(ASTTransformer):
    def visit_binary_expr(self, expr):
        if isinstance(expr.left, LiteralExpr) and isinstance(expr.right, LiteralExpr):
            if expr.operator == "+":
                return LiteralExpr(expr.left.value + expr.right.value)
        return expr
```

The transformer preserves `node_id` and `location` from original nodes when creating replacements.

### PrettyPrinter

Human-readable indented tree:

```
Program
  Var(x)
    Literal(1)
  Function(add)
    Param(a)
    Param(b)
    Block
      Return
        Binary(+)
          Identifier(a)
          Identifier(b)
```

### DebugPrinter

Same as PrettyPrinter but includes node IDs, source locations, and metadata:

```
[1] Program @ test.i:1:1
  [2] Var(x) @ test.i:1:1
    [3] Literal(1) @ test.i:1:9
```

## Validation

The `ASTValidator` checks structural integrity after parsing:

| Check | Severity | Description |
|-------|----------|-------------|
| Cycle detection | error | Parent-child loops |
| Lvalue assignment | error | `42 = x` is invalid |
| Break outside loop | error | `gukoma` not in `wihuse`/`kugeza`/`kuri` |
| Continue outside loop | error | `kugenda` not in loop |
| Return outside function | error | `subira` not in `umurimo` |
| Duplicate declarations | warning | Same name in same scope |

```python
result = validate_ast(program)
if not result.is_valid:
    for error in result.errors:
        print(error)  # "[error] @ test.i:5:3: Break statement outside of loop"
```

Scope tracking: blocks, functions, structs, classes, traits, interfaces, loops, try/catch.

## Serialization

JSON-based round-trip serialization:

```python
serializer = ASTSerializer()
json_str = serializer.to_json(program)

deserializer = ASTDeserializer()
program = deserializer.from_json(json_str)
```

Format:
```json
{
  "kind": "BinaryExpr",
  "node_id": 42,
  "location": { "file": "main.i", "start_line": 1, ... },
  "operator": "+",
  "left": { "kind": "LiteralExpr", "value": 1, ... },
  "right": { "kind": "LiteralExpr", "value": 2, ... }
}
```

## Visualization

### Text Tree

```python
viz = TextTreeVisualizer(show_ids=True, show_location=True)
print(viz.render(program))
```

### Graphviz DOT

```python
viz = DOTVisualizer(show_ids=True)
dot = viz.to_dot(program)
with open("ast.dot", "w") as f:
    f.write(dot)
# Then: dot -Tpng ast.dot -o ast.png
```

Nodes are color-coded: green=expressions, blue=types, orange=declarations, pink=root.

## I Language Keywords in AST

The AST itself uses language-agnostic node names. The Kinyarwanda keywords are handled by the parser when constructing nodes:

| I Keyword | English Equivalent | AST Node |
|-----------|-------------------|----------|
| `shyira` | let | `VarDecl(is_const=False)` |
| `shyira_ko` | const | `VarDecl(is_const=True)` |
| `umurimo` | function | `FunctionDecl` |
| `igiceri` | struct | `StructDecl` |
| `urwego` | class | `ClassDecl` |
| `urubingo` | trait | `TraitDecl` |
| `akabuto` | interface | `InterfaceDecl` |
| `ikindi` | enum | `EnumDecl` |
| `niba`/`cyangwa` | if/else | `IfStmt` |
| `wihuse` | while | `WhileStmt` |
| `kugeza` | until | `UntilStmt` |
| `kuri` | for | `ForStmt` |
| `buri` | each | `ForEachStmt` |
| `subira` | return | `ReturnStmt` |
| `gukoma` | break | `BreakStmt` |
| `kugenda` | continue | `ContinueStmt` |
| `gushyingura` | throw | `ThrowStmt` |
| `kubika` | catch | `TryStmt` |
| `ikinyoma` | finally | `TryStmt` |
| `kora`...`iherezo` | do...end | `BlockStmt` |
| `shyiramo` | import | `ImportDecl` |
| `tanga` | export | `ExportDecl` |
| `kugira_ngo` | as | `ImportDecl.alias` |
| `gukora` | new | `ConstructorExpr` |
| `self` | self | `SelfExpr` |
| `super` | super | `SuperExpr` |
| `kandi` | and | `LogicalExpr("kandi")` |
| `cyangwa` | or | `LogicalExpr("cyangwa")` |
| `nti` | not | `UnaryExpr("nti")` |
| `yego`/`true` | true | `LiteralExpr(True)` |
| `oya`/`false` | false | `LiteralExpr(False)` |
| `ubusa`/`null` | null | `LiteralExpr(None)` |

## Testing

`tests/unit/test_ast.py` — 150+ test cases covering:
- SourceLocation creation, merge, string representation
- NodeType enum completeness
- All 41 node types: creation, node_type property, children()
- Expression lvalue checks
- Metadata set/get
- ASTWalker traversal
- ASTTransformer identity and modification
- PrettyPrinter and DebugPrinter output
- Validator: all error conditions
- Serializer round-trip (small, medium, large programs)
- TextTreeVisualizer and DOTVisualizer output

## Performance

`tests/benchmarks/bench_ast.py` benchmarks:
- Individual node creation (Literal, Binary, VarDecl, FunctionDecl)
- Full program construction (small/medium/large)
- Tree walking (all three sizes)
- Transformation (identity)
- Validation
- Serialization and deserialization
- Visualization (text, DOT, pretty, debug)

## Dependencies

- `compiler.lexer.token` — `Token` and `TokenType` for `LiteralExpr.token_type` and `SourceLocation.from_token`
