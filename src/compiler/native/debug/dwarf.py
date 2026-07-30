from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compiler.ir.function import IRFunction
    from compiler.ir.module import IRModule
    from compiler.ir.values import Value


DWARF_VERSION = 5
DW_TAG_compile_unit = 0x11
DW_TAG_subprogram = 0x2E
DW_TAG_variable = 0x34
DW_TAG_base_type = 0x24
DW_TAG_lexical_block = 0x0B

DW_CHILDREN_yes = 0x01
DW_CHILDREN_no = 0x00

DW_AT_name = 0x03
DW_AT_language = 0x13
DW_AT_comp_dir = 0x1B
DW_AT_low_pc = 0x11
DW_AT_high_pc = 0x12
DW_AT_stmt_list = 0x10
DW_AT_producer = 0x25
DW_AT_type = 0x49
DW_AT_location = 0x02
DW_AT_decl_file = 0x3A
DW_AT_decl_line = 0x3B
DW_AT_byte_size = 0x0B
DW_AT_encoding = 0x3E

DW_FORM_strp = 0x0E
DW_FORM_udata = 0x0F
DW_FORM_flag = 0x0C
DW_FORM_addr = 0x01
DW_FORM_ref4 = 0x13
DW_FORM_data1 = 0x0B
DW_FORM_data2 = 0x05
DW_FORM_data4 = 0x06
DW_FORM_data8 = 0x07
DW_FORM_exprloc = 0x18
DW_FORM_string = 0x08
DW_FORM_implicit_const = 0x21
DW_FORM_sec_offset = 0x17

DW_LNCT_path = 0x01
DW_LNCT_directory_index = 0x02
DW_LNCT_timestamp = 0x03
DW_LNCT_size = 0x04
DW_LNCT_MD5 = 0x05

DW_FORM_block1 = 0x0A
DW_FORM_block2 = 0x03

DW_LNS_copy = 0x01
DW_LNS_advance_pc = 0x02
DW_LNS_advance_line = 0x03
DW_LNS_set_file = 0x04
DW_LNS_set_column = 0x05
DW_LNS_negate_stmt = 0x06
DW_LNS_const_add_pc = 0x07
DW_LNS_fixed_advance_pc = 0x08
DW_LNS_set_prologue_end = 0x09
DW_LNS_set_epilogue_begin = 0x0A
DW_LNS_set_isa = 0x0B

DW_LNE_end_sequence = 0x01
DW_LNE_set_address = 0x02
DW_LNE_define_file = 0x03
DW_LNE_set_discriminator = 0x04

DW_ATE_unsigned = 0x07
DW_ATE_signed = 0x05
DW_ATE_float = 0x01
DW_ATE_boolean = 0x02
DW_ATE_signed_char = 0x06
DW_ATE_unsigned_char = 0x08

DW_OP_lit0 = 0x30
DW_OP_fbreg = 0x91
DW_OP_breg0 = 0x70
DW_OP_breg7 = 0x77
DW_OP_stack_value = 0x9F

DW_LANG_C99 = 0x001C

DW_CC_normal = 0x01

LNCT_std = 0x01


@dataclass
class DWARFDebugSection:
    data: bytes
    name: str


@dataclass
class DWARFAbbreviationTable:
    _abbrevs: list[dict] = field(default_factory=list)

    def add(self, tag: int, children: int, attrs: list[tuple[int, int]]) -> int:
        code = len(self._abbrevs) + 1
        self._abbrevs.append({"code": code, "tag": tag, "children": children, "attrs": attrs})
        return code

    def serialize(self) -> bytes:
        buf = bytearray()
        for ab in self._abbrevs:
            buf.extend(_uleb(ab["code"]))
            buf.extend(_uleb(ab["tag"]))
            buf.append(ab["children"])
            for name, form in ab["attrs"]:
                buf.extend(_uleb(name))
                buf.extend(_uleb(form))
            buf.extend(_uleb(0))
            buf.extend(_uleb(0))
        buf.append(0)
        return bytes(buf)


