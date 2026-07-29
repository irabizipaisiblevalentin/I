// I STUDIO — I-language type definitions for the IDE platform
// Version 0.1.0

// ─── Core Types ────────────────────────────────────────────────────────────

type EditorTheme: string {
    "light"
    "dark"
    "high_contrast"
    "solarized"
    "monokai"
    "custom"
}

type CursorStyle: string {
    "line"
    "block"
    "underline"
}

type FileType: string {
    "i"
    "py"
    "js"
    "ts"
    "rs"
    "go"
    "java"
    "cpp"
    "c"
    "html"
    "css"
    "json"
    "yaml"
    "toml"
    "md"
    "txt"
}

type DiagnosticSeverity: string {
    "error"
    "warning"
    "info"
    "hint"
}

type SymbolKind: string {
    "file" "module" "namespace" "package"
    "class" "method" "property" "field"
    "constructor" "enum" "interface"
    "function" "variable" "constant"
    "string" "number" "boolean" "array" "object"
    "key" "null" "enum_member" "struct"
    "event" "operator" "type_parameter"
}

type BreakpointType: string {
    "line" "conditional" "log_point" "function" "exception" "data"
}

type DebuggerState: string {
    "running" "paused" "stepping" "stopped"
    "breakpoint" "exception"
}

type ProfilerType: string {
    "cpu" "memory" "gpu" "network"
    "database" "ai" "cloud" "frame"
}

type PluginState: string {
    "disabled" "enabled" "error" "loading"
}

type CollaborationRole: string {
    "owner" "editor" "reviewer" "viewer"
}

// ─── Structs ───────────────────────────────────────────────────────────────

struct DocumentPosition {
    line: int = 0
    column: int = 0
}

struct DocumentRange {
    start: DocumentPosition
    end: DocumentPosition
}

struct EditorConfig {
    theme: EditorTheme = "dark"
    font_size: int = 14
    font_family: string = "Cascadia Code, Fira Code, monospace"
    tab_size: int = 4
    auto_save: bool = true
    line_numbers: bool = true
    minimap: bool = true
    word_wrap: bool = false
    format_on_save: bool = true
}

struct WorkspaceConfig {
    name: string
    root_path: string
    projects: [string] = []
    settings: {} = {}
}

struct ProjectConfig {
    name: string
    version: string = "0.1.0"
    type: string = "application"
    language: string = "i"
    entry_point: string = "main.i"
    dependencies: {string: string} = {}
}

struct TabInfo {
    id: string
    title: string
    file_path: string
    language: string = "i"
    is_dirty: bool = false
    cursor_position: DocumentPosition
}

struct Diagnostic {
    severity: DiagnosticSeverity = "error"
    message: string
    range: DocumentRange
    code: string = ""
}

struct CompletionItem {
    label: string
    kind: string = "text"
    detail: string = ""
    insert_text: string = ""
}

struct Breakpoint {
    file: string
    line: int
    type: BreakpointType = "line"
    condition: string = ""
    enabled: bool = true
    hit_count: int = 0
}

struct StackFrame {
    id: int
    name: string
    file: string
    line: int
    module: string = ""
}

struct VariableInfo {
    name: string
    value: string = ""
    type: string = ""
    children: [VariableInfo] = []
}

struct ProfileResult {
    type: ProfilerType = "cpu"
    total_time_ms: float = 0.0
    call_count: int = 0
    memory_used_kb: float = 0.0
}

struct PluginManifest {
    id: string
    name: string
    version: string = "1.0.0"
    description: string = ""
    author: string = ""
    entry_point: string = ""
    permissions: [string] = []
    contributes: {} = {}
}

struct ChatMessage {
    role: string = "user"
    content: string
    timestamp: string = ""
}

struct UIComponent {
    id: string
    type: string = "container"
    label: string = ""
    x: int = 0
    y: int = 0
    width: int = 100
    height: int = 50
    properties: {} = {}
    children: [UIComponent] = []
    events: {string: string} = {}
}

// ─── Workspace & Project Manager ───────────────────────────────────────────

class WorkspaceManager {
    function init(root_path: string = ""): void
    function load_or_create(path: string): WorkspaceConfig
    function add_project(project_path: string): void
    function remove_project(project_path: string): bool
    function open_file(file_path: string): TabInfo
    function close_file(tab_id: string): bool
    function save_file(tab_id: string): bool
    function get_setting(key: string, default: any): any
    function update_setting(key: string, value: any): void
}

// ─── Editor Engine ─────────────────────────────────────────────────────────

class EditorEngine {
    function init(config: EditorConfig = {}): void
    function open_file(path: string): TabInfo
    function get_content(tab_id: string): string
    function set_content(content: string, tab_id: string): void
    function insert_text(text: string, line: int, column: int, tab_id: string): string
    function save_file(tab_id: string): bool
    function undo(tab_id: string): string
    function redo(tab_id: string): string
    function find_text(query: string, tab_id: string, case_sensitive: bool = false): [{}]
    function replace_text(query: string, replacement: string, tab_id: string): int
}

// ─── Language Server ───────────────────────────────────────────────────────

