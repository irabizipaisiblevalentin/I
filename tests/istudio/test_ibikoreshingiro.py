"""Tests for istudio.ibikoreshingiro — core types."""

from __future__ import annotations

from src.istudio.ibikoreshingiro import (
    AICompletionRequest,
    Breakpoint,
    BreakpointType,
    ChatMessage,
    CodeAction,
    CollaborationRole,
    CompletionItem,
    CompletionKind,
    CursorStyle,
    DebuggerError,
    DebuggerState,
    Diagnostic,
    DiagnosticSeverity,
    DocumentPosition,
    DocumentRange,
    EditorConfig,
    EditorError,
    EditorTheme,
    ExtensionPoint,
    FileType,
    HoverInfo,
    IStudioError,
    PluginError,
    PluginManifest,
    PluginState,
    PROJECT_TEMPLATES,
    PROJECT_TYPE_DISPLAY,
    ProfileResult,
    ProfilerType,
    ProjectConfig,
    ProjectError,
    ProjectTemplate,
    ProjectType,
    RefactoringAction,
    SearchResult,
    StackFrame,
    SymbolInfo,
    SymbolKind,
    TabInfo,
    TabSize,
    TestResult,
    VariableInfo,
    WorkspaceConfig,
    BuildTarget,
)


def test_enums_have_all_values():
    assert EditorTheme.DARK.value == "dark"
    assert EditorTheme.LIGHT.value == "light"
    assert CursorStyle.LINE.value == "line"
    assert CursorStyle.BLOCK.value == "block"
    assert TabSize.FOUR.value == 4
    assert FileType.I_LANG.value == "i"
    assert FileType.PYTHON.value == "py"
    assert DiagnosticSeverity.ERROR.value == "error"
    assert SymbolKind.FUNCTION.value == "function"
    assert CompletionKind.KEYWORD.value == "keyword"
    assert BreakpointType.LINE.value == "line"
    assert DebuggerState.RUNNING.value == "running"
    assert ProfilerType.CPU.value == "cpu"
    assert PluginState.ENABLED.value == "enabled"
    assert CollaborationRole.OWNER.value == "owner"


def test_editor_config_defaults():
    cfg = EditorConfig()
    assert cfg.theme == EditorTheme.DARK
    assert cfg.font_size == 14
    assert cfg.tab_size == TabSize.FOUR
    assert cfg.auto_save is True
    assert cfg.line_numbers is True
    assert cfg.minimap is True
    assert cfg.format_on_save is True


def test_workspace_config_defaults():
    cfg = WorkspaceConfig()
    assert cfg.name == "untitled"
    assert cfg.root_path == ""
    assert cfg.projects == []
    assert cfg.settings == {}


def test_project_config():
    cfg = ProjectConfig(name="test", version="1.0.0", type="library", language="i")
    assert cfg.name == "test"
    assert cfg.version == "1.0.0"
    assert cfg.type == "library"
    assert cfg.entry_point == "main.i"


def test_document_position():
    pos = DocumentPosition(line=5, column=10)
    assert pos.line == 5
    assert pos.column == 10


def test_document_range():
    r = DocumentRange(
        start=DocumentPosition(line=1, column=2),
        end=DocumentPosition(line=3, column=4),
    )
    assert r.start.line == 1
    assert r.end.line == 3


def test_diagnostic():
    d = Diagnostic(
        severity=DiagnosticSeverity.WARNING,
        message="test warning",
        source="i",
        code="W001",
    )
    assert d.severity == DiagnosticSeverity.WARNING
    assert d.message == "test warning"
    assert d.code == "W001"


def test_completion_item():
    c = CompletionItem(label="print", kind=CompletionKind.FUNCTION, detail="print function")
    assert c.label == "print"
    assert c.kind == CompletionKind.FUNCTION
    assert c.detail == "print function"


def test_symbol_info():
    s = SymbolInfo(name="main", kind=SymbolKind.FUNCTION)
    assert s.name == "main"
    assert s.kind == SymbolKind.FUNCTION


def test_breakpoint():
    bp = Breakpoint(file="main.i", line=42, type=BreakpointType.CONDITIONAL, condition="x > 0")
    assert bp.file == "main.i"
    assert bp.line == 42
    assert bp.type == BreakpointType.CONDITIONAL
    assert bp.condition == "x > 0"
    assert bp.enabled is True


