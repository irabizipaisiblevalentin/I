"""IVM Bytecode — extended opcode definitions and binary format."""
from __future__ import annotations

from enum import IntEnum
from typing import Any, Optional


class IVMOpcode(IntEnum):
    """Extended IVM opcode set — superset of the base OpCode."""
    HALT = 0
    LOAD_CONST = 1
    LOAD_NULL = 2
    LOAD_TRUE = 3
    LOAD_FALSE = 4
    LOAD_LOCAL = 5
    STORE_LOCAL = 6
    LOAD_GLOBAL = 7
    STORE_GLOBAL = 8
    LOAD_FREE = 9
    POP = 10
    DUP = 11
    SWAP = 12
    ROT_THREE = 13
    ADD = 14
    SUB = 15
    MUL = 16
    DIV = 17
    MOD = 18
    NEG = 19
    BIT_AND = 20
    BIT_OR = 21
    BIT_XOR = 22
    BIT_NOT = 23
    LEFT_SHIFT = 24
    RIGHT_SHIFT = 25
    EQ = 26
    NEQ = 27
    LT = 28
    LTE = 29
    GT = 30
    GTE = 31
    AND = 32
    OR = 33
    NOT = 34
    JUMP = 35
    JUMP_IF_FALSE = 36
    JUMP_IF_TRUE = 37
    JUMP_IF_FALSE_POP = 38
    LOOP = 39
    CALL = 40
    RETURN = 41
    BUILD_LIST = 42
    BUILD_MAP = 43
    BUILD_SET = 44
    BUILD_TUPLE = 45
    GET_ITEM = 46
    SET_ITEM = 47
    SLICE = 48
    GET_ATTR = 49
    SET_ATTR = 50
    NEW_STRUCT = 51
    NEW_INSTANCE = 52
    MAKE_FUNCTION = 53
    MAKE_CLOSURE = 54
    GET_ITER = 55
    FOR_ITER = 56
    RAISE = 57
    SETUP_TRY = 58
    POP_BLOCK = 59
    RESUME = 60
    NOP = 61

    INVOKE = 64
    INVOKE_VIRTUAL = 65
    INVOKE_INTERFACE = 66
    CHECK_CAST = 67
    INSTANCE_OF = 68
    NEW_ARRAY = 69
    NEW_OBJECT = 70
    GET_FIELD = 71
    PUT_FIELD = 72
    GET_STATIC = 73
    PUT_STATIC = 74
    LOAD_FAST = 75
    STORE_FAST = 76
    LOAD_ARG = 77
    STORE_ARG = 78
    ENTER_FRAME = 79
    EXIT_FRAME = 80
    YIELD = 81
    AWAIT = 82
    SEND = 83
    THROW = 84
    FINALLY = 85
    LOCK = 86
    UNLOCK = 87
    NOP2 = 88


class IVMInstruction:
    """An IVM bytecode instruction with metadata."""
    __slots__ = ("opcode", "arg", "arg2", "line", "column", "source_file")

    def __init__(self, opcode: IVMOpcode, arg: int = 0, arg2: int = 0,
                 line: int = 0, column: int = 0, source_file: str = "") -> None:
        self.opcode = opcode
        self.arg = arg
        self.arg2 = arg2
        self.line = line
        self.column = column
        self.source_file = source_file

    def __repr__(self) -> str:
        parts = [f"{self.opcode.name}"]
        if self.arg or self.arg2:
            parts.append(str(self.arg))
        if self.arg2:
            parts.append(str(self.arg2))
        return " ".join(parts)


class IVMChunk:
    """Extended bytecode chunk with source mapping."""

    __slots__ = ("_name", "_instructions", "_constants", "_functions",
                 "_line_table", "_source_files", "_version")

    def __init__(self, name: str = "<module>") -> None:
        self._name = name
        self._instructions: list[IVMInstruction] = []
        self._constants: list[Any] = []
        self._functions: list[IVMChunk] = []
        self._line_table: list[tuple[int, int]] = []
        self._source_files: list[str] = []
        self._version: int = 1

    @property
    def name(self) -> str:
        return self._name

    @property
    def instructions(self) -> list[IVMInstruction]:
        return self._instructions

    @property
    def code(self) -> list[IVMInstruction]:
        return self._instructions

    @code.setter
    def code(self, value: list[IVMInstruction]) -> None:
        self._instructions = value

    @property
    def constants(self) -> list[Any]:
        return self._constants

    @property
    def functions(self) -> list[IVMChunk]:
        return self._functions

    @property
    def version(self) -> int:
        return self._version

    def emit(self, opcode: IVMOpcode, arg: int = 0, arg2: int = 0,
             line: int = 0, column: int = 0, source_file: str = "") -> int:
        inst = IVMInstruction(
            opcode=opcode, arg=arg, arg2=arg2,
            line=line, column=column, source_file=source_file,
        )
        self._instructions.append(inst)
        return len(self._instructions) - 1

    def add_constant(self, value: Any) -> int:
        for i, c in enumerate(self._constants):
            if c == value and type(c) is type(value):
                return i
        idx = len(self._constants)
        self._constants.append(value)
        return idx

    def add_function(self, chunk: IVMChunk) -> int:
        idx = len(self._functions)
        self._functions.append(chunk)
        return idx

    def add_source_file(self, path: str) -> int:
        if path in self._source_files:
            return self._source_files.index(path)
        idx = len(self._source_files)
        self._source_files.append(path)
        return idx

    def record_line(self, line: int, offset: int) -> None:
        self._line_table.append((line, offset))

    def get_line(self, offset: int) -> int:
        result_line = 0
        for line, off in self._line_table:
            if off <= offset:
                result_line = line
            else:
                break
        return result_line

    @property
    def instruction_count(self) -> int:
        return len(self._instructions)

    @property
    def constant_count(self) -> int:
        return len(self._constants)

    def __repr__(self) -> str:
        return f"IVMChunk({self._name!r}, {len(self._instructions)} insts, {len(self._constants)} consts)"