@dataclass
class DWARFLineTable:
    _entries: list[dict] = field(default_factory=list)
    _files: list[str] = field(default_factory=list)

    def set_files(self, files: list[str]) -> None:
        self._files = files

    def add_entry(self, address: int, line: int, column: int = 0, file_index: int = 1) -> None:
        self._entries.append({"address": address, "line": line, "column": column, "file": file_index})

    def serialize(self) -> bytes:
        buf = bytearray()

        unit_length_offset = len(buf)
        buf.extend(b"\x00\x00\x00\x00")
        buf.extend(b"\x05\x00")
        buf.extend(b"\x00\x00\x00\x00")

        min_inst_len = 1
        max_ops_per_inst = 1
        default_is_stmt = 1
        line_base = -5
        line_range = 14
        opcode_base = 13

        buf.append(min_inst_len)
        buf.append(max_ops_per_inst)
        buf.append(default_is_stmt)
        buf.append(line_base & 0xFF)
        buf.append(line_range)
        buf.append(opcode_base)

        std_opcode_lengths = [0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1]
        for length in std_opcode_lengths:
            buf.append(length)

        dir_count = 0
        buf.extend(_uleb(dir_count))

        file_count = len(self._files)
        buf.extend(_uleb(file_count))
        for f in self._files:
            buf.extend(f.encode("utf-8"))
            buf.append(0)
            buf.extend(_uleb(0))
            buf.extend(_uleb(0))
            buf.extend(_uleb(0))

        prev_address = 0
        prev_line = 1

        if self._entries:
            e = self._entries[0]
            buf.append(0)
            buf.extend(_sleb(e["address"]))
            buf.extend(_sleb(e["line"] - prev_line))
            buf.append(e["column"])
            buf.append(e["file"])
            buf.append(0)
            buf.append(0)
            buf.append(0)
            buf.append(DW_LNS_copy)
            prev_address = e["address"]
            prev_line = e["line"]

            for e in self._entries[1:]:
                addr_diff = e["address"] - prev_address
                line_diff = e["line"] - prev_line

                if addr_diff > 0:
                    buf.append(DW_LNS_advance_pc)
                    buf.extend(_uleb(addr_diff))
                if line_diff != 0:
                    buf.append(DW_LNS_advance_line)
                    buf.extend(_sleb(line_diff))

                buf.append(DW_LNS_copy)

                prev_address = e["address"]
                prev_line = e["line"]

        buf.append(0)
        buf.append(1)
        buf.append(DW_LNE_end_sequence)
        buf.append(0)

        total_len = len(buf) - 4
        struct.pack_into("<I", buf, unit_length_offset, total_len)

        return bytes(buf)


def _uleb(value: int) -> bytes:
    buf = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            byte |= 0x80
        buf.append(byte)
        if not value:
            break
    return bytes(buf)


def _sleb(value: int) -> bytes:
    buf = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if (value == 0 and (byte & 0x40) == 0) or (value == -1 and (byte & 0x40) != 0):
            buf.append(byte)
            break
        byte |= 0x80
        buf.append(byte)
    return bytes(buf)


