# AST Implementation — Sprint 3

## Architecture

The AST subsystem is the canonical representation of every I program between the Parser and the Semantic Analyzer. It is immutable-by-convention (dataclass-based), extensible via the visitor pattern, and supports full round-trip serialization.

### Package Layout

```
src/compiler/ast/
├── __init__.py        # Public API exports
├── nodes.py           # Node definitions, NodeType enum, ASTVisitor interface
├── visitor.py         # ASTWalker, ASTTransformer, ASTRewriter, ASTInspector,
│                      #   PrettyPrinter, DebugPrinter
├── validator.py       # Structural validation, cycle detection, source span checks
├── serializer.py      # JSON serializer/deserializer, binary serialization,
│                      #   versioned serialization
└── visualizer.py      # TextTreeVisualizer, DOTVisualizer
```

---

## Node Hierarchy

```
ASTNode (abstract base)
├── Expr
│   ├── LiteralExpr          — integer, float, string, char, bool, null
│   ├── IdentifierExpr       — variable reference
│   ├── UnaryExpr            — operator operand
│   ├── BinaryExpr           — left operator right
│   ├── LogicalExpr          — left and/or right
│   ├── AssignmentExpr       — target = value
│   ├── CompoundAssignmentExpr — target op= value
│   ├── CallExpr             — callee(args)
│   ├── MethodCallExpr       — object.method(args)        [NEW]
│   ├── ConstructorExpr      — gukora ClassName(args)
│   ├── GetExpr              — object.property
│   ├── SetExpr              — object.property = value
│   ├── IndexExpr            — object[index]
│   ├── SliceExpr            — object[start:end]
│   ├── SelfExpr             — self reference
│   ├── SuperExpr            — super.method
│   ├── ListExpr             — [elements]
│   ├── DictExpr             — {key: value}
│   ├── TupleExpr            — (elements)
│   ├── LambdaExpr           — (params) => body
│   ├── IfExpr               — niba cond expr iherezo
│   ├── GroupingExpr         — (expression)
│   └── PlaceholderExpr      — future extension slot    [NEW]
├── TypeNode
│   ├── NamedType            — type name reference
│   ├── GenericType          — name<T>
│   ├── FunctionType         — (params) -> return
│   ├── OptionalType         — T?
│   └── TupleType            — (T1, T2, ...)
├── Decl
│   ├── VarDecl              — shyira name = value
│   ├── FunctionDecl         — umurimo name(params) body
│   ├── MethodDecl           — method declaration        [NEW]
│   ├── StructDecl           — igiceri name fields methods
│   ├── EnumDecl             — ikindi name variants
│   ├── ClassDecl            — urwego name parent members
│   ├── TraitDecl            — urubingo name members
│   ├── InterfaceDecl        — akabuto name members
│   ├── ImportDecl           — shyiramo path [alias]
│   └── ExportDecl           — tanga name
├── Stmt
│   ├── BlockStmt            — statements
│   ├── IfStmt               — niba/cyangwa/cyangwa niba
│   ├── WhileStmt            — wihuse condition body
│   ├── UntilStmt            — kugeza condition body
│   ├── ForStmt              — kuri var = start kugeza end
│   ├── ForEachStmt          — buri element muri iterable
│   ├── ReturnStmt           — subira value
│   ├── BreakStmt            — gukoma
│   ├── ContinueStmt         — kugenda
│   ├── ThrowStmt            — gushyingura expr
│   ├── TryStmt              — try-catch-finally
│   ├── ExpressionStmt       — expression ;
│   └── EmptyStmt            — ;
├── Program                  — root node, list of declarations
└── Module                   — named module container      [NEW]
```

### Helper Nodes

| Node | Purpose |
|------|---------|
| `Parameter` | Function/method parameter with optional type and default |
| `StructField` | Struct field with type annotation and optional default |
| `EnumVariant` | Enum variant with optional value expression |
| `ElifBranch` | Single elif branch (condition + body) |

---

## Source Location

Every node carries a `SourceLocation`:

