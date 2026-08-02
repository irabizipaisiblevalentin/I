"""I STUDIO Desktop — code editor widget (tkinter).

A code editor built on ``tk.Text``: line-number gutter with breakpoint
markers, syntax highlighting, bracket matching, current-line highlight,
live diagnostics underlines, autocomplete popup, hover tooltips,
go-to-definition, and undo/redo driven by the editor engine.
"""

from __future__ import annotations

import re
import tkinter as tk
import tkinter.font as tkfont
from typing import Any

from ..ibikoreshingiro import Diagnostic, DiagnosticSeverity
from .highlight import tokenize_line

_BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}"}
_BRACKET_REVERSE = {v: k for k, v in _BRACKET_PAIRS.items()}

_TAG_MAP = {
    "keyword": "syntax.keyword",
    "string": "syntax.string",
    "number": "syntax.number",
    "comment": "syntax.comment",
    "builtin": "syntax.builtin",
    "operator": "syntax.operator",
}

_MONOSPACE_CANDIDATES = (
    "Cascadia Mono",
    "Cascadia Code",
    "Consolas",
    "JetBrains Mono",
    "Fira Code",
    "Courier New",
)


class CompletionPopup:
    """Small overlay listbox used for autocompletion."""

    def __init__(self, editor: CodeEditor):
        self.editor = editor
        self.top = tk.Toplevel(editor)
        self.top.withdraw()
        self.top.overrideredirect(True)
        self.listbox = tk.Listbox(
            self.top,
            activestyle="none",
            exportselection=False,
            borderwidth=1,
            relief="solid",
        )
        self.listbox.pack(fill="both", expand=True)
        self._items: list[Any] = []
        self._selected: Any | None = None
        self.listbox.bind("<ButtonRelease-1>", lambda e: self.accept())

    @property
    def open(self) -> bool:
        return self.top.state() != "withdrawn"

    def show(self, items: list[Any], x: int, y: int) -> None:
        self._items = items
        self.listbox.delete(0, "end")
        for item in items:
            label = getattr(item, "label", str(item))
            detail = getattr(item, "detail", "")
            self.listbox.insert("end", f"{label}  {detail}" if detail else label)
        if not items:
            self.hide()
            return
        width = max(len(self.listbox.get(i)) for i in range(self.listbox.size())) + 4
        self.listbox.config(width=max(width, 16), height=min(len(items), 10))
        self.top.geometry(f"+{x}+{y}")
        self._select(0)
        self.top.deiconify()
        self.top.lift()
        self.editor.text.focus_set()

    def hide(self) -> None:
        self.top.withdraw()
        self._items = []
        self._selected = None

    def move(self, delta: int) -> None:
        if not self.open or not self._items:
            return
        current = self.listbox.curselection()
        idx = current[0] if current else 0
        idx = max(0, min(len(self._items) - 1, idx + delta))
        self._select(idx)

    def accept(self) -> bool:
        if not self.open or self._selected is None:
            return False
        self.editor._insert_completion(self._selected)
        self.hide()
        return True

    def _select(self, index: int) -> None:
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(index)
        self.listbox.activate(index)
        self.listbox.see(index)
        self._selected = self._items[index]


