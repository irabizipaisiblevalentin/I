# Distributed Systems — `gukwirakwiza`

Build fault-tolerant distributed systems with Raft consensus, RPC, service
discovery, distributed locks, and message queues.

## Quick Start

```python
from sisitemu.gukwirakwiza import (
    RaftConsensus, RaftConfig, RaftRole,
    ServiceDiscovery, DistributedLock,
)

# Raft consensus
config = RaftConfig(
    node_id="node-1",
    peers=["node-2:9001", "node-3:9002"],
    election_timeout_ms=150,
)
raft = RaftConsensus(config)
raft.start()
raft.propose("set:key=value")
```

## Components

### RaftConsensus
```python
raft = RaftConsensus(config)
raft.start()
raft.propose("set:key=value")
```

### RPCServer
```python
def my_handler(request):
    return {"status": "ok"}

server = RPCServer(host="0.0.0.0", port=9001)
server.register_handler("my_method", my_handler)
server.start()
```

### ServiceDiscovery
```python
sd = ServiceDiscovery(host="0.0.0.0", port=8500)
sd.register(name="api-v1", host="10.0.0.1", port=8080, ttl=30)
instances = sd.discover("api-v1")
sd.unregister("api-v1", instance_id="...")
```

### DistributedLock
```python
lock = DistributedLock(host="redis:6379", ttl_ms=30_000)
token = lock.acquire("resource-1", holder="worker-1")
# ... do work ...
lock.release("resource-1", holder="worker-1", token=token)
```

### MessageQueue
```python
queue = MessageQueue()
queue.create_topic("events", partitions=3)
queue.publish("events", b"key", b"value")

def handler(msg):
    print(f"Received: key={msg.key}, value={msg.value}")

queue.subscribe("events", handler, consumer_group="workers")
```

## Architecture

```
Distributed Systems Stack
├── RaftConsensus    — leader election, log replication, safety
├── RPCServer        — method-based RPC framework
├── ServiceDiscovery — service registry with TTL health checks
├── DistributedLock  — fencing tokens, lease-based locking
└── MessageQueue     — partitioned pub/sub with consumer groups
```
