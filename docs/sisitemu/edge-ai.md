# Edge & AI Compute — `inkomoko`

Build edge-native AI inference servers, IoT gateways, GPU compute pipelines,
tensor operations, model serving, real-time controllers, and low power managers.

## Quick Start

```python
from sisitemu.inkomoko import (
    EdgeRuntime, IoTGateway,
    GPUCompute, Tensor, ModelServing,
    RealTimeController, LowPowerManager,
)

# Edge device
edge = EdgeRuntime()
device = edge.register_device("sensor-01", device_type="temperature")
edge.ingest(device.id, {"temperature": 23.5, "humidity": 60})

# Tensor operations
a = Tensor(shape=(2, 3), data=[1,2,3,4,5,6])
b = Tensor(shape=(2, 3), data=[6,5,4,3,2,1])
c = a + b  # element-wise addition
```

## Components

### EdgeRuntime
```python
edge = EdgeRuntime()
dev = edge.register_device("cam-01", device_type="camera")
edge.ingest(dev.id, {"frame": 1234, "detections": 5})
commands = edge.get_pending_commands(dev.id)
edge.send_command(dev.id, "ota_update", {"version": "2.1.0"})
status = edge.get_device_status(dev.id)
```

### IoTGateway
```python
gw = IoTGateway(bind="0.0.0.0", port=8883)
gw.add_protocol_bridge("mqtt", "coap")
gw.route("sensors/temperature", "http://10.0.0.1:8080/ingest")
gw.start()
```

### GPUCompute
```python
gpu = GPUCompute()
device = gpu.discover_devices()[0]
gpu.allocate(device, memory_mb=1024)
kernel_result = gpu.launch_kernel(
    device, kernel="matmul",
    args=[a_tensor, b_tensor],
)
```

### Tensor
```python
a = Tensor(shape=(2, 3), data=[1,2,3,4,5,6])
b = Tensor(shape=(3, 2), data=[1,2,3,4,5,6])
c = a.matmul(b)    # matrix multiply
d = a.relu()       # activation
e = a.softmax()    # softmax
f = a.transpose()  # (3, 2)
```

### ModelServing
```python
ms = ModelServing()
model = ms.load("resnet50", version="v2")
result = ms.predict(model, input_tensor, batch=True)
```

### RealTimeController
```python
rt = RealTimeController()
task = rt.create_task(
    name="pid-loop",
    priority=RTTaskPriority.HIGH,
    deadline_ms=10,
    jitter_us=100,
)
```

### LowPowerManager
```python
lpm = LowPowerManager()
lpm.set_idle_timeout("5m")
lpm.sleep()
```

## Architecture

```
Edge & AI Compute Stack
├── EdgeRuntime       — device registry, telemetry, OTA, offline queue
├── IoTGateway        — MQTT/CoAP/BLE/Zigbee/LoRaWAN protocol bridge
├── GPUCompute        — device discovery, allocation, kernel launch
├── Tensor            — add/sub/mul/matmul/relu/sigmoid/softmax/transpose
├── ModelServing      — load, predict, batch, cache with TTL
├── RealTimeController — RT tasks, deadlines, jitter control
└── LowPowerManager   — sleep/deep-sleep/hibernate/wake sources
```
