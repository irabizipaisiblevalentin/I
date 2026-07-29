"""Tests for istudio.porogaramu — Extension Platform."""

from __future__ import annotations

import json
import os
import tempfile

from src.istudio.porogaramu import ExtensionManager
from src.istudio.ibikoreshingiro import PluginManifest, PluginState


def _write_manifest(data: dict) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
    json.dump(data, f)
    fname = f.name
    f.close()
    return fname


def test_extension_manager_init():
    em = ExtensionManager()
    assert em.list_plugins() == []
    assert em.list_extension_points() == []


def test_register_extension_point():
    em = ExtensionManager()
    ep = em.register_extension_point("editor.didOpen", "File opened event")
    assert ep.name == "editor.didOpen"
    assert em.get_extension_point("editor.didOpen") is not None
    assert em.get_extension_point("nonexistent") is None


def test_list_extension_points():
    em = ExtensionManager()
    em.register_extension_point("ep1")
    em.register_extension_point("ep2")
    assert len(em.list_extension_points()) == 2


def test_register_handler():
    em = ExtensionManager()
    em.register_extension_point("test.point")
    called = []
    def handler(data):
        called.append(data)
    assert em.register_handler("test.point", handler) is True
    em.invoke_handlers("test.point", "hello")
    assert called == ["hello"]


def test_register_handler_nonexistent():
    em = ExtensionManager()
    assert em.register_handler("nonexistent", lambda: None) is False


def test_invoke_handlers():
    em = ExtensionManager()
    em.register_extension_point("calc")
    results = []
    em.register_handler("calc", lambda x: x * 2)
    em.register_handler("calc", lambda x: x * 3)
    r = em.invoke_handlers("calc", 5)
    assert r == [10, 15]


def test_invoke_handlers_empty():
    em = ExtensionManager()
    em.register_extension_point("empty")
    assert em.invoke_handlers("empty") == []


def test_install_plugin():
    em = ExtensionManager()
    manifest = {
        "id": "test-plugin",
        "name": "Test Plugin",
        "version": "1.0.0",
        "description": "A test plugin",
        "author": "Tester",
    }
    fname = _write_manifest(manifest)
    try:
        pm = em.install_plugin(fname)
        assert pm.id == "test-plugin"
        assert pm.name == "Test Plugin"
    finally:
        os.unlink(fname)


def test_list_plugins():
    em = ExtensionManager()
    fname = _write_manifest({"id": "p1", "name": "Plugin 1"})
    try:
        em.install_plugin(fname)
        plugins = em.list_plugins()
        assert len(plugins) == 1
        assert plugins[0]["id"] == "p1"
        assert plugins[0]["name"] == "Plugin 1"
    finally:
        os.unlink(fname)


def test_get_plugin():
    em = ExtensionManager()
    fname = _write_manifest({"id": "p1", "name": "P1"})
    try:
        em.install_plugin(fname)
        p = em.get_plugin("p1")
        assert p is not None
        assert p["manifest"].id == "p1"
        assert em.get_plugin("nonexistent") is None
    finally:
        os.unlink(fname)


def test_enable_disable_plugin():
    em = ExtensionManager()
    fname = _write_manifest({"id": "p1", "name": "P1"})
    try:
        em.install_plugin(fname)
        assert em.disable_plugin("p1") is True
        assert em.get_plugin("p1")["enabled"] is False
        assert em.enable_plugin("p1") is True
        assert em.get_plugin("p1")["enabled"] is True
        assert em.enable_plugin("nonexistent") is False
        assert em.disable_plugin("nonexistent") is False
    finally:
        os.unlink(fname)


def test_uninstall_plugin():
    em = ExtensionManager()
    fname = _write_manifest({"id": "p1", "name": "P1"})
    try:
        em.install_plugin(fname)
        assert em.uninstall_plugin("p1") is True
        assert em.get_plugin("p1")["enabled"] is False
        assert em.uninstall_plugin("nonexistent") is False
    finally:
        os.unlink(fname)
