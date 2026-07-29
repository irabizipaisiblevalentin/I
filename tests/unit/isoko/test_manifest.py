"""Tests for isoko manifest module."""

import json
import os
import tempfile

import pytest
from isoko.manifest import Manifest, load, save, find_manifest, _parse_toml_simple


class TestManifest:
    def test_defaults(self):
        m = Manifest()
        assert m.name == ""
        assert m.version == "0.1.0"
        assert m.license == "MIT"
        assert m.dependencies == {}
        assert m.dev_dependencies == {}

    def test_all_dependencies(self):
        m = Manifest()
        m.dependencies = {"a": "^1.0.0"}
        m.optional_dependencies = {"b": "^2.0.0"}
        result = m.all_dependencies
        assert "a" in result
        assert "b" in result

    def test_full_name(self):
        m = Manifest()
        m.name = "test-pkg"
        m.version = "1.0.0"
        assert m.full_name == "test-pkg@1.0.0"

    def test_to_dict(self):
        m = Manifest()
        m.name = "test-pkg"
        m.version = "1.0.0"
        m.description = "A test package"
        d = m.to_dict()
        assert d["package"]["name"] == "test-pkg"
        assert d["package"]["version"] == "1.0.0"
        assert d["package"]["description"] == "A test package"

    def test_to_dict_with_deps(self):
        m = Manifest()
        m.name = "test"
        m.dependencies = {"dep1": "^1.0.0"}
        d = m.to_dict()
        assert d["dependencies"]["dep1"] == "^1.0.0"

    def test_to_dict_with_dev_deps(self):
        m = Manifest()
        m.name = "test"
        m.dev_dependencies = {"dev1": "^1.0.0"}
        d = m.to_dict()
        assert d["dev-dependencies"]["dev1"] == "^1.0.0"

    def test_to_dict_full(self):
        m = Manifest()
        m.name = "test"
        m.authors = [{"name": "Author", "email": "a@b.com"}]
        m.keywords = ["test"]
        m.categories = ["testing"]
        m.engines = {"i": ">=0.1.0"}
        m.scripts = {"test": "i test"}
        m.bin = "test"
        d = m.to_dict()
        assert "authors" in d["package"]
        assert "keywords" in d["package"]
        assert "scripts" in d


class TestTOMLParsing:
    def test_simple_table(self):
        toml = '[package]\nname = "test"\nversion = "1.0.0"'
        result = _parse_toml_simple(toml)
        assert result["package"]["name"] == "test"
        assert result["package"]["version"] == "1.0.0"

    def test_dependencies(self):
        toml = '[dependencies]\nfoo = "^1.0.0"\nbar = ">=2.0.0"'
        result = _parse_toml_simple(toml)
        assert result["dependencies"]["foo"] == "^1.0.0"
        assert result["dependencies"]["bar"] == ">=2.0.0"

    def test_comments(self):
        toml = '# comment\n[package]\nname = "test" # inline'
        result = _parse_toml_simple(toml)
        assert result["package"]["name"] == "test"

    def test_string_types(self):
        toml = '[package]\nname = "double"\nother = \'single\''
        result = _parse_toml_simple(toml)
        assert result["package"]["name"] == "double"
        assert result["package"]["other"] == "single"

    def test_boolean(self):
        toml = '[package]\nactive = true\ndisabled = false'
        result = _parse_toml_simple(toml)
        assert result["package"]["active"] is True
        assert result["package"]["disabled"] is False

    def test_integer(self):
        toml = '[package]\ncount = 42'
        result = _parse_toml_simple(toml)
        assert result["package"]["count"] == 42

    def test_float(self):
        toml = '[package]\npi = 3.14'
        result = _parse_toml_simple(toml)
        assert result["package"]["pi"] == 3.14

    def test_array(self):
        toml = '[package]\ntags = ["a", "b", "c"]'
        result = _parse_toml_simple(toml)
        assert result["package"]["tags"] == ["a", "b", "c"]

    def test_inline_table(self):
        toml = '[package]\nauthor = {name = "Test", email = "test@test.com"}'
        result = _parse_toml_simple(toml)
        assert result["package"]["author"]["name"] == "Test"

    def test_nested_tables(self):
        toml = '[package]\n[package.metadata]\nkey = "value"'
        result = _parse_toml_simple(toml)
        assert result["package"]["metadata"]["key"] == "value"


class TestLoadSave:
    def test_load_toml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml",
                                          delete=False) as f:
            f.write('[package]\nname = "test-pkg"\nversion = "2.0.0"\n')
            path = f.name
        try:
            m = load(path)
            assert m.name == "test-pkg"
            assert m.version == "2.0.0"
        finally:
            os.unlink(path)

    def test_load_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                          delete=False) as f:
            json.dump({
                "package": {"name": "json-pkg", "version": "3.0.0"},
                "dependencies": {"dep1": "^1.0.0"},
            }, f)
            path = f.name
        try:
            m = load(path)
            assert m.name == "json-pkg"
            assert m.version == "3.0.0"
            assert m.dependencies["dep1"] == "^1.0.0"
        finally:
            os.unlink(path)

    def test_save_json(self):
        m = Manifest()
        m.name = "saved-pkg"
        m.version = "1.0.0"
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            save(m, path)
            with open(path) as f:
                data = json.load(f)
            assert data["package"]["name"] == "saved-pkg"
        finally:
            os.unlink(path)

    def test_load_not_found(self):
        with pytest.raises(FileNotFoundError):
            load("/nonexistent/path/ilang.toml")


class TestFindManifest:
    def test_find_in_current_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            toml_path = os.path.join(tmpdir, "ilang.toml")
            with open(toml_path, "w") as f:
                f.write('[package]\nname = "test"')
            result = find_manifest(tmpdir)
            assert result == toml_path

    def test_find_in_parent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = os.path.join(tmpdir, "sub", "dir")
            os.makedirs(subdir)
            toml_path = os.path.join(tmpdir, "ilang.toml")
            with open(toml_path, "w") as f:
                f.write('[package]\nname = "test"')
            result = find_manifest(subdir)
            assert result == toml_path

    def test_find_not_found(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = find_manifest(tmpdir)
            assert result is None

    def test_find_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "ilang.json")
            with open(json_path, "w") as f:
                json.dump({"package": {"name": "test"}}, f)
            result = find_manifest(tmpdir)
            assert result == json_path
