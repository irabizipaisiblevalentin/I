"""imodoka — Autonomous vehicle simulation: vehicle dynamics, traffic, sensors, ADAS."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ibikoreshingiro import Vector3, Vector2, Quaternion, Transform, clamp, lerp, smoothstep


class VehicleType(str, Enum):
    SEDAN = "sedan"
    SUV = "suv"
    TRUCK = "truck"
    BUS = "bus"
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"
    EMERGENCY = "emergency"


class DriveType(str, Enum):
    FRONT_WHEEL = "fwd"
    REAR_WHEEL = "rwd"
    ALL_WHEEL = "awd"


class TrafficLightState(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    LEFT_TURN = "left_turn"


class RoadType(str, Enum):
    HIGHWAY = "highway"
    URBAN = "urban"
    RESIDENTIAL = "residential"
    INTERSECTION = "intersection"
    ROUNDABOUT = "roundabout"
    PARKING = "parking"


class ScenarioCategory(str, Enum):
    HIGHWAY_DRIVING = "highway_driving"
    URBAN_DRIVING = "urban_driving"
    INTERSECTION = "intersection"
    PARKING = "parking"
    EMERGENCY = "emergency"
    ADVERSE_WEATHER = "adverse_weather"
    NIGHT_DRIVING = "night_driving"
    PEDESTRIAN = "pedestrian"


@dataclass
class VehicleDynamics:
    vehicle_type: VehicleType = VehicleType.SEDAN
    drive_type: DriveType = DriveType.FRONT_WHEEL
    mass: float = 1500.0
    engine_power: float = 150000.0
    brake_force: float = 10000.0
    drag_coefficient: float = 0.3
    frontal_area: float = 2.2
    wheel_radius: float = 0.33
    max_steering_angle: float = math.radians(40)
    wheelbase: float = 2.8
    track_width: float = 1.6

    position: Vector3 = field(default_factory=Vector3)
    rotation: float = 0.0
    velocity: float = 0.0
    steering_angle: float = 0.0
    acceleration: float = 0.0
    angular_velocity: float = 0.0
    throttle: float = 0.0
    brake: float = 0.0
    heading: float = 0.0

    @property
    def speed_kmh(self) -> float:
        return abs(self.velocity) * 3.6

    @property
    def speed_mph(self) -> float:
        return abs(self.velocity) * 2.237

    def update(self, dt: float, throttle_input: float = 0.0,
               brake_input: float = 0.0, steering_input: float = 0.0) -> None:
        self.throttle = clamp(throttle_input, -1.0, 1.0)
        self.brake = clamp(brake_input, 0.0, 1.0)
        self.steering_angle = clamp(steering_input, -1.0, 1.0) * self.max_steering_angle
        accel_force = self.throttle * self.engine_power / max(self.velocity, 1.0) if abs(self.velocity) > 0.1 else self.throttle * self.engine_power / 10.0
        brake_force = self.brake * self.brake_force
        drag_force = self.drag_coefficient * self.frontal_area * 1.225 * self.velocity * abs(self.velocity) * 0.5
        net_force = accel_force - brake_force - drag_force
        self.acceleration = net_force / self.mass
        self.velocity += self.acceleration * dt
        if abs(self.velocity) < 0.01:
            self.velocity = 0.0
        slip_angle = math.atan2(self.steering_angle, 1.0) if abs(self.velocity) > 0.1 else 0.0
        self.heading += self.velocity * math.tan(slip_angle) / self.wheelbase * dt
        self.position.x += self.velocity * math.cos(self.heading) * dt
        self.position.z += self.velocity * math.sin(self.heading) * dt

    def get_forward(self) -> Vector3:
        return Vector3(math.cos(self.heading), 0, math.sin(self.heading))

    def get_right(self) -> Vector3:
        return Vector3(math.cos(self.heading + math.pi / 2), 0, math.sin(self.heading + math.pi / 2))

    def distance_to(self, other: Vector3) -> float:
        return self.position.distance_to(other)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": {"x": self.position.x, "y": self.position.y, "z": self.position.z},
            "heading": math.degrees(self.heading),
            "speed_kmh": self.speed_kmh,
            "velocity": self.velocity,
            "throttle": self.throttle,
            "brake": self.brake,
            "steering": self.steering_angle,
        }


@dataclass
class TrafficLight:
    position: Vector3 = field(default_factory=Vector3)
    state: TrafficLightState = TrafficLightState.RED
    timer: float = 0.0
    green_duration: float = 30.0
    yellow_duration: float = 5.0
    red_duration: float = 30.0
    left_turn_duration: float = 10.0

    def update(self, dt: float) -> None:
        self.timer += dt
        duration = self._current_duration()
        if self.timer >= duration:
            self.timer = 0.0
            self._advance_state()

    def _current_duration(self) -> float:
        return {
            TrafficLightState.GREEN: self.green_duration,
            TrafficLightState.YELLOW: self.yellow_duration,
            TrafficLightState.RED: self.red_duration,
            TrafficLightState.LEFT_TURN: self.left_turn_duration,
        }.get(self.state, 30.0)

    def _advance_state(self) -> None:
        order = [TrafficLightState.GREEN, TrafficLightState.YELLOW,
                 TrafficLightState.RED, TrafficLightState.LEFT_TURN]
        idx = order.index(self.state) if self.state in order else 0
        self.state = order[(idx + 1) % len(order)]

    def to_dict(self) -> Dict[str, Any]:
        return {"state": self.state.value, "timer": self.timer}


@dataclass
class TrafficParticipant:
    vehicle_type: VehicleType = VehicleType.SEDAN
    dynamics: VehicleDynamics = field(default_factory=VehicleDynamics)
    path: List[Vector3] = field(default_factory=list)
    path_index: int = 0
    desired_speed: float = 10.0
    min_gap: float = 2.0
    reaction_time: float = 1.0
    comfort_accel: float = 2.0
    comfort_brake: float = 3.0

    def update(self, dt: float, leader: Optional[TrafficParticipant] = None) -> None:
        throttle = 0.0
        brake = 0.0
        steering = 0.0
        if self.path and self.path_index < len(self.path):
            target = self.path[self.path_index]
            dx = target.x - self.dynamics.position.x
            dz = target.z - self.dynamics.position.z
            dist = math.sqrt(dx * dx + dz * dz)
            target_angle = math.atan2(dz, dx)
            angle_diff = target_angle - self.dynamics.heading
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi
            steering = clamp(angle_diff * 2.0, -1.0, 1.0)
            speed_error = self.desired_speed - self.dynamics.velocity
            if leader:
                leader_dist = dist
                if leader_dist < self.min_gap + self.dynamics.velocity * self.reaction_time:
                    speed_error = -self.dynamics.velocity * 0.5
            if speed_error > 0:
                throttle = clamp(speed_error / 5.0, 0.0, 1.0)
            else:
                brake = clamp(-speed_error / 5.0, 0.0, 1.0)
            if dist < 1.0:
                self.path_index = (self.path_index + 1) % len(self.path)
        self.dynamics.update(dt, throttle, brake, steering)

    def distance_to(self, other: TrafficParticipant) -> float:
        return self.dynamics.position.distance_to(other.dynamics.position)


@dataclass
class TrafficScenario:
    name: str = ""
    category: ScenarioCategory = ScenarioCategory.URBAN_DRIVING
    participants: List[TrafficParticipant] = field(default_factory=list)
    traffic_lights: List[TrafficLight] = field(default_factory=list)
    road_type: RoadType = RoadType.URBAN
    time_of_day: float = 12.0
    weather: str = "clear"
    duration: float = 60.0
    max_participants: int = 50

    def add_participant(self, participant: TrafficParticipant) -> None:
        if len(self.participants) < self.max_participants:
            self.participants.append(participant)

    def add_traffic_light(self, light: TrafficLight) -> None:
        self.traffic_lights.append(light)

    def update(self, dt: float) -> None:
        for light in self.traffic_lights:
            light.update(dt)
        for i, participant in enumerate(self.participants):
            leader = self.participants[i - 1] if i > 0 else None
            participant.update(dt, leader)

    def check_collisions(self) -> List[Tuple[int, int, float]]:
        collisions = []
        for i, p1 in enumerate(self.participants):
            for j, p2 in enumerate(self.participants):
                if i >= j:
                    continue
                dist = p1.distance_to(p2)
                if dist < 2.0:
                    collisions.append((i, j, dist))
        return collisions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category.value,
            "participants": len(self.participants),
            "traffic_lights": len(self.traffic_lights),
            "road_type": self.road_type.value,
            "time_of_day": self.time_of_day,
            "weather": self.weather,
            "duration": self.duration,
        }


@dataclass
class ADASSystem:
    adaptive_cruise_control: bool = False
    lane_keep_assist: bool = False
    automatic_emergency_braking: bool = False
    blind_spot_monitoring: bool = False
    parking_assist: bool = False
    traffic_sign_recognition: bool = False
    target_speed: float = 30.0
    follow_distance: float = 2.5
    lane_center_offset: float = 0.0

    def update_adaptive_cruise(self, ego_speed: float, leader_speed: float,
                               distance: float, dt: float) -> float:
        if not self.adaptive_cruise_control:
            return 0.0
        speed_error = self.target_speed - ego_speed
        if leader_speed < ego_speed and distance < self.follow_distance * ego_speed:
            speed_error = leader_speed - ego_speed
        return clamp(speed_error / 3.0, -1.0, 1.0)

    def update_lane_keep(self, lateral_offset: float, heading_error: float) -> float:
        if not self.lane_keep_assist:
            return 0.0
        return clamp(-lateral_offset * 0.5 - heading_error * 2.0, -1.0, 1.0)

    def should_emergency_brake(self, distance: float, ego_speed: float) -> bool:
        if not self.automatic_emergency_braking:
            return False
        stopping_distance = ego_speed * 1.5
        return distance < stopping_distance and distance < 20.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "acc": self.adaptive_cruise_control,
            "lka": self.lane_keep_assist,
            "aeb": self.automatic_emergency_braking,
            "bsm": self.blind_spot_monitoring,
            "target_speed": self.target_speed,
        }


class AutonomousVehicleSystem:
    def __init__(self):
        self.scenarios: Dict[str, TrafficScenario] = {}
        self.active_scenario: Optional[TrafficScenario] = None
        self.adas = ADASSystem()
        self._ego_vehicle: Optional[VehicleDynamics] = None

    def create_scenario(self, name: str,
                        category: ScenarioCategory = ScenarioCategory.URBAN_DRIVING) -> TrafficScenario:
        scenario = TrafficScenario(name=name, category=category)
        self.scenarios[name] = scenario
        return scenario

    def load_scenario(self, name: str) -> bool:
        if name in self.scenarios:
            self.active_scenario = self.scenarios[name]
            return True
        return False

    def set_ego_vehicle(self, vehicle: VehicleDynamics) -> None:
        self._ego_vehicle = vehicle

    def update(self, dt: float) -> None:
        if self.active_scenario:
            self.active_scenario.update(dt)
            if self._ego_vehicle and self.active_scenario.participants:
                leader = self.active_scenario.participants[0]
                dist = self._ego_vehicle.distance_to(leader.dynamics.position)
                throttle = self.adas.update_adaptive_cruise(
                    self._ego_vehicle.velocity, leader.dynamics.velocity, dist, dt)
                steering = self.adas.update_lane_keep(0.0, 0.0)
                brake = 1.0 if self.adas.should_emergency_brake(dist, self._ego_vehicle.velocity) else 0.0
                self._ego_vehicle.update(dt, throttle if not brake else 0.0, brake, steering)

    def summary(self) -> Dict[str, Any]:
        return {
            "scenarios": list(self.scenarios.keys()),
            "active": self.active_scenario.name if self.active_scenario else None,
            "adas": self.adas.to_dict(),
            "participants": len(self.active_scenario.participants) if self.active_scenario else 0,
        }


_av_system = AutonomousVehicleSystem()


def get_av_system() -> AutonomousVehicleSystem:
    return _av_system
