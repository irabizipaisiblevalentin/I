"""ibyinjijwe — Embedded systems: MCU support, ARM/RISC-V, GPIO, SPI, I2C, UART, PWM, ADC, timers, RTOS."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple


class Architecture(Enum):
    ARM_CORTEX_M0 = "arm_cortex_m0"
    ARM_CORTEX_M3 = "arm_cortex_m3"
    ARM_CORTEX_M4 = "arm_cortex_m4"
    ARM_CORTEX_M7 = "arm_cortex_m7"
    ARM_CORTEX_A = "arm_cortex_a"
    RISC_V_32 = "riscv32"
    RISC_V_64 = "riscv64"
    ESP32 = "esp32"
    ESP8266 = "esp8266"
    STM32 = "stm32"
    AVR = "avr"
    PIC = "pic"


class MCUFamily(Enum):
    STM32F0 = "stm32f0"
    STM32F1 = "stm32f1"
    STM32F4 = "stm32f4"
    STM32H7 = "stm32h7"
    ESP32 = "esp32"
    RP2040 = "rp2040"
    ATMEGA = "atmega"
    ATTINY = "attiny"
    TEENSY = "teensy"


class PinMode(Enum):
    INPUT = "input"
    OUTPUT = "output"
    INPUT_PULLUP = "input_pullup"
    INPUT_PULLDOWN = "input_pulldown"
    OUTPUT_OPEN_DRAIN = "output_open_drain"
    ALTERNATE = "alternate"
    ANALOG = "analog"


class InterruptTrigger(Enum):
    RISING = "rising"
    FALLING = "falling"
    CHANGE = "change"
    LOW = "low"
    HIGH = "high"


@dataclass
class GPIOPin:
    port: str = "A"
    pin: int = 0
    mode: PinMode = PinMode.INPUT
    value: bool = False
    pull: bool = False
    alternate_fn: int = 0

    def set_mode(self, mode: PinMode) -> None:
        self.mode = mode

    def write(self, value: bool) -> None:
        self.value = value

    def read(self) -> bool:
        return self.value

    def toggle(self) -> None:
        self.value = not self.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "port": self.port,
            "pin": self.pin,
            "mode": self.mode.value,
            "value": self.value,
        }


class GPIOController:
    def __init__(self):
        self.pins: Dict[str, GPIOPin] = {}
        self._interrupts: Dict[str, List[Callable]] = {}

    def add_pin(self, port: str, pin: int,
                mode: PinMode = PinMode.INPUT) -> GPIOPin:
        key = f"{port}{pin}"
        gpio = GPIOPin(port=port, pin=pin, mode=mode)
        self.pins[key] = gpio
        return gpio

    def get_pin(self, port: str, pin: int) -> Optional[GPIOPin]:
        return self.pins.get(f"{port}{pin}")

    def write(self, port: str, pin: int, value: bool) -> None:
        gpio = self.get_pin(port, pin)
        if gpio:
            gpio.write(value)

    def read(self, port: str, pin: int) -> bool:
        gpio = self.get_pin(port, pin)
        return gpio.read() if gpio else False

    def on_interrupt(self, port: str, pin: int,
                     trigger: InterruptTrigger,
                     handler: Callable) -> None:
        key = f"{port}{pin}"
        if key not in self._interrupts:
            self._interrupts[key] = []
        self._interrupts[key].append(handler)

    def summary(self) -> Dict[str, Any]:
        return {
            "pins": len(self.pins),
            "interrupts": sum(len(v) for v in self._interrupts.values()),
        }


@dataclass
class SPIConfig:
    mode: int = 0
    frequency: int = 1000000
    bit_order: str = "msb"
    cs_pin: Optional[GPIOPin] = None


class SPIBus:
    def __init__(self, name: str = "SPI1", config: Optional[SPIConfig] = None):
        self.name = name
        self.config = config or SPIConfig()
        self._enabled = False

    def begin(self) -> bool:
        self._enabled = True
        return True

    def end(self) -> None:
        self._enabled = False

    def transfer(self, data: bytes) -> bytes:
        if not self._enabled:
            return b""
        return bytes([~b & 0xFF for b in data])

    def write(self, data: bytes) -> int:
        if not self._enabled:
            return 0
        return len(data)

    def read(self, length: int) -> bytes:
        if not self._enabled:
            return b"\x00" * length
        return b"\x00" * length

    def summary(self) -> Dict[str, Any]:
        return {"name": self.name, "enabled": self._enabled, "frequency": self.config.frequency}


@dataclass
class I2CConfig:
    frequency: int = 100000
    address: int = 0x00


class I2CBus:
    def __init__(self, name: str = "I2C1", config: Optional[I2CConfig] = None):
        self.name = name
        self.config = config or I2CConfig()
        self._enabled = False

    def begin(self) -> bool:
        self._enabled = True
        return True

    def end(self) -> None:
        self._enabled = False

    def write(self, address: int, data: bytes) -> bool:
        if not self._enabled:
            return False
        return True

    def read(self, address: int, length: int) -> bytes:
        if not self._enabled:
            return b"\x00" * length
        return b"\x00" * length

    def scan(self) -> List[int]:
        return [0x3C, 0x76, 0x68]

    def summary(self) -> Dict[str, Any]:
        return {"name": self.name, "enabled": self._enabled, "frequency": self.config.frequency}


@dataclass
class UARTConfig:
    baudrate: int = 115200
    data_bits: int = 8
    stop_bits: int = 1
    parity: str = "none"
    flow_control: bool = False


class UART:
    def __init__(self, name: str = "UART1", config: Optional[UARTConfig] = None):
        self.name = name
        self.config = config or UARTConfig()
        self._buffer: bytearray = bytearray()
        self._open = False

    def begin(self, baudrate: Optional[int] = None) -> None:
        if baudrate:
            self.config.baudrate = baudrate
        self._open = True

    def end(self) -> None:
        self._open = False

    def write(self, data: bytes) -> int:
        if not self._open:
            return 0
        self._buffer.extend(data)
        return len(data)

    def read(self, size: int = 1) -> bytes:
        result = bytes(self._buffer[:size])
        self._buffer = self._buffer[size:]
        return result

    def available(self) -> int:
        return len(self._buffer)

    def flush(self) -> None:
        self._buffer.clear()

    def write_byte(self, byte: int) -> None:
        self._buffer.append(byte)

    def summary(self) -> Dict[str, Any]:
        return {"name": self.name, "baudrate": self.config.baudrate, "open": self._open}


@dataclass
class PWMPin:
    channel: int = 0
    frequency: int = 1000
    duty_cycle: float = 0.0
    resolution: int = 8
    enabled: bool = False


class PWMController:
    def __init__(self):
        self.channels: Dict[int, PWMPin] = {}

    def setup(self, channel: int, frequency: int = 1000,
              resolution: int = 8) -> PWMPin:
        pin = PWMPin(channel=channel, frequency=frequency, resolution=resolution)
        self.channels[channel] = pin
        return pin

    def write(self, channel: int, duty: float) -> None:
        pin = self.channels.get(channel)
        if pin:
            pin.duty_cycle = max(0.0, min(1.0, duty))
            pin.enabled = True

    def enable(self, channel: int) -> None:
        pin = self.channels.get(channel)
        if pin:
            pin.enabled = True

    def disable(self, channel: int) -> None:
        pin = self.channels.get(channel)
        if pin:
            pin.enabled = False


@dataclass
class ADCChannel:
    channel: int = 0
    resolution: int = 12
    reference_voltage: float = 3.3
    value: int = 0

    def read(self) -> int:
        return self.value

    def read_voltage(self) -> float:
        return (self.value / (2 ** self.resolution)) * self.reference_voltage


class ADCController:
    def __init__(self):
        self.channels: Dict[int, ADCChannel] = {}

    def setup(self, channel: int, resolution: int = 12,
              ref_voltage: float = 3.3) -> ADCChannel:
        adc = ADCChannel(channel=channel, resolution=resolution,
                         reference_voltage=ref_voltage)
        self.channels[channel] = adc
        return adc

    def read(self, channel: int) -> int:
        adc = self.channels.get(channel)
        return adc.read() if adc else 0

    def read_voltage(self, channel: int) -> float:
        adc = self.channels.get(channel)
        return adc.read_voltage() if adc else 0.0


@dataclass
class TimerConfig:
    period_us: int = 1000
    auto_reload: bool = True
    interrupt_enable: bool = False


class HardwareTimer:
    def __init__(self, name: str = "TIM1", config: Optional[TimerConfig] = None):
        self.name = name
        self.config = config or TimerConfig()
        self._running = False
        self._overflow_count = 0
        self.callback: Optional[Callable] = None

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def reset(self) -> None:
        self._overflow_count = 0

    def set_period(self, us: int) -> None:
        self.config.period_us = us

    @property
    def overflow_count(self) -> int:
        return self._overflow_count

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "period_us": self.config.period_us,
            "running": self._running,
        }


@dataclass
class InterruptController:
    nested: bool = True
    priority_bits: int = 4
    _enabled: bool = True

    def enable_interrupts(self) -> None:
        self._enabled = True

    def disable_interrupts(self) -> None:
        self._enabled = False

    def set_priority(self, irq_num: int, priority: int) -> None:
        pass

    def summary(self) -> Dict[str, Any]:
        return {"enabled": self._enabled, "nested": self.nested}


class RTOS:
    def __init__(self, name: str = "FreeRTOS"):
        self.name = name
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self._scheduler_running = False

    def create_task(self, name: str, fn: Callable,
                    priority: int = 1, stack_size: int = 1024) -> bool:
        self.tasks[name] = {
            "fn": fn,
            "priority": priority,
            "stack_size": stack_size,
            "state": "ready",
        }
        return True

    def start_scheduler(self) -> None:
        self._scheduler_running = True

    def delay_ms(self, ms: int) -> None:
        time.sleep(ms / 1000.0)

    def suspend_task(self, name: str) -> bool:
        if name in self.tasks:
            self.tasks[name]["state"] = "suspended"
            return True
        return False

    def resume_task(self, name: str) -> bool:
        if name in self.tasks:
            self.tasks[name]["state"] = "ready"
            return True
        return False

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "scheduler_running": self._scheduler_running,
            "tasks": len(self.tasks),
        }


class MCU:
    def __init__(self, family: MCUFamily = MCUFamily.STM32F4,
                 architecture: Architecture = Architecture.ARM_CORTEX_M4):
        self.family = family
        self.architecture = architecture
        self.name = family.value
        self.frequency_hz: int = 168000000
        self.flash_size: int = 1048576
        self.ram_size: int = 196608
        self.gpio = GPIOController()
        self.pwm = PWMController()
        self.adc = ADCController()
        self.spi_buses: Dict[str, SPIBus] = {}
        self.i2c_buses: Dict[str, I2CBus] = {}
        self.uart_ports: Dict[str, UART] = {}
        self.timers: Dict[str, HardwareTimer] = {}
        self.interrupts = InterruptController()
        self.rtos = RTOS()
        self._running = False

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def create_spi(self, name: str, config: Optional[SPIConfig] = None) -> SPIBus:
        bus = SPIBus(name, config)
        self.spi_buses[name] = bus
        return bus

    def create_i2c(self, name: str, config: Optional[I2CConfig] = None) -> I2CBus:
        bus = I2CBus(name, config)
        self.i2c_buses[name] = bus
        return bus

    def create_uart(self, name: str, config: Optional[UARTConfig] = None) -> UART:
        port = UART(name, config)
        self.uart_ports[name] = port
        return port

    def create_timer(self, name: str, config: Optional[TimerConfig] = None) -> HardwareTimer:
        timer = HardwareTimer(name, config)
        self.timers[name] = timer
        return timer

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "architecture": self.architecture.value,
            "frequency": f"{self.frequency_hz / 1e6:.0f} MHz",
            "flash": f"{self.flash_size / 1024:.0f} KB",
            "ram": f"{self.ram_size / 1024:.0f} KB",
            "gpio_pins": len(self.gpio.pins),
            "spi": len(self.spi_buses),
            "i2c": len(self.i2c_buses),
            "uart": len(self.uart_ports),
            "timers": len(self.timers),
            "rtos_tasks": len(self.rtos.tasks),
        }


# ─── Real-Time Control (DDS, RT scheduling extensions) ──────────────────────

class DDSQoS(Enum):
    BEST_EFFORT = "best_effort"
    RELIABLE = "reliable"
    KEEP_LAST = "keep_last"
    KEEP_ALL = "keep_all"


@dataclass
class DDSParticipant:
    participant_id: str = ""
    domain_id: int = 0
    enabled: bool = True


@dataclass
class DDSTopic:
    name: str = ""
    type_name: str = ""
    qos: DDSQoS = DDSQoS.RELIABLE


@dataclass
class DDSWriter:
    writer_id: str = ""
    topic: str = ""
    publication_matched: int = 0


@dataclass
class DDSReader:
    reader_id: str = ""
    topic: str = ""
    subscription_matched: int = 0


class DDS:
    def __init__(self, domain_id: int = 0):
        self.domain_id = domain_id
        self._participants: Dict[str, DDSParticipant] = {}
        self._topics: Dict[str, DDSTopic] = {}
        self._writers: Dict[str, DDSWriter] = {}
        self._readers: Dict[str, DDSReader] = {}
        self._lock = threading.Lock()

    def create_participant(self, participant_id: str) -> DDSParticipant:
        p = DDSParticipant(participant_id=participant_id, domain_id=self.domain_id)
        with self._lock:
            self._participants[participant_id] = p
        return p

    def create_topic(self, name: str, type_name: str,
                     qos: DDSQoS = DDSQoS.RELIABLE) -> DDSTopic:
        topic = DDSTopic(name=name, type_name=type_name, qos=qos)
        with self._lock:
            self._topics[name] = topic
        return topic

    def create_writer(self, participant_id: str, topic_name: str) -> Optional[DDSWriter]:
        with self._lock:
            if topic_name not in self._topics:
                return None
            writer = DDSWriter(writer_id=f"W{len(self._writers) + 1}", topic=topic_name)
            self._writers[writer.writer_id] = writer
            return writer

    def create_reader(self, participant_id: str, topic_name: str) -> Optional[DDSReader]:
        with self._lock:
            if topic_name not in self._topics:
                return None
            reader = DDSReader(reader_id=f"R{len(self._readers) + 1}", topic=topic_name)
            self._readers[reader.reader_id] = reader
            return reader

    def write(self, writer_id: str, data: bytes) -> bool:
        with self._lock:
            writer = self._writers.get(writer_id)
            if not writer:
                return False
            writer.publication_matched += 1
            return True

    def read(self, reader_id: str) -> Optional[bytes]:
        with self._lock:
            reader = self._readers.get(reader_id)
            if not reader:
                return None
            reader.subscription_matched += 1
            return b"\x00" * 64

    def summary(self) -> Dict[str, Any]:
        return {
            "domain": self.domain_id,
            "participants": len(self._participants),
            "topics": len(self._topics),
            "writers": len(self._writers),
            "readers": len(self._readers),
        }


class RTController:
    def __init__(self, name: str = "rt-controller"):
        self.name = name
        self.dds = DDS()
        self._control_loops: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create_control_loop(self, name: str, frequency_hz: float,
                            kp: float = 1.0, ki: float = 0.0, kd: float = 0.0) -> bool:
        with self._lock:
            if name in self._control_loops:
                return False
            self._control_loops[name] = {
                "frequency": frequency_hz,
                "pid": {"kp": kp, "ki": ki, "kd": kd, "integral": 0.0, "prev_error": 0.0},
                "setpoint": 0.0,
                "measurement": 0.0,
                "output": 0.0,
                "running": False,
            }
            return True

    def set_setpoint(self, loop_name: str, value: float) -> bool:
        with self._lock:
            loop = self._control_loops.get(loop_name)
            if not loop:
                return False
            loop["setpoint"] = value
            return True

    def update_measurement(self, loop_name: str, value: float) -> Optional[float]:
        with self._lock:
            loop = self._control_loops.get(loop_name)
            if not loop:
                return None
            pid = loop["pid"]
            error = loop["setpoint"] - value
            pid["integral"] += error
            derivative = error - pid["prev_error"]
            output = pid["kp"] * error + pid["ki"] * pid["integral"] + pid["kd"] * derivative
            pid["prev_error"] = error
            loop["measurement"] = value
            loop["output"] = output
            return output

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "control_loops": len(self._control_loops),
            "dds": self.dds.summary(),
        }


_embedded = MCU()


def get_embedded() -> MCU:
    return _embedded
