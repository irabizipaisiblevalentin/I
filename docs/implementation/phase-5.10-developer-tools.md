# Phase 5.10: Developer Tools Engineering Plan

**Status:** Draft
**Version:** 1.0
**Date:** July 2026
**Author:** I Engineering Team

---

## 1. Objectives

### 1.1 Primary Objectives

Implement the complete developer tooling ecosystem:

1. **Language Server Protocol (LSP)**: IDE support
2. **Formatter (iformat)**: Code formatting
3. **Linter**: Code quality checks
4. **Debugger (idebug)**: Runtime debugging
5. **Test Runner (itest)**: Test execution
6. **Documentation Generator (idoc)**: API documentation
7. **Build System**: Project compilation
8. **Code Analysis**: Static analysis
9. **Editor Extensions**: VSCode, Vim, etc.
10. **CLI Interface**: Command-line tools

### 1.2 Quality Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| Test Coverage | > 90% | Line coverage |
| Documentation | 100% public API | Doc comments |
| Tool Count | 10+ tools | Tool count |
| IDE Support | 3+ editors | Editor support |

### 1.3 Non-Objectives

- IDE implementation (Future)
- Cloud IDE (Future)
- Mobile development (Future)

---

## 2. Engineering Design

### 2.1 Architecture Overview

```
Developer Tools
    ├── LSP Server (ilang-lsp)
    ├── Formatter (iformat)
    ├── Linter (ilang-lint)
    ├── Debugger (idebug)
    ├── Test Runner (itest)
    ├── Doc Generator (idoc)
    ├── Build System (ibuild)
    ├── Code Analyzer (ianalyze)
    └── CLI Interface (ilang)
```

### 2.2 Language Server Protocol (LSP)

```rust
// LSP server implementation
pub struct LspServer {
    connection: Connection,
    capabilities: ServerCapabilities,
}

impl LspServer {
    pub fn new() -> Self {
        let capabilities = ServerCapabilities {
            text_document_sync: Some(TextDocumentSyncCapability::Kind(
                TextDocumentSyncKind::Full,
            )),
            completion_provider: Some(CompletionOptions {
                resolve_provider: Some(true),
                trigger_characters: Some(vec![".".to_string()]),
                work_done_progress_options: WorkDoneProgressOptions::default(),
            }),
            hover_provider: Some(OneOf::Left(true)),
            definition_provider: Some(OneOf::Left(true)),
            type_definition_provider: Some(OneOf::Left(true)),
            references_provider: Some(OneOf::Left(true)),
            document_highlight_provider: Some(OneOf::Left(true)),
            document_symbol_provider: Some(OneOf::Left(true)),
            workspace_symbol_provider: Some(OneOf::Left(true)),
            code_action_provider: Some(CodeActionProviderCapability::Simple(true)),
            code_lens_provider: Some(CodeLensOptions {
                resolve_provider: Some(true),
            }),
            document_formatting_provider: Some(OneOf::Left(true)),
            document_range_formatting_provider: Some(OneOf::Left(true)),
            rename_provider: Some(OneOf::Left(true)),
            ..Default::default()
        };

        Self {
            connection: Connection::stdio(),
            capabilities,
        }
    }

    pub fn run(&self) -> Result<(), LspError> {
        let (initialize_id, initialize_params) = self.connection.initialize_start()?;
        let init_result = self.handle_initialize(&initialize_params);
        self.connection.initialize_finish(initialize_id, init_result)?;
        
        loop {
            match self.connection.receiver.recv() {
                Ok(Message::Request(req)) => {
                    if self.connection.handle_shutdown(&req)? {
                        return Ok(());
                    }
                    self.handle_request(req)?;
                }
                Ok(Message::Response(_)) => {}
                Ok(Message::Notification(not)) => {
                    self.handle_notification(not)?;
                }
                Err(_) => return Ok(()),
            }
        }
    }
}
```

### 2.3 Formatter

