"""templates — Template engine for urubuga.

Provides simple template rendering with variable interpolation,
template inheritance, and partials.
"""

from __future__ import annotations

import os
import re
from typing import Any, Callable, Dict, List, Optional


class Template:
    """A compiled template."""

    __slots__ = ("name", "source", "_compiled", "_blocks", "_extends",
                 "_includes")

    def __init__(self, name: str = "", source: str = "") -> None:
        self.name = name
        self.source = source
        self._compiled: Optional[Callable] = None
        self._blocks: Dict[str, str] = {}
        self._extends: Optional[str] = None
        self._includes: List[str] = []

    def render(self, **kwargs: Any) -> str:
        if self._compiled:
            return self._compiled(kwargs)
        return self._render_simple(kwargs)

    def _render_simple(self, context: Dict[str, Any]) -> str:
        result = self.source
        for key, value in context.items():
            pattern = re.compile(r'\{\{\s*' + re.escape(key) + r'\s*\}\}')
            result = pattern.sub(str(value), result)

        def loop_replacer(match: re.Match) -> str:
            loop_var = match.group(1)
            collection_name = match.group(2)
            template_body = match.group(3)
            items = context.get(collection_name, [])
            parts = []
            for item in items:
                item_ctx = dict(context)
                if isinstance(item, dict):
                    item_ctx.update(item)
                else:
                    item_ctx["item"] = item
                rendered = template_body
                for k, v in item_ctx.items():
                    rendered = re.sub(
                        r'\{\{\s*' + re.escape(k) + r'\s*\}\}',
                        str(v), rendered)
                parts.append(rendered)
            return "".join(parts)

        result = re.sub(
            r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}',
            loop_replacer, result, flags=re.DOTALL)

        def if_replacer(match: re.Match) -> str:
            var_name = match.group(1)
            template_body = match.group(2)
            else_body = match.group(3) or ""
            value = context.get(var_name)
            if value:
                rendered = template_body
                for k, v in context.items():
                    rendered = re.sub(
                        r'\{\{\s*' + re.escape(k) + r'\s*\}\}',
                        str(v), rendered)
                return rendered
            return else_body

        result = re.sub(
            r'\{%\s*if\s+(\w+)\s*%\}(.*?)(?:\{%\s*else\s*%\}(.*?))?\{%\s*endif\s*%\}',
            if_replacer, result, flags=re.DOTALL)

        return result


class TemplateEngine:
    """Template engine with loader, caching, and configuration."""

    def __init__(self, template_dir: str = "templates",
                 auto_reload: bool = True,
                 cache_size: int = 100) -> None:
        self.template_dir = template_dir
        self.auto_reload = auto_reload
        self.cache_size = cache_size
        self._cache: Dict[str, Template] = {}
        self._globals: Dict[str, Any] = {}
        self._filters: Dict[str, Callable] = {}
        self._loaders: List[Callable] = []

    def render(self, template_name: str,
               **kwargs: Any) -> str:
        template = self.get_template(template_name)
        if not template:
            raise FileNotFoundError(f"template not found: {template_name}")
        context = dict(self._globals)
        context.update(kwargs)
        return template.render(**context)

    def get_template(self, name: str) -> Optional[Template]:
        if name in self._cache:
            return self._cache[name]

        source = self._load_source(name)
        if source is None:
            return None

        template = Template(name, source)
        self._cache[name] = template
        if len(self._cache) > self.cache_size:
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        return template

    def _load_source(self, name: str) -> Optional[str]:
        for loader in self._loaders:
            source = loader(name)
            if source is not None:
                return source

        path = os.path.join(self.template_dir, name)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return None

    def add_loader(self, loader: Callable) -> None:
        self._loaders.append(loader)

    def add_string(self, name: str, source: str) -> None:
        self._cache[name] = Template(name, source)

    def set_global(self, name: str, value: Any) -> None:
        self._globals[name] = value

    def add_filter(self, name: str, fn: Callable) -> None:
        self._filters[name] = fn

    def clear_cache(self) -> int:
        count = len(self._cache)
        self._cache.clear()
        return count

    def template_count(self) -> int:
        return len(self._cache)
