# Query Guide (Cyanditswe)

## Fluent Query Builder

```python
from ububiko.cyanditswe import QueryBuilder, JoinType, OrderDirection

# Build a SELECT query
qb = QueryBuilder("users")
qb.select("id", "name", "email")
qb.where_eq("active", True)
qb.order("name", OrderDirection.ASC)
qb.limit(10)

sql, params = qb.build_select()
# SELECT id, name, email FROM users WHERE active = :eq_1 ORDER BY name ASC LIMIT 10
```

## Joins

```python
qb = QueryBuilder("users")
qb.select("users.name", "posts.title")
qb.join("posts", "posts.user_id = users.id")
qb.where("posts.published = :pub", pub=True)
```

## Raw Queries

```python
from ububiko.cyanditswe import RawQuery

raw = RawQuery("SELECT * FROM users WHERE name LIKE :pattern", {"pattern": "%I%"})
results = raw.execute(adapter)
```

## Full-Text Search

```python
from ububiko.cyanditswe import FullTextSearch

fts = FullTextSearch("users", ["name", "email"], "developer")
fts.limit(5)
sql, params = fts.build()
```

## Window Functions

```python
from ububiko.cyanditswe import WindowFunction

wf = WindowFunction("ROW_NUMBER", "id")
wf.partition_by("status")
wf.order_by("created_at", OrderDirection.DESC)
# ROW_NUMBER(id) OVER (PARTITION BY status ORDER BY created_at DESC)
```

## CTEs

```python
from ububiko.cyanditswe import CTE

cte = CTE("active_users", qb)
cte.recursive()
```
