from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from compiler.native.target.desc import TargetDescription

if TYPE_CHECKING:
    from compiler.ir.instructions import Instruction
    from compiler.ir.module import IRModule


class ValidationError(Exception):
    pass


@dataclass
class ValidationResult:
    success: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.success = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def merge(self, other: ValidationResult) -> None:
        if not other.success:
            self.success = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


_KNOWN_ELF_MAGIC = b"\x7fELF"
_KNOWN_PE_MAGIC = b"MZ"
_KNOWN_MACHO_MAGIC = bytes([0xFE, 0xED, 0xFA, 0xCF])

_VALID_ELF_MACHINES = {62, 183, 40, 50}
_VALID_ELF_TYPES = {0, 1, 2, 3, 4}
_VALID_SECTION_FLAGS = {
    0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7,
    0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27,
    0x30, 0x32, 0x40, 0x42, 0x60, 0x62,
    0x80, 0x82, 0xA0, 0xA2, 0xC0, 0xC2, 0xE0, 0xE2,
}


class BackendValidator:
    def __init__(self, target: TargetDescription | None = None) -> None:
        self._target = target
        self._result = ValidationResult()

    def validate_object(self, object_bytes: bytes, fmt: str = "elf") -> ValidationResult:
        self._result = ValidationResult()

        if not object_bytes:
            self._result.add_error("object file is empty")
            return self._result

        if fmt == "elf":
            self._validate_elf(object_bytes)
        elif fmt == "pe":
            self._validate_pe(object_bytes)
        elif fmt == "macho":
            self._validate_macho(object_bytes)
        else:
            self._result.add_error(f"unsupported object format: {fmt}")

        return self._result

    def validate_executable(self, path: Path) -> ValidationResult:
        self._result = ValidationResult()

        if not path.exists():
            self._result.add_error(f"executable not found: {path}")
            return self._result

        if not path.is_file():
            self._result.add_error(f"path is not a file: {path}")
            return self._result

        data = path.read_bytes()

        if len(data) < 4:
            self._result.add_error("file too small to be a valid executable")
            return self._result

        magic = data[:4]
        if magic[:4] == _KNOWN_ELF_MAGIC:
            self._validate_elf(data)
        elif magic[:2] == _KNOWN_PE_MAGIC:
            self._validate_pe(data)
        elif magic == _KNOWN_MACHO_MAGIC:
            self._validate_macho(data)
        else:
            self._result.add_warning(f"unknown executable format (magic: {magic.hex()})")

        return self._result

    def validate_module(self, module: IRModule) -> ValidationResult:
        self._result = ValidationResult()

        if not module.name and module.function_count == 0:
            self._result.add_warning("module is empty (no name, no functions)")

        for func in module.functions:
            if not func.is_declaration:
                seen_blocks: set[str] = set()
                for block in func:
                    if block.name in seen_blocks:
                        self._result.add_error(
                            f"duplicate block name '{block.name}' in function '{func.name}'"
                        )
                    seen_blocks.add(block.name)

                    if not block.instructions:
                        self._result.add_error(
                            f"empty block '{block.name}' in function '{func.name}'"
                        )
                        continue

                    for inst in block:
                        if not self.validate_instruction(inst):
                            self._result.add_error(
                                f"invalid instruction in '{func.name}', block '{block.name}': {inst}"
                            )

        return self._result

    def validate_instruction(self, inst: Instruction) -> bool:
        try:
            oc = inst.opcode
            return oc is not None
        except Exception:
            return False

    def _validate_elf(self, data: bytes) -> None:
        if len(data) < 64:
            self._result.add_error("ELF header too short")
            return

        magic = data[:4]
        if magic != _KNOWN_ELF_MAGIC:
            self._result.add_error(f"invalid ELF magic: {magic.hex()}")
            return

        elf_class = data[4]
        if elf_class not in (1, 2):
            self._result.add_error(f"invalid ELF class: {elf_class}")
            return

        encoding = data[5]
        if encoding not in (1, 2):
            self._result.add_error(f"invalid ELF encoding: {encoding}")

        e_type = struct.unpack_from("<H", data, 16)[0]
        if e_type not in _VALID_ELF_TYPES:
            self._result.add_warning(f"unusual ELF type: {e_type}")

        e_machine = struct.unpack_from("<H", data, 18)[0]
        if e_machine == 0:
            self._result.add_error("ELF machine type is EM_NONE")
        elif e_machine not in _VALID_ELF_MACHINES:
            self._result.add_warning(f"unknown ELF machine: {e_machine}")

        e_shoff = struct.unpack_from("<Q", data, 40)[0]
        e_shentsize = struct.unpack_from("<H", data, 58)[0]
        e_shnum = struct.unpack_from("<H", data, 60)[0]

        if e_shoff > len(data):
            self._result.add_error("section header table offset out of bounds")
            return

        for i in range(e_shnum):
            shdr_off = e_shoff + i * e_shentsize
            if shdr_off + e_shentsize > len(data):
                self._result.add_error(f"section header {i} out of bounds")
                continue

            sh_flags = struct.unpack_from("<Q", data, shdr_off + 8)[0]
            if sh_flags not in _VALID_SECTION_FLAGS and sh_flags != 0:
                self._result.add_warning(f"section {i} has unusual flags: 0x{sh_flags:x}")

            sh_size = struct.unpack_from("<Q", data, shdr_off + 32)[0]
            sh_offset_in = struct.unpack_from("<Q", data, shdr_off + 24)[0]

            is_nobits = struct.unpack_from("<I", data, shdr_off + 4)[0] == 8
            if is_nobits:
                continue

            if sh_offset_in + sh_size > len(data) and sh_size > 0:
                self._result.add_error(
                    f"section {i} data at {sh_offset_in}+{sh_size} exceeds file size {len(data)}"
                )

    def _validate_pe(self, data: bytes) -> None:
        if len(data) < 64:
            self._result.add_error("PE file too short")
            return

        if data[:2] != _KNOWN_PE_MAGIC:
            self._result.add_error("invalid PE magic")
            return

        pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
        if pe_offset + 4 > len(data):
            self._result.add_error("PE signature offset out of bounds")
            return

        pe_sig = data[pe_offset:pe_offset + 4]
        if pe_sig != b"PE\x00\x00":
            self._result.add_error("invalid PE signature")
            return

        coff_header_start = pe_offset + 4
        if coff_header_start + 20 > len(data):
            self._result.add_error("COFF header out of bounds")
            return

        num_sections = struct.unpack_from("<H", data, coff_header_start + 2)[0]
        if num_sections == 0:
            self._result.add_warning("PE file has no sections")

    def _validate_macho(self, data: bytes) -> None:
        if len(data) < 32:
            self._result.add_error("Mach-O file too short")
            return

        magic = struct.unpack_from("<I", data, 0)[0]
        if magic != 0xFEEDFACF:
            self._result.add_error(f"invalid Mach-O magic: 0x{magic:08X}")
            return

        cputype = struct.unpack_from("<I", data, 4)[0]
        if cputype not in (0x01000007, 0x0100000C):
            self._result.add_warning(f"unusual Mach-O CPU type: 0x{cputype:08X}")

        filetype = struct.unpack_from("<I", data, 12)[0]
        if filetype not in (1, 2):
            self._result.add_warning(f"unusual Mach-O file type: {filetype}")
