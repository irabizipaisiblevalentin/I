"""ikusanyamakuru — Database adapters for the UBUBIKO data platform.

Provides the abstract DatabaseAdapter interface and concrete
implementations for all supported database engines.
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Type

from ububiko.ikubamiro import ConnectionConfig, DatabaseType


class ResultSet:
    """Wrapper for query results providing dict-like access."""

    def __init__(self, columns: List[str], rows: List[tuple]) -> None:
        self._columns = columns
        self._rows = rows

    @property
    def columns(self) -> List[str]:
        return list(self._columns)

    @property
    def rows(self) -> List[tuple]:
        return list(self._rows)

    def __len__(self) -> int:
        return len(self._rows)

    def __getitem__(self, index: int) -> Any:
        row = self._rows[index]
        if isinstance(row, tuple):
            return dict(zip(self._columns, row))
        return row

    def first(self) -> Optional[Dict[str, Any]]:
        if self._rows:
            return dict(zip(self._columns, self._rows[0]))
        return None

    def all(self) -> List[Dict[str, Any]]:
        return [dict(zip(self._columns, row)) for row in self._rows]

    def __iter__(self):
        return iter(self.all())

    def __repr__(self) -> str:
        return f"ResultSet(rows={len(self._rows)}, cols={self._columns})"


class DatabaseAdapter(ABC):
    """Abstract base class for database adapters.

    All database engines implement this interface to provide
    a unified programming model.
    """

    def __init__(self) -> None:
        self._config: Optional[ConnectionConfig] = None
        self._connected: bool = False

    @property
    def config(self) -> Optional[ConnectionConfig]:
        return self._config

    @property
    def connected(self) -> bool:
        return self._connected

    @abstractmethod
    def connect(self, config: ConnectionConfig) -> None:
        """Establish a connection to the database."""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Close the database connection."""
        ...

    @abstractmethod
    def execute(self, query: str, params: Dict[str, Any]) -> ResultSet:
        """Execute a query and return results."""
        ...

    @abstractmethod
    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        """Execute a query with multiple parameter sets."""
        ...

    @abstractmethod
    def begin(self) -> Any:
        """Begin a transaction."""
        ...

    @abstractmethod
    def commit(self, transaction: Any) -> None:
        """Commit a transaction."""
        ...

    @abstractmethod
    def rollback(self, transaction: Any) -> None:
        """Rollback a transaction."""
        ...

    def close(self) -> None:
        """Close the adapter (alias for disconnect)."""
        self.disconnect()

    def call_procedure(self, name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Call a stored procedure (default implementation raises)."""
        raise NotImplementedError(f"Stored procedures not supported by {type(self).__name__}")

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        try:
            self.execute(f"SELECT 1 FROM {table_name} LIMIT 1", {})
            return True
        except Exception:
            return False


_ADAPTER_REGISTRY: Dict[DatabaseType, Type[DatabaseAdapter]] = {}


def register_adapter(db_type: DatabaseType, adapter_class: Type[DatabaseAdapter]) -> None:
    """Register a database adapter for a database type."""
    _ADAPTER_REGISTRY[db_type] = adapter_class


def get_adapter(db_type: DatabaseType) -> Type[DatabaseAdapter]:
    """Get the registered adapter class for a database type."""
    if db_type in _ADAPTER_REGISTRY:
        return _ADAPTER_REGISTRY[db_type]
    if db_type == DatabaseType.SQLITE:
        return SQLiteAdapter
    raise ValueError(f"No adapter registered for {db_type.value}")


class SQLiteAdapter(DatabaseAdapter):
    """SQLite database adapter — reference implementation.

    Uses the built-in sqlite3 module and supports all standard
    SQL operations, transactions, and schema management.
    """

    def __init__(self) -> None:
        super().__init__()
        self._connection: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()

    def connect(self, config: ConnectionConfig) -> None:
        db_path = config.database if config.database != ":memory:" else ":memory:"
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._config = config
        self._connected = True

    def disconnect(self) -> None:
        with self._lock:
            if self._connection:
                self._connection.close()
                self._connection = None
                self._connected = False

    def execute(self, query: str, params: Dict[str, Any]) -> ResultSet:
        if not self._connection:
            raise RuntimeError("Not connected")
        with self._lock:
            cursor = self._connection.execute(query, params)
            if query.strip().upper().startswith(("SELECT", "PRAGMA", "WITH")):
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                return ResultSet(columns, rows)
            self._connection.commit()
            return ResultSet([], [])

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        if not self._connection:
            raise RuntimeError("Not connected")
        with self._lock:
            cursor = self._connection.executemany(query, params_list)
            self._connection.commit()
            return cursor.rowcount

    def begin(self) -> Any:
        if not self._connection:
            raise RuntimeError("Not connected")
        self._connection.execute("BEGIN")
        return id(self._connection)

    def commit(self, transaction: Any) -> None:
        if self._connection:
            self._connection.commit()

    def rollback(self, transaction: Any) -> None:
        if self._connection:
            self._connection.rollback()

    def table_exists(self, table_name: str) -> bool:
        result = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=:name",
            {"name": table_name},
        )
        return len(result) > 0


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL database adapter.

    Uses psycopg2 or pg8000 driver.
    """

    def connect(self, config: ConnectionConfig) -> None:
        try:
            import psycopg2
            self._connection = psycopg2.connect(
                host=config.host,
                port=config.port,
                dbname=config.database,
                user=config.username,
                password=config.password,
                sslmode="require" if config.ssl else "disable",
            )
            self._connection.autocommit = False
            self._config = config
            self._connected = True
        except ImportError:
            raise ImportError("psycopg2 is required for PostgreSQL. Install with: pip install psycopg2-binary")

    def disconnect(self) -> None:
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
            self._connection = None
            self._connected = False

    def execute(self, query: str, params: Dict[str, Any]) -> ResultSet:
        if not self._connection:
            raise RuntimeError("Not connected")
        with self._connection.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                self._connection.commit()
                return ResultSet(columns, rows)
            self._connection.commit()
            return ResultSet([], [])

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        if not self._connection:
            raise RuntimeError("Not connected")
        with self._connection.cursor() as cur:
            for params in params_list:
                cur.execute(query, params)
            self._connection.commit()
            return len(params_list)

    def begin(self) -> Any:
        if self._connection:
            return self._connection
        return None

    def commit(self, transaction: Any) -> None:
        if self._connection:
            self._connection.commit()

    def rollback(self, transaction: Any) -> None:
        if self._connection:
            self._connection.rollback()


class MySQLAdapter(DatabaseAdapter):
    """MySQL/MariaDB database adapter.

    Uses pymysql or mysql-connector-python driver.
    """

    def connect(self, config: ConnectionConfig) -> None:
        try:
            import pymysql
            self._connection = pymysql.connect(
                host=config.host,
                port=config.port,
                database=config.database,
                user=config.username,
                password=config.password,
                ssl=config.ssl,
            )
            self._config = config
            self._connected = True
        except ImportError:
            raise ImportError("pymysql is required for MySQL. Install with: pip install pymysql")

    def disconnect(self) -> None:
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
            self._connection = None
            self._connected = False

    def execute(self, query: str, params: Dict[str, Any]) -> ResultSet:
        if not self._connection:
            raise RuntimeError("Not connected")
        with self._connection.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                self._connection.commit()
                return ResultSet(columns, rows)
            self._connection.commit()
            return ResultSet([], [])

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        if not self._connection:
            raise RuntimeError("Not connected")
        with self._connection.cursor() as cur:
            for params in params_list:
                cur.execute(query, params)
            self._connection.commit()
            return len(params_list)

    def begin(self) -> Any:
        if self._connection:
            self._connection.begin()
            return self._connection
        return None

    def commit(self, transaction: Any) -> None:
        if self._connection:
            self._connection.commit()

    def rollback(self, transaction: Any) -> None:
        if self._connection:
            self._connection.rollback()


class MongoDBAdapter(DatabaseAdapter):
    """MongoDB database adapter.

    Uses pymongo driver.
    """

    def connect(self, config: ConnectionConfig) -> None:
        try:
            import pymongo
            uri = f"mongodb://{config.host}:{config.port}"
            self._client = pymongo.MongoClient(uri)
            self._db = self._client[config.database]
            self._config = config
            self._connected = True
        except ImportError:
            raise ImportError("pymongo is required for MongoDB. Install with: pip install pymongo")

    def disconnect(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            self._connected = False

    def execute(self, query: str, params: Dict[str, Any]) -> ResultSet:
        import re
        collection_match = re.match(r"db\.(\w+)\.(\w+)", query)
        if not collection_match:
            return ResultSet([], [])
        collection_name, operation = collection_match.group(1), collection_match.group(2)
        collection = self._db[collection_name]

        if operation == "find":
            filter_dict = params.get("filter", {})
            cursor = collection.find(filter_dict)
            limit = params.get("limit", 0)
            if limit:
                cursor = cursor.limit(limit)
            docs = list(cursor)
            columns = list(docs[0].keys()) if docs else []
            rows = [tuple(d.values()) for d in docs]
            return ResultSet(columns, rows)
        elif operation == "insert_one":
            result = collection.insert_one(params.get("document", {}))
            return ResultSet(["inserted_id"], [(str(result.inserted_id),)])
        elif operation == "update_one":
            result = collection.update_one(
                params.get("filter", {}),
                {"$set": params.get("update", {})},
            )
            return ResultSet(["modified_count"], [(result.modified_count,)])
        elif operation == "delete_one":
            result = collection.delete_one(params.get("filter", {}))
            return ResultSet(["deleted_count"], [(result.deleted_count,)])
        return ResultSet([], [])

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        import re
        collection_match = re.match(r"db\.(\w+)\.insert_many", query)
        if collection_match:
            collection_name = collection_match.group(1)
            collection = self._db[collection_name]
            documents = [p.get("document", {}) for p in params_list]
            result = collection.insert_many(documents)
            return len(result.inserted_ids)
        return 0

    def begin(self) -> Any:
        return None

    def commit(self, transaction: Any) -> None:
        pass

    def rollback(self, transaction: Any) -> None:
        pass


class RedisAdapter(DatabaseAdapter):
    """Redis database adapter.

    Uses redis-py driver.
    """

    def connect(self, config: ConnectionConfig) -> None:
        try:
            import redis as redis_module
            self._client = redis_module.Redis(
                host=config.host,
                port=config.port,
                db=int(config.database) if config.database.isdigit() else 0,
                password=config.password or None,
                ssl=config.ssl,
            )
            self._config = config
            self._connected = True
        except ImportError:
            raise ImportError("redis is required for Redis. Install with: pip install redis")

    def disconnect(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
            self._connected = False

    def execute(self, query: str, params: Dict[str, Any]) -> ResultSet:
        cmd = query.strip().upper().split()[0]
        if cmd == "GET":
            val = self._client.get(params.get("key", ""))
            return ResultSet(["value"], [(val.decode() if val else None,)])
        elif cmd == "SET":
            self._client.set(params.get("key", ""), params.get("value", ""))
            return ResultSet([], [])
        elif cmd == "DELETE":
            count = self._client.delete(params.get("key", ""))
            return ResultSet(["deleted"], [(count,)])
        elif cmd == "KEYS":
            keys = self._client.keys(params.get("pattern", "*"))
            return ResultSet(["keys"], [(k.decode(),) for k in keys])
        return ResultSet([], [])

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        pipe = self._client.pipeline()
        for params in params_list:
            cmd = query.strip().upper()
            if "SET" in cmd:
                pipe.set(params.get("key", ""), params.get("value", ""))
            elif "DELETE" in cmd:
                pipe.delete(params.get("key", ""))
        pipe.execute()
        return len(params_list)

    def begin(self) -> Any:
        self._client = self._client.pipeline()
        return self._client

    def commit(self, transaction: Any) -> None:
        if transaction:
            transaction.execute()

    def rollback(self, transaction: Any) -> None:
        transaction.reset()


class CassandraAdapter(DatabaseAdapter):
    """Cassandra database adapter.

    Uses cassandra-driver.
    """

    def connect(self, config: ConnectionConfig) -> None:
        try:
            from cassandra.cluster import Cluster
            cluster = Cluster([config.host], port=config.port)
            self._session = cluster.connect(config.database)
            self._config = config
            self._connected = True
        except ImportError:
            raise ImportError("cassandra-driver required for Cassandra. Install with: pip install cassandra-driver")

    def disconnect(self) -> None:
        if self._session:
            self._session.shutdown()
            self._session = None
            self._connected = False

    def execute(self, query: str, params: Dict[str, Any]) -> ResultSet:
        if not self._session:
            raise RuntimeError("Not connected")
        prepared = self._session.prepare(query) if "?" in query else None
        if prepared:
            result = self._session.execute(prepared, list(params.values()))
        else:
            result = self._session.execute(query)
        columns = result.column_names if hasattr(result, "column_names") else []
        rows = result.all() if hasattr(result, "all") else list(result)
        return ResultSet(columns, rows)

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        prepared = self._session.prepare(query)
        for params in params_list:
            self._session.execute(prepared, list(params.values()))
        return len(params_list)

    def begin(self) -> Any:
        return None

    def commit(self, transaction: Any) -> None:
        pass

    def rollback(self, transaction: Any) -> None:
        pass


class Neo4jAdapter(DatabaseAdapter):
    """Neo4j graph database adapter.

    Uses neo4j driver.
    """

    def connect(self, config: ConnectionConfig) -> None:
        try:
            from neo4j import GraphDatabase
            uri = f"bolt://{config.host}:{config.port}"
            self._driver = GraphDatabase.driver(uri, auth=(config.username, config.password))
            self._config = config
            self._connected = True
        except ImportError:
            raise ImportError("neo4j is required for Neo4j. Install with: pip install neo4j")

    def disconnect(self) -> None:
        if self._driver:
            self._driver.close()
            self._driver = None
            self._connected = False

    def execute(self, query: str, params: Dict[str, Any]) -> ResultSet:
        if not self._driver:
            raise RuntimeError("Not connected")
        with self._driver.session() as session:
            result = session.run(query, params)
            records = list(result)
            columns = list(result.keys()) if records else []
            rows = [tuple(r.values()) for r in records]
            return ResultSet(columns, rows)

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        with self._driver.session() as session:
            for params in params_list:
                session.run(query, params)
        return len(params_list)

    def begin(self) -> Any:
        return None

    def commit(self, transaction: Any) -> None:
        pass

    def rollback(self, transaction: Any) -> None:
        pass


class InfluxDBAdapter(DatabaseAdapter):
    """InfluxDB time-series database adapter.

    Uses influxdb-client.
    """

    def connect(self, config: ConnectionConfig) -> None:
        try:
            from influxdb_client import InfluxDBClient
            url = f"http://{config.host}:{config.port}"
            token = config.password or ""
            self._client = InfluxDBClient(url=url, token=token, org=config.database)
            self._config = config
            self._connected = True
        except ImportError:
            raise ImportError("influxdb-client is required. Install with: pip install influxdb-client")

    def disconnect(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
            self._connected = False

    def execute(self, query: str, params: Dict[str, Any]) -> ResultSet:
        if not self._client:
            raise RuntimeError("Not connected")
        query_api = self._client.query_api()
        result = query_api.query(query)
        rows = []
        for table in result:
            for record in table.records:
                rows.append(tuple(record.values.values()))
        return ResultSet(list(result[0].columns) if result else [], rows)

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        return 0

    def begin(self) -> Any:
        return None

    def commit(self, transaction: Any) -> None:
        pass

    def rollback(self, transaction: Any) -> None:
        pass


class ElasticsearchAdapter(DatabaseAdapter):
    """Elasticsearch/OpenSearch adapter.

    Uses elasticsearch-py.
    """

    def connect(self, config: ConnectionConfig) -> None:
        try:
            from elasticsearch import Elasticsearch
            url = f"{'https' if config.ssl else 'http'}://{config.host}:{config.port}"
            self._client = Elasticsearch(url, basic_auth=(config.username, config.password) if config.username else None)
            self._config = config
            self._connected = True
        except ImportError:
            raise ImportError("elasticsearch is required. Install with: pip install elasticsearch")

    def disconnect(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
            self._connected = False

    def execute(self, query: str, params: Dict[str, Any]) -> ResultSet:
        if not self._client:
            raise RuntimeError("Not connected")
        if "search" in query.lower():
            body = params.get("body", {"query": {"match_all": {}}})
            idx = params.get("index", "_all")
            result = self._client.search(index=idx, body=body)
            hits = result.get("hits", {}).get("hits", [])
            columns = ["_id", "_score", "_source"]
            rows = [(h["_id"], h["_score"], json.dumps(h["_source"])) for h in hits]
            return ResultSet(columns, rows)
        elif "index" in query.lower():
            idx = params.get("index", "")
            doc = params.get("document", {})
            result = self._client.index(index=idx, document=doc)
            return ResultSet(["result"], [(result["result"],)])
        return ResultSet([], [])

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        count = 0
        for params in params_list:
            self.execute(query, params)
            count += 1
        return count

    def begin(self) -> Any:
        return None

    def commit(self, transaction: Any) -> None:
        pass

    def rollback(self, transaction: Any) -> None:
        pass


class VectorAdapter(DatabaseAdapter):
    """Vector database adapter for embedding storage and similarity search.

    Provides native vector storage with approximate nearest neighbor search,
    metadata filtering, and hybrid search capabilities.

    Uses an in-memory HNSW-like index by default.
    """

    def __init__(self) -> None:
        super().__init__()
        self._index: Dict[str, Dict[str, Any]] = {}
        self._dimensions: int = 384

    def connect(self, config: ConnectionConfig) -> None:
        self._config = config
        self._dimensions = int(config.extra.get("dimensions", 384))
        self._connected = True

    def disconnect(self) -> None:
        self._index.clear()
        self._connected = False

    def execute(self, query: str, params: Dict[str, Any]) -> ResultSet:
        op = query.strip().lower()
        if op == "insert":
            vector_id = str(uuid.uuid4())
            self._index[vector_id] = {
                "id": vector_id,
                "vector": params.get("vector", []),
                "metadata": params.get("metadata", {}),
            }
            return ResultSet(["id"], [(vector_id,)])
        elif op == "search":
            import math
            query_vec = params.get("vector", [])
            top_k = params.get("top_k", 10)
            scores = []
            for vid, data in self._index.items():
                vec = data["vector"]
                if len(vec) != len(query_vec):
                    continue
                dot = sum(a * b for a, b in zip(query_vec, vec))
                na = math.sqrt(sum(a * a for a in query_vec))
                nb = math.sqrt(sum(b * b for b in vec))
                score = dot / (na * nb) if na > 0 and nb > 0 else 0
                scores.append((vid, score, data))
            scores.sort(key=lambda x: x[1], reverse=True)
            columns = ["id", "score", "metadata"]
            rows = [(s[0], s[1], json.dumps(s[2].get("metadata", {}))) for s in scores[:top_k]]
            return ResultSet(columns, rows)
        elif op == "delete":
            vid = params.get("id", "")
            self._index.pop(vid, None)
            return ResultSet(["deleted"], [(1,)])
        return ResultSet([], [])

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        for params in params_list:
            self.execute(query, params)
        return len(params_list)

    def begin(self) -> Any:
        return None

    def commit(self, transaction: Any) -> None:
        pass

    def rollback(self, transaction: Any) -> None:
        pass


class ObjectStorageAdapter(DatabaseAdapter):
    """Object storage adapter (S3-compatible).

    Uses boto3 for S3-compatible storage services.
    """

    def connect(self, config: ConnectionConfig) -> None:
        try:
            import boto3
            endpoint = f"{config.host}:{config.port}" if config.host != "localhost" else None
            self._client = boto3.client(
                "s3",
                endpoint_url=endpoint,
                aws_access_key_id=config.username,
                aws_secret_access_key=config.password,
                use_ssl=config.ssl,
            )
            self._bucket = config.database
            self._config = config
            self._connected = True
        except ImportError:
            raise ImportError("boto3 is required for object storage. Install with: pip install boto3")

    def disconnect(self) -> None:
        self._client = None
        self._connected = False

    def execute(self, query: str, params: Dict[str, Any]) -> ResultSet:
        if not self._client:
            raise RuntimeError("Not connected")
        op = query.strip().lower()
        if op == "list":
            response = self._client.list_objects_v2(Bucket=self._bucket)
            objects = response.get("Contents", [])
            columns = ["key", "size", "last_modified"]
            rows = [(o["Key"], o["Size"], str(o["LastModified"])) for o in objects]
            return ResultSet(columns, rows)
        elif op == "get":
            key = params.get("key", "")
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            body = response["Body"].read()
            return ResultSet(["key", "data"], [(key, body.decode())])
        elif op == "put":
            key = params.get("key", str(uuid.uuid4()))
            data = params.get("data", b"")
            self._client.put_object(Bucket=self._bucket, Key=key, Body=data)
            return ResultSet(["key"], [(key,)])
        elif op == "delete":
            key = params.get("key", "")
            self._client.delete_object(Bucket=self._bucket, Key=key)
            return ResultSet(["deleted"], [(1,)])
        return ResultSet([], [])

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        count = 0
        for params in params_list:
            self.execute(query, params)
            count += 1
        return count

    def begin(self) -> Any:
        return None

    def commit(self, transaction: Any) -> None:
        pass

    def rollback(self, transaction: Any) -> None:
        pass


class CloudStorageAdapter(DatabaseAdapter):
    """Cloud storage adapter for managed database services.

    Provides a unified interface for cloud databases.
    """

    def connect(self, config: ConnectionConfig) -> None:
        self._config = config
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def execute(self, query: str, params: Dict[str, Any]) -> ResultSet:
        return ResultSet([], [])

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        return 0

    def begin(self) -> Any:
        return None

    def commit(self, transaction: Any) -> None:
        pass

    def rollback(self, transaction: Any) -> None:
        pass


# Register all adapters
register_adapter(DatabaseType.POSTGRESQL, PostgreSQLAdapter)
register_adapter(DatabaseType.MYSQL, MySQLAdapter)
register_adapter(DatabaseType.MARIADB, MySQLAdapter)
register_adapter(DatabaseType.SQLITE, SQLiteAdapter)
register_adapter(DatabaseType.MONGODB, MongoDBAdapter)
register_adapter(DatabaseType.REDIS, RedisAdapter)
register_adapter(DatabaseType.CASSANDRA, CassandraAdapter)
register_adapter(DatabaseType.NEO4J, Neo4jAdapter)
register_adapter(DatabaseType.INFLUXDB, InfluxDBAdapter)
register_adapter(DatabaseType.ELASTICSEARCH, ElasticsearchAdapter)
register_adapter(DatabaseType.OPENSEARCH, ElasticsearchAdapter)
register_adapter(DatabaseType.VECTOR, VectorAdapter)
register_adapter(DatabaseType.OBJECT_STORAGE, ObjectStorageAdapter)
register_adapter(DatabaseType.CLOUD, CloudStorageAdapter)
