from __future__ import annotations
from compiler.optimization.base import Analysis, AnalysisResult
from compiler.ir.module import IRModule


class DominanceResult(AnalysisResult):
    __slots__ = ("_idom", "_dominates", "_dominance_frontiers", "_dominator_tree_children")

    def __init__(self, module: IRModule) -> None:
        super().__init__("dominance")
        self._idom: dict[str, dict[str, str | None]] = {}
        self._dominates: dict[str, dict[str, set[str]]] = {}
        self._dominance_frontiers: dict[str, dict[str, set[str]]] = {}
        self._dominator_tree_children: dict[str, dict[str, list[str]]] = {}
        self._compute(module)

    def _compute(self, module: IRModule) -> None:
        for fname, func in module.functions.items():
            bbs = [bb.name for bb in func.basic_blocks]
            if not bbs:
                continue
            entry = bbs[0]
            idom = self._compute_idom(func, entry, bbs)
            self._idom[fname] = idom

            dominates: dict[str, set[str]] = {bb: set() for bb in bbs}
            for bb in bbs:
                cur = bb
                visited: set[str] = set()
                while cur is not None and cur in idom and cur not in visited:
                    dominates[cur].add(bb)
                    visited.add(cur)
                    nxt = idom[cur]
                    if nxt == cur:
                        break
                    cur = nxt
            self._dominates[fname] = dominates

            df: dict[str, set[str]] = {bb: set() for bb in bbs}
            for bb in bbs:
                bb_block = func.get_block(bb)
                if bb_block is None:
                    continue
                preds = [p.name for p in bb_block.predecessors]
                if len(preds) >= 2:
                    for pred in preds:
                        runner = pred
                        while runner is not None and runner != idom.get(bb):
                            df[runner].add(bb)
                            runner_idom = idom.get(runner)
                            if runner_idom == runner or runner_idom is None:
                                break
                            runner = runner_idom
            self._dominance_frontiers[fname] = df

            children: dict[str, list[str]] = {bb: [] for bb in bbs}
            for bb in bbs:
                parent = idom.get(bb)
                if parent and parent in children and parent != bb:
                    children[parent].append(bb)
            self._dominator_tree_children[fname] = children

    @staticmethod
    def _compute_idom(func, entry_name: str, bbs: list[str]) -> dict[str, str | None]:
        idom: dict[str, str | None] = {bb: None for bb in bbs}
        idom[entry_name] = entry_name
        changed = True
        while changed:
            changed = False
            for bb in bbs:
                if bb == entry_name:
                    continue
                bb_block = func.get_block(bb)
                if bb_block is None:
                    continue
                preds = [p.name for p in bb_block.predecessors]
                new_idom: str | None = None
                for pred in preds:
                    if pred in idom and idom[pred] is not None:
                        new_idom = pred
                        break
                for pred in preds:
                    if pred == bb or pred not in idom or idom[pred] is None:
                        continue
                    if new_idom is None:
                        new_idom = pred
                        continue
                    new_idom = DominanceResult._intersect(idom, bbs, new_idom, pred)
                if new_idom != idom.get(bb):
                    idom[bb] = new_idom
                    changed = True
        return idom

    @staticmethod
    def _intersect(idom: dict[str, str | None], bbs: list[str], b1: str, b2: str) -> str:
        finger1 = b1
        finger2 = b2
        idx = {name: i for i, name in enumerate(bbs)}
        while finger1 != finger2:
            while finger1 in idx and finger2 in idx and idx[finger1] > idx[finger2]:
                nxt = idom.get(finger1)
                if nxt is None or nxt == finger1:
                    break
                finger1 = nxt
            while finger1 in idx and finger2 in idx and idx[finger2] > idx[finger1]:
                nxt = idom.get(finger2)
                if nxt is None or nxt == finger2:
                    break
                finger2 = nxt
            if finger1 == finger2:
                break
            if finger1 not in idx or finger2 not in idx:
                break
        return finger1

    @property
    def idom(self) -> dict[str, dict[str, str | None]]:
        return self._idom

    @property
    def dominators(self) -> dict[str, dict[str, set[str]]]:
        return self._dominates

    @property
    def dominance_frontiers(self) -> dict[str, dict[str, set[str]]]:
        return self._dominance_frontiers

    @property
    def dominator_tree_children(self) -> dict[str, dict[str, list[str]]]:
        return self._dominator_tree_children

    def immediate_dominator(self, func_name: str, bb_name: str) -> str | None:
        return self._idom.get(func_name, {}).get(bb_name)

    def dominates(self, func_name: str, a: str, b: str) -> bool:
        return b in self._dominates.get(func_name, {}).get(a, set())

    def get_dominance_frontier(self, func_name: str, bb_name: str) -> set[str]:
        return self._dominance_frontiers.get(func_name, {}).get(bb_name, set())

    def get_dominator_children(self, func_name: str, bb_name: str) -> list[str]:
        return self._dominator_tree_children.get(func_name, {}).get(bb_name, [])


class DominanceAnalysis(Analysis):
    """Computes dominator tree and dominance frontiers."""

    def __init__(self) -> None:
        super().__init__("dominance")

    def run(self, module: IRModule, ctx) -> DominanceResult:
        return DominanceResult(module)

    def estimated_complexity(self) -> str:
        return "O(n^2)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Dominator tree, immediate dominators, dominance frontiers"
