"""isoko test — Run I project tests."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from typing import List

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("test", help="Run tests")
    p.add_argument("pattern", nargs="?", help="Test file pattern")
    p.add_argument("--verbose", "-v", action="store_true",
                   help="Verbose test output")
    p.add_argument("--release", action="store_true",
                   help="Run tests in release mode")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path:
        output.error("no ilang.toml found")
        return 1

    m = load_manifest(manifest_path)
    project_dir = os.path.dirname(manifest_path)
    pattern = getattr(args, "pattern", None)
    verbose = getattr(args, "verbose", False)

    output.header(f"Running tests for {m.full_name}")

    # Find test files
    test_dirs = [os.path.join(project_dir, "tests")]
    test_files = _find_test_files(test_dirs, pattern)

    if not test_files:
        output.warning("no test files found")
        output.dim(f"  Expected location: tests/test_*.i")
        return 0

    output.info(f"Found {len(test_files)} test file(s)")

    passed = 0
    failed = 0
    errors = []
    start = time.time()

    for tf in test_files:
        rel = os.path.relpath(tf, project_dir)
        try:
            result = subprocess.run(
                [sys.executable, "-m", "vm.virtual_machine", tf],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                passed += 1
                if verbose:
                    output.success(f"  PASS {rel}")
            else:
                failed += 1
                errors.append((rel, result.stderr.strip()))
                output.error(f"  FAIL {rel}")
                if verbose and result.stderr:
                    output.dim(f"    {result.stderr.strip()[:200]}")
        except subprocess.TimeoutExpired:
            failed += 1
            errors.append((rel, "timeout"))
            output.error(f"  TIMEOUT {rel}")
        except FileNotFoundError:
            output.warning("VM not available. Skipping .i test execution.")
            break
        except Exception as e:
            failed += 1
            errors.append((rel, str(e)))
            output.error(f"  ERROR {rel}: {e}")

    elapsed = time.time() - start
    output.header("Test Results")
    output.label_value("Passed", str(passed))
    output.label_value("Failed", str(failed))
    output.label_value("Total", str(passed + failed))
    output.label_value("Time", f"{elapsed:.2f}s")

    if errors:
        output.header("Failures")
        for name, err in errors:
            output.error(f"{name}: {err[:200]}")

    return 1 if failed > 0 else 0


def _find_test_files(directories: List[str], pattern: str = None) -> List[str]:
    files = []
    for d in directories:
        if not os.path.isdir(d):
            continue
        for root, _, fnames in os.walk(d):
            for f in fnames:
                if f.endswith(".i") and f.startswith("test_"):
                    if pattern and pattern not in f:
                        continue
                    files.append(os.path.join(root, f))
    return sorted(files)
