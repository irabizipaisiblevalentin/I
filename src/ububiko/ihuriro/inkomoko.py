"""inkomoko — Model definition reader for the IHuriro generator.

Parses Entity classes, dataclasses, or raw dict definitions into
CanonicalModel objects that feed the generation pipeline.
"""

from __future__ import annotations

import inspect
from typing import Any, Dict, List, Optional, Type

from ububiko.ububazimurizo import Entity, Field, Relationship, RelationshipType
from ububiko.ihuriro.ihuriro import CanonicalField, CanonicalIndex, CanonicalModel

_NATIVE_TYPE_MAP: Dict[type, str] = {
    str: "string",
    int: "integer",
    float: "float",
    bool: "boolean",
    bytes: "blob",
    list: "array",
    dict: "json",
    type(None): "null",
}

try:
    from datetime import datetime, date, time
    _NATIVE_TYPE_MAP[datetime] = "datetime"
    _NATIVE_TYPE_MAP[date] = "date"
    _NATIVE_TYPE_MAP[time] = "time"
except ImportError:
    pass

try:
    import decimal
    _NATIVE_TYPE_MAP[decimal.Decimal] = "decimal"
except ImportError:
    pass

try:
    import uuid
    _NATIVE_TYPE_MAP[uuid.UUID] = "uuid"
except ImportError:
    pass


def _map_type(py_type: type, field_def: Optional[Field] = None) -> str:
    if py_type in _NATIVE_TYPE_MAP:
        return _NATIVE_TYPE_MAP[py_type]
    if hasattr(py_type, "__origin__"):
        origin = py_type.__origin__
        if origin is list:
            return "array"
        if origin is dict:
            return "json"
        if origin is Optional:
            args = getattr(py_type, "__args__", [])
            if args:
                return _map_type(args[0])
    if hasattr(py_type, "__name__"):
        name = py_type.__name__.lower()
        if name in ("str", "string"):
            return "string"
        if name in ("int", "integer"):
            return "integer"
        if name in ("float", "double"):
            return "float"
        if name in ("bool", "boolean"):
            return "boolean"
        if name in ("datetime",):
            return "datetime"
        if name in ("date",):
            return "date"
        if name in ("decimal",):
            return "decimal"
        if name in ("uuid",):
            return "uuid"
    return "string"


def from_entity(entity_class: Type[Entity],
                generate: Optional[List[str]] = None,
                **kwargs: Any) -> CanonicalModel:
    """Parse an Entity subclass into a CanonicalModel.

    Args:
        entity_class: The Entity subclass to parse.
        generate: List of generator targets to enable.
        **kwargs: Additional CanonicalModel fields to override.

    Returns:
        A CanonicalModel ready for generation.
    """
    fields: Dict[str, CanonicalField] = {}
    indexes: List[CanonicalIndex] = []

    for field_name, field_def in entity_class._fields.items():
        native_type = _map_type(field_def.field_type, field_def)
        cf = CanonicalField(
            name=field_name,
            native_type=native_type,
            required=not field_def.nullable,
            unique=field_def.unique,
            indexed=field_def.index,
            primary_key=field_def.primary_key,
            auto_increment=field_def.generated,
            default=field_def.default,
            max_length=field_def.max_length,
            precision=field_def.precision,
            scale=field_def.scale,
            foreign_key=field_def.foreign_key if field_def.foreign_key else None,
            description=field_def.metadata.get("description", ""),
            example=field_def.metadata.get("example"),
            widget=field_def.metadata.get("widget"),
            secret=field_def.metadata.get("secret", False),
            embed=field_def.metadata.get("embed", False),
            read_only=field_def.metadata.get("read_only", False),
            choices=field_def.metadata.get("choices", []),
            validation_rules=field_def.metadata.get("validation_rules", []),
            metadata={k: v for k, v in field_def.metadata.items()
                      if k not in ("description", "example", "widget",
                                   "secret", "embed", "read_only",
                                   "choices", "validation_rules")},
        )
        fields[field_name] = cf

    relations: Dict[str, CanonicalField] = {}
    for rel_name, rel_def in entity_class._relationships.items():
        target = rel_def.target
        fk = rel_def.foreign_key
        if rel_def.type == RelationshipType.ONE_TO_MANY or rel_def.type == RelationshipType.MANY_TO_ONE:
            rel_type = "has_many" if rel_def.type == RelationshipType.ONE_TO_MANY else "belongs_to"
        elif rel_def.type == RelationshipType.ONE_TO_ONE:
            rel_type = "has_one"
        else:
            rel_type = "many_to_many"
        cf = CanonicalField(
            name=rel_name,
            native_type="relation",
            relation=rel_type,
            target_entity=target,
            foreign_key=fk if fk else None,
            through=rel_def.through if rel_def.through else None,
        )
        relations[rel_name] = cf

    fields.update(relations)
    table = entity_class._table_name

    if generate is None:
        generate = ["database", "validation", "rest_api", "serialization", "docs"]

    return CanonicalModel(
        name=entity_class.__name__,
        table_name=table,
        module=entity_class.__module__,
        description=entity_class.__doc__.strip() if entity_class.__doc__ else "",
        fields=fields,
        indexes=indexes,
        generate=generate,
        **kwargs,
    )


