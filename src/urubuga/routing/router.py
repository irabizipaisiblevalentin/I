"""router — Enterprise-grade URL routing system.

Supports static routes, dynamic parameters, groups, versioning,
named routes, nested routes, middleware per route, and automatic
route discovery.
"""

from __future__ import annotations

import enum
import re
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


class RouteParamType(enum.Enum):
    STRING = "string"
    INT = "int"
    FLOAT = "float"
    UUID = "uuid"
    PATH = "path"
    SLUG = "slug"


ROUTE_PARAM_PATTERNS = {
    RouteParamType.STRING: r"([^/]+)",
    RouteParamType.INT: r"(\d+)",
    RouteParamType.FLOAT: r"(\d+\.?\d*)",
    RouteParamType.UUID: r"([0-9a-fA-F-]{36})",
    RouteParamType.PATH: r"(.+)",
    RouteParamType.SLUG: r"([a-z0-9]+(?:-[a-z0-9]+)*)",
}


class RouteParam:
    """A parameter extracted from a URL pattern."""
    __slots__ = ("name", "param_type", "required", "default")

    def __init__(self, name: str,
                 param_type: RouteParamType = RouteParamType.STRING,
                 required: bool = True, default: Any = None) -> None:
        self.name = name
        self.param_type = param_type
        self.required = required
        self.default = default


class Route:
    """A registered route definition."""
    __slots__ = ("method", "pattern", "handler", "name", "middleware",
                 "params", "regex", "tags", "deprecated", "version",
                 "host", "group")

    def __init__(self, method: str, pattern: str, handler: Callable,
                 name: str = "", middleware: Optional[List[str]] = None,
                 params: Optional[List[RouteParam]] = None,
                 tags: Optional[List[str]] = None,
                 deprecated: bool = False, version: str = "",
                 host: str = "", group: str = "") -> None:
        self.method = method.upper()
        self.pattern = pattern
        self.handler = handler
        self.name = name
        self.middleware = middleware or []
        self.params = params or []
        self.regex: Optional[re.Pattern] = None
        self.tags = tags or []
        self.deprecated = deprecated
        self.version = version
        self.host = host
        self.group = group

    @property
    def path(self) -> str:
        return self.pattern

    @property
    def full_pattern(self) -> str:
        if self.version:
            return f"/{self.version}{self.pattern}"
        return self.pattern

    def __repr__(self) -> str:
        return f"Route({self.method} {self.pattern}, name={self.name!r})"


class RouteGroup:
    """A group of routes sharing a prefix and middleware."""
    __slots__ = ("prefix", "middleware", "name", "version", "host",
                 "tags", "routes", "_parent_router")

    def __init__(self, prefix: str = "",
                 middleware: Optional[List[str]] = None,
                 name: str = "", version: str = "",
                 host: str = "", tags: Optional[List[str]] = None) -> None:
        self.prefix = prefix.rstrip("/")
        self.middleware = middleware or []
        self.name = name
        self.version = version
        self.host = host
        self.tags = tags or []
        self.routes: List[Route] = []
        self._parent_router: Optional["Router"] = None

    def route(self, pattern: str, method: str = "GET",
              name: str = "", middleware: Optional[List[str]] = None,
              tags: Optional[List[str]] = None) -> Callable:
        def decorator(handler: Callable) -> Callable:
            full_pattern = f"{self.prefix}{pattern}"
            mw = list(self.middleware) + list(middleware or [])
            route_name = name or handler.__name__
            route = Route(method, full_pattern, handler, route_name,
                          mw, tags=tags or [], version=self.version,
                          host=self.host, group=self.name)
            self.routes.append(route)
            if self._parent_router is not None:
                self._parent_router._add_route(route)
            return handler
        return decorator

    def get(self, pattern: str, **kw: Any) -> Callable:
        return self.route(pattern, "GET", **kw)

    def post(self, pattern: str, **kw: Any) -> Callable:
        return self.route(pattern, "POST", **kw)

    def put(self, pattern: str, **kw: Any) -> Callable:
        return self.route(pattern, "PUT", **kw)

    def patch(self, pattern: str, **kw: Any) -> Callable:
        return self.route(pattern, "PATCH", **kw)

    def delete(self, pattern: str, **kw: Any) -> Callable:
        return self.route(pattern, "DELETE", **kw)


class RouteMatch:
    """Result of matching a URL against routes."""
    __slots__ = ("route", "params", "handler")

    def __init__(self, route: Route, params: Dict[str, Any],
                 handler: Callable) -> None:
        self.route = route
        self.params = params
        self.handler = handler


