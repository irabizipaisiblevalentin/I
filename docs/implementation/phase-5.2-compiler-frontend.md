# Phase 5.2: Compiler Frontend Engineering Plan

**Status:** Draft
**Version:** 1.0
**Date:** July 2026
**Author:** I Engineering Team

---

## 1. Objectives

### 1.1 Primary Objectives

Implement the compiler frontend that transforms source code into an Abstract Syntax Tree (AST):

1. **Lexer**: Tokenize source code with Unicode support
2. **Parser**: Parse tokens into AST using recursive descent
3. **AST**: Complete AST node definitions
4. **AST Validation**: Validate AST structure
5. **Source Mapping**: Track source locations through compilation
6. **Unicode Support**: Full UTF-8 identifier and string support
7. **Diagnostics**: Error reporting with source snippets
8. **Error Recovery**: Graceful error recovery for better UX
9. **Testing**: Comprehensive test suite
10. **Fuzz Testing**: Fuzz testing for robustness
11. **Coverage**: Code coverage tracking

### 1.2 Quality Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| Test Coverage | > 95% | Line coverage |
| Documentation | 100% public API | Doc comments |
| Parse Success | > 99% | Valid programs |
| Error Recovery | > 90% | Recovery success |
| Fuzz Stability | 0 crashes | Fuzz testing |

### 1.3 Non-Objectives

- Semantic analysis (Phase 5.3)
- Type checking (Phase 5.4)
- Code generation (Phase 5.6)
- Optimization (Phase 5.5)

---

## 2. Engineering Design

### 2.1 Architecture Overview

```
Source Code (String)
    ↓
Lexer (Token Stream)
    ↓
Parser (AST)
    ↓
AST Validation
    ↓
Validated AST
```

### 2.2 Lexer Design

#### 2.2.1 Token Types

```rust
// Token categories
pub enum TokenKind {
    // Literals
    Integer(i64),
    Float(f64),
    String(String),
    Bool(bool),
    Null,
    
    // Identifiers
    Identifier(Symbol),
    
    // Keywords (Kinyarwanda)
    Niba,           // if
    Cyangwa,        // else
    Kora,           // do
    Iherezo,        // end
    Shyira,         // let
    Umurimo,        // function
    Igiceri,        // struct
    Urwego,         // class
    Ubwoko,         // enum
    Uburumbarizo,   // trait
    Gusangiza,      // const
    Isoko,          // import
    Subira,         // return
    Gukomeza,       // continue
    Guhagarika,     // break
    // ... more keywords
    
    // Keywords (English aliases)
    If,
    Else,
    Do,
    End,
    Let,
    Function,
    Struct,
    Class,
    Enum,
    Trait,
    Const,
    Import,
    Return,
    Continue,
    Break,
    // ... more English aliases
    
    // Operators
    Plus,           // +
    Minus,          // -
    Star,           // *
    Slash,          // /
    Percent,        // %
    PlusEq,         // +=
    MinusEq,        // -=
    StarEq,         // *=
    SlashEq,        // /=
    Eq,             // =
    EqEq,           // ==
    NotEq,          // !=
    Lt,             // <
    Gt,             // >
    LtEq,           // <=
    GtEq,           // >=
    And,            // &&
    Or,             // ||
    Not,            // !
    BitAnd,         // &
    BitOr,          // |
    BitXor,         // ^
    BitNot,         // ~
    Shl,            // <<
    Shr,            // >>
    Arrow,          // ->
    FatArrow,       // =>
    Colon,          // :
    ColonColon,     // ::
    Dot,            // .
    Comma,          // ,
    Semicolon,      // ;
    LParen,         // (
    RParen,         // )
    LBrace,         // {
    RBrace,         // }
    LBracket,       // [
    RBracket,       // ]
    
    // Special
    Eof,
    Error(String),
}
```

#### 2.2.2 Lexer State Machine

```
Start → [whitespace] → Start
Start → [letter] → Identifier
Start → [digit] → Number
Start → ['"'] → String
Start → [operator] → Operator
Start → [delimiter] → Delimiter
Start → [newline] → Newline
Start → [eof] → Eof
```

#### 2.2.3 Unicode Support

- Full UTF-8 source code support
- Unicode identifiers (Kinyarwanda characters)
- Unicode string escapes
- Unicode normalization

