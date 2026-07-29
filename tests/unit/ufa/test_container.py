"""Tests for UFA dependency injection container."""

import pytest
from ufa.container import Container, Scope


class DummyService:
    def __init__(self):
        self.value = 42


class DependentService:
    def __init__(self, dep: DummyService):
        self.dep = dep


class TestContainer:
    def test_register_and_resolve(self):
        c = Container()
        c.register_singleton(DummyService)
        s = c.resolve(DummyService)
        assert isinstance(s, DummyService)
        assert s.value == 42

    def test_singleton_same_instance(self):
        c = Container()
        c.register_singleton(DummyService)
        s1 = c.resolve(DummyService)
        s2 = c.resolve(DummyService)
        assert s1 is s2

    def test_transient_new_instances(self):
        c = Container()
        c.register_transient(DummyService)
        s1 = c.resolve(DummyService)
        s2 = c.resolve(DummyService)
        assert s1 is not s2

    def test_register_instance(self):
        c = Container()
        inst = DummyService()
        c.register_instance(DummyService, inst)
        assert c.resolve(DummyService) is inst

    def test_register_factory(self):
        c = Container()
        c.register_factory(DummyService, lambda c: DummyService())
        s = c.resolve(DummyService)
        assert isinstance(s, DummyService)

    def test_try_resolve_none(self):
        c = Container()
        assert c.try_resolve(DummyService) is None

    def test_has(self):
        c = Container()
        assert not c.has(DummyService)
        c.register_singleton(DummyService)
        assert c.has(DummyService)

    def test_parent_child(self):
        parent = Container()
        parent.register_singleton(DummyService)
        child = parent.create_scope()
        s = child.resolve(DummyService)
        assert isinstance(s, DummyService)

    def test_child_override(self):
        parent = Container()
        parent.register_singleton(DummyService)
        child = parent.create_scope()
        child.register_singleton(DummyService)
        s_parent = parent.resolve(DummyService)
        s_child = child.resolve(DummyService)
        assert s_parent is not s_child

    def test_resolve_missing_raises(self):
        c = Container()
        with pytest.raises(LookupError):
            c.resolve(DummyService)

    def test_scoped(self):
        c = Container()
        c.register_scoped(DummyService)
        scope = c.create_scope()
        s1 = scope.resolve(DummyService)
        s2 = scope.resolve(DummyService)
        assert s1 is s2

    def test_clear(self):
        c = Container()
        c.register_singleton(DummyService)
        c.clear()
        assert not c.has(DummyService)
