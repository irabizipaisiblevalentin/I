from __future__ import annotations
from collections import deque
from compiler.optimization.base import Analysis, AnalysisResult
from compiler.ir.module import IRModule


class ReachabilityResult(AnalysisResult):
    __slots__ = ("_reachable", "_unreachable")

    def __init__(self, module: IRModule) -> None:
        super().__init__("reachability")
        self._reachable: dict[str, set[str]] = {}
        self._unreachable: dict[str, set[str]] = {}
        self._compute(module)

    def _compute(self, module: IRModule) -> None:
        for fname, func in module.functions.items():
            if not func.basic_blocks:
                continue
            entry = func.basic_blocks[0]
            visited: set[str] = set()
            queue: deque[str] = deque([entry.name])
            while queue:
                bname = queue.popleft()
                if bname in visited:
                    continue
                visited.add(bname)
                bb = func.get_block(bname)
                if bb:
                    for succ in bb.successors:
                        queue.append(succ.name)
            all_names = {bb.name for bb in func.basic_blocks}
            self._reachable[fname] = visited
            self._unreachable[fname] = all_names - visited

    @property
    def reachable(self) -> dict[str, set[str]]:
        return self._reachable

    @property
    def unreachable(self) -> dict[str, set[str]]:
        return self._unreachable

    def is_reachable(self, func_name: str, bb_name: str) -> bool:
        return bb_name in self._reachable.get(func_name, set())

    def unreachable_blocks(self, func_name: str) -> set[str]:
        return self._unreachable.get(func_name, set())

    def reachable_blocks(self, func_name: str) -> set[str]:
        return self._reachable.get(func_name, set())

    def has_unreachable(self, func_name: str) -> bool:
        return len(self._unreachable.get(func_name, set())) > 0


class ReachabilityAnalysis(Analysis):
    """Computes which basic blocks are reachable from function entry."""

    def __init__(self) -> None:
        super().__init__("reachability")

    def run(self, module: IRModule, ctx) -> ReachabilityResult:
        return ReachabilityResult(module)

    def estimated_complexity(self) -> str:
        return "O(V + E)"

    def performance_impact(self) -> str:
        return "none"

    def description(self) -> str:
        return "Block reachability from function entry"
