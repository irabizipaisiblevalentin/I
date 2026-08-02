"""I Studio IDE — Extensions API.

Extensions are installed as folders under ``<ISTUDIO_HOME>/extensions``, each
described by an ``extension.json`` manifest. The developer-platform package
registry (``isoko.ideveloper.ububiko``) provides the installable catalogue.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any


def _extensions_dir() -> str:
    return os.path.join(
        os.environ.get("ISTUDIO_HOME", str(Path.home() / ".istudio")),
        "extensions",
    )


class ExtensionsService:
    def __init__(self, base_dir: str = "") -> None:
        self._dir = base_dir or _extensions_dir()

    def list_installed(self) -> list[dict[str, Any]]:
        if not os.path.isdir(self._dir):
            return []
        installed = []
        for name in sorted(os.listdir(self._dir)):
            entry = os.path.join(self._dir, name)
            if not os.path.isdir(entry):
                continue
            manifest = self._read_manifest(name)
            if manifest is None:
                continue
            installed.append({
                "name": name,
                "version": manifest.get("version", "0.0.0"),
                "description": manifest.get("description", ""),
                "author": manifest.get("author", ""),
                "path": entry,
            })
        return installed

    def browse(self, query: str = "") -> list[dict[str, Any]]:
        """List installable extensions from the developer-platform registry."""
        try:
            from isoko.ideveloper.ububiko import PackageRegistry
        except ImportError:
            return []
        q = (query or "").lower()
        results = []
        for pkg in PackageRegistry().search(q):
            if not pkg["name"]:
                continue
            results.append({
                "name": pkg["name"],
                "version": pkg["version"],
                "description": pkg["description"],
                "author": pkg["author"],
                "installed": os.path.isdir(os.path.join(self._dir, pkg["name"])),
            })
        return results

    def install(self, name: str, version: str = "") -> dict[str, Any] | None:
        """Install an extension from the developer-platform registry."""
        if not name or name in {".", ".."}:
            return None
        try:
            from isoko.ideveloper.ububiko import PackageRegistry
        except ImportError:
            return None
        pkg = PackageRegistry().get_package(name)
        if pkg is None:
            return None
        target_version = version or pkg.version
        target = os.path.join(self._dir, name)
        os.makedirs(target, exist_ok=True)
        manifest = {
            "name": name,
            "version": target_version,
            "description": pkg.description,
            "author": pkg.author_name,
        }
        manifest_path = os.path.join(target, "extension.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        return manifest

    def uninstall(self, name: str) -> bool:
        target = os.path.join(self._dir, name)
        if not os.path.isdir(target) or os.path.basename(target) in {".", ".."}:
            return False
        shutil.rmtree(target)
        return True

    def _read_manifest(self, name: str) -> dict[str, Any] | None:
        path = os.path.join(self._dir, name, "extension.json")
        try:
            with open(path, encoding="utf-8-sig") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return None
        if not isinstance(data, dict) or not data.get("name"):
            return None
        return data
