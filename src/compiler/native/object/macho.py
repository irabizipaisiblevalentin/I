"""
Mach-O object file writer for macOS targets.
"""

from __future__ import annotations

import struct
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from compiler.native.target.desc import TargetDescription


MH_MAGIC_64 = 0xFEEDFACF
MH_CIGAM_64 = 0xCFFAEDFE
MH_OBJECT = 0x00000001

CPU_TYPE_X86_64 = 0x01000007
CPU_TYPE_ARM64 = 0x0100000C
CPU_SUBTYPE_X86_64_ALL = 0x00000003
CPU_SUBTYPE_ARM64_ALL = 0x00000000

LC_SEGMENT_64 = 0x00000019
LC_SYMTAB = 0x00000002

S_REGULAR = 0x00
S_ZEROFILL = 0x01
S_ATTR_SOME_INSTRUCTIONS = 0x00000400
S_ATTR_PURE_INSTRUCTIONS = 0x80000000

N_LIST = 0x1
N_PEXT = 0x1
N_EXT = 0x01

N_SECT = 0x0E
N_UNDF = 0x00

RELOC_TARGET_ADDR = 0x00000001
RELOC_PAIR = 0x00000002
RELOC_SIZE_32 = 0x00000000
RELOC_SIZE_64 = 0x00000004
X86_64_RELOC_UNSIGNED = 0x00
X86_64_RELOC_SIGNED = 0x01
X86_64_RELOC_BRANCH = 0x02
X86_64_RELOC_GOT_LOAD = 0x03
X86_64_RELOC_GOT = 0x04
X86_64_RELOC_SUBTRACTOR = 0x05
X86_64_RELOC_SIGNED_1 = 0x06
X86_64_RELOC_SIGNED_2 = 0x07
X86_64_RELOC_SIGNED_4 = 0x08
X86_64_RELOC_TLV = 0x09

ARM64_RELOC_UNSIGNED = 0x00
ARM64_RELOC_BRANCH26 = 0x02
ARM64_RELOC_PAGE21 = 0x03
ARM64_RELOC_PAGEOFF12 = 0x04
ARM64_RELOC_GOT_LOAD_PAGE21 = 0x05
ARM64_RELOC_GOT_LOAD_PAGEOFF12 = 0x06
ARM64_RELOC_POINTER_TO_GOT = 0x07
ARM64_RELOC_TLVP_LOAD_PAGE21 = 0x08
ARM64_RELOC_TLVP_LOAD_PAGEOFF12 = 0x09
ARM64_RELOC_ADDEND = 0x0A