### 2.3 Parser Design

#### 2.3.1 Parsing Strategy

- **Algorithm**: Recursive descent
- **Expression Parsing**: Pratt parser
- **Lookahead**: LL(2) (2 tokens)
- **Error Recovery**: Panic mode with synchronizing tokens

#### 2.3.2 Grammar Structure

```
Program → Declaration*
Declaration → FunctionDecl | StructDecl | ClassDecl | EnumDecl | 
              TraitDecl | VarDecl | ConstDecl | ImportDecl | Statement
Statement → ExprStatement | ReturnStatement | IfStatement | 
            WhileStatement | ForStatement | Block | Break | Continue
Block → '{' Declaration* '}'
Expression → Assignment
Assignment → Identifier '=' Assignment | LogicOr
LogicOr → LogicAnd ('||' LogicAnd)*
LogicAnd → Equality ('&&' Equality)*
Equality → Comparison (('==' | '!=') Comparison)*
Comparison → Addition (('<' | '>' | '<=' | '>=') Addition)*
Addition → Multiplication (('+' | '-') Multiplication)*
Multiplication → Unary (('*' | '/' | '%') Unary)*
Unary → ('-' | '!' | '~') Unary | Call
Call → Primary ('(' Arguments? ')')*
Primary → Number | String | Bool | Null | Identifier | '(' Expression ')'
```

#### 2.3.3 Precedence Levels

| Level | Operators | Associativity |
|-------|-----------|---------------|
| 1 | `||` | Left |
| 2 | `&&` | Left |
| 3 | `==`, `!=` | Left |
| 4 | `<`, `>`, `<=`, `>=` | Left |
| 5 | `+`, `-` | Left |
| 6 | `*`, `/`, `%` | Left |
| 7 | `-`, `!`, `~` | Right |
| 8 | Function call | Left |
| 9 | Primary | - |

### 2.4 AST Design

#### 2.4.1 AST Node Types

```rust
// Program
pub struct Program {
    pub declarations: Vec<Declaration>,
    pub span: Span,
}

// Declarations
pub enum Declaration {
    Function(FunctionDecl),
    Struct(StructDecl),
    Class(ClassDecl),
    Enum(EnumDecl),
    Trait(TraitDecl),
    Variable(VarDecl),
    Constant(ConstDecl),
    Import(ImportDecl),
    Statement(Statement),
}

// Statements
pub enum Statement {
    Expression(ExprStatement),
    Return(ReturnStatement),
    If(IfStatement),
    While(WhileStatement),
    For(ForStatement),
    Block(Block),
    Break(BreakStatement),
    Continue(ContinueStatement),
}

// Expressions
pub enum Expression {
    Literal(Literal),
    Identifier(Identifier),
    Binary(BinaryExpr),
    Unary(UnaryExpr),
    Call(CallExpr),
    Index(IndexExpr),
    Field(FieldExpr),
    Assign(AssignExpr),
    If(IfExpr),
    Block(BlockExpr),
}
```

#### 2.4.2 Span Tracking

Every AST node contains a `Span` for source location tracking:

```rust
pub struct Span {
    pub start: u32,
    pub end: u32,
    pub file_id: FileId,
}
```

---

## 3. File Structure

### 3.1 Crate Structure

```
crates/
├── ilang-lexer/
│   ├── Cargo.toml
│   ├── src/
│   │   ├── lib.rs
│   │   ├── token.rs
│   │   ├── lexer.rs
│   │   ├── cursor.rs
│   │   ├── unicode.rs
│   │   └── error.rs
│   └── tests/
│       ├── lexer_tests.rs
│       └── unicode_tests.rs
├── ilang-parser/
│   ├── Cargo.toml
│   ├── src/
│   │   ├── lib.rs
│   │   ├── parser.rs
│   │   ├── expression.rs
│   │   ├── statement.rs
│   │   ├── declaration.rs
│   │   ├── recovery.rs
│   │   └── error.rs
│   └── tests/
│       ├── parser_tests.rs
│       └── recovery_tests.rs
└── ilang-ast/
    ├── Cargo.toml
    ├── src/
    │   ├── lib.rs
    │   ├── program.rs
    │   ├── declaration.rs
    │   ├── statement.rs
    │   ├── expression.rs
    │   ├── types.rs
    │   ├── patterns.rs
    │   └── visitor.rs
    └── tests/
        └── ast_tests.rs
```

