"""cyanditswe — Query Engine for the UBUBIKO data platform.

Provides fluent query building, raw queries, stored procedures,
full-text search, window functions, CTEs, and more.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union


class JoinType(enum.Enum):
    """Types of SQL joins."""

    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL OUTER JOIN"
    CROSS = "CROSS JOIN"


class OrderDirection(enum.Enum):
    """Sort order directions."""

    ASC = "ASC"
    DESC = "DESC"


@dataclass
class Join:
    """Defines a table join."""

    join_type: JoinType = JoinType.INNER
    table: str = ""
    alias: str = ""
    condition: str = ""


@dataclass
class OrderBy:
    """Defines an ORDER BY clause."""

    expression: str = ""
    direction: OrderDirection = OrderDirection.ASC


@dataclass
class Expression:
    """A SQL expression with optional parameters."""

    sql: str = ""
    params: Dict[str, Any] = field(default_factory=dict)


class QueryBuilder:
    """Fluent SQL query builder.

    Supports SELECT, INSERT, UPDATE, DELETE with joins,
    conditions, grouping, ordering, limiting, and more.
    """

    def __init__(self, table: str = "", alias: str = "") -> None:
        self._table: str = table
        self._alias: str = alias
        self._columns: List[str] = []
        self._joins: List[Join] = []
        self._conditions: List[str] = []
        self._params: Dict[str, Any] = {}
        self._param_counter: int = 0
        self._group_by: List[str] = []
        self._having: List[str] = []
        self._order_by: List[OrderBy] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._distinct: bool = False
        self._for_update: bool = False
        self._is_count: bool = False

    def _next_param(self, name: str = "p") -> str:
        self._param_counter += 1
        return f"{name}_{self._param_counter}"

    def from_table(self, table: str, alias: str = "") -> QueryBuilder:
        """Set the source table."""
        self._table = table
        self._alias = alias
        return self

    def select(self, *columns: str) -> QueryBuilder:
        """Set columns to select."""
        self._columns = list(columns) if columns else ["*"]
        return self

    def distinct(self, value: bool = True) -> QueryBuilder:
        """Enable DISTINCT selection."""
        self._distinct = value
        return self

    def join(self, table: str, condition: str, join_type: JoinType = JoinType.INNER,
             alias: str = "") -> QueryBuilder:
        """Add a JOIN clause."""
        self._joins.append(Join(join_type=join_type, table=table, alias=alias, condition=condition))
        return self

    def left_join(self, table: str, condition: str, alias: str = "") -> QueryBuilder:
        """Add a LEFT JOIN clause."""
        return self.join(table, condition, JoinType.LEFT, alias)

    def right_join(self, table: str, condition: str, alias: str = "") -> QueryBuilder:
        """Add a RIGHT JOIN clause."""
        return self.join(table, condition, JoinType.RIGHT, alias)

    def where(self, condition: str, **params: Any) -> QueryBuilder:
        """Add a WHERE condition."""
        self._conditions.append(condition)
        self._params.update(params)
        return self

    def where_eq(self, column: str, value: Any) -> QueryBuilder:
        """Add an equality condition."""
        param = self._next_param("eq")
        self._conditions.append(f"{column} = :{param}")
        self._params[param] = value
        return self

    def where_in(self, column: str, values: Sequence[Any]) -> QueryBuilder:
        """Add an IN condition."""
        if not values:
            self._conditions.append("1 = 0")
            return self
        params = []
        for i, val in enumerate(values):
            p = self._next_param("in")
            params.append(f":{p}")
            self._params[p] = val
        self._conditions.append(f"{column} IN ({', '.join(params)})")
        return self

    def where_like(self, column: str, pattern: str) -> QueryBuilder:
        """Add a LIKE condition."""
        param = self._next_param("like")
        self._conditions.append(f"{column} LIKE :{param}")
        self._params[param] = pattern
        return self

    def where_between(self, column: str, low: Any, high: Any) -> QueryBuilder:
        """Add a BETWEEN condition."""
        lp = self._next_param("btw1")
        hp = self._next_param("btw2")
        self._conditions.append(f"{column} BETWEEN :{lp} AND :{hp}")
        self._params[lp] = low
        self._params[hp] = high
        return self

    def where_null(self, column: str) -> QueryBuilder:
        """Add an IS NULL condition."""
        self._conditions.append(f"{column} IS NULL")
        return self

    def where_not_null(self, column: str) -> QueryBuilder:
        """Add an IS NOT NULL condition."""
        self._conditions.append(f"{column} IS NOT NULL")
        return self

    def group_by(self, *columns: str) -> QueryBuilder:
        """Add GROUP BY columns."""
        self._group_by = list(columns)
        return self

    def having(self, condition: str) -> QueryBuilder:
        """Add a HAVING condition."""
        self._having.append(condition)
        return self

    def order(self, expression: str, direction: OrderDirection = OrderDirection.ASC) -> QueryBuilder:
        """Add an ORDER BY clause."""
        self._order_by.append(OrderBy(expression=expression, direction=direction))
        return self

    def limit(self, count: int) -> QueryBuilder:
        """Set a row limit."""
        self._limit = count
        return self

    def offset(self, count: int) -> QueryBuilder:
        """Set an offset for pagination."""
        self._offset = count
        return self

    def for_update(self, value: bool = True) -> QueryBuilder:
        """Add FOR UPDATE locking."""
        self._for_update = value
        return self

    def build_select(self) -> Tuple[str, Dict[str, Any]]:
        """Build the SELECT query string and parameters."""
        if self._is_count:
            col_clause = "COUNT(*) AS cnt"
        else:
            col_clause = ", ".join(self._columns) if self._columns else "*"

        if self._distinct:
            col_clause = f"DISTINCT {col_clause}"

        parts = [f"SELECT {col_clause}"]
        table_ref = self._table
        if self._alias:
            table_ref = f"{self._table} AS {self._alias}"
        parts.append(f"FROM {table_ref}")

        for join in self._joins:
            ref = join.table
            if join.alias:
                ref = f"{join.table} AS {join.alias}"
            parts.append(f"{join.join_type.value} {ref} ON {join.condition}")

        if self._conditions:
            parts.append("WHERE " + " AND ".join(self._conditions))
        if self._group_by:
            parts.append("GROUP BY " + ", ".join(self._group_by))
        if self._having:
            parts.append("HAVING " + " AND ".join(self._having))
        if self._order_by:
            parts.append("ORDER BY " + ", ".join(f"{o.expression} {o.direction.value}" for o in self._order_by))
        if self._limit is not None:
            parts.append(f"LIMIT {self._limit}")
        if self._offset is not None:
            parts.append(f"OFFSET {self._offset}")
        if self._for_update:
            parts.append("FOR UPDATE")

        return "\n".join(parts), dict(self._params)

    def build_insert(self, data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Build an INSERT query."""
        columns = ", ".join(data.keys())
        params = ", ".join(f":{k}" for k in data)
        return f"INSERT INTO {self._table} ({columns}) VALUES ({params})", dict(data)

    def build_update(self, data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Build an UPDATE query."""
        set_clause = ", ".join(f"{k} = :_{k}" for k in data)
        params = {f"_{k}": v for k, v in data.items()}
        params.update({k: v for k, v in self._params.items() if k.startswith("p_")})

        param_map = dict(self._params)
        for k, v in data.items():
            key = f"_{k}"
            param_map[key] = v

        for k in list(param_map.keys()):
            if k in data:
                param_map[f"_{k}"] = param_map.pop(k)

        parts = [f"UPDATE {self._table} SET {set_clause}"]
        if self._conditions:
            parts.append("WHERE " + " AND ".join(self._conditions))

        return "\n".join(parts), param_map

    def build_delete(self) -> Tuple[str, Dict[str, Any]]:
        """Build a DELETE query."""
        parts = [f"DELETE FROM {self._table}"]
        if self._conditions:
            parts.append("WHERE " + " AND ".join(self._conditions))
        return "\n".join(parts), dict(self._params)

    def count(self) -> QueryBuilder:
        """Convert to a COUNT query."""
        self._is_count = True
        return self

    def __str__(self) -> str:
        sql, _ = self.build_select()
        return sql


class RawQuery:
    """Executes a raw SQL query."""

    def __init__(self, sql: str, params: Optional[Dict[str, Any]] = None) -> None:
        self._sql = sql
        self._params = params or {}

    @property
    def sql(self) -> str:
        return self._sql

    @property
    def params(self) -> Dict[str, Any]:
        return dict(self._params)

    def execute(self, adapter: Any) -> Any:
        """Execute against a database adapter."""
        return adapter.execute(self._sql, self._params)


class StoredProcedure:
    """Represents a stored procedure call."""

    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None) -> None:
        self._name = name
        self._params = params or {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def params(self) -> Dict[str, Any]:
        return dict(self._params)

    def call(self, adapter: Any) -> Any:
        """Call the stored procedure via adapter."""
        return adapter.call_procedure(self._name, self._params)


class FullTextSearch:
    """Full-text search query builder."""

    def __init__(self, table: str, columns: List[str], query: str) -> None:
        self._table = table
        self._columns = columns
        self._query = query
        self._limit: Optional[int] = None
        self._rank: bool = True

    def limit(self, count: int) -> FullTextSearch:
        self._limit = count
        return self

    def build(self) -> Tuple[str, Dict[str, Any]]:
        like_clauses = [f"{col} LIKE :q" for col in self._columns]
        sql = f"SELECT * FROM {self._table} WHERE {' OR '.join(like_clauses)}"
        params: Dict[str, Any] = {"q": f"%{self._query}%"}
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
        return sql, params


class WindowFunction:
    """Window function builder.

    Supports ROW_NUMBER, RANK, DENSE_RANK, NTILE, LEAD, LAG,
    SUM, AVG, COUNT, MIN, MAX over partitions.
    """

    def __init__(self, function: str, column: str) -> None:
        self._function = function
        self._column = column
        self._partition: List[str] = []
        self._order: List[OrderBy] = []

    def partition_by(self, *columns: str) -> WindowFunction:
        self._partition = list(columns)
        return self

    def order_by(self, expression: str, direction: OrderDirection = OrderDirection.ASC) -> WindowFunction:
        self._order.append(OrderBy(expression=expression, direction=direction))
        return self

    def build(self) -> str:
        parts = [f"{self._function}({self._column}) OVER ("]
        if self._partition:
            parts.append(f"PARTITION BY {', '.join(self._partition)}")
        if self._order:
            parts.append(f"ORDER BY {', '.join(f'{o.expression} {o.direction.value}' for o in self._order)}")
        parts.append(")")
        return " ".join(parts)


class CTE:
    """Common Table Expression (WITH clause)."""

    def __init__(self, name: str, query: Union[QueryBuilder, str]) -> None:
        self._name = name
        self._query = query
        self._recursive: bool = False

    def recursive(self, value: bool = True) -> CTE:
        self._recursive = value
        return self

    def build(self) -> str:
        query_str = str(self._query) if isinstance(self._query, QueryBuilder) else self._query
        return f"{'RECURSIVE ' if self._recursive else ''}{self._name} AS ({query_str})"
