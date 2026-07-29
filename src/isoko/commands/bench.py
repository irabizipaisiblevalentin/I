"""isoko bench — Run I project benchmarks."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from typing import List

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("bench", help="Run benchmarks")
    p.add_argument("pattern", nargs="?", help="Benchmark file pattern")
    p.add_argument("--iterations", "-n", type=int, default=1,
                   help="Number of iterations")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path:
        output.error("no ilang.toml found")
        return 1

    m = load_manifest(manifest_path)
    project_dir = os.path.dirname(manifest_path)
    pattern = getattr(args, "pattern", None)
    iterations = getattr(args, "iterations", 1)

    output.header(f"Benchmarks for {m.full_name}")

    bench_dirs = [
        os.path.join(project_dir, "benchmarks"),
        os.path.join(project_dir, "bench"),
    ]
    bench_files = _find_bench_files(bench_dirs, pattern)

    if not bench_files:
        output.warning("no benchmark files found")
        output.dim(f"  Expected location: benchmarks/bench_*.i")
        return 0

    output.info(f"Found {len(bench_files)} benchmark file(s)")
    output.dim(f"  Iterations: {iterations}")

    for bf in bench_files:
        rel = os.path.relpath(bf, project_dir)
        output.header(f"  {rel}")

        for i in range(iterations):
            start = time.time()
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "vm.virtual_machine", bf],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                elapsed = time.time() - start
                output.label_value(f"  Run {i+1}", f"{elapsed:.4f}s")
                if result.returncode != 0 and result.stderr:
                    output.dim(f"    {result.stderr.strip()[:100]}")
            except subprocess.TimeoutExpired:
                output.error(f"  Run {i+1}: timeout (300s)")
            except FileNotFoundError:
                output.warning("VM not available")
                break
            except Exception as e:
                output.error(f"  Run {i+1}: {e}")

    return 0


def _find_bench_files(directories: List[str], pattern: str = None) -> List[str]:
    files = []
    for d in directories:
        if not os.path.isdir(d):
            continue
        for root, _, fnames in os.walk(d):
            for f in fnames:
                if f.endswith(".i") and (f.startswith("bench_") or f.startswith("benchmark_")):
                    if pattern and pattern not in f:
                        continue
                    files.append(os.path.join(root, f))
    return sorted(files)