class LanguageServer {
    function init(): void
    function analyze(content: string, file_path: string = ""): [Diagnostic]
    function get_completions(content: string, line: int, column: int): [CompletionItem]
    function get_hover(content: string, line: int, column: int): {} | null
    function get_symbols(content: string, file_path: string = ""): [{}]
    function go_to_definition(content: string, line: int, column: int): DocumentRange | null
    function get_references(content: string, line: int, column: int): [DocumentRange]
    function format_document(content: string): string
}

// ─── Debugger ──────────────────────────────────────────────────────────────

class Debugger {
    function init(): void
    function start(): void
    function stop(): void
    function pause(): void
    function step_over(): void
    function step_into(): void
    function step_out(): void
    function continue(): void
    function add_breakpoint(file: string, line: int): Breakpoint
    function remove_breakpoint(file: string, line: int): bool
    function get_breakpoints(file: string = ""): [Breakpoint]
    function clear_breakpoints(file: string = ""): void
    function get_stack_frames(): [StackFrame]
    function get_variables(scope: string = ""): {string: VariableInfo}
    function evaluate(expression: string): string
}

// ─── Profiler ──────────────────────────────────────────────────────────────

class Profiler {
    function init(): void
    function start_session(name: string, type: ProfilerType = "cpu"): string
    function stop_session(session_id: string = ""): ProfileResult | null
    function add_sample(data: {}, session_id: string = ""): void
    function list_sessions(): [{}]
    function get_results(session_id: string = ""): ProfileResult | null
}

// ─── Visual Designer ───────────────────────────────────────────────────────

class VisualDesigner {
    function init(): void
    function add_component(component: UIComponent): string
    function remove_component(id: string): bool
    function get_component(id: string): UIComponent | null
    function list_components(): [UIComponent]
    function generate_code(component_id: string, language: string = "i"): string
}

// ─── AI Assistant ──────────────────────────────────────────────────────────

class AIAssistant {
    function init(): void
    function create_conversation(id: string = ""): string
    function send_message(message: string, conversation_id: string = ""): string
    function get_conversation(id: string): [ChatMessage]
    function list_conversations(): {string: int}
    function clear_conversation(id: string = ""): void
}

// ─── Extension Manager ─────────────────────────────────────────────────────

class ExtensionManager {
    function init(): void
    function install_plugin(manifest_path: string): PluginManifest
    function uninstall_plugin(id: string): bool
    function enable_plugin(id: string): bool
    function disable_plugin(id: string): bool
    function get_plugin(id: string): {} | null
    function list_plugins(): [{}]
    function register_extension_point(name: string, description: string = ""): void
}

// ─── Collaboration ─────────────────────────────────────────────────────────

class CollaborationManager {
    function init(): void
    function create_session(id: string, host: string, name: string = ""): {}
    function join_session(session_id: string, user_id: string): {} | null
    function leave_session(session_id: string, user_id: string): bool
    function add_user(user_id: string, name: string = "", role: string = "editor"): {}
    function get_session(id: string): {} | null
    function list_sessions(): [{}]
    function add_comment(file_path: string, user_id: string, content: string, line: int = 0): {}
    function get_comments(file_path: string = ""): {string: [{}]}
    function create_review(id: string, title: string, author: string, files: [string]): {}
    function get_reviews(): [{}]
}

// ─── Database Tools ────────────────────────────────────────────────────────

class DatabaseExplorer {
    function init(): void
    function connect(name: string, connection_string: string, db_type: string = "sqlite"): string
    function disconnect(name: string): bool
    function list_connections(): [{}]
    function execute_query(query: string, connection: string = ""): {}
    function get_tables(connection: string = ""): [string]
    function generate_select_query(table: string, columns: [string] = []): string
    function generate_insert_query(table: string, data: {}): string
}

// ─── Cloud Tools ───────────────────────────────────────────────────────────

class CloudExplorer {
    function init(): void
    function register_provider(name: string, type: string = "igicu", config: {} = {}): string
    function list_providers(): [{}]
    function list_resources(provider: string = ""): {string: [{}]}
    function deploy(name: string, provider: string, config: {}): {}
    function get_deployment(name: string): {} | null
    function list_deployments(): [{}]
    function get_logs(deployment: string, lines: int = 100): [string]
    function get_metrics(deployment: string): {}
}

// ─── Game Tools ────────────────────────────────────────────────────────────

class GameDesigner {
    function init(): void
    function add_asset(name: string, type: string = "sprite", path: string = ""): string
    function list_assets(): [{}]
    function create_scene(name: string, background: string = "", physics: bool = false): {}
    function list_scenes(): [{}]
    function create_animation(name: string, frames: [string], duration_ms: int = 100): {}
    function generate_scene_code(scene_name: string): string
}

// ─── System Tools ──────────────────────────────────────────────────────────

class SystemExplorer {
    function init(): void
    function get_system_info(): {}
    function get_cpu_info(): {}
    function get_memory_info(): {}
    function get_disk_info(): [{}]
    function get_network_info(): {}
    function list_processes(): [{}]
    function get_environment_variables(): {string: string}
}

// ─── Constants ─────────────────────────────────────────────────────────────

const ISTUDIO_VERSION: string = "0.1.0"
