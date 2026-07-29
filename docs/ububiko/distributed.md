# Distributed Data Guide (Ikwirakwira)

## Replication

```python
from ububiko.ikwirakwira import Replicator, ReplicationConfig, ReplicationRole

config = ReplicationConfig(
    role=ReplicationRole.PRIMARY,
    replicas=["replica1:5432", "replica2:5432"],
    sync_mode="async",
)
replicator = Replicator(config)

replicator.record_change("users", "INSERT", {"id": 1, "name": "I Developer"})
replicator.propagate(replica_adapter)
```

## Sharding

```python
from ububiko.ikwirakwira import ShardManager, ShardConfig, ShardStrategy

manager = ShardManager(strategy=ShardStrategy.HASH)
manager.add_shard(ShardConfig(id="shard1", host="node1", database="db1", weight=2))
manager.add_shard(ShardConfig(id="shard2", host="node2", database="db2", weight=1))

shard = manager.get_shard_for("user_123")
```

## Distributed Transactions

```python
from ububiko.ikwirakwira import DistributedTransaction

tx = DistributedTransaction()
tx.add_participant("db1", adapter1)
tx.add_participant("db2", adapter2)

def transfer():
    adapter1.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1", {})
    adapter2.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2", {})

tx.execute(transfer)
```

## Read Replicas

```python
from ububiko.ikwirakwira import ReadReplicaManager

rr = ReadReplicaManager(primary, [replica1, replica2])
reader = rr.get_reader()  # Round-robin
writer = rr.get_writer()  # Always primary
```
