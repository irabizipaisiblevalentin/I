# Developer Tools Architecture

This document specifies the complete architecture of all official I Programming Language developer tools.

## Table of Contents

- [Overview](#overview)
- [I Studio — IDE](#i-studio--ide)
- [isoko — Package Manager](#isoko--package-manager)
- [iformat — Code Formatter](#iformat--code-formatter)
- [idebug — Debugger](#idebug--debugger)
- [itest — Testing Framework](#itest--testing-framework)
- [isearch — Code Search & LSP](#isearch--code-search--lsp)
- [imigrate — Database Migration Tool](#imigrate--database-migration-tool)
- [ideploy — Deployment Tool](#ideploy--deployment-tool)
- [Cross-Tool Integration](#cross-tool-integration)

## Overview

The I ecosystem includes a complete set of developer tools designed to work seamlessly together. All tools share:

1. **Consistent CLI**: Same flag conventions, help system, output format
2. **LSP Integration**: All tools provide Language Server Protocol support
3. **Plugin System**: All tools support extensions
4. **Configuration**: Shared `ilang.toml` project configuration
5. **Bilingual Output**: All messages in English + Kinyarwanda

### Shared Configuration

```toml
# ilang.toml
[project]
name = "my_project"
version = "0.1.0"
description = "My I project"

[compiler]
target = "x86_64-unknown-linux-gnu"
optimize = true
debug = true

[package]
registry = "https://isoko.ilang.dev"
dependencies = []

[format]
indent = 4
max_line = 100
sort_imports = true

[lint]
warnings = true
errors = true
suggestions = true

[test]
framework = "itest"
coverage = true
```

---

## I Studio — IDE

### Purpose

Full-featured IDE for I Programming Language development.

### Architecture

```
i-studio/
├── core/           # Core editor
│   ├── editor.i    # Text editor engine
│   ├── buffer.i    # Buffer management
│   ├── syntax.i    # Syntax highlighting
│   ├── indent.i    # Auto-indentation
│   └── bracket.i   # Bracket matching
├── lsp/            # Language Server Protocol
│   ├── client.i    # LSP client
│   ├── server.i    # LSP server
│   └── protocol.i  # Protocol implementation
├── ui/             # User interface
│   ├── window.i    # Window management
│   ├── panel.i     # Side panels
│   ├── tab.i       # Tab management
│   ├── toolbar.i   # Toolbar
│   ├── statusbar.i # Status bar
│   ├── terminal.i  # Integrated terminal
│   ├── explorer.i  # File explorer
│   └── theme.i     # Theme system
├── features/       # IDE features
│   ├── completion.i # Autocomplete
│   ├── goto.i      # Go to definition
│   ├── find.i      # Find & replace
│   ├── refactor.i  # Refactoring
│   ├── debug.i     # Debug integration
│   ├── git.i       # Git integration
│   ├── test.i      # Test runner
│   └── build.i     # Build system
├── extensions/     # Extension system
│   ├── loader.i    # Extension loader
│   ├── api.i       # Extension API
│   └── marketplace.i # Extension marketplace
└── platform/       # Platform support
    ├── windows.i   # Windows
    ├── linux.i     # Linux
    └── macos.i     # macOS
```

### Core Features

1. **Syntax Highlighting**: Full I language syntax support
2. **Autocomplete**: Context-aware code completion
3. **Error Linting**: Real-time error detection
4. **Go to Definition**: Jump to function/type definitions
5. **Find References**: Find all usages of a symbol
6. **Refactoring**: Rename, extract, inline, move
7. **Integrated Terminal**: Built-in command line
8. **Git Integration**: Version control UI
9. **Debug Integration**: Breakpoints, variables, call stack
10. **Test Runner**: Run tests from IDE

### LSP Server

```
# LSP Capabilities
igiceri LSPServer
    # Text document synchronization
    did_open(self, params: DidOpenParams) -> void
    did_change(self, params: DidChangeParams) -> void
    did_save(self, params: DidSaveParams) -> void
    did_close(self, params: DidCloseParams) -> void
    
    # Features
    completion(self, params: CompletionParams) -> CompletionList
    hover(self, params: HoverParams) -> Hover?
    definition(self, params: DefinitionParams) -> Location?
    references(self, params: ReferenceParams) -> List<Location>
    document_symbol(self, params: DocumentSymbolParams) -> List<DocumentSymbol>
    rename(self, params: RenameParams) -> WorkspaceEdit?
    code_action(self, params: CodeActionParams) -> List<CodeAction>
    formatting(self, params: DocumentFormattingParams) -> List<TextEdit>
    
    # Diagnostics
    publish_diagnostics(self, uri: string, diagnostics: List<Diagnostic>) -> void
iherezo
```

### UI Layout

```
+------------------+-------------------+------------------+
| File Explorer    | Editor Area       | Outline          |
|                  |                   |                  |
| - src/           | [Tab 1] [Tab 2]  | - Module A       |
|   - main.i       |                   |   - Function 1   |
|   - lib/         | func main() {    |   - Function 2   |
|     - utils.i    |   // code here    | - Module B       |
| - tests/         | }                 |   - Function 3   |
|                  |                   |                  |
+------------------+-------------------+------------------+
| Terminal / Problems / Output                             |
| > ilang build                                              |
| Compiling... Done.                                         |
+----------------------------------------------------------+
| Status: Ready | Ln 10, Col 5 | UTF-8 | I                |
+----------------------------------------------------------+
```

---

## isoko — Package Manager

### Purpose

Package management, dependency resolution, and project scaffolding.

### Architecture

```
isoko/
├── core/           # Core
│   ├── resolver.i  # Dependency resolver
│   ├── lockfile.i  # Lock file management
│   └── registry.i  # Registry client
├── commands/       # CLI commands
│   ├── init.i      # Project initialization
│   ├── add.i       # Add dependency
│   ├── remove.i    # Remove dependency
│   ├── update.i    # Update dependencies
│   ├── install.i   # Install dependencies
│   ├── search.i    # Search packages
│   ├── publish.i   # Publish package
│   ├── list.i      # List dependencies
│   └── tree.i      # Dependency tree
├── config/         # Configuration
│   ├── manifest.i  # Project manifest
│   ├── lockfile.i  # Lock file
│   └── config.i    # User config
├── registry/       # Registry
│   ├── client.i    # HTTP client
│   ├── cache.i     # Local cache
│   └── auth.i      # Authentication
└── scaffold/       # Project templates
    ├── templates/  # Project templates
    └── generate.i  # Code generation
```

### CLI Commands

```
# Initialize project
isoko init my_project
isoko init my_project --template web
isoko init my_project --template ai

# Add dependencies
isoko add urubuga@latest
isoko add ubwenge@^0.5.0
isoko add --dev itest@latest

# Remove dependencies
isoko remove urubuga

# Update dependencies
isoko update
isoko update urubuga

# Install dependencies
isoko install

# Search packages
isoko search web
isoko search database --registry official

# Publish package
isoko publish

# List dependencies
isoko list
isoko list --tree

# Run scripts
isoko run build
isoko run test
isoko run dev
```

### Manifest Format

```toml
# ilang.toml
[project]
name = "my_web_app"
version = "0.1.0"
authors = ["Author Name <email@example.com>"]
description = "My web application"
license = "MIT"
repository = "https://github.com/user/repo"

[dependencies]
urubuga = "0.5.0"
ubwenge = "^0.5.0"
ilang-database = "0.3.0"

[dev-dependencies]
itest = "0.1.0"

[scripts]
build = "ilang build"
test = "itest run"
dev = "ilang dev"
format = "iformat src/"

[[templates]]
name = "web"
description = "Web application template"
path = "templates/web/"
```

### Lock File

```toml
# ilang.lock
[[package]]
name = "urubuga"
version = "0.5.0"
source = "registry+https://isoko.ilang.dev"
checksum = "abc123..."

[[package]]
name = "ubwenge"
version = "0.5.0"
source = "registry+https://isoko.ilang.dev"
checksum = "def456..."

[[package]]
name = "itest"
version = "0.1.0"
source = "registry+https://isoko.ilang.dev"
checksum = "ghi789..."
```

### Package Structure

```
my_package/
├── ilang.toml          # Package manifest
├── src/
│   ├── lib.i           # Main library
│   └── ...
├── tests/
│   ├── test_main.i     # Tests
│   └── ...
├── docs/               # Documentation
│   └── ...
├── examples/           # Examples
│   └── ...
└── README.md
```

---

## iformat — Code Formatter

### Purpose

Automatic code formatting for consistent style.

### Architecture

```
iformat/
├── core/           # Core
│   ├── parser.i    # Source parsing
│   ├── ast.i       # AST representation
│   └── printer.i   # Code generation
├── rules/          # Formatting rules
│   ├── indent.i    # Indentation
│   ├── spacing.i   # Spacing
│   ├── newline.i   # Line breaks
│   ├── braces.i    # Bracket style
│   ├── import.i    # Import sorting
│   └── comment.i   # Comment formatting
├── config/         # Configuration
│   ├── defaults.i  # Default settings
│   └── editor.i    # EditorConfig support
└── cli/            # CLI interface
    ├── format.i    # Format command
    ├── check.i     # Check command
    └── diff.i      # Diff command
```

### CLI Commands

```
# Format files
iformat src/
iformat src/main.i
iformat .

# Check without modifying
iformat --check src/

# Show diff
iformat --diff src/

# Format with config
iformat --config .iformat.toml src/
```

### Configuration

```toml
# .iformat.toml
[general]
indent = 4
indent_style = "spaces"
max_line_length = 100
end_of_line = "lf"

[spacing]
around_operators = true
after_commas = true
before_braces = true
inside_brackets = false

[breaking]
single_line_blocks = false
single_line_statements = false

[imports]
sort = true
group_by_source = true
group_order = ["std", "official", "third-party", "local"]

[comments]
preserve_doc_comments = true
format_doc_comments = true
```

### Format Rules

| Rule | Default | Description |
|------|---------|-------------|
| `indent` | 4 | Spaces per indent level |
| `max_line_length` | 100 | Maximum line length |
| `trailing_commas` | true | Add trailing commas |
| `sort_imports` | true | Sort import statements |
| `blank_lines` | 2 | Blank lines between functions |
| `bracket_style` | "next_line" | Bracket placement |

---

## idebug — Debugger

### Purpose

Interactive debugger with breakpoints, stepping, and inspection.

### Architecture

```
idebug/
├── core/           # Core
│   ├── debugger.i  # Debugger engine
│   ├── breakpoint.i # Breakpoint management
│   ├── step.i      # Stepping logic
│   └── inspect.i   # Variable inspection
├── protocol/       # Debug protocol
│   ├── adapter.i   # Debug adapter
│   ├── protocol.i  # DAP implementation
│   └── transport.i # Transport layer
├── ui/             # User interface
│   ├── tui.i       # Terminal UI
│   ├── gui.i       # GUI (future)
│   └── web.i       # Web UI
├── commands/       # Debug commands
│   ├── run.i       # Run/continue
│   ├── step.i      # Step in/out/over
│   ├── break.i     # Breakpoint management
│   ├── watch.i     # Watch expressions
│   ├── stack.i     # Call stack
│   ├── vars.i      # Variables
│   └── eval.i      # Expression evaluation
└── integration/    # Integration
    ├── vscode.i    # VS Code adapter
    ├── editor.i    # Editor integration
    └── ide.i       # IDE integration
```

### CLI Interface

```
# Start debug session
idebug run main.i

# Run with arguments
idebreak run main.i -- arg1 arg2

# Attach to running process
idebug attach --pid 1234

# Remote debugging
idebug connect --host localhost --port 9229
```

### Debug Commands

```
# Execution
run            # Start/continue execution
pause          # Pause execution
stop           # Stop debugging
restart        # Restart program

# Stepping
step           # Step into function
step-over      # Step over function
step-out       # Step out of function
step-line      # Step one line

# Breakpoints
break <line>           # Set breakpoint at line
break <file>:<line>    # Set breakpoint in file
break <function>       # Set breakpoint at function
break --condition <expr> # Conditional breakpoint
break --hit-count <n>  # Hit count breakpoint
delete <id>            # Delete breakpoint
enable <id>            # Enable breakpoint
disable <id>           # Disable breakpoint
list                   # List all breakpoints

# Inspection
print <variable>       # Print variable value
watch <expression>     # Add watch expression
locals                 # Show local variables
globals                # Show global variables
stack                  # Show call stack
args                   # Show function arguments

# Evaluation
eval <expression>      # Evaluate expression

# Memory
memory                 # Show memory usage
gc                     # Force garbage collection
```

### TUI Layout

```
+------------------------------------------+
| Debug: main.i | Running | PID: 12345    |
+------------------------------------------+
| main.i                    | Watch        |
| 10: shyiramo urubuga     | x: 5         |
| 11:                      | y: "hello"   |
| 12: func main() {        |               |
|>13:   x = 5              |               |
| 14:   y = "hello"        |               |
| 15:   print(x + y)       |               |
| 16: }                    |               |
+------------------------------------------+
| Output                                   |
| > Compilation successful                 |
| > Starting debugger...                   |
+------------------------------------------+
| (s)tep (n)ext (c)ontinue (b)reak (p)rint |
+------------------------------------------+
```

---

## itest — Testing Framework

### Purpose

Unit testing, integration testing, and test runner.

### Architecture

```
itest/
├── core/           # Core
│   ├── test.i      # Test runner
│   ├── suite.i     # Test suite
│   ├── assertion.i # Assertions
│   └── mock.i      # Mocking
├── runner/         # Test runner
│   ├── discover.i  # Test discovery
│   ├── execute.i   # Test execution
│   ├── reporter.i  # Result reporting
│   └── filter.i    # Test filtering
├── matchers/       # Matchers
│   ├── equality.i  # Equality matchers
│   ├── type.i      # Type matchers
│   ├── exception.i # Exception matchers
│   ├── string.i    # String matchers
│   ├── collection.i # Collection matchers
│   └── custom.i    # Custom matchers
├── mock/           # Mocking
│   ├── mock.i      # Mock objects
│   ├── spy.i       # Spies
│   ├── stub.i      # Stubs
│   └── verify.i    # Verification
├── fixture/        # Fixtures
│   ├── setup.i     # Setup/teardown
│   ├── temp.i      # Temporary files
│   └── data.i      # Test data
└── coverage/       # Coverage
    ├── track.i     # Coverage tracking
    ├── report.i    # Coverage report
    └── threshold.i # Threshold enforcement
```

### CLI Commands

```
# Run all tests
itest run

# Run specific file
itest run tests/test_main.i

# Run specific test
itest run tests/test_main.i::test_addition

# Run with filter
itest run --filter "test_user_*"

# Run with coverage
itest run --coverage
itest run --coverage --threshold 80

# Run with reporter
itest run --reporter verbose
itest run --reporter json

# Watch mode
itest watch

# Generate coverage report
itest coverage --report html
itest coverage --report lcov
```

### Test API

```
# Test suite
igiceri TestSuite
    setup(self) -> void        # Before each test
    teardown(self) -> void     # After each test
    setup_suite(self) -> void  # Before all tests
    teardown_suite(self) -> void # After all tests
iherezo

# Assertions
assert_equal(actual, expected) -> void
assert_not_equal(actual, expected) -> void
assert_true(condition) -> void
assert_false(condition) -> void
assert_null(value) -> void
assert_not_null(value) -> void
assert_throws(fn: () -> void, error_type: Type) -> void
assert_contains(collection, item) -> void
assert_length(collection, expected: int) -> void
assert_match(string, pattern: string) -> void

# Mocking
mock = Mock()
mock.when("method_name").then_return(value)
mock.verify("method_name").called_times(3)
mock.verify("method_name").called_with(args)
```

### Example Test

```
shyiramo itest

igiceri MathTest(itest.TestSuite)
    setup(self) -> void
        self.calculator = Calculator()
    iherezo
    
    test_addition(self) -> void
        result = self.calculator.add(2, 3)
        itest.assert_equal(result, 5)
    iherezo
    
    test_subtraction(self) -> void
        result = self.calculator.subtract(5, 3)
        itest.assert_equal(result, 2)
    iherezo
    
    test_division_by_zero(self) -> void
        itest.assert_throws(
            () => self.calculator.divide(10, 0),
            DivisionByZeroError
        )
    iherezo
iherezo

itest.run(MathTest)
```

---

## isearch — Code Search & LSP

### Purpose

Language Server Protocol implementation and code intelligence.

### Architecture

```
isearch/
├── core/           # Core
│   ├── server.i    # LSP server
│   ├── session.i   # Session management
│   └── config.i    # Configuration
├── analysis/       # Code analysis
│   ├── parse.i     # Source parsing
│   ├── symbol.i    # Symbol resolution
│   ├── type.i      # Type inference
│   ├── scope.i     # Scope analysis
│   └── flow.i      # Control flow
├── features/       # LSP features
│   ├── completion.i # Autocomplete
│   ├── hover.i     # Hover information
│   ├── goto.i      # Go to definition
│   ├── reference.i # Find references
│   ├── symbol.i    # Document symbols
│   ├── rename.i    # Rename refactoring
│   ├── code_action.i # Quick fixes
│   ├── diagnostic.i # Diagnostics
│   └── format.i    # Formatting
├── protocol/       # Protocol
│   ├── jsonrpc.i   # JSON-RPC
│   ├── message.i   # Message types
│   └── transport.i # Transport layer
└── integration/    # Integration
    ├── vscode.i    # VS Code
    ├── vim.i       # Vim/Neovim
    ├── emacs.i     # Emacs
    └── sublime.i   # Sublime Text
```

### LSP Features

| Feature | Description |
|---------|-------------|
| `textDocument/completion` | Autocomplete suggestions |
| `textDocument/hover` | Hover documentation |
| `textDocument/definition` | Go to definition |
| `textDocument/references` | Find all references |
| `textDocument/documentSymbol` | Document outline |
| `textDocument/rename` | Rename symbol |
| `textDocument/codeAction` | Quick fixes |
| `textDocument/publishDiagnostics` | Error/warning diagnostics |
| `textDocument/formatting` | Code formatting |
| `workspace/symbol` | Workspace symbol search |

### Diagnostics

```
# Error diagnostic
igiceri Diagnostic
    range: Range
    severity: DiagnosticSeverity
    code: string
    message: string
    source: string = "isearch"
    related_information: List<DiagnosticRelatedInformation> = []
    tags: List<DiagnosticTag> = []
iherezo

# Severity levels
enum DiagnosticSeverity
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4
iherezo
```

---

## imigrate — Database Migration Tool

### Purpose

Database schema migration management.

### Architecture

```
imigrate/
├── core/           # Core
│   ├── migration.i # Migration engine
│   ├── schema.i    # Schema representation
│   └── generator.i # Migration generator
├── commands/       # CLI commands
│   ├── init.i      # Initialize migrations
│   ├── create.i    # Create migration
│   ├── up.i        # Apply migrations
│   ├── down.i      # Rollback migrations
│   ├── status.i    # Migration status
│   └── seed.i      # Seed data
├── drivers/        # Database drivers
│   ├── postgres.i  # PostgreSQL
│   ├── mysql.i     # MySQL
│   ├── sqlite.i    # SQLite
│   └── mongodb.i   # MongoDB
└── templates/      # Migration templates
    ├── create.i    # Create table
    ├── alter.i     # Alter table
    └── drop.i      # Drop table
```

### CLI Commands

```
# Initialize migrations
imigrate init

# Create migration
imigrate create add_users_table
imigrate create add_email_to_users --table users

# Apply migrations
imigrate up
imigrate up --steps 3

# Rollback migrations
imigrate down
imigrate down --steps 2

# Check status
imigrate status

# Seed database
imigrate seed
imigrate seed --file seed.i
```

### Migration Format

```
# migrations/001_add_users_table.i
igiceri AddUsersTable(imigrate.Migration)
    up(self) -> void
        self.create_table("users", (table) => {
            table.id()
            table.string("name", length=100)
            table.string("email", unique=true)
            table.timestamp("created_at")
            table.timestamp("updated_at")
        })
    iherezo
    
    down(self) -> void
        self.drop_table("users")
    iherezo
iherezo
```

---

## ideploy — Deployment Tool

### Purpose

Application deployment to various platforms.

### Architecture

```
ideploy/
├── core/           # Core
│   ├── deployer.i  # Deployment engine
│   ├── config.i    # Configuration
│   └── status.i    # Status tracking
├── platforms/      # Platform support
│   ├── docker.i    # Docker deployment
│   ├── kubernetes.i # Kubernetes deployment
│   ├── serverless.i # Serverless deployment
│   ├── vm.i        # Virtual machine
│   └── bare.i      # Bare metal
├── strategies/     # Deployment strategies
│   ├── rolling.i   # Rolling update
│   ├── blue-green.i # Blue-green
│   ├── canary.i    # Canary
│   └── recreate.i  # Recreate
├── health/         # Health checks
│   ├── http.i      # HTTP health check
│   ├── tcp.i       # TCP health check
│   └── custom.i    # Custom health check
└── rollback/       # Rollback
    ├── automatic.i # Automatic rollback
    └── manual.i    # Manual rollback
```

### CLI Commands

```
# Deploy to platform
ideploy docker
ideploy kubernetes
ideploy serverless

# Check deployment status
ideploy status

# Rollback deployment
ideploy rollback
ideploy rollback --to v1.2.0

# View logs
ideploy logs
ideploy logs --follow

# Scale deployment
ideploy scale --replicas 3
```

### Configuration

```toml
# ideploy.toml
[platform]
type = "kubernetes"
namespace = "production"

[strategy]
type = "rolling"
max_surge = "25%"
max_unavailable = "25%"

[health]
path = "/health"
port = 8000
initial_delay = 30
period = 10

[rollback]
automatic = true
threshold = 0.1
```

---

## Cross-Tool Integration

### Shared Interfaces

```
# All tools implement
igiceri Tool
    name: string
    version: string
    
    run(self, args: List<string>) -> Result<void, Error>
    help(self) -> string
    version(self) -> string
iherezo

# All tools support LSP
igiceri LSPCapable
    start_lsp(self) -> LSPServer
    stop_lsp(self) -> void
iherezo
```

### Tool Dependencies

```
ilang (Compiler)
    ├── uses: isearch (LSP)
    ├── uses: iformat (Formatting)
    └── uses: itest (Testing)

i-studio (IDE)
    ├── uses: isearch (LSP)
    ├── uses: idebug (Debugging)
    ├── uses: itest (Testing)
    └── uses: isoko (Package Manager)

isoko (Package Manager)
    ├── uses: ilang (Compilation)
    └── uses: imigrate (Database)

ideploy (Deployment)
    └── uses: ilang (Compilation)
```

### Shared Configuration

All tools read from `ilang.toml` and can be configured with tool-specific sections:

```toml
[project]
name = "my_project"

# Compiler settings
[compiler]
optimize = true

# Formatter settings
[format]
indent = 4

# Debugger settings
[debug]
port = 9229

# Test settings
[test]
coverage = true

# Deploy settings
[deploy]
platform = "kubernetes"
```

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
