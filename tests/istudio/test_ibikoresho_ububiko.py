"""Tests for istudio.ibikoresho_ububiko — Database Tools."""

from __future__ import annotations

from src.istudio.ibikoresho_ububiko import DatabaseExplorer


def test_database_explorer_init():
    de = DatabaseExplorer()
    assert de.list_connections() == []


def test_connect():
    de = DatabaseExplorer()
    name = de.connect("mydb", "sqlite:///test.db", db_type="sqlite")
    assert name == "mydb"
    conns = de.list_connections()
    assert len(conns) == 1
    assert conns[0]["type"] == "sqlite"
    assert conns[0]["connected"] is True


def test_disconnect():
    de = DatabaseExplorer()
    de.connect("mydb", "sqlite:///test.db")
    assert de.disconnect("mydb") is True
    assert de.disconnect("nonexistent") is False


def test_get_tables():
    de = DatabaseExplorer()
    de.connect("mydb", "sqlite:///test.db")
    assert de.get_tables() == []
    de.set_tables(["users", "posts"])
    assert len(de.get_tables()) == 2


def test_execute_query():
    de = DatabaseExplorer()
    de.connect("mydb", "sqlite:///test.db")
    result = de.execute_query("SELECT * FROM users")
    assert "columns" in result
    assert "rows" in result
    assert "execution_time_ms" in result


def test_get_schema():
    de = DatabaseExplorer()
    de.connect("mydb", "sqlite:///test.db")
    schema = de.get_schema("users")
    assert schema == []


def test_generate_select_query():
    de = DatabaseExplorer()
    sql = de.generate_select_query("users", columns=["id", "name"], where="active = 1")
    assert "SELECT id, name FROM users WHERE active = 1" == sql


def test_generate_select_all():
    de = DatabaseExplorer()
    sql = de.generate_select_query("users")
    assert sql == "SELECT * FROM users"


def test_generate_insert_query():
    de = DatabaseExplorer()
    sql = de.generate_insert_query("users", {"name": "Alice", "age": 30})
    assert "INSERT INTO users" in sql
    assert "Alice" in sql
    assert "30" in sql


def test_generate_update_query():
    de = DatabaseExplorer()
    sql = de.generate_update_query("users", {"name": "Bob"}, "id = 1")
    assert "UPDATE users SET" in sql
    assert "Bob" in sql
    assert "WHERE id = 1" in sql


def test_export_results():
    de = DatabaseExplorer()
    de.connect("mydb", "sqlite:///test.db")
    result = de.export_results("mydb", "SELECT * FROM users", format="json")
    assert result is not None


def test_connection_not_found():
    de = DatabaseExplorer()
    try:
        de.execute_query("SELECT 1")
        assert False, "Should have raised"
    except ConnectionError:
        pass
