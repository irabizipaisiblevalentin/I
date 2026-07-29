"""ububazimurizo — ORM (Object-Relational Mapping) for UBUBIKO.

Provides entity mapping, field definitions, relationships,
repositories, change tracking, and query generation.
"""

from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Type, TypeVar, Union

T = TypeVar("T", bound="Entity")


class RelationshipType(enum.Enum):
    """Types of entity relationships."""

    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


@dataclass
class Relationship:
    """Defines a relationship between entities.

    Attributes:
        type: Relationship type.
        target: Target entity class name.
        foreign_key: Local foreign key field name.
        referenced_key: Referenced key in target entity.
        through: For many-to-many, the junction table.
        lazy: Whether to load lazily.
        cascade: Cascade operations (save, delete).
    """

    type: RelationshipType = RelationshipType.ONE_TO_MANY
    target: str = ""
    foreign_key: str = ""
    referenced_key: str = "id"
    through: str = ""
    lazy: bool = True
    cascade: bool = False


@dataclass
class Field:
    """Defines a field on an entity.

    Attributes:
        name: Field name.
        field_type: Python type.
        primary_key: Whether this is the primary key.
        unique: Whether values must be unique.
        nullable: Whether null is allowed.
        default: Default value.
        index: Whether to create an index.
        foreign_key: Reference to another entity's field.
        max_length: Maximum length for string fields.
        precision: Numeric precision.
        scale: Numeric scale.
        generated: Auto-generated value.
        metadata: Additional field metadata.
    """

    name: str = ""
    field_type: type = str
    primary_key: bool = False
    unique: bool = False
    nullable: bool = False
    default: Any = None
    index: bool = False
    foreign_key: str = ""
    max_length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    generated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_column_def(self) -> str:
        """Generate a SQL column definition string."""
        type_map: Dict[type, str] = {
            int: "INTEGER",
            float: "REAL",
            str: f"VARCHAR({self.max_length or 255})",
            bool: "BOOLEAN",
            bytes: "BLOB",
            datetime: "TIMESTAMP",
            uuid.UUID: "UUID",
        }
        col_type = type_map.get(self.field_type, "TEXT")
        parts = [self.name, col_type]
        if self.primary_key:
            parts.append("PRIMARY KEY")
        if self.unique:
            parts.append("UNIQUE")
        if not self.nullable:
            parts.append("NOT NULL")
        if self.default is not None:
            if isinstance(self.default, str):
                parts.append(f"DEFAULT '{self.default}'")
            else:
                parts.append(f"DEFAULT {self.default}")
        return " ".join(parts)


class EntityMeta(type):
    """Metaclass for Entity classes.

    Collects field definitions and table metadata from class attributes.
    """

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> type:
        fields: Dict[str, Field] = {}
        relationships: Dict[str, Relationship] = {}
        table_name = namespace.get("__table__", name.lower())

        for key, value in namespace.items():
            if isinstance(value, Field):
                if not value.name:
                    value.name = key
                fields[key] = value
            elif isinstance(value, Relationship):
                relationships[key] = value

        namespace["_fields"] = fields
        namespace["_relationships"] = relationships
        namespace["_table_name"] = table_name

        pk_fields = [f for f in fields.values() if f.primary_key]
        namespace["_pk_field"] = pk_fields[0] if pk_fields else Field(name="id", field_type=int, primary_key=True)
        namespace["_pk_name"] = namespace["_pk_field"].name

        return super().__new__(mcs, name, bases, namespace)


