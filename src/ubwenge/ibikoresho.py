from __future__ import annotations

import hashlib
import importlib
import json
import os
import time
import uuid
from collections import OrderedDict
from datetime import datetime
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Type, Union
from pathlib import Path


class UwagaRegistry:
    _models: Dict[str, Dict[str, Any]] = {}
    _pipelines: Dict[str, List[Dict[str, Any]]] = {}
    _hooks: Dict[str, List[Callable]] = {}

    @classmethod
    def register_model(cls, model_id: str, metadata: Dict[str, Any]) -> None:
        cls._models[model_id] = {**metadata, "registered_at": datetime.utcnow().isoformat()}

    @classmethod
    def get_model(cls, model_id: str) -> Optional[Dict[str, Any]]:
        return cls._models.get(model_id)

    @classmethod
    def list_models(cls, filter_tags: Optional[List[str]] = None) -> List[str]:
        if not filter_tags:
            return list(cls._models.keys())
        result = []
        for mid, meta in cls._models.items():
            tags = meta.get("tags", [])
            if any(t in tags for t in filter_tags):
                result.append(mid)
        return result

    @classmethod
    def register_pipeline(cls, name: str, steps: List[Dict[str, Any]]) -> None:
        cls._pipelines[name] = steps

    @classmethod
    def get_pipeline(cls, name: str) -> Optional[List[Dict[str, Any]]]:
        return cls._pipelines.get(name)

    @classmethod
    def register_hook(cls, event: str, handler: Callable) -> None:
        if event not in cls._hooks:
            cls._hooks[event] = []
        cls._hooks[event].append(handler)

    @classmethod
    def trigger_hook(cls, event: str, **kwargs: Any) -> List[Any]:
        results = []
        for handler in cls._hooks.get(event, []):
            results.append(handler(**kwargs))
        return results


class AIError(Exception):
    pass


class ModelLoadError(AIError):
    pass


class InferenceError(AIError):
    pass


class ConfigError(AIError):
    pass


class TimeHelpers:
    @staticmethod
    def now() -> str:
        return datetime.utcnow().isoformat()

    @staticmethod
    def elapsed(start: float) -> float:
        return time.time() - start


class Serialization:
    @staticmethod
    def to_json(obj: Any, path: Optional[str] = None) -> str:
        data = json.dumps(obj, default=str, indent=2)
        if path:
            Path(path).write_text(data, encoding="utf-8")
        return data

    @staticmethod
    def from_json(path: str) -> Any:
        return json.loads(Path(path).read_text(encoding="utf-8"))

    @staticmethod
    def safe_model_id(name: str) -> str:
        safe = hashlib.sha256(name.encode()).hexdigest()[:12]
        return f"{name.lower().replace(' ', '_')[:48]}_{safe}"


def generate_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:16]}"


def chunks(lst: List[Any], n: int) -> Generator[List[Any], None, None]:
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def timed(fn: Callable) -> Callable:
    def wrapper(*args: Any, **kwargs: Any) -> Tuple[Any, float]:
        start = time.time()
        result = fn(*args, **kwargs)
        return result, time.time() - start
    return wrapper


def load_class(path: str) -> Type:
    module_name, class_name = path.rsplit(".", 1)
    mod = importlib.import_module(module_name)
    return getattr(mod, class_name)
