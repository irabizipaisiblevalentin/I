"""ibikoreshingiro — Core utilities, math primitives (vectors, matrices, transforms)."""

from __future__ import annotations

import math
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

T = TypeVar("T")


@dataclass
class Vector2:
    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2:
        return Vector2(self.x * scalar, self.y * scalar)

    def __neg__(self) -> Vector2:
        return Vector2(-self.x, -self.y)

    @property
    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self) -> Vector2:
        l = self.length
        if l == 0:
            return Vector2()
        return Vector2(self.x / l, self.y / l)

    def dot(self, other: Vector2) -> float:
        return self.x * other.x + self.y * other.y

    def distance_to(self, other: Vector2) -> float:
        return (self - other).length

    def lerp(self, other: Vector2, t: float) -> Vector2:
        return Vector2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
        )

    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y}


@dataclass
class Vector3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other: Vector3) -> Vector3:
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector3) -> Vector3:
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> Vector3:
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __neg__(self) -> Vector3:
        return Vector3(-self.x, -self.y, -self.z)

    @property
    def length(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self) -> Vector3:
        l = self.length
        if l == 0:
            return Vector3()
        return Vector3(self.x / l, self.y / l, self.z / l)

    def dot(self, other: Vector3) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vector3) -> Vector3:
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def distance_to(self, other: Vector3) -> float:
        return (self - other).length

    def lerp(self, other: Vector3, t: float) -> Vector3:
        return Vector3(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t,
        )

    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass
class Quaternion:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    w: float = 1.0

    @staticmethod
    def identity() -> Quaternion:
        return Quaternion(0, 0, 0, 1)

    @staticmethod
    def from_euler(pitch: float, yaw: float, roll: float) -> Quaternion:
        cp = math.cos(pitch / 2)
        sp = math.sin(pitch / 2)
        cy = math.cos(yaw / 2)
        sy = math.sin(yaw / 2)
        cr = math.cos(roll / 2)
        sr = math.sin(roll / 2)
        return Quaternion(
            sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy,
            cr * cp * cy + sr * sp * sy,
        )

    @staticmethod
    def from_axis_angle(axis: Vector3, angle: float) -> Quaternion:
        s = math.sin(angle / 2)
        return Quaternion(axis.x * s, axis.y * s, axis.z * s, math.cos(angle / 2))

    def normalize(self) -> Quaternion:
        l = math.sqrt(self.x**2 + self.y**2 + self.z**2 + self.w**2)
        if l == 0:
            return Quaternion.identity()
        return Quaternion(self.x / l, self.y / l, self.z / l, self.w / l)

    def to_euler(self) -> Vector3:
        t0 = 2.0 * (self.w * self.x + self.y * self.z)
        t1 = 1.0 - 2.0 * (self.x * self.x + self.y * self.y)
        rx = math.atan2(t0, t1)
        t2 = 2.0 * (self.w * self.y - self.z * self.x)
        t2 = max(-1.0, min(1.0, t2))
        ry = math.asin(t2)
        t3 = 2.0 * (self.w * self.z + self.x * self.y)
        t4 = 1.0 - 2.0 * (self.y * self.y + self.z * self.z)
        rz = math.atan2(t3, t4)
        return Vector3(rx, ry, rz)


@dataclass
class Matrix4:
    data: List[float] = field(default_factory=lambda: [
        1, 0, 0, 0,
        0, 1, 0, 0,
        0, 0, 1, 0,
        0, 0, 0, 1,
    ])

    @staticmethod
    def identity() -> Matrix4:
        return Matrix4()

    @staticmethod
    def translation(x: float, y: float, z: float) -> Matrix4:
        return Matrix4([
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            x, y, z, 1,
        ])

    @staticmethod
    def scaling(x: float, y: float, z: float) -> Matrix4:
        return Matrix4([
            x, 0, 0, 0,
            0, y, 0, 0,
            0, 0, z, 0,
            0, 0, 0, 1,
        ])

    @staticmethod
    def rotation(quat: Quaternion) -> Matrix4:
        q = quat.normalize()
        xx, yy, zz = q.x * q.x, q.y * q.y, q.z * q.z
        xy, xz, yz = q.x * q.y, q.x * q.z, q.y * q.z
        wx, wy, wz = q.w * q.x, q.w * q.y, q.w * q.z
        return Matrix4([
            1 - 2 * (yy + zz), 2 * (xy + wz), 2 * (xz - wy), 0,
            2 * (xy - wz), 1 - 2 * (xx + zz), 2 * (yz + wx), 0,
            2 * (xz + wy), 2 * (yz - wx), 1 - 2 * (xx + yy), 0,
            0, 0, 0, 1,
        ])

    @staticmethod
    def perspective(fov: float, aspect: float, near: float, far: float) -> Matrix4:
        f = 1.0 / math.tan(fov / 2)
        return Matrix4([
            f / aspect, 0, 0, 0,
            0, f, 0, 0,
            0, 0, (far + near) / (near - far), -1,
            0, 0, (2 * far * near) / (near - far), 0,
        ])

    @staticmethod
    def look_at(eye: Vector3, target: Vector3, up: Vector3) -> Matrix4:
        z = (eye - target).normalize()
        x = up.cross(z).normalize()
        y = z.cross(x)
        return Matrix4([
            x.x, y.x, z.x, 0,
            x.y, y.y, z.y, 0,
            x.z, y.z, z.z, 0,
            -x.dot(eye), -y.dot(eye), -z.dot(eye), 1,
        ])

    def multiply(self, other: Matrix4) -> Matrix4:
        a, b = self.data, other.data
        result = [0.0] * 16
        for row in range(4):
            for col in range(4):
                result[row * 4 + col] = sum(
                    a[row * 4 + k] * b[k * 4 + col] for k in range(4)
                )
        return Matrix4(result)