class Entity(metaclass=EntityMeta):
    """Base class for all database entities.

    Provides attribute-style field access, dirty tracking,
    serialization, and comparison.
    """

    __table__: str = ""

    def __init__(self, **kwargs: Any) -> None:
        self._initialized = False
        self._dirty: Set[str] = set()
        self._original: Dict[str, Any] = {}

        for name, field_def in self._fields.items():
            value = kwargs.get(name, field_def.default)
            object.__setattr__(self, name, value)
            self._original[name] = value

        for rel_name in self._relationships:
            object.__setattr__(self, rel_name, None)

        self._initialized = True

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if self._initialized and name in self._fields:
            self._dirty.add(name)

    @property
    def is_dirty(self) -> bool:
        """Whether any fields have been modified."""
        return len(self._dirty) > 0

    @property
    def dirty_fields(self) -> Set[str]:
        """Set of modified field names."""
        return set(self._dirty)

    @property
    def table_name(self) -> str:
        """The database table name for this entity."""
        return self._table_name

    @property
    def pk_value(self) -> Any:
        """The primary key value."""
        return getattr(self, self._pk_name)

    @pk_value.setter
    def pk_value(self, value: Any) -> None:
        setattr(self, self._pk_name, value)

    def clean(self) -> None:
        """Mark all fields as unmodified (called after save)."""
        self._dirty.clear()
        for name in self._fields:
            self._original[name] = getattr(self, name)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize entity to a dictionary."""
        result: Dict[str, Any] = {}
        for name in self._fields:
            result[name] = getattr(self, name)
        for rel_name in self._relationships:
            val = getattr(self, rel_name, None)
            if val is not None:
                if isinstance(val, list):
                    result[rel_name] = [v.to_dict() if isinstance(v, Entity) else v for v in val]
                elif isinstance(val, Entity):
                    result[rel_name] = val.to_dict()
                else:
                    result[rel_name] = val
        return result

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create an entity from a dictionary."""
        filtered = {k: v for k, v in data.items() if k in cls._fields}
        return cls(**filtered)

    def __repr__(self) -> str:
        pk = self.pk_value
        return f"<{type(self).__name__}({self._pk_name}={pk})>"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.pk_value is not None and self.pk_value == other.pk_value

    def __hash__(self) -> int:
        return hash((type(self), self.pk_value))


class ChangeTracker:
    """Tracks entity changes for persistence operations.

    Maintains sets of added, modified, and deleted entities
    and can flush changes to the database.
    """

    def __init__(self) -> None:
        self._added: Dict[Type[Entity], Dict[Any, Entity]] = {}
        self._modified: Dict[Type[Entity], Dict[Any, Entity]] = {}
        self._deleted: Dict[Type[Entity], Dict[Any, Entity]] = {}

    def track_add(self, entity: Entity) -> None:
        """Register an entity for insertion."""
        cls = type(entity)
        if cls not in self._added:
            self._added[cls] = {}
        self._added[cls][entity.pk_value] = entity

    def track_modify(self, entity: Entity) -> None:
        """Register an entity for update."""
        cls = type(entity)
        if cls not in self._modified:
            self._modified[cls] = {}
        self._modified[cls][entity.pk_value] = entity

    def track_delete(self, entity: Entity) -> None:
        """Register an entity for deletion."""
        cls = type(entity)
        if cls not in self._deleted:
            self._deleted[cls] = {}
        self._deleted[cls][entity.pk_value] = entity

    @property
    def has_changes(self) -> bool:
        """Whether any pending changes exist."""
        return bool(self._added or self._modified or self._deleted)

    def clear(self) -> None:
        """Clear all tracked changes."""
        self._added.clear()
        self._modified.clear()
        self._deleted.clear()

    def get_added(self, entity_class: Optional[Type[Entity]] = None) -> List[Entity]:
        if entity_class:
            return list(self._added.get(entity_class, {}).values())
        return [e for d in self._added.values() for e in d.values()]

    def get_modified(self, entity_class: Optional[Type[Entity]] = None) -> List[Entity]:
        if entity_class:
            return list(self._modified.get(entity_class, {}).values())
        return [e for d in self._modified.values() for e in d.values()]

    def get_deleted(self, entity_class: Optional[Type[Entity]] = None) -> List[Entity]:
        if entity_class:
            return list(self._deleted.get(entity_class, {}).values())
        return [e for d in self._deleted.values() for e in d.values()]


