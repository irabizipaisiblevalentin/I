"""I STUDIO — Extension Platform (Porogaramu)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .ibikoreshingiro import ExtensionPoint, PluginError, PluginManifest, PluginState


class ExtensionManager:
    def __init__(self):
        self._plugins: Dict[str, Dict[str, Any]] = {}
        self._extension_points: Dict[str, ExtensionPoint] = {}
        self._handlers: Dict[str, List[Callable]] = {}

    def register_extension_point(self, name: str, description: str = "") -> ExtensionPoint:
        ep = ExtensionPoint(name=name, description=description)
        self._extension_points[name] = ep
        self._handlers.setdefault(name, [])
        return ep

    def get_extension_point(self, name: str) -> Optional[ExtensionPoint]:
        return self._extension_points.get(name)

    def list_extension_points(self) -> List[ExtensionPoint]:
        return list(self._extension_points.values())

    def install_plugin(self, manifest_path: str) -> PluginManifest:
        path = Path(manifest_path)
        if not path.exists():
            raise PluginError(f"Plugin manifest not found: {manifest_path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        manifest = PluginManifest(
            id=data.get("id", path.stem),
            name=data.get("name", path.stem),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            min_istudio_version=data.get("min_istudio_version", "0.1.0"),
            entry_point=data.get("entry_point", ""),
            permissions=data.get("permissions", []),
            contributes=data.get("contributes", {}),
        )
        self._plugins[manifest.id] = {
            "manifest": manifest,
            "state": PluginState.LOADING,
            "enabled": True,
        }
        self._load_plugin(manifest)
        return manifest

    def _load_plugin(self, manifest: PluginManifest) -> None:
        if manifest.entry_point:
            try:
                import importlib
                module_path = manifest.entry_point.replace("/", ".").replace(".py", "")
                importlib.import_module(module_path)
                self._plugins[manifest.id]["state"] = PluginState.ENABLED
            except Exception as e:
                self._plugins[manifest.id]["state"] = PluginState.ERROR
                self._plugins[manifest.id]["error"] = str(e)

    def uninstall_plugin(self, plugin_id: str) -> bool:
        if plugin_id in self._plugins:
            self._plugins[plugin_id]["enabled"] = False
            self._plugins[plugin_id]["state"] = PluginState.DISABLED
            return True
        return False

    def enable_plugin(self, plugin_id: str) -> bool:
        plugin = self._plugins.get(plugin_id)
        if not plugin:
            return False
        plugin["enabled"] = True
        plugin["state"] = PluginState.ENABLED
        return True

    def disable_plugin(self, plugin_id: str) -> bool:
        plugin = self._plugins.get(plugin_id)
        if not plugin:
            return False
        plugin["enabled"] = False
        plugin["state"] = PluginState.DISABLED
        return True

    def get_plugin(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        plugin = self._plugins.get(plugin_id)
        if plugin:
            return {
                "manifest": plugin["manifest"],
                "state": plugin["state"],
                "enabled": plugin["enabled"],
                "error": plugin.get("error"),
            }
        return None

    def list_plugins(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": pid,
                "name": p["manifest"].name,
                "version": p["manifest"].version,
                "state": p["state"].value,
                "enabled": p["enabled"],
            }
            for pid, p in self._plugins.items()
        ]

    def register_handler(self, extension_point: str, handler: Callable) -> bool:
        if extension_point not in self._handlers:
            return False
        self._handlers[extension_point].append(handler)
        return True

    def invoke_handlers(self, extension_point: str, *args: Any, **kwargs: Any) -> List[Any]:
        results = []
        for handler in self._handlers.get(extension_point, []):
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception as e:
                results.append(e)
        return results

    def get_plugin_settings(self, plugin_id: str) -> Dict[str, Any]:
        return {}

    def set_plugin_setting(self, plugin_id: str, key: str, value: Any) -> None:
        pass
