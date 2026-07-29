from __future__ import annotations
from collections import deque
from compiler.optimization.base import Analysis, AnalysisResult
from compiler.ir.module import IRModule

class ControlFlowResult(AnalysisResult):
    """Result of control flow analysis."""
    __slots__ = ("_reachable", "_entry_blocks", "_exit_blocks", "_predecessors", "_successors")
    
    def __init__(self, module: IRModule) -> None:
        super().__init__("control_flow")
        self._reachable: dict[str, set[str]] = {}
        self._entry_blocks: dict[str, str] = {}
        self._exit_blocks: dict[str, list[str]] = {}
        self._predecessors: dict[str, dict[str, list[str]]] = {}
        self._successors: dict[str, dict[str, list[str]]] = {}
        self._compute(module)
    
    def _compute(self, module: IRModule) -> None:
        for fname, func in module.functions.items():
            if not func.basic_blocks:
                continue
            entry = func.basic_blocks[0]
            self._entry_blocks[fname] = entry.name
            preds: dict[str, list[str]] = {}
            succs: dict[str, list[str]] = {}
            for bb in func.basic_blocks:
                preds[bb.name] = [p.name for p in bb.predecessors]
                succs[bb.name] = [s.name for s in bb.successors]
            self._predecessors[fname] = preds
            self._successors[fname] = succs
            visited: set[str] = set()
            queue = deque([entry.name])
            while queue:
                name = queue.popleft()
                if name in visited:
                    continue
                visited.add(name)
                for s in succs.get(name, []):
                    queue.append(s)
            self._reachable[fname] = visited
            exits = [name for name in visited if not succs.get(name, [])]
            self._exit_blocks[fname] = exits
    
    @property
    def reachable(self) -> dict[str, set[str]]:
        return self._reachable

    def is_reachable(self, func_name: str, bb_name: str) -> bool:
        return bb_name in self._reachable.get(func_name, set())

    def entry_block(self, func_name: str) -> str | None:
        return self._entry_blocks.get(func_name)

    def exit_blocks(self, func_name: str) -> list[str]:
        return list(self._exit_blocks.get(func_name, []))

    def predecessors(self, func_name: str, bb_name: str) -> list[str]:
        return list(self._predecessors.get(func_name, {}).get(bb_name, []))

    def successors(self, func_name: str, bb_name: str) -> list[str]:
        return list(self._successors.get(func_name, {}).get(bb_name, []))

    def unreachable_blocks(self, func_name: str) -> set[str]:
        all_blocks = set(self._predecessors.get(func_name, {}).keys())
        return all_blocks - self._reachable.get(func_name, set())


class ControlFlowAnalysis(Analysis):
    """Computes control flow properties of each function."""
    def __init__(self) -> None:
        super().__init__("control_flow")

    def run(self, module: IRModule, ctx) -> ControlFlowResult:
        return ControlFlowResult(module)

    def estimated_complexity(self) -> str:
        return "O(V + E)"

    def performance_impact(self) -> str:
        return "none"

    def description(self) -> str:
        return "Control flow reachability, entry/exit blocks, predecessors/successors"
