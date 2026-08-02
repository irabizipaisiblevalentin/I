"""Tests for istudio.ide.projects — project service and path security."""

from __future__ import annotations

import os

import pytest

from src.istudio.ide import templates
from src.istudio.ide.projects import ProjectError, ProjectService
from src.istudio.ide.util import safe_join


@pytest.fixture
def service(temp_dir: str) -> ProjectService:
    return ProjectService(os.path.join(temp_dir, "workspace"), state_path=os.path.join(temp_dir, "state.json"))


def test_create_project(service: ProjectService) -> None:
    result = service.create("myapp", "console")
    assert result["path"]
    assert os.path.isfile(os.path.join(result["path"], "ilang.toml"))
    assert os.path.isfile(os.path.join(result["path"], "src", "main.i"))


def test_create_invalid_name(service: ProjectService) -> None:
    with pytest.raises(ProjectError):
        service.create("has space!", "console")


def test_create_duplicate(service: ProjectService) -> None:
    service.create("dup", "console")
    with pytest.raises(ProjectError):
        service.create("dup", "console")


def test_list_projects(service: ProjectService) -> None:
    one = service.create("one", "console")
    two = service.create("two", "web")
    paths = {p["path"] for p in service.list_projects()}
    assert {one["path"], two["path"]} <= paths


def test_open_project_and_recent(service: ProjectService) -> None:
    created = service.create("recent-app", "console")
    assert created["path"] in service.recent()
    info = service.open_project(created["path"])
    assert info["path"] == created["path"]
    assert os.path.basename(info["path"]) == "recent-app"


def test_open_plain_folder_works(service: ProjectService, temp_dir: str) -> None:
    plain = os.path.join(temp_dir, "plain")
    os.makedirs(plain, exist_ok=True)
    info = service.open_project(plain)
    assert info["path"] == plain
    assert info["template"] == "custom"


def test_current_returns_most_recent(service: ProjectService) -> None:
    assert service.current() is None
    created = service.create("current-app", "console")
    current = service.current()
    assert current is not None
    assert current["path"] == created["path"]


def test_write_read_roundtrip(service: ProjectService) -> None:
    root = service.create("files", "console")["path"]
    service.write_file(root, "src/notes.txt", "hello\n")
    assert service.read_file(root, "src/notes.txt") == "hello\n"


def test_file_tree(service: ProjectService) -> None:
    root = service.create("tree", "console")["path"]
    names = {node["name"] for node in service.file_tree(root)}
    assert {"src", "ilang.toml"} <= names


def test_delete_and_rename(service: ProjectService) -> None:
    root = service.create("mut", "console")["path"]
    service.write_file(root, "tmp.txt", "x")
    service.rename_path(root, "tmp.txt", "renamed.txt")
    assert os.path.isfile(os.path.join(root, "renamed.txt"))
    service.delete_path(root, "renamed.txt")
    assert not os.path.exists(os.path.join(root, "renamed.txt"))


def test_traversal_rejected(service: ProjectService) -> None:
    root = service.create("sec", "console")["path"]
    with pytest.raises(ProjectError):
        service.read_file(root, "../outside.i")
    with pytest.raises(ProjectError):
        service.write_file(root, "../../evil.py", "x")
    with pytest.raises(ProjectError):
        service.delete_path(root, "..")


def test_delete_root_rejected(service: ProjectService) -> None:
    root = service.create("root", "console")["path"]
    with pytest.raises(ProjectError):
        service.delete_path(root, "")


def test_safe_join() -> None:
    base = r"C:\work\proj"
    assert safe_join(base, "src", "main.i")
    assert safe_join(base, "..") is None
    assert safe_join(base, "..\\..\\etc\\passwd") is None


def test_all_templates_metadata(service: ProjectService) -> None:
    for key in templates.template_keys():
        meta = templates.get_template(key)
        assert meta["name"]
        assert "ilang.toml" in meta["files"]


def test_create_from_upload(service: ProjectService) -> None:
    result = service.create_from_upload("uploaded", {"main.i": "andika 1\n", "lib/util.i": "andika 2\n"})
    assert result["template"] == "imported"
    assert os.path.isfile(os.path.join(result["path"], "main.i"))
    assert os.path.isfile(os.path.join(result["path"], "lib", "util.i"))
    assert not os.path.isfile(os.path.join(result["path"], "ilang.toml"))


def test_create_from_upload_rejects_bad_name(service: ProjectService) -> None:
    with pytest.raises(ProjectError):
        service.create_from_upload("has space!", {"a.i": "x"})


def test_replace_with_removes_template_files(service: ProjectService) -> None:
    root = service.create("repl", "console")["path"]
    assert os.path.isfile(os.path.join(root, "ilang.toml"))
    written = service.replace_with(root, {"app.i": "andika 1\n"})
    assert written == ["app.i"]
    assert not os.path.isfile(os.path.join(root, "ilang.toml"))
    assert not os.path.exists(os.path.join(root, "src"))
    assert os.path.isfile(os.path.join(root, "app.i"))


def test_replace_with_rejects_traversal(service: ProjectService) -> None:
    root = service.create("repl-sec", "console")["path"]
    with pytest.raises(ProjectError):
        service.replace_with(root, {"../evil.py": "x"})


def _make_src_folder(temp_dir: str, name: str) -> str:
    src = os.path.join(temp_dir, name)
    os.makedirs(os.path.join(src, "lib", "sub"), exist_ok=True)
    with open(os.path.join(src, "main.i"), "w", encoding="utf-8") as f:
        f.write("andika 1\n")
    with open(os.path.join(src, "lib", "util.i"), "w", encoding="utf-8") as f:
        f.write("andika 2\n")
    with open(os.path.join(src, "lib", "sub", "deep.i"), "w", encoding="utf-8") as f:
        f.write("andika 3\n")
    return src


def test_create_from_folder_keeps_structure(service: ProjectService, temp_dir: str) -> None:
    src = _make_src_folder(temp_dir, "my-src")
    result = service.create_from_folder("imported", src)
    assert result["template"] == "imported"
    assert os.path.isfile(os.path.join(result["path"], "main.i"))
    assert os.path.isfile(os.path.join(result["path"], "lib", "util.i"))
    assert os.path.isfile(os.path.join(result["path"], "lib", "sub", "deep.i"))
    assert not os.path.isfile(os.path.join(result["path"], "ilang.toml"))


def test_create_from_folder_rejects_missing_source(service: ProjectService) -> None:
    with pytest.raises(ProjectError):
        service.create_from_folder("bad", "C:/does/not/exist")


def test_replace_from_folder_removes_templates(service: ProjectService, temp_dir: str) -> None:
    root = service.create("repl-folder", "console")["path"]
    src = _make_src_folder(temp_dir, "src-folder")
    written = service.replace_from_folder(root, src)
    assert {"main.i", "lib/util.i", "lib/sub/deep.i"} <= set(written)
    assert not os.path.isfile(os.path.join(root, "ilang.toml"))
    assert not os.path.exists(os.path.join(root, "src"))
    assert os.path.isfile(os.path.join(root, "lib", "sub", "deep.i"))


def test_replace_from_folder_same_source_rejected(service: ProjectService) -> None:
    root = service.create("same", "console")["path"]
    with pytest.raises(ProjectError):
        service.replace_from_folder(root, root)
