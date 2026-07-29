"""ihuriro — Core engine of the Unified Model Generator.

Defines the canonical model dataclasses and the IHuriro engine
that orchestrates multi-target code generation from a single model definition.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Type


@dataclass
class CanonicalField:
    """Canonical representation of a single model field.

    This is the universal intermediate format from which all
    target-specific generators produce their output.

    Attributes:
        name: Field name in snake_case.
        native_type: Semantic type string ("string", "integer", "float",
            "boolean", "datetime", "date", "decimal", "json", "array",
            "relation", "file", "email", "url", "uuid", "text").
        required: Whether the field must have a value.
        unique: Whether values must be unique across rows.
        indexed: Whether a database index should be created.
        primary_key: Whether this is the primary key field.
        auto_increment: Whether the value is auto-generated.
        default: Default value for new records.
        max_length: Maximum string length (string types).
        min_value: Minimum numeric value.
        max_value: Maximum numeric value.
        precision: Total decimal digits (decimal types).
        scale: Digits after decimal point (decimal types).
        foreign_key: Foreign key reference ("table.column").
        relation: Relation type ("belongs_to", "has_many", "has_one", "many_to_many").
        target_entity: Name of the related entity.
        through: Junction table for many-to-many.
        widget: UI widget hint ("textarea", "select", "richtext", "checkbox",
            "file", "password", "email", "color").
        read_only: Whether the field is read-only after creation.
        secret: Whether the field contains sensitive data (PII, passwords).
        embed: Whether to generate an AI embedding for this field.
        description: Human-readable field description.
        example: Example value for documentation and test generation.
        choices: Allowed values (list of (value, label) tuples).
        validation_rules: Additional validation rule identifiers.
        metadata: Extension point for generator-specific metadata.
    """

    name: str = ""
    native_type: str = "string"
    required: bool = False
    unique: bool = False
    indexed: bool = False
    primary_key: bool = False
    auto_increment: bool = False
    default: Any = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    foreign_key: Optional[str] = None
    relation: Optional[str] = None
    target_entity: Optional[str] = None
    through: Optional[str] = None
    widget: Optional[str] = None
    read_only: bool = False
    secret: bool = False
    embed: bool = False
    description: str = ""
    example: Any = None
    choices: List[tuple] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CanonicalIndex:
    """Canonical index definition."""

    columns: List[str] = field(default_factory=list)
    unique: bool = False
    name: str = ""
    using: str = "btree"


@dataclass
class CanonicalModel:
    """Canonical representation of an entire data model.

    This is the universal model definition from which all generators
    produce their target-specific artifacts.

    Attributes:
        name: Entity name (PascalCase).
        table_name: Database table name.
        module: Python module path.
        description: Human-readable description of the model.
        fields: Ordered dict of CanonicalField keyed by field name.
        indexes: Additional multi-column indexes.
        relations: Simplified relation metadata.
        audit_fields: Whether to add created_at/updated_at automatically.
        soft_delete: Whether to add deleted_at for soft deletes.
        generate: List of generator targets to enable.
            Values: "database", "validation", "rest_api", "graphql",
            "serialization", "forms", "admin", "docs", "test_data", "embeddings".
        tags: Arbitrary tags for filtering/categorization.
        metadata: Extension point for model-level metadata.
    """

    name: str = ""
    table_name: str = ""
    module: str = ""
    description: str = ""
    fields: Dict[str, CanonicalField] = field(default_factory=dict)
    indexes: List[CanonicalIndex] = field(default_factory=list)
    audit_fields: bool = True
    soft_delete: bool = False
    generate: List[str] = field(default_factory=lambda: [
        "database", "validation", "rest_api", "serialization", "docs",
    ])
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def pk_field(self) -> Optional[CanonicalField]:
        for f in self.fields.values():
            if f.primary_key:
                return f
        return None

    @property
    def field_names(self) -> List[str]:
        return list(self.fields.keys())

    @property
    def searchable_fields(self) -> List[CanonicalField]:
        return [f for f in self.fields.values() if f.indexed or f.unique]

    @property
    def secret_fields(self) -> List[CanonicalField]:
        return [f for f in self.fields.values() if f.secret]

    @property
    def embed_fields(self) -> List[CanonicalField]:
        return [f for f in self.fields.values() if f.embed]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "table_name": self.table_name,
            "module": self.module,
            "description": self.description,
            "fields": {k: {attr: getattr(v, attr) for attr in dir(v)
                           if not attr.startswith("_") and not callable(getattr(v, attr))}
                       for k, v in self.fields.items()},
            "indexes": [{"columns": i.columns, "unique": i.unique, "name": i.name} for i in self.indexes],
            "audit_fields": self.audit_fields,
            "soft_delete": self.soft_delete,
            "generate": self.generate,
            "tags": self.tags,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def to_markdown(self) -> str:
        lines = [f"# {self.name}", ""]
        if self.description:
            lines.append(f"{self.description}")
            lines.append("")
        lines.append(f"**Table:** `{self.table_name}`  ")
        lines.append(f"**Module:** `{self.module}`  ")
        lines.append("")
        lines.append("## Fields")
        lines.append("")
        lines.append("| Field | Type | Required | Unique | Indexed | Description |")
        lines.append("|-------|------|----------|--------|---------|-------------|")
        for f in self.fields.values():
            req = "Yes" if f.required else "No"
            uniq = "Yes" if f.unique else "No"
            idx = "Yes" if f.indexed else "No"
            lines.append(f"| {f.name} | {f.native_type} | {req} | {uniq} | {idx} | {f.description} |")
        return "\n".join(lines)


GeneratorFn = Callable[[CanonicalModel], Dict[str, str]]


class IHuriro:
    """The Unified Model Generator engine.

    Orchestrates multi-target code generation from a single CanonicalModel.
    Each registered generator produces target-specific artifacts.
    """

    def __init__(self) -> None:
        self._generators: Dict[str, GeneratorFn] = {}
        self._output: Dict[str, Dict[str, str]] = {}

    def register(self, name: str, generator_fn: GeneratorFn) -> None:
        """Register a generator function by target name."""
        self._generators[name] = generator_fn

    def unregister(self, name: str) -> None:
        """Remove a registered generator."""
        self._generators.pop(name, None)

    @property
    def registered_targets(self) -> List[str]:
        return list(self._generators.keys())

    def generate(self, model: CanonicalModel,
                 targets: Optional[List[str]] = None,
                 output_dir: str = "") -> Dict[str, Dict[str, str]]:
        """Generate artifacts for one or more targets from a canonical model.

        Args:
            model: The canonical model to generate from.
            targets: Subset of targets to generate (None = all registered).
            output_dir: If set, write generated files to this directory.

        Returns:
            Dict mapping target names to dicts of {filename: content}.
        """
        if targets is None:
            targets = [t for t in model.generate if t in self._generators]

        results: Dict[str, Dict[str, str]] = {}
        for target in targets:
            if target not in self._generators:
                continue
            try:
                output = self._generators[target](model)
                results[target] = output
                if output_dir:
                    import os
                    target_dir = os.path.join(output_dir, target)
                    os.makedirs(target_dir, exist_ok=True)
                    for filename, content in output.items():
                        filepath = os.path.join(target_dir, filename)
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)
            except Exception as e:
                results[target] = {"_error": str(e)}

        self._output = results
        return results

    def generate_all(self, models: List[CanonicalModel],
                     output_dir: str = "") -> Dict[str, Dict[str, str]]:
        """Generate artifacts for multiple models."""
        combined: Dict[str, Dict[str, str]] = {}
        for model in models:
            result = self.generate(model, output_dir=output_dir)
            for target, files in result.items():
                if target not in combined:
                    combined[target] = {}
                combined[target].update(files)
        return combined

    @property
    def last_output(self) -> Dict[str, Dict[str, str]]:
        return dict(self._output)

    def summary(self) -> Dict[str, Any]:
        """Return a summary of the last generation run."""
        total_files = sum(len(files) for files in self._output.values())
        return {
            "targets": list(self._output.keys()),
            "total_files": total_files,
            "generators": self.registered_targets,
        }

    def generate_as_string(self, model: CanonicalModel,
                           targets: Optional[List[str]] = None) -> str:
        """Generate and return a formatted string summary of all output."""
        results = self.generate(model, targets)
        parts = [f"# Generated artifacts for {model.name}", ""]
        for target, files in sorted(results.items()):
            parts.append(f"## {target}")
            for filename, content in files.items():
                parts.append(f"### {filename}")
                parts.append("```" + self._ext(filename))
                parts.append(content)
                parts.append("```")
                parts.append("")
        return "\n".join(parts)

    @staticmethod
    def _ext(filename: str) -> str:
        _, ext = filename.rsplit(".", 1) if "." in filename else ("", "")
        lang_map = {
            "py": "python", "js": "javascript", "ts": "typescript",
            "graphql": "graphql", "json": "json", "yaml": "yaml",
            "yml": "yaml", "md": "markdown", "html": "html",
            "csv": "csv", "sql": "sql", "i": "text",
        }
        return lang_map.get(ext, "text")