### 3.2 Key Files

```toml
# crates/ilang-lexer/Cargo.toml
[package]
name = "ilang-lexer"
version.workspace = true
edition.workspace = true

[dependencies]
ilang-core = { workspace = true }
ilang-diagnostics = { workspace = true }
unicode-segmentation = "1.10"

[dev-dependencies]
ilang-test = { workspace = true }
```

```toml
# crates/ilang-parser/Cargo.toml
[package]
name = "ilang-parser"
version.workspace = true
edition.workspace = true

[dependencies]
ilang-core = { workspace = true }
ilang-ast = { workspace = true }
ilang-lexer = { workspace = true }
ilang-diagnostics = { workspace = true }
```

```toml
# crates/ilang-ast/Cargo.toml
[package]
name = "ilang-ast"
version.workspace = true
edition.workspace = true

[dependencies]
ilang-core = { workspace = true }
```

---

## 4. Implementation Plan

### 4.1 Implementation Order

| Step | Component | Dependencies | Estimate |
|------|-----------|--------------|----------|
| 1 | AST definitions | ilang-core | 3 days |
| 2 | Token definitions | ilang-core | 1 day |
| 3 | Lexer cursor | ilang-core | 2 days |
| 4 | Lexer core | cursor, tokens | 5 days |
| 5 | Lexer Unicode | lexer core | 2 days |
| 6 | Lexer tests | lexer | 2 days |
| 7 | Parser core | lexer, AST | 5 days |
| 8 | Expression parser | parser core | 5 days |
| 9 | Statement parser | parser core | 3 days |
| 10 | Declaration parser | parser core | 3 days |
| 11 | Error recovery | parser | 3 days |
| 12 | Parser tests | parser | 3 days |
| 13 | AST validation | AST | 2 days |
| 14 | Fuzz testing | lexer, parser | 2 days |
| 15 | Documentation | all | 3 days |
| 16 | Benchmarks | all | 2 days |

**Total Estimated Duration:** 46 days (9 weeks)

### 4.2 Detailed Implementation Steps

#### Step 1: AST Definitions (3 days)

```rust
// crates/ilang-ast/src/lib.rs

pub mod program;
pub mod declaration;
pub mod statement;
pub mod expression;
pub mod types;
pub mod patterns;
pub mod visitor;
pub mod span;

pub use program::*;
pub use declaration::*;
pub use statement::*;
pub use expression::*;
pub use types::*;
pub use patterns::*;
pub use visitor::*;
pub use span::*;
```

#### Step 2: Token Definitions (1 day)

```rust
// crates/ilang-lexer/src/token.rs

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Token {
    pub kind: TokenKind,
    pub span: Span,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TokenKind {
    // ... as defined in section 2.2.1
}
```

#### Step 3: Lexer Cursor (2 days)

```rust
// crates/ilang-lexer/src/cursor.rs

pub struct Cursor<'a> {
    source: &'a str,
    position: usize,
    line: u32,
    column: u32,
}

impl<'a> Cursor<'a> {
    pub fn new(source: &'a str) -> Self { ... }
    pub fn peek(&self) -> Option<char> { ... }
    pub fn advance(&mut self) -> Option<char> { ... }
    pub fn peek_ahead(&self, n: usize) -> Option<char> { ... }
    pub fn is_at_end(&self) -> bool { ... }
    pub fn span(&self, start: usize) -> Span { ... }
}
```

#### Step 4-5: Lexer Core (7 days)

```rust
// crates/ilang-lexer/src/lexer.rs

pub struct Lexer<'a> {
    cursor: Cursor<'a>,
    source_id: FileId,
}

impl<'a> Lexer<'a> {
    pub fn new(source: &'a str, source_id: FileId) -> Self { ... }
    
    pub fn next_token(&mut self) -> Token { ... }
    
    pub fn peek_token(&self) -> &Token { ... }
    
    fn read_identifier(&mut self) -> TokenKind { ... }
    fn read_number(&mut self) -> TokenKind { ... }
    fn read_string(&mut self) -> TokenKind { ... }
    fn read_operator(&mut self) -> TokenKind { ... }
    fn read_comment(&mut self) { ... }
    fn skip_whitespace(&mut self) { ... }
}
```

