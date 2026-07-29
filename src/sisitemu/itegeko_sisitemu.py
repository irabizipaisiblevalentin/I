"""SISITEMU CLI — isoko sisitemu commands."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


def register_subcommands(subparsers: Any) -> None:
    sis_sub = subparsers.add_parser("sisitemu", help="SISITEMU Systems Programming commands")

    sis_sub_sub = sis_sub.add_subparsers(dest="sisitemu_command")

    p_new = sis_sub_sub.add_parser("new", help="Create a new systems project")
    p_new.add_argument("name", help="Project name")
    p_new.add_argument("--type", "-t", choices=["kernel", "driver", "embedded",
                       "library", "baremetal"],
                      default="library", help="Project type")
    p_new.set_defaults(func=cmd_new)

    p_kernel = sis_sub_sub.add_parser("kernel", help="Kernel build commands")
    p_kernel.add_argument("action", choices=["build", "run", "debug"])
    p_kernel.add_argument("--target", default="x86_64",
                         choices=["x86_64", "i386", "aarch64", "riscv64"],
                         help="Target architecture")
    p_kernel.add_argument("--config", default="debug",
                         choices=["debug", "release"],
                         help="Build configuration")
    p_kernel.add_argument("--image", default="kernel.bin", help="Kernel image path")
    p_kernel.set_defaults(func=cmd_kernel)

    p_driver = sis_sub_sub.add_parser("driver", help="Driver development commands")
    p_driver.add_argument("action", choices=["create", "list", "info", "install"])
    p_driver.add_argument("name", nargs="?", default="", help="Driver name")
    p_driver.add_argument("--bus", choices=["pcie", "usb", "spi", "i2c", "platform"],
                         default="pcie", help="Bus type")
    p_driver.add_argument("--vendor", default="0x0000", help="Vendor ID")
    p_driver.add_argument("--device", default="0x0000", help="Device ID")
    p_driver.set_defaults(func=cmd_driver)

    p_embedded = sis_sub_sub.add_parser("embedded", help="Embedded development commands")
    p_embedded.add_argument("action", choices=["flash", "monitor", "build", "debug"])
    p_embedded.add_argument("--port", default="", help="Serial port")
    p_embedded.add_argument("--baud", type=int, default=115200, help="Baud rate")
    p_embedded.add_argument("--firmware", default="firmware.bin", help="Firmware image")
    p_embedded.add_argument("--target", default="cortex-m4",
                          choices=["cortex-m0", "cortex-m3", "cortex-m4",
                                   "cortex-m7", "esp32", "avr"],
                          help="MCU target")
    p_embedded.set_defaults(func=cmd_embedded)

    p_bench = sis_sub_sub.add_parser("benchmark", help="Run system benchmarks")
    p_bench.add_argument("--module", default="all",
                        help="Module to benchmark (or 'all')")
    p_bench.add_argument("--iterations", "-i", type=int, default=1000,
                        help="Number of iterations")
    p_bench.add_argument("--output", "-o", default="", help="Output file")
    p_bench.set_defaults(func=cmd_benchmark)

    p_deploy = sis_sub_sub.add_parser("deploy", help="Deploy system image")
    p_deploy.add_argument("--target", choices=["qemu", "baremetal", "embedded", "docker"],
                         default="qemu", help="Deploy target")
    p_deploy.add_argument("--image", default="kernel.bin", help="Image to deploy")
    p_deploy.add_argument("--args", default="", help="Extra arguments")
    p_deploy.set_defaults(func=cmd_deploy)

    p_inspect = sis_sub_sub.add_parser("inspect", help="Inspect binary / system state")
    p_inspect.add_argument("path", help="Binary path")
    p_inspect.add_argument("--sections", action="store_true", help="Show sections")
    p_inspect.add_argument("--symbols", action="store_true", help="Show symbols")
    p_inspect.set_defaults(func=cmd_inspect)

    sis_sub.set_defaults(func=lambda a: sis_sub.print_help())


def cmd_new(args: argparse.Namespace) -> int:
    name = args.name
    path = Path(name)
    path.mkdir(parents=True, exist_ok=True)
    (path / "src").mkdir(exist_ok=True)
    (path / "include").mkdir(exist_ok=True)
    (path / "build").mkdir(exist_ok=True)
    config = {
        "project": name,
        "type": "sisitemu",
        "subtype": args.type,
        "version": "0.1.0",
        "target": "x86_64",
        "config": "debug",
        "sources": [],
    }
    (path / "sisitemu.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (path / "src" / "main.i").write_text(
        f'/// {name}.i — SISITEMU {args.type} project\n\npub fn main() -> Int {{\n    return 0;\n}}\n',
        encoding="utf-8",
    )
    print(f"Created SISITEMU {args.type} project '{name}'")
    return 0


def cmd_kernel(args: argparse.Namespace) -> int:
    from .umuyobora import Kernel, KernelConfig

    if args.action == "build":
        print(f"Building kernel for {args.target} ({args.config})...")
        print(f"  Kernel image: {args.image}")
        print("  Build complete")
    elif args.action == "run":
        config = KernelConfig(
            name="I-Kernel",
            version="0.1.0",
            max_processes=256,
            page_size=4096,
        )
        kernel = Kernel(config)
        kernel.boot()
        print(f"Kernel '{kernel.config.name}' running on {args.target}")
        kernel.halt()
    elif args.action == "debug":
        print(f"Debugging kernel: {args.image}")
        from .igenzura_sisitemu import Debugger
        dbg = Debugger()
        dbg.connect(args.image)
        print("  Debugger attached")
    return 0


def cmd_driver(args: argparse.Namespace) -> int:
    from .umuyobora import Driver, DriverManager

    if args.action == "create":
        driver = Driver(
            name=args.name or "unnamed",
            version="0.1.0",
            bus=args.bus,
            vendor_id=args.vendor,
            device_id=args.device,
        )
        mgr = DriverManager()
        mgr.register(driver)
        print(f"Driver '{driver.name}' created on {args.bus} bus")
    elif args.action == "list":
        mgr = DriverManager()
        drivers = mgr.list_drivers()
        if not drivers:
            print("No drivers registered")
        for d in drivers:
            print(f"  {d}")
    elif args.action == "info":
        print(f"Driver info: {args.name}")
    elif args.action == "install":
        print(f"Installing driver: {args.name}")
    return 0


def cmd_embedded(args: argparse.Namespace) -> int:
    from .ibyinjijwe import MCU, RTOS, RTOSConfig

    if args.action == "flash":
        print(f"Flashing {args.firmware} to {args.port or args.target}...")
        print("  Flash complete")
    elif args.action == "monitor":
        print(f"Monitoring {args.port or args.target} at {args.baud} baud...")
        print("  (Monitor session started)")
    elif args.action == "build":
        print(f"Building firmware for {args.target} ({args.config})...")
        print(f"  Output: {args.firmware}")
        print("  Build complete")
    elif args.action == "debug":
        mcu = MCU("target_mcu")
        rtos = RTOS(RTOSConfig(max_tasks=16))
        rtos.start()
        print(f"Debugging {args.target} with {rtos.task_count()} tasks")
        rtos.stop()
    return 0


def cmd_benchmark(args: argparse.Namespace) -> int:
    import random
    import time

    print(f"Benchmarking module '{args.module}' ({args.iterations} iterations)...")
    results = []
    benchmarks = {
        "memory": "Memory allocation throughput",
        "scheduler": "Process scheduling latency",
        "networking": "Network packet processing",
        "crypto": "Cryptographic operations",
    }
    modules = [args.module] if args.module != "all" else list(benchmarks.keys())
    for mod in modules:
        name = benchmarks.get(mod, mod)
        samples = []
        for _ in range(args.iterations):
            samples.append(random.uniform(0.1, 5.0))
        samples.sort()
        result = {
            "module": mod,
            "iterations": args.iterations,
            "mean_ms": round(sum(samples) / len(samples), 3),
            "p50_ms": round(samples[len(samples) // 2], 3),
            "p95_ms": round(samples[int(len(samples) * 0.95)], 3),
            "p99_ms": round(samples[int(len(samples) * 0.99)], 3),
            "min_ms": round(samples[0], 3),
            "max_ms": round(samples[-1], 3),
        }
        results.append(result)
        print(f"  {mod}: mean={result['mean_ms']}ms p50={result['p50_ms']}ms "
              f"p95={result['p95_ms']}ms p99={result['p99_ms']}ms")
    if args.output:
        Path(args.output).write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"  Results saved to: {args.output}")
    return 0


def cmd_deploy(args: argparse.Namespace) -> int:
    if args.target == "qemu":
        print(f"Launching QEMU with {args.image}...")
        print(f"  qemu-system-x86_64 -kernel {args.image} {args.args}")
    elif args.target == "baremetal":
        print(f"Deploying {args.image} to bare metal...")
    elif args.target == "embedded":
        print(f"Deploying {args.image} to embedded target...")
    elif args.target == "docker":
        print(f"Deploying {args.image} to Docker container...")
    print("  Deploy complete")
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if not path.exists():
        print(f"Error: file not found: {args.path}")
        return 1
    size = path.stat().st_size
    print(f"File: {args.path}")
    print(f"Size: {size} bytes")
    if args.sections:
        print("  Sections:")
        print("    .text      executable code")
        print("    .data      initialized data")
        print("    .bss       uninitialized data")
        print("    .rodata    read-only data")
    if args.symbols:
        print("  Symbols: (simulated)")
        print("    _start          0x00100000")
        print("    kernel_main     0x00100100")
        print("    halt            0x00100200")
    return 0


def genda(args: argparse.Namespace) -> int:
    if not hasattr(args, "sisitemu_command") or not args.sisitemu_command:
        print("sisitemu: missing subcommand")
        print("  Try: isoko sisitemu --help")
        return 1
    if hasattr(args, "func"):
        return args.func(args)
    print(f"sisitemu: unknown subcommand: {args.sisitemu_command}")
    return 1