class DWARFDebugInfo:
    def __init__(self) -> None:
        self._str_table: list[tuple[str, int]] = []
        self._str_offsets: dict[str, int] = {}
        self._next_str_offset: int = 0
        self._debug_info = bytearray()
        self._abbrev_table = DWARFAbbreviationTable()
        self._line_table = DWARFLineTable()
        self._cu_start_offset: int = 0

    def _alloc_str(self, s: str) -> int:
        if s not in self._str_offsets:
            self._str_offsets[s] = self._next_str_offset
            self._str_table.append((s, self._next_str_offset))
            self._next_str_offset += len(s.encode("utf-8")) + 1
        return self._str_offsets[s]

    def _write_debug_info_header(self, unit_length: int, version: int, debug_abbrev_offset: int, address_size: int) -> bytes:
        hdr = bytearray()
        hdr.extend(struct.pack("<I", unit_length))
        hdr.extend(struct.pack("<H", version))
        hdr.extend(b"\x01")
        hdr.extend(struct.pack("<I", debug_abbrev_offset))
        hdr.extend(b"\x08")
        return bytes(hdr)

    def generate_compile_unit(self, module: IRModule, source_file: str) -> bytes:
        self._abbrev_table = DWARFAbbreviationTable()
        self._line_table = DWARFLineTable()

        buf = bytearray()

        unit_len_offset = len(buf)
        buf.extend(b"\x00\x00\x00\x00")
        buf.extend(b"\x05\x00")
        buf.append(0x01)
        buf.extend(struct.pack("<I", 0))
        buf.append(8)

        self._cu_start_offset = len(buf) - 5

        producer = "I Programming Language Compiler"

        cu_abbrev = self._abbrev_table.add(
            DW_TAG_compile_unit, DW_CHILDREN_yes, [
                (DW_AT_name, DW_FORM_strp),
                (DW_AT_comp_dir, DW_FORM_strp),
                (DW_AT_language, DW_FORM_data2),
                (DW_AT_producer, DW_FORM_strp),
                (DW_AT_stmt_list, DW_FORM_sec_offset),
                (DW_AT_low_pc, DW_FORM_addr),
                (DW_AT_high_pc, DW_FORM_addr),
            ]
        )

        buf.extend(_uleb(cu_abbrev))
        self._write_strp(buf, source_file)
        self._write_strp(buf, ".")
        buf.extend(struct.pack("<H", DW_LANG_C99))
        self._write_strp(buf, producer)
        buf.extend(struct.pack("<I", 0))
        buf.extend(b"\x00" * 8)
        buf.extend(b"\x00" * 8)

        for func in module.functions:
            if not func.is_declaration:
                self._emit_subprogram_die(buf, func)

        buf.append(0)

        total_len = len(buf) - 4
        struct.pack_into("<I", buf, unit_len_offset, total_len)

        self._debug_info = buf
        return bytes(buf)

    def _emit_subprogram_die(self, buf: bytearray, function: IRFunction) -> None:
        sub_abbrev = self._abbrev_table.add(
            DW_TAG_subprogram, DW_CHILDREN_yes, [
                (DW_AT_name, DW_FORM_strp),
                (DW_AT_low_pc, DW_FORM_addr),
                (DW_AT_high_pc, DW_FORM_addr),
            ]
        )
        buf.extend(_uleb(sub_abbrev))
        self._write_strp(buf, function.name)
        buf.extend(b"\x00" * 8)
        buf.extend(b"\x00" * 8)

        for arg in function.args:
            var_abbrev = self._abbrev_table.add(
                DW_TAG_variable, DW_CHILDREN_no, [
                    (DW_AT_name, DW_FORM_strp),
                    (DW_AT_location, DW_FORM_exprloc),
                ]
            )
            loc_bytes = bytearray()
            loc_bytes.append(0x70 | min(arg.index, 31))
            loc_bytes.append(0x00)

            buf.extend(_uleb(var_abbrev))
            self._write_strp(buf, arg.name)
            buf.append(len(loc_bytes))
            buf.extend(loc_bytes)

        buf.append(0)

    def generate_subprogram(self, function: IRFunction, frame_info: dict | None = None) -> bytes:
        self._abbrev_table = DWARFAbbreviationTable()
        buf = bytearray()

        unit_len_offset = len(buf)
        buf.extend(b"\x00\x00\x00\x00")
        buf.extend(b"\x05\x00")
        buf.append(0x01)
        buf.extend(struct.pack("<I", 0))
        buf.append(8)

        self._cu_start_offset = len(buf) - 5

        sub_abbrev = self._abbrev_table.add(
            DW_TAG_subprogram, DW_CHILDREN_yes, [
                (DW_AT_name, DW_FORM_strp),
                (DW_AT_low_pc, DW_FORM_addr),
                (DW_AT_high_pc, DW_FORM_addr),
            ]
        )
        buf.extend(_uleb(sub_abbrev))
        self._write_strp(buf, function.name)
        buf.extend(b"\x00" * 8)
        buf.extend(b"\x00" * 8)

        for arg in function.args:
            var_abbrev = self._abbrev_table.add(
                DW_TAG_variable, DW_CHILDREN_no, [
                    (DW_AT_name, DW_FORM_strp),
                    (DW_AT_location, DW_FORM_exprloc),
                ]
            )
            loc_bytes = bytearray()
            loc_bytes.append(0x70 | min(arg.index, 31))
            loc_bytes.append(0x00)

            buf.extend(_uleb(var_abbrev))
            self._write_strp(buf, arg.name)
            buf.append(len(loc_bytes))
            buf.extend(loc_bytes)

        buf.append(0)

        total_len = len(buf) - 4
        struct.pack_into("<I", buf, unit_len_offset, total_len)

        self._debug_info = buf
        return bytes(buf)

    def generate_variable(self, variable: Value, location: dict | None = None) -> bytes:
        buf = bytearray()

        unit_len_offset = len(buf)
        buf.extend(b"\x00\x00\x00\x00")
        buf.extend(b"\x05\x00")
        buf.append(0x01)
        buf.extend(struct.pack("<I", 0))
        buf.append(8)

        var_abbrev = self._abbrev_table.add(
            DW_TAG_variable, DW_CHILDREN_no, [
                (DW_AT_name, DW_FORM_strp),
                (DW_AT_location, DW_FORM_exprloc),
            ]
        )

        buf.extend(_uleb(var_abbrev))
        self._write_strp(buf, variable.name)

        if location and "fbreg" in location:
            loc_bytes = bytearray()
            loc_bytes.append(DW_OP_fbreg)
            loc_bytes.extend(_sleb(location["fbreg"]))
            buf.append(len(loc_bytes))
            buf.extend(loc_bytes)
        elif location and "register" in location:
            reg_num = location["register"]
            loc_bytes = bytearray()
            loc_bytes.append(DW_OP_breg0 + min(reg_num, 31))
            loc_bytes.append(0)
            buf.append(len(loc_bytes))
            buf.extend(loc_bytes)
        else:
            buf.append(0)

        buf.append(0)

        total_len = len(buf) - 4
        struct.pack_into("<I", buf, unit_len_offset, total_len)

        return bytes(buf)

    def generate_line_table(self, function: IRFunction) -> bytes:
        return self._line_table.serialize()

    def _write_strp(self, buf: bytearray, s: str) -> None:
        offset = self._alloc_str(s)
        buf.extend(struct.pack("<I", offset))

    def get_debug_info_section(self) -> DWARFDebugSection:
        return DWARFDebugSection(data=bytes(self._debug_info), name=".debug_info")

    def get_abbrev_section(self) -> DWARFDebugSection:
        return DWARFDebugSection(data=self._abbrev_table.serialize(), name=".debug_abbrev")

    def get_line_section(self) -> DWARFDebugSection:
        return DWARFDebugSection(data=self._line_table.serialize(), name=".debug_line")

    def get_str_section(self) -> DWARFDebugSection:
        buf = bytearray()
        for s, offset in self._str_table:
            buf.extend(s.encode("utf-8"))
            buf.append(0)
        return DWARFDebugSection(data=bytes(buf), name=".debug_str")

    def get_sections(self) -> list[DWARFDebugSection]:
        return [
            self.get_debug_info_section(),
            self.get_abbrev_section(),
            self.get_line_section(),
            self.get_str_section(),
        ]
