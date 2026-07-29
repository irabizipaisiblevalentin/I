"""itegeko — CLI commands for the UBUBIKO data platform.

Implements isoko ububiko commands:
  new, migrate, rollback, seed, validate, inspect, backup, restore, sync
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

from ububiko.ikubamiro import ConnectionConfig, ConnectionManager, DatabaseType
from ububiko.ikusanyamakuru import get_adapter
from ububiko.imuka import Migration, MigrationEngine


def _get_adapter_and_engine(args: argparse.Namespace) -> tuple:
    config = _build_config(args)
    adapter_cls = get_adapter(config.db_type)
    adapter = adapter_cls()
    adapter.connect(config)
    migrations_dir = args.migrations_dir if hasattr(args, "migrations_dir") and args.migrations_dir else "migrations"
    engine = MigrationEngine(adapter, migrations_dir)
    return adapter, engine, config


def _build_config(args: argparse.Namespace) -> ConnectionConfig:
    db_type_str = args.db_type if hasattr(args, "db_type") and args.db_type else "sqlite"
    db_type_map = {e.value: e for e in DatabaseType}
    db_type = db_type_map.get(db_type_str, DatabaseType.SQLITE)
    return ConnectionConfig(
        db_type=db_type,
        host=args.host if hasattr(args, "host") and args.host else "localhost",
        port=int(args.port) if hasattr(args, "port") and args.port else 0,
        database=args.database if hasattr(args, "database") and args.database else ":memory:",
        username=args.user if hasattr(args, "user") and args.user else "",
        password=args.password if hasattr(args, "password") and args.password else "",
        connection_string=args.connection_string if hasattr(args, "connection_string") and args.connection_string else "",
    )


def cmd_new(args: argparse.Namespace) -> int:
    """Create a new UBUBIKO project."""
    project_name = args.name
    path = os.path.join(os.getcwd(), project_name)
    os.makedirs(path, exist_ok=True)
    os.makedirs(os.path.join(path, "migrations"), exist_ok=True)
    os.makedirs(os.path.join(path, "models"), exist_ok=True)

    config = {
        "name": project_name,
        "version": "0.1.0",
        "database": {
            "type": "sqlite",
            "name": f"{project_name}.db",
        },
        "migrations_dir": "migrations",
        "models_dir": "models",
    }
    config_path = os.path.join(path, "ububiko.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    init_model = '''"""Models for {name}."""

from ububiko.ububazimurizo import Entity, Field, Relationship


class User(Entity):
    __table__ = "users"

    id = Field(field_type=int, primary_key=True, auto_increment=True)
    name = Field(field_type=str, max_length=255)
    email = Field(field_type=str, unique=True, max_length=255)
'''.format(name=project_name)

    with open(os.path.join(path, "models", "__init__.py"), "w", encoding="utf-8") as f:
        f.write(init_model)

    print(f"Created UBUBIKO project: {project_name}")
    print(f"  {config_path}")
    print(f"  {os.path.join(path, 'migrations')}")
    print(f"  {os.path.join(path, 'models')}")
    return 0


def cmd_migrate(args: argparse.Namespace) -> int:
    """Run pending migrations."""
    adapter, engine, config = _get_adapter_and_engine(args)
    engine.load_from_directory()
    results = engine.migrate()
    for r in results:
        print(r)
    print(f"Migrations applied: {len(results)}")
    adapter.disconnect()
    return 0


def cmd_rollback(args: argparse.Namespace) -> int:
    """Roll back migrations."""
    adapter, engine, config = _get_adapter_and_engine(args)
    engine.load_from_directory()
    target = args.version if hasattr(args, "version") and args.version else ""
    results = engine.rollback(target)
    for r in results:
        print(r)
    print(f"Rolled back: {len(results)}")
    adapter.disconnect()
    return 0


def cmd_seed(args: argparse.Namespace) -> int:
    """Run seed data."""
    adapter, engine, config = _get_adapter_and_engine(args)
    engine.seed()
    print("Seed data applied")
    adapter.disconnect()
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate database schema and data."""
    adapter, engine, config = _get_adapter_and_engine(args)
    status = engine.status()
    print(f"Migrations: {status['total']} total, {status['applied']} applied, {status['pending']} pending")
    adapter.disconnect()
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    """Inspect database structure."""
    adapter, engine, config = _get_adapter_and_engine(args)
    tables = adapter.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", {}
    )
    print(f"Database: {config.database}")
    print(f"Type: {config.db_type.value}")
    print(f"\nTables ({len(tables)}):")
    for (name,) in tables:
        count = adapter.execute(f"SELECT COUNT(*) FROM {name}", {})
        row_count = count[0][0] if count else 0
        print(f"  - {name} ({row_count} rows)")
    adapter.disconnect()
    return 0