class Repository:
    """Generic repository providing CRUD operations for an entity type.

    Attributes:
        entity_class: The entity class managed by this repository.
        adapter: The database adapter used for operations.
    """

    def __init__(self, entity_class: Type[Entity], adapter: Any) -> None:
        self._entity_class = entity_class
        self._adapter = adapter
        self._change_tracker = ChangeTracker()

    @property
    def entity_class(self) -> Type[Entity]:
        return self._entity_class

    @property
    def adapter(self) -> Any:
        return self._adapter

    @property
    def change_tracker(self) -> ChangeTracker:
        return self._change_tracker

    def _table_name(self) -> str:
        return self._entity_class._table_name

    def _pk_name(self) -> str:
        return self._entity_class._pk_name

    def _fields(self) -> Dict[str, Field]:
        return self._entity_class._fields

    def _build_insert(self, entity: Entity) -> str:
        fields = [f for f in self._fields() if f != self._pk_name() or getattr(entity, f) is not None]
        col_names = ", ".join(fields)
        placeholders = ", ".join(f":{f}" for f in fields)
        return f"INSERT INTO {self._table_name()} ({col_names}) VALUES ({placeholders})"

    def _build_update(self, entity: Entity) -> str:
        dirty = entity.dirty_fields or set(self._fields().keys())
        set_clause = ", ".join(f"{f} = :{f}" for f in dirty if f != self._pk_name())
        return f"UPDATE {self._table_name()} SET {set_clause} WHERE {self._pk_name()} = :{self._pk_name()}"

    def _build_delete(self) -> str:
        return f"DELETE FROM {self._table_name()} WHERE {self._pk_name()} = :{self._pk_name()}"

    def add(self, entity: Entity) -> Entity:
        """Queue an entity for insertion."""
        self._change_tracker.track_add(entity)
        return entity

    def get(self, pk_value: Any) -> Optional[Entity]:
        """Retrieve an entity by primary key."""
        result = self._adapter.execute(
            f"SELECT * FROM {self._table_name()} WHERE {self._pk_name()} = :pk",
            {"pk": pk_value},
        )
        if result and len(result) > 0:
            return self._entity_class.from_dict(dict(result[0]))
        return None

    def find(self, **filters: Any) -> List[Entity]:
        """Find entities matching filters."""
        if not filters:
            return self.all()
        conditions = " AND ".join(f"{k} = :{k}" for k in filters)
        result = self._adapter.execute(
            f"SELECT * FROM {self._table_name()} WHERE {conditions}",
            filters,
        )
        return [self._entity_class.from_dict(dict(r)) for r in result]

    def all(self) -> List[Entity]:
        """Retrieve all entities."""
        result = self._adapter.execute(f"SELECT * FROM {self._table_name()}", {})
        return [self._entity_class.from_dict(dict(r)) for r in result]

    def update(self, entity: Entity) -> Entity:
        """Queue an entity for update."""
        self._change_tracker.track_modify(entity)
        return entity

    def delete(self, entity: Entity) -> None:
        """Queue an entity for deletion."""
        self._change_tracker.track_delete(entity)

    def save(self, entity: Entity) -> Entity:
        """Immediately save (insert or update) an entity."""
        if getattr(entity, self._pk_name()) is None:
            query = self._build_insert(entity)
        else:
            query = self._build_update(entity)
        params = {f: getattr(entity, f) for f in self._fields()}
        self._adapter.execute(query, params)
        entity.clean()
        return entity

    def count(self, **filters: Any) -> int:
        """Count entities matching filters."""
        if not filters:
            result = self._adapter.execute(f"SELECT COUNT(*) AS cnt FROM {self._table_name()}", {})
        else:
            conditions = " AND ".join(f"{k} = :{k}" for k in filters)
            result = self._adapter.execute(
                f"SELECT COUNT(*) AS cnt FROM {self._table_name()} WHERE {conditions}",
                filters,
            )
        return result[0][0] if result else 0

    def flush(self) -> None:
        """Flush all tracked changes to the database."""
        for entity in self._change_tracker.get_added():
            self.save(entity)
        for entity in self._change_tracker.get_modified():
            self.save(entity)
        for entity in self._change_tracker.get_deleted():
            query = self._build_delete()
            self._adapter.execute(query, {self._pk_name(): entity.pk_value})
        self._change_tracker.clear()

    def bulk_insert(self, entities: List[Entity]) -> int:
        """Insert multiple entities in a batch operation."""
        if not entities:
            return 0
        fields = list(self._fields().keys())
        col_names = ", ".join(fields)
        placeholders = ", ".join(f":{f}" for f in fields)
        query = f"INSERT INTO {self._table_name()} ({col_names}) VALUES ({placeholders})"
        params_list = [{f: getattr(e, f) for f in fields} for e in entities]
        return self._adapter.execute_many(query, params_list)

    def create_table(self) -> None:
        """Create the database table for this entity."""
        col_defs = [f.to_column_def() for f in self._fields().values()]
        query = f"CREATE TABLE IF NOT EXISTS {self._table_name()} (\n  " + ",\n  ".join(col_defs) + "\n)"
        self._adapter.execute(query, {})

    def drop_table(self) -> None:
        """Drop the database table."""
        self._adapter.execute(f"DROP TABLE IF EXISTS {self._table_name()}", {})