```rust
// Code formatter
pub struct Formatter {
    config: FormatConfig,
}

impl Formatter {
    pub fn new(config: FormatConfig) -> Self {
        Self { config }
    }

    pub fn format(&self, source: &str) -> Result<String, FormatterError> {
        let mut parser = Parser::new(source);
        let ast = parser.parse()?;
        
        let mut formatter = AstFormatter::new(&self.config);
        formatter.format(&ast)
    }
}

// Format configuration
pub struct FormatConfig {
    pub indent_size: usize,
    pub max_line_length: usize,
    pub use_tabs: bool,
    pub trailing_comma: bool,
    pub space_before_paren: bool,
}

impl Default for FormatConfig {
    fn default() -> Self {
        Self {
            indent_size: 4,
            max_line_length: 80,
            use_tabs: false,
            trailing_comma: true,
            space_before_paren: false,
        }
    }
}
```

### 2.4 Linter

```rust
// Linter implementation
pub struct Linter {
    rules: Vec<Box<dyn Rule>>,
}

impl Linter {
    pub fn new() -> Self {
        let mut rules: Vec<Box<dyn Rule>> = Vec::new();
        
        // Add default rules
        rules.push(Box::new(CamelCaseRule));
        rules.push(Box::new(UnusedVariableRule));
        rules.push(Box::new(DeadCodeRule));
        rules.push(Box::new(UnsafeCodeRule));
        rules.push(Box::new(CodeStyleRule));
        
        Self { rules }
    }

    pub fn lint(&self, source: &str) -> Result<Vec<Diagnostic>, LintError> {
        let mut parser = Parser::new(source);
        let ast = parser.parse()?;
        
        let mut diagnostics = Vec::new();
        for rule in &self.rules {
            diagnostics.extend(rule.check(&ast)?);
        }
        
        Ok(diagnostics)
    }
}

// Rule trait
pub trait Rule {
    fn name(&self) -> &str;
    fn check(&self, ast: &Ast) -> Result<Vec<Diagnostic>, LintError>;
    fn severity(&self) -> Severity;
    fn category(&self) -> Category;
}
```

### 2.5 Debugger

```rust
// Debugger implementation
pub struct Debugger {
    session: DebugSession,
    breakpoints: Vec<Breakpoint>,
}

impl Debugger {
    pub fn new(program: &str) -> Result<Self, DebugError> {
        let bytecode = compile_program(program)?;
        let session = DebugSession::new(bytecode);
        
        Ok(Self {
            session,
            breakpoints: Vec::new(),
        })
    }

    pub fn run(&mut self) -> Result<(), DebugError> {
        loop {
            match self.session.status() {
                Status::Running => {
                    self.session.step()?;
                }
                Status::Paused => {
                    let event = self.session.wait_for_event()?;
                    self.handle_event(event)?;
                }
                Status::Finished => {
                    return Ok(());
                }
            }
        }
    }

    pub fn add_breakpoint(&mut self, file: &str, line: usize) -> Result<(), DebugError> {
        let bp = Breakpoint {
            id: self.breakpoints.len(),
            file: file.to_string(),
            line,
            enabled: true,
        };
        self.breakpoints.push(bp);
        Ok(())
    }

    pub fn step_over(&mut self) -> Result<(), DebugError> {
        self.session.step_over()
    }

    pub fn step_into(&mut self) -> Result<(), DebugError> {
        self.session.step_into()
    }

    pub fn step_out(&mut self) -> Result<(), DebugError> {
        self.session.step_out()
    }

    pub fn evaluate(&self, expression: &str) -> Result<Value, DebugError> {
        self.session.evaluate(expression)
    }
}
```

### 2.6 Test Runner

```rust
// Test runner implementation
pub struct TestRunner {
    config: TestConfig,
}

impl TestRunner {
    pub fn new(config: TestConfig) -> Self {
        Self { config }
    }

    pub fn run(&self, path: &Path) -> Result<TestResults, TestError> {
        let test_files = self.find_test_files(path)?;
        let mut results = TestResults::new();
        
        for test_file in &test_files {
            let file_results = self.run_file(test_file)?;
            results.merge(file_results);
        }
        
        Ok(results)
    }

    fn run_file(&self, path: &Path) -> Result<TestResults, TestError> {
        let source = std::fs::read_to_string(path)?;
        let tests = self.parse_tests(&source)?;
        
        let mut results = TestResults::new();
        for test in tests {
            let result = self.run_test(&test)?;
            results.add(result);
        }
        
        Ok(results)
    }

    fn run_test(&self, test: &Test) -> Result<TestResult, TestError> {
        let start = std::time::Instant::now();
        
        match self.execute_test(test) {
            Ok(output) => Ok(TestResult {
                name: test.name.clone(),
                status: TestStatus::Passed,
                duration: start.elapsed(),
                output,
            }),
            Err(error) => Ok(TestResult {
                name: test.name.clone(),
                status: TestStatus::Failed,
                duration: start.elapsed(),
                output: error.to_string(),
            }),
        }
    }
}

// Test results
pub struct TestResults {
    pub passed: usize,
    pub failed: usize,
    pub ignored: usize,
    pub duration: Duration,
    pub tests: Vec<TestResult>,
}

impl TestResults {
    pub fn summary(&self) -> String {
        format!(
            "{} passed, {} failed, {} ignored in {:.2}s",
            self.passed, self.failed, self.ignored, self.duration.as_secs_f64()
        )
    }
}
```

