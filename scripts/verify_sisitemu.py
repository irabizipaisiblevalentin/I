#!/usr/bin/env python3
"""SISITEMU Verification Suite — validates all 14 modules import correctly."""

from __future__ import annotations

import importlib
import inspect
import os
import sys
import traceback


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


MODULES = [
    "sisitemu.igaragaza",
    "sisitemu.ibikoresho_bya_GUI",
    "sisitemu.ikigoroba",
    "sisitemu.ibikoresho_sisitemu",
    "sisitemu.ibikorwa_sisitemu",
    "sisitemu.ububiko",
    "sisitemu.itumanaho_sisitemu",
    "sisitemu.ibyinjijwe",
    "sisitemu.umuyobora",
    "sisitemu.ibikoresho_byinjijwe",
    "sisitemu.umutekano_sisitemu",
    "sisitemu.igenzura_sisitemu",
    "sisitemu.imikorere_sisitemu",
    "sisitemu.itegeko_sisitemu",
    "sisitemu.ububiko_db",
    "sisitemu.gukwirakwiza",
    "sisitemu.ibicu",
    "sisitemu.inkomoko",
    "sisitemu",
]

EXPECTED_CLASSES: dict[str, list[str]] = {
    "sisitemu.ibikoresho_sisitemu": [
        "Allocator", "ArenaAllocator", "PoolAllocator", "RegionAllocator",
        "Pointer", "Slice", "BitManipulator", "AtomicOps",
        "Endianness", "CacheManager", "MemoryBlock", "MemoryRegion",
        "Alignment", "SystemsCore",
    ],
    "sisitemu.ibikorwa_sisitemu": [
        "ProcessManager", "Scheduler", "ProcessInfo", "ProcessState",
        "Timer", "IntervalTimer", "SignalManager", "Signal",
        "EnvironmentManager", "ThreadPriority", "SchedulerPolicy",
    ],
    "sisitemu.ububiko": [
        "VirtualFileSystem", "FileSystem", "MemoryFileSystem", "FATFileSystem",
        "NativeFileSystem", "NullFS", "FileHandle", "FileType",
        "DirEntry", "FileStat", "FilePermission", "OpenMode",
    ],
    "sisitemu.itumanaho_sisitemu": [
        "TCPServer", "UDPEndpoint", "Connection",
        "HTTPServer", "HTTPRequest", "HTTPResponse",
        "DNSResolver", "DHCPClient", "SerialPort", "CANBus",
        "NetworkStack", "NetworkAddress", "Packet", "Protocol",
        "SocketType", "SocketState",
    ],
    "sisitemu.ibyinjijwe": [
        "MCU", "GPIOController", "GPIOPin", "SPIBus", "SPIConfig",
        "I2CBus", "I2CConfig", "UART", "UARTConfig",
        "PWMController", "PWMPin", "ADCController", "ADCChannel",
        "HardwareTimer", "TimerConfig", "InterruptController",
        "InterruptTrigger", "RTOS", "Architecture", "MCUFamily", "PinMode",
    ],
    "sisitemu.umuyobora": [
        "Kernel", "VirtualMemoryManager", "MemoryRegion",
        "IPCChannel", "SharedMemoryRegion",
        "Driver", "DriverManager", "PowerManager",
        "SyscallContext", "SyscallNumber", "Scheduler",
        "KernelThread", "PrivilegeLevel", "KernelState",
    ],
    "sisitemu.ibikoresho_byinjijwe": [
        "USBController", "USBDevice", "PCIeController", "PCIeDevice",
        "StorageDevice", "GraphicsDevice", "SensorDevice", "DisplayDevice",
        "TouchDevice", "IndustrialController", "DeviceManager",
        "DeviceClass", "USBDeviceClass", "PCIeDeviceClass",
    ],
    "sisitemu.umutekano_sisitemu": [
        "MemoryProtectionUnit", "MemoryProtectionRegion", "Sandbox",
        "CryptographicEngine", "SecureIPCChannel", "StackProtection",
        "AuditLog", "SecurityManager", "SecurityLevel", "SandboxPolicy",
        "HashAlgorithm", "CipherAlgorithm",
    ],
    "sisitemu.igenzura_sisitemu": [
        "Tracer", "Profiler", "MemoryInspector", "CrashDump",
        "LiveDiagnostics", "Debugger", "TracePoint", "TraceEvent",
        "ProfileSample", "DebugLevel", "MemoryRegion",
    ],
    "sisitemu.imikorere_sisitemu": [
        "Benchmark", "BenchmarkResult", "LatencyMeter", "MemoryUsageTracker",
        "ThroughputMeter", "PerformanceOptimizer",
    ],
    "sisitemu.itegeko_sisitemu": [
        "register_subcommands", "genda",
    ],
    "sisitemu.ububiko_db": [
        "StorageEngine", "BTreeIndex", "LSMTree", "WriteAheadLog",
        "BufferPool", "TransactionManager", "HashIndex", "MemTable",
        "SSTable", "IndexType", "IsolationLevel", "Transaction",
    ],
    "sisitemu.gukwirakwiza": [
        "RaftConsensus", "RPCServer", "ServiceDiscovery", "DistributedLock",
        "MessageQueue", "CRDTCounter", "RaftConfig", "RaftRole",
        "LogEntry", "Message",
    ],
    "sisitemu.ibicu": [
        "ContainerRuntime", "VMManager", "LoadBalancer", "Orchestrator",
        "SecretManager", "ConfigManager", "Container", "VirtualMachine",
        "ContainerState", "VMState", "LBAlgorithm", "DeploymentStrategy",
    ],
    "sisitemu.inkomoko": [
        "EdgeRuntime", "IoTGateway", "GPUCompute", "Tensor",
        "ModelServing", "RealTimeController", "LowPowerManager",
        "GPUDevice", "RTTask", "TensorOps",
    ],
    "sisitemu.igaragaza": [
        "Compositor", "Window", "Theme", "Color", "Rect", "Point",
        "FontRenderer", "CursorShape", "Event", "EventType", "WindowState",
    ],
    "sisitemu.ibikoresho_bya_GUI": [
        "Widget", "Container", "Button", "Label", "TextBox", "CheckBox",
        "RadioButton", "ListBox", "ComboBox", "ProgressBar", "Slider",
        "Panel", "GroupBox", "MenuBar", "Menu", "MenuItem",
        "ScrollView", "StatusBar", "ToolTip", "TabControl", "TreeView",
    ],
    "sisitemu.ikigoroba": [
        "Desktop", "Taskbar", "SystemTray", "DesktopIcon", "TrayIcon",
    ],
}