def test_stack_frame():
    sf = StackFrame(id=1, name="foo", file="main.i", line=10, column=5, module="app")
    assert sf.id == 1
    assert sf.name == "foo"
    assert sf.line == 10


def test_variable_info():
    v = VariableInfo(name="x", value="42", type="int", children=[
        VariableInfo(name="y", value="7", type="int"),
    ])
    assert v.name == "x"
    assert v.value == "42"
    assert len(v.children) == 1


def test_profile_result():
    pr = ProfileResult(type=ProfilerType.CPU, total_time_ms=150.5, call_count=100)
    assert pr.type == ProfilerType.CPU
    assert pr.total_time_ms == 150.5
    assert pr.call_count == 100


def test_plugin_manifest():
    pm = PluginManifest(id="test-plugin", name="Test Plugin", version="2.0.0", permissions=["filesystem", "network"])
    assert pm.id == "test-plugin"
    assert pm.name == "Test Plugin"
    assert pm.version == "2.0.0"
    assert "filesystem" in pm.permissions


def test_tab_info():
    tab = TabInfo(id="tab1", title="main.i", file_path="/project/main.i", language="i")
    assert tab.id == "tab1"
    assert tab.is_dirty is False
    assert tab.is_readonly is False


def test_search_result():
    sr = SearchResult(file="main.i", line=10, column=5, match_length=3, line_content="hello world")
    assert sr.file == "main.i"
    assert sr.line == 10
    assert sr.match_length == 3


def test_refactoring_action():
    ra = RefactoringAction(name="rename", description="Rename variable")
    assert ra.name == "rename"


def test_code_action():
    ca = CodeAction(title="Fix issue", kind="quickfix")
    assert ca.title == "Fix issue"
    assert ca.kind == "quickfix"


def test_hover_info():
    hi = HoverInfo(contents=["**print**\n\nprint function"])
    assert len(hi.contents) == 1


def test_build_target():
    bt = BuildTarget(name="app", kind="executable", source_files=["main.i", "lib.i"])
    assert bt.name == "app"
    assert len(bt.source_files) == 2


def test_test_result():
    tr = TestResult(name="test_foo", passed=True, duration_ms=10.5)
    assert tr.passed is True
    assert tr.duration_ms == 10.5


def test_chat_message():
    msg = ChatMessage(role="user", content="Hello!")
    assert msg.role == "user"
    assert msg.content == "Hello!"


def test_ai_completion_request():
    req = AICompletionRequest(code="function foo()", language="i")
    assert req.code == "function foo()"
    assert req.language == "i"


def test_extension_point():
    ep = ExtensionPoint(name="editor.didOpen", description="File opened")
    assert ep.name == "editor.didOpen"


def test_error_hierarchy():
    assert issubclass(EditorError, IStudioError)
    assert issubclass(DebuggerError, IStudioError)
    assert issubclass(ProjectError, IStudioError)
    assert issubclass(PluginError, IStudioError)


def test_project_type_enum():
    assert ProjectType.WEBSITE.value == "website"
    assert ProjectType.GAME.value == "game"
    assert ProjectType.LIBRARY.value == "library"
    assert len(ProjectType) == 12


def test_project_type_display():
    assert "Website (Urubuga)" in PROJECT_TYPE_DISPLAY[ProjectType.WEBSITE]
    assert "Game (Imikino)" in PROJECT_TYPE_DISPLAY[ProjectType.GAME]


def test_project_templates_all_types():
    assert len(PROJECT_TEMPLATES) == len(ProjectType)
    for pt in ProjectType:
        assert pt in PROJECT_TEMPLATES
        tmpl = PROJECT_TEMPLATES[pt]
        assert isinstance(tmpl, ProjectTemplate)
        assert tmpl.display_name
        assert tmpl.ai_context
        assert tmpl.initial_dirs
        assert tmpl.entry_point


def test_project_template_defaults():
    tmpl = PROJECT_TEMPLATES[ProjectType.LIBRARY]
    assert tmpl.build_system == "i build --target library"
    assert tmpl.entry_point == "src/lib.i"
    assert "src" in tmpl.initial_dirs
    assert "src/lib.i" in tmpl.initial_files
