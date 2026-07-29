"""ibikoresho_byinjijwe — Device drivers: USB, PCIe, storage, graphics, audio, network, sensors, displays, touch, industrial."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

from .ibyinjijwe import GPIOPin, SPIBus, I2CBus, UART, PWMPin


class DeviceClass(Enum):
    USB = "usb"
    PCIE = "pcie"
    STORAGE = "storage"
    GRAPHICS = "graphics"
    AUDIO = "audio"
    NETWORK = "network"
    SENSOR = "sensor"
    DISPLAY = "display"
    TOUCH = "touch"
    INPUT = "input"
    INDUSTRIAL = "industrial"
    TIMER = "timer"
    DMA = "dma"


class USBDeviceClass(Enum):
    AUDIO = 1
    COMMUNICATIONS = 2
    HID = 3
    PHYSICAL = 5
    IMAGE = 6
    PRINTER = 7
    MASS_STORAGE = 8
    HUB = 9
    VIDEO = 14
    WIRELESS = 224


class PCIeDeviceClass(Enum):
    MASS_STORAGE = 0x01
    NETWORK = 0x02
    DISPLAY = 0x03
    MULTIMEDIA = 0x04
    MEMORY = 0x05
    BRIDGE = 0x06
    SIMPLE_COMM = 0x07
    BASE_PERIPHERAL = 0x08
    INPUT = 0x09
    SERIAL = 0x0C


@dataclass
class USBDevice:
    vendor_id: int = 0
    product_id: int = 0
    device_class: USBDeviceClass = USBDeviceClass.HID
    manufacturer: str = ""
    product: str = ""
    serial: str = ""
    speed: str = "full"
    address: int = 0
    interfaces: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vendor": hex(self.vendor_id),
            "product": hex(self.product_id),
            "class": self.device_class.name,
            "manufacturer": self.manufacturer,
            "speed": self.speed,
            "interfaces": len(self.interfaces),
        }


@dataclass
class USBController:
    version: str = "3.0"
    ports: int = 4
    devices: Dict[int, USBDevice] = field(default_factory=dict)
    enabled: bool = False

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False

    def enumerate(self) -> List[USBDevice]:
        return list(self.devices.values())

    def attach(self, device: USBDevice) -> int:
        addr = len(self.devices) + 1
        device.address = addr
        self.devices[addr] = device
        return addr

    def detach(self, address: int) -> bool:
        if address in self.devices:
            del self.devices[address]
            return True
        return False

    def summary(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "ports": self.ports,
            "devices": len(self.devices),
            "enabled": self.enabled,
        }


@dataclass
class PCIeDevice:
    vendor_id: int = 0
    device_id: int = 0
    device_class: PCIeDeviceClass = PCIeDeviceClass.NETWORK
    revision: int = 0
    bus: int = 0
    slot: int = 0
    function: int = 0
    memory_bars: List[int] = field(default_factory=list)
    irq: int = 0
    enabled: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vendor": hex(self.vendor_id),
            "device": hex(self.device_id),
            "class": self.device_class.name,
            "bus": f"{self.bus:02x}:{self.slot:02x}.{self.function}",
            "irq": self.irq,
        }


@dataclass
class PCIeController:
    buses: int = 1
    devices: Dict[str, PCIeDevice] = field(default_factory=dict)

    def scan(self) -> List[PCIeDevice]:
        return list(self.devices.values())

    def attach(self, device: PCIeDevice) -> None:
        key = f"{device.bus:02x}:{device.slot:02x}.{device.function}"
        self.devices[key] = device

    def summary(self) -> Dict[str, Any]:
        return {"buses": self.buses, "devices": len(self.devices)}


@dataclass
class StorageDevice:
    name: str = ""
    device_type: str = "sata"
    capacity_bytes: int = 0
    block_size: int = 512
    readonly: bool = False
    removable: bool = False
    _data: Dict[int, bytes] = field(default_factory=dict)

    def read_block(self, block: int) -> Optional[bytes]:
        return self._data.get(block, b'\x00' * self.block_size)

    def write_block(self, block: int, data: bytes) -> bool:
        if self.readonly:
            return False
        self._data[block] = data
        return True

    def read(self, offset: int, size: int) -> bytes:
        start_block = offset // self.block_size
        end_block = (offset + size - 1) // self.block_size
        result = bytearray()
        for b in range(start_block, end_block + 1):
            result.extend(self.read_block(b) or b'\x00' * self.block_size)
        return bytes(result[offset % self.block_size:offset % self.block_size + size])

    @property
    def total_size(self) -> int:
        return self.capacity_bytes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.device_type,
            "capacity": self.capacity_bytes,
            "block_size": self.block_size,
        }


@dataclass
class GraphicsDevice:
    name: str = ""
    width: int = 1920
    height: int = 1080
    bpp: int = 32
    refresh_rate: int = 60
    vram_size: int = 0
    _framebuffer: bytearray = field(default_factory=lambda: bytearray())

    def init(self) -> bool:
        self._framebuffer = bytearray(self.width * self.height * (self.bpp // 8))
        return True

    def clear(self, color: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> None:
        pixel = bytes(color)
        for i in range(0, len(self._framebuffer), 4):
            self._framebuffer[i:i + 4] = pixel

    def draw_pixel(self, x: int, y: int, color: Tuple[int, int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = (y * self.width + x) * 4
            self._framebuffer[offset:offset + 4] = bytes(color)

    def present(self) -> None:
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "resolution": f"{self.width}x{self.height}",
            "bpp": self.bpp,
        }


@dataclass
class SensorDevice:
    name: str = ""
    sensor_type: str = "temperature"
    unit: str = "celsius"
    range_min: float = -40.0
    range_max: float = 85.0
    precision: float = 0.1
    _value: float = 25.0

    def read(self) -> float:
        return self._value

    def set_value(self, value: float) -> None:
        self._value = max(self.range_min, min(self.range_max, value))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.sensor_type,
            "unit": self.unit,
            "value": self._value,
        }


@dataclass
class DisplayDevice:
    name: str = ""
    width: int = 320
    height: int = 240
    color_depth: int = 16
    backlight: int = 100
    spi_bus: Optional[SPIBus] = None
    _buffer: bytearray = field(default_factory=bytearray)

    def init(self) -> bool:
        self._buffer = bytearray(self.width * self.height * (self.color_depth // 8))
        return True

    def fill(self, color: int) -> None:
        pixel = bytes([color >> 8, color & 0xFF])
        for i in range(0, len(self._buffer), 2):
            self._buffer[i:i + 2] = pixel

    def draw_pixel(self, x: int, y: int, color: int) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = (y * self.width + x) * 2
            self._buffer[offset:offset + 2] = bytes([color >> 8, color & 0xFF])

    def refresh(self) -> None:
        pass

    def set_backlight(self, level: int) -> None:
        self.backlight = max(0, min(100, level))


@dataclass
class TouchDevice:
    name: str = ""
    touch_type: str = "capacitive"
    max_points: int = 10
    resolution_x: int = 320
    resolution_y: int = 240
    i2c_bus: Optional[I2CBus] = None
    _points: List[Dict[str, Any]] = field(default_factory=list)

    def read_touch(self) -> List[Dict[str, Any]]:
        return self._points

    def simulate_touch(self, x: int, y: int, pressure: float = 1.0) -> None:
        self._points.append({"x": x, "y": y, "pressure": pressure, "id": len(self._points)})

    def clear(self) -> None:
        self._points.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.touch_type,
            "resolution": f"{self.resolution_x}x{self.resolution_y}",
            "points": len(self._points),
        }


@dataclass
class IndustrialController:
    name: str = ""
    controller_type: str = "plc"
    protocols: List[str] = field(default_factory=lambda: ["modbus"])
    digital_inputs: int = 8
    digital_outputs: int = 8
    analog_inputs: int = 4
    analog_outputs: int = 2

    def read_digital(self, channel: int) -> bool:
        return False

    def write_digital(self, channel: int, value: bool) -> None:
        pass

    def read_analog(self, channel: int) -> float:
        return 0.0

    def write_analog(self, channel: int, value: float) -> None:
        pass

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.controller_type,
            "protocols": self.protocols,
            "di": self.digital_inputs,
            "do": self.digital_outputs,
            "ai": self.analog_inputs,
            "ao": self.analog_outputs,
        }


class DeviceManager:
    def __init__(self):
        self.usb_controllers: Dict[str, USBController] = {}
        self.pcie_controllers: Dict[str, PCIeController] = {}
        self.storage_devices: Dict[str, StorageDevice] = {}
        self.graphics_devices: Dict[str, GraphicsDevice] = {}
        self.sensor_devices: Dict[str, SensorDevice] = {}
        self.display_devices: Dict[str, DisplayDevice] = {}
        self.touch_devices: Dict[str, TouchDevice] = {}
        self.industrial_controllers: Dict[str, IndustrialController] = {}

    def create_usb_controller(self, name: str = "USB1") -> USBController:
        ctrl = USBController()
        self.usb_controllers[name] = ctrl
        return ctrl

    def create_pcie_controller(self, name: str = "PCIe1") -> PCIeController:
        ctrl = PCIeController()
        self.pcie_controllers[name] = ctrl
        return ctrl

    def create_storage(self, name: str, capacity: int = 1073741824,
                       block_size: int = 512) -> StorageDevice:
        dev = StorageDevice(name=name, capacity_bytes=capacity, block_size=block_size)
        self.storage_devices[name] = dev
        return dev

    def create_graphics(self, name: str = "GPU0", width: int = 1920,
                        height: int = 1080) -> GraphicsDevice:
        dev = GraphicsDevice(name=name, width=width, height=height)
        dev.init()
        self.graphics_devices[name] = dev
        return dev

    def create_sensor(self, name: str, sensor_type: str = "temperature",
                      unit: str = "celsius") -> SensorDevice:
        dev = SensorDevice(name=name, sensor_type=sensor_type, unit=unit)
        self.sensor_devices[name] = dev
        return dev

    def create_display(self, name: str, width: int = 320,
                       height: int = 240) -> DisplayDevice:
        dev = DisplayDevice(name=name, width=width, height=height)
        dev.init()
        self.display_devices[name] = dev
        return dev

    def create_touch(self, name: str = "Touch1") -> TouchDevice:
        dev = TouchDevice(name=name)
        self.touch_devices[name] = dev
        return dev

    def create_industrial(self, name: str = "PLC1") -> IndustrialController:
        ctrl = IndustrialController(name=name)
        self.industrial_controllers[name] = ctrl
        return ctrl

    def summary(self) -> Dict[str, Any]:
        return {
            "usb": len(self.usb_controllers),
            "pcie": len(self.pcie_controllers),
            "storage": len(self.storage_devices),
            "graphics": len(self.graphics_devices),
            "sensors": len(self.sensor_devices),
            "displays": len(self.display_devices),
            "touch": len(self.touch_devices),
            "industrial": len(self.industrial_controllers),
        }


_device_manager = DeviceManager()


def get_device_manager() -> DeviceManager:
    return _device_manager