#### Step 7-12: Parser (22 days)

```rust
// crates/ilang-parser/src/parser.rs

pub struct Parser<'a> {
    lexer: Lexer<'a>,
    current: Token,
    peek: Token,
    diagnostics: &'a mut DiagnosticHandler,
}

impl<'a> Parser<'a> {
    pub fn new(lexer: Lexer<'a>, diagnostics: &'a mut DiagnosticHandler) -> Self { ... }
    
    pub fn parse_program(&mut self) -> Result<Program, ParseError> { ... }
    
    fn parse_declaration(&mut self) -> Result<Declaration, ParseError> { ... }
    fn parse_statement(&mut self) -> Result<Statement, ParseError> { ... }
    fn parse_expression(&mut self) -> Result<Expression, ParseError> { ... }
    
    fn advance(&mut self) -> Token { ... }
    fn peek(&self) -> &Token { ... }
    fn expect(&mut self, kind: TokenKind) -> Result<Token, ParseError> { ... }
    fn synchronize(&mut self) { ... }  // Error recovery
}
```

---

## 5. Task Breakdown

### 5.1 Task List

| ID | Task | Priority | Estimate | Dependencies |
|----|------|----------|----------|--------------|
| 5.2.1 | Implement AST definitions | Critical | 3 days | - |
| 5.2.2 | Implement token definitions | Critical | 1 day | - |
| 5.2.3 | Implement lexer cursor | Critical | 2 days | - |
| 5.2.4 | Implement lexer core | Critical | 5 days | 5.2.2, 5.2.3 |
| 5.2.5 | Implement Unicode support | Critical | 2 days | 5.2.4 |
| 5.2.6 | Write lexer tests | Critical | 2 days | 5.2.4, 5.2.5 |
| 5.2.7 | Implement parser core | Critical | 5 days | 5.2.1, 5.2.4 |
| 5.2.8 | Implement expression parser | Critical | 5 days | 5.2.7 |
| 5.2.9 | Implement statement parser | Critical | 3 days | 5.2.7 |
| 5.2.10 | Implement declaration parser | Critical | 3 days | 5.2.7 |
| 5.2.11 | Implement error recovery | High | 3 days | 5.2.7 |
| 5.2.12 | Write parser tests | Critical | 3 days | 5.2.7-5.2.11 |
| 5.2.13 | Implement AST validation | High | 2 days | 5.2.1 |
| 5.2.14 | Write fuzz tests | High | 2 days | 5.2.4, 5.2.7 |
| 5.2.15 | Write documentation | High | 3 days | All above |
| 5.2.16 | Write benchmarks | Medium | 2 days | All above |

**Total Estimated Duration:** 46 days (9 weeks)

### 5.2 Milestone Schedule

| Milestone | Date | Tasks |
|-----------|------|-------|
| M5.2.1 | Week 1-2 | 5.2.1, 5.2.2, 5.2.3 |
| M5.2.2 | Week 3-4 | 5.2.4, 5.2.5, 5.2.6 |
| M5.2.3 | Week 5-7 | 5.2.7, 5.2.8, 5.2.9, 5.2.10 |
| M5.2.4 | Week 8 | 5.2.11, 5.2.12, 5.2.13 |
| M5.2.5 | Week 9 | 5.2.14, 5.2.15, 5.2.16 |

---

## 6. Testing Strategy

### 6.1 Test Types

| Type | Coverage Target | Description |
|------|-----------------|-------------|
| Lexer Unit Tests | 95% | Token production tests |
| Parser Unit Tests | 95% | AST production tests |
| Integration Tests | 90% | End-to-end parse tests |
| Error Recovery Tests | 85% | Error handling tests |
| Fuzz Tests | N/A | Random input testing |
| Unicode Tests | 100% | Unicode handling tests |
| Snapshot Tests | 100% | AST output tests |

### 6.2 Test Examples

