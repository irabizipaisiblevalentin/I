"""
Bytecode definitions for the I programming language.

This module defines the bytecode instruction set and related structures.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, List, Optional


class OpCode(Enum):
    """Bytecode operation codes."""
    
    # Constants and Literals
    LOAD_CONST = auto()
    LOAD_NULL = auto()
    LOAD_TRUE = auto()
    LOAD_FALSE = auto()
    
    # Variable Operations
    LOAD_LOCAL = auto()
    STORE_LOCAL = auto()
    LOAD_GLOBAL = auto()
    STORE_GLOBAL = auto()
    LOAD_FREE = auto()
    
    # Stack Operations
    POP = auto()
    DUP = auto()
    SWAP = auto()
    ROT_THREE = auto()
    
    # Arithmetic Operations
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    NEG = auto()
    
    # Bitwise Operations
    BIT_AND = auto()
    BIT_OR = auto()
    BIT_XOR = auto()
    BIT_NOT = auto()
    LEFT_SHIFT = auto()
    RIGHT_SHIFT = auto()
    
    # Comparison Operations
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()
    
    # Logical Operations
    AND = auto()
    OR = auto()
    NOT = auto()
    
    # Control Flow
    JUMP = auto()
    JUMP_IF_FALSE = auto()
    JUMP_IF_TRUE = auto()
    JUMP_IF_FALSE_POP = auto()
    LOOP = auto()
    CALL = auto()
    RETURN = auto()
    
    # Collections
    BUILD_LIST = auto()
    BUILD_MAP = auto()
    BUILD_SET = auto()
    BUILD_TUPLE = auto()
    GET_ITEM = auto()
    SET_ITEM = auto()
    SLICE = auto()
    
    # Objects
    GET_ATTR = auto()
    SET_ATTR = auto()
    NEW_STRUCT = auto()
    NEW_INSTANCE = auto()
    
    # Functions
    MAKE_FUNCTION = auto()
    MAKE_CLOSURE = auto()
    GET_ITER = auto()
    FOR_ITER = auto()
    
    # Exceptions
    RAISE = auto()
    SETUP_TRY = auto()
    POP_BLOCK = auto()
    
    # Other
    NOP = auto()
    HALT = auto()


@dataclass
class Instruction:
    """A single bytecode instruction."""
    
    opcode: OpCode
    arg: Optional[int] = None
    line: int = 0
    
    def __repr__(self) -> str:
        if self.arg is not None:
            return f"{self.opcode.name} {self.arg}"
        return self.opcode.name


@dataclass
class Chunk:
    """A chunk of bytecode with constants and metadata."""
    
    name: str
    code: List[Instruction]
    constants: List[Any]
    
    def __init__(self, name: str):
        self.name = name
        self.code: List[Instruction] = []
        self.constants: List[Any] = []
    
    def emit(self, opcode: OpCode, arg: Optional[int] = None, line: int = 0) -> int:
        """Emit an instruction and return its position."""
        instruction = Instruction(opcode, arg, line)
        self.code.append(instruction)
        return len(self.code) - 1
    
    def add_constant(self, value: Any) -> int:
        """Add a constant to the chunk and return its index."""
        self.constants.append(value)
        return len(self.constants) - 1
    
    def disassemble(self) -> str:
        """Disassemble the chunk to a human-readable format."""
        lines = []
        lines.append(f"== {self.name} ==")
        lines.append(f"Constants: {len(self.constants)}")
        lines.append(f"Instructions: {len(self.code)}")
        lines.append("")
        
        for i, constant in enumerate(self.constants):
            lines.append(f"  [{i}] {repr(constant)}")
        
        lines.append("")
        
        for i, instruction in enumerate(self.code):
            lines.append(f"  {i:04d}: {instruction}")
        
        return "\n".join(lines)
