"""ubwonekano — Physics engine: rigid bodies, collision detection, constraints."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .ibikoreshingiro import Vector3, Transform, Matrix4, clamp, lerp
from .imiyoborere import Component


class CollisionShape(str, Enum):
    SPHERE = "sphere"
    BOX = "box"
    CAPSULE = "capsule"
    PLANE = "plane"
    MESH = "mesh"
    CYLINDER = "cylinder"


class PhysicsBodyType(str, Enum):
    STATIC = "static"
    DYNAMIC = "dynamic"
    KINEMATIC = "kinematic"


@dataclass
class RigidBodyComponent(Component):
    body_type: PhysicsBodyType = PhysicsBodyType.DYNAMIC
    mass: float = 1.0
    drag: float = 0.01
    angular_drag: float = 0.05
    gravity_scale: float = 1.0
    velocity: Vector3 = field(default_factory=Vector3)
    angular_velocity: Vector3 = field(default_factory=Vector3)
    use_gravity: bool = True
    is_sleeping: bool = False
    freeze_rotation: bool = False
    freeze_position: bool = False


@dataclass
class ColliderComponent(Component):
    shape: CollisionShape = CollisionShape.BOX
    size: Vector3 = field(default_factory=lambda: Vector3(1, 1, 1))
    radius: float = 0.5
    height: float = 1.0
    center: Vector3 = field(default_factory=Vector3)
    is_trigger: bool = False
    friction: float = 0.5
    restitution: float = 0.3
    density: float = 1.0
    is_sensor: bool = False


@dataclass
class CollisionInfo:
    entity_a: str = ""
    entity_b: str = ""
    contact_point: Vector3 = field(default_factory=Vector3)
    contact_normal: Vector3 = field(default_factory=Vector3)
    penetration: float = 0.0
    impulse: float = 0.0


@dataclass
class JointComponent(Component):
    joint_type: str = "fixed"
    connected_entity: str = ""
    anchor: Vector3 = field(default_factory=Vector3)
    break_force: float = float('inf')
    break_torque: float = float('inf')


@dataclass
class RaycastHit:
    entity_id: str = ""
    point: Vector3 = field(default_factory=Vector3)
    normal: Vector3 = field(default_factory=Vector3)
    distance: float = 0.0


class PhysicsSystem:
    def __init__(self):
        self.gravity = Vector3(0, -9.81, 0)
        self.bodies: Dict[str, RigidBodyComponent] = {}
        self.colliders: Dict[str, ColliderComponent] = {}
        self.collision_pairs: List[Tuple[str, str]] = []
        self._contacts: List[CollisionInfo] = []

    def add_body(self, entity_id: str, body: RigidBodyComponent,
                 collider: Optional[ColliderComponent] = None) -> None:
        self.bodies[entity_id] = body
        if collider:
            self.colliders[entity_id] = collider

    def remove_body(self, entity_id: str) -> None:
        self.bodies.pop(entity_id, None)
        self.colliders.pop(entity_id, None)

    def add_force(self, entity_id: str, force: Vector3) -> None:
        body = self.bodies.get(entity_id)
        if body and body.body_type == PhysicsBodyType.DYNAMIC:
            accel = Vector3(force.x / body.mass, force.y / body.mass, force.z / body.mass)
            body.velocity += accel * 0.016

    def set_velocity(self, entity_id: str, velocity: Vector3) -> None:
        body = self.bodies.get(entity_id)
        if body:
            body.velocity = velocity

    def raycast(self, origin: Vector3, direction: Vector3,
                max_distance: float = 1000.0) -> Optional[RaycastHit]:
        direction = direction.normalize()
        closest: Optional[RaycastHit] = None
        closest_dist = max_distance
        for eid, collider in self.colliders.items():
            c = collider.center
            to_center = Vector3(c.x - origin.x, c.y - origin.y, c.z - origin.z)
            dist = to_center.dot(direction)
            if dist < 0 or dist > closest_dist:
                continue
            hit_point = Vector3(
                origin.x + direction.x * dist,
                origin.y + direction.y * dist,
                origin.z + direction.z * dist,
            )
            d = hit_point.distance_to(Vector3(c.x, c.y, c.z))
            if d < max(collider.size.x, collider.size.y, collider.size.z) * 0.5:
                if dist < closest_dist:
                    closest = RaycastHit(
                        entity_id=eid, point=hit_point,
                        normal=direction * -1, distance=dist,
                    )
                    closest_dist = dist
        return closest

    def update(self, dt: float) -> None:
        self._contacts.clear()
        for eid, body in self.bodies.items():
            if body.body_type != PhysicsBodyType.DYNAMIC or body.is_sleeping:
                continue
            if body.use_gravity:
                body.velocity += Vector3(
                    self.gravity.x * body.gravity_scale * dt,
                    self.gravity.y * body.gravity_scale * dt,
                    self.gravity.z * body.gravity_scale * dt,
                )
            body.velocity *= max(0, 1 - body.drag * dt)
            if not body.freeze_position:
                pass
        self._detect_collisions()

    def _detect_collisions(self) -> None:
        eids = list(self.colliders.keys())
        for i in range(len(eids)):
            for j in range(i + 1, len(eids)):
                a, b = eids[i], eids[j]
                coll_a = self.colliders[a]
                coll_b = self.colliders[b]
                if self._sphere_sphere(a, coll_a, b, coll_b):
                    self._contacts.append(CollisionInfo(
                        entity_a=a, entity_b=b,
                        penetration=0.1,
                    ))

    def _sphere_sphere(self, a_id: str, a: ColliderComponent,
                       b_id: str, b: ColliderComponent) -> bool:
        dist = a.center.distance_to(b.center)
        return dist < (a.radius + b.radius)

    @property
    def contacts(self) -> List[CollisionInfo]:
        return self._contacts

    def summary(self) -> Dict[str, Any]:
        return {
            "bodies": len(self.bodies),
            "colliders": len(self.colliders),
            "contacts": len(self._contacts),
        }


_physics = PhysicsSystem()


def get_physics() -> PhysicsSystem:
    return _physics