class Router:
    """Enterprise-grade URL router with pattern matching and parameter extraction."""

    def __init__(self) -> None:
        self._routes: List[Route] = []
        self._named_routes: Dict[str, Route] = {}
        self._route_cache: Dict[str, RouteMatch] = {}
        self._compiled_patterns: List[Tuple[re.Pattern, Route]] = []
        self._groups: List[RouteGroup] = []
        self._version_prefixes: Set[str] = set()

    def route(self, pattern: str, method: str = "GET",
              name: str = "", middleware: Optional[List[str]] = None,
              tags: Optional[List[str]] = None,
              version: str = "", host: str = "") -> Callable:
        def decorator(handler: Callable) -> Callable:
            route_name = name or handler.__name__
            r = Route(method, pattern, handler, route_name, middleware or [],
                      tags=tags, version=version, host=host)
            self._add_route(r)
            return handler
        return decorator

    def get(self, pattern: str, **kw: Any) -> Callable:
        return self.route(pattern, "GET", **kw)

    def post(self, pattern: str, **kw: Any) -> Callable:
        return self.route(pattern, "POST", **kw)

    def put(self, pattern: str, **kw: Any) -> Callable:
        return self.route(pattern, "PUT", **kw)

    def patch(self, pattern: str, **kw: Any) -> Callable:
        return self.route(pattern, "PATCH", **kw)

    def delete(self, pattern: str, **kw: Any) -> Callable:
        return self.route(pattern, "DELETE", **kw)

    def head(self, pattern: str, **kw: Any) -> Callable:
        return self.route(pattern, "HEAD", **kw)

    def options(self, pattern: str, **kw: Any) -> Callable:
        return self.route(pattern, "OPTIONS", **kw)

    def group(self, prefix: str = "",
              middleware: Optional[List[str]] = None,
              name: str = "", version: str = "",
              host: str = "",
              tags: Optional[List[str]] = None) -> RouteGroup:
        group = RouteGroup(prefix, middleware, name, version, host, tags)
        group._parent_router = self
        self._groups.append(group)
        return group

    def add_group(self, group: RouteGroup) -> None:
        self._groups.append(group)
        for route in group.routes:
            self._add_route(route)

    def match(self, method: str, path: str,
              host: str = "") -> Optional[RouteMatch]:
        cache_key = f"{method}:{path}:{host}"
        if cache_key in self._route_cache:
            return self._route_cache[cache_key]

        for pattern, route in self._compiled_patterns:
            if route.method != method.upper():
                continue
            if route.host and route.host != host:
                continue
            match = pattern.match(path)
            if match:
                params = match.groupdict()
                result = RouteMatch(route, params, route.handler)
                self._route_cache[cache_key] = result
                return result

        return None

    def url_for(self, name: str, **kwargs: Any) -> str:
        route = self._named_routes.get(name)
        if not route:
            raise KeyError(f"no route named '{name}'")

        url = route.full_pattern
        for param_name, param_value in kwargs.items():
            url = url.replace(f"{{{param_name}}}", str(param_value))
        return url

    def routes(self) -> List[Route]:
        return list(self._routes)

    def route_count(self) -> int:
        return len(self._routes)

    def named_routes(self) -> Dict[str, str]:
        return {name: route.full_pattern for name, route in self._named_routes.items()}

    def method_allowed(self, path: str, method: str) -> List[str]:
        allowed = []
        for route in self._routes:
            full = route.full_pattern
            if self._pattern_matches(full, path) and route.method not in allowed:
                allowed.append(route.method)
        return allowed

    def _add_route(self, route: Route) -> None:
        self._routes.append(route)
        if route.name:
            self._named_routes[route.name] = route
        regex = self._compile_pattern(route.full_pattern)
        route.regex = regex
        self._compiled_patterns.append((regex, route))
        self._route_cache.clear()

    def _compile_pattern(self, pattern: str) -> re.Pattern:
        parts = pattern.split("/")
        regex_parts = []
        for part in parts:
            if part.startswith("{") and part.endswith("}"):
                param_name = part[1:-1]
                if ":" in param_name:
                    name, type_name = param_name.split(":", 1)
                    try:
                        ptype = RouteParamType(type_name)
                        inner = ROUTE_PARAM_PATTERNS[ptype].strip("()")
                        regex_parts.append(f"(?P<{name}>{inner})")
                        route_param = RouteParam(name, ptype)
                    except ValueError:
                        regex_parts.append(f"(?P<{param_name}>[^/]+)")
                        route_param = RouteParam(param_name)
                else:
                    regex_parts.append(f"(?P<{param_name}>[^/]+)")
                    route_param = RouteParam(param_name)
            elif part:
                regex_parts.append(re.escape(part))
            else:
                regex_parts.append("")

        regex_str = "/".join(regex_parts)
        if not regex_str.startswith("^"):
            regex_str = f"^{regex_str}$"

        return re.compile(regex_str)

    def _pattern_matches(self, pattern: str, path: str) -> bool:
        regex = self._compile_pattern(pattern)
        return bool(regex.match(path))

    def clear(self) -> None:
        self._routes.clear()
        self._named_routes.clear()
        self._route_cache.clear()
        self._compiled_patterns.clear()
        self._groups.clear()

    def openapi_paths(self) -> Dict[str, Dict[str, Any]]:
        """Generate OpenAPI-compatible path specifications."""
        paths: Dict[str, Dict[str, Any]] = {}
        for route in self._routes:
            path = route.full_pattern
            method_lower = route.method.lower()
            if path not in paths:
                paths[path] = {}
            paths[path][method_lower] = {
                "operationId": route.name,
                "tags": route.tags,
                "deprecated": route.deprecated,
                "parameters": [
                    {"name": p.name, "in": "path",
                     "required": p.required,
                     "schema": {"type": p.param_type.value}}
                    for p in route.params
                ],
            }
        return paths