| Field | Type | Description |
|-------|------|-------------|
| `file` | `str` | Source file path |
| `start_line` | `int` | 1-based start line |
| `start_column` | `int` | 1-based start column |
| `end_line` | `int` | 1-based end line |
| `end_column` | `int` | 1-based end column |
| `start_offset` | `int` | Byte offset start |
| `end_offset` | `int` | Byte offset end |

Locations can be created via `SourceLocation.from_token(token)` or `SourceLocation.merge(a, b)`.

---

## Node ID System

Every node gets a unique integer ID from a global counter (`_NodeIDGenerator`). This is used for:
- Tracking nodes across transformations
- Cycle detection in validation
- Debug output and serialization

---

## Compiler Metadata

Every node has a `metadata: Dict[str, Any]` dictionary for compiler passes (type info, symbol table entries, etc.). Use `node.set_metadata(key, value)` and `node.get_metadata(key, default)`.

---

## Visitor System

### ASTVisitor (interface)

Abstract base with `visit_*` methods for every node type. All visitors inherit from this.

### ASTWalker

Walks the tree without modifying it. Uses `on_enter(callback)` and `on_exit(callback)` hooks.

```python
walker = ASTWalker()
walker.on_enter(lambda node: print(f"enter: {node.node_type}"))
walker.walk(program)
```

### ASTTransformer

Walks and replaces nodes. Override specific `visit_*` methods to return new nodes. Uses identity checking for optimization (unchanged children → reuse original node).

```python
class ConstantFolder(ASTTransformer):
    def visit_binary_expr(self, expr):
        if isinstance(expr.left, LiteralExpr) and isinstance(expr.right, LiteralExpr):
            return LiteralExpr(value=eval(f"{expr.left.value}{expr.operator}{expr.right.value}"))
        return expr
```

### ASTRewriter

Callback-based rewriting using a registry pattern. Register handlers by node class.

```python
rewriter = ASTRewriter()
rewriter.register(LiteralExpr, lambda e: LiteralExpr(e.value * 2, location=e.location))
new_tree = rewriter.rewrite(program)
```

### ASTInspector

Collects statistics about the AST: node counts, depth, function/class/method names, identifiers, etc.

```python
inspector = ASTInspector()
stats = inspector.inspect(program)
print(f"Total nodes: {stats['total_nodes']}")
print(f"Functions: {stats['function_names']}")
```

### PrettyPrinter

Human-readable indented tree output.

### DebugPrinter

Detailed output with node IDs, source locations, and metadata.

---

## Validation

`ASTValidator` performs structural validation:

- **Cycle detection**: Uses ID-based set to detect node reference cycles
- **Source span validation**: Checks all source locations are well-formed (non-negative, end >= start)
- **Lvalue checking**: Assignment targets must be identifier, property access, or index
- **Scope checking**: Break/continue outside loops, return outside functions
- **Scope tracking**: Detects duplicate declarations in same scope
- **Required field checks**: Children arrays are populated correctly

```python
result = validate_ast(program)
if not result.is_valid:
    for error in result.errors:
        print(f"{error.severity}: {error.message}")
```

---

## Serialization

### JSON (ASTSerializer / ASTDeserializer)

Full round-trip JSON serialization. All node types supported.

```python
serializer = ASTSerializer()
json_str = serializer.to_json(program)

deserializer = ASTDeserializer()
program = deserializer.from_json(json_str)
```

### Binary (ASTBinarySerializer)

Compressed binary format using JSON + zlib. Includes version header.

```python
serializer = ASTBinarySerializer()
data = serializer.to_bytes(program)
program = serializer.from_bytes(data)

# Or file-based:
serializer.to_file(program, "output.iast")
program = serializer.from_file("output.iast")
```

Format: `I-AST-v1\n<zlib-compressed JSON>`

### Versioned (ASTVersionedSerializer)

JSON with version envelope for forward/backward compatibility.

```python
serializer = ASTVersionedSerializer()
json_str = serializer.to_json(program)
program = serializer.from_json(json_str)
```

Envelope: `{ "format_version": "1.0", "ast_version": 1, "ast": {...} }`

---

## Visualization

### TextTreeVisualizer

Unicode box-drawing tree for terminal output.

