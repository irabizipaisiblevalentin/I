"""End-to-end tests that the standard library ships inside the built wheel.

Builds the wheel from a clean copy of the source tree (once per test session),
inspects its contents, installs it to an isolated target, imports the stdlib
modules from that install, and runs the compiler CLI (from the wheel) on a
``shyiramo`` import source.

The clean-copy build keeps setuptools ``build/`` artifacts out of the real
repository and avoids stale-state collisions on Windows.
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

STDLIB_MODULES = [
    "stdlib.text",
    "stdlib.math",
    "stdlib.numbers",
    "stdlib.io",
    "stdlib.json",
    "stdlib.csv",
    "stdlib.collections",
    "stdlib.filesystem",
    "stdlib.time",
    "stdlib.http",
    "stdlib.crypto",
]

_WHEEL_PATH = None


def _clean_source_copy(dst: str) -> str:
    """Copy the build inputs into ``dst`` (no build artifacts, no SCM)."""
    os.makedirs(dst)
    shutil.copytree(
        os.path.join(REPO_ROOT, "src"),
        os.path.join(dst, "src"),
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    for name in ("pyproject.toml", "README.md"):
        shutil.copy2(os.path.join(REPO_ROOT, name), os.path.join(dst, name))
    return dst


def _build_wheel_once() -> str:
    """Build the wheel from a clean source copy. Build happens once per session."""
    global _WHEEL_PATH
    if _WHEEL_PATH and os.path.isfile(_WHEEL_PATH):
        return _WHEEL_PATH

    work = tempfile.mkdtemp(prefix="i_lang_wheel_")
    project = _clean_source_copy(os.path.join(work, "project"))
    outdir = os.path.join(work, "dist")
    os.makedirs(outdir)

    proc = subprocess.run(
        [sys.executable, "-m", "pip", "wheel", project, "--no-deps", "-w", outdir],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if proc.returncode != 0:
        raise AssertionError(f"wheel build failed:\n{proc.stdout}\n{proc.stderr}")

    wheels = glob.glob(os.path.join(outdir, "*.whl"))
    if len(wheels) != 1:
        raise AssertionError(f"expected one wheel, got {wheels}")
    _WHEEL_PATH = wheels[0]
    return _WHEEL_PATH


def _install_wheel(wheel: str, target: str) -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-deps", "--target", target, wheel],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if proc.returncode != 0:
        raise AssertionError(f"wheel install failed:\n{proc.stderr}")


class TestStdlibWheel(unittest.TestCase):
    """The wheel must carry the stdlib and it must import once installed."""

    def test_wheel_contains_stdlib(self):
        wheel = _build_wheel_once()
        names = zipfile.ZipFile(wheel).namelist()
        stdlib_py = [n for n in names if n.startswith("stdlib/") and n.endswith(".py")]
        self.assertGreaterEqual(
            len(stdlib_py), 40, "stdlib Python modules must ship in the wheel"
        )
        self.assertIn(
            "stdlib/urubuga.i", names, "urubuga.i framework source must ship in the wheel"
        )

    def test_stdlib_imports_from_installed_wheel(self):
        wheel = _build_wheel_once()
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "target")
            _install_wheel(wheel, target)
            env = dict(os.environ)
            env["PYTHONPATH"] = target
            code = (
                "import importlib, stdlib\n"
                f"for m in {STDLIB_MODULES!r}:\n"
                "    importlib.import_module(m)\n"
                "assert stdlib.__version__ == '1.0.0', stdlib.__version__\n"
                "print('OK', stdlib.__file__)\n"
            )
            proc = subprocess.run(
                [sys.executable, "-c", code],
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(
                proc.returncode,
                0,
                msg=f"stdlib import failed:\nstdout={proc.stdout}\nstderr={proc.stderr}",
            )
            self.assertIn("OK", proc.stdout)

    def test_language_import_resolves_from_wheel(self):
        wheel = _build_wheel_once()
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "target")
            _install_wheel(wheel, target)
            env = dict(os.environ)
            env["PYTHONPATH"] = target
            src = os.path.join(tmp, "imports.i")
            with open(src, "w", encoding="utf-8") as f:
                f.write("shyiramo urubuga\nshyiramo math kugira_ngo m\n")
            out = os.path.join(tmp, "out.bin")
            proc = subprocess.run(
                [sys.executable, "-m", "compiler.compiler", src, "-o", out],
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(
                proc.returncode,
                0,
                msg=f"compile failed:\nstdout={proc.stdout}\nstderr={proc.stderr}",
            )
            self.assertTrue(os.path.isfile(out), "bytecode artifact should exist")


if __name__ == "__main__":
    unittest.main()
