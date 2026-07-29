from __future__ import annotations
from compiler.optimization.base import Analysis, AnalysisResult
from compiler.ir.module import IRModule
from compiler.ir.instructions import Load, Store, Alloca


class MemoryAccess:
    __slots__ = ("name", "kind", "bb_name", "is_volatile")

    def __init__(self, name: str, kind: str, bb_name: str, is_volatile: bool = False) -> None:
        self.name = name
        self.kind = kind
        self.bb_name = bb_name
        self.is_volatile = is_volatile


class MemoryAccessResult(AnalysisResult):
    __slots__ = ("_accesses", "_loads", "_stores", "_allocas")

    def __init__(self, module: IRModule) -> None:
        super().__init__("memory_access")
        self._accesses: dict[str, list[MemoryAccess]] = {}
        self._loads: dict[str, dict[str, list[str]]] = {}
        self._stores: dict[str, dict[str, list[str]]] = {}
        self._allocas: dict[str, dict[str, str]] = {}
        self._compute(module)

    def _compute(self, module: IRModule) -> None:
        for fname, func in module.functions.items():
            accesses: list[MemoryAccess] = []
            loads: dict[str, list[str]] = {}
            stores: dict[str, list[str]] = {}
            allocas: dict[str, str] = {}
            for bb in func.basic_blocks:
                for inst in bb.instructions:
                    if isinstance(inst, Load):
                        ptr = inst.pointer
                        ptr_name = ptr.name if hasattr(ptr, "name") and ptr.name else "?"
                        is_vol = inst.volatile if hasattr(inst, "volatile") else False
                        accesses.append(MemoryAccess(ptr_name, "load", bb.name, is_vol))
                        loads.setdefault(ptr_name, []).append(bb.name)
                    elif isinstance(inst, Store):
                        ptr = inst.pointer
                        ptr_name = ptr.name if hasattr(ptr, "name") and ptr.name else "?"
                        is_vol = inst.volatile if hasattr(inst, "volatile") else False
                        accesses.append(MemoryAccess(ptr_name, "store", bb.name, is_vol))
                        stores.setdefault(ptr_name, []).append(bb.name)
                    elif isinstance(inst, Alloca) and inst.name:
                        allocas[inst.name] = bb.name
                        accesses.append(MemoryAccess(inst.name, "alloca", bb.name))
            self._accesses[fname] = accesses
            self._loads[fname] = loads
            self._stores[fname] = stores
            self._allocas[fname] = allocas

    @property
    def accesses(self) -> dict[str, list[MemoryAccess]]:
        return self._accesses

    @property
    def loads(self) -> dict[str, dict[str, list[str]]]:
        return self._loads

    @property
    def stores(self) -> dict[str, dict[str, list[str]]]:
        return self._stores

    @property
    def allocas(self) -> dict[str, dict[str, str]]:
        return self._allocas

    def load_count(self, func_name: str) -> int:
        func_loads = self._loads.get(func_name, {})
        count = 0
        for bbs in func_loads.values():
            count += len(bbs)
        return count

    def store_count(self, func_name: str) -> int:
        func_stores = self._stores.get(func_name, {})
        count = 0
        for bbs in func_stores.values():
            count += len(bbs)
        return count

    def alloca_count(self, func_name: str) -> int:
        return len(self._allocas.get(func_name, {}))

    def total_memory_ops(self, func_name: str) -> int:
        return self.load_count(func_name) + self.store_count(func_name) + self.alloca_count(func_name)

    def is_only_loaded(self, func_name: str, ptr_name: str) -> bool:
        func_loads = self._loads.get(func_name, {})
        func_stores = self._stores.get(func_name, {})
        has_loads = ptr_name in func_loads and len(func_loads[ptr_name]) > 0
        has_stores = ptr_name in func_stores and len(func_stores[ptr_name]) > 0
        return has_loads and not has_stores

    def is_only_stored(self, func_name: str, ptr_name: str) -> bool:
        func_loads = self._loads.get(func_name, {})
        func_stores = self._stores.get(func_name, {})
        has_loads = ptr_name in func_loads and len(func_loads[ptr_name]) > 0
        has_stores = ptr_name in func_stores and len(func_stores[ptr_name]) > 0
        return has_stores and not has_loads


class MemoryAccessAnalysis(Analysis):
    def __init__(self) -> None:
        super().__init__("memory_access")

    def run(self, module: IRModule, ctx) -> MemoryAccessResult:
        return MemoryAccessResult(module)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "low"

    def description(self) -> str:
        return "Memory access pattern analysis"
