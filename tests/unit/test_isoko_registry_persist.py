"""Tests for developer-platform PackageRegistry persistence."""

import os

from isoko.ideveloper.ibikoreshingiro import (
    PackageRelease,
    PackageVisibility,
)
from isoko.ideveloper.ububiko import PackageRegistry


class TestRegistryPersistence:
    def test_publish_and_reload(self, monkeypatch, tmp_path):
        os.environ["ISOKO_HOME"] = str(tmp_path)
        r = PackageRegistry()
        r.publish(PackageRelease(
            name="demo", version="1.0.0", description="d",
            author_name="A", visibility=PackageVisibility.PRIVATE,
        ))

        r2 = PackageRegistry()
        pkg = r2.get_package("demo")
        assert pkg is not None
        assert pkg.name == "demo"
        assert pkg.version == "1.0.0"
        assert pkg.visibility == PackageVisibility.PRIVATE

    def test_search_across_reload(self, monkeypatch, tmp_path):
        os.environ["ISOKO_HOME"] = str(tmp_path)
        PackageRegistry().publish(PackageRelease(
            name="tok", version="2.0.0", description="keyword here"))
        results = PackageRegistry().search("keyword")
        assert any(x["name"] == "tok" for x in results)

    def test_yank_persists(self, monkeypatch, tmp_path):
        os.environ["ISOKO_HOME"] = str(tmp_path)
        PackageRegistry().publish(PackageRelease(name="pkg", version="1.0.0"))
        assert PackageRegistry().yank_version("pkg", "1.0.0", "outdated")
        v = PackageRegistry().get_version("pkg", "1.0.0")
        assert v is not None and v.yanked

    def test_verified_publishers_persist(self, monkeypatch, tmp_path):
        os.environ["ISOKO_HOME"] = str(tmp_path)
        PackageRegistry().verify_publisher("author-1")
        assert PackageRegistry().is_verified_publisher("author-1")

    def test_isolation_between_homes(self, monkeypatch, tmp_path):
        a = str(tmp_path / "a")
        b = str(tmp_path / "b")
        os.environ["ISOKO_HOME"] = a
        PackageRegistry().publish(PackageRelease(name="only-a", version="1.0.0"))
        os.environ["ISOKO_HOME"] = b
        assert PackageRegistry().get_package("only-a") is None
