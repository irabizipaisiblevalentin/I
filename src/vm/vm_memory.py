"""IVM memory management — heap, stack, object allocator, pools."""
from __future__ import annotations

import sys
from typing import Any


class StackOverflowError(RuntimeError):
    pass


class HeapOverflowError(RuntimeError):
    pass


class Stack:
    """Fixed-size value stack with overflow protection."""

    __slots__ = ("_data", "_top", "_size")

    def __init__(self, max_size: int = 1024) -> None:
        self._data: list[Any] = [None] * max_size
        self._top: int = 0
        self._size: int = max_size

    @property
    def top(self) -> int:
        return self._top

    @property
    def size(self) -> int:
        return self._size

    def push(self, value: Any) -> None:
        if self._top >= self._size:
            raise StackOverflowError(f"stack overflow: max depth {self._size}")
        self._data[self._top] = value
        self._top += 1

    def pop(self) -> Any:
        if self._top <= 0:
            raise IndexError("stack underflow")
        self._top -= 1
        val = self._data[self._top]
        self._data[self._top] = None
        return val

    def peek(self) -> Any:
        if self._top <= 0:
            raise IndexError("stack empty")
        return self._data[self._top - 1]

    def peek_at(self, offset: int) -> Any:
        idx = self._top - 1 - offset
        if idx < 0 or idx >= self._top:
            raise IndexError(f"stack peek out of range: offset={offset}")
        return self._data[idx]

    def set_at(self, offset: int, value: Any) -> None:
        idx = self._top - 1 - offset
        if idx < 0 or idx >= self._top:
            raise IndexError(f"stack set out of range: offset={offset}")
        self._data[idx] = value

    def dup(self) -> None:
        if self._top <= 0:
            raise IndexError("stack empty")
        val = self._data[self._top - 1]
        self.push(val)

    def swap(self) -> None:
        if self._top < 2:
            raise IndexError("stack too small for swap")
        a = self._data[self._top - 1]
        b = self._data[self._top - 2]
        self._data[self._top - 1] = b
        self._data[self._top - 2] = a

    def rot_three(self) -> None:
        if self._top < 3:
            raise IndexError("stack too small for rot_three")
        a = self._data[self._top - 1]
        b = self._data[self._top - 2]
        c = self._data[self._top - 3]
        self._data[self._top - 1] = b
        self._data[self._top - 2] = c
        self._data[self._top - 3] = a

    def clear(self) -> None:
        for i in range(self._top):
            self._data[i] = None
        self._top = 0

    def truncate(self, new_size: int) -> None:
        if new_size < self._top:
            for i in range(new_size, self._top):
                self._data[i] = None
            self._top = new_size

    def to_list(self) -> list[Any]:
        return list(self._data[:self._top])

    def __len__(self) -> int:
        return self._top

    def __bool__(self) -> bool:
        return self._top > 0


class CallFrame:
    """A single call frame on the VM call stack."""
    __slots__ = (
        "_chunk", "_ip", "_base_pointer", "_function_name",
        "_line", "_closure",
    )

    def __init__(
        self,
        chunk: Any,
        ip: int = 0,
        base_pointer: int = 0,
        function_name: str = "<module>",
        line: int = 0,
        closure: Any = None,
    ) -> None:
        self._chunk = chunk
        self._ip = ip
        self._base_pointer = base_pointer
        self._function_name = function_name
        self._line = line
        self._closure = closure

    @property
    def chunk(self) -> Any:
        return self._chunk

    @property
    def ip(self) -> int:
        return self._ip

    @ip.setter
    def ip(self, value: int) -> None:
        self._ip = value

    @property
    def base_pointer(self) -> int:
        return self._base_pointer

    @property
    def function_name(self) -> str:
        return self._function_name

    @property
    def line(self) -> int:
        return self._line

    @line.setter
    def line(self, value: int) -> None:
        self._line = value

    @property
    def closure(self) -> Any:
        return self._closure

    def advance(self) -> None:
        self._ip += 1

    def read_byte(self) -> int:
        code = self._chunk.code
        if self._ip >= len(code):
            return -1
        inst = code[self._ip]
        self._ip += 1
        return inst.opcode.value if hasattr(inst.opcode, 'value') else inst.opcode

    def __repr__(self) -> str:
        return f"CallFrame({self._function_name!r}, ip={self._ip}, bp={self._base_pointer})"


class Heap:
    """Simple object heap with allocation tracking."""

    __slots__ = (
        "_objects", "_size", "_max_size", "_allocated",
        "_collections", "_total_allocated", "_threshold",
    )

    def __init__(self, initial_size: int = 1024 * 1024, threshold: int = 1024) -> None:
        self._objects: list[Any] = []
        self._size: int = 0
        self._max_size: int = initial_size
        self._allocated: int = 0
        self._collections: int = 0
        self._total_allocated: int = 0
        self._threshold: int = threshold

    @property
    def allocated(self) -> int:
        return self._allocated

    @property
    def size(self) -> int:
        return self._size

    @property
    def collections(self) -> int:
        return self._collections

    @property
    def total_allocated(self) -> int:
        return self._total_allocated

    @property
    def needs_gc(self) -> bool:
        return self._allocated >= self._threshold

    def allocate(self, obj: Any) -> Any:
        self._objects.append(obj)
        self._size += 1
        self._allocated += 1
        self._total_allocated += 1
        return obj

    def collect(self) -> int:
        before = self._size
        self._objects = [o for o in self._objects if o is not None]
        self._size = len(self._objects)
        self._allocated = self._size
        self._collections += 1
        return before - self._size

    def track(self, obj: Any) -> None:
        self._objects.append(obj)
        self._size += 1

    def untrack(self, obj: Any) -> None:
        try:
            self._objects.remove(obj)
            self._size -= 1
        except ValueError:
            pass

    def get_stats(self) -> dict[str, int]:
        return {
            "objects": self._size,
            "allocated": self._allocated,
            "max_size": self._max_size,
            "collections": self._collections,
            "total_allocated": self._total_allocated,
        }


class StringPool:
    """Interned string pool for deduplication."""

    __slots__ = ("_strings", "_by_id", "_next_id")

    def __init__(self) -> None:
        self._strings: dict[str, int] = {}
        self._by_id: dict[int, str] = {}
        self._next_id: int = 0

    def intern(self, s: str) -> int:
        if s in self._strings:
            return self._strings[s]
        idx = self._next_id
        self._next_id += 1
        self._strings[s] = idx
        self._by_id[idx] = s
        return idx

    def lookup(self, idx: int) -> str:
        return self._by_id.get(idx, "")

    def resolve(self, s: str) -> int:
        return self._strings.get(s, -1)

    @property
    def count(self) -> int:
        return self._next_id

    def __len__(self) -> int:
        return self._next_id


class ConstantPool:
    """Constant pool for a chunk/module."""

    __slots__ = ("_constants", "_index")

    def __init__(self) -> None:
        self._constants: list[Any] = []
        self._index: dict[int, int] = {}

    def add(self, value: Any) -> int:
        for i, c in enumerate(self._constants):
            if c == value and type(c) is type(value):
                return i
        idx = len(self._constants)
        self._constants.append(value)
        return idx

    def get(self, idx: int) -> Any:
        if idx < 0 or idx >= len(self._constants):
            return None
        return self._constants[idx]

    def __len__(self) -> int:
        return len(self._constants)

    def __iter__(self):
        return iter(self._constants)

    def to_list(self) -> list[Any]:
        return list(self._constants)
