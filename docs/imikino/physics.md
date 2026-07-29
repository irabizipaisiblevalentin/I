# Physics Guide

## Rigid Bodies
```python
from imikino.ubwonekano import RigidBodyComponent, ColliderComponent, PhysicsBodyType

body = RigidBodyComponent(body_type=PhysicsBodyType.DYNAMIC, mass=2.0)
collider = ColliderComponent()
```

## Raycasting
```python
from imikino.ibikoreshingiro import Vector3

hit = physics.raycast(Vector3(0, 0, 0), Vector3(0, -1, 0), max_distance=100)
if hit:
    print(f"Hit: {hit.entity_id}")
```

## Forces
```python
physics.add_force(entity_id, Vector3(0, 10, 0))
physics.set_velocity(entity_id, Vector3(5, 0, 0))
```
