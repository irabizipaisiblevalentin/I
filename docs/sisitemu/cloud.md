# Cloud Infrastructure — `ibicu`

Build cloud infrastructure with containers, virtual machines, load balancers,
orchestrators, secrets management, and configuration management.

## Quick Start

```python
from sisitemu.ibicu import (
    ContainerRuntime, ContainerImage,
    LoadBalancer, LBAlgorithm,
    ConfigManager, SecretManager,
)

# Run a container
runtime = ContainerRuntime()
container = runtime.create("web-1", image="nginx:latest")
runtime.start(container.id)

# Load balancing
lb = LoadBalancer(algorithm=LBAlgorithm.ROUND_ROBIN)
lb.add_backend("10.0.0.1:8080")
lb.add_backend("10.0.0.2:8080")
server = lb.next("web-backend")
```

## Components

### ContainerRuntime
```python
runtime = ContainerRuntime()
c = runtime.create("app", image="python:3.11")
runtime.start(c.id)
runtime.exec(c.id, ["echo", "hello"])
state = runtime.status(c.id)
runtime.stop(c.id)
```

### VMManager
```python
vmm = VMManager()
vm = vmm.create("worker-1", image="ubuntu-22.04", vcpus=4, memory_mb=8192)
vmm.power_on(vm.id)
vmm.migrate(vm.id, target_host="node02")
vmm.power_off(vm.id)
```

### LoadBalancer
```python
lb = LoadBalancer(name="api-lb", algorithm=LBAlgorithm.LEAST_CONNECTIONS)
lb.add_backend("10.0.0.1:8080", weight=3)
lb.add_backend("10.0.0.2:8080", weight=1)
server = lb.next("api-lb")
```

### Orchestrator
```python
orch = Orchestrator()
deploy = orch.deploy(
    name="my-service",
    image="myapp:1.0.0",
    replicas=3,
    strategy=DeploymentStrategy.ROLLING,
)
orch.scale(deploy.id, replicas=5)
orch.rolling_update(deploy.id, image="myapp:1.0.1")
```

### SecretManager
```python
sm = SecretManager()
sm.store("db-password", value="s3cret!", encrypt=True)
password = sm.retrieve("db-password")
sm.rotate("db-password")
```

### ConfigManager
```python
cm = ConfigManager()
cm.set("log_level", "debug")
value = cm.get("log_level")
cm.watch("log_level", lambda key, val: print(f"{key}={val}"))
cm.hot_reload()
```

## Architecture

```
Cloud Infrastructure Stack
├── ContainerRuntime  — create, start, stop, exec containers
├── VMManager         — create, power on/off, migrate VMs
├── LoadBalancer      — R-R, least-connections, IP hash, weighted
├── Orchestrator      — deploy, scale, rolling update, blue-green
├── SecretManager     — store, retrieve, rotate, encrypt secrets
└── ConfigManager     — set, get, watch, hot-reload config
```
