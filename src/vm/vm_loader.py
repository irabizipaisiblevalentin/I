"""IVM Loader — loads and validates bytecode chunks."""
from __future__ import annotations

import struct
from typing import Any

from compiler.codegen.bytecode import Chunk, Instruction, OpCode
from vm.vm_bytecode import IVMChunk, IVMInstruction, IVMOpcode


class BytecodeFormat:
    """Binary bytecode format specification."""
    MAGIC = b"IBCM"
    VERSION = 1
    HEADER_SIZE = 16

    @staticmethod
    def header() -> bytes:
        return (
            BytecodeFormat.MAGIC
            + struct.pack(">H", BytecodeFormat.VERSION)
            + struct.pack(">H", 0)
            + struct.pack(">I", 0)
            + struct.pack(">I", 0)
        )


class VMVerifier:
    """Bytecode verifier — validates bytecode before execution."""

    __slots__ = ("_errors",)

    VALID_OPCODES = set(range(0, 89))

    ARG_REQUIRED = {
        "LOAD_CONST", "LOAD_LOCAL", "STORE_LOCAL",
        "LOAD_GLOBAL", "STORE_GLOBAL",
        "JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE", "JUMP_IF_FALSE_POP", "LOOP",
        "CALL", "BUILD_LIST", "BUILD_MAP", "BUILD_SET", "BUILD_TUPLE",
        "MAKE_FUNCTION", "MAKE_CLOSURE",
    }

    BRANCH_OPS = {
        "JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE", "JUMP_IF_FALSE_POP", "LOOP",
    }

    def __init__(self) -> None:
        self._errors: list[str] = []

    @property
    def errors(self) -> list[str]:
        return list(self._errors)

    @property
    def is_valid(self) -> bool:
        return len(self._errors) == 0

    @staticmethod
    def _stack_effect(inst: Any) -> int:
        name = getattr(inst.opcode, "name", str(inst.opcode))
        if name in ("LOAD_CONST", "LOAD_NULL", "LOAD_TRUE", "LOAD_FALSE",
                    "LOAD_LOCAL", "LOAD_GLOBAL", "LOAD_FREE",
                    "DUP", "NEW_INSTANCE", "MAKE_FUNCTION", "MAKE_CLOSURE",
                    "LOAD_FAST", "GET_STATIC", "GET_FIELD", "GET_ATTR"):
            return 1
        if name in ("STORE_LOCAL", "STORE_GLOBAL", "STORE_FAST", "PUT_STATIC",
                    "PUT_FIELD", "POP", "JUMP_IF_FALSE_POP"):
            return -1
        if name in ("ADD", "SUB", "MUL", "DIV", "MOD",
                    "BIT_AND", "BIT_OR", "BIT_XOR", "SHIFT_LEFT", "SHIFT_RIGHT",
                    "EQ", "NEQ", "LT", "LTE", "GT", "GTE", "AND", "OR",
                    "GET_ITEM", "INSTANCE_OF"):
            return -1
        if name in ("SET_ITEM", "SET_ATTR"):
            return -2
        if name == "SLICE":
            return -3
        if name in ("BUILD_LIST", "BUILD_MAP", "BUILD_SET", "BUILD_TUPLE",
                    "NEW_ARRAY", "NEW_OBJECT"):
            return 1 - (inst.arg or 0)
        if name == "CALL":
            return -(inst.arg or 0)
        if name in ("INVOKE", "INVOKE_VIRTUAL", "INVOKE_INTERFACE"):
            return -(inst.arg or 0)
        if name == "NEW_STRUCT":
            return -(getattr(inst, "arg2", 0) or 0)
        return 0

    def verify(self, chunk: Chunk) -> bool:
        self._errors.clear()
        code = chunk.code
        depth = 0

        for i, inst in enumerate(code):
            if not isinstance(inst, (Instruction, IVMInstruction)):
                self._errors.append(f"offset {i}: not an Instruction")
                continue

            opcode_val = inst.opcode.value if hasattr(inst.opcode, 'value') else inst.opcode
            if opcode_val not in self.VALID_OPCODES:
                self._errors.append(
                    f"offset {i}: invalid opcode {opcode_val}"
                )
                continue

            name = getattr(inst.opcode, "name", str(inst.opcode))

            if name in self.ARG_REQUIRED and inst.arg is None:
                self._errors.append(
                    f"offset {i}: {name} requires an argument"
                )

            if name in self.BRANCH_OPS and inst.arg is not None:
                if not 0 <= inst.arg < len(code):
                    self._errors.append(
                        f"offset {i}: branch target {inst.arg} out of range"
                    )

            depth += self._stack_effect(inst)
            if depth < 0:
                self._errors.append(
                    f"offset {i}: stack underflow ({name})"
                )
                depth = 0

        return self.is_valid


