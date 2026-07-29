from __future__ import annotations
from compiler.optimization.base import Analysis, AnalysisResult
from compiler.ir.module import IRModule
from compiler.ir.instructions import Call


class CallGraphResult(AnalysisResult):
    __slots__ = ("_callers", "_callees", "_call_sites", "_recursive")

    def __init__(self, module: IRModule) -> None:
        super().__init__("call_graph")
        self._callers: dict[str, set[str]] = {}
        self._callees: dict[str, set[str]] = {}
        self._call_sites: dict[str, list[tuple[str, str, str]]] = {}
        self._recursive: set[str] = set()
        self._compute(module)

    def _compute(self, module: IRModule) -> None:
        for fname, func in module.functions.items():
            callees: set[str] = set()
            sites: list[tuple[str, str, str]] = []
            for bb in func.basic_blocks:
                for inst in bb.instructions:
                    if isinstance(inst, Call) and hasattr(inst, "function"):
                        callee_val = inst.function
                        callee_name = ""
                        if hasattr(callee_val, "name"):
                            callee_name = callee_val.name
                        elif isinstance(callee_val, str):
                            callee_name = callee_val
                        if callee_name and callee_name in module.functions:
                            callees.add(callee_name)
                            sites.append((bb.name, callee_name, inst.name or ""))
            self._callees[fname] = callees
            self._call_sites[fname] = sites
        for fname, callees in self._callees.items():
            for callee in callees:
                if callee not in self._callers:
                    self._callers[callee] = set()
                self._callers[callee].add(fname)
        for fname in self._callees:
            if fname in self._callees[fname]:
                self._recursive.add(fname)

    @property
    def callers(self) -> dict[str, set[str]]:
        return self._callers

    @property
    def callees(self) -> dict[str, set[str]]:
        return self._callees

    @property
    def call_sites(self) -> dict[str, list[tuple[str, str, str]]]:
        return self._call_sites

    @property
    def recursive(self) -> set[str]:
        return self._recursive

    def callers_of(self, func_name: str) -> set[str]:
        return set(self._callers.get(func_name, set()))

    def callees_of(self, func_name: str) -> set[str]:
        return set(self._callees.get(func_name, set()))

    def is_recursive(self, func_name: str) -> bool:
        return func_name in self._recursive

    def call_sites_in(self, func_name: str) -> list[tuple[str, str, str]]:
        return list(self._call_sites.get(func_name, []))

    def is_leaf(self, func_name: str) -> bool:
        return len(self._callees.get(func_name, set())) == 0

    def transitive_callees(self, func_name: str) -> set[str]:
        visited: set[str] = set()
        stack = list(self._callees.get(func_name, set()))
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            for callee in self._callees.get(current, set()):
                if callee not in visited:
                    stack.append(callee)
        return visited


class CallGraphAnalysis(Analysis):
    def __init__(self) -> None:
        super().__init__("call_graph")

    def run(self, module: IRModule, ctx) -> CallGraphResult:
        return CallGraphResult(module)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "low"

    def description(self) -> str:
        return "Call graph, recursion detection, leaf functions"
