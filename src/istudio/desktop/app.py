"""I STUDIO Desktop — main application window (tkinter)."""

from __future__ import annotations

import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any

from ..ibikoreshingiro import ISTUDIO_VERSION, EditorTheme
from .controller import DesktopController
from .editor import CodeEditor
from .panel import BottomPanel
from .runner import ScriptRunner
from .sidebar import Sidebar
from .theme import get_palette, theme_names

APP_VERSION = "1.0.0"


class IStudioApp(tk.Tk):
    def __init__(self, workspace_path: str | None = None):
        super().__init__()
        self.title(f"I Studio {APP_VERSION}")
        self.geometry("1200x760")
        self.minsize(800, 500)

        self.controller = DesktopController(workspace_path=workspace_path)
        self.palette = get_palette(self.controller.current_theme())
        self._editors: dict[str, CodeEditor] = {}
        self._holders: dict[str, ttk.Frame] = {}
        self._untitled_index = 1
        self._runner_state = "idle"

        self._configure_style()
        self._build_ui()
        self._build_menu()
        self._bind_shortcuts()
        self._wire_runner()

        if workspace_path:
            self.sidebar.refresh_explorer()
        self._new_editor_tab()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._schedule_autosave()

    # ── Construction ─────────────────────────────────────────────────────

    def _configure_style(self) -> None:
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._apply_ui_theme(self.palette)

    def _build_ui(self) -> None:
        # Toolbar
        self.toolbar = ttk.Frame(self, padding=(4, 2))
        self.toolbar.pack(side="top", fill="x")
        self._tool_new = ttk.Button(self.toolbar, text="New", command=self.new_file)
        self._tool_new.pack(side="left", padx=2)
        self._tool_open = ttk.Button(self.toolbar, text="Open", command=self.open_file_dialog)
        self._tool_open.pack(side="left", padx=2)
        self._tool_folder = ttk.Button(self.toolbar, text="Open Folder", command=self.open_folder_dialog)
        self._tool_folder.pack(side="left", padx=2)
        self._tool_save = ttk.Button(self.toolbar, text="Save", command=self.save_active)
        self._tool_save.pack(side="left", padx=2)
        ttk.Separator(self.toolbar, orient="vertical").pack(side="left", fill="y", padx=6, pady=2)
        self._tool_run = ttk.Button(self.toolbar, text="Run", command=self.run_active)
        self._tool_run.pack(side="left", padx=2)
        self._tool_stop = ttk.Button(self.toolbar, text="Stop", command=self.stop_run, state="disabled")
        self._tool_stop.pack(side="left", padx=2)

        # Main split
        self.main_pane = ttk.Panedwindow(self, orient="horizontal")
        self.main_pane.pack(fill="both", expand=True)

        self.sidebar = Sidebar(self.main_pane, self.controller, self.palette, on_open_file=self.open_file)
        self.sidebar.pack(fill="both", expand=True)
        self.main_pane.add(self.sidebar, weight=0)

        self.center = ttk.Frame(self.main_pane)
        self.center.pack(fill="both", expand=True)
        self.main_pane.add(self.center, weight=1)

        self.tabs = ttk.Notebook(self.center)
        self.tabs.pack(fill="both", expand=True)
        self.tabs.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.tabs.bind("<Button-3>", self._on_tab_right_click)

        # Bottom panel
        self.bottom_pane = ttk.Panedwindow(self, orient="vertical")
        self.bottom_pane.pack(fill="both", expand=True)
        self.main_pane.pack_forget()
        self.bottom_pane.add(self.main_pane, weight=1)
        self.bottom = BottomPanel(self.bottom_pane, self.controller, self.palette)
        self.bottom_pane.add(self.bottom, weight=0)

        # Status bar
        self.status = tk.Frame(self, bg=self.palette["status.bg"])
        self.status.pack(side="bottom", fill="x")
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            self.status, textvariable=self.status_var, anchor="w",
            bg=self.palette["status.bg"], fg=self.palette["status.fg"], padx=8,
        ).pack(side="left", fill="x", expand=True)
        self.cursor_var = tk.StringVar(value="Ln 1, Col 1")
        tk.Label(
            self.status, textvariable=self.cursor_var, anchor="e",
            bg=self.palette["status.bg"], fg=self.palette["status.fg"], padx=8,
        ).pack(side="right")

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        m_file = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=m_file)
        m_file.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        m_file.add_command(label="Open File...", accelerator="Ctrl+O", command=self.open_file_dialog)
        m_file.add_command(label="Open Folder...", accelerator="Ctrl+K O", command=self.open_folder_dialog)
        m_file.add_separator()
        m_file.add_command(label="Save", accelerator="Ctrl+S", command=self.save_active)
        m_file.add_command(label="Save As...", accelerator="Ctrl+Shift+S", command=self.save_as_active)
        m_file.add_separator()
        m_file.add_command(label="Close Tab", accelerator="Ctrl+W", command=self.close_active_tab)
        m_file.add_command(label="Exit", accelerator="Ctrl+Q", command=self._on_close)

        m_edit = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=m_edit)
        m_edit.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: self._active_editor()._do_undo())
        m_edit.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: self._active_editor()._do_redo())
        m_edit.add_separator()
        m_edit.add_command(label="Format Document", accelerator="Shift+Alt+F", command=self.format_active)
        m_edit.add_command(label="Go to Definition", accelerator="F12", command=lambda: self._active_editor()._goto_definition())
        m_edit.add_command(label="Toggle Breakpoint", accelerator="F9", command=self.toggle_breakpoint_active)

        m_view = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=m_view)
        m_view.add_command(label="Show Symbols", accelerator="Ctrl+Shift+O", command=self.refresh_panels)
        m_view.add_command(label="Increase Font", accelerator="Ctrl+=", command=lambda: self._adjust_font(1))
        m_view.add_command(label="Decrease Font", accelerator="Ctrl+-", command=lambda: self._adjust_font(-1))
        m_view.add_separator()
        m_theme = tk.Menu(menubar, tearoff=0)
        m_view.add_cascade(label="Theme", menu=m_theme)
        for label, theme in theme_names().items():
            m_theme.add_command(label=label.title(), command=lambda t=theme: self.set_theme(t))

        m_run = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=m_run)
        m_run.add_command(label="Run File", accelerator="F5", command=self.run_active)
        m_run.add_command(label="Stop", command=self.stop_run)

        m_help = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=m_help)
        m_help.add_command(label="About I Studio", command=self._show_about)

    def _bind_shortcuts(self) -> None:
        self.bind_all("<Control-n>", lambda e: self.new_file())
        self.bind_all("<Control-o>", lambda e: self.open_file_dialog())
        self.bind_all("<Control-s>", lambda e: self.save_active())
        self.bind_all("<Control-Shift-S>", lambda e: self.save_as_active())
        self.bind_all("<Control-w>", lambda e: self.close_active_tab())
        self.bind_all("<Control-q>", lambda e: self._on_close())
        self.bind_all("<Control-k>", self._on_ctrl_k)
        self.bind_all("<Control-Shift-o>", lambda e: self.refresh_panels())
        self.bind_all("<F5>", lambda e: self.run_active())
        self.bind_all("<F9>", lambda e: self.toggle_breakpoint_active())
        self.bind_all("<Control-equal>", lambda e: self._adjust_font(1))
        self.bind_all("<Control-minus>", lambda e: self._adjust_font(-1))
        self.bind_all("<Shift-Alt-F>", lambda e: self.format_active())

    def _on_ctrl_k(self, event: tk.Event) -> str | None:
        if event.keysym.lower() == "o":
            self.open_folder_dialog()
            return "break"
        return None

    def _wire_runner(self) -> None:
        self.controller.runner = ScriptRunner(
            on_output=lambda text: self.after(0, lambda: self.bottom.append_run(text)),
            on_done=lambda ok, err: self.after(0, lambda: self._run_finished(ok, err)),
        )

    # ── Tabs ─────────────────────────────────────────────────────────────

    def _new_editor_tab(self, tab_id: str | None = None) -> None:
        if tab_id is None:
            tab_id = self.controller.engine.get_active_tab().id
        holder = ttk.Frame(self.tabs)
        editor = CodeEditor(
            holder,
            self.controller,
            tab_id,
            self.palette,
            on_status=self._on_status,
            on_change=self._on_change,
        )
        editor.pack(fill="both", expand=True)
        self._editors[tab_id] = editor
        self._holders[tab_id] = holder
        title = self.controller.get_active_tab().title
        self.tabs.add(holder, text=title)
        self.tabs.select(holder)
        editor.set_content(self.controller.get_content(tab_id))
        self.controller.analyze(tab_id)
        self.refresh_panels()
        editor.focus()

    def _active_editor(self) -> CodeEditor | None:
        tab = self.controller.get_active_tab()
        if not tab:
            return None
        return self._editors.get(tab.id)

    def _active_tab_id(self) -> str | None:
        tab = self.controller.get_active_tab()
        return tab.id if tab else None

    def _on_tab_changed(self, event: tk.Event) -> None:
        holder = self.tabs.select()
        if not holder:
            return
        for tab_id, h in self._holders.items():
            if str(h) == str(holder):
                self.controller.engine.set_active_tab(tab_id)
                self.sidebar.refresh_symbols(tab_id)
                self._update_status()
                break

    def _tab_id_at_index(self, index: int) -> str | None:
        for tab_id, holder in self._holders.items():
            try:
                if self.tabs.index(holder) == index:
                    return tab_id
            except tk.TclError:
                continue
        return None

    def _on_tab_right_click(self, event: tk.Event) -> None:
        try:
            index = self.tabs.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return
        tab_id = self._tab_id_at_index(index)
        if tab_id:
            self.close_tab(tab_id)

    def new_file(self) -> None:
        tab_id = self.controller.new_file()
        self._new_editor_tab(tab_id)

    def open_file(self, path: str | None, jump_to: int | None = None) -> None:
        if path:
            path = os.path.abspath(path)
            existing = None
            for tab_id, holder in self._holders.items():
                tab = _tab_by_id(self.controller, tab_id)
                if tab and os.path.abspath(tab.file_path or "") == path:
                    existing = tab_id
                    break
            if existing is not None:
                self.tabs.select(self._holders[existing])
            else:
                try:
                    tab_id = self.controller.open_file(path)
                except Exception as exc:  # pragma: no cover
                    messagebox.showerror("I Studio", f"Could not open file:\n{exc}")
                    return
                self._new_editor_tab(tab_id)
        if jump_to is not None:
            tab_id = self._active_tab_id()
            if tab_id:
                self._jump_to_line(tab_id, jump_to)

    def _jump_to_line(self, tab_id: str, jump_to: int | None) -> None:
        if jump_to is None:
            return
        editor = self._editors.get(tab_id)
        if not editor:
            return
        line = jump_to + 1
        editor.text.mark_set("insert", f"{line}.0")
        editor.text.see(f"{line}.0")
        editor._update_current_line()
        editor._sync_cursor()

    def open_file_dialog(self) -> None:
        path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[("I Source", "*.i"), ("All Files", "*.*")],
        )
        if path:
            self.open_file(path)

    def open_folder_dialog(self) -> None:
        path = filedialog.askdirectory(title="Open Folder")
        if path:
            self.open_folder(path)

    def open_folder(self, path: str) -> None:
        self.controller.open_folder(path)
        self.sidebar.refresh_explorer()
        self._update_status()

    def save_active(self) -> bool:
        editor = self._active_editor()
        if not editor:
            return False
        if not self.controller.save():
            return self.save_as_active()
        self._update_status()
        return True

    def save_as_active(self) -> bool:
        editor = self._active_editor()
        if not editor:
            return False
        tab = self.controller.get_active_tab()
        default = tab.title if tab else "untitled.i"
        path = filedialog.asksaveasfilename(
            title="Save As",
            initialfile=default,
            filetypes=[("I Source", "*.i"), ("All Files", "*.*")],
        )
        if not path:
            return False
        ok = self.controller.save_as(tab.id if tab else None, path)
        if ok and editor is not None:
            tab_id = tab.id if tab else None
            self._editors[tab_id].set_content(self.controller.get_content(tab_id))
            self.tabs.tab(self._holders[tab_id], text=self.controller.get_active_tab().title)
        self._update_status()
        return ok

    def close_active_tab(self) -> None:
        tab = self.controller.get_active_tab()
        if tab:
            self.close_tab(tab.id)

    def close_tab(self, tab_id: str) -> None:
        holder = self._holders.get(tab_id)
        if holder is None:
            return
        tab = _tab_by_id(self.controller, tab_id)
        if tab and tab.is_dirty:
            proceed = messagebox.askyesnocancel(
                "I Studio", f"Save changes to '{tab.title}'?"
            )
            if proceed is None:
                return
            if proceed:
                self.controller.engine.set_active_tab(tab_id)
                if not self.save_active():
                    return
        self.controller.close_file(tab_id)
        editor = self._editors.pop(tab_id)
        editor.destroy()
        self.tabs.forget(holder)
        self._holders.pop(tab_id)
        self.refresh_panels()
        if not self.controller.get_active_tab():
            self.new_file()
        self._update_status()

    # ── Callbacks ────────────────────────────────────────────────────────

    def _on_status(self, info: dict[str, Any]) -> None:
        self.cursor_var.set(f"Ln {info['line']}, Col {info['column']}")

    def _on_change(self, tab_id: str, force: bool) -> None:
        self.refresh_panels()
        self._update_status()

    def refresh_panels(self) -> None:
        tab_id = self._active_tab_id()
        self.sidebar.refresh_symbols(tab_id)
        self.bottom.refresh_problems()

    def _update_status(self) -> None:
        info = self.controller.get_status_info()
        dirty = "\u25cf" if info["dirty"] else ""
        root = os.path.basename(info["root"]) or ""
        self.status_var.set(
            f"{dirty}{info['file']}  |  {info['language']}  |  "
            f"{root or 'no workspace'}  |  {self.controller.current_theme().value} theme  |  run: {self._runner_state}"
        )

    # ── Editing actions ──────────────────────────────────────────────────

    def format_active(self) -> None:
        editor = self._active_editor()
        tab = self.controller.get_active_tab()
        if not editor or not tab:
            return
        formatted = self.controller.format_document(tab.id)
        if formatted is not None:
            editor.set_content(formatted)
            self.controller.analyze(tab.id)
            self.refresh_panels()
            self._update_status()

    def toggle_breakpoint_active(self) -> None:
        editor = self._active_editor()
        if editor:
            editor._toggle_breakpoint(editor._current_line)

    # ── Run ──────────────────────────────────────────────────────────────

    def run_active(self) -> None:
        if self._runner_state == "running":
            return
        tab = self.controller.get_active_tab()
        if not tab:
            return
        self.bottom.clear_run()
        self.bottom.append_run(f"\u25b6 Running {tab.file_path or tab.title}\n")
        self._runner_state = "running"
        self._tool_run.config(state="disabled")
        self._tool_stop.config(state="normal")
        self._update_status()
        self.controller.run_active(tab.id)

    def stop_run(self) -> None:
        self.controller.runner.stop()
        self.bottom.append_run("\u25a0 Stopped\n")
        self._runner_state = "idle"
        self._tool_run.config(state="normal")
        self._tool_stop.config(state="disabled")
        self._update_status()

    def _run_finished(self, ok: bool, error: str | None) -> None:
        if error:
            self.bottom.append_run(f"\n[error] {error}\n")
        else:
            self.bottom.append_run("\n[done]\n")
        self._runner_state = "idle"
        self._tool_run.config(state="normal")
        self._tool_stop.config(state="disabled")
        self._update_status()

    # ── Theme / font ─────────────────────────────────────────────────────

    def set_theme(self, theme: EditorTheme) -> None:
        self.palette = self.controller.set_theme(theme)
        self._apply_ui_theme(self.palette)
        for editor in self._editors.values():
            editor.apply_palette(self.palette)
        self.bottom.apply_palette(self.palette)
        self.status.config(bg=self.palette["status.bg"])
        for child in self.status.winfo_children():
            child.config(bg=self.palette["status.bg"], fg=self.palette["status.fg"])
        self._update_status()

    def _apply_ui_theme(self, palette: dict[str, str]) -> None:
        self.configure(bg=palette["panel.bg"])
        self.style.configure("TFrame", background=palette["panel.bg"])
        self.style.configure("TNotebook", background=palette["panel.bg"], borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            background=palette["panel.bg"],
            foreground=palette["panel.fg"],
            padding=(10, 4),
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", palette["panel.accent"])],
            foreground=[("selected", palette["status.fg"])],
        )
        self.style.configure(
            "Treeview",
            background=palette["panel.bg"],
            fieldbackground=palette["panel.bg"],
            foreground=palette["panel.fg"],
            borderwidth=0,
        )
        self.style.map(
            "Treeview",
            background=[("selected", palette["panel.accent"])],
            foreground=[("selected", palette["status.fg"])],
        )
        self.style.configure("TScrollbar", background=palette["panel.border"], troughcolor=palette["panel.bg"])
        self.style.configure("Toolbutton", background=palette["panel.bg"], foreground=palette["panel.fg"])

    def _adjust_font(self, delta: int) -> None:
        for editor in self._editors.values():
            current = editor._font.cget("size")
            editor._font.config(size=max(6, current + delta))
        self.controller.update_config(font_size=max(6, self.controller.engine.config.font_size + delta))

    # ── Lifecycle ────────────────────────────────────────────────────────

    def _schedule_autosave(self) -> None:
        config = self.controller.engine.config
        if config.auto_save:
            self._autosave()
        self.after(5000, self._schedule_autosave)

    def _autosave(self) -> None:
        for tab_id in list(self._editors):
            tab = _tab_by_id(self.controller, tab_id)
            if tab and tab.is_dirty and tab.file_path:
                try:
                    self.controller.engine.save_file(tab_id)
                except Exception:
                    pass

    def _on_close(self) -> None:
        dirty_tabs = [t.id for t in self.controller.engine.get_tabs() if t.is_dirty]
        if dirty_tabs:
            proceed = messagebox.askyesnocancel(
                "I Studio", f"{len(dirty_tabs)} file(s) have unsaved changes.\nSave before quitting?"
            )
            if proceed is None:
                return
            if proceed:
                for tab_id in dirty_tabs:
                    self.controller.engine.set_active_tab(tab_id)
                    if not self.save_active():
                        return
        self.destroy()

    def _show_about(self) -> None:
        messagebox.showinfo(
            "About I Studio",
            f"I Studio Desktop {APP_VERSION}\nI Programming Language {ISTUDIO_VERSION}\n\n"
            "The world's first professional programming language designed around Kinyarwanda.",
        )


def _tab_by_id(controller: Any, tab_id: str) -> Any:
    for tab in controller.engine.get_tabs():
        if tab.id == tab_id:
            return tab
    return None


def main(argv: list | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        prog="istudio-desktop",
        description="Launch the I Studio desktop application (I Programming Language IDE).",
    )
    parser.add_argument("path", nargs="?", default=None, help="workspace folder to open")
    parser.add_argument(
        "--version",
        action="version",
        version=f"I Studio Desktop {APP_VERSION} (I Programming Language v{ISTUDIO_VERSION})",
    )
    args = parser.parse_args(argv)

    workspace: str | None = None
    if args.path:
        workspace = str(Path(args.path).expanduser().resolve())

    app = IStudioApp(workspace_path=workspace)
    app.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
