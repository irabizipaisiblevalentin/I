"""Tests for UFA plugin system."""

import pytest
from ufa.plugins import Plugin, PluginRegistry, PluginMetadata, PluginState


class DummyPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.metadata = PluginMetadata(name="dummy", version="1.0.0")
        self.init_called = False
        self.start_called = False
        self.stop_called = False

    def initialize(self, context):
        self.init_called = True
        self._state = PluginState.INITIALIZED

    def start(self):
        self.start_called = True
        self._state = PluginState.STARTED

    def stop(self):
        self.stop_called = True
        self._state = PluginState.STOPPED


class TestPlugin:
    def test_plugin_metadata(self):
        p = DummyPlugin()
        assert p.name == "dummy"
        assert p.state == PluginState.REGISTERED

    def test_plugin_health(self):
        p = DummyPlugin()
        assert p.health_check() is True


class TestPluginRegistry:
    def test_register_and_get(self):
        reg = PluginRegistry()
        p = DummyPlugin()
        reg.register(p)
        assert reg.get("dummy") is p

    def test_has(self):
        reg = PluginRegistry()
        assert not reg.has("dummy")
        reg.register(DummyPlugin())
        assert reg.has("dummy")

    def test_unregister(self):
        reg = PluginRegistry()
        reg.register(DummyPlugin())
        assert reg.unregister("dummy")
        assert not reg.has("dummy")

    def test_list_plugins(self):
        reg = PluginRegistry()
        reg.register(DummyPlugin())
        plugins = reg.list_plugins()
        assert len(plugins) == 1
        assert plugins[0].name == "dummy"

    def test_resolve_load_order(self):
        reg = PluginRegistry()
        p1 = DummyPlugin()
        p1.metadata.name = "a"
        p2 = DummyPlugin()
        p2.metadata.name = "b"
        p2.metadata.dependencies = ["a"]
        reg.register(p1)
        reg.register(p2)
        order = reg.resolve_load_order()
        assert order.index("a") < order.index("b")

    def test_validate_dependencies(self):
        reg = PluginRegistry()
        p = DummyPlugin()
        p.metadata.dependencies = ["missing"]
        reg.register(p)
        errors = reg.validate_dependencies()
        assert len(errors) == 1

    def test_initialize_all(self):
        reg = PluginRegistry()
        p = DummyPlugin()
        reg.register(p)
        reg.initialize_all()
        assert p.init_called

    def test_start_all(self):
        reg = PluginRegistry()
        p = DummyPlugin()
        reg.register(p)
        reg.initialize_all()
        reg.start_all()
        assert p.start_called

    def test_stop_all(self):
        reg = PluginRegistry()
        p = DummyPlugin()
        reg.register(p)
        reg.initialize_all()
        reg.start_all()
        reg.stop_all()
        assert p.stop_called

    def test_health_check(self):
        reg = PluginRegistry()
        p = DummyPlugin()
        reg.register(p)
        result = reg.health_check()
        assert result["dummy"] is True

    def test_count(self):
        reg = PluginRegistry()
        assert reg.count() == 0
        reg.register(DummyPlugin())
        assert reg.count() == 1
