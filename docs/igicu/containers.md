# IGICU Containers Guide

## Overview

IGICU provides a complete container platform for building, storing, and running
containerized applications.

## Container Runtime

### Building Images

```bash
# Build from a Dockerfile
isoko igicu image build my-app --context . --tag v1.0.0

# Build from igicu.json
# Create a igicu.json in your project root
```

Example `igicu.json`:
```json
{
  "layers": ["base", "deps", "app"],
  "files": ["src/", "config/", "requirements.txt"],
  "entrypoint": ["i", "run", "app.i"]
}
```

### Running Containers

```python
from igicu.ikorwa import ContainerRuntime, ContainerConfig

runtime = ContainerRuntime()
config = ContainerConfig(
    image="my-app:latest",
    name="web-server",
    ports={80: 8080},
    environment={"MODE": "production"},
)
container_id = runtime.create(config)
runtime.start(container_id)
print(f"Container running: {container_id}")
```

### Image Registry

```python
from igicu.ikorwa import ImageRegistry

registry = ImageRegistry()
registry.register(ImageConfig(name="my-app", tag="v1.0.0", size_mb=42.5))

# List all images
for img in registry.list():
    print(f"{img['id']} - {img['size_mb']}MB")
```

## Container Networking

IGICU supports multiple network modes:
- **bridge**: Isolated network with port mapping
- **host**: Direct host network access
- **overlay**: Multi-node networking
- **none**: No network

## Best Practices

1. Keep images small — use minimal base layers
2. Tag images with semantic versions
3. Use health checks for auto-recovery
4. Set resource limits for all containers
5. Use environment variables for configuration
