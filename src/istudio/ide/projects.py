"""I STUDIO IDE — project workspace service.

Manages projects under a base directory: create from template, list, file tree,
and read/write/delete/rename files. All file paths are validated against
traversal outside the project root.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

from . import templates
from .util import safe_join, walk_tree


class ProjectError(Exception):
    pass


class ProjectService:
    def __init__(self, base_dir: str, state_path: str | None = None):
        self.base_dir = os.path.abspath(os.path.expanduser(base_dir))
        self.state_path = state_path or os.path.join(
            os.environ.get("ISTUDIO_HOME", str(Path.home() / ".istudio")),
            "projects.json",
        )
        self._recent: list[str] = []
        os.makedirs(self.base_dir, exist_ok=True)
        self._load_state()

    # ── state (recent projects) ─────────────────────────────────────────

    def _load_state(self) -> None:
        try:
            with open(self.state_path, encoding="utf-8") as f:
                data = json.load(f)
            self._recent = [p for p in data.get("recent", []) if os.path.isdir(p)]
        except (OSError, ValueError):
            self._recent = []

    def _save_state(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump({"recent": self._recent}, f, indent=2)
        except OSError:
            pass

    def recent(self) -> list[str]:
        return list(self._recent)

    def current(self) -> dict[str, Any] | None:
        """Return the most recently opened project, or None if none yet."""
        for path in self._recent:
            if os.path.isdir(path):
                return self._project_info(path)
        return None

    # ── projects ────────────────────────────────────────────────────────

    def create_from_upload(self, name: str, files: dict[str, str]) -> dict[str, Any]:
        """Create a fresh project containing exactly the uploaded files."""
        if not name or not name.replace("-", "_").replace("_", "").isalnum():
            raise ProjectError(f"invalid project name: {name!r}")
        root = os.path.abspath(os.path.join(self.base_dir, name))
        if os.path.exists(root):
            raise ProjectError(f"destination already exists: {root}")
        os.makedirs(root, exist_ok=True)
        self._write_files(root, files)
        if root not in self._recent:
            self._recent.insert(0, root)
            self._recent = self._recent[:12]
            self._save_state()
        return {"name": name, "path": root, "template": "imported"}

    def replace_with(self, root: str, files: dict[str, str]) -> list[str]:
        """Replace a project's contents with the uploaded files.

        Removes every existing file/folder under ``root`` first, then writes
        the uploaded files. Used by "Import Folder" to drop template files.
        """
        root = os.path.abspath(root)
        if not os.path.isdir(root):
            raise ProjectError(f"not a directory: {root}")
        if root == os.path.normpath(self.base_dir):
            raise ProjectError("refusing to clear the projects base directory")
        for entry in os.listdir(root):
            target = os.path.join(root, entry)
            if os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)
        return self._write_files(root, files)

    def _write_files(self, root: str, files: dict[str, str]) -> list[str]:
        written: list[str] = []
        for rel in sorted(files):
            target = self._resolve(root, rel)
            if target is None:
                raise ProjectError(f"unsafe path: {rel}")
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8", newline="\n") as f:
                f.write(str(files[rel]))
            written.append(rel)
        return written

    def create_from_folder(self, name: str, source: str) -> dict[str, Any]:
        """Create a fresh project by copying an existing folder (structure kept)."""
        if not name or not name.replace("-", "_").replace("_", "").isalnum():
            raise ProjectError(f"invalid project name: {name!r}")
        source = os.path.abspath(os.path.expanduser(source))
        if not os.path.isdir(source):
            raise ProjectError(f"not a folder: {source}")
        root = os.path.abspath(os.path.join(self.base_dir, name))
        if os.path.exists(root):
            raise ProjectError(f"destination already exists: {root}")
        os.makedirs(root, exist_ok=True)
        self._copy_tree(source, root)
        if root not in self._recent:
            self._recent.insert(0, root)
            self._recent = self._recent[:12]
            self._save_state()
        return {"name": name, "path": root, "template": "imported"}

    def replace_from_folder(self, root: str, source: str) -> list[str]:
        """Replace a project's contents by copying an existing folder.

        Removes every existing file/folder under ``root`` first, then copies the
        source folder's contents (structure preserved). Used by desktop
        "Import Folder".
        """
        root = os.path.abspath(root)
        source = os.path.abspath(os.path.expanduser(source))
        if not os.path.isdir(root):
            raise ProjectError(f"not a directory: {root}")
        if not os.path.isdir(source):
            raise ProjectError(f"not a folder: {source}")
        if root == os.path.normpath(self.base_dir):
            raise ProjectError("refusing to clear the projects base directory")
        root_norm = os.path.normcase(os.path.normpath(root))
        src_norm = os.path.normcase(os.path.normpath(source))
        if src_norm == root_norm:
            raise ProjectError("source and destination are the same folder")
        if src_norm.startswith(root_norm + os.sep):
            raise ProjectError("source folder cannot be inside the destination")
        for entry in os.listdir(root):
            target = os.path.join(root, entry)
            if os.path.isdir(target):
                shutil.rmtree(target)
            else:
                os.remove(target)
        return self._copy_tree(source, root)

    def _copy_tree(self, source: str, dest: str) -> list[str]:
        written: list[str] = []
        for dirpath, dirnames, filenames in os.walk(source):
            dirnames[:] = [
                d for d in dirnames if d not in {".git", "node_modules", "__pycache__", ".istudio", "dist", "build"}
            ]
            for name in filenames:
                src_file = os.path.join(dirpath, name)
                rel = os.path.relpath(src_file, source)
                target = self._resolve(dest, rel)
                if target is None:
                    raise ProjectError(f"unsafe path: {rel}")
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copy2(src_file, target)
                written.append(rel.replace(os.sep, "/"))
        return written

    def create(self, name: str, template: str, path: str | None = None) -> dict[str, Any]:
        if not name or not name.replace("-", "_").replace("_", "").isalnum():
            raise ProjectError(f"invalid project name: {name!r}")
        files = templates.template_files(template)
        root = os.path.abspath(path or os.path.join(self.base_dir, name))
        if os.path.exists(root):
            raise ProjectError(f"destination already exists: {root}")
        os.makedirs(os.path.join(root, "src"), exist_ok=True)
        for rel, content in files.items():
            target = safe_join(root, *rel.split("/"))
            if target is None:
                raise ProjectError(f"unsafe template path: {rel}")
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
        if root not in self._recent:
            self._recent.insert(0, root)
            self._recent = self._recent[:12]
            self._save_state()
        return {"name": name, "path": root, "template": template}

    def list_projects(self) -> list[dict[str, Any]]:
        """Projects = directories under base_dir containing an ilang.toml."""
        results: list[dict[str, Any]] = []
        try:
            names = sorted(os.listdir(self.base_dir))
        except OSError:
            names = []
        for entry in names:
            path = os.path.join(self.base_dir, entry)
            if os.path.isdir(path) and os.path.isfile(os.path.join(path, "ilang.toml")):
                results.append(self._project_info(path))
        return results

    def open_project(self, path: str) -> dict[str, Any]:
        root = os.path.abspath(os.path.expanduser(path))
        if not os.path.isdir(root):
            raise ProjectError(f"not a directory: {root}")
        if root not in self._recent:
            self._recent.insert(0, root)
            self._recent = self._recent[:12]
            self._save_state()
        return self._project_info(root)

    def _project_info(self, root: str) -> dict[str, Any]:
        manifest: dict[str, Any] = {}
        manifest_path = os.path.join(root, "ilang.toml")
        try:
            with open(manifest_path, encoding="utf-8") as f:
                text = f.read()
            if "[package]" in text:
                pkg = text.split("[package]", 1)[1].split("[", 1)[0]
                for line in pkg.splitlines():
                    if "=" in line and not line.strip().startswith("#"):
                        key, _, value = line.partition("=")
                        manifest[key.strip()] = value.strip().strip('"')
        except OSError:
            pass
        return {
            "name": manifest.get("name", os.path.basename(root)),
            "path": root,
            "template": "custom",
            "description": manifest.get("description", ""),
        }

    # ── files ───────────────────────────────────────────────────────────

    def _resolve(self, root: str, rel: str) -> str:
        target = safe_join(root, rel)
        if target is None:
            raise ProjectError("path escapes project root")
        return target

    def file_tree(self, root: str) -> list[dict[str, Any]]:
        return walk_tree(root)

    def read_file(self, root: str, rel: str) -> str:
        target = self._resolve(root, rel)
        if not os.path.isfile(target):
            raise ProjectError(f"not a file: {rel}")
        with open(target, encoding="utf-8") as f:
            return f.read()

    def write_file(self, root: str, rel: str, content: str) -> None:
        target = self._resolve(root, rel)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)

    def delete_path(self, root: str, rel: str) -> None:
        target = self._resolve(root, rel)
        if target == os.path.normpath(root):
            raise ProjectError("cannot delete project root")
        if os.path.isdir(target):
            shutil.rmtree(target)
        elif os.path.exists(target):
            os.remove(target)
        else:
            raise ProjectError(f"not found: {rel}")

    def rename_path(self, root: str, rel: str, new_name: str) -> None:
        target = self._resolve(root, rel)
        if not os.path.exists(target):
            raise ProjectError(f"not found: {rel}")
        new_path = os.path.join(os.path.dirname(target), new_name)
        if os.path.exists(new_path):
            raise ProjectError(f"destination exists: {new_name}")
        os.rename(target, new_path)
