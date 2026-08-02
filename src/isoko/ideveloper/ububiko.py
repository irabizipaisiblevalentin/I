"""I Developer Platform — Package Registry (Ububiko)."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Set

from .ibikoreshingiro import (
    PackageRelease,
    PackageStats,
    PackageVersion,
    PackageVisibility,
)


def _registry_path() -> str:
    return os.path.join(
        os.environ.get("ISOKO_HOME", os.path.join(os.path.expanduser("~"), ".isoko")),
        "registry.json",
    )


class PackageRegistry:
    def __init__(self):
        self._packages: Dict[str, PackageRelease] = {}
        self._versions: Dict[str, List[PackageVersion]] = {}
        self._stats: Dict[str, PackageStats] = {}
        self._verified_publishers: Set[str] = set()
        self._path = _registry_path()
        self._load()

    def publish(self, release: PackageRelease) -> str:
        pkg_id = f"{release.name}@{release.version}"
        if release.name in self._packages and not self._packages[release.name].verified:
            pass
        self._packages[release.name] = release
        pv = PackageVersion(
            package_name=release.name,
            version=release.version,
            published_at="",
            checksum=hashlib.sha256(json.dumps({
                "name": release.name, "version": release.version,
                "description": release.description,
            }, sort_keys=True).encode()).hexdigest(),
        )
        self._versions.setdefault(release.name, []).append(pv)

        if release.name not in self._stats:
            self._stats[release.name] = PackageStats(name=release.name)
        self._stats[release.name].versions_count = len(self._versions[release.name])
        self._save()
        return pkg_id

    def get_package(self, name: str) -> Optional[PackageRelease]:
        return self._packages.get(name)

    def get_version(self, name: str, version: str) -> Optional[PackageVersion]:
        for v in self._versions.get(name, []):
            if v.version == version:
                return v
        return None

    def search(self, query: str) -> List[Dict[str, Any]]:
        q = query.lower()
        results = []
        for name, pkg in self._packages.items():
            if q in name.lower() or q in pkg.description.lower():
                stats = self._stats.get(name)
                results.append({
                    "name": name,
                    "version": pkg.version,
                    "description": pkg.description,
                    "author": pkg.author_name,
                    "downloads": stats.total_downloads if stats else 0,
                    "score": stats.score if stats else 0.0,
                    "verified": pkg.verified,
                })
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def yank_version(self, name: str, version: str, reason: str = "") -> bool:
        for v in self._versions.get(name, []):
            if v.version == version:
                v.yanked = True
                v.deprecation_message = reason
                self._save()
                return True
        return False

    def record_download(self, name: str, version: str = "") -> None:
        if name in self._stats:
            self._stats[name].total_downloads += 1
            self._stats[name].recent_downloads += 1
        for v in self._versions.get(name, []):
            if not version or v.version == version:
                v.downloads += 1
        self._save()

    def get_stats(self, name: str) -> Optional[PackageStats]:
        return self._stats.get(name)

    def verify_publisher(self, author_id: str) -> None:
        self._verified_publishers.add(author_id)
        self._save()

    def is_verified_publisher(self, author_id: str) -> bool:
        return author_id in self._verified_publishers

    def list_packages(self, visibility: Optional[PackageVisibility] = None) -> List[str]:
        if visibility:
            return [n for n, p in self._packages.items() if p.visibility == visibility]
        return list(self._packages.keys())

    def get_dependency_graph(self, name: str) -> Dict[str, List[str]]:
        graph: Dict[str, List[str]] = {}
        pkg = self._packages.get(name)
        if pkg:
            graph[name] = list(pkg.dependencies.keys())
            for dep in pkg.dependencies:
                if dep in self._packages:
                    graph[dep] = list(self._packages[dep].dependencies.keys())
        return graph

    def get_popularity(self, name: str) -> Dict[str, Any]:
        stats = self._stats.get(name)
        if not stats:
            return {"error": "Package not found"}
        return {
            "name": stats.name,
            "total_downloads": stats.total_downloads,
            "recent_downloads": stats.recent_downloads,
            "stars": stats.stars,
            "forks": stats.forks,
            "score": stats.score,
        }

    # -- persistence -------------------------------------------------------

    def _load(self) -> None:
        if not self._path or not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return
        for name, raw in (data.get("packages") or {}).items():
            self._packages[name] = _from_dict(PackageRelease, raw)
        for name, raws in (data.get("versions") or {}).items():
            self._versions[name] = [_from_dict(PackageVersion, r) for r in raws]
        for name, raw in (data.get("stats") or {}).items():
            self._stats[name] = _from_dict(PackageStats, raw)
        self._verified_publishers = set(data.get("verified_publishers") or [])

    def _save(self) -> None:
        if not self._path:
            return
        try:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            data = {
                "packages": {n: _to_dict(p) for n, p in self._packages.items()},
                "versions": {n: [_to_dict(v) for v in vs] for n, vs in self._versions.items()},
                "stats": {n: _to_dict(s) for n, s in self._stats.items()},
                "verified_publishers": sorted(self._verified_publishers),
            }
            tmp = self._path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, self._path)
        except OSError:
            pass


def _to_dict(obj: Any) -> Dict[str, Any]:
    import enum as _enum

    def convert(value: Any) -> Any:
        if dataclasses.is_dataclass(value) and not isinstance(value, type):
            return _to_dict(value)
        if isinstance(value, _enum.Enum):
            return value.value
        if isinstance(value, list):
            return [convert(v) for v in value]
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        return value

    return {key: convert(value) for key, value in dataclasses.asdict(obj).items()}


def _from_dict(cls: Any, raw: Dict[str, Any]) -> Any:
    fields = {f.name: f.type for f in dataclasses.fields(cls)}
    kwargs: Dict[str, Any] = {}
    for key, value in raw.items():
        if key not in fields:
            continue
        field_type = fields[key]
        if isinstance(value, list) and hasattr(field_type, "__origin__") and field_type.__origin__ is list:
            kwargs[key] = value
        elif isinstance(value, dict) and hasattr(field_type, "__origin__") and field_type.__origin__ is dict:
            kwargs[key] = value
        else:
            kwargs[key] = value
    # restore enum fields
    if cls is PackageRelease and "visibility" in kwargs:
        try:
            kwargs["visibility"] = PackageVisibility(kwargs["visibility"])
        except ValueError:
            kwargs["visibility"] = PackageVisibility.PUBLIC
    try:
        return cls(**kwargs)
    except TypeError:
        return cls()
