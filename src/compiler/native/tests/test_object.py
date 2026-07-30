from __future__ import annotations

import struct
import unittest

from compiler.native.object.elf import ELF_MAGIC, EM_AARCH64, EM_X86_64, ELFWriter
from compiler.native.object.macho import MachOWriter
from compiler.native.object.pe import PEWriter
from compiler.native.target.desc import TargetDescription
from compiler.native.target.kind import TargetKind


class TestELFWriter(unittest.TestCase):
    def setUp(self) -> None:
        self.writer = ELFWriter(EM_X86_64)

    def test_elf_header_magic(self) -> None:
        sections = {".text": b"\x90\xc3"}
        symbols = {"func": {"bind": 1, "type": 2, "section": ".text", "value": 0, "size": 2}}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)

        self.assertEqual(data[:4], ELF_MAGIC)
        self.assertEqual(data[4], 2)

    def test_elf_header_machine(self) -> None:
        sections = {".text": b"\x90\xc3"}
        symbols = {}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)

        machine = struct.unpack_from("<H", data, 18)[0]
        self.assertEqual(machine, EM_X86_64)

    def test_elf_with_multiple_sections(self) -> None:
        sections = {
            ".text": b"\x90\xc3",
            ".data": b"\x42\x00\x00\x00",
            ".rodata": b"\x01\x02\x03\x04",
        }
        symbols = {"main": {"bind": 1, "type": 2, "section": ".text", "value": 0, "size": 2}}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)

        e_shnum = struct.unpack_from("<H", data, 60)[0]
        self.assertGreater(e_shnum, 3)

    def test_elf_with_relocations(self) -> None:
        sections = {".text": b"\xe8\x00\x00\x00\x00\xc3"}
        symbols = {"call_me": {"bind": 1, "type": 2, "section": ".text", "value": 0, "size": 5}}
        relocations = [{"offset": 1, "type": 2, "sym_idx": 1, "addend": -4, "section": ".text"}]
        data = self.writer.write_object(sections, symbols, relocations)

        self.assertGreater(len(data), 100)

    def test_elf_local_symbol(self) -> None:
        sections = {".text": b"\x90\xc3"}
        symbols = {"local_func": {"bind": 0, "type": 2, "section": ".text", "value": 0, "size": 2}}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)
        self.assertTrue(len(data) > 0)

    def test_elf_data_section_flags(self) -> None:
        sections = {".text": b"\xc3", ".data": b"\x00"}
        symbols = {}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)

        e_shoff = struct.unpack_from("<Q", data, 40)[0]
        e_shentsize = struct.unpack_from("<H", data, 58)[0]

        for i in range(3):
            off = e_shoff + i * e_shentsize
            sh_type = struct.unpack_from("<I", data, off + 4)[0]
            if i == 0:
                continue
            self.assertIn(sh_type, (1, 8))

    def test_elf_empty_sections(self) -> None:
        sections = {}
        symbols = {}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)
        e_shnum = struct.unpack_from("<H", data, 60)[0]
        self.assertGreaterEqual(e_shnum, 1)

    def test_elf_aarch64_machine(self) -> None:
        writer = ELFWriter(EM_AARCH64)
        sections = {".text": b"\xc3"}
        symbols = {}
        relocations = []
        data = writer.write_object(sections, symbols, relocations)

        machine = struct.unpack_from("<H", data, 18)[0]
        self.assertEqual(machine, EM_AARCH64)

    def test_elf_for_target_x86_64(self) -> None:
        target = TargetDescription(kind=TargetKind.X86_64)
        writer = ELFWriter.for_target(target)
        self.assertEqual(writer.machine, EM_X86_64)

    def test_elf_for_target_arm64(self) -> None:
        target = TargetDescription(kind=TargetKind.ARM64)
        writer = ELFWriter.for_target(target)
        self.assertEqual(writer.machine, EM_AARCH64)

    def test_elf_symtab_entries(self) -> None:
        sections = {".text": b"\x90\xc3", ".data": b"\x00"}
        symbols = {
            "func": {"bind": 1, "type": 2, "section": ".text", "value": 0, "size": 2},
            "gvar": {"bind": 1, "type": 1, "section": ".data", "value": 0, "size": 4},
        }
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)
        self.assertGreater(len(data), 0)


