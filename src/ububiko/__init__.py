"""ububiko — Official Data Platform for the I Programming Language.

A complete universal data platform supporting relational, NoSQL, graph,
vector, document, and cloud-based storage through a unified API.
"""

from __future__ import annotations

__version__ = "1.0.0"

from ububiko.ihuriro import (
    IHuriro, CanonicalModel, CanonicalField, CanonicalIndex, ModelReader,
    DatabaseGenerator, ValidationGenerator, RestApiGenerator,
    GraphQLGenerator, SerializationGenerator, FormGenerator,
    AdminGenerator, DocumentationGenerator, TestDataGenerator,
    EmbeddingGenerator,
)

from ububiko.ikubamiro import DatabaseType, ConnectionConfig, ConnectionManager
from ububiko.ububazimurizo import Entity, Repository, Field, Relationship, RelationshipType, ChangeTracker
from ububiko.cyanditswe import QueryBuilder, RawQuery, StoredProcedure
from ububiko.imuka import Migration, MigrationEngine
from ububiko.ubushakashatsi import EmbeddingService, VectorIndex, SemanticSearch, RAGPipeline, Document
from ububiko.ikwirakwira import Replicator, ShardManager, DistributedTransaction
from ububiko.umutekano import EncryptionEngine, RoleBasedAccessControl, AuditLogger
from ububiko.ikoreshana import ConnectionPool, CacheLayer, BatchProcessor
from ububiko.muruhande import OfflineDatabase, ConflictResolver, DeltaSyncEngine
from ububiko.kwitegereza import MetricsCollector, HealthChecker, SlowQueryDetector
from ububiko.ikusanyamakuru import DatabaseAdapter, get_adapter, register_adapter

__all__ = [
    # IHuriro — Define Once, Use Everywhere
    "IHuriro",
    "CanonicalModel",
    "CanonicalField",
    "CanonicalIndex",
    "ModelReader",
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
    # Core
    "DatabaseType",
    "ConnectionConfig",
    "ConnectionManager",
    "Entity",
    "Repository",
    "Field",
    "Relationship",
    "RelationshipType",
    "ChangeTracker",
    "QueryBuilder",
    "RawQuery",
    "StoredProcedure",
    "Migration",
    "MigrationEngine",
    "EmbeddingService",
    "VectorIndex",
    "SemanticSearch",
    "RAGPipeline",
    "Document",
    "Replicator",
    "ShardManager",
    "DistributedTransaction",
    "EncryptionEngine",
    "RoleBasedAccessControl",
    "AuditLogger",
    "ConnectionPool",
    "CacheLayer",
    "BatchProcessor",
    "OfflineDatabase",
    "ConflictResolver",
    "DeltaSyncEngine",
    "MetricsCollector",
    "HealthChecker",
    "SlowQueryDetector",
    "DatabaseAdapter",
    "get_adapter",
    "register_adapter",
]
