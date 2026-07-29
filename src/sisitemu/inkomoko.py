"""inkomoko — Edge & AI Compute: edge runtime, IoT gateway, GPU compute, tensor operations, model serving."""

from __future__ import annotations

import enum
import hashlib
import json
import math
import random
import struct
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple


class DeviceType(Enum):
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    GATEWAY = "gateway"
    CAMERA = "camera"
    DISPLAY = "display"
    CONTROLLER = "controller"


class Protocol(Enum):
    MQTT = "mqtt"
    COAP = "coap"
    HTTP = "http"
    BLE = "ble"
    ZIGBEE = "zigbee"
    LORAWAN = "lorawan"
    MODBUS = "modbus"


class GPUVendor(Enum):
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    APPLE = "apple"
    QUALCOMM = "qualcomm"


class RTTaskPriority(Enum):
    IDLE = 0
    LOW = 16
    NORMAL = 32
    HIGH = 48
    REALTIME = 64
    CRITICAL = 96


@dataclass
class EdgeDevice:
    device_id: str = ""
    name: str = ""
    device_type: DeviceType = DeviceType.SENSOR
    protocol: Protocol = Protocol.MQTT
    location: str = ""
    firmware_version: str = "1.0.0"
    battery_level: float = 100.0
    signal_strength: float = -50.0
    last_seen: float = 0.0
    online: bool = False
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class TelemetryData:
    device_id: str = ""
    timestamp: float = 0.0
    metrics: Dict[str, float] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)


class EdgeRuntime:
    def __init__(self, name: str = "edge-node-1"):
        self.name = name
        self._devices: Dict[str, EdgeDevice] = {}
        self._telemetry: List[TelemetryData] = []
        self._handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        self._running = False
        self._offline_queue: List[Dict[str, Any]] = []

    def register_device(self, device: EdgeDevice) -> None:
        with self._lock:
            device.last_seen = time.time()
            self._devices[device.device_id] = device

    def unregister_device(self, device_id: str) -> bool:
        with self._lock:
            if device_id in self._devices:
                del self._devices[device_id]
                return True
            return False

    def ingest_telemetry(self, data: TelemetryData) -> None:
        with self._lock:
            data.timestamp = time.time()
            self._telemetry.append(data)
            if device := self._devices.get(data.device_id):
                device.last_seen = time.time()
                device.online = True
            if len(self._telemetry) > 10000:
                self._telemetry = self._telemetry[-5000:]

    def process_telemetry(self, handler: Callable[[TelemetryData], None]) -> None:
        with self._lock:
            for data in self._telemetry:
                try:
                    handler(data)
                except Exception:
                    pass

    def send_command(self, device_id: str, command: str, payload: bytes) -> bool:
        with self._lock:
            device = self._devices.get(device_id)
            if not device:
                self._offline_queue.append({
                    "device_id": device_id,
                    "command": command,
                    "payload": payload.hex(),
                    "queued_at": time.time(),
                })
                return False
            if device.online:
                handler = self._handlers.get(device_id)
                if handler:
                    try:
                        handler(command, payload)
                    except Exception:
                        pass
                return True
            self._offline_queue.append({
                "device_id": device_id,
                "command": command,
                "payload": payload.hex(),
                "queued_at": time.time(),
            })
            return False

    def ota_update(self, device_id: str, firmware_path: str) -> bool:
        with self._lock:
            device = self._devices.get(device_id)
            if not device:
                return False
            device.firmware_version = firmware_path.split("_v")[-1].replace(".bin", "")
            return True

    def list_devices(self, device_type: Optional[DeviceType] = None) -> List[EdgeDevice]:
        with self._lock:
            if device_type:
                return [d for d in self._devices.values() if d.device_type == device_type]
            return list(self._devices.values())

    def get_telemetry(self, device_id: str, limit: int = 100) -> List[TelemetryData]:
        with self._lock:
            return [t for t in self._telemetry if t.device_id == device_id][-limit:]

    def sync_offline(self) -> int:
        with self._lock:
            count = len(self._offline_queue)
            self._offline_queue.clear()
            return count

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            online = sum(1 for d in self._devices.values() if d.online)
            return {
                "name": self.name,
                "devices": len(self._devices),
                "online": online,
                "offline": len(self._devices) - online,
                "telemetry_points": len(self._telemetry),
                "queued_commands": len(self._offline_queue),
            }


