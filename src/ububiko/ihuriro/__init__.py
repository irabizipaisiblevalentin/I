"""ihuriro — Unified Model Generator for the I Programming Language.

Defines a canonical model once and automatically produces:
  - Database schemas & migrations
  - Validation rules
  - REST API contracts
  - GraphQL schemas
  - JSON serialization
  - Form definitions
  - Admin dashboard scaffolding
  - Documentation
  - Test data generators
  - AI embedding metadata
"""

from __future__ import annotations

__all__ = [
    "CanonicalField",
    "CanonicalModel",
    "CanonicalIndex",
    "IHuriro",
    "ModelReader",
    "BaseGenerator",
    "DatabaseGenerator",
    "ValidationGenerator",
    "RestApiGenerator",
    "GraphQLGenerator",
    "SerializationGenerator",
    "FormGenerator",
    "AdminGenerator",
    "DocumentationGenerator",
    "TestDataGenerator",
    "EmbeddingGenerator",
]

from ububiko.ihuriro.ihuriro import CanonicalField, CanonicalModel, CanonicalIndex, IHuriro
from ububiko.ihuriro.inkomoko import ModelReader
from ububiko.ihuriro.ibyara import (
    BaseGenerator,
    DatabaseGenerator,
    ValidationGenerator,
    RestApiGenerator,
    GraphQLGenerator,
    SerializationGenerator,
    FormGenerator,
    AdminGenerator,
    DocumentationGenerator,
    TestDataGenerator,
    EmbeddingGenerator,
)
