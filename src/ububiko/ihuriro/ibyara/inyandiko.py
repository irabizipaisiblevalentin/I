"""inyandiko — Documentation generator.

Produces Markdown documentation, OpenAPI/ Swagger specs,
field reference tables, and model relationship diagrams
from a CanonicalModel.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from ububiko.ihuriro.ibyara import BaseGenerator
from ububiko.ihuriro.ihuriro import CanonicalField, CanonicalModel


class DocumentationGenerator(BaseGenerator):
    """Generates documentation artifacts."""

    target_name = "docs"

    @classmethod
    def generate(cls, model: CanonicalModel) -> Dict[str, str]:
        base_name = model.table_name
        class_name = model.name

        # Markdown doc
        md = (
            f"# {class_name}\n\n"
            f"{model.description}\n\n"
            f"## Overview\n\n"
            f"- **Table:** `{base_name}`\n"
            f"- **Module:** `{model.module}`\n"
            f"- **PK:** `{model.pk_field.name if model.pk_field else 'id'}`\n"
            f"- **Audit Fields:** {model.audit_fields}\n"
            f"- **Soft Delete:** {model.soft_delete}\n\n"
            f"## Fields\n\n"
            f"| Field | Type | Required | Unique | Default | Description |\n"
            f"|-------|------|----------|--------|---------|-------------|\n"
        )
        for f in model.fields.values():
            req = "Yes" if f.required else "No"
            uniq = "Yes" if f.unique else "No"
            default = str(f.default) if f.default is not None else ""
            md += f"| {f.name} | {f.native_type} | {req} | {uniq} | {default} | {f.description} |\n"

        if model.secret_fields:
            md += "\n## Sensitive Fields\n\n"
            for f in model.secret_fields:
                md += f"- `{f.name}` — encrypted at rest\n"

        if model.embed_fields:
            md += "\n## AI Embedding Fields\n\n"
            for f in model.embed_fields:
                md += f"- `{f.name}` — included in vector embeddings\n"

        # OpenAPI schema component
        properties = {}
        for f in model.fields.values():
            prop: Dict[str, Any] = {"type": "string"}
            type_map = {"integer": "integer", "float": "number", "boolean": "boolean",
                        "datetime": "string", "date": "string", "text": "string",
                        "json": "object", "array": "array", "decimal": "number"}
            prop["type"] = type_map.get(f.native_type, "string")
            if f.native_type in ("datetime", "date"):
                prop["format"] = "date-time" if f.native_type == "datetime" else "date"
            if f.description:
                prop["description"] = f.description
            if f.example:
                prop["example"] = f.example
            properties[f.name] = prop

        openapi_schema = {
            "type": "object",
            "required": [f.name for f in model.fields.values()
                         if f.required and not f.primary_key and not f.auto_increment],
            "properties": properties,
        }
        if model.description:
            openapi_schema["description"] = model.description

        return {
            f"{base_name}.md": md,
            f"{base_name}.openapi.json": json.dumps(openapi_schema, indent=2, default=str),
        }
