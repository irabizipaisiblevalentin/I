"""Tests for isoko.ideveloper.ububiko — Package Registry."""

from __future__ import annotations

from isoko.ideveloper.ububiko import PackageRegistry
from isoko.ideveloper.ibikoreshingiro import PackageRelease, PackageVisibility


def test_registry_init():
    reg = PackageRegistry()
    assert reg.list_packages() == []


def test_publish_package():
    reg = PackageRegistry()
    release = PackageRelease(name="test-pkg", version="1.0.0", description="A test package", author_name="Alice")
    pkg_id = reg.publish(release)
    assert pkg_id == "test-pkg@1.0.0"
    assert reg.get_package("test-pkg") is not None


def test_get_version():
    reg = PackageRegistry()
    release = PackageRelease(name="mylib", version="0.1.0", description="My library")
    reg.publish(release)
    v = reg.get_version("mylib", "0.1.0")
    assert v is not None
    assert v.version == "0.1.0"


def test_search():
    reg = PackageRegistry()
    reg.publish(PackageRelease(name="web-framework", version="1.0.0", description="Web framework for I"))
    reg.publish(PackageRelease(name="test-utils", version="0.1.0", description="Testing utilities"))
    results = reg.search("web")
    assert any(r["name"] == "web-framework" for r in results)
    assert not any(r["name"] == "test-utils" for r in results)


def test_yank_version():
    reg = PackageRegistry()
    reg.publish(PackageRelease(name="broken-pkg", version="0.1.0"))
    assert reg.yank_version("broken-pkg", "0.1.0", "Security issue") is True
    v = reg.get_version("broken-pkg", "0.1.0")
    assert v is not None
    assert v.yanked is True


def test_record_download():
    reg = PackageRegistry()
    reg.publish(PackageRelease(name="popular", version="1.0.0"))
    reg.record_download("popular")
    stats = reg.get_stats("popular")
    assert stats is not None
    assert stats.total_downloads == 1


def test_verify_publisher():
    reg = PackageRegistry()
    assert reg.is_verified_publisher("publisher1") is False
    reg.verify_publisher("publisher1")
    assert reg.is_verified_publisher("publisher1") is True


def test_visibility_filter():
    reg = PackageRegistry()
    reg.publish(PackageRelease(name="public-pkg", version="1.0.0", visibility=PackageVisibility.PUBLIC))
    reg.publish(PackageRelease(name="private-pkg", version="1.0.0", visibility=PackageVisibility.PRIVATE))
    public = reg.list_packages(PackageVisibility.PUBLIC)
    assert "public-pkg" in public
    assert "private-pkg" not in public


def test_dependency_graph():
    reg = PackageRegistry()
    reg.publish(PackageRelease(name="app", version="1.0.0", dependencies={"lib-a": "^1.0", "lib-b": "^2.0"}))
    reg.publish(PackageRelease(name="lib-a", version="1.0.0", dependencies={"lib-c": "^1.0"}))
    graph = reg.get_dependency_graph("app")
    assert "app" in graph
    assert "lib-a" in graph


def test_popularity():
    reg = PackageRegistry()
    reg.publish(PackageRelease(name="mypkg", version="1.0.0"))
    pop = reg.get_popularity("mypkg")
    assert "downloads" in pop
    assert pop["score"] == 0.0


def test_package_not_found():
    reg = PackageRegistry()
    assert reg.get_package("nonexistent") is None
    assert reg.get_version("nonexistent", "0.1.0") is None