def from_dataclass(dc: Type, table_name: str = "",
                   generate: Optional[List[str]] = None,
                   **kwargs: Any) -> CanonicalModel:
    """Parse a Python dataclass into a CanonicalModel."""
    if not hasattr(dc, "__dataclass_fields__"):
        raise TypeError(f"{dc.__name__} is not a dataclass")

    import dataclasses
    fields: Dict[str, CanonicalField] = {}
    for f in dataclasses.fields(dc):
        native_type = _map_type(f.type)
        cf = CanonicalField(
            name=f.name,
            native_type=native_type,
            required=True if f.default is dataclasses.MISSING else False,
            default=f.default if f.default is not dataclasses.MISSING else None,
            metadata=f.metadata or {},
        )
        cf.description = cf.metadata.get("description", "")
        cf.example = cf.metadata.get("example")
        cf.secret = cf.metadata.get("secret", False)
        fields[f.name] = cf

    return CanonicalModel(
        name=dc.__name__,
        table_name=table_name or dc.__name__.lower(),
        module=dc.__module__,
        description=dc.__doc__.strip() if dc.__doc__ else "",
        fields=fields,
        generate=generate or ["database", "validation", "serialization", "docs"],
        **kwargs,
    )


def from_dict(name: str, definition: Dict[str, Any], **kwargs: Any) -> CanonicalModel:
    """Parse a raw dict definition into a CanonicalModel.

    Expected format:
    {
        "table_name": "products",
        "description": "...",
        "fields": {
            "id": {"type": "integer", "primary_key": True, ...},
            "name": {"type": "string", "required": True, "max_length": 200},
        }
    }
    """
    raw_fields = definition.get("fields", {})
    fields: Dict[str, CanonicalField] = {}
    for fname, fdef in raw_fields.items():
        if isinstance(fdef, str):
            fdef: dict = {"native_type": fdef}
        fdef["name"] = fname
        if "type" in fdef and "native_type" not in fdef:
            fdef["native_type"] = fdef.pop("type")
        fields[fname] = CanonicalField(**{k: v for k, v in fdef.items()})

    return CanonicalModel(
        name=name,
        table_name=definition.get("table_name", name.lower()),
        description=definition.get("description", ""),
        fields=fields,
        indexes=[CanonicalIndex(**i) for i in definition.get("indexes", [])],
        audit_fields=definition.get("audit_fields", True),
        soft_delete=definition.get("soft_delete", False),
        generate=definition.get("generate", ["database", "validation", "rest_api", "serialization", "docs"]),
        tags=definition.get("tags", []),
        **kwargs,
    )


class ModelReader:
    """Reads model definitions from various sources.

    Provides convenience wrappers around from_entity, from_dataclass,
    and from_dict.
    """

    @staticmethod
    def from_entity(entity_class: Type[Entity],
                    generate: Optional[List[str]] = None,
                    **kwargs: Any) -> CanonicalModel:
        """Parse an Entity subclass into a CanonicalModel."""
        return from_entity(entity_class, generate=generate, **kwargs)

    @staticmethod
    def from_dataclass(dc: Type, table_name: str = "",
                       generate: Optional[List[str]] = None,
                       **kwargs: Any) -> CanonicalModel:
        """Parse a dataclass into a CanonicalModel."""
        return from_dataclass(dc, table_name=table_name, generate=generate, **kwargs)

    @staticmethod
    def from_dict(name: str, definition: Dict[str, Any],
                  **kwargs: Any) -> CanonicalModel:
        """Parse a raw dict definition into a CanonicalModel."""
        return from_dict(name, definition, **kwargs)