class TestPEWriter(unittest.TestCase):
    def setUp(self) -> None:
        self.writer = PEWriter()

    def test_pe_magic(self) -> None:
        sections = {".text": b"\x90\xc3"}
        symbols = {}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)
        machine = struct.unpack_from("<H", data, 0)[0]
        self.assertEqual(machine, 0x8664)

    def test_pe_coff_header(self) -> None:
        sections = {".text": b"\xc3"}
        symbols = {}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)

        machine = struct.unpack_from("<H", data, 0)[0]
        self.assertEqual(machine, 0x8664)

    def test_pe_with_symbols(self) -> None:
        sections = {".text": b"\x90\xc3"}
        symbols = {"main": {"type": 0x20, "section": ".text", "value": 0}}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)
        self.assertGreater(len(data), 50)

    def test_pe_with_relocations(self) -> None:
        sections = {".text": b"\xe8\x00\x00\x00\x00\xc3"}
        symbols = {"printf": {"type": 0x20, "section": "", "value": 0}}
        relocations = [{"section": ".text", "offset": 1, "symbol": "printf", "type": 4}]
        data = self.writer.write_object(sections, symbols, relocations)
        self.assertGreater(len(data), 50)

    def test_pe_long_symbol_name(self) -> None:
        sections = {".text": b"\x90\xc3"}
        long_name = "a_very_long_function_name_that_exceeds_eight_bytes"
        symbols = {long_name: {"type": 0x20, "section": ".text", "value": 0}}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)
        self.assertGreater(len(data), 50)

    def test_pe_multiple_sections(self) -> None:
        sections = {".text": b"\xc3", ".data": b"\x00\x00\x00\x00", ".rdata": b"\x01\x02"}
        symbols = {}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)
        self.assertGreater(len(data), 100)

    def test_pe_num_sections(self) -> None:
        sections = {".text": b"\xc3"}
        symbols = {}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)

        num_sections = struct.unpack_from("<H", data, 2)[0]
        self.assertEqual(num_sections, 1)


class TestMachOWriter(unittest.TestCase):
    def setUp(self) -> None:
        self.writer = MachOWriter()

    def test_macho_magic(self) -> None:
        sections = {"__text": b"\x90\xc3"}
        symbols = {}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)

        magic = struct.unpack_from("<I", data, 0)[0]
        self.assertEqual(magic, 0xFEEDFACF)

    def test_macho_cputype(self) -> None:
        sections = {"__text": b"\xc3"}
        symbols = {}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)

        cputype = struct.unpack_from("<I", data, 4)[0]
        self.assertEqual(cputype, 0x01000007)

    def test_macho_with_symbols(self) -> None:
        sections = {"__text": b"\x90\xc3"}
        symbols = {"_main": {"section": "__text", "value": 0}}
        relocations = []
        data = self.writer.write_object(sections, symbols, relocations)
        self.assertGreater(len(data), 50)

    def test_macho_with_relocations(self) -> None:
        sections = {"__text": b"\x00\x00\x00\x00"}
        symbols = {"_printf": {"section": "", "value": 0}}
        relocations = [{"section": "__text", "offset": 0, "sym_idx": 1, "type": 0}]
        data = self.writer.write_object(sections, symbols, relocations)
        self.assertGreater(len(data), 50)

    def test_macho_for_target_x86_64(self) -> None:
        target = TargetDescription(kind=TargetKind.X86_64)
        writer = MachOWriter.for_target(target)
        data = writer.write_object({"__text": b"\xc3"}, {}, [])
        cputype = struct.unpack_from("<I", data, 4)[0]
        self.assertEqual(cputype, 0x01000007)

    def test_macho_for_target_arm64(self) -> None:
        target = TargetDescription(kind=TargetKind.ARM64)
        writer = MachOWriter.for_target(target)
        data = writer.write_object({"__text": b"\xc3"}, {}, [])
        cputype = struct.unpack_from("<I", data, 4)[0]
        self.assertEqual(cputype, 0x0100000C)
