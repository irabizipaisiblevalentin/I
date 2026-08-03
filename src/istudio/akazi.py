"""I STUDIO — Workspace & Project Manager (Akazi)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .ibikoreshingiro import (
    IStudioError,
    ProjectConfig,
    ProjectError,
    ProjectTemplate,
    ProjectType,
    PROJECT_TEMPLATES,
    WorkspaceConfig,
)


class AkaziError(IStudioError):
    pass


class ProjectManager:
    def __init__(self, workspace: Optional[WorkspaceManager] = None):
        self._projects: Dict[str, ProjectConfig] = {}
        self._workspace = workspace

    def create_project(
        self,
        name: str,
        path: str,
        project_type: Union[str, ProjectType] = ProjectType.LIBRARY,
        language: str = "i",
    ) -> ProjectConfig:
        if isinstance(project_type, str):
            try:
                project_type = ProjectType(project_type)
            except ValueError:
                project_type = ProjectType.LIBRARY

        template = PROJECT_TEMPLATES.get(project_type, PROJECT_TEMPLATES[ProjectType.LIBRARY])

        cfg = ProjectConfig(
            name=name,
            type=project_type.value,
            project_type=project_type,
            language=language,
            entry_point=template.entry_point,
        )
        project_dir = Path(path) / name
        project_dir.mkdir(parents=True, exist_ok=True)

        for d in template.initial_dirs:
            (project_dir / d).mkdir(parents=True, exist_ok=True)

        for fname, content in template.initial_files.items():
            fp = project_dir / fname
            if not fp.exists():
                fp.parent.mkdir(parents=True, exist_ok=True)
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(content)

        config_path = project_dir / "project.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump({
                "name": name,
                "version": cfg.version,
                "type": cfg.type,
                "project_type": project_type.value,
                "language": cfg.language,
                "entry_point": cfg.entry_point,
                "dependencies": cfg.dependencies,
                "build_config": cfg.build_config,
            }, f, indent=2)
        self._projects[name] = cfg
        if self._workspace:
            self._workspace.add_project(str(project_dir))
        return cfg

    def load_project(self, path: str) -> ProjectConfig:
        config_path = Path(path) / "project.json"
        if not config_path.exists():
            raise ProjectError(f"Project not found: {config_path}")
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        pt_raw = data.get("project_type", data.get("type", "library"))
        try:
            project_type = ProjectType(pt_raw)
        except ValueError:
            project_type = ProjectType.LIBRARY
        cfg = ProjectConfig(
            name=data.get("name", "unnamed"),
            version=data.get("version", "0.1.0"),
            type=data.get("type", "application"),
            project_type=project_type,
            language=data.get("language", "i"),
            entry_point=data.get("entry_point", "main.i"),
            dependencies=data.get("dependencies", {}),
            build_config=data.get("build_config", {}),
        )
        self._projects[cfg.name] = cfg
        return cfg

    def get_project(self, name: str) -> Optional[ProjectConfig]:
        return self._projects.get(name)

    def list_projects(self) -> List[ProjectConfig]:
        return list(self._projects.values())

    def remove_project(self, name: str) -> bool:
        return self._projects.pop(name, None) is not None


class WorkspaceManager:
    def __init__(self, root_path: Optional[str] = None):
        self._config = WorkspaceConfig()
        self._project_manager = ProjectManager(workspace=self)
        if root_path:
            self.load_or_create(root_path)

    @property
    def config(self) -> WorkspaceConfig:
        return self._config

    @property
    def project_manager(self) -> ProjectManager:
        return self._project_manager

    def load_or_create(self, root_path: str) -> WorkspaceConfig:
        root = Path(root_path).resolve()
        root.mkdir(parents=True, exist_ok=True)
        workspace_file = root / ".istudio-workspace"
        if workspace_file.exists():
            return self._load(root_path)
        self._config = WorkspaceConfig(name=root.name, root_path=str(root))
        self._save()
        return self._config

    def _load(self, root_path: str) -> WorkspaceConfig:
        root = Path(root_path).resolve()
        workspace_file = root / ".istudio-workspace"
        if not workspace_file.exists():
            raise AkaziError(f"No workspace found at {root_path}")
        with open(workspace_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._config = WorkspaceConfig(
            name=data.get("name", root.name),
            root_path=str(root),
            projects=data.get("projects", []),
            settings=data.get("settings", {}),
            extensions=data.get("extensions", []),
        )
        return self._config

    def _save(self) -> None:
        root = Path(self._config.root_path)
        workspace_file = root / ".istudio-workspace"
        with open(workspace_file, "w", encoding="utf-8") as f:
            json.dump({
                "name": self._config.name,
                "projects": self._config.projects,
                "settings": self._config.settings,
                "extensions": self._config.extensions,
            }, f, indent=2)

    def add_project(self, project_path: str) -> None:
        if project_path not in self._config.projects:
            self._config.projects.append(project_path)
            self._save()

    def remove_project(self, project_path: str) -> bool:
        if project_path in self._config.projects:
            self._config.projects.remove(project_path)
            self._save()
            return True
        return False

    def update_setting(self, key: str, value: Any) -> None:
        self._config.settings[key] = value
        self._save()

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self._config.settings.get(key, default)

    def install_extension(self, extension_id: str) -> None:
        if extension_id not in self._config.extensions:
            self._config.extensions.append(extension_id)
            self._save()

    def uninstall_extension(self, extension_id: str) -> bool:
        if extension_id in self._config.extensions:
            self._config.extensions.remove(extension_id)
            self._save()
            return True
        return False

    def list_extensions(self) -> List[str]:
        return list(self._config.extensions)

    def get_root_path(self) -> str:
        return self._config.root_path
