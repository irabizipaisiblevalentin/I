"""
PE/COFF object file writer for Windows x64 targets.
"""

from __future__ import annotations

import struct
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any



IMAGE_FILE_MACHINE_AMD64 = 0x8664
IMAGE_FILE_RELOCS_STRIPPED = 0x0001
IMAGE_FILE_EXECUTABLE_IMAGE = 0x0002
IMAGE_FILE_LINE_NUMS_STRIPPED = 0x0004
IMAGE_FILE_LARGE_ADDRESS_AWARE = 0x0020
IMAGE_FILE_32BIT_MACHINE = 0x0100
IMAGE_FILE_DEBUG_STRIPPED = 0x0200

IMAGE_SCN_CNT_CODE = 0x00000020
IMAGE_SCN_CNT_INITIALIZED_DATA = 0x00000040
IMAGE_SCN_CNT_UNINITIALIZED_DATA = 0x00000080
IMAGE_SCN_MEM_EXECUTE = 0x20000000
IMAGE_SCN_MEM_READ = 0x40000000
IMAGE_SCN_MEM_WRITE = 0x80000000

IMAGE_SYM_CLASS_EXTERNAL = 2
IMAGE_SYM_CLASS_STATIC = 3
IMAGE_SYM_CLASS_FUNCTION = 0x2E
IMAGE_SYM_DTYPE_FUNCTION = 0x20

IMAGE_REL_AMD64_ADDR64 = 0x0001
IMAGE_REL_AMD64_ADDR32 = 0x0002
IMAGE_REL_AMD64_REL32 = 0x0004


