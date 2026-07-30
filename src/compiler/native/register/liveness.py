from __future__ import annotations

from typing import TYPE_CHECKING

from compiler.ir.instructions import Instruction, Phi
from compiler.ir.values import Value

if TYPE_CHECKING:

    from compiler.ir.basic_block import BasicBlock
    from compiler.ir.function import IRFunction
    from compiler.native.register.allocator import PhysicalRegister


class LiveInterval:
    __slots__ = ("start", "end", "value", "reg", "is_fixed")

    def __init__(
        self,
        start: int,
        end: int,
        value: Value,
        reg: PhysicalRegister | None = None,
        is_fixed: bool = False,
    ) -> None:
        self.start = start
        self.end = end
        self.value = value
        self.reg = reg
        self.is_fixed = is_fixed

    @property
    def range(self) -> range:
        return range(self.start, self.end)

    def overlaps(self, other: LiveInterval) -> bool:
        return self.start < other.end and other.start < self.end

    def contains(self, point: int) -> bool:
        return self.start <= point < self.end

    def __repr__(self) -> str:
        r = f"{self.reg.name}" if self.reg else "?"
        f = " [fixed]" if self.is_fixed else ""
        return f"Live({self.value.name}: [{self.start}, {self.end}) -> {r}{f})"


class LiveRangeAnalysis:
    __slots__ = ("_intervals", "_inst_numbers", "_block_numbers")

    def __init__(self) -> None:
        self._intervals: dict[Value, LiveInterval] = {}
        self._inst_numbers: dict[Instruction, int] = {}
        self._block_numbers: dict[BasicBlock, int] = {}

    def analyze(self, function: IRFunction) -> dict[Value, LiveInterval]:
        self._number_instructions(function)
        live_in, live_out = self.compute_global_liveness(function)
        self._compute_live_intervals(function, live_in, live_out)
        return dict(self._intervals)

    def get_instruction_number(self, inst: Instruction) -> int:
        return self._inst_numbers.get(inst, -1)

    def get_block_number(self, block: BasicBlock) -> int:
        return self._block_numbers.get(block, -1)

    def _number_instructions(self, function: IRFunction) -> None:
        idx = 0
        for bi, block in enumerate(function.blocks):
            self._block_numbers[block] = bi
            for inst in block.instructions:
                self._inst_numbers[inst] = idx
                idx += 1

    def compute_global_liveness(
        self, function: IRFunction
    ) -> tuple[dict[BasicBlock, set[Value]], dict[BasicBlock, set[Value]]]:
        block_defs: dict[BasicBlock, set[Value]] = {}
        block_uses: dict[BasicBlock, set[Value]] = {}

        for block in function.blocks:
            defined: set[Value] = set()
            used: set[Value] = set()
            for inst in block.instructions:
                for op in inst.operands:
                    if isinstance(op, Value) and op not in defined:
                        used.add(op)
                if inst.name:
                    defined.add(inst)
            block_defs[block] = defined
            block_uses[block] = used

        live_in: dict[BasicBlock, set[Value]] = {b: set() for b in function.blocks}
        live_out: dict[BasicBlock, set[Value]] = {b: set() for b in function.blocks}

        changed = True
        while changed:
            changed = False
            for block in reversed(function.blocks):
                new_out: set[Value] = set()
                for succ in block.successors:
                    new_out |= live_in[succ]
                new_in = block_uses[block] | (new_out - block_defs[block])

                if new_out != live_out[block]:
                    live_out[block] = new_out
                    changed = True
                if new_in != live_in[block]:
                    live_in[block] = new_in
                    changed = True

        return live_in, live_out

    def _compute_live_intervals(
        self,
        function: IRFunction,
        live_in: dict[BasicBlock, set[Value]],
        live_out: dict[BasicBlock, set[Value]],
    ) -> None:
        intervals: dict[Value, LiveInterval] = {}

        for block in function.blocks:
            for inst in block.instructions:
                if inst.type.is_void or inst.type.kind.name == "LABEL":
                    continue
                if not inst.name:
                    continue
                start = self._inst_numbers[inst]
                end = self._compute_last_use(inst, function, live_out)
                if end is None:
                    end = start + 1
                intervals[inst] = LiveInterval(start, end, inst)

        for arg in function.args:
            start = 0
            end = self._compute_last_use(arg, function, live_out)
            if end is None:
                end = 1
            intervals[arg] = LiveInterval(start, end, arg)

        self._intervals = intervals

    def _compute_last_use(
        self,
        value: Value,
        function: IRFunction,
        live_out: dict[BasicBlock, set[Value]],
    ) -> int | None:
        max_use: int | None = None
        for use in value.uses:
            use_num = self._inst_numbers.get(use)
            if use_num is not None:
                if max_use is None or use_num > max_use:
                    max_use = use_num

        for block in function.blocks:
            for inst in block.instructions:
                if isinstance(inst, Phi):
                    for val, _ in inst.incoming:
                        if val is value:
                            inst_num = self._inst_numbers.get(inst)
                            if inst_num is not None and (max_use is None or inst_num > max_use):
                                max_use = inst_num

        for block in function.blocks:
            if value in live_out.get(block, set()):
                last_inst = block.instructions[-1] if block.instructions else None
                if last_inst is not None:
                    last_num = self._inst_numbers.get(last_inst)
                    if last_num is not None and (max_use is None or last_num > max_use):
                        max_use = last_num

        if max_use is not None:
            return max_use + 1
        return max_use
