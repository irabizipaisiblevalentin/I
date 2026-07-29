/// sisitemu.i — The unified infrastructure foundation of the I Language
///
/// SISITEMU powers ALL infrastructure built in I:
///   Operating Systems ─ Embedded Devices ─ Database Engines
///   Distributed Systems ─ Cloud Infrastructure ─ High-Performance Networking
///   AI Inference Servers ─ Edge Computing ─ Robotics Controllers
///
/// Higher-level platforms (UBWENGE, IMIKINO, IGICU, Web) all build on this foundation.

// ─── Layer 0: Hardware Abstraction ──────────────────────────────────────────

pub enum Architecture {
    X86_64 = "x86_64", AArch64 = "aarch64", RISC_V_64 = "riscv64",
    ARM_Cortex_M = "cortex-m", ESP32 = "esp32", AVR = "avr",
}

pub enum BusProtocol {
    PCIe = "pcie", USB = "usb", SPI = "spi", I2C = "i2c",
    UART = "uart", CAN = "can",
}

pub enum MemoryModel {
    Flat = "flat", Segmented = "segmented", Paged = "paged", MPU = "mpu",
}

pub struct MemoryRegion {
    base: UInt64, size: Int, permissions: String = "rw-",
}

pub fn gpio_read(pin: Int) -> Bool
pub fn gpio_write(pin: Int, value: Bool)
pub fn spi_transfer(bus: Int, data: [UInt8]) -> [UInt8]
pub fn i2c_read(addr: UInt8, reg: UInt8) -> UInt8
pub fn i2c_write(addr: UInt8, reg: UInt8, data: UInt8)

// ─── Layer 1: Core Primitives ───────────────────────────────────────────────

pub enum Endianness { Little = "little", Big = "big" }
pub enum SchedulerPolicy { RoundRobin, Priority, FIFO, MLFQ, CFS }

pub struct Pointer { address: UInt64, offset: Int = 0 }
pub struct Allocator { pool_size: Int, used: Int, alignment: Int = 8 }

pub fn alloc(size: Int) -> Pointer
pub fn free(ptr: Pointer)
pub fn memcpy(dst: Pointer, src: Pointer, size: Int)

pub enum CryptoAlgorithm {
    AES256GCM = "aes-256-gcm", SHA256 = "sha-256",
    SHA512 = "sha-512", Ed25519 = "ed25519",
}

pub fn crypto_encrypt(algo: CryptoAlgorithm, key: [UInt8], data: [UInt8]) -> [UInt8]
pub fn crypto_hash(algo: CryptoAlgorithm, data: [UInt8]) -> [UInt8]

// ─── Layer 2: System Services ───────────────────────────────────────────────

pub struct Process { pid: Int, name: String, priority: Int = 0 }
pub struct KernelConfig { name: String, version: String, max_processes: Int }

pub fn process_create(name: String) -> Process
pub fn process_kill(pid: Int) -> Bool
pub fn fs_open(path: String, flags: String) -> FileHandle
pub fn fs_read(fd: FileHandle, size: Int) -> [UInt8]
pub fn fs_write(fd: FileHandle, data: [UInt8]) -> Int
pub fn tcp_connect(host: String, port: Int) -> Connection
pub fn tcp_listen(port: Int) -> Listener
pub fn dns_resolve(hostname: String) -> [String]
pub fn kernel_boot(config: KernelConfig) -> Bool
pub fn kernel_halt()
pub fn driver_register(driver: Driver) -> Bool

// ─── Layer 3: Infrastructure Domains ────────────────────────────────────────

// Database Engine Primitives
pub struct BTreeIndex { order: Int }
pub struct LSMTree { path: String }
pub struct WriteAheadLog { path: String }
pub struct Transaction { id: String, isolation: String }

pub fn btree_insert(tree: BTreeIndex, key: [UInt8], value: [UInt8])
pub fn btree_search(tree: BTreeIndex, key: [UInt8]) -> [UInt8]?
pub fn wal_append(log: WriteAheadLog, entry: WALEntry) -> Int
pub fn txn_begin() -> Transaction
pub fn txn_commit(txn: Transaction) -> Bool
pub fn txn_rollback(txn: Transaction) -> Bool

// Distributed Systems
pub enum RaftRole { Follower, Candidate, Leader }
pub struct RaftNode { id: String, role: RaftRole, term: Int }
pub struct MessageQueue { topic: String, partitions: Int }

