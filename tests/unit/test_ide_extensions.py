"""Tests for the I Studio IDE extensions service."""

import os

from isoko.ideveloper.ibikoreshingiro import PackageRelease
from isoko.ideveloper.ububiko import PackageRegistry
from src.istudio.ide.extensions_api import ExtensionsService


class TestExtensionsService:
    def _setup(self, monkeypatch, tmp_path):
        os.environ["ISOKO_HOME"] = str(tmp_path / "isoko")
        os.environ["ISTUDIO_HOME"] = str(tmp_path / "istudio")
        monkeypatch.setenv("ISOKO_HOME", str(tmp_path / "isoko"))
        monkeypatch.setenv("ISTUDIO_HOME", str(tmp_path / "istudio"))
        PackageRegistry().publish(PackageRelease(
            name="demo-ext", version="1.0.0", description="Demo",
            author_name="A. Author"))
        return ExtensionsService()

    def test_list_empty(self, monkeypatch, tmp_path):
        svc = self._setup(monkeypatch, tmp_path)
        assert svc.list_installed() == []

    def test_install_and_list(self, monkeypatch, tmp_path):
        svc = self._setup(monkeypatch, tmp_path)
        manifest = svc.install("demo-ext")
        assert manifest is not None
        assert manifest["name"] == "demo-ext"
        assert manifest["version"] == "1.0.0"
        installed = svc.list_installed()
        assert len(installed) == 1
        assert installed[0]["name"] == "demo-ext"

    def test_browse_flags_installed(self, monkeypatch, tmp_path):
        svc = self._setup(monkeypatch, tmp_path)
        assert svc.browse("demo")[0]["installed"] is False
        svc.install("demo-ext")
        assert svc.browse("demo")[0]["installed"] is True

    def test_install_missing_package(self, monkeypatch, tmp_path):
        svc = self._setup(monkeypatch, tmp_path)
        assert svc.install("does-not-exist") is None

    def test_uninstall(self, monkeypatch, tmp_path):
        svc = self._setup(monkeypatch, tmp_path)
        svc.install("demo-ext")
        assert svc.uninstall("demo-ext") is True
        assert svc.list_installed() == []
        assert svc.uninstall("demo-ext") is False

    def test_install_name_traversal_guarded(self, monkeypatch, tmp_path):
        svc = self._setup(monkeypatch, tmp_path)
        assert svc.install("..") is None
        assert svc.install(".") is None

    def test_invalid_manifest_ignored(self, monkeypatch, tmp_path):
        svc = self._setup(monkeypatch, tmp_path)
        bad = os.path.join(os.environ["ISTUDIO_HOME"], "extensions", "broken")
        os.makedirs(bad)
        with open(os.path.join(bad, "extension.json"), "w") as f:
            f.write("not json")
        assert svc.list_installed() == []
