"""
ELF64 object file writer for x86-64 and ARM64 targets.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from compiler.native.target.desc import TargetDescription


ELF_MAGIC = b"\x7fELF"

EM_X86_64 = 62
EM_AARCH64 = 183

SHT_NULL = 0
SHT_PROGBITS = 1
SHT_SYMTAB = 2
SHT_STRTAB = 3
SHT_RELA = 4
SHT_NOBITS = 8

SHF_WRITE = 0x1
SHF_ALLOC = 0x2
SHF_EXECINSTR = 0x4
SHF_STRINGS = 0x20

STB_LOCAL = 0
STB_GLOBAL = 1
STT_FUNC = 2
STT_OBJECT = 1
STT_NOTYPE = 0

R_X86_64_64 = 1
R_X86_64_PC32 = 2
R_X86_64_PLT32 = 4
R_AARCH64_ABS64 = 0x101
R_AARCH64_CALL26 = 0x103

ELF_HEADER_SIZE = 64
SECTION_HEADER_SIZE = 64
SYMBOL_ENTRY_SIZE = 24
RELA_ENTRY_SIZE = 24


@dataclass
class _SectionInfo:
    name: str
    data: bytes
    sh_type: int
    sh_flags: int
    sh_addr: int = 0
    sh_link: int = 0
    sh_info: int = 0
    sh_addralign: int = 1
    sh_entsize: int = 0



class ELFWriter:
    """Generates ELF64 relocatable object files."""

    __slots__ = ("_machine",)

    def __init__(self, machine: int = EM_X86_64) -> None:
        self._machine = machine

    @property
    def machine(self) -> int:
        return self._machine

    def write_object(
        self,
        sections: dict[str, bytes],
        symbols: dict[str, dict[str, Any]],
        relocations: list[dict[str, Any]],
    ) -> bytes:
        symstr_names, symstr_data = self._build_symbol_strings(symbols)
        secstr_data = self._build_section_strings(sections)

        sec_names = list(sections.keys())

        sec_infos: list[_SectionInfo] = []
        for name in sec_names:
            data = sections[name]
            sh_type = SHT_NOBITS if name == ".bss" else SHT_PROGBITS
            sh_flags = 0
            if name == ".text":
                sh_flags = SHF_ALLOC | SHF_EXECINSTR
            elif name in (".data", ".bss"):
                sh_flags = SHF_ALLOC | SHF_WRITE
            elif name == ".rodata":
                sh_flags = SHF_ALLOC
            sh_addralign = 16 if name == ".text" else 8
            sec_infos.append(_SectionInfo(name, data, sh_type, sh_flags, sh_addralign=sh_addralign))

        symtab_data = self._build_symtab(symbols, sec_infos, symstr_names)
        symtab_info = _SectionInfo(".symtab", symtab_data, SHT_SYMTAB, 0, sh_link=1, sh_info=0, sh_addralign=8, sh_entsize=SYMBOL_ENTRY_SIZE)

        strtab_info = _SectionInfo(".strtab", secstr_data, SHT_STRTAB, SHF_STRINGS, sh_addralign=1)

        symstr_info = _SectionInfo(".symstr", symstr_data, SHT_STRTAB, SHF_STRINGS, sh_addralign=1)

        all_infos = [symtab_info, strtab_info, symstr_info]
        sec_index_map: dict[str, int] = {}
        for i, info in enumerate(sec_infos):
            sec_index_map[info.name] = i + 1
        for info in all_infos:
            if info.name == ".symtab":
                info.sh_link = len(sec_infos) + 2
                info.sh_info = 0

        rela_infos: list[_SectionInfo] = []
        for i, name in enumerate(sec_names):
            sec_relocs = [r for r in relocations if r.get("section") == name]
            if not sec_relocs:
                continue
            rela_data = self._build_rela(sec_relocs)
            sec_idx = i + 1
            sh_info = sec_idx
            sh_link = len(sec_infos) + 1
            rela_name = f".rela{name}"
            rela_infos.append(_SectionInfo(
                rela_name, rela_data, SHT_RELA, 0,
                sh_link=sh_link, sh_info=sh_info,
                sh_addralign=8, sh_entsize=RELA_ENTRY_SIZE,
            ))

        ordered = [None] + sec_infos + all_infos + rela_infos

        strtab_data_full = self._build_full_strtab(ordered, secstr_data)
        for info in ordered:
            if info is not None and info.name == ".strtab":
                info.data = strtab_data_full
            elif info is None:
                pass

        shstrndx = ordered.index(next(i for i in ordered if i is not None and i.name == ".strtab"))

        file_size, section_offsets = self._compute_layout(ordered)

        buf = bytearray(file_size)

        self._write_elf_header(buf, ordered, shstrndx)
        self._write_section_headers(buf, ordered, section_offsets, shstrndx)
        self._write_section_data(buf, ordered, section_offsets)

        return bytes(buf)

    def _write_elf_header(self, buf: bytearray, ordered: list, shstrndx: int) -> None:
        e_type = 1
        e_machine = self._machine
        e_version = 1
        e_entry = 0
        e_phoff = 0
        e_shoff = ELF_HEADER_SIZE
        e_flags = 0
        e_ehsize = ELF_HEADER_SIZE
        e_phentsize = 56
        e_phnum = 0
        e_shentsize = SECTION_HEADER_SIZE
        e_shnum = len(ordered)
        e_shstrndx = shstrndx

        struct.pack_into("<4sBBB9x", buf, 0, ELF_MAGIC, 2, 1, 1)
        struct.pack_into("<H", buf, 16, e_type)
        struct.pack_into("<H", buf, 18, e_machine)
        struct.pack_into("<I", buf, 20, e_version)
        struct.pack_into("<Q", buf, 24, e_entry)
        struct.pack_into("<Q", buf, 32, e_phoff)
        struct.pack_into("<Q", buf, 40, e_shoff)
        struct.pack_into("<I", buf, 48, e_flags)
        struct.pack_into("<H", buf, 52, e_ehsize)
        struct.pack_into("<H", buf, 54, e_phentsize)
        struct.pack_into("<H", buf, 56, e_phnum)
        struct.pack_into("<H", buf, 58, e_shentsize)
        struct.pack_into("<H", buf, 60, e_shnum)
        struct.pack_into("<H", buf, 62, e_shstrndx)

    def _write_section_headers(
        self,
        buf: bytearray,
        ordered: list,
        section_offsets: list[int],
        shstrndx: int,
    ) -> None:
        base = ELF_HEADER_SIZE
        for i, info in enumerate(ordered):
            off = base + i * SECTION_HEADER_SIZE
            if info is None:
                continue
            struct.pack_into("<I", buf, off, 0)
            struct.pack_into("<I", buf, off + 4, info.sh_type)
            struct.pack_into("<Q", buf, off + 8, info.sh_flags)
            struct.pack_into("<Q", buf, off + 16, info.sh_addr)
            struct.pack_into("<Q", buf, off + 24, section_offsets[i])
            struct.pack_into("<Q", buf, off + 32, len(info.data))
            struct.pack_into("<I", buf, off + 40, info.sh_link)
            struct.pack_into("<I", buf, off + 44, info.sh_info)
            struct.pack_into("<Q", buf, off + 48, info.sh_addralign)
            struct.pack_into("<Q", buf, off + 56, info.sh_entsize)

    def _write_section_data(self, buf: bytearray, ordered: list, section_offsets: list[int]) -> None:
        for i, info in enumerate(ordered):
            if info is None or not info.data:
                continue
            off = section_offsets[i]
            buf[off:off + len(info.data)] = info.data

    def _compute_layout(self, ordered: list) -> tuple[int, list[int]]:
        offset = ELF_HEADER_SIZE + len(ordered) * SECTION_HEADER_SIZE
        offsets: list[int] = []
        for info in ordered:
            if info is None:
                offsets.append(0)
                continue
            offset = (offset + info.sh_addralign - 1) // info.sh_addralign * info.sh_addralign
            offsets.append(offset)
            offset += len(info.data)
        return offset, offsets

    def _build_section_strings(self, sections: dict[str, bytes]) -> bytes:
        data = bytearray(b"\x00")
        for name in sections:
            data.extend(name.encode("utf-8"))
            data.append(0)
        return bytes(data)

    def _build_symbol_strings(self, symbols: dict[str, Any]) -> tuple[list[str], bytes]:
        names = [""]
        data = bytearray(b"\x00")
        for sym_name in symbols:
            names.append(sym_name)
            data.extend(sym_name.encode("utf-8"))
            data.append(0)
        return names, bytes(data)

    def _build_full_strtab(self, ordered: list, existing: bytes) -> bytes:
        extra_names = []
        for info in ordered:
            if info is not None and info.name not in (".strtab", ".symstr"):
                if info.name not in extra_names:
                    extra_names.append(info.name)
        data = bytearray(existing)
        for name in extra_names:
            if name.encode("utf-8") + b"\x00" not in data:
                data.extend(name.encode("utf-8"))
                data.append(0)
        return bytes(data)

    def _build_symtab(
        self,
        symbols: dict[str, dict[str, Any]],
        sec_infos: list[_SectionInfo],
        symstr_names: list[str],
    ) -> bytes:
        buf = bytearray()

        buf.extend(b"\x00" * SYMBOL_ENTRY_SIZE)

        for sym_name, sym_info in symbols.items():
            st_name = self._strtab_offset(sym_name, symstr_names)
            st_bind = sym_info.get("bind", STB_GLOBAL)
            st_type = sym_info.get("type", STT_FUNC)
            st_info = (st_bind << 4) | st_type
            st_other = 0

            sec_name = sym_info.get("section", "")
            st_shndx = 0
            for i, info in enumerate(sec_infos):
                if info.name == sec_name:
                    st_shndx = i + 1
                    break

            st_value = sym_info.get("value", 0)
            st_size = sym_info.get("size", 0)

            buf.extend(struct.pack("<IBBHQQ", st_name, st_info, st_other, st_shndx, st_value, st_size))

        return bytes(buf)

    def _build_rela(self, relocations: list[dict[str, Any]]) -> bytes:
        buf = bytearray()
        for r in relocations:
            r_offset = r.get("offset", 0)
            sym_idx = r.get("sym_idx", 0)
            reloc_type = r.get("type", R_X86_64_64)
            addend = r.get("addend", 0)
            r_info = (sym_idx << 32) | (reloc_type & 0xFFFFFFFF)
            buf.extend(struct.pack("<QQq", r_offset, r_info, addend))
        return bytes(buf)

    def _strtab_offset(self, name: str, names: list[str]) -> int:
        offset = 0
        for n in names:
            if n == name:
                return offset
            offset += len(n.encode("utf-8")) + 1
        return 0

    @classmethod
    def for_target(cls, target: TargetDescription) -> ELFWriter:
        from compiler.native.target.kind import TargetKind
        machine = EM_AARCH64 if target.kind == TargetKind.ARM64 else EM_X86_64
        return cls(machine)
