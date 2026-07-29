from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compiler.optimization.registry import PassRegistry


# ──────────────────────────────────────────────────────────────────────
# OptimizationScheduler
# ──────────────────────────────────────────────────────────────────────

class OptimizationScheduler:
    """Determines pass execution order via topological sort on dependencies."""
    __slots__ = ("_registry", "_custom_order")

    def __init__(self, registry: PassRegistry) -> None:
        self._registry = registry
        self._custom_order: list[str] | None = None

    def schedule(self, pass_names: list[str]) -> list[str]:
        """Given a list of pass names, return them in valid execution order.

        Respects dependency constraints. Raises ValueError on cycles.
        """
        if self._custom_order is not None:
            filtered = [n for n in self._custom_order if n in pass_names]
            remaining = [n for n in pass_names if n not in filtered]
            return filtered + remaining
        return self._topological_sort(pass_names)

    def schedule_all_at_level(self, level: int) -> list[str]:
        """Schedule all passes registered at or below the given optimization level."""
        passes = self._registry.passes_at_level(level)
        pass_names = [p.name for p in passes if p.name in self._registry.pass_names()]
        return self.schedule(pass_names)

    def validate_order(self, ordered: list[str]) -> bool:
        """Check that the ordering satisfies all dependency constraints."""
        seen: set[str] = set()
        for name in ordered:
            info = self._registry.get_pass(name)
            if info is None:
                return False
            for dep in info.dependencies:
                if dep not in self._registry.pass_names():
                    continue
                if dep not in seen:
                    return False
            seen.add(name)
        return True

    def find_cycle(self, pass_names: list[str]) -> list[str] | None:
        """Return the cycle if one exists, else None."""
        name_set = set(pass_names)
        adj: dict[str, list[str]] = {}
        for name in pass_names:
            info = self._registry.get_pass(name)
            if info is None:
                continue
            deps = [d for d in info.dependencies if d in name_set]
            for dep in deps:
                if dep not in adj:
                    adj[dep] = []
                adj[dep].append(name)

        in_degree: dict[str, int] = {n: 0 for n in pass_names}
        for name in pass_names:
            info = self._registry.get_pass(name)
            if info is None:
                continue
            for dep in info.dependencies:
                if dep in name_set:
                    in_degree[name] += 1

        queue: deque[str] = deque()
        for name in pass_names:
            if in_degree[name] == 0:
                queue.append(name)

        visited = 0
        while queue:
            node = queue.popleft()
            visited += 1
            for neighbor in adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if visited != len(pass_names):
            cycle_nodes = [n for n in pass_names if in_degree[n] > 0]
            if cycle_nodes:
                return cycle_nodes
        return None

    def _topological_sort(self, pass_names: list[str]) -> list[str]:
        """Kahn's algorithm for topological sort."""
        name_set = set(pass_names)
        adj: dict[str, list[str]] = {n: [] for n in pass_names}
        in_degree: dict[str, int] = {n: 0 for n in pass_names}

        for name in pass_names:
            info = self._registry.get_pass(name)
            if info is None:
                continue
            for dep in info.dependencies:
                if dep in name_set and dep != name:
                    adj[dep].append(name)
                    in_degree[name] += 1

        queue: deque[str] = deque()
        for name in pass_names:
            if in_degree[name] == 0:
                queue.append(name)

        result: list[str] = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(pass_names):
            missing = [n for n in pass_names if n not in result]
            raise ValueError(
                f"cycle detected among passes: {missing}"
            )

        return result
