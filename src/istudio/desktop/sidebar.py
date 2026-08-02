"""I STUDIO Desktop — sidebar (file explorer + symbols outline)."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Any

from ..ibikoreshingiro import SymbolKind


class Sidebar(ttk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        controller: Any,
        palette: dict[str, str],
        on_open_file: callable | None = None,
    ):
        super().__init__(master)
        self.controller = controller
        self.palette = palette
        self.on_open_file = on_open_file
        self._file_paths: dict[str, str] = {}
        self._symbol_ranges = {}

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.explorer = ttk.Frame(self.notebook)
        self.notebook.add(self.explorer, text="Explorer")

        self.explorer_tree = ttk.Treeview(self.explorer, show="tree")
        explorer_scroll = ttk.Scrollbar(self.explorer, orient="vertical", command=self.explorer_tree.yview)
        self.explorer_tree.configure(yscrollcommand=explorer_scroll.set)
        self.explorer_tree.pack(side="left", fill="both", expand=True)
        explorer_scroll.pack(side="right", fill="y")
        self.explorer_tree.bind("<Double-Button-1>", self._on_explorer_open)
        self.explorer_tree.bind("<Return>", self._on_explorer_open)

        self.symbols = ttk.Frame(self.notebook)
        self.notebook.add(self.symbols, text="Symbols")

        self.symbols_tree = ttk.Treeview(self.symbols, show="tree")
        symbols_scroll = ttk.Scrollbar(self.symbols, orient="vertical", command=self.symbols_tree.yview)
        self.symbols_tree.configure(yscrollcommand=symbols_scroll.set)
        self.symbols_tree.pack(side="left", fill="both", expand=True)
        symbols_scroll.pack(side="right", fill="y")
        self.symbols_tree.bind("<Double-Button-1>", self._on_symbols_open)

    # ── Explorer ─────────────────────────────────────────────────────────

    def refresh_explorer(self) -> None:
        self.explorer_tree.delete(*self.explorer_tree.get_children())
        self._file_paths.clear()
        root = self.controller.workspace.get_root_path()
        if not root:
            self.explorer_tree.insert("", "end", text="Open a folder (Ctrl+K O)")
            return
        root_path = Path(root)
        self.explorer_tree.insert("", "end", text=root_path.name, open=True)
        parent_node = ""

        def add_dir(node: str, directory: Path) -> None:
            dirs = sorted((p for p in directory.iterdir() if p.is_dir() and p.name not in (".git", "__pycache__", ".venv", "venv", "node_modules")), key=lambda p: p.name.lower())
            files = sorted((p for p in directory.iterdir() if p.is_file()), key=lambda p: p.name.lower())
            for d in dirs:
                child = self.explorer_tree.insert(node, "end", text=f"{d.name}/", open=False)
                add_dir(child, d)
            for f in files:
                iid = self.explorer_tree.insert(node, "end", text=f.name)
                self._file_paths[iid] = str(f)

        add_dir(parent_node, root_path)

    def _on_explorer_open(self, event: tk.Event) -> None:
        selection = self.explorer_tree.selection()
        if not selection:
            return
        path = self._file_paths.get(selection[0])
        if path and self.on_open_file is not None:
            self.on_open_file(path)

    # ── Symbols outline ──────────────────────────────────────────────────

    def refresh_symbols(self, tab_id: str | None = None) -> None:
        self.symbols_tree.delete(*self.symbols_tree.get_children())
        symbols = self.controller.get_symbols(tab_id)
        self._symbol_ranges = {}
        for sym in symbols:
            icon = _symbol_icon(sym.kind)
            iid = self.symbols_tree.insert("", "end", text=f"{icon} {sym.name}")
            self._symbol_ranges[iid] = sym.range

    def _on_symbols_open(self, event: tk.Event) -> None:
        selection = self.symbols_tree.selection()
        if not selection:
            return
        rng = self._symbol_ranges.get(selection[0])
        if rng and self.on_open_file is not None:
            self.on_open_file(None, jump_to=rng.start.line)


def _symbol_icon(kind: SymbolKind) -> str:
    return {
        SymbolKind.CLASS: "\u25c9",
        SymbolKind.FUNCTION: "\u0192",
        SymbolKind.METHOD: "\u0192",
        SymbolKind.VARIABLE: "\u2022",
        SymbolKind.CONSTANT: "\u0394",
        SymbolKind.MODULE: "\u25a6",
    }.get(kind, "\u2022")
