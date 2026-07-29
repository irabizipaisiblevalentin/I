# PARSER_IMPLEMENTATION.md — I Language Parser

## Overview

The I language parser transforms a validated token stream into a complete Abstract Syntax Tree (AST). It is the second stage of the I compiler pipeline, operating after the lexer.

## Architecture

```
Token Stream
    ↓
Parser Engine
    ├── Pratt Expression Parser (precedence climbing)
    ├── Recursive Descent Statement Parser
    └── Block Structure Validator (kora/iherezo)
    ↓
Abstract Syntax Tree (AST)
```

## Grammar Summary

### Program Structure
```
program         ::= declaration* EOF
declaration     ::= function_decl | variable_decl | type_decl | import_decl
                  | export_decl | statement
```

### Statements
```
statement       ::= if_stmt | while_stmt | until_stmt | for_stmt
                  | for_each_stmt | break_stmt | continue_stmt
                  | return_stmt | throw_stmt | try_stmt
                  | block_stmt | expression_stmt

if_stmt         ::= 'niba' expression block
                    ('cyangwa_niba' expression block)*
                    ('cyangwa' block)?

while_stmt      ::= 'wihuse' expression block
until_stmt      ::= 'kugeza' expression block
for_stmt        ::= 'kuri' IDENTIFIER '=' expression 'kugeza' expression block
for_each_stmt   ::= 'buri' IDENTIFIER 'muri' expression block
break_stmt      ::= 'gukoma'
continue_stmt   ::= 'kugenda'
return_stmt     ::= 'subira' expression?
throw_stmt      ::= 'gushyingura' expression
try_stmt        ::= 'kora' block ('kubika' IDENTIFIER block)? ('ikinyoma' block)?

block           ::= 'kora' declaration* 'iherezo'
```

### Declarations
```
variable_decl   ::= ('shyira' | 'shyira_ko') IDENTIFIER (':' IDENTIFIER)? ('=' expression)?
function_decl   ::= 'umurimo' IDENTIFIER '(' params? ')' ('->' IDENTIFIER)? block
struct_decl     ::= 'igiceri' IDENTIFIER 'kora' struct_body 'iherezo'
enum_decl       ::= 'ikindi' IDENTIFIER 'kora' enum_body 'iherezo'
class_decl      ::= 'urwego' IDENTIFIER ('kugira' IDENTIFIER)? 'kora' class_body 'iherezo'
trait_decl      ::= 'urubingo' IDENTIFIER 'kora' class_body 'iherezo'
interface_decl  ::= 'akabuto' IDENTIFIER 'kora' class_body 'iherezo'
import_decl     ::= 'shyiramo' IDENTIFIER ('kugira_ngo' IDENTIFIER)?
export_decl     ::= 'tanga' IDENTIFIER
```

### Expressions (Pratt Parsing)
```
expression      ::= assignment
assignment      ::= (call | get | index) '=' assignment | logic_or
logic_or        ::= logic_and ('cyangwa' | '||' logic_and)*
logic_and       ::= equality ('kandi' | '&&' equality)*
equality        ::= comparison (('==' | '!=' | '===' | '!==') comparison)*
comparison      ::= bitwise_or (('>' | '<' | '>=' | '<=') bitwise_or)*
bitwise_or      ::= bitwise_xor ('|' bitwise_xor)*
bitwise_xor     ::= bitwise_and ('^' bitwise_and)*
bitwise_and     ::= shift ('&' shift)*
shift           ::= term (('<<' | '>>' | '>>>') term)*
term            ::= factor (('+' | '-') factor)*
factor          ::= power (('*' | '/' | '%') power)*
power           ::= unary ('**' power)?    -- right-associative
unary           ::= ('-' | '!' | '~' | 'si') unary | call
call            ::= primary ('(' args? ')' | '.' IDENTIFIER | '[' expression ']')*
primary         ::= INTEGER | FLOAT | STRING | CHARACTER | BOOLEAN | NULL
                  | IDENTIFIER | 'self' | 'super' '.' IDENTIFIER
                  | '(' expression ')' | list | dict
                  | 'gukora' IDENTIFIER '(' args? ')'
                  | 'kora' statement* expression 'iherezo'
                  | 'niba' expression 'kora' expression 'iherezo' ('cyangwa' expression)?
```

## Operator Precedence

| Level | Operators | Associativity |
|-------|-----------|---------------|
| 1 | `=` `+=` `-=` `*=` `/=` `%=` `**=` | Right |
| 2 | `cyangwa` `\|\|` | Left |
| 3 | `kandi` `&&` | Left |
| 4 | `==` `!=` `===` `!==` | Left |
| 5 | `>` `<` `>=` `<=` | Left |
| 6 | `\|` | Left |
| 7 | `^` | Left |
| 8 | `&` | Left |
| 9 | `<<` `>>` `>>>` | Left |
| 10 | `+` `-` | Left |
| 11 | `*` `/` `%` | Left |
| 12 | `**` | Right |
| 13 | `-` `!` `~` `si` | Right |
| 14 | `()` `[]` `.` | Left |
| 15 | Literals, identifiers, grouping | N/A |

