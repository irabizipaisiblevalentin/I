# I STUDIO — Integrated Development Environment & Developer Experience Platform

**Version:** 0.1.0  
**Status:** Development Sprint 20  
**Previous:** IGICU Cloud Platform (Sprint 19) — completed

## Overview

I STUDIO is the official integrated development environment for the I programming language. It is not a traditional text editor — it is a full platform spanning editor engine, language intelligence, debugging, profiling, visual design, AI assistance, database/cloud/game/system integration, collaboration, and an extension ecosystem.

## Module Architecture

```
src/istudio/
├── __init__.py                  # Public API exports
├── ibikoreshingiro.py           # Core types, enums, dataclasses, errors
├── akazi.py                     # Workspace & Project Manager
├── indura.py                    # Editor Engine
├── ururimi.py                   # Language Server & Language Intelligence
├── ugutunganya.py               # Debugging Platform
├── gupima.py                    # Profiling Platform
├── igishushanyo.py              # Visual Designers (UI, Forms)
├── umufasha.py                  # AI Assistant (UBWENGE Integration)
├── ibikoresho_ububiko.py        # Database Tools (UBUBIKO Integration)
├── ibikoresho_igicu.py          # Cloud Tools (IGICU Integration)
├── ibikoresho_imikino.py        # Game Tools (IMIKINO Integration)
├── ibikoresho_sisitemu.py       # System Tools (SISITEMU Integration)
├── porogaramu.py                # Extension Platform
├── iterambere.py                # Collaboration
├── itegeko.py                   # CLI subcommands (istudio + isoko bridge)
├── ibikoresho_rusange.py        # Common utilities (cache, event bus, etc.)
```

## Module Responsibilities

### `ibikoreshingiro.py` — Core Types
- All enums: `EditorTheme`, `CursorStyle`, `TabSize`, `FileType`, `DiagnosticSeverity`, `SymbolKind`, `CompletionKind`, `BreakpointType`, `DebuggerState`, `ProfilerType`, `PluginState`, `CollaborationRole`
- All dataclasses: `EditorConfig`, `WorkspaceConfig`, `ProjectConfig`, `DocumentPosition`, `DocumentRange`, `Diagnostic`, `CompletionItem`, `SymbolInfo`, `Breakpoint`, `StackFrame`, `VariableInfo`, `ProfileResult`, `PluginManifest`, `ExtensionPoint`, `TabInfo`, `SearchResult`, `RefactoringAction`, `CodeAction`, `HoverInfo`, `BuildTarget`, `TestResult`, `ChatMessage`, `AICompletionRequest`
- Error hierarchy: `IStudioError` > `EditorError`, `LanguageServerError`, `DebuggerError`, `ProjectError`, `PluginError`, `BuildError`

### `akazi.py` — Workspace & Project Manager
- `WorkspaceManager`: load/create/update workspaces, manage settings, extensions, projects
- `ProjectManager`: create/load/list/remove projects with `project.json` persistence
- Uses `.istudio-workspace` JSON file for workspace state

### `indura.py` — Editor Engine
- Multi-tab file editor with `open_file`, `close_file`, `get/set_content`, `insert_text`, `delete_range`
- `save_file`, `undo`, `redo` with 100-level undo stack
- `find_text`, `replace_text` with optional case sensitivity
- Event system: `on`/`off`/`emit` for tab lifecycle, cursor movement, content changes
- `detect_file_type` static method for file extension mapping

### `ururimi.py` — Language Server
- `analyze`: diagnostics for undefined references, unterminated strings, int overflow
- `get_completions`: keyword and snippet completions
- `get_hover`: built-in function documentation
- `get_symbols`: extract functions, classes, variables
- `go_to_definition`, `get_references`
- `get_code_actions`, `format_document` (indentation-based)
- LSP-compatible via `cmd_server` with stdio transport

### `ugutunganya.py` — Debugging Platform
- State machine: `start`, `stop`, `pause`, `continue`, `step_over`, `step_into`, `step_out`
- Breakpoint management: `add`, `remove`, `toggle`, `clear`, list
- Stack frame tracking, variable scoping, expression evaluation
- Event-driven lifecycle

### `gupima.py` — Profiling Platform
- Session-based profiling with `start_session`, `stop_session`, `add_sample`
- `CPUSampler` and `MemorySampler` using psutil
- Multi-session tracking with results aggregation

### `igishushanyo.py` — Visual Designers
- `VisualDesigner`: component tree management, clipboard, code generation
- `FormDesigner`: form layout with field types, validation, code generation
- Supports UI components: container, button, label, input, image, table

### `umufasha.py` — AI Assistant
- Multi-conversation chat with contextual responses
- `complete_code`: context-aware inline code completion
- Integration point for UBWENGE AI platform

### `ibikoresho_ububiko.py` — Database Explorer
- Connection management (SQLite, PostgreSQL, MySQL)
- Query execution, schema browsing
- Query generation (SELECT, INSERT, UPDATE)
- Result export

### `ibikoresho_igicu.py` — Cloud Explorer
- Provider registration and resource management
- Deployment lifecycle: deploy, undeploy, logs, metrics
- Remote command execution