pub fn raft_propose(node: RaftNode, command: String, data: [UInt8]) -> Int?
pub fn service_register(name: String, host: String, port: Int)
pub fn service_discover(name: String) -> [(String, Int)]
pub fn lock_acquire(lock_id: String, holder: String, ttl: Int) -> Int?
pub fn lock_release(lock_id: String, holder: String, token: Int) -> Bool
pub fn queue_publish(topic: String, key: [UInt8], value: [UInt8]) -> Int
pub fn queue_subscribe(topic: String, handler: fn(Message))

// Cloud Infrastructure
pub struct Container { id: String, name: String, image: String }
pub struct VirtualMachine { id: String, vcpus: Int, memory_mb: Int }
pub struct LoadBalancer { name: String, algorithm: String }

pub fn container_create(name: String, image: String) -> Container
pub fn container_start(id: String) -> Bool
pub fn container_stop(id: String) -> Bool
pub fn vm_create(name: String, image: String) -> VirtualMachine
pub fn vm_power_on(id: String) -> Bool
pub fn lb_next(backend: String) -> (String, Int)?
pub fn secret_store(name: String, value: String)
pub fn secret_retrieve(name: String) -> String?

// Edge & AI Compute
pub struct Tensor { shape: [Int], dtype: String }
pub struct GPUDevice { name: String, memory_mb: Int }
pub struct Model { id: String, version: String }

pub fn tensor_add(a: Tensor, b: Tensor) -> Tensor
pub fn tensor_matmul(a: Tensor, b: Tensor) -> Tensor
pub fn gpu_allocate(device: GPUDevice, memory_mb: Int) -> Bool
pub fn model_load(path: String) -> Model
pub fn model_predict(model: Model, input: Tensor) -> Tensor
pub fn edge_register_device(device: EdgeDevice) -> Bool
pub fn edge_ingest(device_id: String, metrics: {String: Float})

// High-Performance Networking
pub struct RdmaEndpoint { host: String, port: Int }
pub struct DpdkPort { name: String, rx_queues: Int, tx_queues: Int }
pub struct ZeroCopyBuffer { size: Int }

pub fn rdma_write(ep: RdmaEndpoint, remote_addr: UInt64, data: [UInt8]) -> Bool
pub fn rdma_read(ep: RdmaEndpoint, remote_addr: UInt64, size: Int) -> [UInt8]?
pub fn dpdk_send(port: DpdkPort, data: [UInt8]) -> Bool
pub fn dpdk_recv(port: DpdkPort) -> [UInt8]?
pub fn zc_send(buf: ZeroCopyBuffer, data: [UInt8]) -> Int
pub fn zc_recv(buf: ZeroCopyBuffer, size: Int) -> [UInt8]

// ─── GUI / Display Server ───────────────────────────────────────────────────

pub enum WindowState { Normal, Minimized, Maximized, Closed }
pub enum CursorShape { Default, Hand, Text, Move, Resize }

pub struct Point { x: Int, y: Int }
pub struct Rect { x: Int, y: Int, width: Int, height: Int }
pub struct Color { r: Int, g: Int, b: Int, a: Int }

pub struct Theme {
    title_bar_active: String, taskbar_background: String,
    button_face: String, window_background: String,
}

pub struct Window { title: String, x: Int, y: Int, width: Int, height: Int }

pub fn window_create(title: String, x: Int, y: Int, w: Int, h: Int) -> Window
pub fn window_close(win: Window)
pub fn window_move(win: Window, dx: Int, dy: Int)
pub fn window_resize(win: Window, w: Int, h: Int)
pub fn screen_get_size() -> (Int, Int)

pub struct Button { text: String, x: Int, y: Int, width: Int, height: Int }
pub struct Label { text: String, x: Int, y: Int }
pub struct TextBox { text: String, x: Int, y: Int, width: Int, height: Int }
pub struct ListBox { items: [String], x: Int, y: Int, width: Int, height: Int }
pub struct ProgressBar { value: Float, x: Int, y: Int, width: Int, height: Int }

pub fn btn_create(text: String, x: Int, y: Int, w: Int, h: Int) -> Button
pub fn label_create(text: String, x: Int, y: Int) -> Label
pub fn textbox_create(x: Int, y: Int, w: Int, h: Int) -> TextBox
pub fn listbox_add(items: [String]) -> ListBox
pub fn progress_set(pb: ProgressBar, value: Float)

pub struct Taskbar { x: Int, y: Int, width: Int, height: Int }
pub struct Desktop { background: String }

pub fn compositor_init(width: Int, height: Int) -> Bool
pub fn compositor_run()
pub fn desktop_show(desktop: Desktop)
