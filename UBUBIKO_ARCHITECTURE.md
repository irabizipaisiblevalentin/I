# UBUBIKO — The Official Data Platform

UBUBIKO is the complete universal data platform of the I Programming Language.
It provides a single, unified interface for every major type of data storage:
relational, NoSQL, graph, vector, document, time-series, and cloud-based systems.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                         │
├─────────────────────────────────────────────────────────────┤
│  ORM       Query      Migration    AI Data    Distributed    │
│  (ububazi-  Engine    (imuka)      (ubusha-   (ikwirakwira)  │
│   murizo)   (cyand.)               kashatsi)                  │
├─────────────────────────────────────────────────────────────┤
│  Security   Perform.  Offline     Observab.  Connection     │
│  (umute-    (ikore-   (muruhan.)  (kwite-    Manager        │
│   kano)     shana)                 gereza)    (ikubamiro)    │
├─────────────────────────────────────────────────────────────┤
│              Database Adapters (ikusanyamakuru)               │
│  SQLite  PG  MySQL  Mongo  Redis  Neo4j  ES  Vector  Cloud  │
└─────────────────────────────────────────────────────────────┘
```

## Core Modules

| Module | Kinyarwanda | Purpose |
|--------|-------------|---------|
| Connection | ikubamiro | Connection config, pooling, lifecycle |
| ORM | ububazimurizo | Entity mapping, repositories, relationships |
| Query | cyanditswe | Fluent query builder, raw SQL, FTS, CTEs, window functions |
| Migration | imuka | Schema versioning, rollback, seeding |
| AI Data | ubushakashatsi | Embeddings, vector search, semantic search, RAG |
| Distributed | ikwirakwira | Replication, sharding, distributed transactions |
| Security | umutekano | Encryption, RBAC, audit logging, compliance |
| Performance | ikoreshana | Connection pooling, caching, batch processing |
| Offline | muruhande | Offline DB, conflict resolution, delta sync |
| Observability | kwitegereza | Slow query detection, metrics, health checks |
| Adapters | ikusanyamakuru | Database engine implementations |

## Supported Databases

- **Relational:** PostgreSQL, MySQL, MariaDB, SQLite, MSSQL, Oracle
- **NoSQL:** MongoDB, Redis, Cassandra
- **Graph:** Neo4j
- **Time-Series:** InfluxDB
- **Search:** Elasticsearch, OpenSearch
- **Vector:** Native vector database adapter
- **Object Storage:** S3-compatible
- **Cloud:** Managed cloud databases

## Design Principles

1. **Unified API** — Every database engine shares the same interface
2. **Not a Wrapper** — Native adapters with clean abstractions
3. **Kinyarwanda First** — All APIs expressed in Kinyarwanda
4. **Performance** — Connection pooling, caching, prepared statements
5. **Security** — Encryption, RBAC, audit built into the core
6. **AI-Ready** — Native vector search, embeddings, RAG pipelines
7. **Offline-First** — Full offline support with conflict resolution
8. **Observable** — Metrics, slow query detection, health checks

## CLI Usage

```bash
isoko ububiko new <name>        # Create a new data project
isoko ububiko migrate            # Run pending migrations
isoko ububiko rollback           # Roll back migrations
isoko ububiko seed               # Run seed data
isoko ububiko validate           # Validate schema
isoko ububiko inspect            # Inspect database
isoko ububiko backup <file>      # Backup database
isoko ububiko restore <file>     # Restore database
isoko ububiko sync               # Sync databases
```
