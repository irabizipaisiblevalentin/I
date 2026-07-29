"""Tests for UFA module system."""

import pytest
from ufa.modules import Module, ModuleRegistry, ModuleState, ModuleMetadata


class DummyModule(Module):
    def __init__(self, name="dummy"):
        super().__init__()
        self.metadata = ModuleMetadata(name=name)
        self.init_called = False
        self.start_called = False
        self.stop_called = False

    def initialize(self, context):
        self.init_called = True

    def start(self):
        super().start()
        self.start_called = True

    def stop(self):
        super().stop()
        self.stop_called = True


class TestModule:
    def test_metadata(self):
        m = DummyModule("test")
        assert m.name == "test"

    def test_register_service(self):
        m = DummyModule()
        m.register_service("db", {"conn": True})
        assert m.get_service("db") == {"conn": True}

    def test_services(self):
        m = DummyModule()
        m.register_service("a", 1)
        m.register_service("b", 2)
        assert m.services() == {"a": 1, "b": 2}


class TestModuleRegistry:
    def test_register_and_get(self):
        reg = ModuleRegistry()
        m = DummyModule("m1")
        reg.register(m)
        assert reg.get("m1") is m

    def test_has(self):
        reg = ModuleRegistry()
        assert not reg.has("m1")
        reg.register(DummyModule("m1"))
        assert reg.has("m1")

    def test_unregister(self):
        reg = ModuleRegistry()
        reg.register(DummyModule("m1"))
        assert reg.unregister("m1")
        assert not reg.has("m1")

    def test_list_modules(self):
        reg = ModuleRegistry()
        reg.register(DummyModule("a"))
        reg.register(DummyModule("b"))
        assert len(reg.list_modules()) == 2

    def test_resolve_load_order(self):
        reg = ModuleRegistry()
        m1 = DummyModule("a")
        m2 = DummyModule("b")
        m2.metadata.dependencies = ["a"]
        reg.register(m1)
        reg.register(m2)
        order = reg.resolve_load_order()
        assert order.index("a") < order.index("b")

    def test_validate_dependencies(self):
        reg = ModuleRegistry()
        m = DummyModule("x")
        m.metadata.dependencies = ["missing"]
        reg.register(m)
        errors = reg.validate_dependencies()
        assert len(errors) == 1

    def test_initialize_all(self):
        reg = ModuleRegistry()
        m = DummyModule("m1")
        reg.register(m)
        reg.initialize_all()
        assert m.init_called

    def test_start_all(self):
        reg = ModuleRegistry()
        m = DummyModule("m1")
        reg.register(m)
        reg.initialize_all()
        reg.start_all()
        assert m.start_called

    def test_stop_all(self):
        reg = ModuleRegistry()
        m = DummyModule("m1")
        reg.register(m)
        reg.initialize_all()
        reg.start_all()
        reg.stop_all()
        assert m.stop_called

    def test_module_count(self):
        reg = ModuleRegistry()
        assert reg.module_count() == 0
        reg.register(DummyModule("a"))
        assert reg.module_count() == 1

    def test_circular_dependency(self):
        reg = ModuleRegistry()
        m1 = DummyModule("a")
        m1.metadata.dependencies = ["b"]
        m2 = DummyModule("b")
        m2.metadata.dependencies = ["a"]
        reg.register(m1)
        reg.register(m2)
        with pytest.raises(ValueError, match="circular"):
            reg.resolve_load_order()
