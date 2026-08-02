"""I STUDIO IDE — Isoko package manager integration.

Search uses the registry client library; install/uninstall run the real Isoko
CLI in the project directory so manifest/lockfile behaviour stays faithful.
"""

from __future__ import annotations

import os
import subprocess
from typing import Any

from . import util


def _parse_dependencies(manifest_text: str) -> dict[str, str]:
    deps: dict[str, str] = {}
    try:
        section = manifest_text.split("[dependencies]", 1)[1].split("[", 1)[0]
    except IndexError:
        return deps
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        deps[key.strip()] = value.strip().strip('"')
    return deps


class IsokoService:
    def __init__(self, project_root: str):
        self.project_root = os.path.abspath(project_root)

    def search(self, query: str, limit: int = 20) -> dict[str, Any]:
        try:
            from isoko.registry import RegistryClient

            results = RegistryClient().search(query, limit=limit)
            return {"results": results, "offline": False, "error": ""}
        except Exception as exc:  # noqa: BLE001 — registry may be unreachable
            return {"results": [], "offline": True, "error": str(exc)}

    def installed(self) -> list[dict[str, str]]:
        manifest_path = os.path.join(self.project_root, "ilang.toml")
        if not os.path.isfile(manifest_path):
            return []
        with open(manifest_path, encoding="utf-8") as f:
            text = f.read()
        return [{"name": name, "version": version} for name, version in _parse_dependencies(text).items()]

    def _run_cli(self, *args: str, timeout: float = 120.0) -> dict[str, Any]:
        try:
            proc = subprocess.run(
                util.child_cmd("isoko", *args),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                cwd=self.project_root,
                env=util.env_with_src(),
            )
        except subprocess.TimeoutExpired:
            return {"ok": False, "output": "", "error": "isoko command timed out"}
        output = (proc.stdout + proc.stderr).strip()
        return {"ok": proc.returncode == 0, "output": output, "error": "" if proc.returncode == 0 else output}

    def install(self, name: str, version: str | None = None) -> dict[str, Any]:
        package = name if not version else f"{name}@{version}"
        return self._run_cli("install", package)

    def uninstall(self, name: str) -> dict[str, Any]:
        return self._run_cli("uninstall", name)

    def update(self, name: str | None = None) -> dict[str, Any]:
        args = ["update"]
        if name:
            args.append(name)
        return self._run_cli("update", *args[1:]) if name else self._run_cli("update")
