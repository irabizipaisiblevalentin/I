"""I STUDIO Desktop — bottom panel (Problems / Output / Run console)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any


class BottomPanel(ttk.Frame):
    def __init__(self, master: tk.Misc, controller: Any, palette: dict[str, str]):
        super().__init__(master)
        self.controller = controller
        self.palette = palette

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Problems
        self.problems = ttk.Frame(self.notebook)
        self.notebook.add(self.problems, text="Problems")
        self.problems_tree = ttk.Treeview(
            self.problems,
            columns=("severity", "location", "message"),
            show="headings",
        )
        self.problems_tree.heading("severity", text="Severity")
        self.problems_tree.heading("location", text="Location")
        self.problems_tree.heading("message", text="Message")
        self.problems_tree.column("severity", width=80, stretch=False)
        self.problems_tree.column("location", width=180, stretch=False)
        self.problems_tree.column("message", width=400)
        self.problems_tree.pack(side="left", fill="both", expand=True)
        problems_scroll = ttk.Scrollbar(self.problems, orient="vertical", command=self.problems_tree.yview)
        self.problems_tree.configure(yscrollcommand=problems_scroll.set)
        problems_scroll.pack(side="right", fill="y")

        # Output (compiler diagnostics)
        self.output = ttk.Frame(self.notebook)
        self.notebook.add(self.output, text="Output")
        self.output_text = tk.Text(
            self.output,
            height=8,
            wrap="none",
            state="disabled",
            bg=self.palette["panel.bg"],
            fg=self.palette["panel.fg"],
            relief="flat",
            borderwidth=0,
        )
        self.output_text.pack(side="left", fill="both", expand=True)
        output_scroll = ttk.Scrollbar(self.output, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_scroll.set)
        output_scroll.pack(side="right", fill="y")

        # Run console
        self.run = ttk.Frame(self.notebook)
        self.notebook.add(self.run, text="Run")
        self.run_text = tk.Text(
            self.run,
            height=8,
            wrap="none",
            state="disabled",
            bg=self.palette["panel.bg"],
            fg=self.palette["panel.fg"],
            relief="flat",
            borderwidth=0,
        )
        self.run_text.pack(side="left", fill="both", expand=True)
        run_scroll = ttk.Scrollbar(self.run, orient="vertical", command=self.run_text.yview)
        self.run_text.configure(yscrollcommand=run_scroll.set)
        run_scroll.pack(side="right", fill="y")

    # ── Problems ─────────────────────────────────────────────────────────

    def refresh_problems(self) -> None:
        self.problems_tree.delete(*self.problems_tree.get_children())
        count = 0
        for tab in self.controller.engine.get_tabs():
            name = tab.file_path or tab.title
            for d in self.controller.language.get_diagnostics(name):
                count += 1
                loc = f"{tab.title}:{d.range.start.line + 1}:{d.range.start.column + 1}"
                self.problems_tree.insert("", "end", values=(d.severity.value, loc, d.message))
        self.notebook.tab(self.problems, text=f"Problems ({count})")

    # ── Output / Run ─────────────────────────────────────────────────────

    def append_output(self, text: str) -> None:
        self._append(self.output_text, text)
        self.notebook.select(self.output)

    def append_run(self, text: str) -> None:
        self._append(self.run_text, text)
        self.notebook.select(self.run)

    def clear_run(self) -> None:
        self._clear(self.run_text)

    def _append(self, widget: tk.Text, text: str) -> None:
        widget.config(state="normal")
        widget.insert("end", text)
        widget.see("end")
        widget.config(state="disabled")

    def _clear(self, widget: tk.Text) -> None:
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.config(state="disabled")

    def apply_palette(self, palette: dict[str, str]) -> None:
        self.palette = palette
        for widget in (self.output_text, self.run_text):
            widget.config(bg=palette["panel.bg"], fg=palette["panel.fg"])
