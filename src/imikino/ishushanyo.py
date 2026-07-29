"""ishushanyo — Rendering pipeline: 2D, 3D, PBR, post-processing, particles."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .ibikoreshingiro import Vector2, Vector3, Color, Matrix4, Transform, Quaternion
from .imiyoborere import Component


class ShaderType(str, Enum):
    VERTEX = "vertex"
    FRAGMENT = "fragment"
    COMPUTE = "compute"
    GEOMETRY = "geometry"


class PrimitiveType(str, Enum):
    TRIANGLE = "triangle"
    TRIANGLE_STRIP = "triangle_strip"
    LINE = "line"
    LINE_STRIP = "line_strip"
    POINT = "point"


class BlendMode(str, Enum):
    OPAQUE = "opaque"
    TRANSPARENT = "transparent"
    ADDITIVE = "additive"
    MULTIPLY = "multiply"


class RenderQueue(str, Enum):
    BACKGROUND = "background"
    OPAQUE = "opaque"
    TRANSPARENT = "transparent"
    OVERLAY = "overlay"


@dataclass
class Vertex:
    position: Vector3 = field(default_factory=Vector3)
    normal: Vector3 = field(default_factory=Vector3)
    uv: Vector2 = field(default_factory=Vector2)
    color: Color = field(default_factory=Color.white)
    tangent: Vector3 = field(default_factory=Vector3)


@dataclass
class Mesh:
    vertices: List[Vertex] = field(default_factory=list)
    indices: List[int] = field(default_factory=list)
    name: str = "Mesh"

    def add_quad(self, size: float = 1.0) -> None:
        h = size / 2
        verts = [
            Vertex(position=Vector3(-h, -h, 0), uv=Vector2(0, 0)),
            Vertex(position=Vector3(h, -h, 0), uv=Vector2(1, 0)),
            Vertex(position=Vector3(h, h, 0), uv=Vector2(1, 1)),
            Vertex(position=Vector3(-h, h, 0), uv=Vector2(0, 1)),
        ]
        idx = [0, 1, 2, 0, 2, 3]
        self.vertices.extend(verts)
        self.indices.extend([i + len(self.vertices) - 4 for i in idx])

    def add_cube(self, size: float = 1.0) -> None:
        h = size / 2
        positions = [
            Vector3(-h, -h, -h), Vector3(h, -h, -h), Vector3(h, h, -h), Vector3(-h, h, -h),
            Vector3(-h, -h, h), Vector3(h, -h, h), Vector3(h, h, h), Vector3(-h, h, h),
        ]
        faces = [
            (0, 1, 2, 3), (1, 5, 6, 2), (5, 4, 7, 6),
            (4, 0, 3, 7), (3, 2, 6, 7), (4, 5, 1, 0),
        ]
        for quad in faces:
            for i in quad:
                self.vertices.append(Vertex(position=positions[i]))
            base = len(self.vertices) - 4
            self.indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])

    def add_sphere(self, radius: float = 0.5, segments: int = 16) -> None:
        for lat in range(segments + 1):
            theta = lat * 3.14159 / segments
            for lon in range(segments + 1):
                phi = lon * 2 * 3.14159 / segments
                x = radius * math.sin(theta) * math.cos(phi)
                y = radius * math.cos(theta)
                z = radius * math.sin(theta) * math.sin(phi)
                self.vertices.append(Vertex(position=Vector3(x, y, z)))
        for lat in range(segments):
            for lon in range(segments):
                first = lat * (segments + 1) + lon
                second = first + segments + 1
                self.indices.extend([first, second, first + 1, second, second + 1, first + 1])

    def combine(self, other: Mesh) -> None:
        base = len(self.vertices)
        self.vertices.extend(other.vertices)
        self.indices.extend(i + base for i in other.indices)


@dataclass
class Material:
    name: str = "Material"
    shader: str = "default"
    albedo: Color = field(default_factory=Color.white)
    metallic: float = 0.0
    roughness: float = 0.5
    emissive: Color = field(default_factory=Color.black)
    emissive_intensity: float = 0.0
    normal_strength: float = 1.0
    blend_mode: BlendMode = BlendMode.OPAQUE
    textures: Dict[str, str] = field(default_factory=dict)
    uniforms: Dict[str, Any] = field(default_factory=dict)
    cull_mode: str = "back"
    depth_test: bool = True
    depth_write: bool = True


@dataclass
class RenderComponent(Component):
    mesh: Optional[Mesh] = None
    material: Optional[Material] = None
    visible: bool = True
    render_queue: RenderQueue = RenderQueue.OPAQUE
    cast_shadows: bool = True
    receive_shadows: bool = True
    layer: int = 0


@dataclass
class LightComponent(Component):
    light_type: str = "directional"
    color: Color = field(default_factory=Color.white)
    intensity: float = 1.0
    range: float = 10.0
    spot_angle: float = 45.0
    shadows: bool = True


@dataclass
class CameraComponent(Component):
    fov: float = 70.0
    near: float = 0.1
    far: float = 1000.0
    orthographic: bool = False
    ortho_size: float = 10.0
    clear_color: Color = field(default_factory=lambda: Color(0.1, 0.1, 0.15, 1))
    priority: int = 0
    viewport_x: float = 0.0
    viewport_y: float = 0.0
    viewport_w: float = 1.0
    viewport_h: float = 1.0

    def projection_matrix(self, aspect: float) -> Matrix4:
        if self.orthographic:
            h = self.ortho_size
            w = h * aspect
            return Matrix4([
                1 / w, 0, 0, 0,
                0, 1 / h, 0, 0,
                0, 0, -2 / (self.far - self.near), 0,
                0, 0, -(self.far + self.near) / (self.far - self.near), 1,
            ])
        return Matrix4.perspective(self.fov * 3.14159 / 180, aspect, self.near, self.far)


@dataclass
class Particle:
    position: Vector3 = field(default_factory=Vector3)
    velocity: Vector3 = field(default_factory=Vector3)
    color: Color = field(default_factory=Color.white)
    size: float = 1.0
    life: float = 1.0
    max_life: float = 1.0


@dataclass
class ParticleSystemComponent(Component):
    particles: List[Particle] = field(default_factory=list)
    max_particles: int = 1000
    emission_rate: float = 10.0
    spawn_count: int = 1
    lifetime: float = 2.0
    speed: float = 5.0
    size_start: float = 0.5
    size_end: float = 0.1
    color_start: Color = field(default_factory=Color.white)
    color_end: Color = field(default_factory=lambda: Color(1, 1, 1, 0))
    gravity: Vector3 = field(default_factory=lambda: Vector3(0, -9.81, 0))
    playing: bool = True
    _accumulator: float = 0.0


@dataclass
class SpriteComponent(Component):
    texture: str = ""
    color: Color = field(default_factory=Color.white)
    size: Vector2 = field(default_factory=lambda: Vector2(1, 1))
    pivot: Vector2 = field(default_factory=lambda: Vector2(0.5, 0.5))
    flip_x: bool = False
    flip_y: bool = False
    tiling: Vector2 = field(default_factory=lambda: Vector2(1, 1))
    offset: Vector2 = field(default_factory=Vector2)


@dataclass
class TextComponent(Component):
    text: str = ""
    font: str = ""
    font_size: int = 32
    color: Color = field(default_factory=Color.white)
    alignment: str = "left"
    line_spacing: float = 1.2


class RenderingSystem:
    def __init__(self):
        self._renderables: List[Tuple[RenderComponent, Any]] = []
        self._lights: List[LightComponent] = []
        self._camera: Optional[CameraComponent] = None
        self.particles: List[ParticleSystemComponent] = []

    def add_renderable(self, renderable: RenderComponent, transform: Any) -> None:
        self._renderables.append((renderable, transform))

    def remove_renderable(self, renderable: RenderComponent) -> None:
        self._renderables = [(r, t) for r, t in self._renderables if r is not renderable]

    def set_camera(self, camera: CameraComponent) -> None:
        self._camera = camera

    def add_light(self, light: LightComponent) -> None:
        self._lights.append(light)

    def render(self) -> Dict[str, Any]:
        return {
            "renderables": len(self._renderables),
            "lights": len(self._lights),
            "camera": self._camera is not None,
            "particle_systems": len(self.particles),
        }

    def clear(self) -> None:
        self._renderables.clear()
        self._lights.clear()
        self.particles.clear()


import math

_rendering_system = RenderingSystem()


def get_rendering() -> RenderingSystem:
    return _rendering_system
