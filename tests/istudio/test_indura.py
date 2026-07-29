"""Tests for istudio.indura — Editor Engine."""

from __future__ import annotations

import os
import tempfile

from src.istudio.indura import EditorEngine
from src.istudio.ibikoreshingiro import DocumentPosition, EditorConfig, EditorError


def test_editor_init():
    e = EditorEngine()
    assert e.config.font_size == 14
    assert e.get_tabs() == []


def test_editor_custom_config():
    cfg = EditorConfig(font_size=18, theme=None)
    e = EditorEngine(config=cfg)
    assert e.config.font_size == 18


def test_editor_update_config():
    e = EditorEngine()
    e.update_config(font_size=20, auto_save=False)
    assert e.config.font_size == 20
    assert e.config.auto_save is False


def test_editor_open_file():
    e = EditorEngine()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".i", delete=False, encoding="utf-8") as f:
        f.write("hello world")
        f.flush()
        tab = e.open_file(f.name)
        assert tab.title == os.path.basename(f.name)
        assert tab.language == "i"
        assert e.get_content() == "hello world"
        assert e.get_active_tab() is not None


def test_editor_open_nonexistent():
    e = EditorEngine()
    try:
        e.open_file("/nonexistent/file.i")
        assert False, "Should have raised"
    except EditorError:
        pass


def test_editor_close_file():
    e = EditorEngine()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".i", delete=False, encoding="utf-8") as f:
        f.write("test")
        f.flush()
        tab = e.open_file(f.name)
        assert e.close_file(tab.id) is True
        assert e.get_tabs() == []


def test_editor_set_content():
    e = EditorEngine()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".i", delete=False, encoding="utf-8") as f:
        f.write("original")
        f.flush()
        e.open_file(f.name)
        e.set_content("modified")
        assert e.get_content() == "modified"


def test_editor_insert_text():
    e = EditorEngine()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".i", delete=False, encoding="utf-8") as f:
        f.write("hello world")
        f.flush()
        e.open_file(f.name)
        e.insert_text(" beautiful", DocumentPosition(line=0, column=5))
        assert e.get_content() == "hello beautiful world"


def test_editor_delete_range():
    e = EditorEngine()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".i", delete=False, encoding="utf-8") as f:
        f.write("hello world")
        f.flush()
        e.open_file(f.name)
        e.delete_range(DocumentPosition(line=0, column=5), DocumentPosition(line=0, column=11))
        assert e.get_content() == "hello"


def test_editor_save_file():
    e = EditorEngine()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".i", delete=False, encoding="utf-8") as f:
        f.write("original")
        f_path = f.name
    try:
        tab = e.open_file(f_path)
        e.set_content("saved content")
        assert e.save_file() is True
        with open(f_path, "r", encoding="utf-8") as f:
            assert f.read() == "saved content"
    finally:
        os.unlink(f_path)


def test_editor_undo_redo():
    e = EditorEngine()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".i", delete=False, encoding="utf-8") as f:
        f.write("original")
        f.flush()
        e.open_file(f.name)
        e.set_content("version1")
        e.set_content("version2")
        assert e.undo() == "version1"
        assert e.undo() == "original"
        assert e.redo() == "version1"
        assert e.redo() == "version2"


def test_editor_find_text():
    e = EditorEngine()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".i", delete=False, encoding="utf-8") as f:
        f.write("hello hello world")
        f.flush()
        e.open_file(f.name)
        results = e.find_text("hello")
        assert len(results) == 2


def test_editor_replace_text():
    e = EditorEngine()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".i", delete=False, encoding="utf-8") as f:
        f.write("hello hello world")
        f.flush()
        e.open_file(f.name)
        count = e.replace_text("hello", "hi")
        assert count == 2
        assert e.get_content() == "hi hi world"


def test_editor_tab_activation():
    e = EditorEngine()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".a.i", delete=False, encoding="utf-8") as f1:
        f1.write("a")
        f1.flush()
        tab1 = e.open_file(f1.name)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".b.i", delete=False, encoding="utf-8") as f2:
        f2.write("b")
        f2.flush()
        tab2 = e.open_file(f2.name)
        assert e.get_active_tab().id == tab2.id
        e.set_active_tab(tab1.id)
        assert e.get_active_tab().id == tab1.id


def test_editor_cursor():
    e = EditorEngine()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".i", delete=False, encoding="utf-8") as f:
        f.write("test")
        f.flush()
        e.open_file(f.name)
        e.set_cursor_position(DocumentPosition(line=0, column=2))
        pos = e.get_cursor_position()
        assert pos.line == 0
        assert pos.column == 2


def test_editor_detect_file_type():
    assert EditorEngine.detect_file_type("main.i").value == "i"
    assert EditorEngine.detect_file_type("test.py").value == "py"
    assert EditorEngine.detect_file_type("styles.css").value == "css"
    assert EditorEngine.detect_file_type("unknown.xyz").value == "txt"


def test_editor_events():
    e = EditorEngine()
    events = []
    e.on("tab.opened", lambda d: events.append(("opened", d["tab"].id)))
    e.on("file.saved", lambda d: events.append(("saved", d["tab_id"])))
    with tempfile.NamedTemporaryFile(mode="w", suffix=".i", delete=False, encoding="utf-8") as f:
        f.write("test")
        f.flush()
        tab = e.open_file(f.name)
        assert len(events) >= 1


def test_editor_no_active_tab_errors():
    e = EditorEngine()
    try:
        e.get_content()
        assert False
    except EditorError:
        pass
    try:
        e.set_content("x")
        assert False
    except EditorError:
        pass
