from __future__ import annotations
from compiler.optimization.base import Analysis, AnalysisResult
from compiler.ir.module import IRModule
from compiler.ir.instructions import Return, Store


class EscapeKind:
    NONE = "none"
    ARGUMENT = "argument"
    RETURN = "return"
    GLOBAL = "global"
    ESCAPED = "escaped"


class EscapeResult(AnalysisResult):
    __slots__ = ("_escape_status", "_escaped_values")

    def __init__(self, module: IRModule) -> None:
        super().__init__("escape")
        self._escape_status: dict[str, dict[str, str]] = {}
        self._escaped_values: dict[str, set[str]] = {}
        self._compute(module)

    def _compute(self, module: IRModule) -> None:
        for fname, func in module.functions.items():
            status: dict[str, str] = {}
            for arg in func.args:
                if arg.name:
                    status[arg.name] = EscapeKind.ARGUMENT
            for bb in func.basic_blocks:
                for inst in bb.instructions:
                    if hasattr(inst, "name") and inst.name and inst.name not in status:
                        status[inst.name] = EscapeKind.NONE
                    if isinstance(inst, Return):
                        val = getattr(inst, "value", None)
                        if val is not None and hasattr(val, "name") and val.name:
                            status[val.name] = EscapeKind.RETURN
                    if isinstance(inst, Store):
                        ptr = getattr(inst, "ptr", None)
                        val = getattr(inst, "value", None)
                        if ptr is not None and hasattr(ptr, "name"):
                            if status.get(ptr.name) == EscapeKind.ARGUMENT:
                                if val is not None and hasattr(val, "name") and val.name:
                                    status[val.name] = EscapeKind.ESCAPED
            escaped = {n for n, s in status.items() if s not in (EscapeKind.NONE, EscapeKind.ARGUMENT)}
            self._escape_status[fname] = status
            self._escaped_values[fname] = escaped

    @property
    def escape_status(self) -> dict[str, dict[str, str]]:
        return self._escape_status

    @property
    def escaped_values(self) -> dict[str, set[str]]:
        return self._escaped_values

    def does_escape(self, func_name: str, value_name: str) -> bool:
        return value_name in self._escaped_values.get(func_name, set())

    def escape_kind(self, func_name: str, value_name: str) -> str:
        return self._escape_status.get(func_name, {}).get(value_name, EscapeKind.NONE)

    def non_escaping_values(self, func_name: str) -> set[str]:
        status = self._escape_status.get(func_name, {})
        return {n for n, s in status.items() if s == EscapeKind.NONE}

    def escaping_values(self, func_name: str) -> set[str]:
        return self._escaped_values.get(func_name, set())


class EscapeAnalysis(Analysis):
    """Determines which values escape their defining scope."""

    def __init__(self) -> None:
        super().__init__("escape")

    def run(self, module: IRModule, ctx) -> EscapeResult:
        return EscapeResult(module)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "low"

    def description(self) -> str:
        return "Escape analysis for stack allocation decisions"
