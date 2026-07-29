"""I STUDIO — Common Utilities (Ibikoresho Rusange)."""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


def generate_id(prefix: str = "") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

def timestamp() -> float:
    return time.time()

def format_timestamp(ts: float, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    import datetime
    return datetime.datetime.fromtimestamp(ts).strftime(fmt)

def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def safe_filename(name: str) -> str:
    return re.sub(r'[^\w\-\. ]', '_', name)

def ensure_dir(path: str) -> str:
    Path(path).mkdir(parents=True, exist_ok=True)
    return path

def read_json(path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def write_json(path: str, data: Any, indent: int = 2) -> None:
    ensure_dir(str(Path(path).parent))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)

def search_files(root: str, pattern: str, include_hidden: bool = False) -> List[str]:
    results = []
    for root_dir, dirs, files in os.walk(root):
        if not include_hidden:
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            files = [f for f in files if not f.startswith(".")]
        for f in files:
            if re.search(pattern, f, re.IGNORECASE):
                results.append(os.path.join(root_dir, f))
    return results

def find_text_in_files(root: str, query: str, include: str = "*.i") -> List[Dict[str, Any]]:
    results = []
    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for f in files:
            if not f.endswith(include.replace("*", "")):
                continue
            filepath = os.path.join(root_dir, f)
            try:
                with open(filepath, "r", encoding="utf-8") as fh:
                    for line_idx, line in enumerate(fh, 1):
                        if query in line:
                            results.append({
                                "file": filepath,
                                "line": line_idx,
                                "content": line.rstrip(),
                                "column": line.index(query),
                            })
            except (UnicodeDecodeError, IOError):
                continue
    return results

def diff_strings(old: str, new: str) -> List[Dict[str, Any]]:
    old_lines = old.split("\n")
    new_lines = new.split("\n")
    import difflib
    diff = list(difflib.unified_diff(old_lines, new_lines, lineterm=""))
    changes = []
    for line in diff:
        if line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
            continue
        changes.append({
            "type": "added" if line.startswith("+") else "removed" if line.startswith("-") else "context",
            "content": line[1:] if line else line,
        })
    return changes

def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    return result

def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def tokenize(text: str) -> List[str]:
    return re.findall(r'\w+|[^\w\s]', text)


class LRUCache:
    def __init__(self, max_size: int = 100):
        self._max_size = max_size
        self._cache: Dict[str, Any] = {}
        self._order: List[str] = []

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            self._order.remove(key)
            self._order.append(key)
            return self._cache[key]
        return None

    def put(self, key: str, value: Any) -> None:
        if key in self._cache:
            self._order.remove(key)
        elif len(self._cache) >= self._max_size:
            oldest = self._order.pop(0)
            del self._cache[oldest]
        self._cache[key] = value
        self._order.append(key)

    def remove(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            self._order.remove(key)
            return True
        return False

    def clear(self) -> None:
        self._cache.clear()
        self._order.clear()

    def size(self) -> int:
        return len(self._cache)


class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[callable]] = {}

    def on(self, event: str, handler: callable) -> None:
        self._listeners.setdefault(event, []).append(handler)

    def off(self, event: str, handler: callable) -> None:
        handlers = self._listeners.get(event, [])
        if handler in handlers:
            handlers.remove(handler)

    def emit(self, event: str, *args: Any, **kwargs: Any) -> List[Any]:
        results = []
        for handler in self._listeners.get(event, []):
            try:
                results.append(handler(*args, **kwargs))
            except Exception:
                pass
        return results

    def clear(self) -> None:
        self._listeners.clear()