class CodeEditor(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        controller: Any,
        tab_id: str,
        palette: dict[str, str],
        on_status: callable | None = None,
        on_change: callable | None = None,
    ):
        super().__init__(master)
        self.controller = controller
        self.tab_id = tab_id
        self.palette = palette
        self.on_status = on_status
        self.on_change = on_change

        config = controller.engine.config
        self._font_family = self._pick_font_family()
        self._font = tkfont.Font(family=self._font_family, size=config.font_size)
        self._gutter_width = 46

        self.gutter = tk.Canvas(self, width=self._gutter_width, highlightthickness=0, bd=0)
        self.text = tk.Text(
            self,
            wrap="none",
            undo=False,
            font=self._font,
            insertwidth=2,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            tabs=(self._font.measure(" " * config.tab_size.value),),
            spacing1=1,
        )

        self._breakpoint_lines: set = set()
        self._diagnostics: list[Diagnostic] = []
        self._current_line = 1
        self._hover_after: str | None = None
        self._completion_after: str | None = None
        self._tooltip: tk.Toplevel | None = None
        self._formatting = False

        self.gutter.pack(side="left", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        self._setup_tags()
        self._bind_events()
        self.completion = CompletionPopup(self)

    # ── Setup ────────────────────────────────────────────────────────────

    def _pick_font_family(self) -> str:
        try:
            families = set(tkfont.families(self))
        except Exception:  # pragma: no cover
            families = set()
        for name in _MONOSPACE_CANDIDATES:
            if name in families:
                return name
        return "TkFixedFont"

    def _setup_tags(self) -> None:
        self.text.tag_config("current.line", background=self.palette["current_line"])
        self.text.tag_config("match.bracket", background=self.palette["bracket_match"])
        self.text.tag_config("diag.error", underline=True, underlinefg=self.palette["diagnostic.error"])
        self.text.tag_config("diag.warning", underline=True, underlinefg=self.palette["diagnostic.warning"])
        self.text.tag_config("goto.highlight", background=self.palette["selection"])

    def _bind_events(self) -> None:
        self.text.bind("<KeyRelease>", self._on_key_release)
        self.text.bind("<Return>", self._on_return)
        self.text.bind("<Tab>", self._on_tab)
        self.text.bind("<Control-space>", self._trigger_completion)
        self.text.bind("<Down>", lambda e: self._popup_key(e, 1))
        self.text.bind("<Up>", lambda e: self._popup_key(e, -1))
        self.text.bind("<Escape>", self._popup_escape)
        self.text.bind("<Button-1>", self._on_click)
        self.text.bind("<ButtonRelease-1>", self._on_click_release)
        self.text.bind("<Control-Motion>", self._on_control_motion)
        self.text.bind("<Button-4>", lambda e: self._scroll())
        self.text.bind("<Button-5>", lambda e: self._scroll())
        self.text.bind("<MouseWheel>", lambda e: self._scroll())
        self.text.bind("<Configure>", lambda e: self._redraw_gutter())
        self.text.bind("<Control-z>", lambda e: self._do_undo())
        self.text.bind("<Control-y>", self._do_redo)
        self.text.bind("<Control-Shift-z>", self._do_redo)
        self.text.bind("<F12>", self._goto_definition)
        self.gutter.bind("<Button-1>", self._on_gutter_click)

    # ── Content ──────────────────────────────────────────────────────────

    def set_content(self, content: str) -> None:
        self._formatting = True
        self.text.delete("1.0", "end")
        if content:
            self.text.insert("1.0", content)
        self.text.edit_reset()
        self._formatting = False
        self._highlight_all()
        self._refresh_diagnostics()
        self._redraw_gutter()
        self._update_current_line()
        self._sync_cursor()

    def get_content(self) -> str:
        return self.text.get("1.0", "end-1c")

    def focus(self) -> None:
        self.text.focus_set()

    # ── Highlighting ─────────────────────────────────────────────────────

    def _highlight_all(self) -> None:
        for tag in _TAG_MAP.values():
            self.text.tag_remove(tag, "1.0", "end")
        first, last = self._visible_range()
        for line in range(first, last + 1):
            self._highlight_line(line)

    def _highlight_line(self, line: int) -> None:
        start = f"{line}.0"
        end = self.text.index(f"{line}.end")
        for tag in _TAG_MAP.values():
            self.text.tag_remove(tag, start, end)
        content = self.text.get(start, end)
        for cstart, cend, tag in tokenize_line(content):
            self.text.tag_add(_TAG_MAP.get(tag, tag), f"{line}.{cstart}", f"{line}.{cend}")

    def _visible_range(self) -> tuple:
        first = int(str(self.text.index("@0,0")).split(".")[0])
        last = int(str(self.text.index("@0,1000000")).split(".")[0])
        return max(1, first), max(first, last)

    # ── Change handling ──────────────────────────────────────────────────

    def _on_key_release(self, event: tk.Event) -> None:
        if self._formatting:
            return
        self._after_text_change()
        self._schedule_completion(event)

    def _after_text_change(self) -> None:
        self._sync_to_engine()
        self._refresh_diagnostics()
        self._redraw_gutter()
        self._update_current_line()
        self._sync_cursor()
        if self.on_change is not None:
            self.on_change(self.tab_id, False)

    def _sync_to_engine(self) -> None:
        self.controller.set_content(self.get_content(), self.tab_id)

    def _refresh_diagnostics(self) -> None:
        self.text.tag_remove("diag.error", "1.0", "end")
        self.text.tag_remove("diag.warning", "1.0", "end")
        self._diagnostics = self.controller.get_diagnostics(self.tab_id)
        for d in self._diagnostics:
            line = d.range.start.line + 1
            start_col = d.range.start.column
            end_col = d.range.end.column
            if end_col <= start_col:
                end_col = len(self.text.get(f"{line}.0", f"{line}.end")) or start_col + 1
            tag = "diag.error" if d.severity == DiagnosticSeverity.ERROR else "diag.warning"
            self.text.tag_add(tag, f"{line}.{start_col}", f"{line}.{end_col}")

    def _update_current_line(self) -> None:
        self.text.tag_remove("current.line", "1.0", "end")
        line = int(str(self.text.index("insert")).split(".")[0])
        self._current_line = line
        self.text.tag_add("current.line", f"{line}.0", f"{line}.end")
        self._match_brackets(line)

    def _match_brackets(self, line: int) -> None:
        self.text.tag_remove("match.bracket", "1.0", "end")
        col = int(str(self.text.index("insert")).split(".")[1])
        char = self.text.get(f"{line}.{col}", f"{line}.{col + 1}")
        if char in _BRACKET_PAIRS or char in _BRACKET_REVERSE:
            match = self._find_matching_bracket(line, col, char)
            if match:
                self.text.tag_add("match.bracket", f"{line}.{col}", f"{line}.{col + 1}")
                self.text.tag_add("match.bracket", f"{match[0]}.{match[1]}", f"{match[0]}.{match[1] + 1}")

    def _find_matching_bracket(self, line: int, col: int, char: str) -> tuple | None:
        content = self.get_content()
        lines = content.split("\n")
        if line - 1 >= len(lines):
            return None
        pos = sum(len(ln) + 1 for ln in lines[: line - 1]) + col
        if char in _BRACKET_PAIRS:
            opening, closing = char, _BRACKET_PAIRS[char]
            depth = 0
            for i in range(pos, len(content)):
                c = content[i]
                if c == opening:
                    depth += 1
                elif c == closing:
                    depth -= 1
                    if depth == 0:
                        before = content[:i]
                        return before.count("\n") + 1, i - (before.rfind("\n") + 1)
        elif char in _BRACKET_REVERSE:
            opening, closing = _BRACKET_REVERSE[char], char
            depth = 0
            for i in range(pos, -1, -1):
                c = content[i]
                if c == closing:
                    depth += 1
                elif c == opening:
                    depth -= 1
                    if depth == 0:
                        before = content[:i]
                        return before.count("\n") + 1, i - (before.rfind("\n") + 1)
        return None

    def _sync_cursor(self) -> None:
        if self.on_status is None:
            return
        line, col = str(self.text.index("insert")).split(".")
        self.on_status({"line": int(line), "column": int(col) + 1})

    # ── Keyboard handling ────────────────────────────────────────────────

    def _on_return(self, event: tk.Event) -> str:
        if self.completion.open:
            self.completion.accept()
            return "break"
        line = int(str(self.text.index("insert")).split(".")[0])
        current = self.text.get(f"{line}.0", f"{line}.end")
        indent = re.match(r"^\s*", current).group(0)
        if current.rstrip().endswith(("{", "(", "[")):
            indent += " " * self.controller.engine.config.tab_size.value
        self.text.insert("insert", f"\n{indent}")
        self.text.see("insert")
        self._after_text_change()
        return "break"

    def _on_tab(self, event: tk.Event) -> str:
        if self.completion.open:
            self.completion.accept()
            return "break"
        size = self.controller.engine.config.tab_size.value
        self.text.insert("insert", " " * size)
        self._after_text_change()
        return "break"

    def _popup_key(self, event: tk.Event, delta: int) -> str | None:
        if self.completion.open:
            self.completion.move(delta)
            return "break"
        return None

    def _popup_escape(self, event: tk.Event) -> str | None:
        if self.completion.open:
            self.completion.hide()
            return "break"
        return None

    # ── Completions ──────────────────────────────────────────────────────

    def _schedule_completion(self, event: tk.Event) -> None:
        if self._completion_after:
            self.after_cancel(self._completion_after)
            self._completion_after = None
        if not event.char or not (event.char.isalnum() or event.char == "_"):
            if event.keysym == "BackSpace":
                self.completion.hide()
            return
        self._completion_after = self.after(300, self._auto_complete)

    def _trigger_completion(self, event: tk.Event | None = None) -> str:
        self._show_completions()
        return "break"

    def _auto_complete(self) -> None:
        self._completion_after = None
        self._show_completions()

    def _show_completions(self) -> None:
        line, col = str(self.text.index("insert")).split(".")
        items = self.controller.get_completions(int(line), int(col) - 1, self.tab_id)
        if not items:
            self.completion.hide()
            return
        bbox = self.text.bbox("insert")
        if not bbox:
            self.completion.hide()
            return
        x = self.text.winfo_rootx() + bbox[0]
        y = self.text.winfo_rooty() + bbox[1] + bbox[3]
        self.completion.show(items, x, y)

    def _insert_completion(self, item: Any) -> None:
        start, end = self._word_bounds()
        insert_text = getattr(item, "insert_text", "") or getattr(item, "label", "")
        cleaned, offset = _clean_snippet(insert_text)
        self.text.delete(start, end)
        self.text.insert(start, cleaned)
        self._set_cursor_after_insert(start, cleaned, offset)
        self.text.see("insert")
        self._after_text_change()

    def _word_bounds(self) -> tuple:
        insert = self.text.index("insert")
        line = int(insert.split(".")[0])
        col = int(insert.split(".")[1])
        content = self.text.get(f"{line}.0", f"{line}.end")
        start = col
        while start > 0 and (content[start - 1].isalnum() or content[start - 1] == "_"):
            start -= 1
        end = col
        while end < len(content) and (content[end].isalnum() or content[end] == "_"):
            end += 1
        return f"{line}.{start}", f"{line}.{end}"

    def _set_cursor_after_insert(self, start_index: str, cleaned: str, offset: int | None) -> None:
        prefix = cleaned if offset is None else cleaned[:offset]
        lines = prefix.split("\n")
        target_line = int(start_index.split(".")[0]) + len(lines) - 1
        target_col = len(lines[-1])
        self.text.mark_set("insert", f"{target_line}.{target_col}")

    # ── Hover / go to definition ─────────────────────────────────────────

    def _on_control_motion(self, event: tk.Event) -> str | None:
        self._hide_tooltip()
        if not (event.state & 0x0004):
            return None
        if self._hover_after:
            self.after_cancel(self._hover_after)
        self._hover_after = self.after(300, lambda: self._show_hover(event.x, event.y))
        return "break"

    def _show_hover(self, x: int, y: int) -> None:
        self._hover_after = None
        index = self.text.index(f"@{x},{y}")
        line = int(index.split(".")[0])
        col = int(index.split(".")[1])
        info = self.controller.get_hover(line - 1, col, self.tab_id)
        if not info or not info.contents:
            return
        contents = info.contents[0] if info.contents else ""
        contents = contents.replace("**", "")
        top = tk.Toplevel(self)
        top.overrideredirect(True)
        label = tk.Label(
            top,
            text=contents,
            justify="left",
            padx=8,
            pady=6,
            bg=self.palette["tooltip.bg"],
            fg=self.palette["tooltip.fg"],
            font=self._font,
        )
        label.pack()
        top.geometry(f"+{self.text.winfo_rootx() + x + 12}+{self.text.winfo_rooty() + y + 12}")
        top.lift()
        self._tooltip = top

    def _hide_tooltip(self) -> None:
        if self._hover_after:
            self.after_cancel(self._hover_after)
            self._hover_after = None
        if self._tooltip is not None:
            try:
                self._tooltip.destroy()
            except tk.TclError:
                pass
            self._tooltip = None

    def _goto_definition(self, event: tk.Event | None = None) -> str:
        line, col = str(self.text.index("insert")).split(".")
        target = self.controller.go_to_definition(int(line) - 1, int(col), self.tab_id)
        if target:
            dest_line = target.start.line + 1
            self.text.mark_set("insert", f"{dest_line}.{target.start.column}")
            self.text.tag_add("goto.highlight", f"{dest_line}.0", f"{dest_line}.end")
            self.text.after(600, lambda: self.text.tag_remove("goto.highlight", "1.0", "end"))
            self.text.see(f"{dest_line}.0")
            self._update_current_line()
            self._sync_cursor()
        return "break"

    # ── Undo / redo ──────────────────────────────────────────────────────

    def _do_undo(self) -> str:
        content = self.controller.undo(self.tab_id)
        if content is not None:
            self.set_content(content)
        return "break"

    def _do_redo(self, event: tk.Event | None = None) -> str:
        content = self.controller.redo(self.tab_id)
        if content is not None:
            self.set_content(content)
        return "break"

    # ── Gutter ───────────────────────────────────────────────────────────

    def _on_gutter_click(self, event: tk.Event) -> str:
        index = self.text.index(f"@0,{event.y}")
        line = int(index.split(".")[0])
        self._toggle_breakpoint(line)
        return "break"

    def _toggle_breakpoint(self, line: int) -> None:
        tab = self.controller.get_active_tab()
        name = tab.file_path or tab.title
        if line in self._breakpoint_lines:
            self.controller.debugger.remove_breakpoint(name, line)
            self._breakpoint_lines.discard(line)
        else:
            self.controller.debugger.add_breakpoint(name, line)
            self._breakpoint_lines.add(line)
        self._redraw_gutter()
        if self.on_change is not None:
            self.on_change(self.tab_id, True)

    def _redraw_gutter(self) -> None:
        total_lines = int(self.text.index("end-1c").split(".")[0])
        width = 8 * len(str(total_lines)) + 16
        if width != self._gutter_width:
            self._gutter_width = width
            self.gutter.config(width=width)
        self.gutter.delete("all")
        first, last = self._visible_range()
        for line in range(first, last + 1):
            dline = self.text.dlineinfo(f"{line}.0")
            if dline is None:
                continue
            y = dline[1]
            if line in self._breakpoint_lines:
                self.gutter.create_oval(
                    width - 12, y + 3, width - 2, y + 13,
                    fill=self.palette["breakpoint"], outline=self.palette["breakpoint"],
                )
            self.gutter.create_text(
                width - 16, y + 2, anchor="ne", text=str(line),
                fill=self.palette["gutter.fg"],
            )

    def _scroll(self) -> None:
        self.text.after_idle(self._redraw_gutter)

    # ── Misc ─────────────────────────────────────────────────────────────

    def _on_click(self, event: tk.Event) -> None:
        self.completion.hide()
        self._hide_tooltip()

    def _on_click_release(self, event: tk.Event) -> None:
        self._update_current_line()
        self._sync_cursor()

    def apply_palette(self, palette: dict[str, str]) -> None:
        self.palette = palette
        self.text.config(
            bg=palette["bg"],
            fg=palette["fg"],
            insertbackground=palette["cursor"],
            selectbackground=palette["selection"],
        )
        self.gutter.config(bg=palette["gutter.bg"])
        self._setup_tags()
        self._refresh_diagnostics()
        self._redraw_gutter()

    def destroy(self) -> None:
        try:
            self.completion.top.destroy()
        except tk.TclError:
            pass
        self._hide_tooltip()
        super().destroy()


def _clean_snippet(text: str) -> tuple:
    match = re.search(r"\$\d+", text)
    offset = match.start() if match else None
    cleaned = re.sub(r"\$\d+", "", text)
    return cleaned, offset
