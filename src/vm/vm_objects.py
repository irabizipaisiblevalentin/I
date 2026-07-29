"""IVM object representation — heap-allocated values."""
from __future__ import annotations

from typing import Any, Optional


class VMObject:
    """Base class for all heap-allocated VM objects."""
    __slots__ = ("_gc_next", "_gc_marked", "_gc_gen")

    def __init__(self) -> None:
        self._gc_next: VMObject | None = None
        self._gc_marked: bool = False
        self._gc_gen: int = 0

    @property
    def gc_marked(self) -> bool:
        return self._gc_marked

    @gc_marked.setter
    def gc_marked(self, value: bool) -> None:
        self._gc_marked = value

    @property
    def gc_gen(self) -> int:
        return self._gc_gen

    @gc_gen.setter
    def gc_gen(self, value: int) -> None:
        self._gc_gen = value

    @property
    def gc_next(self) -> VMObject | None:
        return self._gc_next

    @gc_next.setter
    def gc_next(self, value: VMObject | None) -> None:
        self._gc_next = value

    def gc_trace(self) -> list[Any]:
        return []

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class VMString(VMObject):
    """VM string value."""
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        super().__init__()
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f'VMString({self._value!r})'

    def __eq__(self, other: object) -> bool:
        if isinstance(other, VMString):
            return self._value == other._value
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

    def __len__(self) -> int:
        return len(self._value)


class VMList(VMObject):
    """VM list value."""
    __slots__ = ("_elements",)

    def __init__(self, elements: list[Any] | None = None) -> None:
        super().__init__()
        self._elements = list(elements) if elements is not None else []

    @property
    def elements(self) -> list[Any]:
        return self._elements

    def get(self, index: int) -> Any:
        if index < 0 or index >= len(self._elements):
            raise IndexError(f"list index out of range: {index}")
        return self._elements[index]

    def set(self, index: int, value: Any) -> None:
        if index < 0 or index >= len(self._elements):
            raise IndexError(f"list index out of range: {index}")
        self._elements[index] = value

    def append(self, value: Any) -> None:
        self._elements.append(value)

    def slice(self, start: int, stop: int, step: int = 1) -> VMList:
        return VMList(self._elements[start:stop:step])

    def to_list(self) -> list[Any]:
        return list(self._elements)

    def gc_trace(self) -> list[Any]:
        return list(self._elements)

    def __len__(self) -> int:
        return len(self._elements)

    def __repr__(self) -> str:
        return f"VMList({self._elements!r})"


class VMMap(VMObject):
    """VM map (dictionary) value."""
    __slots__ = ("_entries", "_keys")

    def __init__(self) -> None:
        super().__init__()
        self._entries: dict[int, Any] = {}
        self._keys: list[Any] = []

    @property
    def entries(self) -> dict[int, Any]:
        return self._entries

    def get(self, key: Any) -> Any:
        k = id(key) if isinstance(key, VMObject) else key
        return self._entries.get(k)

    def set(self, key: Any, value: Any) -> None:
        k = id(key) if isinstance(key, VMObject) else key
        self._entries[k] = value

    def gc_trace(self) -> list[Any]:
        return list(self._entries.values())

    def __len__(self) -> int:
        return len(self._entries)

    def __repr__(self) -> str:
        return f"VMMap({len(self._entries)} entries)"


class VMSet(VMObject):
    """VM set value."""
    __slots__ = ("_elements",)

    def __init__(self) -> None:
        super().__init__()
        self._elements: set[int] = set()

    @property
    def elements(self) -> set[int]:
        return self._elements

    def add(self, value: Any) -> None:
        self._elements.add(id(value) if isinstance(value, VMObject) else hash(value))

    def gc_trace(self) -> list[Any]:
        return []

    def __len__(self) -> int:
        return len(self._elements)


class VMTuple(VMObject):
    """VM tuple value (immutable)."""
    __slots__ = ("_elements",)

    def __init__(self, elements: tuple[Any, ...] | None = None) -> None:
        super().__init__()
        self._elements = tuple(elements) if elements is not None else ()

    @property
    def elements(self) -> tuple[Any, ...]:
        return self._elements

    def gc_trace(self) -> list[Any]:
        return list(self._elements)

    def __len__(self) -> int:
        return len(self._elements)

    def __repr__(self) -> str:
        return f"VMTuple({self._elements!r})"