### 2.7 Documentation Generator

```rust
// Documentation generator
pub struct DocGenerator {
    config: DocConfig,
}

impl DocGenerator {
    pub fn new(config: DocConfig) -> Self {
        Self { config }
    }

    pub fn generate(&self, path: &Path) -> Result<(), DocError> {
        let source = std::fs::read_to_string(path)?;
        let ast = Parser::new(&source).parse()?;
        
        let doc_items = self.extract_docs(&ast)?;
        
        match self.config.format {
            DocFormat::Markdown => self.generate_markdown(&doc_items, path)?,
            DocFormat::Html => self.generate_html(&doc_items, path)?,
            DocFormat::Json => self.generate_json(&doc_items, path)?,
        }
        
        Ok(())
    }

    fn extract_docs(&self, ast: &Ast) -> Result<Vec<DocItem>, DocError> {
        let mut items = Vec::new();
        
        for node in ast.nodes() {
            match node {
                Node::Function(func) => {
                    items.push(DocItem::Function {
                        name: func.name.clone(),
                        description: func.doc_comment.clone(),
                        parameters: self.extract_params(func)?,
                        return_type: func.return_type.clone(),
                        examples: self.extract_examples(func)?,
                    });
                }
                Node::Struct(struct) => {
                    items.push(DocItem::Struct {
                        name: struct.name.clone(),
                        description: struct.doc_comment.clone(),
                        fields: self.extract_fields(struct)?,
                        methods: self.extract_methods(struct)?,
                        examples: self.extract_examples(struct)?,
                    });
                }
                // ... more nodes
            }
        }
        
        Ok(items)
    }
}
```

---

## 3. File Structure

### 3.1 Crate Structure

```
crates/
├── ilang-lsp/
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── main.rs
│       ├── server.rs
│       ├── handlers.rs
│       └── capabilities.rs
├── ilang-formatter/
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── config.rs
│       └── formatter.rs
├── ilang-lint/
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── rules/
│       └── linter.rs
├── ilang-debug/
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── main.rs
│       ├── session.rs
│       └── breakpoints.rs
├── ilang-test/
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── main.rs
│       ├── runner.rs
│       └── results.rs
├── ilang-doc/
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── main.rs
│       └── generator.rs
└── ilang-cli/
    ├── Cargo.toml
    └── src/
        ├── main.rs
        └── commands/
```

### 3.2 Key Files

```toml
# crates/ilang-lsp/Cargo.toml
[package]
name = "ilang-lsp"
version.workspace = true
edition.workspace = true

[[bin]]
name = "ilang-lsp"
path = "src/main.rs"

[dependencies]
ilang-core = { workspace = true }
ilang-lexer = { workspace = true }
ilang-parser = { workspace = true }
ilang-analyzer = { workspace = true }
ilang-types = { workspace = true }
lsp-types = "0.94"
lsp-server = "0.7"
serde = { version = "1.0", features = ["derive"] }
```

---

## 4. Implementation Plan

### 4.1 Implementation Order

| Step | Component | Dependencies | Estimate |
|------|-----------|--------------|----------|
| 1 | LSP server | all compiler crates | 5 days |
| 2 | Formatter | ilang-parser | 3 days |
| 3 | Linter | ilang-parser | 4 days |
| 4 | Debugger | ilang-vm | 4 days |
| 5 | Test runner | ilang-vm | 3 days |
| 6 | Doc generator | ilang-parser | 3 days |
| 7 | Build system | all above | 3 days |
| 8 | CLI interface | all above | 3 days |
| 9 | Editor extensions | LSP | 4 days |
| 10 | Unit tests | all above | 5 days |
| 11 | Integration tests | all above | 3 days |
| 12 | Documentation | all above | 4 days |

