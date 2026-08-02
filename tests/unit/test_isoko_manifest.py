"""Tests for isoko manifest parsing robustness (BOM handling)."""

import os
import tempfile

from isoko.manifest import _parse_toml_simple, load


class TestManifestBom:
    def test_toml_with_utf8_bom(self):
        text = "\ufeff[package]\nname = \"demo\"\nversion = \"1.0.0\"\n"
        data = _parse_toml_simple(text)
        assert data["package"]["name"] == "demo"
        assert data["package"]["version"] == "1.0.0"

    def test_load_toml_file_with_bom(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "ilang.toml")
            with open(path, "wb") as f:
                f.write(b"\xef\xbb\xbf[package]\nname = \"demo\"\nversion = \"1.0.0\"\n")
            m = load(path)
            assert m.name == "demo"
            assert m.version == "1.0.0"
            assert m.lib == "lib"

    def test_load_json_with_bom(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "ilang.json")
            with open(path, "wb") as f:
                f.write(b"\xef\xbb\xbf{\"package\": {\"name\": \"demo\"}}")
            m = load(path)
            assert m.name == "demo"

    def test_plain_toml_without_bom(self):
        data = _parse_toml_simple("[package]\nname = \"demo\"\n")
        assert data["package"]["name"] == "demo"
