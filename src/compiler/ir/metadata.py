"""
IR Metadata

Debug information and source-level metadata attached to IR instructions.
Preserves the connection between IR and source code for debugging,
profiling, and IDE tooling.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from .types import IRType


# ══════════════════════════════════════════════════════════════════
# Metadata Kinds
# ══════════════════════════════════════════════════════════════════


class MetadataKind(Enum):
    """Classification of metadata entries."""
    DEBUG_LOCATION = auto()
    SOURCE_FILE = auto()
    VARIABLE_NAME = auto()
    FUNCTION_NAME = auto()
    MODULE_NAME = auto()
    INSTRUCTION_REF = auto()
    CUSTOM = auto()


# ══════════════════════════════════════════════════════════════════
# Metadata (Abstract Base)
# ══════════════════════════════════════════════════════════════════


class Metadata(ABC):
    """Base class for all metadata entries."""
    __slots__ = ()

    @property
    @abstractmethod
    def kind(self) -> MetadataKind:
        """Metadata kind classification."""
        ...

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        ...

    @abstractmethod
    def __hash__(self) -> int:
        ...

    @abstractmethod
    def __repr__(self) -> str:
        ...


# ══════════════════════════════════════════════════════════════════
# Concrete Metadata
# ══════════════════════════════════════════════════════════════════


class DebugLocation(Metadata):
    """Source location for debug info."""
    __slots__ = ("_file", "_line", "_column", "_end_line", "_end_column", "_scope")

    def __init__(
        self,
        file: str,
        line: int,
        column: int = 0,
        end_line: int = 0,
        end_column: int = 0,
        scope: Optional[str] = None,
    ) -> None:
        object.__setattr__(self, "_file", file)
        object.__setattr__(self, "_line", line)
        object.__setattr__(self, "_column", column)
        object.__setattr__(self, "_end_line", end_line)
        object.__setattr__(self, "_end_column", end_column)
        object.__setattr__(self, "_scope", scope)

    @property
    def kind(self) -> MetadataKind:
        return MetadataKind.DEBUG_LOCATION

    @property
    def file(self) -> str:
        return self._file

    @property
    def line(self) -> int:
        return self._line

    @property
    def column(self) -> int:
        return self._column

    @property
    def end_line(self) -> int:
        return self._end_line

    @property
    def end_column(self) -> int:
        return self._end_column

    @property
    def scope(self) -> Optional[str]:
        return self._scope

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, DebugLocation)
                and self._file == other._file
                and self._line == other._line
                and self._column == other._column)

    def __hash__(self) -> int:
        return hash(("debug_loc", self._file, self._line, self._column))

    def __repr__(self) -> str:
        return f"{self._file}:{self._line}:{self._column}"


class SourceFile(Metadata):
    """Source file reference."""
    __slots__ = ("_filename", "_directory")

    def __init__(self, filename: str, directory: str = "") -> None:
        object.__setattr__(self, "_filename", filename)
        object.__setattr__(self, "_directory", directory)

    @property
    def kind(self) -> MetadataKind:
        return MetadataKind.SOURCE_FILE

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def directory(self) -> str:
        return self._directory

    @property
    def full_path(self) -> str:
        if self._directory:
            return f"{self._directory}/{self._filename}"
        return self._filename

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, SourceFile)
                and self._filename == other._filename
                and self._directory == other._directory)

    def __hash__(self) -> int:
        return hash(("source_file", self._filename, self._directory))

    def __repr__(self) -> str:
        return self.full_path


class VariableName(Metadata):
    """Original variable name from source code."""
    __slots__ = ("_name", "_mangled_name")

    def __init__(self, name: str, mangled_name: str = "") -> None:
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_mangled_name", mangled_name)

    @property
    def kind(self) -> MetadataKind:
        return MetadataKind.VARIABLE_NAME

    @property
    def name(self) -> str:
        return self._name

    @property
    def mangled_name(self) -> str:
        return self._mangled_name if self._mangled_name else self._name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, VariableName) and self._name == other._name

    def __hash__(self) -> int:
        return hash(("var_name", self._name))

    def __repr__(self) -> str:
        return self._name


class FunctionName(Metadata):
    """Original function name from source code."""
    __slots__ = ("_name", "_mangled_name")

    def __init__(self, name: str, mangled_name: str = "") -> None:
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_mangled_name", mangled_name)

    @property
    def kind(self) -> MetadataKind:
        return MetadataKind.FUNCTION_NAME

    @property
    def name(self) -> str:
        return self._name

    @property
    def mangled_name(self) -> str:
        return self._mangled_name if self._mangled_name else self._name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FunctionName) and self._name == other._name

    def __hash__(self) -> int:
        return hash(("func_name", self._name))

    def __repr__(self) -> str:
        return self._name


class ModuleName(Metadata):
    """Module name metadata."""
    __slots__ = ("_name",)

    def __init__(self, name: str) -> None:
        object.__setattr__(self, "_name", name)

    @property
    def kind(self) -> MetadataKind:
        return MetadataKind.MODULE_NAME

    @property
    def name(self) -> str:
        return self._name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ModuleName) and self._name == other._name

    def __hash__(self) -> int:
        return hash(("module_name", self._name))

    def __repr__(self) -> str:
        return self._name


class CustomMetadata(Metadata):
    """Arbitrary key-value metadata."""
    __slots__ = ("_key", "_value")

    def __init__(self, key: str, value: Any) -> None:
        object.__setattr__(self, "_key", key)
        object.__setattr__(self, "_value", value)

    @property
    def kind(self) -> MetadataKind:
        return MetadataKind.CUSTOM

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self) -> Any:
        return self._value

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, CustomMetadata)
                and self._key == other._key
                and self._value == other._value)

    def __hash__(self) -> int:
        return hash(("custom_meta", self._key, str(self._value)))

    def __repr__(self) -> str:
        return f"{self._key}={self._value}"


# ══════════════════════════════════════════════════════════════════
# Metadata Collection
# ══════════════════════════════════════════════════════════════════


class MetadataCollection:
    """A collection of metadata entries attached to an IR element."""
    __slots__ = ("_entries",)

    def __init__(self) -> None:
        object.__setattr__(self, "_entries", {})

    def add(self, meta: Metadata) -> None:
        """Add a metadata entry."""
        self._entries[meta.kind] = meta

    def get(self, kind: MetadataKind) -> Optional[Metadata]:
        """Get metadata by kind."""
        return self._entries.get(kind)

    def has(self, kind: MetadataKind) -> bool:
        """Check if metadata of this kind exists."""
        return kind in self._entries

    def remove(self, kind: MetadataKind) -> Optional[Metadata]:
        """Remove and return metadata by kind."""
        return self._entries.pop(kind, None)

    @property
    def debug_location(self) -> Optional[DebugLocation]:
        """Get the debug location, if present."""
        meta = self.get(MetadataKind.DEBUG_LOCATION)
        return meta if isinstance(meta, DebugLocation) else None

    @property
    def source_file(self) -> Optional[SourceFile]:
        """Get the source file, if present."""
        meta = self.get(MetadataKind.SOURCE_FILE)
        return meta if isinstance(meta, SourceFile) else None

    @property
    def entries(self) -> Dict[MetadataKind, Metadata]:
        return dict(self._entries)

    @property
    def is_empty(self) -> bool:
        return len(self._entries) == 0

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries.values())

    def __repr__(self) -> str:
        entries = ", ".join(repr(m) for m in self._entries.values())
        return f"Metadata({entries})"


# ══════════════════════════════════════════════════════════════════
# Metadata Utilities
# ══════════════════════════════════════════════════════════════════


def make_debug_location(
    file: str,
    line: int,
    column: int = 0,
    scope: Optional[str] = None,
) -> DebugLocation:
    """Create a debug location metadata."""
    return DebugLocation(file, line, column, scope=scope)


def make_source_file(filename: str, directory: str = "") -> SourceFile:
    """Create source file metadata."""
    return SourceFile(filename, directory)
