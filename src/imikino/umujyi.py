"""umujyi — Smart city simulation: traffic, population, infrastructure, environment."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ibikoreshingiro import Vector3, Vector2, Color, clamp, lerp, smoothstep


class ZoneType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    PARK = "park"
    SCHOOL = "school"
    HOSPITAL = "hospital"
    WATER = "water"
    GOVERNMENT = "government"
    MIXED_USE = "mixed_use"


class WeatherType(str, Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    SNOW = "snow"
    FOG = "fog"
    WINDY = "windy"


class InfrastructureType(str, Enum):
    POWER = "power"
    WATER = "water"
    TELECOM = "telecom"
    GAS = "gas"
    SEWAGE = "sewage"
    TRANSPORT = "transport"
    INTERNET = "internet"


class BuildingType(str, Enum):
    HOUSE = "house"
    APARTMENT = "apartment"
    OFFICE = "office"
    SHOP = "shop"
    SCHOOL = "school"
    HOSPITAL = "hospital"
    FACTORY = "factory"
    WAREHOUSE = "warehouse"
    GOVERNMENT = "government"
    PARKING = "parking"
    STADIUM = "stadium"


@dataclass
class Zone:
    name: str = ""
    zone_type: ZoneType = ZoneType.RESIDENTIAL
    bounds_min: Vector3 = field(default_factory=Vector3)
    bounds_max: Vector3 = field(default_factory=Vector3)
    population: int = 0
    capacity: int = 1000
    buildings: List["Building"] = field(default_factory=list)
    demand_energy: float = 0.0
    demand_water: float = 0.0
    satisfaction: float = 0.8

    @property
    def area(self) -> float:
        dx = self.bounds_max.x - self.bounds_min.x
        dz = self.bounds_max.z - self.bounds_min.z
        return dx * dz

    @property
    def density(self) -> float:
        return self.population / max(self.area, 1.0)

    def is_inside(self, position: Vector3) -> bool:
        return (self.bounds_min.x <= position.x <= self.bounds_max.x and
                self.bounds_min.z <= position.z <= self.bounds_max.z)

    def update(self, dt: float) -> None:
        load = self.population / max(self.capacity, 1)
        self.satisfaction = clamp(1.0 - load * 0.3, 0.0, 1.0)
        self.demand_energy = self.population * 0.5 + len(self.buildings) * 2.0
        self.demand_water = self.population * 0.1 + len(self.buildings) * 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.zone_type.value,
            "population": self.population,
            "capacity": self.capacity,
            "density": round(self.density, 2),
            "satisfaction": round(self.satisfaction, 2),
            "buildings": len(self.buildings),
        }


@dataclass
class Building:
    name: str = ""
    building_type: BuildingType = BuildingType.HOUSE
    position: Vector3 = field(default_factory=Vector3)
    size: Vector3 = field(default_factory=lambda: Vector3(10, 5, 10))
    floors: int = 1
    occupants: int = 0
    energy_consumption: float = 0.0
    water_consumption: float = 0.0
    condition: float = 1.0

    def update(self, dt: float) -> None:
        self.energy_consumption = self.occupants * 0.3 + self.floors * 0.5
        self.water_consumption = self.occupants * 0.05

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.building_type.value,
            "occupants": self.occupants,
            "floors": self.floors,
            "condition": round(self.condition, 2),
        }


@dataclass
class Infrastructure:
    infra_type: InfrastructureType = InfrastructureType.POWER
    capacity: float = 1000.0
    load: float = 0.0
    efficiency: float = 0.9
    uptime: float = 1.0
    maintenance_cost: float = 100.0
    connections: List[str] = field(default_factory=list)

    @property
    def available_capacity(self) -> float:
        return self.capacity - self.load

    @property
    def utilization(self) -> float:
        return self.load / max(self.capacity, 1.0)

    def update(self, dt: float, demand: float) -> None:
        self.load = min(demand, self.capacity)
        if self.load > self.capacity * 0.9:
            self.efficiency = max(0.5, self.efficiency - dt * 0.01)
        else:
            self.efficiency = min(0.95, self.efficiency + dt * 0.005)
        self.uptime = max(0.0, self.uptime - dt * (1 - self.efficiency) * 0.001)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.infra_type.value,
            "capacity": self.capacity,
            "load": self.load,
            "utilization": round(self.utilization, 2),
            "efficiency": round(self.efficiency, 2),
            "uptime": round(self.uptime, 2),
        }


@dataclass
class Environment:
    time_of_day: float = 6.0
    day_length: float = 24.0
    weather: WeatherType = WeatherType.CLEAR
    temperature: float = 25.0
    humidity: float = 60.0
    wind_speed: float = 5.0
    rain_intensity: float = 0.0
    fog_density: float = 0.0
    pollution_level: float = 0.0
    day_cycle_speed: float = 1.0

    @property
    def sunlight_intensity(self) -> float:
        hour = self.time_of_day % 24
        if 6 <= hour <= 18:
            return math.sin((hour - 6) / 12 * math.pi)
        return 0.0

    @property
    def is_daytime(self) -> bool:
        return 6 <= (self.time_of_day % 24) <= 18

    @property
    def is_night(self) -> bool:
        return not self.is_daytime

    def update(self, dt: float) -> None:
        self.time_of_day += dt * self.day_cycle_speed / 60.0
        if self.time_of_day > 24:
            self.time_of_day -= 24
        if self.weather == WeatherType.RAIN:
            self.rain_intensity = min(1.0, self.rain_intensity + dt * 0.1)
        elif self.weather == WeatherType.STORM:
            self.rain_intensity = min(1.0, self.rain_intensity + dt * 0.2)
        else:
            self.rain_intensity = max(0.0, self.rain_intensity - dt * 0.05)
        self.temperature += (25.0 - self.temperature) * dt * 0.005 + (self.sunlight_intensity * 5 - 2.5) * dt * 0.01

    def set_weather(self, weather: WeatherType) -> None:
        self.weather = weather

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": f"{int(self.time_of_day):02d}:{int((self.time_of_day % 1) * 60):02d}",
            "weather": self.weather.value,
            "temperature": round(self.temperature, 1),
            "humidity": self.humidity,
            "sunlight": round(self.sunlight_intensity, 2),
            "pollution": round(self.pollution_level, 2),
        }


@dataclass
class Pedestrian:
    position: Vector3 = field(default_factory=Vector3)
    velocity: Vector3 = field(default_factory=Vector3)
    speed: float = 1.4
    destination: Optional[Vector3] = None
    path: List[Vector3] = field(default_factory=list)
    path_index: int = 0
    patience: float = 10.0
    waiting_time: float = 0.0

    def update(self, dt: float, obstacles: Optional[List[Vector3]] = None) -> None:
        if self.destination:
            dx = self.destination.x - self.position.x
            dz = self.destination.z - self.position.z
            dist = math.sqrt(dx * dx + dz * dz)
            if dist < 0.5:
                self.destination = None
                self.velocity = Vector3()
                return
            self.velocity = Vector3(dx / dist * self.speed, 0, dz / dist * self.speed)
        self.position.x += self.velocity.x * dt
        self.position.z += self.velocity.z * dt

    def set_destination(self, dest: Vector3) -> None:
        self.destination = dest

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": {"x": self.position.x, "y": self.position.y, "z": self.position.z},
            "speed": self.speed,
            "has_destination": self.destination is not None,
        }


class CitySimulation:
    def __init__(self, name: str = "City"):
        self.name = name
        self.zones: Dict[str, Zone] = {}
        self.buildings: List[Building] = []
        self.infrastructure: Dict[InfrastructureType, Infrastructure] = {}
        self.pedestrians: List[Pedestrian] = []
        self.environment = Environment()
        self.total_population: int = 0
        self._time: float = 0.0
        self._budget: float = 1000000.0

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone

    def add_building(self, building: Building, zone_name: Optional[str] = None) -> None:
        self.buildings.append(building)
        if zone_name and zone_name in self.zones:
            self.zones[zone_name].buildings.append(building)

    def add_infrastructure(self, infra: Infrastructure) -> None:
        self.infrastructure[infra.infra_type] = infra

    def add_pedestrian(self, pedestrian: Pedestrian) -> None:
        self.pedestrians.append(pedestrian)

    def update(self, dt: float) -> None:
        self._time += dt
        self.environment.update(dt)
        total_energy_demand = 0.0
        total_water_demand = 0.0
        for zone in self.zones.values():
            zone.update(dt)
            total_energy_demand += zone.demand_energy
            total_water_demand += zone.demand_water
        for building in self.buildings:
            building.update(dt)
        for infra_type, infra in self.infrastructure.items():
            demand = total_energy_demand if infra_type == InfrastructureType.POWER else total_water_demand
            infra.update(dt, demand)
        for ped in self.pedestrians:
            ped.update(dt)
        self.total_population = sum(z.population for z in self.zones.values())

    def get_stats(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "population": self.total_population,
            "zones": len(self.zones),
            "buildings": len(self.buildings),
            "pedestrians": len(self.pedestrians),
            "environment": self.environment.to_dict(),
            "budget": self._budget,
            "time_simulated": self._time,
        }

    def summary(self) -> Dict[str, Any]:
        return {
            "city": self.get_stats(),
            "zones": [z.to_dict() for z in self.zones.values()],
            "infrastructure": [i.to_dict() for i in self.infrastructure.values()],
            "env": self.environment.to_dict(),
        }


_city_sim = CitySimulation()


def get_city_sim() -> CitySimulation:
    return _city_sim