**Total Estimated Duration:** 44 days (9 weeks)

### 4.2 Detailed Implementation Steps

#### Step 1: LSP Server (5 days)

```rust
// crates/ilang-lsp/src/server.rs

pub struct LspServer {
    connection: Connection,
    state: ServerState,
}

struct ServerState {
    documents: HashMap<Url, Document>,
    analysis: Analysis,
}

impl LspServer {
    pub fn run(&mut self) -> Result<(), LspError> {
        // Initialize
        let (id, params) = self.connection.initialize_start()?;
        let init_result = self.handle_initialize(&params);
        self.connection.initialize_finish(id, init_result)?;
        
        // Main loop
        for msg in &self.connection.receiver {
            match msg {
                Message::Request(req) => {
                    if self.connection.handle_shutdown(&req)? {
                        return Ok(());
                    }
                    self.handle_request(req)?;
                }
                Message::Response(_resp) => {}
                Message::Notification(not) => {
                    self.handle_notification(not)?;
                }
            }
        }
        
        Ok(())
    }
    
    fn handle_request(&mut self, req: Request) -> Result<(), LspError> {
        match req.method.as_str() {
            "textDocument/completion" => {
                let params: CompletionParams = serde_json::from_value(req.params)?;
                let result = self.completion(&params)?;
                self.connection.sender.send(Message::Response(Response {
                    id: req.id,
                    result: Some(serde_json::to_value(result)?),
                    error: None,
                }))?;
            }
            "textDocument/hover" => {
                let params: HoverParams = serde_json::from_value(req.params)?;
                let result = self.hover(&params)?;
                self.connection.sender.send(Message::Response(Response {
                    id: req.id,
                    result: Some(serde_json::to_value(result)?),
                    error: None,
                }))?;
            }
            // ... more handlers
        }
        Ok(())
    }
}
```

#### Step 2: Formatter (3 days)

```rust
// crates/ilang-formatter/src/formatter.rs

pub struct AstFormatter<'a> {
    config: &'a FormatConfig,
    indent_level: usize,
}

impl<'a> AstFormatter<'a> {
    pub fn new(config: &'a FormatConfig) -> Self {
        Self {
            config,
            indent_level: 0,
        }
    }

    pub fn format(&mut self, ast: &Ast) -> Result<String, FormatterError> {
        let mut output = String::new();
        for node in ast.nodes() {
            self.format_node(node, &mut output)?;
        }
        Ok(output)
    }

    fn format_node(&mut self, node: &Node, output: &mut String) -> Result<(), FormatterError> {
        match node {
            Node::Function(func) => self.format_function(func, output)?,
            Node::Struct(s) => self.format_struct(s, output)?,
            Node::Expression(expr) => self.format_expression(expr, output)?,
            Node::Statement(stmt) => self.format_statement(stmt, output)?,
        }
        Ok(())
    }

    fn format_function(&mut self, func: &Function, output: &mut String) -> Result<(), FormatterError> {
        // Format function
        output.push_str("umurimo ");
        output.push_str(&func.name);
        output.push('(');
        
        for (i, param) in func.params.iter().enumerate() {
            if i > 0 {
                output.push_str(", ");
            }
            self.format_parameter(param, output)?;
        }
        
        output.push_str(") -> ");
        self.format_type(&func.return_type, output)?;
        output.push_str(" kora\n");
        
        self.indent_level += 1;
        self.format_block(&func.body, output)?;
        self.indent_level -= 1;
        
        output.push_str(&self.indent());
        output.push_str("iherezo\n");
        
        Ok(())
    }
}
```

---

## 5. Task Breakdown

### 5.1 Task List

| ID | Task | Priority | Estimate | Dependencies |
|----|------|----------|----------|--------------|
| 5.10.1 | Implement LSP server | Critical | 5 days | - |
| 5.10.2 | Implement formatter | Critical | 3 days | - |
| 5.10.3 | Implement linter | High | 4 days | - |
| 5.10.4 | Implement debugger | Critical | 4 days | - |
| 5.10.5 | Implement test runner | Critical | 3 days | - |
| 5.10.6 | Implement doc generator | High | 3 days | - |
| 5.10.7 | Implement build system | High | 3 days | All above |
| 5.10.8 | Implement CLI interface | Critical | 3 days | All above |
| 5.10.9 | Implement editor extensions | Medium | 4 days | 5.10.1 |
| 5.10.10 | Write unit tests | Critical | 5 days | All above |
| 5.10.11 | Write integration tests | Critical | 3 days | All above |
| 5.10.12 | Write documentation | High | 4 days | All above |

