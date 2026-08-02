# Migration Guide (Imuka)

## Defining Migrations

```python
from ububiko.imuka import Migration, MigrationEngine, TableDef, ColumnDef, ColumnType


class CreateUsersTable(Migration):
    version = "20250101000000"
    description = "Create users table"

    def up(self, engine: MigrationEngine) -> None:
        table = TableDef(name="users")
        table.columns = [
            ColumnDef(name="id", col_type=ColumnType.INTEGER, primary_key=True, auto_increment=True),
            ColumnDef(name="name", col_type=ColumnType.VARCHAR, nullable=False),
            ColumnDef(name="email", col_type=ColumnType.VARCHAR, unique=True, nullable=False),
            ColumnDef(name="created_at", col_type=ColumnType.TIMESTAMP),
        ]
        engine.execute(table.to_create_sql(), {})
        engine.execute(
            "CREATE INDEX idx_users_email ON users (email)", {}
        )

    def down(self, engine: MigrationEngine) -> None:
        engine.execute("DROP TABLE IF EXISTS users", {})

    def seed(self, engine: MigrationEngine) -> None:
        engine.execute(
            "INSERT INTO users (name, email) VALUES (:name, :email)",
            {"name": "Admin", "email": "admin@example.com"},
        )
```

## Running Migrations

```python
import sqlite3
from ububiko.ikusanyamakuru import SQLiteAdapter
from ububiko.ikubamiro import ConnectionConfig, DatabaseType
from ububiko.imuka import MigrationEngine

adapter = SQLiteAdapter()
adapter.connect(ConnectionConfig(db_type=DatabaseType.SQLITE, database="app.db"))

engine = MigrationEngine(adapter, "migrations")
engine.register_class(CreateUsersTable)

# Apply
results = engine.migrate()

# Rollback
results = engine.rollback()

# Status
status = engine.status()
print(f"Pending: {status['pending_versions']}")

# Generate new migration
path = engine.generate_migration("add_posts_table")
```

## CLI

```bash
isoko ububiko migrate --db-type sqlite --database app.db
isoko ububiko rollback --version 20250101000000
isoko ububiko seed
isoko ububiko validate
```