class IoTGateway:
    def __init__(self, name: str = "iot-gateway"):
        self.name = name
        self._protocols: Dict[Protocol, Callable] = {}
        self._routes: Dict[str, str] = {}
        self._lock = threading.Lock()
        self._message_count: int = 0

    def add_protocol(self, protocol: Protocol, handler: Callable) -> None:
        with self._lock:
            self._protocols[protocol] = handler

    def add_route(self, topic: str, target: str) -> None:
        with self._lock:
            self._routes[topic] = target

    def publish(self, protocol: Protocol, topic: str, payload: bytes) -> bool:
        with self._lock:
            handler = self._protocols.get(protocol)
            if not handler:
                return False
            try:
                handler(topic, payload)
                self._message_count += 1
                return True
            except Exception:
                return False

    def subscribe(self, protocol: Protocol, topic: str,
                  callback: Callable[[str, bytes], None]) -> None:
        def handler(t: str, p: bytes) -> None:
            if glob_match(t, topic):
                callback(t, p)
        self.add_protocol(protocol, handler)

    def route_message(self, topic: str, payload: bytes) -> Optional[str]:
        with self._lock:
            for pattern, target in self._routes.items():
                if glob_match(topic, pattern):
                    self._message_count += 1
                    return target
            return None

    @property
    def message_count(self) -> int:
        return self._message_count

    def summary(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "protocols": [p.value for p in self._protocols],
            "routes": len(self._routes),
            "messages": self._message_count,
        }


def glob_match(text: str, pattern: str) -> bool:
    i, j = 0, 0
    star = -1
    match = 0
    while i < len(text):
        if j < len(pattern) and pattern[j] in (text[i], "+"):
            i += 1
            j += 1
        elif j < len(pattern) and pattern[j] == "#":
            star = j
            match = i
            j += 1
        elif star != -1:
            j = star + 1
            match += 1
            i = match
        else:
            return False
    while j < len(pattern) and pattern[j] == "#":
        j += 1
    return j == len(pattern)


@dataclass
class GPUDevice:
    device_id: str = ""
    vendor: GPUVendor = GPUVendor.NVIDIA
    name: str = ""
    compute_capability: str = "7.5"
    memory_mb: int = 8192
    cores: int = 2560
    clock_mhz: int = 1500
    memory_used_mb: int = 0
    utilization: float = 0.0
    temperature_c: float = 45.0


class GPUCompute:
    def __init__(self):
        self._devices: Dict[str, GPUDevice] = {}
        self._lock = threading.Lock()

    def discover(self) -> List[GPUDevice]:
        with self._lock:
            if not self._devices:
                device = GPUDevice(
                    device_id="gpu-0",
                    vendor=GPUVendor.NVIDIA,
                    name="I-Core GPU",
                    compute_capability="8.0",
                    memory_mb=16384,
                    cores=5120,
                    clock_mhz=1800,
                )
                self._devices[device.device_id] = device
            return list(self._devices.values())

    def allocate(self, memory_mb: int) -> Optional[str]:
        with self._lock:
            for did, dev in self._devices.items():
                if dev.memory_used_mb + memory_mb <= dev.memory_mb:
                    dev.memory_used_mb += memory_mb
                    dev.utilization = min(100.0, dev.utilization + random.uniform(1, 10))
                    return did
            return None

    def free(self, device_id: str, memory_mb: int) -> bool:
        with self._lock:
            dev = self._devices.get(device_id)
            if not dev:
                return False
            dev.memory_used_mb = max(0, dev.memory_used_mb - memory_mb)
            dev.utilization = max(0.0, dev.utilization - random.uniform(1, 10))
            return True

    def launch_kernel(self, device_id: str, kernel_name: str,
                      grid: Tuple[int, int, int],
                      block: Tuple[int, int, int],
                      args: bytes) -> Optional[float]:
        with self._lock:
            dev = self._devices.get(device_id)
            if not dev:
                return None
            total_threads = grid[0] * grid[1] * grid[2] * block[0] * block[1] * block[2]
            duration_ms = (total_threads / dev.cores) * random.uniform(0.1, 2.0)
            dev.temperature_c += random.uniform(0.1, 0.5)
            return duration_ms

    def get_device(self, device_id: str) -> Optional[GPUDevice]:
        with self._lock:
            return self._devices.get(device_id)

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "devices": len(self._devices),
                "total_memory_mb": sum(d.memory_mb for d in self._devices.values()),
                "used_memory_mb": sum(d.memory_used_mb for d in self._devices.values()),
            }


