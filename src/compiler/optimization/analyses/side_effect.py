from __future__ import annotations
from compiler.optimization.base import Analysis, AnalysisResult
from compiler.ir.module import IRModule
from compiler.ir.instructions import Store, Call, Load, Alloca


class SideEffectResult(AnalysisResult):
    __slots__ = ("_has_side_effects", "_reads_memory", "_writes_memory", "_function_info")

    def __init__(self, module: IRModule) -> None:
        super().__init__("side_effect")
        self._has_side_effects: dict[str, bool] = {}
        self._reads_memory: dict[str, bool] = {}
        self._writes_memory: dict[str, bool] = {}
        self._function_info: dict[str, dict[str, bool]] = {}
        self._compute(module)

    def _compute(self, module: IRModule) -> None:
        for fname, func in module.functions.items():
            has_effects = False
            reads_mem = False
            writes_mem = False
            for bb in func.basic_blocks:
                for inst in bb.instructions:
                    if isinstance(inst, Store):
                        writes_mem = True
                        has_effects = True
                    if isinstance(inst, Load):
                        reads_mem = True
                    if isinstance(inst, Call):
                        callee_name = ""
                        callee_val = inst.function
                        if hasattr(callee_val, "name"):
                            callee_name = callee_val.name
                        elif isinstance(callee_val, str):
                            callee_name = callee_val
                        if callee_name in module.functions:
                            sub_result = SideEffectResult.__new__(SideEffectResult)
                            sub_result._has_side_effects = {}
                            sub_result._reads_memory = {}
                            sub_result._writes_memory = {}
                            sub_result._function_info = {}
                            sub_result._name = "side_effect"
                            sub_result._timestamp = 0.0
                            callee_func = module.functions[callee_name]
                            callee_has = False
                            callee_reads = False
                            callee_writes = False
                            for cbb in callee_func.basic_blocks:
                                for cinst in cbb.instructions:
                                    if isinstance(cinst, Store):
                                        callee_writes = True
                                        callee_has = True
                                    if isinstance(cinst, Load):
                                        callee_reads = True
                                    if isinstance(cinst, Call):
                                        callee_has = True
                                        callee_reads = True
                                        callee_writes = True
                            if callee_has:
                                has_effects = True
                            if callee_reads:
                                reads_mem = True
                            if callee_writes:
                                writes_mem = True
                        else:
                            has_effects = True
                            reads_mem = True
                            writes_mem = True
            self._has_side_effects[fname] = has_effects
            self._reads_memory[fname] = reads_mem
            self._writes_memory[fname] = writes_mem
            self._function_info[fname] = {
                "has_effects": has_effects,
                "reads_mem": reads_mem,
                "writes_mem": writes_mem,
            }

    @property
    def has_side_effects(self) -> dict[str, bool]:
        return self._has_side_effects

    @property
    def reads_memory(self) -> dict[str, bool]:
        return self._reads_memory

    @property
    def writes_memory(self) -> dict[str, bool]:
        return self._writes_memory

    def function_has_effects(self, func_name: str) -> bool:
        return self._has_side_effects.get(func_name, False)

    def function_reads_memory(self, func_name: str) -> bool:
        return self._reads_memory.get(func_name, False)

    def function_writes_memory(self, func_name: str) -> bool:
        return self._writes_memory.get(func_name, False)

    def is_pure(self, func_name: str) -> bool:
        return not self._has_side_effects.get(func_name, False)

    def is_read_only(self, func_name: str) -> bool:
        reads = self._reads_memory.get(func_name, False)
        writes = self._writes_memory.get(func_name, False)
        return reads and not writes


class SideEffectAnalysis(Analysis):
    def __init__(self) -> None:
        super().__init__("side_effect")

    def run(self, module: IRModule, ctx) -> SideEffectResult:
        return SideEffectResult(module)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "low"

    def description(self) -> str:
        return "Side effect and purity analysis"
