"""ikubamiro — Connection management for the UBUBIKO data platform.

Defines database types, connection configuration, connection pooling,
and the abstract connection interface used by all database adapters.
"""

from __future__ import annotations

import enum
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class DatabaseType(enum.Enum):
    """Supported database engine types."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MARIADB = "mariadb"
    SQLITE = "sqlite"
    MSSQL = "mssql"
    ORACLE = "oracle"
    MONGODB = "mongodb"
    REDIS = "redis"
    CASSANDRA = "cassandra"
    NEO4J = "neo4j"
    INFLUXDB = "influxdb"
    ELASTICSEARCH = "elasticsearch"
    OPENSEARCH = "opensearch"
    VECTOR = "vector"
    OBJECT_STORAGE = "object_storage"
    CLOUD = "cloud"


CONNECTION_STRING_PREFIXES: Dict[DatabaseType, str] = {
    DatabaseType.POSTGRESQL: "postgresql://",
    DatabaseType.MYSQL: "mysql://",
    DatabaseType.MARIADB: "mariadb://",
    DatabaseType.SQLITE: "sqlite://",
    DatabaseType.MSSQL: "mssql://",
    DatabaseType.ORACLE: "oracle://",
    DatabaseType.MONGODB: "mongodb://",
    DatabaseType.REDIS: "redis://",
    DatabaseType.CASSANDRA: "cassandra://",
    DatabaseType.NEO4J: "neo4j://",
    DatabaseType.INFLUXDB: "influxdb://",
    DatabaseType.ELASTICSEARCH: "http://",
    DatabaseType.OPENSEARCH: "http://",
    DatabaseType.VECTOR: "vector://",
    DatabaseType.OBJECT_STORAGE: "s3://",
    DatabaseType.CLOUD: "cloud://",
}


@dataclass
class ConnectionConfig:
    """Configuration for a database connection.

    Attributes:
        db_type: Type of database engine.
        host: Server hostname or IP.
        port: Server port.
        database: Database name.
        username: Authentication username.
        password: Authentication password.
        connection_string: Full connection string (overrides individual fields if set).
        pool_size: Maximum connections in pool.
        pool_timeout: Seconds to wait for a connection from pool.
        pool_recycle: Seconds after which to recycle connections.
        ssl: Whether to use SSL/TLS.
        ssl_ca: CA certificate path.
        ssl_cert: Client certificate path.
        ssl_key: Client key path.
        extra: Additional engine-specific parameters.
    """

    db_type: DatabaseType = DatabaseType.SQLITE
    host: str = "localhost"
    port: int = 0
    database: str = ":memory:"
    username: str = ""
    password: str = ""
    connection_string: str = ""
    pool_size: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    ssl: bool = False
    ssl_ca: str = ""
    ssl_cert: str = ""
    ssl_key: str = ""
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.port:
            default_ports = {
                DatabaseType.POSTGRESQL: 5432,
                DatabaseType.MYSQL: 3306,
                DatabaseType.MARIADB: 3306,
                DatabaseType.MSSQL: 1433,
                DatabaseType.ORACLE: 1521,
                DatabaseType.MONGODB: 27017,
                DatabaseType.REDIS: 6379,
                DatabaseType.CASSANDRA: 9042,
                DatabaseType.NEO4J: 7687,
                DatabaseType.INFLUXDB: 8086,
                DatabaseType.ELASTICSEARCH: 9200,
                DatabaseType.OPENSEARCH: 9200,
            }
            self.port = default_ports.get(self.db_type, 0)

    def to_connection_string(self) -> str:
        """Build a connection string from config fields."""
        if self.connection_string:
            return self.connection_string
        prefix = CONNECTION_STRING_PREFIXES.get(self.db_type, "")
        if self.db_type == DatabaseType.SQLITE:
            return f"sqlite:///{self.database}"
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"{prefix}{auth}{self.host}:{self.port}/{self.database}"

    @classmethod
    def from_env(cls, prefix: str = "DB_") -> ConnectionConfig:
        """Build config from environment variables."""
        db_type_str = os.environ.get(f"{prefix}TYPE", "sqlite")
        db_type_map = {e.value: e for e in DatabaseType}
        db_type = db_type_map.get(db_type_str, DatabaseType.SQLITE)
        return cls(
            db_type=db_type,
            host=os.environ.get(f"{prefix}HOST", "localhost"),
            port=int(os.environ.get(f"{prefix}PORT", "0")),
            database=os.environ.get(f"{prefix}NAME", ":memory:"),
            username=os.environ.get(f"{prefix}USER", ""),
            password=os.environ.get(f"{prefix}PASS", ""),
            connection_string=os.environ.get(f"{prefix}URL", ""),
            pool_size=int(os.environ.get(f"{prefix}POOL_SIZE", "10")),
            ssl=os.environ.get(f"{prefix}SSL", "").lower() == "true",
        )


class Connection:
    """Represents an active database connection.

    Wraps the raw adapter connection with context manager support,
    transaction management, and execution methods.
    """

    def __init__(self, adapter: Any, config: ConnectionConfig) -> None:
        self._adapter = adapter
        self._config = config
        self._closed = False
        self._transaction: Optional[Any] = None

    @property
    def adapter(self) -> Any:
        """The underlying database adapter."""
        return self._adapter

    @property
    def config(self) -> ConnectionConfig:
        """The connection configuration."""
        return self._config

    @property
    def closed(self) -> bool:
        """Whether this connection is closed."""
        return self._closed

    def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a query and return results."""
        if self._closed:
            raise RuntimeError("Connection is closed")
        return self._adapter.execute(query, params or {})

    def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> int:
        """Execute a query with multiple parameter sets."""
        if self._closed:
            raise RuntimeError("Connection is closed")
        return self._adapter.execute_many(query, params_list)

    def begin(self) -> Any:
        """Begin a transaction."""
        if self._closed:
            raise RuntimeError("Connection is closed")
        self._transaction = self._adapter.begin()
        return self._transaction

    def commit(self) -> None:
        """Commit the current transaction."""
        if self._transaction:
            self._adapter.commit(self._transaction)
            self._transaction = None

    def rollback(self) -> None:
        """Rollback the current transaction."""
        if self._transaction:
            self._adapter.rollback(self._transaction)
            self._transaction = None

    def close(self) -> None:
        """Close the connection."""
        if not self._closed:
            self._adapter.close()
            self._closed = True

    def __enter__(self) -> Connection:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()


class ConnectionManager:
    """Manages database connections with pooling support.

    Provides connection lifecycle management, pool configuration,
    and automatic cleanup.
    """

    def __init__(self) -> None:
        self._connections: Dict[str, Connection] = {}
        self._pools: Dict[str, Any] = {}

    def connect(self, config: ConnectionConfig, name: str = "default") -> Connection:
        """Create and register a new connection."""
        from ububiko.ikusanyamakuru import get_adapter
        adapter_cls = get_adapter(config.db_type)
        adapter = adapter_cls()
        adapter.connect(config)
        conn = Connection(adapter, config)
        self._connections[name] = conn
        return conn

    def get(self, name: str = "default") -> Optional[Connection]:
        """Get a connection by name."""
        return self._connections.get(name)

    def disconnect(self, name: str = "default") -> None:
        """Close and remove a connection."""
        conn = self._connections.pop(name, None)
        if conn:
            conn.close()

    def disconnect_all(self) -> None:
        """Close all connections."""
        for name in list(self._connections):
            self.disconnect(name)

    @property
    def active_count(self) -> int:
        """Number of active connections."""
        return len(self._connections)

    def __enter__(self) -> ConnectionManager:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.disconnect_all()
