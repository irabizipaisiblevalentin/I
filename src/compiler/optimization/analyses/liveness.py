from __future__ import annotations
from compiler.optimization.base import Analysis, AnalysisResult
from compiler.ir.module import IRModule

class LivenessResult(AnalysisResult):
    """Result of liveness analysis."""
    __slots__ = ("_live_in", "_live_out")
    
    def __init__(self, module: IRModule) -> None:
        super().__init__("liveness")
        self._live_in: dict[str, dict[str, set[str]]] = {}
        self._live_out: dict[str, dict[str, set[str]]] = {}
        self._compute(module)
    
    def _compute(self, module: IRModule) -> None:
        for fname, func in module.functions.items():
            use: dict[str, set[str]] = {}
            defs: dict[str, set[str]] = {}
            all_bbs = [bb.name for bb in func.basic_blocks]
            for bb in func.basic_blocks:
                used: set[str] = set()
                defined: set[str] = set()
                for inst in bb.instructions:
                    for attr_name in ['a', 'b', 'lhs', 'rhs', 'condition', 'value', 'ptr', 'target']:
                        val = getattr(inst, attr_name, None)
                        if val is not None and hasattr(val, 'name') and val.name and val.name not in defined:
                            used.add(val.name)
                    if hasattr(inst, 'name') and inst.name:
                        defined.add(inst.name)
                use[bb.name] = used
                defs[bb.name] = defined
            in_sets: dict[str, set[str]] = {bb: set() for bb in all_bbs}
            out_sets: dict[str, set[str]] = {bb: set() for bb in all_bbs}
            changed = True
            while changed:
                changed = False
                for bb_name in all_bbs:
                    bb = func.get_block(bb_name)
                    if bb is None:
                        continue
                    new_in = use[bb_name] | (out_sets[bb_name] - defs[bb_name])
                    new_out: set[str] = set()
                    for succ in bb.successors:
                        new_out |= in_sets.get(succ.name, set())
                    if new_in != in_sets[bb_name]:
                        in_sets[bb_name] = new_in
                        changed = True
                    if new_out != out_sets[bb_name]:
                        out_sets[bb_name] = new_out
                        changed = True
            self._live_in[fname] = in_sets
            self._live_out[fname] = out_sets
    
    @property
    def live_in(self) -> dict[str, dict[str, set[str]]]:
        return self._live_in

    @property
    def live_out(self) -> dict[str, dict[str, set[str]]]:
        return self._live_out

    def live_at_entry(self, func_name: str, bb_name: str) -> set[str]:
        return set(self._live_in.get(func_name, {}).get(bb_name, set()))

    def live_at_exit(self, func_name: str, bb_name: str) -> set[str]:
        return set(self._live_out.get(func_name, {}).get(bb_name, set()))

    def is_live_at(self, func_name: str, bb_name: str, var_name: str) -> bool:
        in_set = self._live_in.get(func_name, {}).get(bb_name, set())
        out_set = self._live_out.get(func_name, {}).get(bb_name, set())
        return var_name in in_set or var_name in out_set

    def interference(self, func_name: str) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {}
        func_live_in = self._live_in.get(func_name, {})
        func_live_out = self._live_out.get(func_name, {})
        all_vars: set[str] = set()
        for bb_name in func_live_in:
            combined = func_live_in.get(bb_name, set()) | func_live_out.get(bb_name, set())
            all_vars |= combined
        for var in all_vars:
            result[var] = set()
        for bb_name in func_live_in:
            combined = func_live_in.get(bb_name, set()) | func_live_out.get(bb_name, set())
            var_list = list(combined)
            for i in range(len(var_list)):
                for j in range(i + 1, len(var_list)):
                    result[var_list[i]].add(var_list[j])
                    result[var_list[j]].add(var_list[i])
        return result

    def live_through(self, func_name: str, bb_name: str) -> set[str]:
        in_set = self._live_in.get(func_name, {}).get(bb_name, set())
        out_set = self._live_out.get(func_name, {}).get(bb_name, set())
        return set(in_set & out_set)


class LivenessAnalysis(Analysis):
    """Live variable analysis."""
    def __init__(self) -> None:
        super().__init__("liveness")

    def run(self, module: IRModule, ctx) -> LivenessResult:
        return LivenessResult(module)

    def estimated_complexity(self) -> str:
        return "O(n^2)"

    def performance_impact(self) -> str:
        return "low"

    def description(self) -> str:
        return "Live variable analysis per basic block"