class VMLoader:
    """Loads bytecode chunks and prepares them for execution."""

    __slots__ = ("_verifier", "_enable_verification")

    def __init__(self, enable_verification: bool = True) -> None:
        self._verifier = VMVerifier()
        self._enable_verification = enable_verification

    @property
    def verifier(self) -> VMVerifier:
        return self._verifier

    def load_chunk(self, chunk: Chunk) -> Chunk:
        """Load and optionally verify a bytecode chunk."""
        if self._enable_verification:
            if not self._verifier.verify(chunk):
                raise ValueError(
                    f"bytecode verification failed: {self._verifier.errors}"
                )
        return chunk

    def load_bytes(self, data: bytes) -> Chunk:
        """Deserialize a chunk from binary data."""
        if len(data) < BytecodeFormat.HEADER_SIZE:
            raise ValueError("invalid bytecode: too short")

        magic = data[:4]
        if magic != BytecodeFormat.MAGIC:
            raise ValueError(f"invalid bytecode: bad magic {magic!r}")

        version = struct.unpack(">H", data[4:6])[0]
        if version != BytecodeFormat.VERSION:
            raise ValueError(f"unsupported bytecode version: {version}")

        offset = BytecodeFormat.HEADER_SIZE
        const_count = struct.unpack(">I", data[offset:offset + 4])[0]
        offset += 4

        constants = []
        for _ in range(const_count):
            type_tag = data[offset]
            offset += 1
            if type_tag == 0:
                constants.append(None)
            elif type_tag == 1:
                val = struct.unpack(">q", data[offset:offset + 8])[0]
                offset += 8
                constants.append(val)
            elif type_tag == 2:
                val = struct.unpack(">d", data[offset:offset + 8])[0]
                offset += 8
                constants.append(val)
            elif type_tag == 3:
                val = data[offset] != 0
                offset += 1
                constants.append(val)
            elif type_tag == 4:
                slen = struct.unpack(">H", data[offset:offset + 2])[0]
                offset += 2
                val = data[offset:offset + slen].decode("utf-8")
                offset += slen
                constants.append(val)
            else:
                raise ValueError(f"unknown constant type tag: {type_tag}")

        code_count = struct.unpack(">I", data[offset:offset + 4])[0]
        offset += 4

        instructions = []
        for _ in range(code_count):
            opcode_val = data[offset]
            offset += 1
            has_arg = (opcode_val & 0x80) != 0
            opcode_val = opcode_val & 0x7F
            arg = None
            if has_arg:
                arg = struct.unpack(">H", data[offset:offset + 2])[0]
                offset += 2
            try:
                opcode = IVMOpcode(opcode_val)
            except ValueError:
                raise ValueError(f"unknown opcode: {opcode_val}")
            instructions.append(IVMInstruction(opcode=opcode, arg=arg, line=0))

        name = ""
        name_len = struct.unpack(">H", data[offset:offset + 2])[0]
        offset += 2
        if name_len > 0:
            name = data[offset:offset + name_len].decode("utf-8")
            offset += name_len

        chunk = IVMChunk(name=name)
        chunk.code = instructions
        for const in constants:
            chunk.add_constant(const)
        return chunk

    def save_bytes(self, chunk: Chunk) -> bytes:
        """Serialize a chunk to binary data."""
        parts = [BytecodeFormat.header()]

        const_count = len(chunk.constants)
        parts.append(struct.pack(">I", const_count))

        for const in chunk.constants:
            if const is None:
                parts.append(b"\x00")
            elif isinstance(const, bool):
                parts.append(b"\x03")
                parts.append(b"\x01" if const else b"\x00")
            elif isinstance(const, int):
                parts.append(b"\x01")
                parts.append(struct.pack(">q", const))
            elif isinstance(const, float):
                parts.append(b"\x02")
                parts.append(struct.pack(">d", const))
            elif isinstance(const, str):
                parts.append(b"\x04")
                encoded = const.encode("utf-8")
                parts.append(struct.pack(">H", len(encoded)))
                parts.append(encoded)
            else:
                parts.append(b"\x00")

        code_count = len(chunk.code)
        parts.append(struct.pack(">I", code_count))

        for inst in chunk.code:
            opcode_val = inst.opcode.value & 0x7F
            if inst.arg is not None:
                opcode_val |= 0x80
                parts.append(bytes([opcode_val]))
                parts.append(struct.pack(">H", inst.arg))
            else:
                parts.append(bytes([opcode_val]))

        name_bytes = chunk.name.encode("utf-8")
        parts.append(struct.pack(">H", len(name_bytes)))
        parts.append(name_bytes)

        return b"".join(parts)

    def save_file(self, chunk: Chunk, path: str) -> None:
        """Save a chunk to a file."""
        data = self.save_bytes(chunk)
        with open(path, "wb") as f:
            f.write(data)

    def load_file(self, path: str) -> Chunk:
        """Load a chunk from a file."""
        with open(path, "rb") as f:
            data = f.read()
        return self.load_bytes(data)