class TensorShape:
    def __init__(self, dims: List[int]):
        self.dims = list(dims)

    def __len__(self) -> int:
        return len(self.dims)

    def __getitem__(self, idx: int) -> int:
        return self.dims[idx]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TensorShape):
            return False
        return self.dims == other.dims

    @property
    def size(self) -> int:
        return math.prod(self.dims)

    def reshape(self, new_dims: List[int]) -> TensorShape:
        return TensorShape(new_dims)

    def broadcast(self, other: TensorShape) -> Optional[TensorShape]:
        result = []
        for a, b in zip(reversed(self.dims), reversed(other.dims)):
            if a == b:
                result.append(a)
            elif a == 1:
                result.append(b)
            elif b == 1:
                result.append(a)
            else:
                return None
        return TensorShape(list(reversed(result)))

    def to_dict(self) -> Dict[str, Any]:
        return {"dims": self.dims, "size": self.size}


class Tensor:
    def __init__(self, data: List[Any], shape: TensorShape, dtype: str = "float32"):
        self.data = data
        self._shape = shape
        self.dtype = dtype

    @property
    def shape(self) -> TensorShape:
        return self._shape

    def reshape(self, new_dims: List[int]) -> Tensor:
        return Tensor(self.data, TensorShape(new_dims), self.dtype)

    def __add__(self, other: Tensor) -> Tensor:
        return TensorOps.add(self, other)

    def __sub__(self, other: Tensor) -> Tensor:
        return TensorOps.sub(self, other)

    def __mul__(self, other: Tensor) -> Tensor:
        return TensorOps.mul(self, other)

    def __matmul__(self, other: Tensor) -> Tensor:
        return TensorOps.matmul(self, other)


