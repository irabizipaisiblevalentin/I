from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compiler.ir.function import IRFunction
    from compiler.ir.values import GlobalVariable


class Linkage(Enum):
    LOCAL = auto()
    GLOBAL = auto()
    WEAK = auto()
    EXTERN = auto()


class SymbolType(Enum):
    FUNCTION = auto()
    OBJECT = auto()
    NOTYPE = auto()
    TLS = auto()
    SECTION = auto()
    FILE = auto()


@dataclass
class Symbol:
    name: str
    address: int = 0
    size: int = 0
    linkage: Linkage = Linkage.LOCAL
    section_index: int = 0
    sym_type: SymbolType = SymbolType.NOTYPE
    visibility: str = "default"

    def is_local(self) -> bool:
        return self.linkage == Linkage.LOCAL

    def is_global(self) -> bool:
        return self.linkage == Linkage.GLOBAL

    def is_function(self) -> bool:
        return self.sym_type == SymbolType.FUNCTION

    def is_object(self) -> bool:
        return self.sym_type == SymbolType.OBJECT


@dataclass
class Relocation:
    offset: int
    rel_type: int
    symbol_name: str
    addend: int = 0
    section: str = ".text"

    def __post_init__(self) -> None:
        self.offset = self.offset
        self.rel_type = self.rel_type
        self.symbol_name = self.symbol_name
        self.addend = self.addend
        self.section = self.section


class SymbolGenerator:
    def __init__(self) -> None:
        self._symbols: list[Symbol] = []
        self._relocations: list[Relocation] = []

    def generate_symbol_table(
        self,
        functions: list[IRFunction],
        globals: list[GlobalVariable],
    ) -> list[Symbol]:
        self._symbols = []

        for func in functions:
            linkage = Linkage.GLOBAL if not func.name.startswith("_") else Linkage.LOCAL
            sym = Symbol(
                name=func.name,
                address=0,
                size=0,
                linkage=linkage,
                section_index=1,
                sym_type=SymbolType.FUNCTION,
            )
            self._symbols.append(sym)

        for gv in globals:
            linkage = Linkage.GLOBAL if gv.linkage == "external" else Linkage.LOCAL
            sym = Symbol(
                name=gv.name,
                address=0,
                size=8,
                linkage=linkage,
                section_index=2,
                sym_type=SymbolType.OBJECT,
            )
            self._symbols.append(sym)

        return list(self._symbols)

    def generate_relocations(
        self,
        function: IRFunction,
        code_offset: int = 0,
    ) -> list[Relocation]:
        self._relocations = []

        for block in function:
            for inst in block:
                if inst.opcode.name == "CALL":
                    callee = inst.callee if hasattr(inst, "callee") else None
                    if callee and hasattr(callee, "name"):
                        self._relocations.append(Relocation(
                            offset=code_offset,
                            rel_type=2,
                            symbol_name=callee.name,
                            addend=-4,
                            section=".text",
                        ))
                code_offset += 4

        return list(self._relocations)

    @property
    def symbols(self) -> list[Symbol]:
        return list(self._symbols)

    def add_symbol(self, symbol: Symbol) -> None:
        self._symbols.append(symbol)

    def get_symbol(self, name: str) -> Symbol | None:
        for sym in self._symbols:
            if sym.name == name:
                return sym
        return None

    def to_dict(self) -> dict:
        result: dict[str, dict] = {}
        for sym in self._symbols:
            bind = 1 if sym.is_global() else 0
            type_val = 2 if sym.is_function() else 1
            sec_name = ".text" if sym.section_index == 1 else ".data" if sym.section_index == 2 else ""
            result[sym.name] = {
                "bind": bind,
                "type": type_val,
                "section": sec_name,
                "value": sym.address,
                "size": sym.size,
            }
        return result

    def relocations_to_dict(self) -> list[dict]:
        return [
            {
                "offset": r.offset,
                "type": r.rel_type,
                "symbol": r.symbol_name,
                "addend": r.addend,
                "section": r.section,
            }
            for r in self._relocations
        ]
