"""Tests for the isoko registry client search normalization."""

from isoko.registry import RegistryClient


class TestSearchNormalization:
    def test_normalize_flat_item(self):
        item = {"name": "demo", "latest_version": "1.2.0", "description": "hi"}
        assert RegistryClient._normalize_search_item(item) == {
            "name": "demo", "latest_version": "1.2.0", "description": "hi"}

    def test_normalize_version_key_fallback(self):
        item = {"name": "demo", "version": "0.9.0"}
        out = RegistryClient._normalize_search_item(item)
        assert out["latest_version"] == "0.9.0"

    def test_normalize_nested_package(self):
        item = {"package": {"name": "libx", "version": "2.0.0"}}
        out = RegistryClient._normalize_search_item(item)
        assert out["name"] == "libx"
        assert out["latest_version"] == "2.0.0"

    def test_normalize_non_dict(self):
        out = RegistryClient._normalize_search_item("string-name")
        assert out["name"] == "string-name"

    def test_search_results_shape_uses_results_key(self, monkeypatch):
        client = RegistryClient()
        monkeypatch.setattr(client, "_request", lambda *a, **k: {"results": [{"name": "a"}]})
        results = client.search("a")
        assert len(results) == 1
        assert results[0]["name"] == "a"
        assert results[0]["latest_version"] == "?"

    def test_search_objects_shape(self, monkeypatch):
        client = RegistryClient()
        monkeypatch.setattr(client, "_request",
                            lambda *a, **k: {"objects": [{"package": {"name": "b", "version": "1.0.0"}}]})
        results = client.search("b")
        assert results[0]["name"] == "b"
        assert results[0]["latest_version"] == "1.0.0"

    def test_search_bare_list_shape(self, monkeypatch):
        client = RegistryClient()
        monkeypatch.setattr(client, "_request", lambda *a, **k: [{"name": "c", "version": "3.0.0"}])
        results = client.search("c")
        assert results[0]["latest_version"] == "3.0.0"
