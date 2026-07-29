"""ubugenzuzi — Navigation system for the I mobile platform.

Manages route registration, navigation stack, deep links,
and transition animations for mobile applications.
"""

from __future__ import annotations

import enum
import re
from typing import Any, Callable, Dict, List, Optional


class NavigationEvent(enum.Enum):
    """Types of navigation events in the system."""

    PUSH = "push"
    POP = "pop"
    REPLACE = "replace"
    CLEAR = "clear"
    DEEP_LINK = "deep_link"
    TAB_CHANGE = "tab_change"


class NavigationRoute:
    """A registered navigation route with metadata."""

    def __init__(
        self,
        path: str,
        name: str,
        params: Optional[Dict[str, Any]] = None,
        animation: Optional[str] = None,
        deep_link: Optional[str] = None,
    ) -> None:
        self.path = path
        self.name = name
        self.params = params or {}
        self.animation = animation
        self.deep_link = deep_link
        self._pattern = self._compile_pattern(path)

    @staticmethod
    def _compile_pattern(path: str) -> re.Pattern:
        """Convert a route path with :param placeholders to a regex.

        Args:
            path: The route path, e.g. '/user/:id/profile'.

        Returns:
            A compiled regex pattern.
        """
        regex_str = re.sub(r":(\w+)", r"(?P<\1>[^/]+)", path)
        return re.compile(f"^{regex_str}$")

    def match(self, path: str) -> Optional[Dict[str, str]]:
        """Match a path against this route.

        Args:
            path: The path to match.

        Returns:
            A dict of extracted parameters if matched, None otherwise.
        """
        m = self._pattern.match(path)
        if m is not None:
            return m.groupdict()
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a dictionary for state persistence.

        Returns:
            A dictionary representation of the route.
        """
        return {
            "path": self.path,
            "name": self.name,
            "params": dict(self.params),
            "animation": self.animation,
            "deep_link": self.deep_link,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> NavigationRoute:
        """Deserialize from a dictionary.

        Args:
            data: A dictionary representation of the route.

        Returns:
            A new NavigationRoute instance.
        """
        return cls(
            path=data["path"],
            name=data["name"],
            params=data.get("params"),
            animation=data.get("animation"),
            deep_link=data.get("deep_link"),
        )

    def __repr__(self) -> str:
        return (
            f"NavigationRoute(path={self.path!r}, name={self.name!r})"
        )


class NavigationEntry:
    """An entry on the navigation stack."""

    __slots__ = ("route", "params", "animation")

    def __init__(
        self,
        route: NavigationRoute,
        params: Optional[Dict[str, Any]] = None,
        animation: Optional[str] = None,
    ) -> None:
        self.route = route
        self.params = params or {}
        self.animation = animation or route.animation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "route": self.route.to_dict(),
            "params": dict(self.params),
            "animation": self.animation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> NavigationEntry:
        return cls(
            route=NavigationRoute.from_dict(data["route"]),
            params=data.get("params"),
            animation=data.get("animation"),
        )


class Ubugenzuzi:
    """Navigation system for mobile applications.

    Manages a navigation stack, route registration, deep link handling,
    and transition animations. Supports tab, drawer, and nested navigation.
    """

    def __init__(self) -> None:
        self._stack: List[NavigationEntry] = []
        self._history: List[Dict[str, Any]] = []
        self._routes: Dict[str, NavigationRoute] = {}
        self._routes_by_path: Dict[str, NavigationRoute] = {}
        self._tab_routes: Dict[str, List[NavigationRoute]] = {}
        self._drawer_routes: List[NavigationRoute] = []
        self._nested_navigators: Dict[str, Ubugenzuzi] = {}
        self._listeners: List[Callable] = []
        self._on_navigate: Optional[Callable] = None

    # -- Properties -----------------------------------------------------------

    @property
    def stack(self) -> List[NavigationEntry]:
        """The current navigation stack."""
        return list(self._stack)

    @property
    def history(self) -> List[Dict[str, Any]]:
        """The navigation history log."""
        return list(self._history)

    @property
    def routes(self) -> Dict[str, NavigationRoute]:
        """Registered routes keyed by name."""
        return dict(self._routes)

    @property
    def current_route(self) -> Optional[NavigationRoute]:
        """The route at the top of the stack, if any."""
        if self._stack:
            return self._stack[-1].route
        return None

    @property
    def can_go_back(self) -> bool:
        """Whether a back navigation is possible."""
        return len(self._stack) > 1

    # -- Stack Operations -----------------------------------------------------

    def push(
        self,
        route_name: str,
        params: Optional[Dict[str, Any]] = None,
        animation: Optional[str] = None,
    ) -> None:
        """Push a route onto the navigation stack.

        Args:
            route_name: Name of the registered route.
            params: Optional parameters for the route.
            animation: Optional animation override for the transition.
        """
        route = self._resolve_route(route_name)
        if route is None:
            raise ValueError(f"Unknown route: {route_name}")

        entry = NavigationEntry(route, params, animation)
        self._stack.append(entry)
        self._record_history(NavigationEvent.PUSH, route, params)
        self._notify(NavigationEvent.PUSH, entry)

    def pop(self) -> Optional[NavigationEntry]:
        """Pop the top route from the navigation stack.

        Returns:
            The removed entry, or None if the stack is empty.
        """
        if not self._stack:
            return None
        entry = self._stack.pop()
        self._record_history(NavigationEvent.POP, entry.route, entry.params)
        self._notify(NavigationEvent.POP, entry)
        return entry

    def replace(
        self,
        route_name: str,
        params: Optional[Dict[str, Any]] = None,
        animation: Optional[str] = None,
    ) -> None:
        """Replace the top route on the stack.

        Args:
            route_name: Name of the registered route.
            params: Optional parameters for the route.
            animation: Optional animation override.
        """
        route = self._resolve_route(route_name)
        if route is None:
            raise ValueError(f"Unknown route: {route_name}")

        if self._stack:
            self._stack.pop()
        entry = NavigationEntry(route, params, animation)
        self._stack.append(entry)
        self._record_history(NavigationEvent.REPLACE, route, params)
        self._notify(NavigationEvent.REPLACE, entry)

    def clear(self) -> None:
        """Clear the entire navigation stack."""
        self._stack.clear()
        self._record_history(NavigationEvent.CLEAR, None, None)
        self._notify(NavigationEvent.CLEAR, None)

    def go_back(self) -> bool:
        """Navigate back one step.

        Returns:
            True if navigation occurred, False otherwise.
        """
        if not self.can_go_back:
            return False
        self.pop()
        return True

    # -- Navigation -----------------------------------------------------------

    def navigate(
        self,
        path_or_name: str,
        params: Optional[Dict[str, Any]] = None,
        animation: Optional[str] = None,
    ) -> None:
        """Navigate to a route by path or name.

        Attempts to match by name first, then by path pattern.

        Args:
            path_or_name: Route name or path string.
            params: Optional parameters.
            animation: Optional animation override.
        """
        route = self._routes.get(path_or_name)
        if route is not None:
            self.push(route.name, params, animation)
            return

        for registered in self._routes.values():
            match = registered.match(path_or_name)
            if match is not None:
                merged = dict(registered.params)
                merged.update(match)
                if params:
                    merged.update(params)
                self.push(registered.name, merged, animation)
                return

        raise ValueError(f"Route not found: {path_or_name}")

    # -- Route Registration ---------------------------------------------------

    def register_route(self, route: NavigationRoute) -> None:
        """Register a navigation route.

        Args:
            route: The NavigationRoute to register.
        """
        self._routes[route.name] = route
        self._routes_by_path[route.path] = route

    def register_routes(self, routes: List[NavigationRoute]) -> None:
        """Register multiple navigation routes.

        Args:
            routes: A list of NavigationRoute instances.
        """
        for route in routes:
            self.register_route(route)

    # -- Tab Navigation -------------------------------------------------------

    def register_tab_route(
        self,
        tab_name: str,
        route: NavigationRoute,
    ) -> None:
        """Register a route under a tab group.

        Args:
            tab_name: The tab group identifier.
            route: The route to register.
        """
        self.register_route(route)
        self._tab_routes.setdefault(tab_name, []).append(route)

    def switch_tab(self, tab_name: str, route_name: str) -> None:
        """Switch to a different tab and navigate to a route within it.

        Args:
            tab_name: The tab group identifier.
            route_name: The route name within the tab.
        """
        tab_routes = self._tab_routes.get(tab_name, [])
        for route in tab_routes:
            if route.name == route_name:
                self.clear()
                self.push(route_name)
                self._record_history(NavigationEvent.TAB_CHANGE, route, None)
                self._notify(NavigationEvent.TAB_CHANGE, NavigationEntry(route))
                return

        raise ValueError(f"Route {route_name} not found in tab {tab_name}")

    # -- Drawer Navigation ----------------------------------------------------

    def register_drawer_route(self, route: NavigationRoute) -> None:
        """Register a route accessible via drawer navigation.

        Args:
            route: The route to register.
        """
        self.register_route(route)
        self._drawer_routes.append(route)

    @property
    def drawer_routes(self) -> List[NavigationRoute]:
        """Routes registered for drawer navigation."""
        return list(self._drawer_routes)

    # -- Nested Navigation ----------------------------------------------------

    def register_nested_navigator(
        self,
        route_name: str,
        navigator: Ubugenzuzi,
    ) -> None:
        """Register a nested navigator for a specific route.

        Args:
            route_name: The parent route name.
            navigator: The nested Ubugenzuzi instance.
        """
        self._nested_navigators[route_name] = navigator

    def get_nested_navigator(self, route_name: str) -> Optional[Ubugenzuzi]:
        """Get the nested navigator for a route, if any.

        Args:
            route_name: The parent route name.

        Returns:
            The nested navigator, or None.
        """
        return self._nested_navigators.get(route_name)

    # -- Deep Links -----------------------------------------------------------

    def handle_deep_link(self, uri: str) -> bool:
        """Handle a deep link URI.

        Maps a URI scheme to a registered route and navigates to it.

        Args:
            uri: The deep link URI (e.g. 'i-app://profile/42').

        Returns:
            True if the deep link was handled, False otherwise.
        """
        for route in self._routes.values():
            if route.deep_link is not None and uri.startswith(route.deep_link):
                self.push(route.name)
                self._record_history(NavigationEvent.DEEP_LINK, route, None)
                self._notify(NavigationEvent.DEEP_LINK, NavigationEntry(route))
                return True

        parsed = self._parse_deep_link(uri)
        if parsed is not None:
            name, params = parsed
            try:
                self.navigate(name, params)
                return True
            except ValueError:
                pass

        return False

    def handle_universal_link(self, url: str) -> bool:
        """Handle a universal link (standard HTTPS URL).

        Args:
            url: The universal link URL.

        Returns:
            True if the link was handled, False otherwise.
        """
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(url)
        path = parsed.path
        query_params = parse_qs(parsed.query)
        simple_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

        for route in self._routes.values():
            match = route.match(path)
            if match is not None:
                merged = dict(route.params)
                merged.update(match)
                merged.update(simple_params)
                self.push(route.name, merged)
                self._record_history(NavigationEvent.DEEP_LINK, route, merged)
                return True

        return False

    # -- State Restoration ----------------------------------------------------

    def restore_state(self, history: List[Dict[str, Any]]) -> None:
        """Restore navigation state from a history list.

        Args:
            history: A list of serialised navigation history entries.
        """
        self._stack.clear()
        self._history.clear()
        for entry_data in history:
            try:
                entry = NavigationEntry.from_dict(entry_data)
                self._stack.append(entry)
                self._history.append(entry_data)
            except (KeyError, TypeError):
                pass

    # -- Listener Registration ------------------------------------------------

    def add_listener(self, callback: Callable) -> None:
        """Add a listener for navigation events.

        Args:
            callback: A callable receiving a NavigationEvent and NavigationEntry.
        """
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable) -> None:
        """Remove a previously registered listener.

        Args:
            callback: The callback to remove.
        """
        self._listeners.remove(callback)

    def on_navigate(self, callback: Callable) -> None:
        """Set a single callback invoked on every navigation.

        Args:
            callback: A callable receiving NavigationEvent and NavigationEntry.
        """
        self._on_navigate = callback

    # -- Internal Helpers -----------------------------------------------------

    def _resolve_route(self, name: str) -> Optional[NavigationRoute]:
        return self._routes.get(name)

    def _record_history(
        self,
        event: NavigationEvent,
        route: Optional[NavigationRoute],
        params: Optional[Dict[str, Any]],
    ) -> None:
        self._history.append({
            "event": event.value,
            "route": route.to_dict() if route is not None else None,
            "params": dict(params) if params is not None else None,
            "timestamp": __import__("time").time(),
        })

    def _notify(
        self,
        event: NavigationEvent,
        entry: Optional[NavigationEntry],
    ) -> None:
        if self._on_navigate is not None:
            try:
                self._on_navigate(event, entry)
            except Exception:
                pass
        for listener in self._listeners:
            try:
                listener(event, entry)
            except Exception:
                pass

    @staticmethod
    def _parse_deep_link(uri: str) -> Optional[tuple]:
        """Parse a deep link URI into a route name and parameters.

        Handles formats like 'i-app://route_name/param1/value1'.

        Args:
            uri: The deep link URI.

        Returns:
            A tuple of (route_name, params_dict) or None.
        """
        pattern = re.compile(r"^[\w-]+://([^/]+)(?:/(.*))?$")
        m = pattern.match(uri)
        if m is None:
            return None

        route_name = m.group(1)
        params: Dict[str, Any] = {}

        rest = m.group(2)
        if rest is not None:
            segments = rest.split("/")
            i = 0
            while i + 1 < len(segments):
                params[segments[i]] = segments[i + 1]
                i += 2
            if i < len(segments):
                params["value"] = segments[i]

        return route_name, params

    def __repr__(self) -> str:
        return (
            f"Ubugenzuzi(stack_size={len(self._stack)}, "
            f"routes={len(self._routes)})"
        )
