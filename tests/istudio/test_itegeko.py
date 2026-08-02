"""Tests for istudio.itegeko — CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile

from src.istudio.itegeko import (
    cmd_workspace,
    cmd_project,
    cmd_lint,
    cmd_format,
    cmd_debug,
    cmd_profile,
    cmd_ai,
    cmd_extension,
    cmd_collaboration,
    cmd_server,
    cmd_desktop,
    register_subcommands,
    genda,
)


def _make_args(command: str, **kwargs) -> argparse.Namespace:
    ns = argparse.Namespace()
    ns.command = command
    for k, v in kwargs.items():
        setattr(ns, k, v)
    return ns


def test_register_subcommands():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    register_subcommands(subparsers)
    args = parser.parse_args(["istudio", "workspace", "info"])
    assert args.command == "istudio"
    assert args.istudio_command == "workspace"


def test_genda_no_command():
    args = _make_args("istudio")
    assert genda(args) == 1


def test_genda_unknown():
    args = _make_args("istudio")
    args.istudio_command = "nonexistent"
    assert genda(args) == 1


def test_genda_workspace_init():
    with tempfile.TemporaryDirectory() as tmp:
        args = _make_args("istudio", action="init", path=tmp, istudio_command="workspace")
        assert cmd_workspace(args) == 0


def test_genda_workspace_info():
    with tempfile.TemporaryDirectory() as tmp:
        args = _make_args("istudio", action="init", path=tmp, istudio_command="workspace")
        cmd_workspace(args)
        args2 = _make_args("istudio", action="info", path=tmp, istudio_command="workspace")
        assert cmd_workspace(args2) == 0


def test_cmd_project_create():
    with tempfile.TemporaryDirectory() as tmp:
        args = _make_args("istudio", action="create", name="testproj", path=tmp, type="library", istudio_command="project")
        # Need workspace first
        ws_args = _make_args("istudio", action="init", path=tmp, istudio_command="workspace")
        cmd_workspace(ws_args)
        assert cmd_project(args) == 0


def test_cmd_project_list():
    args = _make_args("istudio", action="list", name=None, path=".", type="library", istudio_command="project")
    assert cmd_project(args) == 0


def test_cmd_project_info():
    args = _make_args("istudio", action="info", name="nonexistent", path=".", type="library", istudio_command="project")
    assert cmd_project(args) == 0


def test_cmd_project_create_with_type():
    with tempfile.TemporaryDirectory() as tmp:
        for pt in ["website", "desktop_app", "game", "cloud_service", "library"]:
            args = _make_args("istudio", action="create", name=f"proj_{pt}", path=tmp, type=pt, istudio_command="project")
            ws_args = _make_args("istudio", action="init", path=tmp, istudio_command="workspace")
            cmd_workspace(ws_args)
            assert cmd_project(args) == 0
            proj_dir = os.path.join(tmp, f"proj_{pt}")
            assert os.path.exists(os.path.join(proj_dir, "project.json"))


def _write_temp_file(suffix: str, content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8")
    f.write(content)
    fname = f.name
    f.close()
    return fname


def test_cmd_lint():
    fname = _write_temp_file(".i", "undefined variable")
    try:
        args = _make_args("istudio", file=fname, format="text", istudio_command="lint")
        code = cmd_lint(args)
        assert code == 1
    finally:
        os.unlink(fname)


def test_cmd_lint_clean():
    fname = _write_temp_file(".i", "function main() {}")
    try:
        args = _make_args("istudio", file=fname, format="text", istudio_command="lint")
        code = cmd_lint(args)
        assert code == 0
    finally:
        os.unlink(fname)


def test_cmd_lint_json():
    fname = _write_temp_file(".i", "undefined")
    try:
        args = _make_args("istudio", file=fname, format="json", istudio_command="lint")
        assert cmd_lint(args) == 1
    finally:
        os.unlink(fname)


def test_cmd_lint_not_found():
    args = _make_args("istudio", file="/nonexistent/file.i", format="text", istudio_command="lint")
    assert cmd_lint(args) == 1


def test_cmd_format():
    fname = _write_temp_file(".i", "function foo() {\nlet x = 1\n}")
    try:
        args = _make_args("istudio", file=fname, istudio_command="format")
        assert cmd_format(args) == 0
        with open(fname, "r", encoding="utf-8") as fr:
            content = fr.read()
            assert "    " in content
    finally:
        os.unlink(fname)


def test_cmd_format_not_found():
    args = _make_args("istudio", file="nonexistent.i", istudio_command="format")
    assert cmd_format(args) == 1


def test_cmd_debug_start():
    args = _make_args("istudio", action="start", istudio_command="debug")
    assert cmd_debug(args) == 0


def test_cmd_debug_stop():
    args = _make_args("istudio", action="stop", istudio_command="debug")
    assert cmd_debug(args) == 0


def test_cmd_debug_step():
    args = _make_args("istudio", action="step", istudio_command="debug")
    assert cmd_debug(args) == 0


def test_cmd_debug_continue():
    args = _make_args("istudio", action="continue", istudio_command="debug")
    assert cmd_debug(args) == 0


def test_cmd_debug_break():
    args = _make_args("istudio", action="break", istudio_command="debug")
    assert cmd_debug(args) == 0


def test_cmd_debug_break_list():
    args = _make_args("istudio", action="break-list", istudio_command="debug")
    assert cmd_debug(args) == 0


def test_cmd_profile():
    args = _make_args("istudio", action="start", type="cpu", name="test", istudio_command="profile")
    assert cmd_profile(args) == 0


def test_cmd_profile_stop():
    args_start = _make_args("istudio", action="start", type="cpu", name="test", istudio_command="profile")
    cmd_profile(args_start)
    args_stop = _make_args("istudio", action="stop", type="cpu", name="", istudio_command="profile")
    assert cmd_profile(args_stop) == 0


def test_cmd_profile_list():
    args = _make_args("istudio", action="list", type="cpu", name="", istudio_command="profile")
    assert cmd_profile(args) == 0


def test_cmd_profile_results():
    args = _make_args("istudio", action="results", type="cpu", name="", istudio_command="profile")
    assert cmd_profile(args) == 0


def test_cmd_ai_chat():
    args = _make_args("istudio", action="chat", message="Hello", istudio_command="ai")
    assert cmd_ai(args) == 0


def test_cmd_ai_empty():
    args = _make_args("istudio", action="chat", message="", istudio_command="ai")
    assert cmd_ai(args) == 0


def test_cmd_ai_conversations():
    args = _make_args("istudio", action="conversations", message="", istudio_command="ai")
    assert cmd_ai(args) == 0


def test_cmd_extension_install_no_path():
    args = _make_args("istudio", action="install", id=None, path=None, istudio_command="extension")
    assert cmd_extension(args) == 0


def test_cmd_extension_list():
    args = _make_args("istudio", action="list", id=None, path=None, istudio_command="extension")
    assert cmd_extension(args) == 0


def test_cmd_collaboration():
    args = _make_args("istudio", action="session-create", id="test-session", istudio_command="collaboration")
    assert cmd_collaboration(args) == 0


def test_cmd_collaboration_list():
    args = _make_args("istudio", action="session-list", id="", istudio_command="collaboration")
    assert cmd_collaboration(args) == 0


def test_cmd_collaboration_users():
    args = _make_args("istudio", action="user-list", id="", istudio_command="collaboration")
    assert cmd_collaboration(args) == 0


def test_cmd_collaboration_review():
    args = _make_args("istudio", action="review-create", id="PR-1", istudio_command="collaboration")
    assert cmd_collaboration(args) == 0


def test_cmd_collaboration_review_list():
    args = _make_args("istudio", action="review-list", id="", istudio_command="collaboration")
    assert cmd_collaboration(args) == 0


def test_cmd_lint_bridge_defaults():
    fname = _write_temp_file(".i", "undefined variable")
    try:
        args = _make_args("istudio", file=fname, istudio_command="lint")
        assert cmd_lint(args) == 1
    finally:
        os.unlink(fname)


def test_cmd_profile_bridge_defaults():
    args = _make_args("istudio", action="start", type="cpu", istudio_command="profile")
    assert cmd_profile(args) == 0


def test_cmd_extension_bridge_defaults():
    args = _make_args("istudio", action="install", id=None, istudio_command="extension")
    assert cmd_extension(args) == 0


def test_genda_lint_clean():
    fname = _write_temp_file(".i", "function main() {}")
    try:
        args = _make_args("istudio", file=fname, istudio_command="lint")
        assert genda(args) == 0
    finally:
        os.unlink(fname)


def test_register_desktop_subcommand():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    register_subcommands(subparsers)
    args = parser.parse_args(["istudio", "desktop"])
    assert args.istudio_command == "desktop"
    args2 = parser.parse_args(["istudio", "desktop", "some/folder"])
    assert args2.path == "some/folder"


def test_cmd_desktop_requires_display(monkeypatch):
    monkeypatch.setattr("src.istudio.desktop.is_available", lambda: False)
    args = _make_args("istudio", path=None, istudio_command="desktop")
    assert cmd_desktop(args) == 1


def test_cmd_desktop_launches(monkeypatch):
    calls = {}
    monkeypatch.setattr("src.istudio.desktop.is_available", lambda: True)

    def fake_main(argv):
        calls["argv"] = argv
        return 0

    monkeypatch.setattr("src.istudio.desktop.main", fake_main)
    args = _make_args("istudio", path=".", istudio_command="desktop")
    assert cmd_desktop(args) == 0
    assert calls["argv"] == ["."]


def test_cmd_desktop_no_path(monkeypatch):
    calls = {}
    monkeypatch.setattr("src.istudio.desktop.is_available", lambda: True)

    def fake_main(argv):
        calls["argv"] = argv
        return 0

    monkeypatch.setattr("src.istudio.desktop.main", fake_main)
    args = _make_args("istudio", path=None, istudio_command="desktop")
    assert cmd_desktop(args) == 0
    assert calls["argv"] == []
