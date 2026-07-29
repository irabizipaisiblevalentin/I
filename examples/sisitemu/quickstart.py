"""SISITEMU Quickstart — demonstrates all 14 modules (core + infrastructure domains)."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))


def demo_ibikoresho_sisitemu():
    from sisitemu.ibikoresho_sisitemu import (
        ArenaAllocator, PoolAllocator, Pointer, Slice,
        BitManipulator, AtomicOps, Endianness, SystemsCore,
    )

    arena = ArenaAllocator(name="main", size=4096)
    block = arena.allocate(64, tag="demo")
    print(f"  Arena allocated: offset={block.address} size={block.size}")

    pool = PoolAllocator(name="pool", block_size=32, count=16)
    pblock = pool.allocate()
    print(f"  Pool allocated: offset={pblock.address}")
    pool.free(pblock)

    ptr = Pointer(address=0x1000, offset=4)
    print(f"  Pointer: addr=0x{ptr.address:x} offset={ptr.offset}")

    s = Slice(data=bytearray(16), offset=0, length=16)
    print(f"  Slice: length={len(s)}")

    bm = BitManipulator()
    value = bm.set_bit(0b00001111, 7)
    print(f"  Bit set: 0b{value:08b}")

    ao = AtomicOps()
    arr = [10]
    result = ao.fetch_add(arr, 0, 5)
    print(f"  Atomic fetch_add: old={result} new={arr[0]}")

    native = Endianness.host()
    print(f"  Native endianness: {native}")

    core = SystemsCore()
    core.create_allocator("core", 8192)
    print(f"  SystemsCore created")


def demo_ibikorwa_sisitemu():
    from sisitemu.ibikorwa_sisitemu import (
        ProcessManager, Scheduler, Timer, IntervalTimer, SignalManager,
        ProcessState, ThreadPriority,
    )

    pm = ProcessManager()
    proc = pm.create_process("demo_process", command="/bin/true", priority=ThreadPriority.NORMAL)
    print(f"  Created process: pid={proc.pid} name={proc.name}")

    sched = Scheduler(policy="round_robin", quantum=10)
    from sisitemu.ibikorwa_sisitemu import ThreadInfo
    thread = ThreadInfo(tid=1, name="main")
    sched.add_thread(thread)
    nxt = sched.next_thread()
    print(f"  Scheduler next: tid={nxt.tid if nxt else 'none'}")

    timer = Timer(name="demo_timer")
    timer.start()
    print(f"  Timer started: running={timer.running}")

    itimer = IntervalTimer(name="periodic", interval=1.0, callback=lambda: None)
    print(f"  IntervalTimer created: interval={itimer.interval}s")

    sm = SignalManager()
    sm.register_handler(2, lambda: None)
    print("  Signal handler registered for SIGINT")


def demo_ububiko():
    from sisitemu.ububiko import MemoryFileSystem, FileHandle, FileType

    fs = MemoryFileSystem()
    fs.write_file("/hello.txt", b"Hello SISITEMU!")
    content = fs.open("/hello.txt", "r")
    data = content.read(1024)
    print(f"  Read file: {data}")
    content.close()

    entries = fs.listdir("/")
    for entry in entries:
        print(f"  Entry: {entry.name} ({'dir' if entry.is_directory() else 'file'})")

    fh = fs.open("/hello.txt", "r")
    data2 = fh.read(1024)
    print(f"  FileHandle read: {data2}")
    fh.close()


def demo_itumanaho_sisitemu():
    from sisitemu.itumanaho_sisitemu import (
        TCPServer, UDPEndpoint, DNSResolver, CANBus, SerialPort,
        NetworkStack, NetworkAddress,
    )

    addr = NetworkAddress.local(9000)
    server = TCPServer(address=addr)
    print(f"  TCP server created: {server}")

    udp = UDPEndpoint(address=NetworkAddress.local(9001))
    print(f"  UDP endpoint created")

    dns = DNSResolver()
    ips = dns.resolve("localhost")
    print(f"  DNS resolved localhost: {ips}")

    can = CANBus(name="vcan0", bitrate=500000)
    print(f"  CAN bus: {can}")

    serial = SerialPort(name="COM1", baudrate=115200)
    print(f"  Serial port: {serial}")

    stack = NetworkStack()
    stack.create_tcp_server("main", 8080)
    stack.create_udp_endpoint("monitor", 9000)
    stack.create_serial_port("debug", "COM1", 115200)
    stack.create_can_bus("vehicle", "vcan0", 500000)
    print(f"  NetworkStack with multiple endpoints")


def demo_ibyinjijwe():
    from sisitemu.ibyinjijwe import (
        MCU, GPIOController, SPIBus, SPIConfig, I2CBus, I2CConfig,
        UART, UARTConfig, PWMController, ADCController,
        HardwareTimer, TimerConfig, InterruptController, RTOS,
        Architecture, MCUFamily, PinMode,
    )

    mcu = MCU(family=MCUFamily.STM32F4, architecture=Architecture.ARM_CORTEX_M4)
    mcu.start()
    print(f"  MCU: {mcu.family.value} @ {mcu.frequency_hz}Hz")

    gpio = GPIOController()
    gpio.add_pin("A", 5, PinMode.OUTPUT)
    gpio.write("A", 5, True)
    val = gpio.read("A", 5)
    print(f"  GPIO A5: {'HIGH' if val else 'LOW'}")

    spi = SPIBus(name="spi1", config=SPIConfig(mode=0, frequency=1000000))
    spi.begin()
    print(f"  SPI bus: {spi}")

    i2c = I2CBus(name="i2c1", config=I2CConfig(frequency=100000))
    i2c.begin()
    print(f"  I2C bus: {i2c}")

    uart = UART(name="uart1", config=UARTConfig(baudrate=115200))
    uart.begin(115200)
    uart.write(b"Hello")
    print(f"  UART: {uart}")

    pwm = PWMController()
    pwm.setup(channel=0, frequency=1000, resolution=255)
    pwm.write(0, 128)
    print(f"  PWM channel 0: duty=128")

    adc = ADCController()
    adc.setup(channel=0, resolution=12, ref_voltage=3.3)
    raw = adc.read(0)
    volt = adc.read_voltage(0)
    print(f"  ADC channel 0: raw={raw} voltage={volt:.2f}V")

    ht = HardwareTimer(name="timer2", config=TimerConfig())
    ht.set_period(1000)
    print(f"  Hardware timer period set")

    ic = InterruptController()
    ic.enable_interrupts()
    print("  Interrupts enabled")

    rtos = RTOS(name="demo_rtos")
    rtos.create_task("blink", lambda: print("    Task blink running"), priority=1, stack_size=256)
    tlist = rtos.summary()
    print(f"  RTOS: {tlist}")


def demo_umuyobora():
    from sisitemu.umuyobora import (
        Kernel, VirtualMemoryManager, IPCChannel, SharedMemoryRegion,
        Driver, DriverManager, PowerManager, KernelState,
    )

    kernel = Kernel(name="I-Kernel")
    kernel.boot()
    print(f"  Kernel booted: {kernel.name} state={kernel.state}")

    vmm = VirtualMemoryManager(total_pages=1024, page_size=4096)
    vmm.map_page(0x1000, 0x2000, process_id=1)
    print(f"  VMM: page 0x1000 mapped (used={vmm.used_pages}/{vmm.total_pages})")

    ipc = IPCChannel(name="demo_channel")
    ipc.subscribe(1, lambda pid, data: None)
    print(f"  IPC channel: {ipc.name}")

    shm = SharedMemoryRegion(name="shared", size=4096)
    print(f"  Shared memory region: {shm.name} ({shm.size} bytes)")

    driver = Driver(name="test_driver", driver_type="pcie")
    driver.init()
    print(f"  Driver: {driver.name} type={driver.driver_type}")

    pm = PowerManager()
    pm.sleep()
    pm.wake()
    print(f"  Power manager: sleep/wake cycle")

    kernel.halt()
    print(f"  Kernel state: {kernel.state.value}")


def demo_ibikoresho_byinjijwe():
    from sisitemu.ibikoresho_byinjijwe import (
        USBController, PCIeController, StorageDevice, GraphicsDevice,
        SensorDevice, DisplayDevice, TouchDevice, IndustrialController,
        DeviceManager,
    )

    usb = USBController()
    usb.enable()
    devices = usb.enumerate()
    print(f"  USB controller: {len(devices)} devices (version {usb.version})")

    pcie = PCIeController()
    pcie.scan()
    print(f"  PCIe controller active")

    storage = StorageDevice(name="nvme0", block_size=512)
    print(f"  Storage: {storage.name} block_size={storage.block_size}")

    gpu = GraphicsDevice(name="gpu0", width=1920, height=1080)
    gpu.clear(0x000000)
    print(f"  Graphics: {gpu.name} {gpu.width}x{gpu.height}")

    sensor = SensorDevice(name="bme280", sensor_type="temperature", unit="celsius")
    sensor.set_value(25.5)
    reading = sensor.read()
    print(f"  Sensor: {reading}")

    display = DisplayDevice(name="lcd", width=320, height=240)
    display.fill(0xFF)
    print(f"  Display: {display.name} {display.width}x{display.height}")

    touch = TouchDevice(name="touch1")
    touch.simulate_touch(100, 200, 0.5)
    tpos = touch.read_touch()
    print(f"  Touch: {tpos}")

    industrial = IndustrialController(name="plc1")
    industrial.write_digital(0, True)
    dval = industrial.read_digital(0)
    print(f"  Industrial: digital channel 0 = {dval}")

    dm = DeviceManager()
    dm.create_usb_controller("usb2")
    dm.create_storage("sata0", 500 * 1024 * 1024, 4096)
    dm.create_graphics("gpu1", 1920, 1080)
    print(f"  DeviceManager with multiple devices")


def demo_umutekano_sisitemu():
    from sisitemu.umutekano_sisitemu import (
        MemoryProtectionUnit, MemoryProtectionRegion, Sandbox,
        SandboxPolicy, CryptographicEngine, SecureIPCChannel,
        StackProtection, AuditLog, SecurityManager, SecurityLevel,
    )

    mpu = MemoryProtectionUnit()
    region = MemoryProtectionRegion(
        start=0x20000000, end=0x20001000,
        readable=True, writable=False, executable=False,
        name="code",
    )
    mpu.add_region(region)
    print(f"  MPU: {len(mpu.regions)} region(s) configured")

    sandbox = Sandbox(name="untrusted", policy=SandboxPolicy.RESTRICTED)
    sandbox.allow_path("/tmp/")
    sandbox.allow_syscall(0)
    print(f"  Sandbox: {sandbox.name} policy={sandbox.policy.value}")

    crypto = CryptographicEngine()
    key = crypto.generate_key(32)
    h = crypto.hash(b"data", "sha256")
    print(f"  Crypto: hash={crypto.hash_to_hex(h)[:16]}...")

    secure = SecureIPCChannel(name="secure_channel")
    secure.set_key(key)
    print(f"  Secure IPC: {secure.name}")

    sp = StackProtection()
    canary = sp.get_canary()
    sp.check(canary)
    print(f"  Stack protection: canary OK failures={sp.failures}")

    audit = AuditLog()
    audit.log(event="demo", details={"module": "umutekano"}, severity="info")
    print(f"  Audit log: {len(audit.entries)} entry/ies")

    mgr = SecurityManager()
    print(f"  Security manager created (level={mgr._level.value if hasattr(mgr, '_level') else 'default'})")


def demo_igenzura_sisitemu():
    from sisitemu.igenzura_sisitemu import (
        Tracer, Profiler, MemoryInspector, CrashDump,
        LiveDiagnostics, Debugger, TraceEvent, DebugLevel,
    )

    tracer = Tracer()
    tracer.enable()
    tracer.trace(TraceEvent.SYSCALL, "read", pid=1)
    tracer.trace(TraceEvent.ALLOC, "malloc 64", pid=1)
    tracer.disable()
    events = tracer.query(event_type=None, pid=1, limit=10)
    print(f"  Tracer: {len(events)} events recorded")

    profiler = Profiler()
    profiler.start(interval=0.1)
    profiler.record_sample("main", "ibikoresho", cpu=10.0, memory=64.0)
    profiler.stop()
    hotspots = profiler.get_hotspots(top_n=5)
    print(f"  Profiler: {len(hotspots)} hotspot(s)")

    inspector = MemoryInspector()
    from sisitemu.igenzura_sisitemu import MemoryRegion as MR
    inspector.add_region(MR(address=0x1000, size=0x1000, tag="heap"))
    stats = inspector.get_stats()
    print(f"  Memory inspector: {stats}")

    crash = CrashDump()
    crash.capture(
        message="test crash",
        registers={"rip": "0x401000", "rsp": "0x7fff"},
        stack_trace=["main", "handler"],
    )
    last = crash.last()
    print(f"  Crash dump record: {last}")

    diag = LiveDiagnostics()
    diag.register_check("mem", lambda: ("ok", "memory healthy"))
    results = diag.run_all()
    print(f"  Diagnostics: {len(results)} check(s)")

    dbg = Debugger()
    dbg.set_breakpoint("main", lambda: None)
    print(f"  Debugger active")


def demo_imikorere_sisitemu():
    from sisitemu.imikorere_sisitemu import (
        Benchmark, LatencyMeter, MemoryUsageTracker,
        ThroughputMeter, PerformanceOptimizer,
    )

    bench = Benchmark(name="demo")
    result = bench.measure("sum", lambda: sum(range(10000)), iterations=100)
    print(f"  Benchmark: name={result.name} avg={result.avg_time:.5f}s p50={result.p50:.3f}s")

    meter = LatencyMeter()
    meter.record(1.5)
    meter.record(2.0)
    meter.record(0.8)
    print(f"  LatencyMeter: avg={meter.avg:.2f} p50={meter.p50:.2f} p95={meter.p95:.2f}")

    tracker = MemoryUsageTracker()
    try:
        tracker.snapshot("start")
        data = bytearray(100000)
        tracker.snapshot("alloc")
        diff = tracker.diff("start", "alloc")
        print(f"  Memory diff: {diff}")
    except Exception:
        print(f"  Memory tracker: (requires psutil)")

    tm = ThroughputMeter(name="data")
    tm.start()
    tm.increment(1000)
    tm.stop()
    print(f"  Throughput meter: {tm.name}")

    opt = PerformanceOptimizer()
    opt.recommend("Use ArenaAllocator for repeated allocations")
    recs = opt.get_recommendations()
    print(f"  Optimizer: {len(recs)} recommendation(s)")


def demo_ububiko_db():
    from sisitemu.ububiko_db import StorageEngine, BTreeIndex, TransactionManager

    engine = StorageEngine(name="test")
    engine.open()
    engine.put(b"key1", b"value1")
    r = engine.get(b"key1")
    engine.close()
    print(f"  StorageEngine: get(key1)={r}")

    tree = BTreeIndex(order=4)
    tree.insert(42, b"db_data")
    r2 = tree.search(42)
    print(f"  BTreeIndex: search(42)={r2}")

    tm = TransactionManager()
    t1 = tm.begin()
    t2 = tm.begin()
    tm.commit(t1)
    tm.rollback(t2)
    print(f"  Transaction: active={len(tm.active_transactions())}")


def demo_gukwirakwiza():
    from sisitemu.gukwirakwiza import (
        RaftConsensus, RaftConfig,
        ServiceDiscovery, ServiceInstance,
        DistributedLock, MessageQueue, RPCServer,
    )

    cfg = RaftConfig(
        node_id="n1", peers=["n2:9001", "n3:9002"],
        election_timeout_min=150,
    )
    raft = RaftConsensus(cfg)
    raft.start()
    raft.propose("set", b"x=1")
    print(f"  Raft: role={raft.role.value} term={raft.current_term}")
    raft.stop()

    sd = ServiceDiscovery()
    sd.register(ServiceInstance(name="svc", host="10.0.0.1", port=8080, ttl=30))
    instances = sd.discover("svc")
    print(f"  ServiceDiscovery: {len(instances)} instance(s)")
    if instances:
        sd.unregister("svc", instances[0].id)

    lock = DistributedLock()
    token = lock.acquire("res-1", "worker-1", ttl=30)
    if token is not None:
        print(f"  DistributedLock: acquired token={token}")
        lock.release("res-1", "worker-1", token)

    queue = MessageQueue()
    queue.create_topic("events", partitions=3)
    seq = queue.publish("events", b"k1", b"v1")
    print(f"  MessageQueue: published seq={seq}")

    server = RPCServer(host="0.0.0.0", port=9001)
    server.register("ping", lambda r: {"pong": True})
    print(f"  RPCServer: registered 'ping' handler")


def demo_ibicu():
    from sisitemu.ibicu import (
        ContainerRuntime, VMManager, LoadBalancer, LBAlgorithm,
        Orchestrator, SecretManager, ConfigManager,
    )

    rt = ContainerRuntime()
    c = rt.create_container("web-1", image="nginx:latest")
    rt.start_container(c.container_id)
    s = rt.get_container(c.container_id)
    print(f"  Container: name={s.name} state={s.state}")
    rt.stop_container(c.container_id)

    vmm = VMManager()
    vm = vmm.create_vm("worker-1", image="ubuntu", vcpus=4, memory_mb=8192)
    vmm.power_on(vm.vm_id)
    print(f"  VM: id={vm.vm_id} vcpus={vm.vcpus} memory={vm.memory_mb}")
    vmm.power_off(vm.vm_id)

    lb = LoadBalancer(name="api", algorithm=LBAlgorithm.ROUND_ROBIN)
    lb.add_backend("10.0.0.1", 8080)
    lb.add_backend("10.0.0.2", 8080, weight=2)
    backend = lb.next_backend("api")
    print(f"  LoadBalancer: backend={backend}")

    orch = Orchestrator(runtime=rt)
    deploy = orch.create_deployment("svc", image="myapp:1.0", replicas=3)
    print(f"  Orchestrator: deployed id={deploy.deployment_id} replicas={deploy.replicas}")
    orch.scale(deploy.deployment_id, replicas=5)

    sm = SecretManager()
    sm.store("db-pass", "s3cret!")
    pw = sm.retrieve("db-pass")
    print(f"  SecretManager: retrieved={pw is not None}")

    cm = ConfigManager()
    cm.set("log_level", "debug")
    val = cm.get("log_level")
    print(f"  ConfigManager: log_level={val}")


def demo_inkomoko():
    from sisitemu.inkomoko import (
        EdgeRuntime, EdgeDevice, DeviceType, IoTGateway,
        GPUCompute, Tensor, TensorShape, TensorOps, ModelServing, ModelSpec,
        RealTimeController, RTTask, RTTaskPriority, LowPowerManager,
        TelemetryData,
    )

    edge = EdgeRuntime()
    dev = EdgeDevice(device_id="sensor-01", name="temp-sensor", device_type=DeviceType.SENSOR)
    edge.register_device(dev)
    edge.ingest_telemetry(TelemetryData(device_id=dev.device_id, metrics={"temp": 23.5, "humidity": 60}))
    telemetry = edge.get_telemetry(dev.device_id)
    # telemetry is a list; show we got some
    print(f"  EdgeRuntime: device={dev.device_id} telemetry_count={len(telemetry)}")

    from sisitemu.inkomoko import Protocol as IoTProtocolEnum
    gw = IoTGateway(name="main-gateway")
    gw.subscribe(IoTProtocolEnum.MQTT, "sensors/#", lambda t, p: None)
    gw.add_route("sensors/temp", target="http://10.0.0.1:8080/ingest")
    gw.publish(IoTProtocolEnum.MQTT, "sensors/temp", b'{"temp":23.5}')
    print(f"  IoTGateway: {gw.name} messages={gw.message_count}")

    compute = GPUCompute()
    ok = compute.allocate(memory_mb=1024)
    print(f"  GPUCompute: allocated={ok}")

    a = Tensor(data=[1, 2, 3, 4, 5, 6], shape=TensorShape([2, 3]))
    b = Tensor(data=[6, 5, 4, 3, 2, 1], shape=TensorShape([2, 3]))
    c = a + b
    d = TensorOps.matmul(a, Tensor(data=[1, 2, 3, 4, 5, 6], shape=TensorShape([3, 2])))
    print(f"  Tensor: add={c.data} matmul={d.data}")

    ms = ModelServing()
    spec = ModelSpec(name="resnet50", version="v2")
    ms.load_model(spec)
    pred = ms.predict("resnet50", a)
    print(f"  ModelServing: predict={pred}")

    rt = RealTimeController()
    task = RTTask(name="pid-loop", fn=lambda: None, period_ms=10, priority=RTTaskPriority.HIGH, deadline_ms=10)
    rt.add_task(task)
    print(f"  RTController: task count={len(rt.get_stats())}")

    lpm = LowPowerManager()
    lpm.set_state("sleep")
    print(f"  LowPowerManager: state={lpm.current_state.value if hasattr(lpm.current_state,'value') else lpm.current_state}")
    lpm.set_state("active")
    print(f"  LowPowerManager: state={lpm.current_state.value if hasattr(lpm.current_state,'value') else lpm.current_state}")


def main():
    print("=" * 60)
    print("SISITEMU Quickstart — Infrastructure Foundation of I")
    print("=" * 60)

    modules = [
        ("ibikoresho_sisitemu", "Memory Management", demo_ibikoresho_sisitemu),
        ("ibikorwa_sisitemu", "OS Services", demo_ibikorwa_sisitemu),
        ("ububiko", "Filesystems", demo_ububiko),
        ("itumanaho_sisitemu", "Networking", demo_itumanaho_sisitemu),
        ("ibyinjijwe", "Embedded", demo_ibyinjijwe),
        ("umuyobora", "Kernel", demo_umuyobora),
        ("ibikoresho_byinjijwe", "Device Drivers", demo_ibikoresho_byinjijwe),
        ("umutekano_sisitemu", "Security", demo_umutekano_sisitemu),
        ("igenzura_sisitemu", "Debugging", demo_igenzura_sisitemu),
        ("imikorere_sisitemu", "Performance", demo_imikorere_sisitemu),
        ("ububiko_db", "Database Engine", demo_ububiko_db),
        ("gukwirakwiza", "Distributed Systems", demo_gukwirakwiza),
        ("ibicu", "Cloud Infrastructure", demo_ibicu),
        ("inkomoko", "Edge & AI Compute", demo_inkomoko),
    ]

    for module_name, display_name, func in modules:
        print(f"\n[{display_name}] ({module_name})")
        try:
            func()
        except Exception as e:
            import traceback
            print(f"  ERROR: {e}")
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("SISITEMU quickstart complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