**Total Estimated Duration:** 44 days (9 weeks)

### 5.2 Milestone Schedule

| Milestone | Date | Tasks |
|-----------|------|-------|
| M5.10.1 | Week 1-2 | 5.10.1, 5.10.2, 5.10.3 |
| M5.10.2 | Week 3-4 | 5.10.4, 5.10.5, 5.10.6 |
| M5.10.3 | Week 5-6 | 5.10.7, 5.10.8, 5.10.9 |
| M5.10.4 | Week 7-9 | 5.10.10, 5.10.11, 5.10.12 |

---

## 6. CLI Commands

### 6.1 Command List

```bash
# Compiler
ilang compile <file.i>
ilang run <file.i>
ilang build

# Package Manager
ilang init
ilang add <package>
ilang remove <package>
ilang install
ilang update

# Formatter
iformat <file.i>
iformat --check <file.i>

# Linter
ilang lint <file.i>
ilang lint --fix <file.i>

# Debugger
idebug <file.i>
idebug --breakpoint <file>:<line> <file.i>

# Test Runner
itest
itest <file.i>
itest --filter <pattern>

# Documentation Generator
idoc <file.i>
idoc --format html <file.i>

# Language Server
ilang-lsp
```

---

## 7. Testing Strategy

### 7.1 Test Types

| Type | Coverage Target | Description |
|------|-----------------|-------------|
| Unit Tests | 90% | Individual tool tests |
| Integration Tests | 85% | End-to-end tests |
| LSP Tests | 90% | Protocol tests |
| Editor Tests | 80% | Extension tests |

### 7.2 Test Examples

```rust
// Formatter test
#[test]
fn test_format_function() {
    let input = r#"
umurimo add(a: int, b: int) -> int kora
ret a + b
iherezo
"#;
    let expected = r#"
umurimo add(a: int, b: int) -> int kora
    ret a + b
iherezo
"#;
    let formatter = Formatter::new(FormatConfig::default());
    let output = formatter.format(input).unwrap();
    assert_eq!(output, expected);
}

// Linter test
#[test]
fn test_unused_variable() {
    let source = r#"
niba x: int = 5 kora
    ret 10
iherezo
"#;
    let linter = Linter::new();
    let diagnostics = linter.lint(source).unwrap();
    assert!(!diagnostics.is_empty());
}
```

---

## 8. Security Considerations

### 8.1 Security Requirements

| Requirement | Description | Verification |
|-------------|-------------|--------------|
| Code Injection | Prevent code injection | Input validation |
| Path Traversal | Prevent path attacks | Sanitize paths |
| Denial of Service | Prevent DoS | Resource limits |

---

## 9. Performance Considerations

### 9.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| LSP Response | < 100ms | Time to response |
| Format Speed | > 50K LOC/s | Throughput |
| Lint Speed | > 100K LOC/s | Throughput |

---

## 10. Definition of Done

### 10.1 Phase 5.10 is complete when:

- [ ] All components implemented and compiling
- [ ] Unit tests passing (> 90% coverage)
- [ ] Integration tests passing
- [ ] LSP server working
- [ ] Formatter working
- [ ] Linter working
- [ ] Debugger working
- [ ] Test runner working
- [ ] Doc generator working
- [ ] Build system working
- [ ] CLI interface working
- [ ] Editor extensions working
- [ ] Documentation complete
- [ ] Examples working
- [ ] Cross-platform testing passing
- [ ] Code review complete
- [ ] Changelog updated

### 10.2 Quality Gates

| Gate | Requirement | Status |
|------|-------------|--------|
| Build | Clean build passes | - |
| Tests | All tests pass | - |
| Coverage | > 90% | - |
| Lint | No warnings | - |
| Format | Formatted | - |
| Docs | All public API documented | - |
| Security | No vulnerabilities | - |
| Review | Code reviewed | - |

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
