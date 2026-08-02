# ORM Guide (Ububazimurizo)

## Defining an Entity

```python
from ububiko.ububazimurizo import Entity, Field, Relationship


class User(Entity):
    __table__ = "users"

    id = Field(field_type=int, primary_key=True)
    name = Field(field_type=str, max_length=255)
    email = Field(field_type=str, unique=True, max_length=255)


class Post(Entity):
    __table__ = "posts"

    id = Field(field_type=int, primary_key=True)
    title = Field(field_type=str, max_length=255)
    content = Field(field_type=str)
    user_id = Field(field_type=int)
    author = Relationship(type=RelationshipType.MANY_TO_ONE, target="User", foreign_key="user_id")
```

## Using Repositories

```python
from ububiko.ububazimurizo import Repository
from ububiko.ikusanyamakuru import SQLiteAdapter
from ububiko.ikubamiro import ConnectionConfig, DatabaseType

adapter = SQLiteAdapter()
adapter.connect(ConnectionConfig(db_type=DatabaseType.SQLITE))

repo = Repository(User, adapter)
repo.create_table()

user = User(name="I Developer", email="dev@example.com")
repo.save(user)

all_users = repo.all()
found = repo.find(email="dev@example.com")
```

## Change Tracking

```python
tracker = ChangeTracker()
tracker.track_add(user)
tracker.track_modify(user)
tracker.flush()
```

## Batch Operations

```python
users = [User(name=f"User {i}") for i in range(100)]
repo.bulk_insert(users)
```
