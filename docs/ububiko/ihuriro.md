# IHuriro — Define Once, Use Everywhere

IHuriro (Kinyarwanda: "unification point") is the Unified Model Generator
built into the UBUBIKO data platform. It enables you to define a data model
once and automatically produce artifacts across the entire I ecosystem.

## Concept

```
┌──────────────────────────────────────────────────────────────┐
│                    One Model Definition                        │
│               (Entity class / dataclass / dict)                │
└─────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────┐
              │    IHuriro Engine  │
              │  CanonicalModel    │
              └──────┬──────┬─────┘
                     │      │
        ┌────────────┼──────┼────────────────┐
        │            │      │                │
        ▼            ▼      ▼                ▼
   Database      REST     GraphQL        Validation
   (SQL, mig.)   (FastAPI)(schema)       (Python rules)
        │            │      │                │
        ▼            ▼      ▼                ▼
   Serialization  Forms    Admin          Documentation
   (JSON Schema)  (HTML)   (Dashboard)    (OpenAPI + MD)
        │            │      │                │
        ▼            ▼      ▼                ▼
   Test Data     Embeddings
   (Faker)       (Vector)

        10 generators → 20+ file types per model
```

## Quick Start

```python
from ububiko.ihuriro import IHuriro, CanonicalModel, CanonicalField
from ububiko.ihuriro.ibyara import (
    DatabaseGenerator, ValidationGenerator, RestApiGenerator,
    GraphQLGenerator, SerializationGenerator, FormGenerator,
    AdminGenerator, DocumentationGenerator, TestDataGenerator,
    EmbeddingGenerator,
)

# 1. Define a model programmatically
model = CanonicalModel(
    name="Product",
    table_name="products",
    description="A sellable product in the catalog",
    fields={
        "id": CanonicalField(name="id", native_type="integer", primary_key=True, auto_increment=True),
        "name": CanonicalField(name="name", native_type="string", required=True, max_length=200,
                               description="Product display name"),
        "price": CanonicalField(name="price", native_type="decimal", required=True,
                                min_value=0, precision=10, scale=2,
                                description="Price in RWF"),
        "active": CanonicalField(name="active", native_type="boolean", default=True),
        "tags": CanonicalField(name="tags", native_type="array", default=[]),
        "category_id": CanonicalField(name="category_id", native_type="integer",
                                      foreign_key="categories.id"),
    },
    audit_fields=True,
)

# 2. Set up the engine
engine = IHuriro()
engine.register("database", DatabaseGenerator.generate)
engine.register("validation", ValidationGenerator.generate)
engine.register("rest_api", RestApiGenerator.generate)
engine.register("graphql", GraphQLGenerator.generate)
engine.register("serialization", SerializationGenerator.generate)
engine.register("forms", FormGenerator.generate)
engine.register("admin", AdminGenerator.generate)
engine.register("docs", DocumentationGenerator.generate)
engine.register("test_data", TestDataGenerator.generate)
engine.register("embeddings", EmbeddingGenerator.generate)

# 3. Generate everything
results = engine.generate(model)
```

## From an Entity Class

```python
from ububiko.ububazimurizo import Entity, Field, Relationship
from ububiko.ihuriro.inkomoko import from_entity

class Product(Entity):
    __table__ = "products"
    id = Field(field_type=int, primary_key=True, auto_increment=True)
    name = Field(field_type=str, max_length=200, required=True,
                 metadata={"description": "Product display name"})
    price = Field(field_type=float, required=True,
                  metadata={"description": "Price in RWF", "min_value": 0})
    active = Field(field_type=bool, default=True)

model = from_entity(Product)
```

## From a Dataclass

```python
from dataclasses import dataclass
from ububiko.ihuriro.inkomoko import from_dataclass

@dataclass
class Product:
    name: str
    price: float
    active: bool = True

model = from_dataclass(Product, table_name="products")
```

## CLI Usage

```bash
# List available generators
isoko ububiko generate --list-targets

# Generate all artifacts for a model
isoko ububiko generate myapp.models.Product

# Generate specific targets only
isoko ububiko generate myapp.models.Product --targets database rest_api docs

# Specify output directory
isoko ububiko generate myapp.models.Product --output ./generated
```

## What Each Generator Produces

| Generator | Target | Output Files |
|-----------|--------|-------------|
| Database | `database` | `{table}.sql`, `{timestamp}_create_{table}.py` |
| Validation | `validation` | `validate_{table}.py` |
| REST API | `rest_api` | `api_{table}.py` |
| GraphQL | `graphql` | `{table}.graphql`, `{table}_resolvers.py` |
| Serialization | `serialization` | `{table}.schema.json`, `serialize_{table}.py` |
| Forms | `forms` | `{table}.form.i`, `{table}.html` |
| Admin | `admin` | `admin_{table}.py` |
| Docs | `docs` | `{table}.md`, `{table}.openapi.json` |
| Test Data | `test_data` | `factory_{table}.py` |
| Embeddings | `embeddings` | `embeddings_{table}.json`, `embeddings_{table}.py` |

## Benefits

- **Single source of truth** — change one model, update every artifact
- **Consistency** — all outputs share the same typing, naming, and constraints
- **Speed** — eliminate repetitive coding of CRUD, forms, serializers, etc.
- **Cross-platform** — outputs target web, desktop, mobile, and cloud equally
- **Extensible** — register custom generators for proprietary toolchains
