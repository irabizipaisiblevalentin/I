# Rendering Guide

## Creating a Mesh
```python
from imikino.ishushanyo import Mesh, Material, RenderComponent
from imikino.ibikoreshingiro import Color

mesh = Mesh(name="Cube")
mesh.add_cube(size=2.0)

material = Material(name="Default", albedo=Color.red(), metallic=0.5, roughness=0.3)
```

## Camera Setup
```python
from imikino.ishushanyo import CameraComponent

camera = CameraComponent(fov=70, near=0.1, far=1000)
```

## Lights
```python
from imikino.ishushanyo import LightComponent

light = LightComponent(light_type="directional", intensity=1.0)
```
