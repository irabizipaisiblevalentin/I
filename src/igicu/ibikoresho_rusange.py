"""IGICU — Common utilities, helpers, and shared infrastructure."""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


class IgicuConfig:
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = config_dir or os.path.join(
            os.path.expanduser("~"), ".igicu"
        )
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        dirs = ["clusters", "registry", "logs", "audit", "secrets", "certs", "config"]
        for d in dirs:
            Path(self.config_dir, d).mkdir(parents=True, exist_ok=True)

    def get_path(self, *parts: str) -> str:
        return str(Path(self.config_dir, *parts))

    def get_version(self) -> str:
        return "0.1.0"


class TimeHelpers:
    @staticmethod
    def now() -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def timestamp() -> float:
        return time.time()

    @staticmethod
    def format_duration(seconds: float) -> str:
        if seconds < 60:
            return f"{seconds:.1f}s"
        if seconds < 3600:
            return f"{seconds / 60:.1f}m"
        if seconds < 86400:
            return f"{seconds / 3600:.1f}h"
        return f"{seconds / 86400:.1f}d"


class Serialization:
    @staticmethod
    def to_json(data: Any) -> str:
        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def from_json(text: str) -> Any:
        return json.loads(text)

    @staticmethod
    def to_json_file(data: Any, path: str) -> None:
        Path(path).write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    @staticmethod
    def from_json_file(path: str) -> Any:
        return json.loads(Path(path).read_text(encoding="utf-8"))


class IdGenerator:
    @staticmethod
    def generate(prefix: str = "igicu") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:12]}"

    @staticmethod
    def short_id() -> str:
        return uuid.uuid4().hex[:8]


class StatusTracker:
    def __init__(self):
        self._status: Dict[str, str] = {}
        self._history: List[Dict[str, Any]] = []

    def set(self, key: str, status: str) -> None:
        old_status = self._status.get(key)
        self._status[key] = status
        self._history.append({
            "key": key,
            "from": old_status,
            "to": status,
            "timestamp": TimeHelpers.now(),
        })

    def get(self, key: str) -> Optional[str]:
        return self._status.get(key)

    def history(self, key: Optional[str] = None) -> List[Dict[str, Any]]:
        if key:
            return [h for h in self._history if h["key"] == key]
        return self._history