class TensorOps:
    @staticmethod
    def add(a: Tensor, b: Tensor) -> Tensor:
        shape = a.shape.broadcast(b.shape)
        if shape is None:
            raise ValueError(f"Cannot broadcast shapes {a.shape.dims} and {b.shape.dims}")
        size = shape.size
        result = [a.data[i % len(a.data)] + b.data[i % len(b.data)] for i in range(size)]
        return Tensor(result, shape, a.dtype)

    @staticmethod
    def sub(a: Tensor, b: Tensor) -> Tensor:
        shape = a.shape.broadcast(b.shape)
        if shape is None:
            raise ValueError(f"Cannot broadcast shapes {a.shape.dims} and {b.shape.dims}")
        size = shape.size
        result = [a.data[i % len(a.data)] - b.data[i % len(b.data)] for i in range(size)]
        return Tensor(result, shape, a.dtype)

    @staticmethod
    def mul(a: Tensor, b: Tensor) -> Tensor:
        shape = a.shape.broadcast(b.shape)
        if shape is None:
            raise ValueError(f"Cannot broadcast shapes {a.shape.dims} and {b.shape.dims}")
        size = shape.size
        result = [a.data[i % len(a.data)] * b.data[i % len(b.data)] for i in range(size)]
        return Tensor(result, shape, a.dtype)

    @staticmethod
    def matmul(a: Tensor, b: Tensor) -> Tensor:
        if len(a.shape.dims) < 2 or len(b.shape.dims) < 2:
            raise ValueError("matmul requires at least 2D tensors")
        if a.shape.dims[-1] != b.shape.dims[-2]:
            raise ValueError(f"Incompatible shapes {a.shape.dims} and {b.shape.dims}")
        m, k = a.shape.dims[-2], a.shape.dims[-1]
        n = b.shape.dims[-1]
        result = []
        for i in range(m):
            for j in range(n):
                total = 0.0
                for p in range(k):
                    total += a.data[i * k + p] * b.data[p * n + j]
                result.append(total)
        out_shape = a.shape.dims[:-2] + [m, n]
        return Tensor(result, TensorShape(out_shape), a.dtype)

    @staticmethod
    def relu(t: Tensor) -> Tensor:
        return Tensor([max(0.0, x) for x in t.data], t.shape, t.dtype)

    @staticmethod
    def sigmoid(t: Tensor) -> Tensor:
        import math
        return Tensor([1.0 / (1.0 + math.exp(-x)) for x in t.data], t.shape, t.dtype)

    @staticmethod
    def softmax(t: Tensor) -> Tensor:
        import math
        max_val = max(t.data)
        exps = [math.exp(x - max_val) for x in t.data]
        sum_exp = sum(exps)
        return Tensor([e / sum_exp for e in exps], t.shape, t.dtype)

    @staticmethod
    def transpose(t: Tensor) -> Tensor:
        if len(t.shape.dims) != 2:
            raise ValueError("transpose requires 2D tensor")
        m, n = t.shape.dims
        result = [t.data[j * n + i] for i in range(m) for j in range(n)]
        return Tensor(result, TensorShape([n, m]), t.dtype)


@dataclass
class ModelSpec:
    model_id: str = ""
    name: str = ""
    version: str = "1.0.0"
    framework: str = "sisitemu"
    input_shape: List[int] = field(default_factory=list)
    output_shape: List[int] = field(default_factory=list)
    precision: str = "float32"
    batch_size: int = 1
    max_latency_ms: float = 100.0


class ModelServing:
    def __init__(self):
        self._models: Dict[str, ModelSpec] = {}
        self._loaded: Dict[str, bool] = {}
        self._lock = threading.Lock()
        self._cache: Dict[str, Any] = {}
        self._batch_queue: List[Tuple[str, Tensor, Callable]] = []

    def load_model(self, spec: ModelSpec) -> bool:
        with self._lock:
            self._models[spec.model_id] = spec
            self._loaded[spec.model_id] = True
            return True

    def unload_model(self, model_id: str) -> bool:
        with self._lock:
            if model_id in self._loaded:
                del self._loaded[model_id]
                return True
            return False

    def predict(self, model_id: str, input_tensor: Tensor) -> Optional[Tensor]:
        with self._lock:
            spec = self._models.get(model_id)
            if not spec or not self._loaded.get(model_id):
                return None
            if input_tensor.shape.dims != spec.input_shape:
                return None
            result_data = [x * random.uniform(0.9, 1.1) for x in input_tensor.data]
            if spec.output_shape:
                result = Tensor(result_data, TensorShape(spec.output_shape), spec.precision)
            else:
                result = Tensor(result_data, input_tensor.shape, spec.precision)
            return result

    def predict_batch(self, model_id: str, inputs: List[Tensor]) -> Optional[List[Tensor]]:
        results = []
        for inp in inputs:
            result = self.predict(model_id, inp)
            if result:
                results.append(result)
        return results if results else None

    def cached_predict(self, model_id: str, input_tensor: Tensor,
                       ttl: float = 5.0) -> Optional[Tensor]:
        key = hashlib.sha256(
            f"{model_id}:{json.dumps(input_tensor.data)}".encode()
        ).hexdigest()
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() - entry["ts"] < ttl:
                    return entry["result"]
        result = self.predict(model_id, input_tensor)
        if result:
            with self._lock:
                self._cache[key] = {"result": result, "ts": time.time()}
        return result

    def list_models(self) -> List[ModelSpec]:
        with self._lock:
            return list(self._models.values())

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "models": len(self._models),
                "loaded": sum(1 for v in self._loaded.values() if v),
                "cache_size": len(self._cache),
                "frameworks": list(set(m.framework for m in self._models.values())),
            }


