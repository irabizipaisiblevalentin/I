from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from compiler.ir.values import Value

if TYPE_CHECKING:

    from compiler.native.register.allocator import InterferenceGraph


@dataclass
class Move:
    dest: Value
    src: Value


class CoalescingOptimizer:
    __slots__ = ("_graph", "_moves", "_coalesced", "_K")

    def __init__(self, K: int = 16) -> None:  # noqa: N803
        self._graph: InterferenceGraph | None = None
        self._moves: list[Move] = []
        self._coalesced: dict[Value, Value] = {}
        self._K = K

    def optimize(
        self,
        graph: InterferenceGraph,
        moves: list[Move],
    ) -> InterferenceGraph:
        self._graph = graph
        self._moves = list(moves)
        self._coalesced = {}
        self._optimistic_coalesce()
        result = self._rebuild_graph()
        self._graph = None
        return result

    def _optimistic_coalesce(self) -> None:
        changed = True
        while changed:
            changed = False
            remaining: list[Move] = []
            for move in self._moves:
                a = self._resolve(move.dest)
                b = self._resolve(move.src)
                if a is b:
                    changed = True
                    continue
                cnb = self._conservative_ok(a, b)
                if cnb:
                    self._coalesced[b] = a
                    self._merge_nodes(a, b)
                    changed = True
                else:
                    if not self._graph.interferes(a, b):
                        george_ok = self._george_criterion(a, b)
                        if george_ok:
                            self._coalesced[b] = a
                            self._merge_nodes(a, b)
                            changed = True
                            continue
                    remaining.append(move)
            self._moves = remaining

    def _resolve(self, v: Value) -> Value:
        while v in self._coalesced:
            v = self._coalesced[v]
        return v

    def _conservative_ok(self, a: Value, b: Value) -> bool:
        if not self._graph.has_node(a) or not self._graph.has_node(b):
            return True
        combined = self._graph.neighbors(a) | self._graph.neighbors(b)
        heavy = 0
        for n in combined:
            if n is a or n is b:
                continue
            if self._graph.degree(n) >= self._K:
                heavy += 1
        return heavy < self._K

    def _george_criterion(self, a: Value, b: Value) -> bool:
        if not self._graph.has_node(a) or not self._graph.has_node(b):
            return True
        for n in self._graph.neighbors(b):
            if n is a:
                continue
            if self._graph.interferes(n, a):
                if self._graph.degree(n) >= self._K:
                    return False
            else:
                if self._graph.degree(n) >= self._K:
                    return False
        return True

    def _merge_nodes(self, target: Value, source: Value) -> None:
        if not self._graph.has_node(target) or not self._graph.has_node(source):
            return
        for n in list(self._graph.neighbors(source)):
            if n is not target:
                self._graph.add_edge(target, n)
        self._graph.remove_node(source)

    def _rebuild_graph(self) -> InterferenceGraph:
        if self._graph is None:
            from compiler.native.register.allocator import InterferenceGraph
            return InterferenceGraph()
        result = self._graph.copy()
        for src, dst in self._coalesced.items():
            if result.has_node(src):
                result.remove_node(src)
        return result


def coalesce(
    graph: InterferenceGraph,
    moves: list[Move],
) -> InterferenceGraph:
    optimizer = CoalescingOptimizer()
    return optimizer.optimize(graph, moves)