### `ibikoresho_imikino.py` — Game Designer
- Asset management (sprites, audio, fonts)
- Scene composition with physics
- Animation system with frame-based timing
- Code generation for game scenes

### `ibikoresho_sisitemu.py` — System Explorer
- System info, CPU, memory, disk, network introspection
- Process listing and inspection
- Environment variables and filesystem info
- Uses psutil for cross-platform system data

### `porogaramu.py` — Extension Platform
- Extension point registration and handler dispatch
- Plugin lifecycle: `install`, `uninstall`, `enable`, `disable`
- Manifest-driven plugin loading with permissions
- Settings per plugin

### `iterambere.py` — Collaboration
- Session management: `create_session`, `join_session`, `leave_session`
- User management with roles (owner, editor, reviewer, viewer)
- Real-time edit tracking, file comments, code reviews
- Event-driven collaboration lifecycle

### `itegeko.py` — CLI
- `register_subcommands`: add `istudio` subparser to isoko
- `genda`: dispatch istudio subcommands
- Standalone commands: `workspace`, `project`, `lint`, `format`, `debug`, `profile`, `ai`, `extension`, `collaboration`, `server` (LSP stdio)
- All commands return 0 on success, 1 on error

### `ibikoresho_rusange.py` — Utilities
- `generate_id`, `timestamp`, `format_timestamp`, `compute_hash`, `safe_filename`
- `ensure_dir`, `read_json`, `write_json`, `search_files`, `find_text_in_files`
- `diff_strings`, `merge_configs`, `truncate`, `tokenize`
- `LRUCache` with get/put/remove/clear
- `EventBus` with on/off/emit/clear

## CLI Integration

### Via `isoko` (primary)
```
isoko istudio workspace init <path>
isoko istudio workspace open <path>
isoko istudio workspace info
isoko istudio project create <name>
isoko istudio project list
isoko istudio lint <file>
isoko istudio format <file>
isoko istudio debug start|stop|step|continue|break|break-list
isoko istudio profile start|stop|list|results
isoko istudio ai chat <message>
isoko istudio ai conversations
isoko istudio extension install|uninstall|list|enable|disable
isoko istudio collaboration session-create|session-list|user-list|review-create|review-list
isoko istudio server --stdio
```

### Via `istudio` (standalone)
```
python -m istudio.itegeko workspace init <path>
python -m istudio.itegeko lint <file>
```

## I-Language Bindings

Type definitions in `istudio/istudio.i` expose the full I STUDIO API to I language programs:
- Type aliases for all enums
- Struct definitions for all data types
- Class interfaces with method signatures for `WorkspaceManager`, `EditorEngine`, `LanguageServer`, `Debugger`, `Profiler`, `VisualDesigner`, `AIAssistant`, `ExtensionManager`, `CollaborationManager`, `DatabaseExplorer`, `CloudExplorer`, `GameDesigner`, `SystemExplorer`

## Extension Points

| Point | Description |
|-------|-------------|
| `editor.didOpen` | File opened in editor |
| `editor.didSave` | File saved |
| `editor.didChange` | Content changed |
| `editor.completion` | Code completion request |
| `editor.hover` | Hover information request |
| `debugger.didStart` | Debug session started |
| `debugger.didStop` | Debug session ended |
| `workspace.didChange` | Workspace configuration changed |

## Integration With Other Platforms

| Platform | Module | Integration |
|----------|--------|-------------|
| UBWENGE (AI) | `umufasha.py` | Code completion, chat, inline suggestions |
| UBUBIKO (Data) | `ibikoresho_ububiko.py` | Database explorer, query builder, schema browser |
| IGICU (Cloud) | `ibikoresho_igicu.py` | Cloud explorer, deployment, metrics |
| IMIKINO (Games) | `ibikoresho_imikino.py` | Game scene designer, asset manager |
| SISITEMU (System) | `ibikoresho_sisitemu.py` | System explorer, process monitor |

## Testing

Tests in `tests/istudio/` follow the pattern:
- `test_ibikoreshingiro.py` — type instantiation and enum values
- `test_akazi.py` — workspace and project manager operations
- `test_indura.py` — editor engine file operations, undo/redo, find/replace
- `test_ururimi.py` — language server analysis, completions, formatting
- `test_ugutunganya.py` — debugger state machine, breakpoints
- `test_gupima.py` — profiler sessions and sampling
- `test_igishushanyo.py` — visual designer component operations
- `test_umufasha.py` — AI assistant conversation and code completion
- `test_ibikoresho_ububiko.py` — database explorer connections and queries
- `test_ibikoresho_igicu.py` — cloud explorer providers and deployments
- `test_ibikoresho_imikino.py` — game designer assets and scenes
- `test_ibikoresho_sisitemu.py` — system explorer info retrieval
- `test_porogaramu.py` — extension manager plugin lifecycle
- `test_iterambere.py` — collaboration sessions and reviews
- `test_itegeko.py` — CLI subcommand dispatch
- Test count target: 180+
