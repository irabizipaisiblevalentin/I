# Parser Design

This document specifies the complete design of the I Programming Language parser, including grammar, parsing strategy, error recovery, and AST construction.

## Table of Contents

- [Overview](#overview)
- [Parsing Strategy](#parsing-strategy)
- [Grammar](#grammar)
- [AST Construction](#ast-construction)
- [Expression Parsing](#expression-parsing)
- [Block Parsing](#block-parsing)
- [Nested Statements](#nested-statements)
- [Error Recovery](#error-recovery)
- [Performance](#performance)
- [Testing Strategy](#testing-strategy)

## Overview

The parser transforms the token stream from the lexer into an Abstract Syntax Tree (AST). It validates that the token sequence conforms to the I language grammar and builds a hierarchical representation of the program.

### Responsibilities

1. Validate grammar rules against the token stream
2. Build hierarchical AST structure
3. Handle operator precedence and associativity
4. Recover from syntax errors to report multiple problems per run
5. Preserve documentation comments for IDE tooling
6. Track source locations for every AST node
7. Provide bilingual error messages

### Input/Output

```
Input:  List[Token] (from Lexer)
Output: Program (AST root node) + List[CompilerError]
```

## Parsing Strategy

### Parser Type: Recursive Descent with Pratt Expressions

The I parser is a hand-written recursive descent parser with a Pratt parser (precedence climbing) for expressions.

**Why recursive descent?**

1. **Full control over error messages**: Each grammar rule can produce a specific, bilingual error message
2. **Natural fit for I's grammar**: I's grammar is LL(2)-compatible, requiring at most 2 tokens of lookahead
3. **No external dependencies**: No parser generator toolchain needed
4. **Easy to extend**: Adding new grammar rules means adding new methods
5. **Debuggable**: Each method corresponds to a grammar rule, making debugging straightforward

### Lookahead

The parser uses at most **2 tokens of lookahead**. The `peek()` method returns the current token without consuming it, and `peek_next()` returns the token after the current one.

```
// Peek at current token
current = peek()

// Peek at next token (lookahead of 2)
next = peek_next()
```

### Token Consumption

```
function advance():
    token = tokens[current]
    current += 1
    return token

function expect(token_type):
    if peek().type == token_type:
        return advance()
    else:
        error(token_type)
        return synthesizeToken(token_type)  // Create synthetic token for recovery
```

## Grammar

### Complete Grammar (BNF)

```
program         ::= declaration* EOF

declaration     ::= function_decl
                  | variable_decl
                  | type_decl
                  | import_decl
                  | export_decl
                  | statement

statement       ::= expression_stmt
                  | block_stmt
                  | if_stmt
                  | while_stmt
                  | until_stmt
                  | for_stmt
                  | for_each_stmt
                  | return_stmt
                  | break_stmt
                  | continue_stmt
                  | throw_stmt
                  | try_stmt
                  | empty_stmt

function_decl   ::= 'umurimo' IDENTIFIER '(' parameters? ')' return_type? block

parameters      ::= parameter (',' parameter)*
parameter       ::= IDENTIFIER ':' type ('=' expression)?

return_type     ::= '->' type

variable_decl   ::= ('shyira' | 'shyira_ko') IDENTIFIER (':' type)? ('=' expression)?

type_decl       ::= struct_decl
                  | enum_decl
                  | class_decl
                  | trait_decl
                  | interface_decl
                  | alias_decl

struct_decl     ::= 'igiceri' IDENTIFIER struct_body
struct_body     ::= field_decl* 'iherezo'

field_decl      ::= IDENTIFIER ':' type

enum_decl       ::= 'ikindi' IDENTIFIER enum_body
enum_body       ::= variant_decl* 'iherezo'

variant_decl    ::= IDENTIFIER ('(' type_list ')')?
type_list       ::= type (',' type)*

class_decl      ::= 'urwego' IDENTIFIER ('kugira' IDENTIFIER)? class_body
class_body      ::= (field_decl | function_decl)* 'iherezo'

trait_decl      ::= 'urubingo' IDENTIFIER trait_body
trait_body      ::= function_decl* 'iherezo'

interface_decl  ::= 'akabuto' IDENTIFIER interface_body
interface_body  ::= function_signature* 'iherezo'

function_signature ::= 'umurimo' IDENTIFIER '(' parameters? ')' return_type?

alias_decl      ::= 'type' IDENTIFIER '=' type

import_decl     ::= 'shyiramo' import_source ('kugira_ngo' IDENTIFIER)?
import_source   ::= STRING | module_path
module_path     ::= IDENTIFIER ('.' IDENTIFIER)*

export_decl     ::= 'tanga' (declaration | IDENTIFIER)

block_stmt      ::= 'kora' statement* 'iherezo'

if_stmt         ::= 'niba' expression block ('cyangwa_niba' expression block)* ('cyangwa' block)?

while_stmt      ::= 'wihuse' expression block

until_stmt      ::= 'kugeza' expression block

for_stmt        ::= 'kuri' IDENTIFIER 'muri' expression 'kugeza' expression block

for_each_stmt   ::= 'buri' IDENTIFIER 'muri' expression block

return_stmt     ::= 'subira' expression?

break_stmt      ::= 'gukoma'

continue_stmt   ::= 'kugenda'

throw_stmt      ::= 'gushyingura' expression

try_stmt        ::= block_stmt 'kubika' IDENTIFIER? block_stmt ('ikinyoma' block_stmt)?

expression_stmt ::= expression

empty_stmt      ::= 'iherezo'

expression      ::= assignment
assignment      ::= logic_or (assign_op logic_or)?
assign_op       ::= '=' | '+=' | '-=' | '*=' | '/=' | '%=' | '**='

logic_or        ::= logic_and (('cyangwa' | 'or') logic_and)*
logic_and       ::= equality (('kandi' | 'and') equality)*
equality        ::= comparison (('iringaniye' | '==' | 'nta_iringani' | '!=') comparison)*
comparison      ::= term (('irenze' | '>' | 'munsi_ya' | '<' | '>=') term)*
term            ::= factor (('+' | '-') factor)*
factor          ::= unary (('*' | '/' | '%') unary)*
unary           ::= ('-' | 'si' | '!' | '~') unary | postfix
postfix         ::= primary (postfix_op)*
postfix_op      ::= '(' argument_list? ')'
                  | '[' expression ']'
                  | '.' IDENTIFIER

primary         ::= literal
                  | IDENTIFIER
                  | '(' expression ')'
                  | lambda_expr
                  | list_expr
                  | dict_expr
                  | if_expr
                  | block_expr
                  | 'gukora' IDENTIFIER '(' argument_list? ')'
                  | 'self'
                  | 'super'

literal         ::= INTEGER | FLOAT | STRING | CHAR | 'yego' | 'oya' | 'ubusa'
                  | 'true' | 'false' | 'null'

lambda_expr     ::= '(' parameters? ')' return_type? '=>' expression
list_expr       ::= '[' (expression (',' expression)*)? ']'
dict_expr       ::= '{' (IDENTIFIER ':' expression (',' IDENTIFIER ':' expression)*)? '}'
if_expr         ::= 'niba' expression '=> expression ('cyangwa' expression)?
block_expr      ::= block_stmt expression

type            ::= named_type
                  | generic_type
                  | function_type
                  | optional_type
                  | tuple_type

named_type      ::= IDENTIFIER ('.' IDENTIFIER)*
generic_type    ::= named_type '<' type (',' type)* '>'
function_type   ::= '(' (type (',' type)*)? ')' '->' type
optional_type   ::= type '?'
tuple_type      ::= '(' type (',' type)+ ')'

argument_list   ::= expression (',' expression)*
```

### Grammar Precedence (Lowest to Highest)

| Level | Productions | Associativity |
|-------|------------|---------------|
| 1 | `assignment` | Right |
| 2 | `logic_or` | Left |
| 3 | `logic_and` | Left |
| 4 | `equality` | Left |
| 5 | `comparison` | Left |
| 6 | `term` (additive) | Left |
| 7 | `factor` (multiplicative) | Left |
| 8 | `unary` | Right |
| 9 | `postfix` | Left |
| 10 | `primary` | N/A |

## AST Construction

### Parser Structure

```
Parser {
    tokens: List[Token]
    current: int
    errors: ErrorCollector
    comment_buffer: List[Token]  // pending documentation comments

    // Core methods
    parse() -> Program
    declaration() -> Declaration
    statement() -> Statement
    expression() -> Expression

    // Token manipulation
    peek() -> Token
    peek_next() -> Token
    advance() -> Token
    expect(type: TokenType) -> Token
    match(types: TokenType...) -> bool
    check(type: TokenType) -> bool
    is_at_end() -> bool

    // Error handling
    error(expected: string) -> CompilerError
    synchronize()
}
```

### Main Parse Loop

```
function parse():
    declarations = []

    while not is_at_end():
        // Collect documentation comments
        if peek().type == DOC_COMMENT:
            comment_buffer.append(advance())
            continue

        decl = declaration()
        declarations.append(decl)

    return Program(declarations, sourceLocation(0))
```

### Declaration Dispatch

```
function declaration():
    // Attach any pending documentation comments
    doc_comments = drainCommentBuffer()

    if match(KW_UMURIMO):    return function_decl(doc_comments)
    if match(KW_SHYIRA, KW_SHYIRA_KO): return variable_decl(doc_comments)
    if match(KW_IGICERI):     return struct_decl(doc_comments)
    if match(KW_IKINDI):      return enum_decl(doc_comments)
    if match(KW_URWEGO):      return class_decl(doc_comments)
    if match(KW_AKABUTO):     return interface_decl(doc_comments)
    if match(KW_URUBINGO):    return trait_decl(doc_comments)
    if match(KW_SHYIRAMO):    return import_decl(doc_comments)
    if match(KW_TANGA_EXPORT): return export_decl(doc_comments)
    if match(KW_TYPE):        return alias_decl(doc_comments)

    return statement()
```

### Statement Dispatch

```
function statement():
    if match(KW_NIBA):        return if_stmt()
    if match(KW_WIHUSE):      return while_stmt()
    if match(KW_KUGEZA):      return until_stmt()
    if match(KW_KURI):        return for_stmt()
    if match(KW_BURI):        return for_each_stmt()
    if match(KW_SUBIRA):      return return_stmt()
    if match(KW_GUKOMA):      return break_stmt()
    if match(KW_KUGENDA):      return continue_stmt()
    if match(KW_GUSHYINGURA): return throw_stmt()
    if match(KW_KORA):        return block_or_try_stmt()
    if match(KW_IHEREZO):     return empty_stmt()

    return expression_stmt()
```

## Expression Parsing

### Pratt Parser Design

The expression parser uses a Pratt parser (also known as precedence climbing). Each token type has a prefix parse function, an infix parse function, and a precedence level.

```
function parse_expression(min_precedence = 0):
    left = parse_prefix()

    while not is_at_end() and get_precedence(peek()) > min_precedence:
        op = peek()
        prec = get_precedence(op)
        consume()

        if is_right_associative(op):
            right = parse_expression(prec - 1)
        else:
            right = parse_expression(prec)

        left = BinaryExpr(left, op, right)

    return left
```

### Prefix Parse Functions

| Token | Function | Creates |
|-------|----------|---------|
| `INTEGER` | `parse_integer()` | `LiteralExpr` |
| `FLOAT` | `parse_float()` | `LiteralExpr` |
| `STRING` | `parse_string()` | `LiteralExpr` |
| `CHAR` | `parse_char()` | `LiteralExpr` |
| `BOOLEAN_TRUE` | `parse_true()` | `LiteralExpr` |
| `BOOLEAN_FALSE` | `parse_false()` | `LiteralExpr` |
| `NULL` | `parse_null()` | `LiteralExpr` |
| `IDENTIFIER` | `parse_identifier()` | `IdentifierExpr` |
| `LPAREN` | `parse_grouping()` | Grouping or tuple |
| `MINUS` | `parse_unary()` | `UnaryExpr` |
| `BANG` | `parse_unary()` | `UnaryExpr` |
| `TILDE` | `parse_unary()` | `UnaryExpr` |
| `KW_SI` | `parse_unary()` | `UnaryExpr` |
| `KW_NIBA` | `parse_if_expr()` | `IfExpr` |
| `KW_KORA` | `parse_block_expr()` | `BlockExpr` |
| `KW_GUKORA` | `parse_constructor()` | `ConstructorExpr` |
| `KW_SELF` | `parse_self()` | `SelfExpr` |
| `KW_SUPER` | `parse_super()` | `SuperExpr` |
| `LBRACKET` | `parse_list()` | `ListExpr` |
| `LBRACE` | `parse_dict()` | `DictExpr` |
| `LPAREN` (lambda) | `parse_lambda()` | `LambdaExpr` |

### Infix Parse Functions

| Token | Function | Creates |
|-------|----------|---------|
| `PLUS`, `MINUS` | `parse_binary()` | `BinaryExpr` |
| `STAR`, `SLASH`, `PERCENT` | `parse_binary()` | `BinaryExpr` |
| `STAR_STAR` | `parse_binary()` | `BinaryExpr` |
| `EQ_EQ`, `BANG_EQ` | `parse_binary()` | `BinaryExpr` |
| `GT`, `LT`, `GT_EQ`, `LT_EQ` | `parse_binary()` | `BinaryExpr` |
| `AND_AND` | `parse_binary()` | `BinaryExpr` |
| `OR_OR` | `parse_binary()` | `BinaryExpr` |
| `AMP`, `PIPE`, `CARET` | `parse_binary()` | `BinaryExpr` |
| `LT_LT`, `GT_GT` | `parse_binary()` | `BinaryExpr` |
| `EQ` | `parse_assignment()` | `AssignmentExpr` |
| `PLUS_EQ`, etc. | `parse_compound_assignment()` | `CompoundAssignmentExpr` |
| `LPAREN` | `parse_call()` | `CallExpr` |
| `LBRACKET` | `parse_index()` | `IndexExpr` |
| `DOT` | `parse_member()` | `MemberExpr` |
| `QUESTION` | `parse_ternary()` | `TernaryExpr` |

### Precedence Table

```
precedence_table = {
    // Level 1 (lowest)
    COMMA:          1,
    ASSIGN:         2,
    PLUS_EQ:        2,
    MINUS_EQ:       2,
    STAR_EQ:        2,
    SLASH_EQ:       2,
    PERCENT_EQ:     2,
    STAR_STAR_EQ:   2,

    // Level 2
    OR_OR:          3,

    // Level 3
    AND_AND:        4,

    // Level 4
    EQ_EQ:          5,
    BANG_EQ:        5,

    // Level 5
    GT:             6,
    LT:             6,
    GT_EQ:          6,
    LT_EQ:          6,

    // Level 6
    PLUS:           7,
    MINUS:          7,

    // Level 7
    STAR:           8,
    SLASH:          8,
    PERCENT:        8,

    // Level 8
    STAR_STAR:      9,

    // Level 9 (highest for infix)
    LPAREN:         10,
    LBRACKET:       10,
    DOT:            10,
}
```

## Block Parsing

### Block Structure

Blocks in I are delimited by `kora` and `iherezo`:

```
kora
    statement1
    statement2
    statement3
iherezo
```

The parser handles blocks as follows:

```
function block():
    expect(KW_KORA)
    statements = []

    while not is_at_end() and not check(KW_IHEREZO):
        stmt = declaration()
        statements.append(stmt)

    expect(KW_IHEREZO)
    return BlockStmt(statements, start_location)
```

### Nested Blocks

Blocks can be nested arbitrarily deep:

```
kora                          // Level 1
    kora                      // Level 2
        kora                  // Level 3
            statement
        iherezo               // Closes Level 3
    iherezo                   // Closes Level 2
iherezo                       // Closes Level 1
```

### Block End Detection

The parser uses `KW_IHEREZO` to detect block ends. If the parser reaches EOF before finding `iherezo`, it emits an error (PARS005) and synthesizes the missing `iherezo`.

## Nested Statements

### If-Else Chains

```
function if_stmt():
    expect(KW_NIBA)
    condition = expression()
    then_branch = block()

    else_branch = null
    elif_branches = []

    while match(KW_CYANGWA_NIBA):
        elif_condition = expression()
        elif_body = block()
        elif_branches.append((elif_condition, elif_body))

    if match(KW_CYANGWA):
        else_branch = block()

    return IfStmt(condition, then_branch, elif_branches, else_branch)
```

### Try-Catch-Finally

```
function try_stmt():
    expect(KW_KORA)  // try block uses 'kora'
    try_body = block_body()  // parse until 'kubika'

    expect(KW_KUBIKA)
    catch_var = if check(IDENTIFIER) then advance().lexeme else null
    catch_body = block_body()

    finally_body = null
    if match(KW_IKINYOMA):
        finally_body = block()

    expect(KW_IHEREZO)
    return TryStmt(try_body, catch_var, catch_body, finally_body)
```

### For Loops

```
function for_stmt():
    expect(KW_KURI)
    variable = expect(IDENTIFIER).lexeme
    expect(KW_MURI)
    start = expression()
    expect(KW_KUGEZA)
    end = expression()
    body = block()
    return ForStmt(variable, start, end, body)

function for_each_stmt():
    expect(KW_BURI)
    variable = expect(IDENTIFIER).lexeme
    expect(KW_MURI)
    iterable = expression()
    body = block()
    return ForEachStmt(variable, iterable, body)
```

## Error Recovery

### Error Recovery Strategy

The parser uses **synchronization point recovery**. When a syntax error is detected:

1. Emit the error with location and expected/found information
2. Skip tokens until reaching a synchronization point
3. Resume parsing from the synchronization point

### Synchronization Points

| Context | Synchronization Points |
|---------|----------------------|
| Statement level | `iherezo`, statement-starting keywords, `;` |
| Block level | `iherezo`, `kora` |
| Expression level | `)`, `]`, `,`, statement keywords |
| Declaration level | declaration-starting keywords |

### Recovery Algorithm

```
function synchronize():
    while not is_at_end():
        // Statement boundary
        if check(KW_IHEREZO):
            return
        if check(KW_NIBA) or check(KW_WIHUSE) or check(KW_KUGEZA) or
           check(KW_KURI) or check(KW_BURI) or check(KW_SUBIRA) or
           check(KW_GUKOMA) or check(KW_KUGENDA) or check(KW_SHYIRA) or
           check(KW_SHYIRA_KO) or check(KW_UMURIMO) or check(KW_IGICERI) or
           check(KW_IKINDI) or check(KW_URWEGO) or check(KW_AKABUTO) or
           check(KW_URUBINGO) or check(KW_SHYIRAMO) or check(KW_TANGA_EXPORT) or
           check(KW_KORA) or check(KW_GUSHYINGURA):
            return

        // Semicolon (if used in future)
        if check(SEMICOLON):
            advance()
            return

        advance()
```

### Error Types and Recovery

#### PARS001: Unexpected Token

```
Error: "Unexpected token '{found}', expected {expected} at line {line}, column {col}"
Recovery: Skip to next synchronization point
```

#### PARS002: Missing Token

```
Error: "Missing {token} at line {line}, column {col}"
Recovery: Insert synthetic token, continue parsing
```

#### PARS003: Extra Token

```
Error: "Extra token '{token}' at line {line}, column {col}"
Recovery: Skip token, continue parsing
```

#### PARS004: Invalid Expression

```
Error: "Invalid expression at line {line}, column {col}"
Recovery: Skip to next statement boundary
```

#### PARS005: Unterminated Block

```
Error: "Unterminated block starting at line {line}, column {col}"
Recovery: Insert synthetic 'iherezo' at EOF, continue
```

### Cascading Error Prevention

The parser tracks an error depth counter. If more than N (default: 10) errors occur without successfully parsing a complete statement, the parser aborts with a "too many errors" diagnostic.

## Performance

### Time Complexity

- **Parsing**: O(n) for most programs (linear scan of tokens)
- **Expression parsing**: O(n) with Pratt parser (each token is processed once)
- **Worst case**: O(n²) with backtracking (rare, only for ambiguous constructs)

### Space Complexity

- **Token storage**: O(n) for the token stream
- **AST**: O(n) for the AST nodes
- **Call stack**: O(d) for recursion depth, where d is the nesting depth
- **Total**: O(n)

### Optimization Strategies

1. **Arena allocation**: All AST nodes allocated from a single arena
2. **String interning**: Identifiers interned to save memory
3. **Minimal lookahead**: 2 tokens max, reducing peek overhead
4. **Inline helpers**: Small helper functions inlined by the compiler

## Testing Strategy

### Unit Tests

- **Grammar rules**: Test each grammar rule in isolation
- **Operator precedence**: Verify correct precedence for all operators
- **Associativity**: Verify correct associativity for all operators
- **Error recovery**: Test that errors are reported and recovery works
- **Source locations**: Verify accurate line/column tracking

### Integration Tests

- **Full programs**: Parse complete I programs
- **Edge cases**: Empty programs, deeply nested blocks, long expressions
- **Error cases**: Programs with multiple syntax errors

### Regression Tests

- **Known bugs**: Test for past parsing bugs
- **Grammar changes**: Test that grammar changes don't break existing code

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