class MachOWriter:
    """Generates Mach-O relocatable object files."""

    __slots__ = ("_cputype", "_cpusubtype")

    def __init__(
        self,
        cputype: int = CPU_TYPE_X86_64,
        cpusubtype: int = CPU_SUBTYPE_X86_64_ALL,
    ) -> None:
        self._cputype = cputype
        self._cpusubtype = cpusubtype

    def write_object(
        self,
        sections: dict[str, bytes],
        symbols: dict[str, dict[str, Any]],
        relocations: list[dict[str, Any]],
    ) -> bytes:
        sec_names = list(sections.keys())

        sec_meta = self._build_section_meta(sec_names, sections)

        sym_data, str_data = self._build_symbol_table(symbols, sec_names, sec_meta)

        reloc_data_by_section: dict[int, bytes] = {}
        for i, name in enumerate(sec_names):
            sec_relocs = [r for r in relocations if r.get("section") == name]
            if sec_relocs:
                reloc_data_by_section[i] = self._build_relocations(sec_relocs)

        for i, (name, meta) in enumerate(sec_meta.items()):
            if i in reloc_data_by_section:
                meta["reloc_count"] = len(relocations)
                meta["reloc_offset"] = 0

        total_load_commands_size = self._compute_load_commands_size(sec_names, sec_meta)

        buf = bytearray()
        buf.extend(self._mach_header(len(sec_names), total_load_commands_size))

        self._write_load_commands(
            buf, sec_names, sec_meta, reloc_data_by_section,
        )

        for i, name in enumerate(sec_names):
            data = sections[name]
            if data:
                buf.extend(data)
            if i in reloc_data_by_section:
                relocs = reloc_data_by_section[i]
                buf.extend(relocs)

        buf.extend(sym_data)
        buf.extend(str_data)

        return bytes(buf)

    def _mach_header(self, num_sections: int, load_commands_size: int) -> bytes:
        ncmds = 1 + (1 if num_sections > 0 else 0)

        buf = bytearray()
        buf.extend(struct.pack("<I", MH_MAGIC_64))
        buf.extend(struct.pack("<I", self._cputype))
        buf.extend(struct.pack("<I", self._cpusubtype))
        buf.extend(struct.pack("<I", MH_OBJECT))
        buf.extend(struct.pack("<I", ncmds))
        buf.extend(struct.pack("<I", load_commands_size))
        buf.extend(struct.pack("<I", 0))
        buf.extend(struct.pack("<I", 0))
        return bytes(buf)

    def _build_section_meta(
        self,
        sec_names: list[str],
        sections: dict[str, bytes],
    ) -> dict[str, dict[str, Any]]:
        meta: dict[str, dict[str, Any]] = {}
        offset = 0

        for i, name in enumerate(sec_names):
            data = sections[name]
            size = len(data)
            flags = S_REGULAR
            if name == "__text":
                flags = S_ATTR_SOME_INSTRUCTIONS | S_ATTR_PURE_INSTRUCTIONS
            elif name == "__bss":
                flags = S_ZEROFILL
                size = 0

            meta[name] = {
                "index": i,
                "addr": offset,
                "size": len(data),
                "file_offset": 0,
                "flags": flags,
                "reloc_count": 0,
                "reloc_offset": 0,
            }
            offset += size

        return meta

    def _compute_load_commands_size(
        self,
        sec_names: list[str],
        sec_meta: dict[str, dict[str, Any]],
    ) -> int:
        size = 0
        if sec_names:
            size += 72 + len(sec_names) * 80
        for meta in sec_meta.values():
            if meta["reloc_count"] > 0:
                pass
        size += 24
        return size

    def _write_load_commands(
        self,
        buf: bytearray,
        sec_names: list[str],
        sec_meta: dict[str, dict[str, Any]],
        reloc_data_by_section: dict[int, bytes],
    ) -> int:
        offset = 0

        if sec_names:
            seg_cmd_size = 72 + len(sec_names) * 80
            buf.extend(struct.pack("<I", LC_SEGMENT_64))
            buf.extend(struct.pack("<I", seg_cmd_size))
            segname = b"\x00" * 16
            buf.extend(segname)
            buf.extend(struct.pack("<Q", 0))
            buf.extend(struct.pack("<Q", 0))
            buf.extend(struct.pack("<Q", 0))
            buf.extend(struct.pack("<Q", 0))
            buf.extend(struct.pack("<I", 0))
            buf.extend(struct.pack("<I", 0))
            buf.extend(struct.pack("<I", 0))
            buf.extend(struct.pack("<I", len(sec_names)))

            file_offset = 0
            for i, name in enumerate(sec_names):
                meta = sec_meta[name]
                sectname = name.encode("utf-8").ljust(16, b"\x00")
                segname = b"\x00" * 16
                buf.extend(sectname)
                buf.extend(segname)
                buf.extend(struct.pack("<Q", meta["addr"]))
                buf.extend(struct.pack("<Q", meta["size"]))
                buf.extend(struct.pack("<I", file_offset))
                buf.extend(struct.pack("<I", 2))
                buf.extend(struct.pack("<I", 0))
                buf.extend(struct.pack("<I", meta["reloc_count"]))
                buf.extend(struct.pack("<I", meta["reloc_offset"]))
                buf.extend(struct.pack("<I", 0))
                buf.extend(struct.pack("<I", meta["flags"]))
                buf.extend(struct.pack("<I", 0))
                buf.extend(struct.pack("<I", 0))
                file_offset += meta["size"]
                offset += seg_cmd_size

        sym_offset = 0
        sym_count = 0
        str_offset = 0
        str_size = 0

        buf.extend(struct.pack("<I", LC_SYMTAB))
        buf.extend(struct.pack("<I", 24))
        buf.extend(struct.pack("<I", sym_offset))
        buf.extend(struct.pack("<I", sym_count))
        buf.extend(struct.pack("<I", str_offset))
        buf.extend(struct.pack("<I", str_size))

        return offset

    def _build_symbol_table(
        self,
        symbols: dict[str, dict[str, Any]],
        sec_names: list[str],
        sec_meta: dict[str, dict[str, Any]],
    ) -> tuple[bytes, bytes]:
        entries = bytearray()

        str_names: list[str] = [""]
        str_data = bytearray(b"\x00")

        for sym_name, sym_info in symbols.items():
            n_strx = self._string_offset(sym_name, str_names, str_data)
            n_type = N_SECT | N_EXT
            n_sect = 0
            sec_name = sym_info.get("section", "")
            if sec_name in sec_names:
                n_sect = sec_meta[sec_name]["index"] + 1
            n_desc = 0
            n_value = sym_info.get("value", 0)

            entries.extend(struct.pack("<I", n_strx))
            entries.extend(struct.pack("<B", n_type))
            entries.extend(struct.pack("<B", n_sect))
            entries.extend(struct.pack("<H", n_desc))
            entries.extend(struct.pack("<Q", n_value))

            if sym_name not in str_names:
                str_names.append(sym_name)
                str_data.extend(sym_name.encode("utf-8"))
                str_data.append(0)

        return bytes(entries), bytes(str_data)

    def _build_relocations(
        self,
        relocations: list[dict[str, Any]],
    ) -> bytes:
        buf = bytearray()
        for r in relocations:
            r_address = r.get("offset", 0)
            r_symbol = r.get("sym_idx", 0)
            r_pcrel = 0
            r_length = 3
            r_extern = 1
            r_type = r.get("type", X86_64_RELOC_UNSIGNED)

            r_info = (
                (r_address & 0xFFFFFFFF)
                | ((r_symbol & 0xFFFFFF) << 8)
                | ((r_pcrel & 1) << 24)
                | ((r_length & 3) << 25)
                | ((r_extern & 1) << 27)
                | ((r_type & 0xF) << 28)
            )

            buf.extend(struct.pack("<I", r_info))
            buf.extend(struct.pack("<I", 0))
        return bytes(buf)

    def _string_offset(
        self,
        name: str,
        names: list[str],
        data: bytearray,
    ) -> int:
        idx = 0
        for n in names:
            if n == name:
                return idx
            idx += len(n.encode("utf-8")) + 1
        names.append(name)
        data.extend(name.encode("utf-8"))
        data.append(0)
        return idx

    @classmethod
    def for_target(cls, target: TargetDescription) -> MachOWriter:
        from compiler.native.target.kind import TargetKind
        if target.kind == TargetKind.ARM64:
            return cls(CPU_TYPE_ARM64, CPU_SUBTYPE_ARM64_ALL)
        return cls(CPU_TYPE_X86_64, CPU_SUBTYPE_X86_64_ALL)
