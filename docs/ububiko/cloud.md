# Cloud Storage Guide

## Object Storage (S3-Compatible)

```python
from ububiko.ikubamiro import ConnectionConfig, DatabaseType
from ububiko.ikusanyamakuru import get_adapter

config = ConnectionConfig(
    db_type=DatabaseType.OBJECT_STORAGE,
    host="s3.amazonaws.com",
    database="my-bucket",
    username="ACCESS_KEY",
    password="SECRET_KEY",
)

adapter_cls = get_adapter(DatabaseType.OBJECT_STORAGE)
adapter = adapter_cls()
adapter.connect(config)

# List objects
result = adapter.execute("list", {})
for obj in result:
    print(obj["key"])

# Put object
adapter.execute("put", {"key": "hello.txt", "data": b"World"})

# Get object
result = adapter.execute("get", {"key": "hello.txt"})

# Delete object
adapter.execute("delete", {"key": "hello.txt"})
```

## Cloud Databases

```python
config = ConnectionConfig(
    db_type=DatabaseType.CLOUD,
    connection_string="cloud://my-instance.cloud.com/mydb",
)
```

## Vector Database

```python
config = ConnectionConfig(
    db_type=DatabaseType.VECTOR,
    extra={"dimensions": 384},
)

adapter_cls = get_adapter(DatabaseType.VECTOR)
adapter = adapter_cls()
adapter.connect(config)

# Insert vectors
adapter.execute("insert", {
    "vector": [0.1, 0.2, 0.3],
    "metadata": {"name": "UBUBIKO doc"},
})

# Search
results = adapter.execute("search", {
    "vector": query_vector,
    "top_k": 10,
})
```
