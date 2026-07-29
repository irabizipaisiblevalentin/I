"""cache — Package cache management for isoko.

Manages downloaded packages, metadata, and build artifacts.
Provides efficient cache operations with integrity verification.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from typing import Any, Dict, List, Optional, Tuple

from isoko import security
from isoko.semver import Version


# ---------------------------------------------------------------------------
# Cache configuration
# ---------------------------------------------------------------------------

class CacheConfig:
    """Cache directory configuration."""

    def __init__(self, cache_dir: str = "") -> None:
        self.cache_dir = cache_dir or os.path.join(
            os.path.expanduser("~"), ".isoko", "cache"
        )

    @property
    def packages_dir(self) -> str:
        return os.path.join(self.cache_dir, "packages")

    @property
    def metadata_dir(self) -> str:
        return os.path.join(self.cache_dir, "metadata")

    @property
    def tarballs_dir(self) -> str:
        return os.path.join(self.cache_dir, "tarballs")

    @property
    def git_dir(self) -> str:
        return os.path.join(self.cache_dir, "git")

    @property
    def index_path(self) -> str:
        return os.path.join(self.cache_dir, "index.json")

    def ensure_dirs(self) -> None:
        for d in [self.packages_dir, self.metadata_dir,
                  self.tarballs_dir, self.git_dir]:
            os.makedirs(d, exist_ok=True)


# ---------------------------------------------------------------------------
# Cache entry
# ---------------------------------------------------------------------------

class CacheEntry:
    """Metadata for a cached package."""

    __slots__ = ("name", "version", "checksum", "size", "cached_at", "source")

    def __init__(self, name: str = "", version: str = "",
                 checksum: str = "", size: int = 0,
                 cached_at: float = 0.0, source: str = "registry") -> None:
        self.name = name
        self.version = version
        self.checksum = checksum
        self.size = size
        self.cached_at = cached_at or time.time()
        self.source = source

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "checksum": self.checksum,
            "size": self.size,
            "cached_at": self.cached_at,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CacheEntry:
        return cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            checksum=data.get("checksum", ""),
            size=data.get("size", 0),
            cached_at=data.get("cached_at", 0.0),
            source=data.get("source", "registry"),
        )


# ---------------------------------------------------------------------------
# Package cache
# ---------------------------------------------------------------------------

class PackageCache:
    """Manages the local package cache."""

    def __init__(self, config: Optional[CacheConfig] = None) -> None:
        self._config = config or CacheConfig()
        self._index: Dict[str, CacheEntry] = {}
        self._loaded = False

    @property
    def config(self) -> CacheConfig:
        return self._config

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._config.ensure_dirs()
        self._load_index()
        self._loaded = True

    def _load_index(self) -> None:
        path = self._config.index_path
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for key, entry_data in data.items():
                    self._index[key] = CacheEntry.from_dict(entry_data)
            except (json.JSONDecodeError, OSError):
                pass

    def _save_index(self) -> None:
        data = {key: entry.to_dict() for key, entry in self._index.items()}
        with open(self._config.index_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _key(self, name: str, version: str) -> str:
        return f"{name}@{version}"

    def has(self, name: str, version: str) -> bool:
        self._ensure_loaded()
        key = self._key(name, version)
        if key not in self._index:
            return False
        pkg_dir = os.path.join(self._config.packages_dir, name, version)
        return os.path.isdir(pkg_dir)

    def get(self, name: str, version: str) -> Optional[str]:
        self._ensure_loaded()
        pkg_dir = os.path.join(self._config.packages_dir, name, version)
        if os.path.isdir(pkg_dir):
            return pkg_dir
        return None

    def put(self, name: str, version: str, source_dir: str,
            checksum: str = "") -> str:
        self._ensure_loaded()
        pkg_dir = os.path.join(self._config.packages_dir, name, version)
        if os.path.exists(pkg_dir):
            shutil.rmtree(pkg_dir)
        shutil.copytree(source_dir, pkg_dir)

        size = sum(
            os.path.getsize(os.path.join(dp, f))
            for dp, _, fnames in os.walk(pkg_dir)
            for f in fnames
        )

        if not checksum:
            checksum = self._dir_checksum(pkg_dir)

        entry = CacheEntry(
            name=name,
            version=version,
            checksum=checksum,
            size=size,
            source="registry",
        )
        key = self._key(name, version)
        self._index[key] = entry
        self._save_index()
        return pkg_dir

    def put_tarball(self, name: str, version: str, data: bytes) -> str:
        self._ensure_loaded()
        path = os.path.join(self._config.tarballs_dir, f"{name}-{version}.tgz")
        with open(path, "wb") as f:
            f.write(data)
        return path

    def get_tarball(self, name: str, version: str) -> Optional[bytes]:
        self._ensure_loaded()
        path = os.path.join(self._config.tarballs_dir, f"{name}-{version}.tgz")
        if os.path.exists(path):
            with open(path, "rb") as f:
                return f.read()
        return None

    def put_metadata(self, name: str, metadata: Dict[str, Any]) -> None:
        self._ensure_loaded()
        path = os.path.join(self._config.metadata_dir, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def get_metadata(self, name: str) -> Optional[Dict[str, Any]]:
        self._ensure_loaded()
        path = os.path.join(self._config.metadata_dir, f"{name}.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return None

    def remove(self, name: str, version: str) -> bool:
        self._ensure_loaded()
        key = self._key(name, version)
        if key not in self._index:
            return False
        pkg_dir = os.path.join(self._config.packages_dir, name, version)
        if os.path.exists(pkg_dir):
            shutil.rmtree(pkg_dir)
        del self._index[key]
        self._save_index()
        return True

    def clear(self) -> int:
        self._ensure_loaded()
        count = len(self._index)
        if os.path.exists(self._config.packages_dir):
            shutil.rmtree(self._config.packages_dir)
        if os.path.exists(self._config.tarballs_dir):
            shutil.rmtree(self._config.tarballs_dir)
        if os.path.exists(self._config.metadata_dir):
            shutil.rmtree(self._config.metadata_dir)
        self._index.clear()
        self._config.ensure_dirs()
        self._save_index()
        return count

    def cleanup(self, max_age_days: int = 90) -> int:
        self._ensure_loaded()
        cutoff = time.time() - (max_age_days * 86400)
        removed = 0
        to_remove = []
        for key, entry in self._index.items():
            if entry.cached_at < cutoff:
                to_remove.append(key)
        for key in to_remove:
            entry = self._index[key]
            pkg_dir = os.path.join(
                self._config.packages_dir, entry.name, entry.version
            )
            if os.path.exists(pkg_dir):
                shutil.rmtree(pkg_dir)
            del self._index[key]
            removed += 1
        if removed:
            self._save_index()
        return removed

    def stats(self) -> Dict[str, Any]:
        self._ensure_loaded()
        total_size = sum(e.size for e in self._index.values())
        return {
            "total_packages": len(self._index),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "cache_dir": self._config.cache_dir,
        }

    def list_packages(self) -> List[CacheEntry]:
        self._ensure_loaded()
        return list(self._index.values())

    def _dir_checksum(self, dirpath: str) -> str:
        h = hashlib.sha256()
        for dp, _, fnames in sorted(os.walk(dirpath)):
            for fn in sorted(fnames):
                fp = os.path.join(dp, fn)
                rel = os.path.relpath(fp, dirpath)
                h.update(rel.encode("utf-8"))
                with open(fp, "rb") as f:
                    while chunk := f.read(8192):
                        h.update(chunk)
        return h.hexdigest()


# ---------------------------------------------------------------------------
# Verify cached package integrity
# ---------------------------------------------------------------------------

def verify_cached(cache: PackageCache, name: str, version: str) -> bool:
    """Verify a cached package matches its expected checksum."""
    entry = cache._index.get(cache._key(name, version))
    if entry is None:
        return False
    pkg_dir = cache.get(name, version)
    if pkg_dir is None:
        return False
    actual = cache._dir_checksum(pkg_dir)
    return actual == entry.checksum
