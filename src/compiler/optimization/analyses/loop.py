from __future__ import annotations
from compiler.optimization.base import Analysis, AnalysisResult
from compiler.ir.module import IRModule


class LoopInfo:
    __slots__ = ("header", "latches", "body", "depth", "exits", "preheader", "parent")

    def __init__(self, header: str) -> None:
        self.header = header
        self.latches: list[str] = []
        self.body: list[str] = []
        self.depth: int = 0
        self.exits: list[str] = []
        self.preheader: str | None = None
        self.parent: LoopInfo | None = None


class LoopResult(AnalysisResult):
    __slots__ = ("_loops", "_loops_by_header", "_loop_depth", "_back_edges")

    def __init__(self, module: IRModule) -> None:
        super().__init__("loop")
        self._loops: dict[str, list[LoopInfo]] = {}
        self._loops_by_header: dict[str, dict[str, LoopInfo]] = {}
        self._loop_depth: dict[str, dict[str, int]] = {}
        self._back_edges: dict[str, list[tuple[str, str]]] = {}
        self._compute(module)

    def _compute(self, module: IRModule) -> None:
        for fname, func in module.functions.items():
            loops: list[LoopInfo] = []
            back_edges: list[tuple[str, str]] = []
            visited: set[str] = set()
            in_stack: set[str] = set()

            def dfs(bb_name: str) -> None:
                visited.add(bb_name)
                in_stack.add(bb_name)
                bb = func.get_block(bb_name)
                if bb:
                    for succ in bb.successors:
                        if succ.name in in_stack:
                            back_edges.append((bb_name, succ.name))
                        elif succ.name not in visited:
                            dfs(succ.name)
                in_stack.discard(bb_name)

            if func.basic_blocks:
                dfs(func.basic_blocks[0].name)

            for tail, header in back_edges:
                loop = LoopInfo(header)
                loop.latches.append(tail)
                loop_body: set[str] = {header}
                stack = [tail]
                while stack:
                    b = stack.pop()
                    if b in loop_body:
                        continue
                    loop_body.add(b)
                    bb = func.get_block(b)
                    if bb:
                        for pred in bb.predecessors:
                            if pred.name not in loop_body:
                                stack.append(pred.name)
                loop.body = sorted(loop_body)
                loop.depth = 1
                loops.append(loop)

            by_header: dict[str, LoopInfo] = {}
            for loop in loops:
                by_header[loop.header] = loop

            for loop in loops:
                for other in loops:
                    if other is loop:
                        continue
                    if other.header in loop.body and other.header != loop.header:
                        if loop.parent is None or loop.depth < other.depth:
                            loop.parent = other
                            other.depth += 1

            for loop in loops:
                body_set = set(loop.body)
                for bb_name in loop.body:
                    bb = func.get_block(bb_name)
                    if bb:
                        for succ in bb.successors:
                            if succ.name not in body_set:
                                if succ.name not in loop.exits:
                                    loop.exits.append(succ.name)

            for loop in loops:
                bb = func.get_block(loop.header)
                if bb:
                    non_loop_preds = [p.name for p in bb.predecessors if p.name not in loop.body]
                    if len(non_loop_preds) == 1:
                        loop.preheader = non_loop_preds[0]

            depth: dict[str, int] = {}
            for bb in func.basic_blocks:
                d = 0
                for loop in loops:
                    if bb.name in loop.body:
                        d = max(d, loop.depth)
                depth[bb.name] = d

            self._loops[fname] = loops
            self._loops_by_header[fname] = by_header
            self._loop_depth[fname] = depth
            self._back_edges[fname] = back_edges

    @property
    def loops(self) -> dict[str, list[LoopInfo]]:
        return self._loops

    @property
    def back_edges(self) -> dict[str, list[tuple[str, str]]]:
        return self._back_edges

    def loops_in(self, func_name: str) -> list[LoopInfo]:
        return list(self._loops.get(func_name, []))

    def loop_at(self, func_name: str, header: str) -> LoopInfo | None:
        return self._loops_by_header.get(func_name, {}).get(header)

    def nesting_depth(self, func_name: str, bb_name: str) -> int:
        return self._loop_depth.get(func_name, {}).get(bb_name, 0)

    def is_loop_header(self, func_name: str, bb_name: str) -> bool:
        return bb_name in self._loops_by_header.get(func_name, {})

    def has_loops(self, func_name: str) -> bool:
        return len(self._loops.get(func_name, [])) > 0


class LoopAnalysis(Analysis):
    def __init__(self) -> None:
        super().__init__("loop")

    def run(self, module: IRModule, ctx) -> LoopResult:
        return LoopResult(module)

    def estimated_complexity(self) -> str:
        return "O(V * E)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Natural loop detection, nesting depth, preheaders"
