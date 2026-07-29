"""Tests for isoko.ideveloper.inyandiko — Documentation Platform."""

from __future__ import annotations

from isoko.ideveloper.inyandiko import DocumentationPlatform


def test_docs_init():
    dp = DocumentationPlatform()
    assert dp.get_versions() == ["0.1.0"]
    assert dp.get_guides() == []


def test_set_and_get_document():
    dp = DocumentationPlatform()
    dp.set_document("/intro", "# Welcome to I")
    assert dp.get_document("/intro") == "# Welcome to I"


def test_versioned_docs():
    dp = DocumentationPlatform()
    dp.add_version("0.2.0")
    dp.set_document("/api/core", "Core API docs", "0.2.0")
    assert dp.get_document("/api/core", "0.2.0") == "Core API docs"
    assert dp.get_document("/api/core", "0.1.0") is None


def test_search():
    dp = DocumentationPlatform()
    dp.set_document("/guide/getting-started", "Install I and start coding")
    results = dp.search("install")
    assert "/guide/getting-started" in results


def test_add_guide():
    dp = DocumentationPlatform()
    guide = dp.add_guide("Getting Started", "How to start with I", "beginners")
    assert guide["title"] == "Getting Started"
    assert len(dp.get_guides("beginners")) == 1


def test_add_tutorial():
    dp = DocumentationPlatform()
    tutorial = dp.add_tutorial("Build a Web App", ["Create project", "Add routes", "Deploy"], "intermediate")
    assert len(tutorial["steps"]) == 3
    assert len(dp.get_tutorials("intermediate")) == 1


def test_translations():
    dp = DocumentationPlatform()
    dp.set_translation("fr", "/intro", "Bienvenue sur I")
    assert dp.get_translation("fr", "/intro") == "Bienvenue sur I"


def test_offline_packs():
    dp = DocumentationPlatform()
    pack_id = dp.add_offline_pack("0.1.0")
    assert pack_id.startswith("offline_")
    assert len(dp.get_offline_packs()) == 1


def test_api_reference():
    dp = DocumentationPlatform()
    dp.set_document("/api/print", "print function docs")
    result = dp.get_api_reference("print")
    assert result is not None
    assert result["symbol"] == "print"


def test_multiple_versions():
    dp = DocumentationPlatform()
    dp.add_version("0.3.0")
    assert "0.3.0" in dp.get_versions()
