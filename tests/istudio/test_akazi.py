"""Tests for istudio.akazi — Workspace & Project Manager."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from src.istudio.akazi import WorkspaceManager, ProjectManager
from src.istudio.ibikoreshingiro import ProjectConfig, ProjectType, PROJECT_TEMPLATES


def test_workspace_manager_init():
    ws = WorkspaceManager()
    assert ws.config.name == "untitled"
    assert ws.config.root_path == ""


def test_workspace_load_or_create():
    with tempfile.TemporaryDirectory() as tmp:
        ws = WorkspaceManager(tmp)
        cfg = ws.load_or_create(tmp)
        assert cfg.root_path == str(Path(tmp).resolve())
        assert os.path.exists(os.path.join(tmp, ".istudio-workspace"))


def test_workspace_load_existing():
    with tempfile.TemporaryDirectory() as tmp:
        ws = WorkspaceManager()
        ws.load_or_create(tmp)
        ws2 = WorkspaceManager()
        cfg = ws2.load_or_create(tmp)
        assert cfg.name == os.path.basename(tmp)


def test_workspace_add_remove_project():
    with tempfile.TemporaryDirectory() as tmp:
        ws = WorkspaceManager(tmp)
        ws.add_project("/fake/project")
        assert "/fake/project" in ws.config.projects
        ws.remove_project("/fake/project")
        assert "/fake/project" not in ws.config.projects


def test_workspace_settings():
    ws = WorkspaceManager()
    ws.update_setting("editor.fontSize", 16)
    assert ws.get_setting("editor.fontSize") == 16
    assert ws.get_setting("nonexistent", "default") == "default"


def test_workspace_extensions():
    ws = WorkspaceManager()
    ws.install_extension("test-ext")
    assert "test-ext" in ws.list_extensions()
    ws.uninstall_extension("test-ext")
    assert "test-ext" not in ws.list_extensions()


def test_workspace_get_root():
    with tempfile.TemporaryDirectory() as tmp:
        ws = WorkspaceManager(tmp)
        assert ws.get_root_path() == str(Path(tmp).resolve())


def test_project_manager_create():
    pm = ProjectManager()
    with tempfile.TemporaryDirectory() as tmp:
        cfg = pm.create_project("testproj", tmp)
        assert cfg.name == "testproj"
        assert os.path.exists(os.path.join(tmp, "testproj", "project.json"))


def test_project_manager_load():
    pm = ProjectManager()
    with tempfile.TemporaryDirectory() as tmp:
        pm.create_project("testproj", tmp)
        cfg = pm.load_project(os.path.join(tmp, "testproj"))
        assert cfg.name == "testproj"


def test_project_manager_get():
    pm = ProjectManager()
    with tempfile.TemporaryDirectory() as tmp:
        pm.create_project("testproj", tmp)
        cfg = pm.get_project("testproj")
        assert cfg is not None
        assert cfg.name == "testproj"
        assert pm.get_project("nonexistent") is None


def test_project_manager_list():
    pm = ProjectManager()
    with tempfile.TemporaryDirectory() as tmp:
        pm.create_project("a", tmp)
        pm.create_project("b", tmp)
        assert len(pm.list_projects()) == 2


def test_project_manager_remove():
    pm = ProjectManager()
    with tempfile.TemporaryDirectory() as tmp:
        pm.create_project("testproj", tmp)
        assert pm.remove_project("testproj") is True
        assert pm.remove_project("nonexistent") is False


def test_project_config_creation():
    cfg = ProjectConfig(name="custom", version="2.0.0", type="library")
    assert cfg.name == "custom"
    assert cfg.dependencies == {}


def test_workspace_integration():
    with tempfile.TemporaryDirectory() as tmp:
        ws = WorkspaceManager(tmp)
        pm = ws.project_manager
        p = os.path.join(tmp, "subproj")
        cfg = pm.create_project("subproj", tmp)
        assert cfg.name in [c.name for c in pm.list_projects()]


def test_project_create_with_type():
    pm = ProjectManager()
    with tempfile.TemporaryDirectory() as tmp:
        cfg = pm.create_project("webapp", tmp, ProjectType.WEBSITE)
        assert cfg.project_type == ProjectType.WEBSITE
        assert cfg.entry_point == "src/main.i"
        proj_dir = os.path.join(tmp, "webapp")
        assert os.path.exists(os.path.join(proj_dir, "src", "components"))
        assert os.path.exists(os.path.join(proj_dir, "public", "index.html"))


def test_project_type_creates_dirs_and_files():
    pm = ProjectManager()
    with tempfile.TemporaryDirectory() as tmp:
        for pt, template in PROJECT_TEMPLATES.items():
            proj_name = f"test_{pt.value}"
            cfg = pm.create_project(proj_name, tmp, pt)
            proj_dir = os.path.join(tmp, proj_name)
            for d in template.initial_dirs:
                assert os.path.isdir(os.path.join(proj_dir, d)), f"Missing dir {d} for {pt.value}"
            for fname in template.initial_files:
                assert os.path.isfile(os.path.join(proj_dir, fname)), f"Missing file {fname} for {pt.value}"


def test_project_type_roundtrip():
    pm = ProjectManager()
    with tempfile.TemporaryDirectory() as tmp:
        cfg = pm.create_project("gameproj", tmp, ProjectType.GAME)
        cfg2 = pm.load_project(os.path.join(tmp, "gameproj"))
        assert cfg2.project_type == ProjectType.GAME


def test_workspace_save_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        ws = WorkspaceManager(tmp)
        ws.update_setting("theme", "dark")
        ws.install_extension("ext1")
        ws.add_project("/p1")
        ws2 = WorkspaceManager()
        ws2.load_or_create(tmp)
        assert ws2.get_setting("theme") == "dark"
        assert "ext1" in ws2.list_extensions()
        assert "/p1" in ws2.config.projects
