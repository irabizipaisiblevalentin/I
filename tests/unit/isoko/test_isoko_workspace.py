"""Tests for isoko workspace module."""

import json
import os
import tempfile

import pytest
from isoko.workspace import Workspace, WorkspaceConfig, WorkspacePackage


class TestWorkspace:
    def test_init(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Workspace(tmpdir)
            assert ws.root == os.path.abspath(tmpdir)

    def test_not_workspace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Workspace(tmpdir)
            assert not ws.is_workspace()

    def test_is_workspace(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws_path = os.path.join(tmpdir, "ilang-workspace.json")
            with open(ws_path, "w") as f:
                json.dump({"members": ["packages/*"]}, f)
            ws = Workspace(tmpdir)
            assert ws.is_workspace()

    def test_save_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Workspace(tmpdir)
            ws.config.members = ["packages/*", "tools/*"]
            ws.config.exclude = ["node_modules"]
            ws.config.shared_deps = {"dep1": "^1.0.0"}
            ws.save()

            ws2 = Workspace(tmpdir)
            ws2.load()
            assert ws2.config.members == ["packages/*", "tools/*"]
            assert ws2.config.exclude == ["node_modules"]
            assert ws2.config.shared_deps["dep1"] == "^1.0.0"

    def test_discover_packages(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create workspace config
            ws_path = os.path.join(tmpdir, "ilang-workspace.json")
            with open(ws_path, "w") as f:
                json.dump({"members": ["packages/*"]}, f)

            # Create a package
            pkg_dir = os.path.join(tmpdir, "packages", "my-pkg")
            os.makedirs(pkg_dir)
            manifest = os.path.join(pkg_dir, "ilang.json")
            with open(manifest, "w") as f:
                json.dump({
                    "package": {"name": "my-pkg", "version": "1.0.0"},
                }, f)

            ws = Workspace(tmpdir)
            ws.load()
            assert "my-pkg" in ws.packages

    def test_load_not_found(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws = Workspace(tmpdir)
            with pytest.raises(FileNotFoundError):
                ws.load()

    def test_get_package(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ws_path = os.path.join(tmpdir, "ilang-workspace.json")
            with open(ws_path, "w") as f:
                json.dump({"members": ["packages/*"]}, f)

            pkg_dir = os.path.join(tmpdir, "packages", "test-pkg")
            os.makedirs(pkg_dir)
            with open(os.path.join(pkg_dir, "ilang.json"), "w") as f:
                json.dump({"package": {"name": "test-pkg", "version": "1.0.0"}}, f)

            ws = Workspace(tmpdir)
            ws.load()
            pkg = ws.get_package("test-pkg")
            assert pkg is not None
            assert pkg.name == "test-pkg"

            assert ws.get_package("nonexistent") is None


class TestWorkspaceConfig:
    def test_defaults(self):
        wc = WorkspaceConfig("/tmp")
        assert wc.root == "/tmp"
        assert wc.members == []
        assert wc.exclude == []


class TestWorkspacePackage:
    def test_defaults(self):
        wp = WorkspacePackage()
        assert wp.name == ""
        assert wp.path == ""
        assert wp.manifest is None