class VMStruct(VMObject):
    """VM struct instance."""
    __slots__ = ("_type_name", "_fields", "_field_names")

    def __init__(self, type_name: str, field_names: list[str]) -> None:
        super().__init__()
        self._type_name = type_name
        self._field_names = field_names
        self._fields: dict[str, Any] = {name: None for name in field_names}

    @property
    def type_name(self) -> str:
        return self._type_name

    @property
    def field_names(self) -> list[str]:
        return self._field_names

    def get_field(self, name: str) -> Any:
        return self._fields.get(name)

    def set_field(self, name: str, value: Any) -> None:
        if name not in self._fields:
            raise AttributeError(f"struct '{self._type_name}' has no field '{name}'")
        self._fields[name] = value

    def gc_trace(self) -> list[Any]:
        return [v for v in self._fields.values() if isinstance(v, VMObject)]

    def __repr__(self) -> str:
        return f"VMStruct({self._type_name}, {self._fields})"


class VMClosure(VMObject):
    """VM closure — function + captured free variables."""
    __slots__ = ("_chunk", "_free_vars", "_name", "_arity")

    def __init__(self, chunk: Any, name: str = "<lambda>", arity: int = 0) -> None:
        super().__init__()
        self._chunk = chunk
        self._name = name
        self._arity = arity
        self._free_vars: list[Any] = []

    @property
    def chunk(self) -> Any:
        return self._chunk

    @property
    def name(self) -> str:
        return self._name

    @property
    def arity(self) -> int:
        return self._arity

    @property
    def free_vars(self) -> list[Any]:
        return self._free_vars

    def capture(self, values: list[Any]) -> None:
        self._free_vars = list(values)

    def gc_trace(self) -> list[Any]:
        return [v for v in self._free_vars if isinstance(v, VMObject)]

    def __repr__(self) -> str:
        return f"VMClosure({self._name!r}, arity={self._arity})"


class VMException(VMObject):
    """VM exception value."""
    __slots__ = ("_message", "_type_name", "_stack_trace", "_cause")

    def __init__(self, message: str, type_name: str = "RuntimeError") -> None:
        super().__init__()
        self._message = message
        self._type_name = type_name
        self._stack_trace: list[dict[str, Any]] = []
        self._cause: VMException | None = None

    @property
    def message(self) -> str:
        return self._message

    @property
    def type_name(self) -> str:
        return self._type_name

    @property
    def stack_trace(self) -> list[dict[str, Any]]:
        return self._stack_trace

    @stack_trace.setter
    def stack_trace(self, value: list[dict[str, Any]]) -> None:
        self._stack_trace = value

    @property
    def cause(self) -> VMException | None:
        return self._cause

    def with_cause(self, cause: VMException) -> VMException:
        self._cause = cause
        return self

    def __repr__(self) -> str:
        return f"VMException({self._type_name}: {self._message!r})"


class VMIterator(VMObject):
    """VM iterator for for-in loops."""
    __slots__ = ("_source", "_index", "_length")

    def __init__(self, source: Any) -> None:
        super().__init__()
        self._source = source
        self._index = 0
        if isinstance(source, (list, VMList, tuple, VMTuple)):
            self._length = len(source)
        elif isinstance(source, str):
            self._length = len(source)
        elif isinstance(source, VMMap):
            self._length = len(source)
        else:
            self._length = 0

    @property
    def source(self) -> Any:
        return self._source

    @property
    def index(self) -> int:
        return self._index

    def has_next(self) -> bool:
        return self._index < self._length

    def next(self) -> Any:
        if not self.has_next():
            raise StopIteration
        src = self._source
        i = self._index
        self._index += 1
        if isinstance(src, VMList):
            return src.get(i)
        elif isinstance(src, VMMap):
            keys = list(src.entries.keys())
            if i < len(keys):
                return keys[i]
            raise StopIteration
        else:
            return src[i]

    def __repr__(self) -> str:
        return f"VMIterator(index={self._index}, length={self._length})"
