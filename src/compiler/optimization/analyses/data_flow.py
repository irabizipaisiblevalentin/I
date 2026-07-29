from __future__ import annotations
from compiler.optimization.base import Analysis, AnalysisResult
from compiler.ir.module import IRModule

class DataFlowResult(AnalysisResult):
    """Result of data flow analysis."""
    __slots__ = ("_reaching_defs_in", "_reaching_defs_out", "_defs")
    
    def __init__(self, module: IRModule) -> None:
        super().__init__("data_flow")
        self._reaching_defs_in: dict[str, dict[str, set[str]]] = {}
        self._reaching_defs_out: dict[str, dict[str, set[str]]] = {}
        self._defs: dict[str, dict[str, str]] = {}
        self._compute(module)
    
    def _compute(self, module: IRModule) -> None:
        for fname, func in module.functions.items():
            defs: dict[str, str] = {}
            gen: dict[str, set[str]] = {}
            kill: dict[str, set[str]] = {}
            for bb in func.basic_blocks:
                gen[bb.name] = set()
                kill[bb.name] = set()
                for inst in bb.instructions:
                    if hasattr(inst, 'name') and inst.name:
                        gen[bb.name].add(inst.name)
                        if inst.name in kill[bb.name]:
                            kill[bb.name].discard(inst.name)
                        kill[bb.name].update(d for d in defs if d not in gen[bb.name])
                        defs[inst.name] = bb.name
            self._defs[fname] = defs
            all_bbs = [bb.name for bb in func.basic_blocks]
            in_sets: dict[str, set[str]] = {bb: set() for bb in all_bbs}
            out_sets: dict[str, set[str]] = {bb: set() for bb in all_bbs}
            changed = True
            while changed:
                changed = False
                for bb_name in all_bbs:
                    new_in: set[str] = set()
                    block = func.get_block(bb_name)
                    preds = [p.name for p in block.predecessors] if block else []
                    for pred in preds:
                        new_in |= out_sets.get(pred, set())
                    new_out = gen.get(bb_name, set()) | (new_in - kill.get(bb_name, set()))
                    if new_out != out_sets[bb_name]:
                        out_sets[bb_name] = new_out
                        changed = True
                    if new_in != in_sets[bb_name]:
                        in_sets[bb_name] = new_in
            self._reaching_defs_in[fname] = in_sets
            self._reaching_defs_out[fname] = out_sets
    
    @property
    def reaching_defs_in(self) -> dict[str, dict[str, set[str]]]:
        return self._reaching_defs_in

    @property
    def reaching_defs_out(self) -> dict[str, dict[str, set[str]]]:
        return self._reaching_defs_out

    def defs_in_block(self, func_name: str, bb_name: str) -> set[str]:
        in_set = self._reaching_defs_in.get(func_name, {}).get(bb_name, set())
        out_set = self._reaching_defs_out.get(func_name, {}).get(bb_name, set())
        return in_set & out_set

    def def_location(self, func_name: str, def_name: str) -> str | None:
        func_defs = self._defs.get(func_name, {})
        return func_defs.get(def_name)

    def reaching_at_entry(self, func_name: str, bb_name: str) -> set[str]:
        return set(self._reaching_defs_in.get(func_name, {}).get(bb_name, set()))

    def reaching_at_exit(self, func_name: str, bb_name: str) -> set[str]:
        return set(self._reaching_defs_out.get(func_name, {}).get(bb_name, set()))


class DataFlowAnalysis(Analysis):
    """Reaching definitions analysis."""
    def __init__(self) -> None:
        super().__init__("data_flow")

    def run(self, module: IRModule, ctx) -> DataFlowResult:
        return DataFlowResult(module)

    def estimated_complexity(self) -> str:
        return "O(n^2)"

    def performance_impact(self) -> str:
        return "low"

    def description(self) -> str:
        return "Reaching definitions and def-use chains"
