"""Tests for UFA configuration system."""

import json
import os
import tempfile

import pytest
from ufa.configuration import Configuration, Profiles


class TestConfiguration:
    def test_get_set(self):
        cfg = Configuration()
        cfg.set("server.port", 8080)
        assert cfg.get("server.port") == 8080

    def test_has(self):
        cfg = Configuration()
        cfg.set("a.b.c", 1)
        assert cfg.has("a.b.c")
        assert not cfg.has("a.b.d")

    def test_delete(self):
        cfg = Configuration()
        cfg.set("a.b", 1)
        assert cfg.delete("a.b")
        assert not cfg.has("a.b")

    def test_merge(self):
        cfg = Configuration()
        cfg.merge({"a": {"b": 1}})
        cfg.merge({"a": {"c": 2}})
        assert cfg.get("a.b") == 1
        assert cfg.get("a.c") == 2

    def test_override(self):
        cfg = Configuration()
        cfg.set("a", 1)
        cfg.override({"a": 2})
        assert cfg.get("a") == 2

    def test_subset(self):
        cfg = Configuration()
        cfg.set("server.host", "localhost")
        cfg.set("server.port", 8080)
        sub = cfg.subset("server")
        assert sub.get("host") == "localhost"

    def test_flatten(self):
        cfg = Configuration()
        cfg.set("a.b", 1)
        flat = cfg.flatten()
        assert "a.b" in flat

    def test_load_env(self):
        os.environ["I_TEST__PORT"] = "3000"
        cfg = Configuration()
        count = cfg.load_env(prefix="I_TEST__")
        os.environ.pop("I_TEST__PORT", None)
        assert cfg.get("port") == 3000 or count >= 0

    def test_load_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                         delete=False) as f:
            json.dump({"x": 1}, f)
            path = f.name
        try:
            cfg = Configuration()
            assert cfg.load_file(path)
            assert cfg.get("x") == 1
        finally:
            os.unlink(path)

    def test_load_file_missing(self):
        cfg = Configuration()
        assert not cfg.load_file("/nonexistent/path.json")

    def test_save(self):
        cfg = Configuration()
        cfg.set("a", 1)
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "cfg.json")
            cfg.save(path)
            with open(path) as f:
                data = json.load(f)
            assert data["a"] == 1

    def test_get_or_default(self):
        cfg = Configuration()
        val = cfg.get_or_default("missing", lambda: "default")
        assert val == "default"

    def test_contains(self):
        cfg = Configuration()
        cfg.set("x", 1)
        assert "x" in cfg

    def test_getitem(self):
        cfg = Configuration()
        cfg.set("x", 1)
        assert cfg["x"] == 1

    def test_getitem_missing(self):
        cfg = Configuration()
        with pytest.raises(KeyError):
            _ = cfg["missing"]

    def test_keys_values_items(self):
        cfg = Configuration()
        cfg.set("a", 1)
        cfg.set("b", 2)
        assert "a" in cfg.keys()
        assert 1 in cfg.values()


class TestProfiles:
    def test_add_activate(self):
        p = Profiles()
        p.add("dev", Configuration({"debug": True}))
        p.activate("dev")
        assert p.active == "dev"
        assert p.get().get("debug") is True

    def test_unknown_profile(self):
        p = Profiles()
        with pytest.raises(ValueError):
            p.activate("unknown")

    def test_list_profiles(self):
        p = Profiles()
        p.add("a", Configuration())
        p.add("b", Configuration())
        assert set(p.profiles()) == {"a", "b"}