def cmd_backup(args: argparse.Namespace) -> int:
    """Backup the database."""
    adapter, engine, config = _get_adapter_and_engine(args)
    output = args.output if hasattr(args, "output") and args.output else f"backup_{config.database}"
    try:
        tables = adapter.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", {}
        )
        backup_data: Dict[str, Any] = {}
        for (name,) in tables:
            rows = adapter.execute(f"SELECT * FROM {name}", {})
            backup_data[name] = [dict(r) for r in rows]
        backup_data["_meta"] = {
            "database": config.database,
            "type": config.db_type.value,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        }
        with open(output, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, default=str)
        print(f"Backup saved: {output} ({len(backup_data)} tables)")
    except Exception as e:
        print(f"Backup failed: {e}")
        return 1
    finally:
        adapter.disconnect()
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    """Restore database from backup."""
    adapter, engine, config = _get_adapter_and_engine(args)
    source = args.source
    if not os.path.isfile(source):
        print(f"Backup file not found: {source}")
        return 1
    try:
        with open(source, "r", encoding="utf-8") as f:
            backup_data = json.load(f)
        for table_name, rows in backup_data.items():
            if table_name == "_meta":
                continue
            if rows:
                cols = list(rows[0].keys())
                placeholders = ", ".join(f":{c}" for c in cols)
                adapter.execute(f"DELETE FROM {table_name}", {})
                for row in rows:
                    adapter.execute(
                        f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})",
                        row,
                    )
        print(f"Restored {len(backup_data) - 1} tables from {source}")
    except Exception as e:
        print(f"Restore failed: {e}")
        return 1
    finally:
        adapter.disconnect()
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    """Sync data between databases."""
    print("Sync requires source and target configuration.")
    print("Use: isoko ububiko sync --source <config> --target <config>")
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate artifacts from a model definition using IHuriro."""
    if args.list_targets:
        from ububiko.ihuriro import IHuriro
        engine = IHuriro()
        _register_all_generators(engine)
        print("Available generator targets:")
        for t in engine.registered_targets:
            print(f"  - {t}")
        return 0

    if not args.entity:
        print("Error: specify an entity class path or use --list-targets")
        return 1

    import importlib
    entity_path = args.entity
    try:
        module_path, class_name = entity_path.rsplit(".", 1)
        mod = importlib.import_module(module_path)
        entity_class = getattr(mod, class_name)
    except Exception as e:
        print(f"Error loading entity '{entity_path}': {e}")
        return 1

    from ububiko.ihuriro.inkomoko import from_entity
    from ububiko.ihuriro import IHuriro

    model = from_entity(entity_class)
    if args.targets:
        model.generate = [t for t in args.targets if t in (
            "database", "validation", "rest_api", "graphql",
            "serialization", "forms", "admin", "docs",
            "test_data", "embeddings",
        )]

    engine = IHuriro()
    _register_all_generators(engine)
    results = engine.generate(model, output_dir=args.output)
    summary = engine.summary()

    print(f"Generated artifacts for {model.name}:")
    for target, files in results.items():
        print(f"  [{target}] {len(files)} file(s)")
        for fname in files:
            print(f"    {fname}")
    print(f"\nTotal: {summary['total_files']} files → {args.output}/")
    return 0


def _register_all_generators(engine: Any) -> None:
    from ububiko.ihuriro.ibyara import (
        DatabaseGenerator, ValidationGenerator, RestApiGenerator,
        GraphQLGenerator, SerializationGenerator, FormGenerator,
        AdminGenerator, DocumentationGenerator, TestDataGenerator,
        EmbeddingGenerator,
    )
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


def kongera_iyobokamana(subparsers: Any) -> None:
    """Register ububiko subcommands."""
    parser = subparsers.add_parser("ububiko", help="UBUBIKO data platform commands")
    ub_sub = parser.add_subparsers(dest="ububiko_command", help="UBUBIKO subcommand")

    p_new = ub_sub.add_parser("new", help="Create a new UBUBIKO project")
    p_new.add_argument("name", help="Project name")
    p_new.set_defaults(func=cmd_new)

    p_migrate = ub_sub.add_parser("migrate", help="Run pending migrations")
    p_migrate.add_argument("--db-type", default="sqlite", help="Database type")
    p_migrate.add_argument("--host", default="localhost", help="Database host")
    p_migrate.add_argument("--port", default="", help="Database port")
    p_migrate.add_argument("--database", default=":memory:", help="Database name")
    p_migrate.add_argument("--user", default="", help="Database user")
    p_migrate.add_argument("--password", default="", help="Database password")
    p_migrate.add_argument("--connection-string", default="", help="Full connection string")
    p_migrate.add_argument("--migrations-dir", default="migrations", help="Migrations directory")
    p_migrate.set_defaults(func=cmd_migrate)

    p_rollback = ub_sub.add_parser("rollback", help="Roll back migrations")
    p_rollback.add_argument("--version", default="", help="Target version to roll back to")
    p_rollback.add_argument("--db-type", default="sqlite")
    p_rollback.add_argument("--host", default="localhost")
    p_rollback.add_argument("--port", default="")
    p_rollback.add_argument("--database", default=":memory:")
    p_rollback.add_argument("--user", default="")
    p_rollback.add_argument("--password", default="")
    p_rollback.add_argument("--connection-string", default="")
    p_rollback.add_argument("--migrations-dir", default="migrations")
    p_rollback.set_defaults(func=cmd_rollback)

    p_seed = ub_sub.add_parser("seed", help="Run seed data")
    p_seed.add_argument("--db-type", default="sqlite")
    p_seed.add_argument("--host", default="localhost")
    p_seed.add_argument("--port", default="")
    p_seed.add_argument("--database", default=":memory:")
    p_seed.add_argument("--user", default="")
    p_seed.add_argument("--password", default="")
    p_seed.add_argument("--connection-string", default="")
    p_seed.set_defaults(func=cmd_seed)

    p_validate = ub_sub.add_parser("validate", help="Validate database schema")
    p_validate.add_argument("--db-type", default="sqlite")
    p_validate.add_argument("--host", default="localhost")
    p_validate.add_argument("--port", default="")
    p_validate.add_argument("--database", default=":memory:")
    p_validate.add_argument("--user", default="")
    p_validate.add_argument("--password", default="")
    p_validate.add_argument("--connection-string", default="")
    p_validate.set_defaults(func=cmd_validate)

    p_inspect = ub_sub.add_parser("inspect", help="Inspect database structure")
    p_inspect.add_argument("--db-type", default="sqlite")
    p_inspect.add_argument("--host", default="localhost")
    p_inspect.add_argument("--port", default="")
    p_inspect.add_argument("--database", default=":memory:")
    p_inspect.add_argument("--user", default="")
    p_inspect.add_argument("--password", default="")
    p_inspect.add_argument("--connection-string", default="")
    p_inspect.set_defaults(func=cmd_inspect)

    p_backup = ub_sub.add_parser("backup", help="Backup database")
    p_backup.add_argument("output", nargs="?", default="", help="Output file path")
    p_backup.add_argument("--db-type", default="sqlite")
    p_backup.add_argument("--host", default="localhost")
    p_backup.add_argument("--port", default="")
    p_backup.add_argument("--database", default=":memory:")
    p_backup.add_argument("--user", default="")
    p_backup.add_argument("--password", default="")
    p_backup.add_argument("--connection-string", default="")
    p_backup.set_defaults(func=cmd_backup)

    p_restore = ub_sub.add_parser("restore", help="Restore database from backup")
    p_restore.add_argument("source", help="Backup file path")
    p_restore.add_argument("--db-type", default="sqlite")
    p_restore.add_argument("--host", default="localhost")
    p_restore.add_argument("--port", default="")
    p_restore.add_argument("--database", default=":memory:")
    p_restore.add_argument("--user", default="")
    p_restore.add_argument("--password", default="")
    p_restore.add_argument("--connection-string", default="")
    p_restore.set_defaults(func=cmd_restore)

    p_sync = ub_sub.add_parser("sync", help="Sync data between databases")
    p_sync.add_argument("--source", default="", help="Source config")
    p_sync.add_argument("--target", default="", help="Target config")
    p_sync.set_defaults(func=cmd_sync)

    # Generate command
    p_gen = ub_sub.add_parser("generate", help="Generate artifacts from a model definition")
    p_gen.add_argument("entity", nargs="?", help="Entity class path (e.g. myapp.models.User)")
    p_gen.add_argument("--targets", nargs="*", default=[],
                       help="Generator targets: database validation rest_api graphql serialization forms admin docs test_data embeddings")
    p_gen.add_argument("--output", "-o", default="generated", help="Output directory")
    p_gen.add_argument("--list-targets", action="store_true", help="List available generator targets")
    p_gen.set_defaults(func=cmd_generate)

    parser.set_defaults(func=lambda a: parser.print_help())


def genda(args: argparse.Namespace) -> int:
    """Execute ububiko commands."""
    if not hasattr(args, "ububiko_command") or not args.ububiko_command:
        print("ububiko: missing subcommand")
        print("  Try: isoko ububiko --help")
        return 1
    if hasattr(args, "func"):
        return args.func(args)
    print(f"ububiko: unknown subcommand: {args.ububiko_command}")
    return 1