@dataclass
class Transform:
    position: Vector3 = field(default_factory=Vector3)
    rotation: Quaternion = field(default_factory=Quaternion.identity)
    scale: Vector3 = field(default_factory=lambda: Vector3(1, 1, 1))

    def to_matrix(self) -> Matrix4:
        t = Matrix4.translation(self.position.x, self.position.y, self.position.z)
        r = Matrix4.rotation(self.rotation)
        s = Matrix4.scaling(self.scale.x, self.scale.y, self.scale.z)
        return t.multiply(r).multiply(s)

    def forward(self) -> Vector3:
        euler = self.rotation.to_euler()
        return Vector3(
            -math.sin(euler.y),
            math.sin(euler.x) * math.cos(euler.y),
            -math.cos(euler.x) * math.cos(euler.y),
        ).normalize()

    def right(self) -> Vector3:
        euler = self.rotation.to_euler()
        return Vector3(
            math.cos(euler.y),
            0,
            math.sin(euler.y),
        ).normalize()

    def up(self) -> Vector3:
        return self.right().cross(self.forward()).normalize()

    def translate(self, x: float, y: float, z: float) -> None:
        self.position += Vector3(x, y, z)

    def rotate(self, pitch: float, yaw: float, roll: float) -> None:
        q = Quaternion.from_euler(pitch, yaw, roll)
        self.rotation = self.rotation.normalize()


class Clock:
    def __init__(self):
        self._start = time.perf_counter()
        self._last = self._start
        self._delta = 0.0
        self._total = 0.0
        self._fps = 0.0
        self._frame_count = 0
        self._fps_timer = 0.0

    def tick(self) -> float:
        now = time.perf_counter()
        self._delta = now - self._last
        self._last = now
        self._total += self._delta
        self._frame_count += 1
        self._fps_timer += self._delta
        if self._fps_timer >= 1.0:
            self._fps = self._frame_count / self._fps_timer
            self._frame_count = 0
            self._fps_timer = 0.0
        return self._delta

    @property
    def delta(self) -> float:
        return self._delta

    @property
    def total(self) -> float:
        return self._total

    @property
    def fps(self) -> float:
        return self._fps


class Random:
    @staticmethod
    def range(min_v: float, max_v: float) -> float:
        return random.uniform(min_v, max_v)

    @staticmethod
    def int_range(min_v: int, max_v: int) -> int:
        return random.randint(min_v, max_v)

    @staticmethod
    def in_unit_circle() -> Vector2:
        angle = random.uniform(0, 2 * math.pi)
        r = math.sqrt(random.uniform(0, 1))
        return Vector2(math.cos(angle) * r, math.sin(angle) * r)

    @staticmethod
    def in_unit_sphere() -> Vector3:
        theta = random.uniform(0, 2 * math.pi)
        phi = math.acos(2 * random.uniform(0, 1) - 1)
        r = random.uniform(0, 1) ** (1 / 3)
        return Vector3(
            r * math.sin(phi) * math.cos(theta),
            r * math.sin(phi) * math.sin(theta),
            r * math.cos(phi),
        )

    @staticmethod
    def on_unit_sphere() -> Vector3:
        v = Random.in_unit_sphere()
        return v.normalize()


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def clamp(value: float, min_v: float, max_v: float) -> float:
    return max(min_v, min(max_v, value))


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def generate_entity_id() -> str:
    return uuid.uuid4().hex[:16]


class Color:
    def __init__(self, r: float = 1, g: float = 1, b: float = 1, a: float = 1):
        self.r = clamp(r, 0, 1)
        self.g = clamp(g, 0, 1)
        self.b = clamp(b, 0, 1)
        self.a = clamp(a, 0, 1)

    @staticmethod
    def white() -> Color:
        return Color(1, 1, 1, 1)

    @staticmethod
    def black() -> Color:
        return Color(0, 0, 0, 1)

    @staticmethod
    def red() -> Color:
        return Color(1, 0, 0, 1)

    @staticmethod
    def green() -> Color:
        return Color(0, 1, 0, 1)

    @staticmethod
    def blue() -> Color:
        return Color(0, 0, 1, 1)

    @staticmethod
    def clear() -> Color:
        return Color(0, 0, 0, 0)

    def to_rgba(self) -> Tuple[int, int, int, int]:
        return (int(self.r * 255), int(self.g * 255), int(self.b * 255), int(self.a * 255))

    def to_dict(self) -> Dict[str, float]:
        return {"r": self.r, "g": self.g, "b": self.b, "a": self.a}
