"""guhindura — Scripting system: I language integration, hot reload, plugins."""

from __future__ import annotations

import importlib
import inspect
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, List, Optional, Type

from .imiyoborere import Entity, Component, World, System


@dataclass
class ScriptComponent(Component):
    module_path: str = ""
    class_name: str = ""
    enabled: bool = True
    _instance: Any = None

    def get_instance(self) -> Any:
        if self._instance is None:
            self._instance = ScriptEngine.load_instance(self.module_path, self.class_name)
        return self._instance


class ScriptEngine:
    _modules: Dict[str, ModuleType] = {}
    _scripts: Dict[str, Type] = {}
    _instances: Dict[str, Any] = {}
    _watchers: List[Callable] = []

    @classmethod
    def load_module(cls, module_path: str) -> Optional[ModuleType]:
        try:
            if module_path in cls._modules:
                return cls._modules[module_path]
            spec = importlib.util.spec_from_file_location(
                module_path.replace(".", "_"), module_path
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                cls._modules[module_path] = mod
                return mod
        except Exception:
            pass
        return None

    @classmethod
    def load_script(cls, module_path: str, class_name: str) -> Optional[Type]:
        key = f"{module_path}:{class_name}"
        if key in cls._scripts:
            return cls._scripts[key]
        mod = cls.load_module(module_path)
        if mod and hasattr(mod, class_name):
            script_class = getattr(mod, class_name)
            if inspect.isclass(script_class):
                cls._scripts[key] = script_class
                return script_class
        return None

    @classmethod
    def load_instance(cls, module_path: str, class_name: str) -> Any:
        key = f"{module_path}:{class_name}"
        if key in cls._instances:
            return cls._instances[key]
        script_class = cls.load_script(module_path, class_name)
        if script_class:
            instance = script_class()
            cls._instances[key] = instance
            return instance
        return None

    @classmethod
    def hot_reload(cls, module_path: str) -> bool:
        if module_path in cls._modules:
            del cls._modules[module_path]
        old_keys = [k for k in cls._scripts if k.startswith(module_path)]
        for k in old_keys:
            cls._scripts.pop(k, None)
            cls._instances.pop(k, None)
        for watcher in cls._watchers:
            try:
                watcher(module_path)
            except Exception:
                pass
        return True

    @classmethod
    def watch(cls, callback: Callable) -> None:
        cls._watchers.append(callback)

    @classmethod
    def clear(cls) -> None:
        cls._modules.clear()
        cls._scripts.clear()
        cls._instances.clear()


class ScriptSystem(System):
    def __init__(self):
        super().__init__()
        self.scripts: Dict[str, ScriptComponent] = {}

    def on_entity_added(self, entity: Entity) -> None:
        script = entity.get(ScriptComponent)
        if script:
            self.scripts[entity.id] = script
            instance = script.get_instance()
            if instance and hasattr(instance, 'on_create'):
                instance.on_create(entity)

    def on_entity_removed(self, entity: Entity) -> None:
        self.scripts.pop(entity.id, None)
        script = entity.get(ScriptComponent)
        if script and script._instance and hasattr(script._instance, 'on_destroy'):
            script._instance.on_destroy()

    def update(self, dt: float) -> None:
        for eid, script in list(self.scripts.items()):
            if not script.enabled:
                continue
            instance = script._instance
            if instance and hasattr(instance, 'on_update'):
                try:
                    instance.on_update(dt)
                except Exception:
                    pass


class Plugin:
    def __init__(self, name: str = "", version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled: bool = True

    def on_register(self, engine: Any) -> None:
        pass

    def on_unregister(self) -> None:
        pass

    def on_update(self, dt: float) -> None:
        pass


class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        self.plugins[plugin.name] = plugin

    def unregister(self, name: str) -> bool:
        if name in self.plugins:
            self.plugins[name].on_unregister()
            del self.plugins[name]
            return True
        return False

    def get(self, name: str) -> Optional[Plugin]:
        return self.plugins.get(name)

    def update(self, dt: float) -> None:
        for plugin in self.plugins.values():
            if plugin.enabled:
                plugin.on_update(dt)


_script_engine = ScriptEngine()
_plugin_manager = PluginManager()


def get_scripting() -> ScriptEngine:
    return _script_engine


def get_plugins() -> PluginManager:
    return _plugin_manager
