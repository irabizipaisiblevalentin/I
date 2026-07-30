from __future__ import annotations

from typing import TYPE_CHECKING

from compiler.ir.instructions import (
    Alloca,
    Load,
    Phi,
    Store,
)
from compiler.ir.values import Value

if TYPE_CHECKING:

    from compiler.ir.basic_block import BasicBlock
    from compiler.ir.function import IRFunction


class StackSlot:
    __slots__ = ("index", "size", "alignment")

    def __init__(self, index: int, size: int = 8, alignment: int = 8) -> None:
        self.index = index
        self.size = size
        self.alignment = alignment

    def __repr__(self) -> str:
        return f"StackSlot({self.index}, size={self.size})"


ALLOCA_ATTR = "_spill_alloca"


class SpillManager:
    __slots__ = ("_slots", "_allocas", "_next_slot")

    def __init__(self) -> None:
        self._slots: dict[Value, StackSlot] = {}
        self._allocas: dict[int, Alloca] = {}
        self._next_slot: int = 0

    def allocate_spill_slot(
        self,
        value: Value,
        function: IRFunction,
    ) -> int:
        if value in self._slots:
            return self._slots[value].index
        slot = StackSlot(self._next_slot)
        self._next_slot += 1
        self._slots[value] = slot

        entry = function.entry_block
        if entry is not None:
            alloca = Alloca(f"spill_slot.{slot.index}", value.type)
            first_non_phi = None
            for inst in entry.instructions:
                if not isinstance(inst, Phi):
                    first_non_phi = inst
                    break
            if first_non_phi is not None:
                entry.insert_before(first_non_phi, alloca)
            else:
                entry.append(alloca)
            self._allocas[slot.index] = alloca

        return slot.index

    def insert_spill_code(
        self,
        value: Value,
        slot: int,
        function: IRFunction,
    ) -> None:
        alloca = self._allocas.get(slot)
        if alloca is None:
            return
        defining_block: BasicBlock | None = None
        defining_inst = None
        for block in function.blocks:
            for inst in block.instructions:
                if inst is value:
                    defining_block = block
                    defining_inst = inst
                    break
        if defining_block is not None and defining_inst is not None:
            if not defining_inst.type.is_void:
                store = Store(value, alloca)
                if defining_inst is defining_block.terminator:
                    defining_block.insert_before(defining_inst, store)
                else:
                    defining_block.insert_after(defining_inst, store)

    def insert_reload_code(
        self,
        value: Value,
        slot: int,
        function: IRFunction,
    ) -> None:
        alloca = self._allocas.get(slot)
        if alloca is None:
            return
        uses = list(value.uses)

        phi_uses: list[tuple[Phi, BasicBlock]] = []
        for block in function.blocks:
            for inst in block.instructions:
                if isinstance(inst, Phi):
                    for pred in block.predecessors:
                        if inst.get_incoming_for(pred) is value:
                            phi_uses.append((inst, pred))

        for use in uses:
            block = use.parent
            if block is None:
                continue
            load = Load(f"{value.name}_rel", value.type, alloca)
            block.insert_before(use, load)
            for i, op in enumerate(use.operands):
                if op is value:
                    use.set_operand(i, load)

        for phi_inst, pred in phi_uses:
            pred_end = pred.terminator
            if pred_end is not None:
                load = Load(f"{value.name}_rel", value.type, alloca)
                pred.insert_before(pred_end, load)
                phi_inst.remove_incoming(pred)
                phi_inst.add_incoming(load, pred)

    def get_slot(self, value: Value) -> StackSlot | None:
        return self._slots.get(value)

    def get_alloca(self, slot: int) -> Alloca | None:
        return self._allocas.get(slot)
