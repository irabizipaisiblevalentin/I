"""Tests for isoko lockfile module."""

import json
import os
import tempfile

import pytest
from isoko.lockfile import LockFile, LockEntry, load_lockfile, save_lockfile, create_from_resolved


class TestLockEntry:
    def test_defaults(self):
        e = LockEntry()
        assert e.name == ""
        assert e.version == ""
        assert e.source == "registry"

    def test_to_dict(self):
        e = LockEntry(name="test", version="1.0.0", checksum="abc123")
        d = e.to_dict()
        assert d["version"] == "1.0.0"
        assert d["source"] == "registry"
        assert d["checksum"] == "abc123"

    def test_from_dict(self):
        d = {"version": "2.0.0", "source": "registry", "checksum": "xyz"}
        e = LockEntry.from_dict("test", d)
        assert e.name == "test"
        assert e.version == "2.0.0"
        assert e.checksum == "xyz"

    def test_with_dependencies(self):
        e = LockEntry(name="a", version="1.0.0", dependencies={"b": "^1.0.0"})
        d = e.to_dict()
        assert d["dependencies"]["b"] == "^1.0.0"

    def test_repr(self):
        e = LockEntry(name="test", version="1.0.0")
        assert "test" in repr(e)
        assert "1.0.0" in repr(e)


class TestLockFile:
    def test_add_get(self):
        lf = LockFile("project")
        lf.add(LockEntry(name="a", version="1.0.0"))
        assert lf.get("a") is not None
        assert lf.get("a").version == "1.0.0"
        assert lf.get("nonexistent") is None

    def test_remove(self):
        lf = LockFile()
        lf.add(LockEntry(name="a", version="1.0.0"))
        assert lf.remove("a") is True
        assert lf.get("a") is None
        assert lf.remove("a") is False

    def test_has(self):
        lf = LockFile()
        lf.add(LockEntry(name="a", version="1.0.0"))
        assert lf.has("a")
        assert not lf.has("b")

    def test_is_satisfied(self):
        lf = LockFile()
        lf.add(LockEntry(name="a", version="1.0.0"))
        assert lf.is_satisfied("a", "1.0.0")
        assert not lf.is_satisfied("a", "2.0.0")
        assert not lf.is_satisfied("b", "1.0.0")

    def test_to_dict(self):
        lf = LockFile("project")
        lf.add(LockEntry(name="b", version="2.0.0"))
        lf.add(LockEntry(name="a", version="1.0.0"))
        d = lf.to_dict()
        assert d["project"] == "project"
        assert "a" in d["packages"]
        assert "b" in d["packages"]
        # entries are sorted by name
        keys = list(d["packages"].keys())
        assert keys == ["a", "b"]

    def test_from_dict(self):
        d = {
            "format_version": "1.0",
            "project": "test",
            "packages": {
                "a": {"version": "1.0.0", "source": "registry"},
                "b": {"version": "2.0.0", "source": "git"},
            },
        }
        lf = LockFile.from_dict(d)
        assert lf.project_name == "test"
        assert lf.has("a")
        assert lf.has("b")
        assert lf.get("b").source == "git"

    def test_to_json(self):
        lf = LockFile("test")
        lf.add(LockEntry(name="a", version="1.0.0"))
        j = lf.to_json()
        data = json.loads(j)
        assert data["project"] == "test"

    def test_checksum(self):
        lf = LockFile("test")
        lf.add(LockEntry(name="a", version="1.0.0"))
        c1 = lf.checksum()
        c2 = lf.checksum()
        assert c1 == c2
        assert len(c1) == 64  # SHA-256 hex

    def test_checksum_changes_with_content(self):
        lf1 = LockFile("test")
        lf1.add(LockEntry(name="a", version="1.0.0"))
        lf2 = LockFile("test")
        lf2.add(LockEntry(name="a", version="2.0.0"))
        assert lf1.checksum() != lf2.checksum()


class TestLoadSave:
    def test_save_load_roundtrip(self):
        lf = LockFile("project")
        lf.add(LockEntry(name="a", version="1.0.0", checksum="abc"))
        lf.add(LockEntry(name="b", version="2.0.0", dependencies={"a": "^1.0.0"}))

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save_lockfile(lf, path)
            loaded = load_lockfile(path)
            assert loaded is not None
            assert loaded.project_name == "project"
            assert loaded.has("a")
            assert loaded.has("b")
            assert loaded.get("a").checksum == "abc"
            assert loaded.get("b").dependencies["a"] == "^1.0.0"
        finally:
            os.unlink(path)

    def test_load_nonexistent(self):
        result = load_lockfile("/nonexistent/path/ilang.lock")
        assert result is None

    def test_load_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                          delete=False) as f:
            f.write("not json {{{")
            path = f.name
        try:
            result = load_lockfile(path)
            assert result is None
        finally:
            os.unlink(path)


class TestCreateFromResolved:
    def test_basic(self):
        resolved = {
            "a": {"version": "1.0.0", "dependencies": {"b": "^1.0.0"}},
            "b": {"version": "1.5.0", "dependencies": {}},
        }
        lf = create_from_resolved("project", resolved)
        assert lf.project_name == "project"
        assert lf.has("a")
        assert lf.has("b")
        assert lf.get("a").version == "1.0.0"
        assert lf.get("b").version == "1.5.0"