```python
viz = TextTreeVisualizer(show_ids=True, show_location=True)
print(viz.render(program))
```

### DOTVisualizer

Graphviz DOT format for graph rendering.

```python
viz = DOTVisualizer()
dot = viz.to_dot(program)
# Save: open("ast.dot", "w").write(dot)
# Render: dot -Tpng ast.dot -o ast.png
```

---

## Memory Design

- **Dataclass-based**: Uses Python dataclasses for efficient attribute access
- **ID-based identity**: Node IDs enable efficient set/dict operations
- **Immutable sharing**: ASTTransformer reuses unchanged subtrees via `is` identity checks
- **Lazy children**: `children()` is a method (not stored), computed on demand
- **Low allocation**: Nodes are lightweight; metadata dict only created when used

---

## Performance Characteristics

| Operation | Complexity |
|-----------|-----------|
| Node creation | O(1) |
| children() | O(k) where k = number of children |
| Walker traversal | O(n) |
| Transformer traversal | O(n) with O(1) reuse for unchanged subtrees |
| JSON serialization | O(n) |
| Binary serialization | O(n) with compression |
| Validation | O(n) |

---

## Extension Guidelines

### Adding a New Node Type

1. Add `NodeType` entry to the enum in `nodes.py`
2. Create the node class extending `Expr`, `Stmt`, `Decl`, or `TypeNode`
3. Implement `node_type`, `accept()`, `children()`
4. Add `visit_*` method to `ASTVisitor` interface
5. Implement in all visitors: `ASTWalker`, `ASTTransformer`, `ASTRewriter`, `ASTInspector`, `PrettyPrinter`, `DebugPrinter`
6. Add to `ASTSerializer` and `ASTDeserializer`
7. Add to `TextTreeVisualizer` and `DOTVisualizer` `_semantic_info` methods
8. Add to validator if structural checks are needed
9. Export from `__init__.py`
10. Write tests

### Adding a New Visitor

1. Subclass `ASTVisitor`
2. Implement all `visit_*` methods (use `pass` for no-ops)
3. Register in `__init__.py`

---

## Test Coverage

### Test Categories (test_ast_sprint3.py)

| Category | Count | Description |
|----------|-------|-------------|
| Node Types | 4 | New NodeType enum entries |
| Module | 3 | Module node creation, children, visitor |
| MethodDecl | 5 | Method declaration, static, params, printer |
| MethodCallExpr | 4 | Method call, args, lvalue, printer |
| PlaceholderExpr | 4 | Placeholder creation, description, printer |
| ASTRewriter | 7 | Identity, replacement, nested, program, method, module |
| ASTInspector | 13 | Empty, binary, function/class/method/struct/enum/trait/interface names |
| Source Span | 6 | Valid, negative start, end before start, same line |
| Validation | 5 | Method decl, module, placeholder, method call |
| Serialization | 5 | Round-trip module, method decl, method call, placeholder, full program |
| Binary Serialization | 4 | Round-trip, compression, invalid header, file I/O |
| Versioned Serialization | 3 | Round-trip, deserialize, wrong version |
| Visualization | 6 | Text tree and DOT for module, method, call, placeholder |
| Debug Printer | 3 | Method decl, static method, module |
| Stress | 7 | 1000 nodes, 100 deep, 500 wide, validation, serialization |
| Unicode | 8 | Identifiers, literals, module, printer, visualizer, serialization, emoji |
| Golden Snapshots | 4 | Simple program, function, method call, module |
| Walker | 4 | Method call, placeholder, module, method decl |
| Transformer | 3 | Method call, method decl, module identity |
| Regression | 5 | Node ID, location, metadata preservation, try-catch |
| Fuzz | 2 | Random AST nodes, random tree shapes |
| **Total** | **105** | |

---

## Definition of Done

- Complete node hierarchy (30+ node types)
- Visitor framework (8 visitor implementations)
- Validation (structural, cycle, source span, lvalue, scope)
- Serialization (JSON, binary, versioned)
- Visualization (text tree, Graphviz DOT)
- Tests (105 new + 101 existing = 206 total, all passing)
- Documentation (this file)
- Zero regressions in existing tests
