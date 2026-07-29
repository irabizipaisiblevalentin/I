from __future__ import annotations
from compiler.optimization.base import Analysis, AnalysisResult
from compiler.ir.module import IRModule
from compiler.ir.instructions import Alloca, Load, Store


class AliasResult(AnalysisResult):
    __slots__ = ("_may_alias", "_no_alias", "_must_alias")

    def __init__(self, module: IRModule) -> None:
        super().__init__("alias")
        self._may_alias: dict[str, set[tuple[str, str]]] = {}
        self._no_alias: dict[str, set[tuple[str, str]]] = {}
        self._must_alias: dict[str, set[tuple[str, str]]] = {}
        self._compute(module)

    def _compute(self, module: IRModule) -> None:
        for fname, func in module.functions.items():
            allocas: list[str] = []
            for bb in func.basic_blocks:
                for inst in bb.instructions:
                    if isinstance(inst, Alloca) and inst.name:
                        allocas.append(inst.name)

            no_alias: set[tuple[str, str]] = set()
            for i in range(len(allocas)):
                for j in range(i + 1, len(allocas)):
                    no_alias.add((allocas[i], allocas[j]))
                    no_alias.add((allocas[j], allocas[i]))

            must_alias: set[tuple[str, str]] = set()
            for n in allocas:
                must_alias.add((n, n))

            may_alias: set[tuple[str, str]] = set()
            for bb in func.basic_blocks:
                for inst in bb.instructions:
                    if isinstance(inst, (Load, Store)):
                        ptr = getattr(inst, "ptr", None)
                        ptr_name = ptr.name if ptr is not None and hasattr(ptr, "name") else None
                        if ptr_name:
                            for n in allocas:
                                if n != ptr_name:
                                    may_alias.add((ptr_name, n))
                                    may_alias.add((n, ptr_name))

            self._may_alias[fname] = may_alias
            self._no_alias[fname] = no_alias
            self._must_alias[fname] = must_alias

    @property
    def may_alias(self) -> dict[str, set[tuple[str, str]]]:
        return self._may_alias

    @property
    def no_alias(self) -> dict[str, set[tuple[str, str]]]:
        return self._no_alias

    @property
    def must_alias(self) -> dict[str, set[tuple[str, str]]]:
        return self._must_alias

    def does_alias(self, func_name: str, name1: str, name2: str) -> str:
        if (name1, name2) in self._must_alias.get(func_name, set()):
            return "must"
        if (name1, name2) in self._no_alias.get(func_name, set()):
            return "no"
        return "may"

    def no_alias_pairs(self, func_name: str) -> set[tuple[str, str]]:
        return self._no_alias.get(func_name, set())

    def may_alias_pairs(self, func_name: str) -> set[tuple[str, str]]:
        return self._may_alias.get(func_name, set())


class AliasAnalysis(Analysis):
    """Determines pointer aliasing relationships."""

    def __init__(self) -> None:
        super().__init__("alias")

    def run(self, module: IRModule, ctx) -> AliasResult:
        return AliasResult(module)

    def estimated_complexity(self) -> str:
        return "O(n^2)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Pointer alias analysis"