```rust
// Lexer test
#[test]
fn test_lex_identifier() {
    let mut lexer = Lexer::new("hello", FileId(0));
    let token = lexer.next_token();
    assert_eq!(token.kind, TokenKind::Identifier(Symbol(0)));
}

// Parser test
#[test]
fn test_parse_function() {
    let source = "umurimo add(a: int, b: int) -> int { subira a + b; }";
    let mut parser = create_parser(source);
    let program = parser.parse_program().unwrap();
    assert_eq!(program.declarations.len(), 1);
}

// Error recovery test
#[test]
fn test_error_recovery() {
    let source = "umurimo add(a: int, b: int) { }";
    let mut parser = create_parser(source);
    let result = parser.parse_program();
    assert!(result.is_err());
    // Check that parsing continues after error
}
```

### 6.3 Fuzz Testing

```rust
// Fuzz target
fuzz_target!(|data: &[u8]| {
    if let Ok(s) = std::str::from_utf8(data) {
        let mut lexer = Lexer::new(s, FileId(0));
        loop {
            let token = lexer.next_token();
            if token.kind == TokenKind::Eof {
                break;
            }
        }
    }
});
```

---

## 7. Security Considerations

### 7.1 Security Requirements

| Requirement | Description | Verification |
|-------------|-------------|--------------|
| Input Validation | All source code validated | Unit tests |
| Unicode Safety | No Unicode exploits | Fuzz testing |
| Memory Safety | No buffer overflows | Clippy audit |
| DoS Prevention | No exponential blowup | Timeouts |
| Error Messages | No code injection | Static analysis |

### 7.2 Security Considerations

1. **Unicode Normalization**: Prevent normalization attacks
2. **String Length Limits**: Prevent DoS via huge strings
3. **Recursion Limits**: Prevent stack overflow
4. **Token Limits**: Prevent memory exhaustion
5. **Error Message Safety**: Ensure error messages are safe

---

## 8. Performance Considerations

### 8.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Lexing Speed | > 100 MB/s | Throughput |
| Parsing Speed | > 50 MB/s | Throughput |
| Memory Usage | < 100 MB | Peak memory |
| Startup Time | < 10ms | Cold start |

### 8.2 Optimization Strategies

1. **Zero-Copy Lexing**: Borrow source strings
2. **Incremental Parsing**: Parse only changed regions
3. **Memory Pooling**: Pool AST nodes
4. **Parallel Lexing**: Lex in parallel for large files
5. **Caching**: Cache parsed results

---

## 9. Documentation Requirements

### 9.1 Documentation Types

| Type | Location | Audience |
|------|----------|----------|
| API Documentation | Source code | Developers |
| Lexer Guide | docs/lexer.md | Contributors |
| Parser Guide | docs/parser.md | Contributors |
| AST Reference | docs/ast.md | Contributors |
| Error Recovery | docs/recovery.md | Contributors |

### 9.2 Documentation Examples

```rust
/// Lexes the next token from the source code.
///
/// # Arguments
///
/// * `cursor` - The cursor to read from
///
/// # Returns
///
/// The next token, or `TokenKind::Eof` if at end of input.
///
/// # Errors
///
/// Returns `TokenKind::Error` if the input is invalid.
///
/// # Examples
///
/// ```
/// let mut lexer = Lexer::new("hello + world", FileId(0));
/// assert_eq!(lexer.next_token().kind, TokenKind::Identifier(...));
/// assert_eq!(lexer.next_token().kind, TokenKind::Plus);
/// ```
pub fn next_token(&mut self) -> Token {
    // Implementation
}
```

---

## 10. Definition of Done

### 10.1 Phase 5.2 is complete when:

- [ ] All crates implemented and compiling
- [ ] Unit tests passing (> 95% coverage)
- [ ] Integration tests passing
- [ ] Error recovery working
- [ ] Unicode support complete
- [ ] Documentation complete
- [ ] Examples working
- [ ] Benchmarks established
- [ ] Fuzz tests stable (0 crashes)
- [ ] Cross-platform testing passing
- [ ] Security review complete
- [ ] Performance review complete
- [ ] Code review complete
- [ ] Changelog updated
- [ ] Release notes drafted

### 10.2 Quality Gates

| Gate | Requirement | Status |
|------|-------------|--------|
| Build | Clean build passes | - |
| Tests | All tests pass | - |
| Coverage | > 95% | - |
| Lint | No warnings | - |
| Format | Formatted | - |
| Docs | All public API documented | - |
| Fuzz | 0 crashes | - |
| Bench | Benchmarks pass | - |
| Security | No vulnerabilities | - |
| Review | Code reviewed | - |

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