## AST Node Types

### Expressions (21 types)
| Node | Description |
|------|-------------|
| `LiteralExpr` | Integer, float, string, char, bool, null |
| `IdentifierExpr` | Variable reference |
| `UnaryExpr` | `-x`, `!x`, `~x`, `si x` |
| `BinaryExpr` | `a + b`, `a * b`, etc. |
| `LogicalExpr` | `a kandi b`, `a cyangwa b` |
| `AssignmentExpr` | `x = value` |
| `CompoundAssignmentExpr` | `x += value` |
| `CallExpr` | `foo(args)` |
| `ConstructorExpr` | `gukora ClassName(args)` |
| `GetExpr` | `obj.property` |
| `SetExpr` | `obj.property = value` |
| `IndexExpr` | `arr[index]` |
| `SliceExpr` | `arr[start:end]` |
| `SelfExpr` | `self` |
| `SuperExpr` | `super.method` |
| `ListExpr` | `[1, 2, 3]` |
| `DictExpr` | `{"a": 1}` |
| `TupleExpr` | `(1, 2, 3)` |
| `LambdaExpr` | `(x) => x + 1` |
| `IfExpr` | `niba cond kora expr iherezo` |
| `BlockExpr` | `kora stmts expr iherezo` |

### Statements (20 types)
| Node | Description |
|------|-------------|
| `ExpressionStmt` | Expression statement |
| `VarStmt` | Variable declaration |
| `BlockStmt` | `kora ... iherezo` |
| `IfStmt` | If/elif/else with chain |
| `WhileStmt` | While loop |
| `UntilStmt` | Until loop |
| `ForStmt` | For loop |
| `ForEachStmt` | For-each loop |
| `BreakStmt` | `gukoma` |
| `ContinueStmt` | `kugenda` |
| `ReturnStmt` | `subira` |
| `FunctionStmt` | Function declaration |
| `StructStmt` | Struct declaration |
| `EnumStmt` | Enum declaration |
| `ClassStmt` | Class declaration |
| `TraitStmt` | Trait declaration |
| `InterfaceStmt` | Interface declaration |
| `ImportStmt` | Import declaration |
| `ExportStmt` | Export declaration |
| `TryStmt` | Try/catch/finally |
| `ThrowStmt` | `gushyingura` |

## Block Structure

The I language uses `kora`...`iherezo` as block delimiters:

```i
niba x > 0 kora
    subira 1
cyangwa
    subira 0
iherezo
```

Every block must be properly terminated with `iherezo`. The parser validates:
- Blocks are properly nested
- `iherezo` matches its opening `kora`
- Missing `iherezo` produces PARS004/PARS006 errors

## Error Recovery

### Error Codes
| Code | Name | Description |
|------|------|-------------|
| PARS001 | Unexpected Token | Found token doesn't match grammar |
| PARS002 | Missing Token | Expected token not found |
| PARS003 | Invalid Expression | Expression parsing failed |
| PARS004 | Unterminated Block | Missing `iherezo` |
| PARS005 | Invalid Assignment | Invalid assignment target |
| PARS006 | Missing Block End | Block not closed with `iherezo` |
| PARS007 | Invalid Statement | Statement parsing failed |
| PARS008 | Too Many Errors | Aborted after 10 consecutive |

### Recovery Strategy
- Synchronization points at statement boundaries
- Skip tokens until next statement-starting keyword
- Continue parsing after errors when possible
- Bilingual error messages (English + Kinyarwanda)
- Max 100 errors per parse, aborts after 10 consecutive

## API Usage

### Basic Parsing
```python
from src.compiler.parser import parse

ast, errors = parse("shyira x = 42")
print(ast.statements[0])  # VarStmt
```

### Accessing AST
```python
for stmt in ast.statements:
    print(type(stmt).__name__)
    if hasattr(stmt, 'name'):
        print(f"  name: {stmt.name.lexeme}")
```

## Design Decisions

1. **Pratt Parsing**: Clean expression precedence handling, easy to add new operators
2. **Recursive Descent**: Clear statement parsing, natural grammar mapping
3. **Immutable AST**: All nodes are frozen dataclasses
4. **Source Spans**: Every node tracks its source location
5. **Kora/Iherezo**: Official block delimiters as per ILS
6. **Error Collection**: Collects all errors instead of failing on first

## Testing Strategy

- 150+ unit tests covering all grammar rules
- Expression precedence tests
- Block structure tests
- Error recovery tests
- Kinyarwanda source code tests
- Edge case tests
- Performance benchmarks

## Future Improvements

1. **Incremental parsing**: Re-parse only changed sections
2. **Comment attachment**: Preserve doc comments in AST
3. **Pattern matching**: Add match expressions
4. **Async/await**: Add coroutine support
5. **Macro system**: Add compile-time code generation