class RTTask:
    def __init__(self, name: str, fn: Callable, period_ms: int = 100,
                 priority: RTTaskPriority = RTTaskPriority.NORMAL,
                 deadline_ms: int = 100, budget_ms: int = 50):
        self.name = name
        self.fn = fn
        self.period_ms = period_ms
        self.priority = priority
        self.deadline_ms = deadline_ms
        self.budget_ms = budget_ms
        self.last_run: float = 0.0
        self.total_runs: int = 0
        self.missed_deadlines: int = 0
        self.max_jitter_ms: float = 0.0


class RealTimeController:
    def __init__(self):
        self._tasks: List[RTTask] = []
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def add_task(self, task: RTTask) -> None:
        with self._lock:
            self._tasks.append(task)
            self._tasks.sort(key=lambda t: t.priority.value, reverse=True)

    def remove_task(self, name: str) -> bool:
        with self._lock:
            before = len(self._tasks)
            self._tasks = [t for t in self._tasks if t.name != name]
            return len(self._tasks) < before

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _run_loop(self) -> None:
        while self._running:
            now = time.time()
            with self._lock:
                for task in self._tasks:
                    if now - task.last_run >= task.period_ms / 1000.0:
                        start = time.time()
                        try:
                            task.fn()
                        except Exception:
                            pass
                        elapsed = (time.time() - start) * 1000
                        task.total_runs += 1
                        if elapsed > task.deadline_ms:
                            task.missed_deadlines += 1
                        task.max_jitter_ms = max(task.max_jitter_ms, abs(elapsed - task.budget_ms))
                        task.last_run = now
            time.sleep(0.001)

    def get_stats(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                {
                    "name": t.name,
                    "priority": t.priority.value,
                    "period_ms": t.period_ms,
                    "total_runs": t.total_runs,
                    "missed_deadlines": t.missed_deadlines,
                    "max_jitter_ms": round(t.max_jitter_ms, 2),
                }
                for t in self._tasks
            ]


class LowPowerManager:
    def __init__(self):
        self._sleep_states: Dict[str, bool] = {
            "wfi": True,
            "sleep": True,
            "deep_sleep": True,
            "hibernate": True,
        }
        self._current_state: str = "active"
        self._wake_sources: List[str] = []
        self._lock = threading.Lock()

    def set_state(self, state: str) -> bool:
        with self._lock:
            if state not in self._sleep_states:
                return False
            self._current_state = state
            return True

    def add_wake_source(self, source: str) -> None:
        with self._lock:
            if source not in self._wake_sources:
                self._wake_sources.append(source)

    def remove_wake_source(self, source: str) -> bool:
        with self._lock:
            if source in self._wake_sources:
                self._wake_sources.remove(source)
                return True
            return False

    def estimate_power(self, state: str) -> float:
        consumption = {
            "active": 500.0,
            "wfi": 100.0,
            "sleep": 10.0,
            "deep_sleep": 1.0,
            "hibernate": 0.1,
        }
        return consumption.get(state, 500.0)

    @property
    def current_state(self) -> str:
        return self._current_state

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "state": self._current_state,
                "power_mw": self.estimate_power(self._current_state),
                "wake_sources": self._wake_sources,
            }


def get_edge_runtime(name: str = "edge-node-1") -> EdgeRuntime:
    return EdgeRuntime(name)


def get_iot_gateway(name: str = "iot-gateway") -> IoTGateway:
    return IoTGateway(name)


def get_gpu_compute() -> GPUCompute:
    return GPUCompute()


def get_model_serving() -> ModelServing:
    return ModelServing()


def get_rt_controller() -> RealTimeController:
    return RealTimeController()


def get_low_power_manager() -> LowPowerManager:
    return LowPowerManager()
