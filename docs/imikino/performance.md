# Performance Guide

## Profiling
```bash
isoko imikino profile --duration 30 --output profile.json
```

## Engine Configuration
```python
from imikino.ikorwa import EngineConfig

config = EngineConfig(
    title="Optimized Game",
    width=1920, height=1080,
    vsync=True,
    max_fps=144,
)
```

## Best Practices
- Use object pooling for frequently spawned entities
- Batch render calls by material
- Use LOD (level of detail) for distant objects
- Occlusion culling for large scenes
- Pool particle systems instead of creating/destroying
- Use physics layers to filter collision checks
