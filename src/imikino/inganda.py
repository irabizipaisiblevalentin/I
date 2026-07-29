"""inganda — Digital twin / industrial simulation: factories, production lines, supply chain."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ibikoreshingiro import Vector3, clamp, lerp, smoothstep


class MachineStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    MAINTENANCE = "maintenance"
    FAULT = "fault"
    OFFLINE = "offline"


class ProductState(str, Enum):
    RAW = "raw"
    IN_PROGRESS = "in_progress"
    QUALITY_CHECK = "quality_check"
    COMPLETED = "completed"
    REJECTED = "rejected"
    PACKAGED = "packaged"
    SHIPPED = "shipped"


class SupplyChainStage(str, Enum):
    PROCUREMENT = "procurement"
    MANUFACTURING = "manufacturing"
    WAREHOUSING = "warehousing"
    DISTRIBUTION = "distribution"
    RETAIL = "retail"
    CONSUMER = "consumer"


@dataclass
class Product:
    product_id: str = ""
    name: str = ""
    product_type: str = ""
    state: ProductState = ProductState.RAW
    position: int = 0
    quality_score: float = 1.0
    process_time: float = 0.0
    defects: List[str] = field(default_factory=list)
    batch_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "state": self.state.value,
            "quality": round(self.quality_score, 2),
            "defects": len(self.defects),
        }


@dataclass
class Machine:
    name: str = ""
    machine_type: str = ""
    status: MachineStatus = MachineStatus.IDLE
    position: Vector3 = field(default_factory=Vector3)
    cycle_time: float = 5.0
    setup_time: float = 10.0
    power_consumption: float = 10.0
    temperature: float = 25.0
    vibration: float = 0.0
    failure_rate: float = 0.001
    maintenance_interval: float = 3600.0
    last_maintenance: float = 0.0
    total_products: int = 0
    defect_count: int = 0
    current_product: Optional[Product] = None
    process_progress: float = 0.0
    uptime: float = 0.0
    downtime: float = 0.0
    parameters: Dict[str, float] = field(default_factory=dict)

    @property
    def overall_equipment_effectiveness(self) -> float:
        availability = self.uptime / max(self.uptime + self.downtime, 1.0)
        performance = self.total_products * self.cycle_time / max(self.uptime, 1.0)
        quality = (self.total_products - self.defect_count) / max(self.total_products, 1)
        return availability * min(performance, 1.0) * quality

    @property
    def efficiency(self) -> float:
        return self.overall_equipment_effectiveness

    def update(self, dt: float) -> Optional[Product]:
        if self.status == MachineStatus.RUNNING and self.current_product:
            self.process_progress += dt / self.cycle_time
            self.temperature += dt * 0.5
            self.vibration = 0.1 + random.random() * 0.2
            self.uptime += dt
            if self.process_progress >= 1.0:
                return self._complete_product()
        if self.status == MachineStatus.FAULT:
            self.downtime += dt
        if self.status == MachineStatus.RUNNING:
            if random.random() < self.failure_rate * dt:
                self.status = MachineStatus.FAULT
                self.current_product = None
        return None

    def _complete_product(self) -> Product:
        product = self.current_product
        self.total_products += 1
        self.process_progress = 0.0
        product.state = ProductState.COMPLETED
        product.quality_score = max(0.0, 1.0 - self.defect_count / max(self.total_products, 1) * 0.1)
        if random.random() < 0.05:
            product.quality_score *= 0.5
            self.defect_count += 1
            product.state = ProductState.REJECTED
            product.defects.append("quality_fail")
        self.current_product = Product(
            product_id=f"prod_{self.total_products}",
            name=f"{self.name}_product_{self.total_products}",
        )
        product.position = self.total_products
        return product

    def start_product(self, product: Product) -> None:
        self.current_product = product
        product.state = ProductState.IN_PROGRESS
        self.process_progress = 0.0
        if self.status == MachineStatus.IDLE:
            self.status = MachineStatus.RUNNING

    def pause(self) -> None:
        if self.status == MachineStatus.RUNNING:
            self.status = MachineStatus.PAUSED

    def resume(self) -> None:
        if self.status == MachineStatus.PAUSED:
            self.status = MachineStatus.RUNNING

    def maintain(self) -> None:
        self.status = MachineStatus.MAINTENANCE
        self.last_maintenance = 0.0
        self.temperature = 25.0
        self.vibration = 0.0

    def repair(self) -> None:
        self.status = MachineStatus.IDLE
        self.temperature = 25.0
        self.vibration = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.machine_type,
            "status": self.status.value,
            "oee": round(self.overall_equipment_effectiveness, 3),
            "total_products": self.total_products,
            "defects": self.defect_count,
            "uptime": round(self.uptime, 1),
            "downtime": round(self.downtime, 1),
            "temp": round(self.temperature, 1),
        }


@dataclass
class ConveyorBelt:
    name: str = ""
    length: float = 10.0
    speed: float = 1.0
    products: List[Product] = field(default_factory=list)
    capacity: int = 50
    entry_point: Optional[Callable[[], Optional[Product]]] = None
    exit_point: Optional[Callable[[Product], None]] = None

    def update(self, dt: float) -> None:
        for product in self.products:
            product.position += self.speed * dt
        self.products = [p for p in self.products if p.position < self.length]
        for product in self.products:
            if product.position >= self.length and self.exit_point:
                self.exit_point(product)
                self.products.remove(product)
        if self.entry_point and len(self.products) < self.capacity:
            new_product = self.entry_point()
            if new_product:
                new_product.position = 0.0
                self.products.append(new_product)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "products": len(self.products),
            "speed": self.speed,
            "capacity": self.capacity,
        }


@dataclass
class ProductionLine:
    name: str = ""
    machines: List[Machine] = field(default_factory=list)
    conveyors: List[ConveyorBelt] = field(default_factory=list)
    target_output: int = 100
    current_output: int = 0
    cycle_count: int = 0
    enabled: bool = True

    def add_machine(self, machine: Machine) -> None:
        self.machines.append(machine)

    def add_conveyor(self, conveyor: ConveyorBelt) -> None:
        self.conveyors.append(conveyor)

    def update(self, dt: float) -> None:
        if not self.enabled:
            return
        for machine in self.machines:
            completed = machine.update(dt)
            if completed:
                self.current_output += 1
                self.cycle_count += 1
        for conveyor in self.conveyors:
            conveyor.update(dt)

    def start(self) -> None:
        self.enabled = True
        for i, machine in enumerate(self.machines):
            if i < len(self.machines) and machine.status == MachineStatus.IDLE:
                product = Product(
                    product_id=f"prod_{self.cycle_count}_{i}",
                    name=f"product_{i}",
                    batch_id=f"batch_{self.cycle_count}",
                )
                machine.start_product(product)

    def stop(self) -> None:
        self.enabled = False
        for machine in self.machines:
            machine.status = MachineStatus.IDLE

    @property
    def throughput(self) -> float:
        total_time = sum(m.uptime + m.downtime for m in self.machines)
        return self.current_output / max(total_time, 1.0)

    @property
    def oee(self) -> float:
        if not self.machines:
            return 0.0
        return sum(m.overall_equipment_effectiveness for m in self.machines) / len(self.machines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "machines": len(self.machines),
            "output": self.current_output,
            "throughput": round(self.throughput, 3),
            "oee": round(self.oee, 3),
            "target": self.target_output,
            "enabled": self.enabled,
        }


@dataclass
class SupplyChainNode:
    name: str = ""
    stage: SupplyChainStage = SupplyChainStage.PROCUREMENT
    inventory: List[Product] = field(default_factory=list)
    capacity: int = 1000
    lead_time: float = 24.0
    operating_cost: float = 100.0
    location: str = ""

    @property
    def inventory_level(self) -> int:
        return len(self.inventory)

    @property
    def utilization(self) -> float:
        return len(self.inventory) / max(self.capacity, 1)

    def receive(self, product: Product) -> None:
        if len(self.inventory) < self.capacity:
            self.inventory.append(product)

    def ship(self, count: int = 1) -> List[Product]:
        shipped = self.inventory[:count]
        self.inventory = self.inventory[count:]
        return shipped

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "stage": self.stage.value,
            "inventory": self.inventory_level,
            "capacity": self.capacity,
            "utilization": round(self.utilization, 2),
        }


@dataclass
class EquipmentSensor:
    name: str = ""
    machine_name: str = ""
    measurement: str = ""
    value: float = 0.0
    unit: str = ""
    normal_min: float = 0.0
    normal_max: float = 100.0
    alarm_threshold: float = 0.0

    @property
    def is_alerting(self) -> bool:
        return self.value < self.normal_min or self.value > self.normal_max

    def read(self, machine: Machine) -> None:
        if self.measurement == "temperature":
            self.value = machine.temperature
        elif self.measurement == "vibration":
            self.value = machine.vibration
        elif self.measurement == "power":
            self.value = machine.power_consumption
        elif self.measurement == "oee":
            self.value = machine.overall_equipment_effectiveness * 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "machine": self.machine_name,
            "value": round(self.value, 2),
            "unit": self.unit,
            "alerting": self.is_alerting,
        }


class FactorySimulation:
    def __init__(self, name: str = "Factory"):
        self.name = name
        self.production_lines: Dict[str, ProductionLine] = {}
        self.supply_chain: Dict[str, SupplyChainNode] = {}
        self.equipment_sensors: List[EquipmentSensor] = []
        self.total_output: int = 0
        self.total_defects: int = 0
        self._time: float = 0.0
        self._budget: float = 500000.0

    def add_production_line(self, line: ProductionLine) -> None:
        self.production_lines[line.name] = line

    def add_supply_chain_node(self, node: SupplyChainNode) -> None:
        self.supply_chain[node.name] = node

    def add_sensor(self, sensor: EquipmentSensor) -> None:
        self.equipment_sensors.append(sensor)

    def update(self, dt: float) -> None:
        self._time += dt
        for line in self.production_lines.values():
            line.update(dt)
            self.total_output += line.current_output
        for sensor in self.equipment_sensors:
            for line in self.production_lines.values():
                for machine in line.machines:
                    if sensor.machine_name == machine.name:
                        sensor.read(machine)

    def start_production(self, line_name: str) -> bool:
        if line_name in self.production_lines:
            self.production_lines[line_name].start()
            return True
        return False

    def stop_production(self, line_name: str) -> bool:
        if line_name in self.production_lines:
            self.production_lines[line_name].stop()
            return True
        return False

    def get_alerts(self) -> List[EquipmentSensor]:
        return [s for s in self.equipment_sensors if s.is_alerting]

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "production_lines": list(self.production_lines.keys()),
            "total_output": self.total_output,
            "total_defects": self.total_defects,
            "time_simulated": round(self._time, 1),
            "budget": self._budget,
            "alerts": len(self.get_alerts()),
            "lines": [l.to_dict() for l in self.production_lines.values()],
            "supply_chain": [n.to_dict() for n in self.supply_chain.values()],
        }


_factory_sim = FactorySimulation()


def get_factory_sim() -> FactorySimulation:
    return _factory_sim
