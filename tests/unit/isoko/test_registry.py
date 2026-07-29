"""Tests for isoko registry module."""

import pytest
from isoko.registry import RegistryClient, RegistryConfig, RegistryError
from isoko.semver import Version


class TestRegistryConfig:
    def test_defaults(self):
        cfg = RegistryConfig()
        assert cfg.url == "https://registry.i-lang.dev"
        assert cfg.token == ""
        assert cfg.offline is False
        assert cfg.timeout == 30

    def test_custom(self):
        cfg = RegistryConfig(
            url="https://custom.registry.dev",
            token="abc",
            offline=True,
            timeout=60,
        )
        assert cfg.url == "https://custom.registry.dev"
        assert cfg.token == "abc"
        assert cfg.offline is True


class TestRegistryClient:
    def test_init(self):
        client = RegistryClient()
        assert client._config is not None

    def test_get_versions_offline(self):
        cfg = RegistryConfig(offline=True)
        client = RegistryClient(cfg)
        versions = client.get_versions("nonexistent")
        assert versions == []

    def test_get_package_offline(self):
        cfg = RegistryConfig(offline=True)
        client = RegistryClient(cfg)
        result = client.get_package("nonexistent", "1.0.0")
        assert result is None

    def test_search_offline(self):
        cfg = RegistryConfig(offline=True)
        client = RegistryClient(cfg)
        results = client.search("test")
        assert results == []

    def test_download_offline(self):
        cfg = RegistryConfig(offline=True)
        client = RegistryClient(cfg)
        result = client.download("pkg", "1.0.0")
        assert result is None

    def test_publish_offline(self):
        cfg = RegistryConfig(offline=True)
        client = RegistryClient(cfg)
        result = client.publish("pkg", "1.0.0", b"data")
        assert result is False

    def test_yank_offline(self):
        cfg = RegistryConfig(offline=True)
        client = RegistryClient(cfg)
        result = client.yank("pkg", "1.0.0", "reason")
        assert result is False


class TestRegistryError:
    def test_message(self):
        err = RegistryError("test error")
        assert str(err) == "test error"
