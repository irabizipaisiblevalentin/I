"""I Developer Platform — Package Registry (Ububiko)."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

from .ibikoreshingiro import (
    PackageRelease,
    PackageStats,
    PackageVersion,
    PackageVisibility,
)


class PackageRegistry:
    def __init__(self):
        self._packages: Dict[str, PackageRelease] = {}
        self._versions: Dict[str, List[PackageVersion]] = {}
        self._stats: Dict[str, PackageStats] = {}
        self._verified_publishers: set = set()

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
                return True
        return False

    def record_download(self, name: str, version: str = "") -> None:
        if name in self._stats:
            self._stats[name].total_downloads += 1
            self._stats[name].recent_downloads += 1
        for v in self._versions.get(name, []):
            if not version or v.version == version:
                v.downloads += 1

    def get_stats(self, name: str) -> Optional[PackageStats]:
        return self._stats.get(name)

    def verify_publisher(self, author_id: str) -> None:
        self._verified_publishers.add(author_id)

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
            "downloads": stats.total_downloads,
            "recent_downloads": stats.recent_downloads,
            "score": stats.score,
            "dependents": stats.dependents,
            "stars": stats.stars,
        }
