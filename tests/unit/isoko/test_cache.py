"""Tests for isoko cache module."""

import os
import tempfile

import pytest
from isoko.cache import PackageCache, CacheConfig, CacheEntry


class TestCacheConfig:
    def test_default_dir(self):
        cfg = CacheConfig()
        assert ".isoko" in cfg.cache_dir

    def test_custom_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = CacheConfig(tmpdir)
            assert cfg.cache_dir == tmpdir
            assert "packages" in cfg.packages_dir
            assert "metadata" in cfg.metadata_dir
            assert "tarballs" in cfg.tarballs_dir

    def test_ensure_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = CacheConfig(tmpdir)
            cfg.ensure_dirs()
            assert os.path.isdir(cfg.packages_dir)
            assert os.path.isdir(cfg.metadata_dir)
            assert os.path.isdir(cfg.tarballs_dir)


class TestCacheEntry:
    def test_to_dict(self):
        e = CacheEntry(name="test", version="1.0.0", checksum="abc", size=1024)
        d = e.to_dict()
        assert d["name"] == "test"
        assert d["version"] == "1.0.0"
        assert d["size"] == 1024

    def test_from_dict(self):
        d = {"name": "test", "version": "2.0.0", "checksum": "xyz", "size": 2048}
        e = CacheEntry.from_dict(d)
        assert e.name == "test"
        assert e.version == "2.0.0"


class TestPackageCache:
    def test_has(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = CacheConfig(tmpdir)
            cache = PackageCache(cfg)
            assert not cache.has("test", "1.0.0")

    def test_put_get(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = CacheConfig(tmpdir)
            cache = PackageCache(cfg)

            # Create a fake package directory
            src_dir = os.path.join(tmpdir, "src")
            os.makedirs(src_dir)
            with open(os.path.join(src_dir, "file.i"), "w") as f:
                f.write("// test")

            pkg_dir = cache.put("test", "1.0.0", src_dir)
            assert os.path.isdir(pkg_dir)
            assert cache.has("test", "1.0.0")
            assert cache.get("test", "1.0.0") == pkg_dir

    def test_put_tarball(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = CacheConfig(tmpdir)
            cache = PackageCache(cfg)
            path = cache.put_tarball("test", "1.0.0", b"fake tarball")
            assert os.path.exists(path)

    def test_get_tarball(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = CacheConfig(tmpdir)
            cache = PackageCache(cfg)
            cache.put_tarball("test", "1.0.0", b"fake data")
            data = cache.get_tarball("test", "1.0.0")
            assert data == b"fake data"

    def test_get_tarball_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = CacheConfig(tmpdir)
            cache = PackageCache(cfg)
            assert cache.get_tarball("missing", "1.0.0") is None

    def test_put_get_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = CacheConfig(tmpdir)
            cache = PackageCache(cfg)
            cache.put_metadata("test", {"name": "test"})
            meta = cache.get_metadata("test")
            assert meta is not None
            assert meta["name"] == "test"

    def test_remove(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = CacheConfig(tmpdir)
            cache = PackageCache(cfg)

            src_dir = os.path.join(tmpdir, "src")
            os.makedirs(src_dir)
            cache.put("test", "1.0.0", src_dir)
            assert cache.has("test", "1.0.0")

            assert cache.remove("test", "1.0.0")
            assert not cache.has("test", "1.0.0")
            assert not cache.remove("test", "1.0.0")

    def test_clear(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = CacheConfig(tmpdir)
            cache = PackageCache(cfg)

            src_dir = os.path.join(tmpdir, "src")
            os.makedirs(src_dir)
            cache.put("a", "1.0.0", src_dir)
            cache.put("b", "2.0.0", src_dir)

            count = cache.clear()
            assert count == 2
            assert not cache.has("a", "1.0.0")
            assert not cache.has("b", "2.0.0")

    def test_stats(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = CacheConfig(tmpdir)
            cache = PackageCache(cfg)
            stats = cache.stats()
            assert stats["total_packages"] == 0
            assert stats["total_size_bytes"] == 0

    def test_list_packages(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = CacheConfig(tmpdir)
            cache = PackageCache(cfg)
            packages = cache.list_packages()
            assert len(packages) == 0
