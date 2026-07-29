"""registry — Package registry client for isoko.

Supports official, private, and local registries with offline fallback.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

from isoko.semver import Version


class RegistryConfig:
    """Registry configuration."""
    __slots__ = ("url", "token", "offline", "cache_dir", "timeout")

    def __init__(self, url: str = "https://registry.i-lang.dev",
                 token: str = "", offline: bool = False,
                 cache_dir: str = "", timeout: int = 30) -> None:
        self.url = url.rstrip("/")
        self.token = token
        self.offline = offline
        self.cache_dir = cache_dir or os.path.join(
            os.path.expanduser("~"), ".isoko", "cache"
        )
        self.timeout = timeout


class RegistryClient:
    """Client for interacting with package registries."""

    def __init__(self, config: Optional[RegistryConfig] = None) -> None:
        self._config = config or RegistryConfig()
        self._cache: Dict[str, Any] = {}
        self._meta_cache: Dict[str, Dict] = {}

    def get_versions(self, name: str) -> List[Version]:
        """Get all available versions of a package."""
        meta = self._get_metadata(name)
        if meta is None:
            return []
        versions = []
        for v_str in meta.get("versions", {}).keys():
            v = Version.try_parse(v_str)
            if v is not None:
                versions.append(v)
        return sorted(versions)

    def get_package(self, name: str, version: str) -> Optional[Dict]:
        """Get full package metadata for a specific version."""
        meta = self._get_metadata(name)
        if meta is None:
            return None
        return meta.get("versions", {}).get(version)

    def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Search for packages."""
        try:
            data = self._request(f"/-/search?q={query}&limit={limit}")
            return data.get("results", [])
        except RegistryError:
            return []

    def download(self, name: str, version: str) -> Optional[bytes]:
        """Download a package tarball."""
        cache_path = self._tarball_path(name, version)
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                return f.read()

        try:
            data = self._request(f"/{name}/-/download/{name}-{version}.tgz")
            if isinstance(data, bytes):
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                with open(cache_path, "wb") as f:
                    f.write(data)
                return data
        except RegistryError:
            pass
        return None

    def publish(self, name: str, version: str, tarball: bytes,
                metadata: Optional[Dict] = None) -> bool:
        """Publish a package to the registry."""
        try:
            payload = {
                "name": name,
                "version": version,
                "metadata": metadata or {},
                "tarball": tarball.hex(),
            }
            self._request(f"/{name}", method="POST", data=payload)
            return True
        except RegistryError:
            return False

    def yank(self, name: str, version: str, reason: str = "") -> bool:
        """Yank a package version."""
        try:
            self._request(f"/{name}/{version}/yank", method="POST",
                          data={"reason": reason})
            return True
        except RegistryError:
            return False

    def _get_metadata(self, name: str) -> Optional[Dict]:
        """Get package metadata with caching."""
        if name in self._meta_cache:
            return self._meta_cache[name]

        if self._config.offline:
            return self._load_cached_metadata(name)

        try:
            meta = self._request(f"/{name}")
            self._meta_cache[name] = meta
            self._save_cached_metadata(name, meta)
            return meta
        except RegistryError:
            return self._load_cached_metadata(name)

    def _load_cached_metadata(self, name: str) -> Optional[Dict]:
        cache_path = os.path.join(self._config.cache_dir, "metadata", f"{name}.json")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def _save_cached_metadata(self, name: str, meta: Dict) -> None:
        cache_path = os.path.join(self._config.cache_dir, "metadata", f"{name}.json")
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    def _tarball_path(self, name: str, version: str) -> str:
        return os.path.join(self._config.cache_dir, "tarballs", f"{name}-{version}.tgz")

    def _request(self, path: str, method: str = "GET",
                 data: Optional[Dict] = None) -> Any:
        """Make an HTTP request to the registry."""
        url = f"{self._config.url}{path}"
        headers = {"Accept": "application/json"}
        if self._config.token:
            headers["Authorization"] = f"Bearer {self._config.token}"

        body = None
        if data is not None:
            body = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = Request(url, data=body, headers=headers, method=method)
        try:
            resp = urlopen(req, timeout=self._config.timeout)
            content = resp.read()
            content_type = resp.headers.get("Content-Type", "")
            if "json" in content_type:
                return json.loads(content)
            return content
        except URLError as e:
            raise RegistryError(f"registry request failed: {e}") from e


class RegistryError(Exception):
    """Error communicating with the registry."""
    pass
