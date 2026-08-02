"""I STUDIO Desktop — application controller (headless-testable).

The controller coordinates the editor engine, language server, workspace /
project managers, debugger, and script runner without any GUI dependency.
The desktop widgets are thin views over this controller.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..akazi import WorkspaceManager
from ..ibikoreshingiro import (
    CompletionItem,
    Diagnostic,
    DocumentPosition,
    DocumentRange,
    EditorConfig,
    EditorTheme,
    TabInfo,
)
from ..indura import EditorEngine
from ..ugutunganya import Debugger
from ..ururimi import LanguageServer
from .runner import ScriptRunner
from .theme import get_palette


class DesktopController:
    def __init__(self, workspace_path: str | None = None, config: EditorConfig | None = None):
        self.engine = EditorEngine(config)
        self.language = LanguageServer()
        self.workspace = WorkspaceManager()
        self.debugger = Debugger()
        self.runner = ScriptRunner()
        self._untitled_count = 0
        if workspace_path:
            self.workspace.load_or_create(workspace_path)
        self.new_file()

    # ── Tabs / files ─────────────────────────────────────────────────────

    def new_file(self, language: str = "i") -> str:
        self._untitled_count += 1
        title = f"untitled-{self._untitled_count}.{language}"
        tab = self.engine.create_tab(title, language=language)
        return tab.id

    def open_file(self, file_path: str) -> str:
        return self.engine.open_file(file_path).id

    def open_folder(self, path: str) -> None:
        self.workspace.load_or_create(path)

    def save(self, tab_id: str | None = None) -> bool:
        tab = self._resolve_tab(tab_id)
        if not tab or not tab.file_path:
            return False
        self.engine.save_file(tab.id)
        return True

    def save_as(self, tab_id: str | None, file_path: str) -> bool:
        tab = self._resolve_tab(tab_id)
        if not tab:
            return False
        self.engine.save_file_as(tab.id, file_path)
        return True

    def close_file(self, tab_id: str | None = None) -> bool:
        tab = self._resolve_tab(tab_id)
        if not tab:
            return False
        return self.engine.close_file(tab.id)

    def get_content(self, tab_id: str | None = None) -> str:
        tab = self._resolve_tab(tab_id)
        if not tab:
            return ""
        return self.engine.get_content(tab.id)

    def set_content(self, content: str, tab_id: str | None = None) -> list[Diagnostic]:
        tab = self._resolve_tab(tab_id)
        if not tab:
            return []
        self.engine.set_content(content, tab.id)
        return self.analyze(tab.id)

    def undo(self, tab_id: str | None = None) -> str | None:
        tab = self._resolve_tab(tab_id)
        return self.engine.undo(tab.id) if tab else None

    def redo(self, tab_id: str | None = None) -> str | None:
        tab = self._resolve_tab(tab_id)
        return self.engine.redo(tab.id) if tab else None

    # ── Language intelligence ────────────────────────────────────────────

    def analyze(self, tab_id: str | None = None) -> list[Diagnostic]:
        tab = self._resolve_tab(tab_id)
        if not tab:
            return []
        content = self.engine.get_content(tab.id)
        name = tab.file_path or tab.title
        return self.language.analyze(content, name)

    def get_diagnostics(self, tab_id: str | None = None) -> list[Diagnostic]:
        tab = self._resolve_tab(tab_id)
        if not tab:
            return []
        name = tab.file_path or tab.title
        return self.language.get_diagnostics(name)

    def get_completions(self, line: int, column: int, tab_id: str | None = None) -> list[CompletionItem]:
        tab = self._resolve_tab(tab_id)
        if not tab:
            return []
        content = self.engine.get_content(tab.id)
        name = tab.file_path or tab.title
        return self.language.get_completions(content, DocumentPosition(line=line, column=column), name)

    def get_hover(self, line: int, column: int, tab_id: str | None = None):
        tab = self._resolve_tab(tab_id)
        if not tab:
            return None
        content = self.engine.get_content(tab.id)
        name = tab.file_path or tab.title
        return self.language.get_hover(content, DocumentPosition(line=line, column=column), name)

    def go_to_definition(self, line: int, column: int, tab_id: str | None = None) -> DocumentRange | None:
        tab = self._resolve_tab(tab_id)
        if not tab:
            return None
        content = self.engine.get_content(tab.id)
        name = tab.file_path or tab.title
        return self.language.go_to_definition(content, DocumentPosition(line=line, column=column), name)

    def get_symbols(self, tab_id: str | None = None) -> list[Any]:
        tab = self._resolve_tab(tab_id)
        if not tab:
            return []
        content = self.engine.get_content(tab.id)
        name = tab.file_path or tab.title
        return self.language.get_symbols(content, name)

    def format_document(self, tab_id: str | None = None) -> str | None:
        tab = self._resolve_tab(tab_id)
        if not tab:
            return None
        content = self.engine.get_content(tab.id)
        name = tab.file_path or tab.title
        formatted = self.language.format_document(content, name)
        self.engine.set_content(formatted, tab.id)
        return formatted

    def find_text(self, query: str, tab_id: str | None = None) -> list[dict[str, Any]]:
        tab = self._resolve_tab(tab_id)
        if not tab:
            return []
        return self.engine.find_text(query, tab.id)

    # ── Workspace ────────────────────────────────────────────────────────

    def list_workspace_files(self, extensions: list[str] | None = None) -> list[str]:
        root = self.workspace.get_root_path()
        if not root:
            return []
        exts = extensions or [".i"]
        files: list[str] = []
        for path in sorted(Path(root).rglob("*")):
            if path.is_file() and path.suffix.lower() in exts:
                if ".git" in path.parts:
                    continue
                files.append(str(path))
        return files

    def list_projects(self) -> list[Any]:
        return self.workspace.project_manager.list_projects()

    # ── Debugging ────────────────────────────────────────────────────────

    def toggle_breakpoint(self, line: int, tab_id: str | None = None):
        tab = self._resolve_tab(tab_id)
        if not tab:
            return None
        name = tab.file_path or tab.title
        return self.debugger.toggle_breakpoint(name, line)

    def get_breakpoints(self) -> list[Any]:
        return self.debugger.get_breakpoints()

    # ── Running ──────────────────────────────────────────────────────────

    def run_active(self, tab_id: str | None = None):
        tab = self._resolve_tab(tab_id)
        if not tab:
            return None
        if tab.file_path:
            return self.runner.run_file(tab.file_path)
        return self.runner.run_source(self.engine.get_content(tab.id), tab.title)

    def is_running(self) -> bool:
        return self.runner.is_running

    # ── Theme / config ───────────────────────────────────────────────────

    def set_theme(self, theme: EditorTheme) -> dict[str, str]:
        self.engine.update_config(theme=theme)
        return get_palette(theme)

    def current_theme(self) -> EditorTheme:
        return self.engine.config.theme

    def update_config(self, **kwargs: Any) -> None:
        self.engine.update_config(**kwargs)

    def get_status_info(self) -> dict[str, Any]:
        tab = self.engine.get_active_tab()
        if not tab:
            return {"file": "", "language": "", "dirty": False, "root": self.workspace.get_root_path() or ""}
        return {
            "file": tab.title,
            "language": tab.language,
            "dirty": tab.is_dirty,
            "root": self.workspace.get_root_path() or "",
        }

    def get_active_tab(self) -> TabInfo | None:
        return self.engine.get_active_tab()

    def _resolve_tab(self, tab_id: str | None) -> TabInfo | None:
        if tab_id:
            for tab in self.engine.get_tabs():
                if tab.id == tab_id:
                    return tab
            return None
        return self.engine.get_active_tab()
