from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

from compiler.ir.function import IRFunction
from compiler.ir.types import (
    FloatType,
    IntegerType,
    PointerType,
    VectorType,
)
from compiler.ir.values import Value
from compiler.native.register.spill import SpillManager

if TYPE_CHECKING:

    from compiler.ir.basic_block import BasicBlock
    from compiler.ir.cfg import CFG
    from compiler.native.register.liveness import LiveInterval
    from compiler.native.target.desc import TargetDescription


class RegisterClass(Enum):
    GPR = "gpr"
    XMM = "xmm"
    MASK = "mask"


class PhysicalRegister:
    __slots__ = ("name", "reg_class", "is_caller_save", "index")

    def __init__(
        self,
        name: str,
        reg_class: RegisterClass,
        is_caller_save: bool = True,
        index: int = 0,
    ) -> None:
        self.name = name
        self.reg_class = reg_class
        self.is_caller_save = is_caller_save
        self.index = index

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash((self.name, self.reg_class))

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, PhysicalRegister)
            and self.name == other.name
            and self.reg_class == other.reg_class
        )


@dataclass
class AllocationResult:
    allocation: dict[Value, PhysicalRegister] = field(default_factory=dict)
    spilled: set[Value] = field(default_factory=set)
    stack_slots: dict[Value, int] = field(default_factory=dict)


class RegisterAllocator(ABC):
    __slots__ = ()

    @abstractmethod
    def allocate(
        self,
        function: IRFunction,
        target: TargetDescription,
    ) -> AllocationResult:
        ...


class InterferenceGraph:
    __slots__ = ("_adj",)

    def __init__(self) -> None:
        self._adj: dict[Value, set[Value]] = {}

    @property
    def nodes(self) -> set[Value]:
        return set(self._adj.keys())

    def has_node(self, v: Value) -> bool:
        return v in self._adj

    def add_node(self, v: Value) -> None:
        if v not in self._adj:
            self._adj[v] = set()

    def add_edge(self, a: Value, b: Value) -> None:
        if a is b:
            return
        if a not in self._adj:
            self._adj[a] = set()
        if b not in self._adj:
            self._adj[b] = set()
        self._adj[a].add(b)
        self._adj[b].add(a)

    def remove_edge(self, a: Value, b: Value) -> None:
        if a in self._adj:
            self._adj[a].discard(b)
        if b in self._adj:
            self._adj[b].discard(a)

    def interferes(self, a: Value, b: Value) -> bool:
        return b in self._adj.get(a, set())

    def degree(self, v: Value) -> int:
        return len(self._adj.get(v, set()))

    def neighbors(self, v: Value) -> set[Value]:
        return set(self._adj.get(v, set()))

    def remove_node(self, v: Value) -> set[Value]:
        nbors = self._adj.pop(v, set())
        for n in nbors:
            self._adj[n].discard(v)
        return nbors

    def copy(self) -> InterferenceGraph:
        g = InterferenceGraph()
        for v, nbors in self._adj.items():
            g._adj[v] = set(nbors)
        return g

    def __len__(self) -> int:
        return len(self._adj)

    def __repr__(self) -> str:
        return f"InterferenceGraph({len(self._adj)} nodes)"


X86_64_GPRS: list[PhysicalRegister] = [
    PhysicalRegister("rax", RegisterClass.GPR, True, 0),
    PhysicalRegister("rcx", RegisterClass.GPR, True, 1),
    PhysicalRegister("rdx", RegisterClass.GPR, True, 2),
    PhysicalRegister("rbx", RegisterClass.GPR, False, 3),
    PhysicalRegister("rsi", RegisterClass.GPR, True, 4),
    PhysicalRegister("rdi", RegisterClass.GPR, True, 5),
    PhysicalRegister("r8", RegisterClass.GPR, True, 6),
    PhysicalRegister("r9", RegisterClass.GPR, True, 7),
    PhysicalRegister("r10", RegisterClass.GPR, True, 8),
    PhysicalRegister("r11", RegisterClass.GPR, True, 9),
    PhysicalRegister("r12", RegisterClass.GPR, False, 10),
    PhysicalRegister("r13", RegisterClass.GPR, False, 11),
    PhysicalRegister("r14", RegisterClass.GPR, False, 12),
    PhysicalRegister("r15", RegisterClass.GPR, False, 13),
    PhysicalRegister("rbp", RegisterClass.GPR, False, 14),
]

X86_64_XMMS: list[PhysicalRegister] = [
    PhysicalRegister(f"xmm{i}", RegisterClass.XMM, True, i)
    for i in range(16)
]


def register_class_for(value: Value) -> RegisterClass:
    t = value.type
    if isinstance(t, (IntegerType, PointerType)):
        return RegisterClass.GPR
    if isinstance(t, (FloatType, VectorType)):
        return RegisterClass.XMM
    return RegisterClass.GPR


def _get_registers(
    target: TargetDescription,
    reg_class: RegisterClass,
) -> list[PhysicalRegister]:
    from compiler.native.target.kind import TargetKind
    if target.kind in (TargetKind.X86_64, TargetKind.X86_32):
        if reg_class == RegisterClass.GPR:
            return X86_64_GPRS
        if reg_class == RegisterClass.XMM:
            return X86_64_XMMS
    return []


