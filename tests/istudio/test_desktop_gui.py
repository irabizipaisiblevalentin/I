"""Tests for istudio.desktop widgets (tkinter, skipped without a display)."""

from __future__ import annotations

import re
import subprocess
import sys
import tkinter as tk
from pathlib import Path

import pytest

from src.istudio.desktop.controller import DesktopController
from src.istudio.desktop.editor import CodeEditor
from src.istudio.desktop.panel import BottomPanel
from src.istudio.desktop.sidebar import Sidebar
from src.istudio.desktop.theme import get_palette
from src.istudio.ibikoreshingiro import CompletionItem, CompletionKind, EditorTheme


@pytest.fixture(scope="module")
def root():
    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError:
        pytest.skip("no display available")
    yield root
    try:
        root.destroy()
    except tk.TclError:
        pass


@pytest.fixture
def editor(root):
    ctrl = DesktopController()
    tab_id = ctrl.get_active_tab().id
    ed = CodeEditor(root, ctrl, tab_id, get_palette(ctrl.current_theme()))
    yield ed, ctrl, tab_id
    ed.destroy()


def test_editor_highlights_keywords(editor):
    ed, ctrl, tab_id = editor
    ed.set_content("niba x == 1 {\n  subira yego\n}")
    ctrl.set_content(ed.get_content(), tab_id)
    ed._highlight_all()
    assert ed.text.tag_ranges("syntax.keyword")


def test_editor_highlights_strings_and_numbers(editor):
    ed, ctrl, tab_id = editor
    ed.set_content('andika "hello" 42')
    ctrl.set_content(ed.get_content(), tab_id)
    ed._highlight_all()
    assert ed.text.tag_ranges("syntax.string")
    assert ed.text.tag_ranges("syntax.number")


def test_editor_get_set_content(editor):
    ed, ctrl, tab_id = editor
    ed.set_content("let x = 1")
    assert ed.get_content() == "let x = 1"


def test_editor_gutter_redraw(editor):
    ed, ctrl, tab_id = editor
    ed.set_content("a\nb\nc\nd\ne")
    ed._redraw_gutter()
    assert ed.gutter.find_all()


def test_editor_current_line(editor):
    ed, ctrl, tab_id = editor
    ed.set_content("line one\nline two")
    ed.text.mark_set("insert", "2.0")
    ed._update_current_line()
    assert ed.text.tag_ranges("current.line")


def test_editor_breakpoint_toggle(editor):
    ed, ctrl, tab_id = editor
    ed.set_content("a\nb")
    ed._toggle_breakpoint(1)
    assert ed._breakpoint_lines == {1}
    assert ctrl.get_breakpoints()
    ed._toggle_breakpoint(1)
    assert not ed._breakpoint_lines
    assert not ctrl.get_breakpoints()


def test_editor_completion_inserts_snippet(editor):
    ed, ctrl, tab_id = editor
    ed.set_content("")
    ed.text.insert("1.0", "for_loop")
    ed.text.mark_set("insert", "1.8")
    item = CompletionItem(
        label="for_loop",
        kind=CompletionKind.SNIPPET,
        insert_text="for (let i = 0; i < $1; i++) {\n    $2\n}",
    )
    ed._insert_completion(item)
    cleaned = re.sub(r"\$\d+", "", item.insert_text)
    assert ed.get_content() == cleaned
    assert str(ed.text.index("insert")) == "1.20"


def test_editor_tab_inserts_spaces(editor):
    ed, ctrl, tab_id = editor
    ed.set_content("")
    ed.text.insert("1.0", "abc")
    ed.text.mark_set("insert", "1.3")
    result = ed._on_tab(None)
    assert result == "break"
    assert ed.get_content().endswith("    ")


def test_editor_apply_palette(editor):
    ed, ctrl, tab_id = editor
    ed.apply_palette(get_palette(EditorTheme.LIGHT))
    assert ed.text.cget("bg") == "#ffffff"


def test_sidebar_explorer(root, tmp_path):
    ctrl = DesktopController()
    ctrl.open_folder(str(tmp_path))
    (tmp_path / "a.i").write_text("andika 1", encoding="utf-8")
    sb = Sidebar(root, ctrl, get_palette(EditorTheme.DARK))
    sb.refresh_explorer()
    assert sb.explorer_tree.get_children()
    sb.destroy()


def test_bottom_panel_run_output(root):
    ctrl = DesktopController()
    panel = BottomPanel(root, ctrl, get_palette(EditorTheme.DARK))
    panel.append_run("hello")
    assert "hello" in panel.run_text.get("1.0", "end")
    panel.clear_run()
    assert panel.run_text.get("1.0", "end").strip() == ""
    panel.destroy()


def test_bottom_panel_problems(root):
    ctrl = DesktopController()
    tab_id = ctrl.get_active_tab().id
    ctrl.set_content('x = "unterminated', tab_id)
    panel = BottomPanel(root, ctrl, get_palette(EditorTheme.DARK))
    panel.refresh_problems()
    text = panel.notebook.tab(panel.problems, "text")
    assert text.startswith("Problems (")
    panel.destroy()


def test_app_smoke(tmp_path):
    try:
        probe = tk.Tk()
        probe.withdraw()
        probe.destroy()
    except tk.TclError:
        pytest.skip("no display available")
    src = str(Path(__file__).resolve().parents[2] / "src")
    tmp = str(tmp_path)
    code = f"""
import sys
sys.path.insert(0, {src!r})
from istudio.desktop.app import IStudioApp
from istudio.ibikoreshingiro import EditorTheme
app = IStudioApp(workspace_path={tmp!r})
app.update()
assert app._editors
app.set_theme(EditorTheme.LIGHT)
assert app.palette["bg"] == "#ffffff"
app.update()
app.destroy()
print("APP_SMOKE_OK")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        pytest.fail(f"app subprocess failed:\n{result.stdout}\n{result.stderr}")
    assert "APP_SMOKE_OK" in result.stdout
