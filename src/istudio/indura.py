"""I STUDIO — Editor Engine (Indura)."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .ibikoreshingiro import (
    CompletionItem,
    CompletionKind,
    DocumentPosition,
    DocumentRange,
    EditorConfig,
    EditorError,
    EditorTheme,
    FileType,
    TabInfo,
)


class EditorEngine:
    def __init__(self, config: Optional[EditorConfig] = None):
        self._config = config or EditorConfig()
        self._tabs: Dict[str, TabInfo] = {}
        self._active_tab_id: Optional[str] = None
        self._file_contents: Dict[str, str] = {}
        self._undo_stack: Dict[str, List[Dict[str, Any]]] = {}
        self._redo_stack: Dict[str, List[Dict[str, Any]]] = {}
        self._listeners: Dict[str, List[callable]] = {}

    @property
    def config(self) -> EditorConfig:
        return self._config

    def update_config(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)

    def open_file(self, file_path: str) -> TabInfo:
        path = Path(file_path).resolve()
        if not path.exists():
            raise EditorError(f"File not found: {file_path}")
        content = path.read_text(encoding="utf-8")
        tab_id = str(path)
        ext = path.suffix.lstrip(".") or "txt"
        tab = TabInfo(
            id=tab_id,
            title=path.name,
            file_path=str(path),
            language=ext,
            is_dirty=False,
            is_readonly=not os.access(str(path), os.W_OK),
        )
        self._tabs[tab_id] = tab
        self._file_contents[tab_id] = content
        self._undo_stack[tab_id] = []
        self._redo_stack[tab_id] = []
        self._active_tab_id = tab_id
        self._emit("tab.opened", {"tab": tab})
        return tab

    def create_tab(self, title: str, language: str = "i", content: str = "") -> TabInfo:
        tab_id = f"untitled:{int(time.time() * 1000)}:{len(self._tabs)}"
        tab = TabInfo(
            id=tab_id,
            title=title,
            file_path="",
            language=language,
            is_dirty=bool(content),
        )
        self._tabs[tab_id] = tab
        self._file_contents[tab_id] = content
        self._undo_stack[tab_id] = []
        self._redo_stack[tab_id] = []
        self._active_tab_id = tab_id
        self._emit("tab.opened", {"tab": tab})
        return tab

    def save_file_as(self, tab_id: str, file_path: str) -> bool:
        if tab_id not in self._tabs:
            raise EditorError(f"Tab not found: {tab_id}")
        tab = self._tabs[tab_id]
        path = Path(file_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._file_contents.get(tab_id, ""), encoding="utf-8")
        tab.file_path = str(path)
        tab.title = path.name
        tab.language = path.suffix.lstrip(".") or tab.language
        tab.is_dirty = False
        tab.is_readonly = not os.access(str(path), os.W_OK)
        self._emit("file.saved", {"tab_id": tab_id, "path": tab.file_path})
        return True

    def close_file(self, tab_id: str) -> bool:
        if tab_id in self._tabs:
            del self._tabs[tab_id]
            self._file_contents.pop(tab_id, None)
            self._undo_stack.pop(tab_id, None)
            self._redo_stack.pop(tab_id, None)
            if self._active_tab_id == tab_id:
                self._active_tab_id = next(iter(self._tabs)) if self._tabs else None
            self._emit("tab.closed", {"tab_id": tab_id})
            return True
        return False

    def get_content(self, tab_id: Optional[str] = None) -> str:
        tab_id = tab_id or self._active_tab_id
        if not tab_id:
            raise EditorError("No active tab")
        return self._file_contents.get(tab_id, "")

    def set_content(self, content: str, tab_id: Optional[str] = None) -> None:
        tab_id = tab_id or self._active_tab_id
        if not tab_id:
            raise EditorError("No active tab")
        old_content = self._file_contents.get(tab_id, "")
        if old_content != content:
            self._undo_stack.setdefault(tab_id, []).append({
                "before": old_content,
                "after": content,
                "timestamp": time.time(),
            })
            self._redo_stack[tab_id] = []
            if len(self._undo_stack[tab_id]) > 100:
                self._undo_stack[tab_id] = self._undo_stack[tab_id][-100:]
        self._file_contents[tab_id] = content
        self._tabs[tab_id].is_dirty = True
        self._emit("content.changed", {"tab_id": tab_id})

    def insert_text(self, text: str, position: DocumentPosition, tab_id: Optional[str] = None) -> str:
        content = self.get_content(tab_id)
        lines = content.split("\n")
        line_idx = min(position.line, len(lines) - 1)
        line = lines[line_idx]
        col = min(position.column, len(line))
        lines[line_idx] = line[:col] + text + line[col:]
        new_content = "\n".join(lines)
        self.set_content(new_content, tab_id)
        return new_content

    def delete_range(self, start: DocumentPosition, end: DocumentPosition, tab_id: Optional[str] = None) -> str:
        content = self.get_content(tab_id)
        lines = content.split("\n")
        if start.line == end.line:
            line = lines[start.line]
            lines[start.line] = line[:start.column] + line[end.column:]
        else:
            first_line = lines[start.line][:start.column]
            last_line = lines[end.line][end.column:]
            lines = lines[:start.line] + [first_line + last_line] + lines[end.line + 1:]
        new_content = "\n".join(lines)
        self.set_content(new_content, tab_id)
        return new_content

    def save_file(self, tab_id: Optional[str] = None) -> bool:
        tab_id = tab_id or self._active_tab_id
        if not tab_id:
            raise EditorError("No active tab")
        tab = self._tabs.get(tab_id)
        if not tab:
            raise EditorError(f"Tab not found: {tab_id}")
        content = self._file_contents.get(tab_id, "")
        Path(tab.file_path).write_text(content, encoding="utf-8")
        tab.is_dirty = False
        self._emit("file.saved", {"tab_id": tab_id, "path": tab.file_path})
        return True

    def undo(self, tab_id: Optional[str] = None) -> Optional[str]:
        tab_id = tab_id or self._active_tab_id
        if not tab_id:
            return None
        stack = self._undo_stack.get(tab_id, [])
        if not stack:
            return None
        change = stack.pop()
        self._redo_stack.setdefault(tab_id, []).append(change)
        self._file_contents[tab_id] = change["before"]
        self._tabs[tab_id].is_dirty = True
        self._emit("undo", {"tab_id": tab_id})
        return change["before"]

    def redo(self, tab_id: Optional[str] = None) -> Optional[str]:
        tab_id = tab_id or self._active_tab_id
        if not tab_id:
            return None
        stack = self._redo_stack.get(tab_id, [])
        if not stack:
            return None
        change = stack.pop()
        self._undo_stack.setdefault(tab_id, []).append(change)
        self._file_contents[tab_id] = change["after"]
        self._tabs[tab_id].is_dirty = True
        self._emit("redo", {"tab_id": tab_id})
        return change["after"]

    def get_tabs(self) -> List[TabInfo]:
        return list(self._tabs.values())

    def get_active_tab(self) -> Optional[TabInfo]:
        if not self._active_tab_id:
            return None
        return self._tabs.get(self._active_tab_id)

    def set_active_tab(self, tab_id: str) -> bool:
        if tab_id in self._tabs:
            self._active_tab_id = tab_id
            self._emit("tab.activated", {"tab_id": tab_id})
            return True
        return False

    def get_cursor_position(self, tab_id: Optional[str] = None) -> DocumentPosition:
        tab = self._get_tab(tab_id)
        return tab.cursor_position

    def set_cursor_position(self, position: DocumentPosition, tab_id: Optional[str] = None) -> None:
        tab = self._get_tab(tab_id)
        tab.cursor_position = position
        self._emit("cursor.moved", {"tab_id": tab.id, "position": position})

    def find_text(self, query: str, tab_id: Optional[str] = None, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        content = self.get_content(tab_id)
        results = []
        if not case_sensitive:
            content_lower = content.lower()
            query = query.lower()
        for line_idx, line in enumerate(content.split("\n")):
            search_line = line if case_sensitive else line.lower()
            col = 0
            while True:
                col = search_line.find(query, col)
                if col == -1:
                    break
                results.append({"line": line_idx, "column": col, "length": len(query), "line_content": line})
                col += 1
        return results

    def replace_text(self, query: str, replacement: str, tab_id: Optional[str] = None, case_sensitive: bool = False) -> int:
        content = self.get_content(tab_id)
        if not case_sensitive:
            import re
            new_content, count = re.subn(re.escape(query), replacement, content, flags=re.IGNORECASE)
        else:
            new_content = content.replace(query, replacement)
            count = content.count(query)
        if count > 0:
            self.set_content(new_content, tab_id)
        return count

    def on(self, event: str, handler: callable) -> None:
        self._listeners.setdefault(event, []).append(handler)

    def off(self, event: str, handler: callable) -> None:
        handlers = self._listeners.get(event, [])
        if handler in handlers:
            handlers.remove(handler)

    def _emit(self, event: str, data: Dict[str, Any]) -> None:
        for handler in self._listeners.get(event, []):
            try:
                handler(data)
            except Exception:
                pass

    def _get_tab(self, tab_id: Optional[str] = None) -> TabInfo:
        tab_id = tab_id or self._active_tab_id
        if not tab_id or tab_id not in self._tabs:
            raise EditorError("No active tab")
        return self._tabs[tab_id]

    @staticmethod
    def detect_file_type(file_path: str) -> FileType:
        ext = Path(file_path).suffix.lstrip(".").lower()
        for ft in FileType:
            if ft.value == ext:
                return ft
        return FileType.TEXT