class GraphColoringAllocator(RegisterAllocator):
    __slots__ = ("_max_iterations",)

    def __init__(self, max_iterations: int = 4) -> None:
        self._max_iterations = max_iterations

    def allocate(
        self,
        function: IRFunction,
        target: TargetDescription,
    ) -> AllocationResult:
        from compiler.native.register.liveness import LiveRangeAnalysis
        from compiler.native.register.spill import SpillManager

        liveness = LiveRangeAnalysis()
        intervals = liveness.analyze(function)

        spill_manager = SpillManager()
        result = AllocationResult()

        for iteration in range(self._max_iterations):
            intervals = liveness.analyze(function)

            intervals_by_class = self._group_by_class(intervals)
            allocation: dict[Value, PhysicalRegister] = {}
            spilled: set[Value] = set()

            for reg_class, cls_intervals in intervals_by_class.items():
                registers = _get_registers(target, reg_class)
                if not registers:
                    continue

                graph = self._build_interference_graph(cls_intervals)
                cls_allocation, cls_spilled = self._color(graph, registers, reg_class)

                allocation.update(cls_allocation)
                spilled.update(cls_spilled)

            if not spilled:
                for v, reg in allocation.items():
                    if v in intervals:
                        intervals[v].reg = reg
                result.allocation = allocation
                return result

            for val in spilled:
                slot = spill_manager.allocate_spill_slot(val, function)
                result.stack_slots[val] = slot
                spill_manager.insert_reload_code(val, slot, function)
                spill_manager.insert_spill_code(val, slot, function)

            if iteration == self._max_iterations - 1:
                result.allocation = allocation
                result.spilled = spilled
                break

            function = self._rewrite_function(function, allocation, spilled, spill_manager)

        return result

    def _group_by_class(
        self,
        intervals: dict[Value, LiveInterval],
    ) -> dict[RegisterClass, dict[Value, LiveInterval]]:
        groups: dict[RegisterClass, dict[Value, LiveInterval]] = {
            RegisterClass.GPR: {},
            RegisterClass.XMM: {},
            RegisterClass.MASK: {},
        }
        for v, li in intervals.items():
            cls = register_class_for(v)
            groups[cls][v] = li
        return groups

    def _build_interference_graph(
        self,
        intervals: dict[Value, LiveInterval],
    ) -> InterferenceGraph:
        graph = InterferenceGraph()
        sorted_vals = sorted(intervals.keys(), key=lambda v: intervals[v].start)

        for v in intervals:
            graph.add_node(v)

        for i, a in enumerate(sorted_vals):
            ia = intervals[a]
            for b in sorted_vals[i + 1:]:
                ib = intervals[b]
                if ia.overlaps(ib):
                    graph.add_edge(a, b)
        return graph

    def _color(
        self,
        graph: InterferenceGraph,
        registers: list[PhysicalRegister],
        reg_class: RegisterClass,
    ) -> tuple[dict[Value, PhysicalRegister], set[Value]]:
        k = len(registers)
        stack: list[Value] = []
        spills: set[Value] = set()

        g = graph.copy()
        while len(g) > 0:
            found = False
            for v in list(g.nodes):
                if g.degree(v) < k:
                    stack.append(v)
                    g.remove_node(v)
                    found = True
                    break
            if not found:
                v = list(g.nodes)[0]
                stack.append(v)
                g.remove_node(v)

        allocation: dict[Value, PhysicalRegister] = {}
        used_colors: set[int] = set()

        for v in reversed(stack):
            used_colors.clear()
            for n in graph.neighbors(v):
                if n in allocation:
                    used_colors.add(allocation[n].index)
            assigned = False
            for reg in registers:
                if reg.index not in used_colors:
                    allocation[v] = reg
                    assigned = True
                    break
            if not assigned:
                spills.add(v)

        return allocation, spills

    def _compute_spill_costs(
        self,
        function: IRFunction,
        intervals: dict[Value, LiveInterval],
        cfg: CFG,
        graph: InterferenceGraph,
    ) -> dict[Value, float]:
        block_depth: dict[BasicBlock, int] = {}
        for li in cfg.loops:
            for block in li.blocks:
                existing = block_depth.get(block, 0)
                if li.depth > existing:
                    block_depth[block] = li.depth

        costs: dict[Value, float] = {}
        for v, li in intervals.items():
            cost = 0.0
            for use in v.uses:
                block = use.parent
                depth = block_depth.get(block, 0)
                cost += 10.0 ** depth
            block = getattr(v, "parent", None)
            if block is not None and block in block_depth:
                depth = block_depth[block]
                cost += 10.0 ** depth
            costs[v] = max(cost, 1.0)

        for v in costs:
            if graph.has_node(v):
                degree = graph.degree(v)
                if degree > 0:
                    costs[v] /= degree

        return costs

    def _rewrite_function(
        self,
        function: IRFunction,
        allocation: dict[Value, PhysicalRegister],
        spilled: set[Value],
        spill_manager: SpillManager,
    ) -> IRFunction:
        return function
