"""ibintu_nyabutatu — Robotics simulation: robot models, kinematics, sensors, ROS2 interop."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ibikoreshingiro import Vector3, Vector2, Quaternion, Transform, Matrix4


class JointType(str, Enum):
    REVOLUTE = "revolute"
    PRISMATIC = "prismatic"
    FIXED = "fixed"
    SPHERICAL = "spherical"
    PLANAR = "planar"
    CONTINUOUS = "continuous"
    FLOATING = "floating"


class SensorType(str, Enum):
    LIDAR = "lidar"
    CAMERA = "camera"
    IMU = "imu"
    GPS = "gps"
    SONAR = "sonar"
    ENCODER = "encoder"
    FORCE_TORQUE = "force_torque"
    RANGE = "range"


@dataclass
class Joint:
    name: str = ""
    joint_type: JointType = JointType.REVOLUTE
    parent_link: str = ""
    child_link: str = ""
    origin: Transform = field(default_factory=Transform)
    axis: Vector3 = field(default_factory=lambda: Vector3(0, 0, 1))
    position: float = 0.0
    velocity: float = 0.0
    effort: float = 0.0
    position_lower: float = -math.pi
    position_upper: float = math.pi
    velocity_limit: float = 100.0
    effort_limit: float = 100.0


@dataclass
class Link:
    name: str = ""
    mass: float = 1.0
    inertia: List[float] = field(default_factory=lambda: [1, 0, 0, 0, 1, 0, 0, 0, 1])
    visual_mesh: str = ""
    collision_mesh: str = ""
    origin: Transform = field(default_factory=Transform)


class RobotModel:
    def __init__(self, name: str = "Robot"):
        self.name = name
        self.links: Dict[str, Link] = {}
        self.joints: Dict[str, Joint] = {}
        self.root_link: str = ""
        self._fk_cache: Dict[str, Transform] = {}

    def add_link(self, link: Link) -> Link:
        self.links[link.name] = link
        if not self.root_link:
            self.root_link = link.name
        return link

    def add_joint(self, joint: Joint) -> Joint:
        self.joints[joint.name] = joint
        return joint

    def get_joint_positions(self) -> Dict[str, float]:
        return {name: j.position for name, j in self.joints.items()}

    def set_joint_positions(self, positions: Dict[str, float]) -> None:
        for name, pos in positions.items():
            if name in self.joints:
                self.joints[name].position = pos
        self._fk_cache.clear()

    def forward_kinematics(self, joint_positions: Optional[Dict[str, float]] = None) -> Dict[str, Transform]:
        if joint_positions is not None:
            self.set_joint_positions(joint_positions)
        transforms: Dict[str, Transform] = {}
        if not self.root_link:
            return transforms
        transforms[self.root_link] = Transform()
        self._compute_fk(self.root_link, Transform(), transforms)
        return transforms

    def _compute_fk(self, link_name: str, parent_transform: Transform,
                    transforms: Dict[str, Transform]) -> None:
        transforms[link_name] = parent_transform
        for joint in self.joints.values():
            if joint.parent_link != link_name:
                continue
            child = joint.child_link
            if child not in self.links:
                continue
            joint_tf = self._joint_transform(joint)
            child_tf = Transform()
            child_tf.position = parent_transform.position + joint_tf.position
            transforms[child] = child_tf
            self._compute_fk(child, child_tf, transforms)

    def _joint_transform(self, joint: Joint) -> Transform:
        tf = Transform()
        if joint.joint_type in (JointType.REVOLUTE, JointType.CONTINUOUS):
            angle = joint.position
            tf.position = Vector3(
                joint.axis.x * angle,
                joint.axis.y * angle,
                joint.axis.z * angle,
            )
        elif joint.joint_type == JointType.PRISMATIC:
            disp = joint.position
            tf.position = Vector3(
                joint.axis.x * disp,
                joint.axis.y * disp,
                joint.axis.z * disp,
            )
        return tf

    def inverse_kinematics(self, target: Transform, link_name: str,
                           max_iterations: int = 100,
                           tolerance: float = 0.01) -> Optional[Dict[str, float]]:
        from copy import deepcopy
        positions = self.get_joint_positions()
        for _ in range(max_iterations):
            fk = self.forward_kinematics(positions)
            if link_name not in fk:
                return None
            current = fk[link_name]
            error = target.position.distance_to(current.position)
            if error < tolerance:
                return positions
            for joint_name in self.joints:
                if joint_name in positions:
                    positions[joint_name] += 0.01 * (target.position.x - current.position.x)
        return positions

    def to_urdf(self) -> str:
        lines = [f'<?xml version="1.0"?>', f'<robot name="{self.name}">']
        for link in self.links.values():
            lines.append(f'  <link name="{link.name}">')
            lines.append(f'    <inertial>')
            lines.append(f'      <mass value="{link.mass}"/>')
            lines.append(f'    </inertial>')
            lines.append(f'  </link>')
        for joint in self.joints.values():
            lines.append(f'  <joint name="{joint.name}" type="{joint.joint_type.value}">')
            lines.append(f'    <parent link="{joint.parent_link}"/>')
            lines.append(f'    <child link="{joint.child_link}"/>')
            lines.append(f'  </joint>')
        lines.append('</robot>')
        return '\n'.join(lines)


@dataclass
class SensorReading:
    sensor_name: str = ""
    sensor_type: SensorType = SensorType.LIDAR
    timestamp: float = 0.0
    data: Dict[str, Any] = field(default_factory=dict)


class SensorModel:
    def __init__(self, name: str = "Sensor", sensor_type: SensorType = SensorType.LIDAR):
        self.name = name
        self.sensor_type = sensor_type
        self.position: Vector3 = Vector3()
        self.rotation: Quaternion = Quaternion.identity()
        self.update_rate: float = 10.0
        self.last_update: float = 0.0
        self.noise_std: float = 0.0
        self.enabled: bool = True

    def read(self, sim_time: float, **kwargs: Any) -> Optional[SensorReading]:
        if not self.enabled:
            return None
        if sim_time - self.last_update < 1.0 / self.update_rate:
            return None
        self.last_update = sim_time
        return self._generate_reading(sim_time, **kwargs)

    def _generate_reading(self, sim_time: float, **kwargs: Any) -> SensorReading:
        return SensorReading(
            sensor_name=self.name,
            sensor_type=self.sensor_type,
            timestamp=sim_time,
            data={},
        )

    def add_noise(self, value: float) -> float:
        if self.noise_std <= 0:
            return value
        import random
        return value + random.gauss(0, self.noise_std)


class LidarSensor(SensorModel):
    def __init__(self, name: str = "Lidar"):
        super().__init__(name, SensorType.LIDAR)
        self.num_beams: int = 64
        self.range_min: float = 0.5
        self.range_max: float = 100.0
        self.horizontal_fov: float = 360.0
        self.vertical_fov: float = 30.0
        self.resolution: float = 0.5

    def _generate_reading(self, sim_time: float, **kwargs: Any) -> SensorReading:
        obstacles = kwargs.get("obstacles", [])
        points = []
        h_angles = int(self.horizontal_fov / self.resolution)
        v_angles = int(self.vertical_fov / self.resolution)
        for hi in range(h_angles):
            h_angle = math.radians(-self.horizontal_fov / 2 + hi * self.resolution)
            for vi in range(v_angles):
                v_angle = math.radians(-self.vertical_fov / 2 + vi * self.resolution)
                dist = self.range_max
                for obs_pos, obs_rad in obstacles:
                    dx = obs_pos.x - self.position.x
                    dz = obs_pos.z - self.position.z
                    angle_to_obs = math.atan2(dz, dx)
                    if abs(angle_to_obs - h_angle) < 0.1:
                        d = math.sqrt(dx * dx + dz * dz)
                        if d < dist:
                            dist = d
                if dist < self.range_max:
                    points.append({
                        "x": dist * math.cos(h_angle) * math.cos(v_angle),
                        "y": dist * math.sin(v_angle),
                        "z": dist * math.sin(h_angle) * math.cos(v_angle),
                        "intensity": 1.0 - dist / self.range_max,
                    })
        return SensorReading(
            sensor_name=self.name,
            sensor_type=self.sensor_type,
            timestamp=sim_time,
            data={"points": points, "num_points": len(points)},
        )


class CameraSensor(SensorModel):
    def __init__(self, name: str = "Camera"):
        super().__init__(name, SensorType.CAMERA)
        self.width: int = 1920
        self.height: int = 1080
        self.fov: float = 70.0
        self.focal_length: float = 50.0

    def _generate_reading(self, sim_time: float, **kwargs: Any) -> SensorReading:
        return SensorReading(
            sensor_name=self.name,
            sensor_type=self.sensor_type,
            timestamp=sim_time,
            data={
                "width": self.width,
                "height": self.height,
                "fov": self.fov,
                "simulated": True,
                "objects_detected": kwargs.get("objects", []),
            },
        )


class IMUSensor(SensorModel):
    def __init__(self, name: str = "IMU"):
        super().__init__(name, SensorType.IMU)
        self.accelerometer_range: float = 19.6
        self.gyroscope_range: float = 4.0

    def _generate_reading(self, sim_time: float, **kwargs: Any) -> SensorReading:
        accel = kwargs.get("acceleration", Vector3())
        angular_vel = kwargs.get("angular_velocity", Vector3())
        return SensorReading(
            sensor_name=self.name,
            sensor_type=self.sensor_type,
            timestamp=sim_time,
            data={
                "acceleration": {"x": accel.x, "y": accel.y, "z": accel.z},
                "angular_velocity": {"x": angular_vel.x, "y": angular_vel.y, "z": angular_vel.z},
                "orientation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
            },
        )


class GPSSensor(SensorModel):
    def __init__(self, name: str = "GPS"):
        super().__init__(name, SensorType.GPS)
        self.latitude: float = 0.0
        self.longitude: float = 0.0
        self.altitude: float = 0.0
        self.horizontal_accuracy: float = 1.0

    def _generate_reading(self, sim_time: float, **kwargs: Any) -> SensorReading:
        position = kwargs.get("position", Vector3())
        return SensorReading(
            sensor_name=self.name,
            sensor_type=self.sensor_type,
            timestamp=sim_time,
            data={
                "latitude": self.latitude + position.x * 0.00001,
                "longitude": self.longitude + position.z * 0.00001,
                "altitude": self.altitude + position.y,
                "accuracy": self.horizontal_accuracy,
            },
        )


class RobotSystem:
    def __init__(self):
        self.robots: Dict[str, RobotModel] = {}
        self.sensors: Dict[str, SensorModel] = {}

    def add_robot(self, robot: RobotModel) -> None:
        self.robots[robot.name] = robot

    def add_sensor(self, sensor: SensorModel) -> None:
        self.sensors[sensor.name] = sensor

    def get_robot(self, name: str) -> Optional[RobotModel]:
        return self.robots.get(name)

    def get_sensor(self, name: str) -> Optional[SensorModel]:
        return self.sensors.get(name)

    def read_all_sensors(self, sim_time: float, **kwargs: Any) -> Dict[str, SensorReading]:
        readings = {}
        for name, sensor in self.sensors.items():
            reading = sensor.read(sim_time, **kwargs)
            if reading:
                readings[name] = reading
        return readings

    def summary(self) -> Dict[str, Any]:
        return {
            "robots": list(self.robots.keys()),
            "sensors": list(self.sensors.keys()),
            "robot_count": len(self.robots),
            "sensor_count": len(self.sensors),
        }


_robotics = RobotSystem()


def get_robotics() -> RobotSystem:
    return _robotics
