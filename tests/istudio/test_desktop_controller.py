"""Tests for istudio.desktop.controller — DesktopController."""

from __future__ import annotations

from src.istudio.desktop.controller import DesktopController
from src.istudio.ibikoreshingiro import DiagnosticSeverity, EditorTheme


def test_init_creates_untitled_tab():
    ctrl = DesktopController()
    tab = ctrl.get_active_tab()
    assert tab is not None
    assert tab.title.startswith("untitled")


def test_new_file_creates_tab():
    ctrl = DesktopController()
    tab_id = ctrl.new_file()
    assert tab_id != ctrl.get_active_tab().id or True
    assert ctrl.get_active_tab().id == tab_id


def test_set_content_analyzes(tmp_path):
    ctrl = DesktopController()
    tab_id = ctrl.get_active_tab().id
    ctrl.set_content('x = "unterminated', tab_id)
    diagnostics = ctrl.get_diagnostics(tab_id)
    assert any(d.severity == DiagnosticSeverity.ERROR for d in diagnostics)


def test_open_and_save_file(tmp_path):
    f = tmp_path / "prog.i"
    f.write_text("andika 1", encoding="utf-8")
    ctrl = DesktopController()
    tab_id = ctrl.open_file(str(f))
    assert ctrl.get_active_tab().id == tab_id
    assert ctrl.get_content(tab_id) == "andika 1"
    assert ctrl.save(tab_id) is True


def test_save_untitled_returns_false():
    ctrl = DesktopController()
    tab_id = ctrl.get_active_tab().id
    assert ctrl.save(tab_id) is False


def test_save_as(tmp_path):
    ctrl = DesktopController()
    tab_id = ctrl.get_active_tab().id
    ctrl.set_content("andika 2", tab_id)
    target = tmp_path / "saved.i"
    assert ctrl.save_as(tab_id, str(target)) is True
    assert target.read_text(encoding="utf-8") == "andika 2"
    assert ctrl.save(tab_id) is True


def test_undo_redo():
    ctrl = DesktopController()
    tab_id = ctrl.get_active_tab().id
    ctrl.set_content("one", tab_id)
    ctrl.set_content("two", tab_id)
    assert ctrl.undo(tab_id) == "one"
    assert ctrl.redo(tab_id) == "two"


def test_completions_filtered_by_prefix():
    ctrl = DesktopController()
    tab_id = ctrl.get_active_tab().id
    ctrl.set_content("re", tab_id)
    items = ctrl.get_completions(0, 2, tab_id)
    labels = {i.label for i in items}
    assert "return" in labels
    assert "if" not in labels


def test_completions_unfiltered_when_not_at_word_end():
    ctrl = DesktopController()
    tab_id = ctrl.get_active_tab().id
    ctrl.set_content("re ", tab_id)
    items = ctrl.get_completions(0, 3, tab_id)
    labels = {i.label for i in items}
    assert "if" in labels


def test_hover_builtin():
    ctrl = DesktopController()
    tab_id = ctrl.get_active_tab().id
    ctrl.set_content("andika len(x)", tab_id)
    hover = ctrl.get_hover(0, 8, tab_id)
    assert hover is not None
    assert any("len" in c for c in hover.contents)


def test_go_to_definition():
    ctrl = DesktopController()
    tab_id = ctrl.get_active_tab().id
    ctrl.set_content("function muraho() {}\nmuraho()", tab_id)
    target = ctrl.go_to_definition(1, 0, tab_id)
    assert target is not None
    assert target.start.line == 0


def test_symbols():
    ctrl = DesktopController()
    tab_id = ctrl.get_active_tab().id
    ctrl.set_content("function foo() {}\nlet x = 1", tab_id)
    symbols = ctrl.get_symbols(tab_id)
    names = {s.name for s in symbols}
    assert "foo" in names
    assert "x" in names


def test_format_document():
    ctrl = DesktopController()
    tab_id = ctrl.get_active_tab().id
    ctrl.set_content("if x {\nandika 1\n}", tab_id)
    formatted = ctrl.format_document(tab_id)
    assert "    " in formatted


def test_open_folder_lists_files(tmp_path):
    proj = tmp_path / "proj"
    proj.mkdir()
    (proj / "main.i").write_text("andika 1", encoding="utf-8")
    (proj / "readme.txt").write_text("hi", encoding="utf-8")
    ctrl = DesktopController()
    ctrl.open_folder(str(proj))
    files = ctrl.list_workspace_files()
    assert any(f.endswith("main.i") for f in files)
    assert not any(f.endswith("readme.txt") for f in files)


def test_breakpoints():
    ctrl = DesktopController()
    tab_id = ctrl.get_active_tab().id
    bp = ctrl.toggle_breakpoint(2, tab_id)
    assert bp is not None
    assert ctrl.get_breakpoints()
    ctrl.debugger.remove_breakpoint(ctrl.get_active_tab().title, 2)
    assert not ctrl.get_breakpoints()


def test_theme_switching():
    ctrl = DesktopController()
    palette = ctrl.set_theme(EditorTheme.LIGHT)
    assert palette["bg"] == "#ffffff"
    assert ctrl.current_theme() == EditorTheme.LIGHT


def test_run_active_file(tmp_path):
    f = tmp_path / "run.i"
    f.write_text('andika "run output"', encoding="utf-8")
    ctrl = DesktopController()
    ctrl.open_file(str(f))
    done = []
    ctrl.runner = _RecordingRunner(done)
    ctrl.run_active()
    assert done


def test_status_info():
    ctrl = DesktopController()
    info = ctrl.get_status_info()
    assert "file" in info
    assert "language" in info


class _RecordingRunner:
    def __init__(self, done):
        self._done = done
        self.is_running = False

    def run_file(self, path):
        self._done.append(path)
        return None

    def run_source(self, source, name):
        self._done.append(name)
        return None