class PEWriter:
    """Generates COFF object files for Windows x64."""

    __slots__ = ("_machine",)

    def __init__(self, machine: int = IMAGE_FILE_MACHINE_AMD64) -> None:
        self._machine = machine

    def write_object(
        self,
        sections: dict[str, bytes],
        symbols: dict[str, dict[str, Any]],
        relocations: list[dict[str, Any]],
    ) -> bytes:
        sec_names = list(sections.keys())
        sec_data_list: list[bytes] = [sections[name] for name in sec_names]

        section_table, raw_data_offset = self._build_section_table(sec_names, sec_data_list)

        sym_table, str_table = self._build_symbol_table(
            symbols, sec_names, sec_data_list, relocations
        )

        relocation_data = self._build_relocations(relocations, sec_names, sec_data_list, sym_table)

        buf = bytearray()
        buf.extend(self._coff_header(len(sec_names), len(sym_table) // 18))
        buf.extend(section_table)

        for i, data in enumerate(sec_data_list):
            if data:
                buf.extend(data)
                buf.extend(b"\x00" * ((4 - len(data) % 4) % 4))

        if relocation_data:
            for sec_relocs in relocation_data:
                if sec_relocs:
                    buf.extend(sec_relocs)

        buf.extend(sym_table)
        buf.extend(str_table)

        return bytes(buf)

    def _coff_header(self, num_sections: int, num_symbols: int) -> bytes:
        buf = bytearray()
        buf.extend(struct.pack("<H", self._machine))
        buf.extend(struct.pack("<H", num_sections))
        buf.extend(struct.pack("<I", int(time.time())))
        buf.extend(struct.pack("<I", 0))
        buf.extend(struct.pack("<H", 0))
        buf.extend(struct.pack("<H", IMAGE_FILE_RELOCS_STRIPPED | IMAGE_FILE_EXECUTABLE_IMAGE | IMAGE_FILE_LINE_NUMS_STRIPPED | IMAGE_FILE_LARGE_ADDRESS_AWARE | IMAGE_FILE_DEBUG_STRIPPED))
        buf.extend(struct.pack("<H", 0))
        buf.extend(struct.pack("<H", 0))
        buf.extend(struct.pack("<H", num_symbols))
        return bytes(buf)

    def _build_section_table(
        self,
        sec_names: list[str],
        sec_data: list[bytes],
    ) -> tuple[bytes, int]:
        buf = bytearray()
        offset = 0
        raw_offset = 0

        coff_header_size = 20
        section_table_size = len(sec_names) * 40
        raw_offset = coff_header_size + section_table_size

        for i, name in enumerate(sec_names):
            name_bytes = name.encode("utf-8")[:8]
            name_bytes = name_bytes.ljust(8, b"\x00")

            characteristics = IMAGE_SCN_MEM_READ
            if name == ".text":
                characteristics |= IMAGE_SCN_CNT_CODE | IMAGE_SCN_MEM_EXECUTE
            elif name == ".data":
                characteristics |= IMAGE_SCN_CNT_INITIALIZED_DATA | IMAGE_SCN_MEM_WRITE
            elif name == ".bss":
                characteristics |= IMAGE_SCN_CNT_UNINITIALIZED_DATA | IMAGE_SCN_MEM_WRITE
            elif name == ".rdata":
                characteristics |= IMAGE_SCN_CNT_INITIALIZED_DATA
            else:
                characteristics |= IMAGE_SCN_CNT_INITIALIZED_DATA

            virtual_size = len(sec_data[i])
            virtual_address = offset
            size_of_raw_data = len(sec_data[i])
            pointer_to_raw_data = raw_offset if size_of_raw_data > 0 else 0
            pointer_to_relocations = 0
            pointer_to_linenumbers = 0
            num_relocations = 0
            num_linenumbers = 0

            buf.extend(name_bytes)
            buf.extend(struct.pack("<I", virtual_size))
            buf.extend(struct.pack("<I", virtual_address))
            buf.extend(struct.pack("<I", size_of_raw_data))
            buf.extend(struct.pack("<I", pointer_to_raw_data))
            buf.extend(struct.pack("<I", pointer_to_relocations))
            buf.extend(struct.pack("<I", pointer_to_linenumbers))
            buf.extend(struct.pack("<H", num_relocations))
            buf.extend(struct.pack("<H", num_linenumbers))
            buf.extend(struct.pack("<I", characteristics))

            offset += virtual_size
            raw_offset += size_of_raw_data
            raw_offset = (raw_offset + 3) // 4 * 4

        return bytes(buf), raw_offset

    def _build_symbol_table(
        self,
        symbols: dict[str, dict[str, Any]],
        sec_names: list[str],
        sec_data: list[bytes],
        relocations: list[dict[str, Any]],
    ) -> tuple[bytes, bytes]:
        entries = bytearray()

        null_entry = b"\x00" * 18
        entries.extend(null_entry)

        str_table_names: list[str] = []
        sym_index_map: dict[str, int] = {"": 0}

        for sym_name, sym_info in symbols.items():
            sym_index_map[sym_name] = len(sym_index_map)

            storage_class = IMAGE_SYM_CLASS_EXTERNAL
            sym_type = sym_info.get("type", IMAGE_SYM_DTYPE_FUNCTION)
            value = sym_info.get("value", 0)

            if len(sym_name) > 8:
                str_table_names.append(sym_name)
                name_bytes = b"\x00\x00\x00\x00"
                name_bytes += struct.pack("<I", self._strtab_offset(sym_name, str_table_names))
            else:
                name_bytes = sym_name.encode("utf-8").ljust(8, b"\x00")

            entries.extend(name_bytes)
            entries.extend(struct.pack("<I", value))
            entries.extend(struct.pack("<H", 0))
            entries.extend(struct.pack("<H", sym_type))
            entries.extend(struct.pack("<B", storage_class))
            entries.extend(struct.pack("<B", 0))

        str_data = bytearray(b"\x00\x00\x00\x00")
        for n in str_table_names:
            str_data.extend(n.encode("utf-8"))
            str_data.append(0)

        str_data[0:4] = struct.pack("<I", len(str_data))

        return bytes(entries), bytes(str_data)

    def _build_relocations(
        self,
        relocations: list[dict[str, Any]],
        sec_names: list[str],
        sec_data: list[bytes],
        sym_table: bytes,
    ) -> list[bytes]:
        sec_relocs: dict[str, list[bytes]] = {name: [] for name in sec_names}

        for r in relocations:
            sec_name = r.get("section", "")
            if sec_name not in sec_relocs:
                continue

            offset = r.get("offset", 0)
            reloc_type = r.get("type", IMAGE_REL_AMD64_REL32)

            buf = bytearray()
            buf.extend(struct.pack("<I", offset))
            buf.extend(struct.pack("<I", 0))
            buf.extend(struct.pack("<H", reloc_type))
            sec_relocs[sec_name].append(bytes(buf))

        result: list[bytes] = []
        for name in sec_names:
            if sec_relocs[name]:
                chunk = b"".join(sec_relocs[name])
                result.append(chunk)
            else:
                result.append(b"")

        return result

    def _strtab_offset(self, name: str, names: list[str]) -> int:
        offset = 4
        for n in names:
            if n == name:
                return offset
            offset += len(n.encode("utf-8")) + 1
        return offset