def verify_import(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except Exception:
        print(f"  FAIL: Could not import {module_name}")
        traceback.print_exc()
        return False


def verify_classes(module_name: str, expected: list[str]) -> bool:
    try:
        mod = importlib.import_module(module_name)
    except Exception:
        return False

    success = True
    for cls_name in expected:
        if not hasattr(mod, cls_name):
            print(f"  MISSING: {module_name}.{cls_name}")
            success = False
    return success


def verify_init_exports() -> bool:
    try:
        mod = importlib.import_module("sisitemu")
        if not hasattr(mod, "__all__"):
            print("  MISSING: sisitemu.__all__")
            return False
        key_exports = [
            "ArenaAllocator", "ProcessManager", "MemoryFileSystem",
            "TCPServer", "MCU", "Kernel", "USBController",
            "MemoryProtectionUnit", "Tracer", "Benchmark",
            "StorageEngine", "RaftConsensus", "ContainerRuntime",
            "EdgeRuntime", "Compositor", "Button", "Desktop",
        ]
        for export in key_exports:
            if export not in mod.__all__:
                print(f"  MISSING in __all__: {export}")
                return False
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


def verify_cross_module() -> bool:
    try:
        from sisitemu.umuyobora import Kernel
        from sisitemu.itegeko_sisitemu import genda, register_subcommands
        from sisitemu import KernelScheduler, DebugMemoryRegion
        from sisitemu.ububiko_db import StorageEngine
        from sisitemu.gukwirakwiza import RaftConsensus, RaftConfig
        from sisitemu.ibicu import ContainerRuntime
        from sisitemu.inkomoko import EdgeRuntime, Tensor
        kernel = Kernel(name="test")
        kernel.boot()
        kernel.halt()
        engine = StorageEngine(name="test")
        engine.open()
        engine.put(b"k", b"v")
        assert engine.get(b"k") == b"v"
        engine.close()
        cfg = RaftConfig(node_id="n1", peers=[], election_timeout_min=150)
        raft = RaftConsensus(cfg)
        raft.start()
        raft.stop()
        rt = ContainerRuntime()
        c = rt.create_container("t", image="a")
        rt.start_container(c.container_id)
        rt.stop_container(c.container_id)
        from sisitemu.inkomoko import EdgeDevice, DeviceType
        edge = EdgeRuntime()
        dev = EdgeDevice(device_id="s1", name="test", device_type=DeviceType.SENSOR)
        edge.register_device(dev)
        t = Tensor(shape=(2,2), data=[1,2,3,4])
        return True
    except Exception as e:
        print(f"  FAIL: Cross-module integration: {e}")
        return False


def verify_all() -> int:
    print("=" * 60)
    print("SISITEMU Verification Suite")
    print("=" * 60)

    failures = 0
    total_checks = 0

    # 1. Import all modules
    print("\n[Module Imports]")
    for mod_name in MODULES:
        total_checks += 1
        if verify_import(mod_name):
            print(f"  OK: {mod_name}")
        else:
            failures += 1

    # 2. Verify expected classes
    print("\n[Expected Classes]")
    for mod_name, classes in EXPECTED_CLASSES.items():
        total_checks += 1
        if verify_classes(mod_name, classes):
            print(f"  OK: {mod_name} ({len(classes)} classes)")
        else:
            failures += 1

    # 3. Verify __init__.py exports
    print("\n[Package Init Exports]")
    total_checks += 1
    if verify_init_exports():
        print("  OK: sisitemu.__all__")
    else:
        failures += 1

    # 4. Cross-module integration
    print("\n[Cross-Module Integration]")
    total_checks += 1
    if verify_cross_module():
        print("  OK: Cross-module integration")
    else:
        failures += 1

    print(f"\n{'=' * 60}")
    print(f"Results: {total_checks} checks, {failures} failures")
    if failures == 0:
        print("SISITEMU: ALL CHECKS PASSED")
    else:
        print(f"SISITEMU: {failures} FAILURES")
    print("=" * 60)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(verify_all())
